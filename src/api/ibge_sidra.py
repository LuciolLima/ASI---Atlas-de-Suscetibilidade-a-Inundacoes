"""SISTEMA ASI — CLIENTE IBGE SIDRA
Versão: 2.0 — Dados censitários, demográfica e socioeconômica com rate limiting, cache e validação
API Oficial: https://apisidra.ibge.gov.br/ (API antiga que funciona - a nova v3 retorna 503/500)
"""

from __future__ import annotations

import logging
import time
from typing import Any

import pandas as pd

from src.api.base import APIClient, APIConfig, APIResponse, streamlit_cache_data
from src.api.schemas import (
    SidraConsolidadoSchema,
    SidraPopulacaoSchema,
    SidraSaneamentoSchema,
    validate_or_warn,
)

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO IBGE SIDRA
# ════════════════════════════════════════════════════════════════════════════════

# IMPORTANTE: Usar a API antiga (apisidra.ibge.gov.br) que funciona
# A nova API v3 (servicodados.ibge.gov.br/api/v3/agregados) retorna 503/500
IBGE_SIDRA_CONFIG = APIConfig(
    name="ibge_sidra",
    base_url="https://apisidra.ibge.gov.br",
    timeout=120,  # SIDRA pode ser lento
    max_retries=3,
    backoff_factor=2.0,
    rate_limit_rps=0.5,   # 1 req a cada 2 segundos - muito conservador
    rate_limit_rpm=15,    # 15 req/min
    cache_ttl_seconds=86400,  # 24h - dados censitários mudam pouco
    headers={
        "User-Agent": "ASI-Flood-Susceptibility/1.0 (https://github.com/LuciolLima/ASI)",
        "Accept": "application/json",
    },
)

IBGE_SIDRA_METADATA = {
    "name": "ibge_sidra",
    "display_name": "IBGE SIDRA",
    "description": "Sistema IBGE de Recuperação Automática - Dados censitários e socioeconômicos",
    "version": "2.0",
    "provider_url": "https://sidra.ibge.gov.br/",
    "auth_required": False,
    "rate_limit_info": "0.5 req/s, 15 req/min (auto-limitado) — API pública oficial (apisidra.ibge.gov.br)",
    "parameters": [
        "População total (Censo 2022)",
        "Saneamento adequado (% domicílios)",
        "Domicílios por tipo",
        "Rendimento médio",
        "Escolaridade",
        "Vulnerabilidade social",
    ],
}

# ════════════════════════════════════════════════════════════════════════════════
# TABELAS SIDRA RELEVANTES PARA ASI
# ════════════════════════════════════════════════════════════════════════════════

SIDRA_TABLES = {
    # Censo 2022 - População
    "populacao_2022": {
        "table_id": "9514",
        "name": "População residente - Censo 2022",
        "variables": ["93"],  # População total
        "period": "2022",
    },
    # Saneamento - Tabela 9860 (Censo 2022)
    # Variáveis: 381=Total domicílios, 382=Moradores, 1000381=%, 1000382=%
    # Para % adequado: usar 1000381 (domicílios ocupados - percentual do total geral)
    "saneamento_2022": {
        "table_id": "9860",
        "name": "Domicílios particulares permanentes por condição de saneamento",
        "variables": ["381", "1000381"],  # Total domicílios, % do total
        "period": "2022",
    },
    # Rendimento - Tabela 5939 (Censo 2022)
    "rendimento_2022": {
        "table_id": "5939",
        "name": "Rendimento médio mensal dos responsáveis",
        "variables": ["9324"],  # Rendimento médio
        "period": "2022",
    },
    # Escolaridade - Tabela 9515 (Censo 2022)
    "escolaridade_2022": {
        "table_id": "9515",
        "name": "Pessoas responsáveis por domicílios por nível de instrução",
        "variables": ["93", "94", "95", "96", "97", "98"],  # Sem instrução, fundamental, médio, superior
        "period": "2022",
    },
}

