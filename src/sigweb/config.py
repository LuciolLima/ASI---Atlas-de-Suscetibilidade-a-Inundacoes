"""
SISTEMA ASI - MÓDULO DE CONFIGURAÇÃO GLOBAL
Versão: 2.8 — Precipitação, Hidrografia, Eventos Históricos, Exportação
"""

import os

# --- Configurações de UI ---
PAGE_TITLE = "ASI | Sistema de Análise de Suscetibilidade"
PAGE_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# --- Caminhos de Arquivos ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# v2.7 — Dados originais
PATH_DATA_TABLE = os.path.join(BASE_DIR, 'data', 'curated', 'attribute_tables', 'data_table.txt')
PATH_GEOJSON    = os.path.join(BASE_DIR, 'data', 'raw', 'arcmap_exports', 'pe_municipios_2024.json')

# v2.9 — Bairros do Cabo (uso futuro — expansão por município)
PATH_BAIRROS    = os.path.join(BASE_DIR, 'data', 'raw', 'arcmap_exports', 'bairros_cabo_oficial.json')

# v2.8 — Dados novos (sistema os.path.exists() antes de usar — nunca quebra se não existir)
PATH_PRECIPITACAO = os.path.join(BASE_DIR, 'data', 'raw', 'apac_exports', 'precipitacao_pernambuco.csv')
PATH_HIDROGRAFIA  = os.path.join(BASE_DIR, 'data', 'raw', 'qgis_exports', 'Hidrografia_Pernambuco.geojson')
PATH_EVENTOS        = os.path.join(BASE_DIR, 'data', 'raw', 'events', 'historico_inundacoes.csv')
PATH_DEFESA_CIVIL   = os.path.join(BASE_DIR, 'data', 'raw', 'events', 'defesacivil_pe_consolidado.csv')

# --- Parâmetros Técnicos (TWI) ---
TWI_THRESHOLD_LOW      = 4.0
TWI_THRESHOLD_MODERATE = 8.0
TWI_THRESHOLD_HIGH     = 12.0
TWI_THRESHOLD_CRITICAL = 16.0

# --- Identidade Visual ---
COLORS = {
    'CRITICO':    '#8B0000',
    'ALTO':       '#FF4500',
    'MODERADO':   '#FFD700',
    'BAIXO':      '#1E90FF',
    'MUITO_BAIXO':'#ADD8E6',
    'NEUTRO':     '#808080'
}

# v2.8 — Cores para camadas novas
COLOR_HIDROGRAFIA = '#00BFFF'
COLORS_EVENTOS = {
    'GRAVE':        '#FF1493',
    'MODERADA':     '#FF8C00',
    'LEVE':         '#FFD700',
    'NÃO INFORMADA':'#AAAAAA'
}

# --- Dicionários de Tradução ---
CLASS_LABELS = {
    'CRITICO':    'Crítico (Saturação Imediata)',
    'ALTO':       'Alto (Potencial de Alagamento)',
    'MODERADO':   'Moderado (Atenção)',
    'BAIXO':      'Baixo (Escoamento)',
    'MUITO_BAIXO':'Muito Baixo (Divisor)'
}

MAPBIOMAS_CODES = {
    3:  'Formação Florestal',
    15: 'Pastagem',
    24: 'Infraestrutura Urbana',
    25: 'Área Não Vegetada',
    33: 'Corpo Hídrico',
    9:  'Silvicultura',
    21: 'Mosaico Agricultura/Pastagem'
}

IBGE_SITUACAO_CODES = {
    1: 'Urbana (Alta Densidade)',
    2: 'Urbana (Baixa Densidade)',
    8: 'Rural',
    9: 'Núcleo Isolado'
}

MAX_POINTS_DISPLAY = 3000

# --- Estrutura esperada nos CSVs novos (documentação interna) ---
# precipitacao_historica.csv        →  data;estacao;precipitacao_mm;latitude;longitude
# historico_inundacoes.csv          →  data;bairro;descricao;severidade;latitude;longitude;fonte
# defesacivil_pe_consolidado.csv    →  municipio;latitude;longitude;periodo;fonte;severidade;
#                                       registros;dh_obitos;dh_desabrigados;dh_desalojados;
#                                       dh_feridos;dh_total;dm_total;dm_estradas;dm_comercial;
#                                       dm_residencial;dm_est_ensino;dm_industrial;dm_p_publico;
#                                       dm_area_prot_amb;dm_estab_saude;dm_pontes;dm_outros