# Mapeamento de códigos IBGE para nomes de municípios PE (baseado na API SIDRA oficial)
PE_MUNICIPIOS_IBGE = {
    2600054: "ABREU E LIMA",
    2600104: "AFOGADOS DA INGAZEIRA",
    2600203: "AFRANIO",
    2600302: "AGRESTINA",
    2600401: "AGUA PRETA",
    2600500: "AGUAS BELAS",
    2600609: "ALAGOINHA",
    2600708: "ALIANCA",
    2600807: "ALTINHO",
    2600906: "AMARAJI",
    2601003: "ANGELIM",
    2601052: "ARACOIABA",
    2601102: "ARARIPINA",
    2601201: "ARCOVERDE",
    2601300: "BARRA DE GUABIRABA",
    2601409: "BARREIROS",
    2601508: "BELEM DE MARIA",
    2601607: "BELEM DO SAO FRANCISCO",
    2601706: "BELO JARDIM",
    2601805: "BETANIA",
    2601904: "BEZERROS",
    2602001: "BODOCÓ",
    2602100: "BOM CONSELHO",
    2602209: "BOM JARDIM",
    2602308: "BONITO",
    2602407: "BREJÃO",
    2602506: "BREJINHO",
    2602605: "BREJO DA MADRE DE DEUS",
    2602704: "BUENOS AIRES",
    2602803: "BUIQUE",
    2602902: "CABO DE SANTO AGOSTINHO",
    2603009: "CABROBO",
    2603108: "CACHOEIRINHA",
    2603207: "CAETES",
    2603306: "CALCADO",
    2603405: "CALUMBI",
    2603454: "CAMARAGIBE",
    2603504: "CAMOCIM DE SAO FELIX",
    2603603: "CAMUTANGA",
    2603702: "CANHOTINHO",
    2603801: "CAPOEIRAS",
    2603900: "CARNAIBA",
    2603926: "CARNAUBEIRA DA PENHA",
    2604007: "CARPINA",
    2604106: "CARUARU",
    2604155: "CASINHAS",
    2604205: "CATENDE",
    2604304: "CEDRO",
    2604403: "CHA DE ALEGRIA",
    2604502: "CHA GRANDE",
    2604601: "CONDADO",
    2604700: "CORRENTES",
    2604809: "CORTES",
    2604908: "CUMARU",
    2605004: "CUPIRA",
    2605103: "CUSTODIA",
    2605152: "DORMENTES",
    2605202: "ESCADA",
    2605301: "EXU",
    2605400: "FEIRA NOVA",
    2605459: "FERNANDO DE NORONHA",
    2605509: "FERREIROS",
    2605608: "FLORES",
    2605707: "FLORESTA",
    2605806: "FREI MIGUELINHO",
    2605905: "GAMELEIRA",
    2606002: "GARANHUNS",
    2606101: "GLORIA DO GOITA",
    2606200: "GOIANA",
    2606309: "GRANITO",
    2606408: "GRAVATA",
    2606507: "IATI",
    2606606: "IBIMIRIM",
    2606705: "IBIRAJUBA",
    2606804: "IGARASSU",
    2606903: "IGUARACI",
    2607000: "INAJA",
    2607109: "INGAZEIRA",
    2607208: "IPOJUCA",
    2607307: "IPUBI",
    2607406: "ITACURUBA",
    2607505: "ITAÍBA",
    2607604: "ILHA DE ITAMARACA",
    2607653: "ITAMBE",
    2607703: "ITAPETIM",
    2607752: "ITAPISSUMA",
    2607802: "ITAQUIRINGA",
    2607901: "JABOATAO DOS GUARARAPES",
    2607950: "JAQUEIRA",
    2608008: "JATAUBA",
    2608057: "JATOBA",
    2608107: "JOAO ALFREDO",
    2608206: "JOAQUIM NABUCO",
    2608255: "JUCATI",
    2608305: "JUPI",
    2608404: "JUREMA",
    2608453: "LAGOA DO CARRO",
    2608503: "LAGOA DE ITAENGA",
    2608602: "LAGOA DO OURO",
    2608701: "LAGOA DOS GATOS",
    2608750: "LAGOA GRANDE",
    2608800: "LAJEDO",
    2608909: "LIMOEIRO",
    2609006: "MACAPARANA",
    2609105: "MACHADOS",
    2609154: "MANARI",
    2609204: "MARAIAL",
    2609303: "MIRANDIBA",
    2609402: "MORENO",
    2609501: "NAZARE DA MATA",
    2609600: "OLINDA",
    2609709: "OROBO",
    2609808: "OROCO",
    2609907: "OURICURI",
    2610004: "PALMARES",
    2610103: "PALMEIRINA",
    2610202: "PANELAS",
    2610301: "PARANATAMA",
    2610400: "PARNAMIRIM",
    2610509: "PASSIRA",
    2610608: "PAUDALHO",
    2610707: "PAULISTA",
    2610806: "PEDRA",
    2610905: "PESQUEIRA",
    2611002: "PETROLANDIA",
    2611101: "PETROLINA",
    2611200: "POCAO",
    2611309: "POMBOS",
    2611408: "PRIMAVERA",
    2611507: "QUIPIAPA",
    2611533: "QUIXABA",
    2611606: "RECIFE",
    2611705: "RIACHO DAS ALMAS",
    2611804: "RIBEIRAO",
    2611903: "RIO FORMOSO",
    2612000: "SAIRE",
    2612109: "SALGADINHO",
    2612208: "SALGUEIRO",
    2612307: "SALOA",
    2612406: "SANHARO",
    2612455: "SANTA CRUZ",
    2612471: "SANTA CRUZ DA BAIXA VERDE",
    2612505: "SANTA CRUZ DO CAPIBARIBE",
    2612554: "SANTA FILOMENA",
    2612604: "SANTA MARIA DA BOA VISTA",
    2612703: "SANTA MARIA DO CAMBUCA",
    2612802: "SANTA TEREZINHA",
    2612901: "SAO BENEDITO DO SUL",
    2613008: "SAO BENTO DO UNA",
    2613107: "SAO CAITANO",
    2613206: "SAO JOAO",
    2613305: "SAO JOAQUIM DO MONTE",
    2613404: "SAO JOSE DA COROA GRANDE",
    2613503: "SAO JOSE DO BELMONTE",
    2613602: "SAO JOSE DO EGITO",
    2613701: "SAO LOURENCO DA MATA",
    2613800: "SAO VICENTE FERRER",
    2613909: "SERRA TALHADA",
    2614006: "SERRITA",
    2614105: "SERTANIA",
    2614204: "SIRINHAÉM",
    2614303: "MOREILANDIA",
    2614402: "SOLIDAO",
    2614501: "SURUBIM",
    2614600: "TABIRA",
    2614709: "TACAIMBO",
    2614808: "TACARATU",
    2614857: "TAMANDARE",
    2615003: "TAQUARITINGA DO NORTE",
    2615102: "TEREZINHA",
    2615201: "TERRA NOVA",
    2615300: "TIMBAUBA",
    2615409: "TORITAMA",
    2615508: "TRACUNHAEM",
    2615607: "TRINDADE",
    2615706: "TRIUNFO",
    2615805: "TUPANATINGA",
    2615904: "TUPARETAMA",
    2616001: "VENTUROSA",
    2616100: "VERDEJANTE",
    2616183: "VERTENTE DO LERIO",
    2616209: "VERTENTES",
    2616308: "VICENCIA",
    2616407: "VITORIA DE SANTO ANTAO",
    2616506: "XEXEU",
}

# Estados brasileiros (código IBGE)
BR_ESTADOS_IBGE = {
    11: "RONDÔNIA",
    12: "ACRE",
    13: "AMAZONAS",
    14: "RORAIMA",
    15: "PARÁ",
    16: "AMAPÁ",
    17: "TOCANTINS",
    21: "MARANHÃO",
    22: "PIAUÍ",
    23: "CEARÁ",
    24: "RIO GRANDE DO NORTE",
    25: "PARAÍBA",
    26: "PERNAMBUCO",
    27: "ALAGOAS",
    28: "SERGIPE",
    29: "BAHIA",
    31: "MINAS GERAIS",
    32: "ESPÍRITO SANTO",
    33: "RIO DE JANEIRO",
    35: "SÃO PAULO",
    41: "PARANÁ",
    42: "SANTA CATARINA",
    43: "RIO GRANDE DO SUL",
    50: "MATO GROSSO DO SUL",
    51: "MATO GROSSO",
    52: "GOIÁS",
    53: "DISTRITO FEDERAL",
}

# Municípios-chave para o ASI (Região Metropolitana do Recife + Cabo)
# Códigos baseados na API SIDRA oficial (apisidra.ibge.gov.br)
ASI_MUNICIPIOS_CHAVE = [
    2602902,  # CABO DE SANTO AGOSTINHO
    2611606,  # RECIFE
    2609600,  # OLINDA
    2610707,  # PAULISTA
    2607901,  # JABOATAO DOS GUARARAPES
    2609402,  # MORENO
    2606200,  # GOIANA
    2613701,  # SÃO LOURENÇO DA MATA
    2607208,  # IPOJUCA
    2616407,  # VITORIA DE SANTO ANTAO
    2604106,  # CARUARU
    2611101,  # PETROLINA
    2606002,  # GARANHUNS
]

# Opções de agregação territorial disponíveis
SIDRA_TERRITORIAL_LEVELS = {
    "municipio": {"code": "n6", "label": "Municípios", "default": ASI_MUNICIPIOS_CHAVE},
    "municipio_all": {"code": "n6/all", "label": "Todos os Municípios (Brasil)"},
    "estado": {"code": "n3", "label": "Estados", "default": [26]},  # PE por padrão
    "estado_all": {"code": "n3/all", "label": "Todos os Estados (Brasil)"},
    "all": {"code": "all", "label": "Todas as Estações (Estados + Municípios)"},
}


# ════════════════════════════════════════════════════════════════════════════════
# CLIENTE IBGE SIDRA
# ════════════════════════════════════════════════════════════════════════════════

class IBGE_SIDRA_Client(APIClient):
    """Cliente para IBGE SIDRA API (apisidra.ibge.gov.br)."""

    def __init__(self, config: APIConfig = IBGE_SIDRA_CONFIG):
        super().__init__(config)

    def health_check(self) -> APIResponse:
        """Verifica se a API SIDRA está acessível."""
        # Testa com uma requisição simples de dados (a API antiga não tem endpoint de metadata)
        resp = self.get(
            endpoint="/values/t/9514/p/2022/v/93/n3/26",
            use_cache=False,
        )
        if resp.success:
            return APIResponse(
                success=True,
                data={"status": "healthy", "api": "ibge_sidra"},
                status_code=resp.status_code,
                response_time_ms=resp.response_time_ms,
                correlation_id=resp.correlation_id,
            )
        return resp

    def fetch_data(self, **kwargs: Any) -> APIResponse:
        """Método abstrato obrigatório."""
        return self.fetch_populacao_pe()

    def _build_sidra_url(
        self,
        table_id: str,
        variables: list[str],
        territorial_level: str,
        period: str | None = None,
    ) -> str:
        """Constrói URL para API SIDRA antiga (apisidra.ibge.gov.br).
        
        Formato: /values/t/{table}/p/{period}/v/{variables}/{territorial_level}
        Exemplo: /values/t/9514/p/2022/v/93/n6/2603405
        """
        vars_str = ",".join(variables)
        
        if period:
            endpoint = f"/values/t/{table_id}/p/{period}/v/{vars_str}/{territorial_level}"
        else:
            # Último período disponível
            endpoint = f"/values/t/{table_id}/v/{vars_str}/{territorial_level}"
        
        return endpoint

    def _fetch_table(
        self,
        table_key: str,
        territorial_level: str = "n6",  # n6 = municípios
        municipios: list[int] | None = None,
        period: str | None = None,
    ) -> APIResponse:
        """Busca uma tabela SIDRA completa."""
        if table_key not in SIDRA_TABLES:
            return APIResponse(
                success=False,
                error=f"Tabela desconhecida: {table_key}. Disponíveis: {list(SIDRA_TABLES.keys())}",
            )

        table_info = SIDRA_TABLES[table_key]

        # Determina nível territorial e localidades
        if territorial_level == "n6" and municipios:
            # Municípios específicos
            mun_str = ",".join(str(m) for m in municipios)
            territorial_param = f"n6/{mun_str}"
        elif territorial_level == "n6/all":
            # Todos os municípios
            territorial_param = "n6/all"
        elif territorial_level == "n3" and municipios:
            # Estados específicos
            est_str = ",".join(str(m) for m in municipios)
            territorial_param = f"n3/{est_str}"
        elif territorial_level == "n3/all":
            # Todos os estados
            territorial_param = "n3/all"
        else:
            # Default: municípios-chave do ASI
            mun_str = ",".join(str(m) for m in ASI_MUNICIPIOS_CHAVE)
            territorial_param = f"n6/{mun_str}"

        period_to_use = period or table_info.get("period", "2022")
        variables = table_info["variables"]

        endpoint = self._build_sidra_url(
            table_id=table_info["table_id"],
            variables=variables,
            territorial_level=territorial_param,
            period=period_to_use,
        )

        logger.info(
            f"[ibge_sidra] Buscando tabela {table_info['table_id']} "
            f"({table_info['name']}) - {territorial_param}"
        )

        resp = self.get(endpoint=endpoint, use_cache=True)

        if not resp.success:
            logger.warning(f"[ibge_sidra] Falha: {resp.error}")
            return resp

        # Processa resposta SIDRA (formato específico da API antiga)
        batch_df = self._parse_sidra_response_old_api(resp.data, table_info["table_id"])
        if batch_df is None or batch_df.empty:
            return APIResponse(
                success=False,
                error="Nenhum dado retornado da API",
            )

        return APIResponse(
            success=True,
            data=batch_df,
            status_code=resp.status_code,
            response_time_ms=resp.response_time_ms,
            correlation_id=resp.correlation_id,
        )

    def _parse_sidra_response_old_api(self, data: Any, table_id: str) -> pd.DataFrame | None:
        """Parseia resposta JSON da API antiga SIDRA (apisidra.ibge.gov.br) para DataFrame.
        
        Formato da resposta:
        [
          {NC, NN, MC, MN, V, D1C, D1N, D2C, D2N, D3C, D3N, ...},  # Header
          {NC, NN, MC, MN, V, D1C, D1N, D2C, D2N, D3C, D3N, ...},  # Data rows
          ...
        ]
        
        Colunas chave:
        - V: Valor
        - D1C/D1N: Primeira dimensão (geralmente Ano ou Variável)
        - D2C/D2N: Segunda dimensão (geralmente Variável ou Município)
        - D3C/D3N: Terceira dimensão (geralmente Município ou Estado)
        """
        try:
            if not isinstance(data, list) or len(data) == 0:
                return None

            # Primeira linha é cabeçalho
            header = data[0]
            rows = data[1:]

            if not rows:
                return None

            # Determina qual coluna é Município/Estado e qual é Variável
            # Procura pelas chaves que contêm "Município" ou "Unidade da Federação"
            mun_code_col = None
            mun_name_col = None
            var_code_col = None
            var_name_col = None
            value_col = "V"

            for key, label in header.items():
                if "Município" in label and "(Código)" in label:
                    mun_code_col = key
                elif "Município" in label and "(Código)" not in label:
                    mun_name_col = key
                elif "Unidade da Federação" in label and "(Código)" in label:
                    mun_code_col = key
                elif "Unidade da Federação" in label and "(Código)" not in label:
                    mun_name_col = key
                elif "Variável" in label and "(Código)" in label:
                    var_code_col = key
                elif "Variável" in label and "(Código)" not in label:
                    var_name_col = key

            # Se não encontrou, tenta posições padrão (D2C/D2N ou D3C/D3N)
            if not mun_code_col:
                for key in ["D3C", "D2C"]:
                    if key in header:
                        mun_code_col = key
                        break
            if not mun_name_col:
                for key in ["D3N", "D2N"]:
                    if key in header:
                        mun_name_col = key
                        break
            if not var_code_col:
                for key in ["D2C", "D1C"]:
                    if key in header and key != mun_code_col:
                        var_code_col = key
                        break
            if not var_name_col:
                for key in ["D2N", "D1N"]:
                    if key in header and key != mun_name_col:
                        var_name_col = key
                        break

            results = []

            for row in rows:
                # Extrai valor
                valor_raw = row.get(value_col)
                if valor_raw in ("-", "...", "", None):
                    valor_num = None
                else:
                    try:
                        valor_num = float(valor_raw)
                    except (ValueError, TypeError):
                        valor_num = None

                # Extrai código e nome do município/estado
                if mun_code_col and mun_code_col in row:
                    try:
                        municipio_cod = int(row[mun_code_col])
                    except (ValueError, TypeError):
                        municipio_cod = row[mun_code_col]
                else:
                    municipio_cod = None

                municipio_nome = row.get(mun_name_col, "") if mun_name_col else ""

                # Extrai variável
                variavel = row.get(var_code_col, "") if var_code_col else ""
                variavel_nome = row.get(var_name_col, "") if var_name_col else ""

                results.append({
                    "municipio_codigo": municipio_cod,
                    "municipio_nome": municipio_nome,
                    "variavel_codigo": variavel,
                    "variavel_nome": variavel_nome,
                    "valor": valor_num,
                })

            if not results:
                return None

            df = pd.DataFrame(results)
            return df

        except Exception as e:
            logger.exception(f"[ibge_sidra] Erro parseando resposta tabela {table_id}: {e}")
            return None

    def _pivot_sidra_data(self, df: pd.DataFrame, value_col: str = "valor") -> pd.DataFrame:
        """Transforma dados longos SIDRA para wide (uma linha por município)."""
        if df.empty:
            return df

        # Pivot: uma coluna por variável
        pivoted = df.pivot_table(
            index=["municipio_codigo", "municipio_nome"],
            columns="variavel_codigo",
            values=value_col,
            aggfunc="first",
        ).reset_index()

        # Achatamento de colunas multi-nível
        pivoted.columns = [str(c) for c in pivoted.columns]
        return pivoted

    def fetch_populacao_pe(
        self,
        territorial_level: str = "n6",
        municipios: list[int] | None = None,
    ) -> APIResponse:
        """Busca população total por município (Censo 2022)."""
        resp = self._fetch_table(
            "populacao_2022",
            territorial_level=territorial_level,
            municipios=municipios,
        )

        if not resp.success or resp.data is None or resp.data.empty:
            return APIResponse(
                success=False,
                error=resp.error or "Dados de população vazios",
            )

        df = resp.data
        df_pivot = self._pivot_sidra_data(df)

        # Renomeia coluna da variável 93 (população total)
        if "93" in df_pivot.columns:
            df_pivot = df_pivot.rename(columns={"93": "populacao_total"})
            df_pivot["populacao_total"] = df_pivot["populacao_total"].astype("Int64")

        # Adiciona nome normalizado para joins
        df_pivot["municipio"] = df_pivot["municipio_nome"].str.upper().str.strip()

        # Valida com schema
        df_validated = validate_or_warn(df_pivot, SidraPopulacaoSchema, "sidra_populacao")

        logger.info(f"[ibge_sidra] População: {len(df_validated)} municípios carregados")

        return APIResponse(
            success=True,
            data=df_validated,
            status_code=resp.status_code,
            response_time_ms=resp.response_time_ms,
            correlation_id=resp.correlation_id,
        )

    def fetch_saneamento_pe(
        self,
        territorial_level: str = "n6",
        municipios: list[int] | None = None,
    ) -> APIResponse:
        """Busca saneamento por município (Censo 2022)."""
        resp = self._fetch_table(
            "saneamento_2022",
            territorial_level=territorial_level,
            municipios=municipios,
        )

        if not resp.success or resp.data is None or resp.data.empty:
            return APIResponse(
                success=False,
                error=resp.error or "Dados de saneamento vazios",
            )

        df = resp.data
        df_pivot = self._pivot_sidra_data(df)

        # Variáveis: 381 = Total domicílios, 1000381 = % do total
        # Para calcular % adequado, precisamos das variáveis de saneamento específico
        # A tabela 9860 tem muitas classificações. Para % adequado, usamos a variável
        # que representa domicílios com saneamento adequado
        
        # Por enquanto, usamos 381 (total) e 1000381 (%)
        if "381" in df_pivot.columns and "1000381" in df_pivot.columns:
            df_pivot["dom_total"] = df_pivot["381"].astype(float)
            df_pivot["dom_adequado_pct"] = df_pivot["1000381"].astype(float)
            df_pivot["perc_saneamento_adequado"] = df_pivot["dom_adequado_pct"].round(2)

        df_pivot["municipio"] = df_pivot["municipio_nome"].str.upper().str.strip()

        df_validated = validate_or_warn(df_pivot, SidraSaneamentoSchema, "sidra_saneamento")

        logger.info(f"[ibge_sidra] Saneamento: {len(df_validated)} municípios carregados")

        return APIResponse(
            success=True,
            data=df_validated,
            status_code=resp.status_code,
            response_time_ms=resp.response_time_ms,
            correlation_id=resp.correlation_id,
        )

    def fetch_consolidado_pe(
        self,
        territorial_level: str = "n6",
        municipios: list[int] | None = None,
    ) -> APIResponse:
        """Busca dataset consolidado: população + saneamento + vulnerabilidade."""
        # Busca população
        pop_resp = self.fetch_populacao_pe(territorial_level, municipios)
        if not pop_resp.success:
            return pop_resp

        # Busca saneamento
        san_resp = self.fetch_saneamento_pe(territorial_level, municipios)
        if not san_resp.success:
            return san_resp

        # Merge
        pop_df = pop_resp.data[["municipio", "populacao_total"]].copy()
        san_df = san_resp.data[["municipio", "perc_saneamento_adequado"]].copy()

        merged = pop_df.merge(san_df, on="municipio", how="left")

        # Calcula vulnerabilidade baseada em saneamento + população
        # Lógica: menor saneamento + maior população = maior vulnerabilidade
        merged["perc_vulnerabilidade"] = (
            (100 - merged["perc_saneamento_adequado"].fillna(50))
            * (merged["populacao_total"] / merged["populacao_total"].max())
        ).round(2)

        # Classifica
        def classificar_vuln(row):
            if row["perc_vulnerabilidade"] >= 70:
                return "CRITICA"
            elif row["perc_vulnerabilidade"] >= 50:
                return "ALTA"
            elif row["perc_vulnerabilidade"] >= 30:
                return "MODERADA"
            elif row["perc_vulnerabilidade"] >= 15:
                return "BAIXA"
            return "SEM DADOS"

        merged["classe_vulnerabilidade"] = merged.apply(classificar_vuln, axis=1)

        df_validated = validate_or_warn(merged, SidraConsolidadoSchema, "sidra_consolidado")

        logger.info(f"[ibge_sidra] Consolidado: {len(df_validated)} municípios")

        return APIResponse(
            success=True,
            data=df_validated,
            status_code=200,
        )

    def fetch_estados_consolidado(
        self,
        table_key: str = "populacao_2022",
    ) -> APIResponse:
        """Busca dados consolidados por Estado (n3/all)."""
        return self._fetch_table(
            table_key,
            territorial_level="n3/all",
        )

    def fetch_all_stations(
        self,
        table_key: str = "populacao_2022",
    ) -> APIResponse:
        """Busca 'Todas as Estações': Estados + Municípios consolidados.
        
        Retorna um dicionário com:
        - 'estados': DataFrame com dados por estado (n3/all)
        - 'municipios': DataFrame com dados por município (n6/all ou n6/PE)
        - 'consolidado': DataFrame unificado com indicador de nível
        """
        resultados = {}
        
        # 1. Busca por Estados
        logger.info(f"[ibge_sidra] Buscando Estados para tabela {table_key}")
        estados_resp = self._fetch_table(table_key, territorial_level="n3/all")
        if estados_resp.success and estados_resp.data is not None:
            resultados["estados"] = estados_resp.data
            logger.info(f"[ibge_sidra] Estados: {len(estados_resp.data)} registros")
        else:
            logger.warning(f"[ibge_sidra] Falha ao buscar estados: {estados_resp.error}")
            resultados["estados"] = pd.DataFrame()

        # 2. Busca por Municípios (todos do Brasil - pode ser pesado)
        # Para performance, vamos buscar só PE (n3/26) que expande para n6 dos municípios de PE
        logger.info(f"[ibge_sidra] Buscando Municípios PE para tabela {table_key}")
        municipios_resp = self._fetch_table(table_key, territorial_level="n3/26")
        if municipios_resp.success and municipios_resp.data is not None:
            resultados["municipios"] = municipios_resp.data
            logger.info(f"[ibge_sidra] Municípios PE: {len(municipios_resp.data)} registros")
        else:
            logger.warning(f"[ibge_sidra] Falha ao buscar municípios: {municipios_resp.error}")
            resultados["municipios"] = pd.DataFrame()

        # 3. Cria consolidado unificado
        consolidated_rows = []
        
        if not resultados["estados"].empty:
            df_est = resultados["estados"].copy()
            df_est["nivel_territorial"] = "Estado"
            consolidated_rows.append(df_est)
        
        if not resultados["municipios"].empty:
            df_mun = resultados["municipios"].copy()
            df_mun["nivel_territorial"] = "Município"
            consolidated_rows.append(df_mun)
        
        if consolidated_rows:
            resultados["consolidado"] = pd.concat(consolidated_rows, ignore_index=True)
        else:
            resultados["consolidado"] = pd.DataFrame()

        return APIResponse(
            success=len(resultados["consolidado"]) > 0,
            data=resultados,
            status_code=200 if resultados["consolidado"].shape[0] > 0 else 404,
        )


# ════════════════════════════════════════════════════════════════════════════════
# FUNÇÕES CACHED PARA STREAMLIT
# ════════════════════════════════════════════════════════════════════════════════

@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando população Censo 2022 (IBGE SIDRA)...")
def fetch_populacao_pe_cached() -> APIResponse:
    """Função cached para Streamlit - população PE."""
    client = IBGE_SIDRA_Client()
    return client.fetch_populacao_pe()


@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando saneamento Censo 2022 (IBGE SIDRA)...")
def fetch_saneamento_pe_cached() -> APIResponse:
    """Função cached para Streamlit - saneamento PE."""
    client = IBGE_SIDRA_Client()
    return client.fetch_saneamento_pe()


@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando dataset consolidado (IBGE SIDRA)...")
def fetch_sidra_consolidado_cached() -> APIResponse:
    """Função cached para Streamlit - consolidado PE."""
    client = IBGE_SIDRA_Client()
    return client.fetch_consolidado_pe()


@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando dados IBGE SIDRA para todos os municípios PE...")
def fetch_sidra_todos_municipios_pe_cached(table_key: str = "populacao_2022") -> APIResponse:
    """Busca tabela para todos os municípios de PE (n3/26 expande para n6)."""
    client = IBGE_SIDRA_Client()
    return client._fetch_table(table_key, territorial_level="n3/26")


@streamlit_cache_data(ttl_seconds=86400, show_spinner="Carregando 'Todas as Estações' (Estados + Municípios)...")
def fetch_sidra_todas_estacoes_cached(table_key: str = "populacao_2022") -> APIResponse:
    """Busca 'Todas as Estações': Estados + Municípios consolidados."""
    client = IBGE_SIDRA_Client()
    return client.fetch_all_stations(table_key)