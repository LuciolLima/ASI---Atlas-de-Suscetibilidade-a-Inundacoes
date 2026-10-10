# Instituições, Órgãos e Fontes de Dados — ASI Atlas de Suscetibilidade a Inundações

---

## Introdução

O **ASI — Atlas de Suscetibilidade a Inundações** é um Sistema de Informação Geográfica para a Web (SIGWeb) desenvolvido com o objetivo de modelar a propensão natural do terreno ao acúmulo hídrico no município do Cabo de Santo Agostinho, Pernambuco. A construção de um sistema desta natureza exige a integração de múltiplas fontes de dados oficiais, produtos de sensoriamento remoto, bases cartográficas municipais e estaduais, além de séries históricas meteorológicas e registros de eventos extremos.

Este documento consolida, de forma estruturada e transparente, o reconhecimento a todas as instituições, órgãos públicos, agências de fomento e projetos científicos cujos dados, infraestrutura ou apoio financeiro tornaram possível a concepção, desenvolvimento e operação do ASI. O crédito devido não é apenas uma exigência ética e legal — é o reconhecimento do ecossistema colaborativo que sustenta a ciência aberta e a gestão de riscos baseada em evidências.

---

## Desenvolvimento

### 1. Fontes Oficiais de Dados Geoespaciais e Socioeconômicos

#### **IBGE — Instituto Brasileiro de Geografia e Estatística**

O IBGE é a pedra angular da infraestrutura de dados do ASI. Duas frentes principais foram utilizadas:

- **API SIDRA (apisidra.ibge.gov.br)** — A API legada do Sistema IBGE de Recuperação Automática fornece dados do Censo Demográfico 2022 em nível municipal: população total (Tabela 9514), saneamento adequado (Tabela 9860), rendimento médio (Tabela 5939) e escolaridade (Tabela 9515). Estes indicadores compõem o índice de vulnerabilidade social integrado ao modelo de suscetibilidade.
- **Malhas Territoriais Oficiais** — Setores censitários e divisões intramunicipais (shapefiles/GeoJSON) servem de base para a agregação espacial e validação das geometrias de bairros.
- **Distribuição SRTM** — O IBGE atua como nó de distribuição nacional dos dados SRTM (ver item 3), garantindo acesso livre ao modelo digital de elevação.

#### **APAC — Agência Pernambucana de Águas e Clima**

A APAC fornece a base hidrológica e pluviométrica do sistema:

- Série histórica de precipitação por estação (dados mensais e diários) para o estado de Pernambuco.
- Parâmetros de bacias hidrográficas e limites de drenagem que subsidiam os limiares hidrológicos do TWI.
- Modelagem de eventos extremos e balanço hídrico regional.

#### **SEPDEC — Secretaria de Políticas de Prevenção e Defesa Civil de Pernambuco**

O dataset consolidado `defesacivil_pe_consolidado.csv` contém registros oficiais de ocorrências de inundação (2024–2026) por município, com severidade (GRAVE, MODERADA, LEVE), quantitativos de desabrigados, desalojados, óbitos e danos materiais. Estes dados validam empiricamente as classes de risco do ASI e alimentam o painel de correlação TWI × Defesa Civil.

#### **INMET — Instituto Nacional de Meteorologia**

Dados meteorológicos de superfície (temperatura, umidade, vento, precipitação) das estações convencionais e automáticas em Pernambuco complementam a base APAC e são acessados via integração programática para séries históricas e previsão.

#### **Prefeitura Municipal do Cabo de Santo Agostinho**

A base cartográfica oficial do município — `bairros_cabo_oficial.json` (EPSG:31985/SIRGAS 2000 UTM 24S) — define a granularidade espacial do sistema: 92 bairros com geometrias validadas, atributos de nome e códigos oficiais. É a camada de referência para recortes espaciais, estatísticas por bairro e exportações.

#### **SEINFRA-PE — Secretaria de Infraestrutura do Estado de Pernambuco**

Diretrizes de macrozoneamento, rede viária estadual e estudos de infraestrutura hídrica subsidiam a contextualização do uso do solo e a interpretação dos padrões de suscetibilidade em escala regional.

#### **CONDEPE-FIDEM — Agência Estadual de Planejamento e Pesquisas de Pernambuco**

Estudos de planejamento territorial, relatórios de macrozoneamento ambiental e inteligência espacial sobre a Região Metropolitana do Recife fornecem o enquadramento político-administrativo e cenários futuros de ocupação.

---

### 2. Fontes de Sensoriamento Remoto e Produtos Científicos Globais

#### **MapBiomas — Projeto MapBiomas (mapbiomas.org)**

A Coleção 10 (1985–2024, 30m) e a Coleção 2 beta (2016–2023, 10m, Sentinel-2) fornecem a classificação de cobertura e uso da terra (LULC) que alimenta o atributo `Uso_Solo_Desc` no dataset principal. Classes utilizadas:

- 3  – Formação Florestal
- 9  – Silvicultura
- 15 – Pastagem
- 21 – Mosaico Agricultura/Pastagem
- 24 – Infraestrutura Urbana
- 25 – Área Não Vegetada
- 33 – Corpo Hídrico

A acurácia por classe e bioma (documentada em `references/articles.md`) embasa a ponderação de uso do solo no índice de risco.

#### **SRTM — Shuttle Radar Topography Mission (NASA / USGS / NGA)**

O Modelo Digital de Elevação (DEM) global a 30m de resolução (SRTM v4.1 / SRTMGL1) é a base altimétrica para o cálculo do **Topographic Wetness Index (TWI)**:

- Declividade (slope) via algoritmo de Horn (3×3 window)
- Área de contribuição específica (flow accumulation) via D8/D-infinity
- TWI = ln(α / tan β) onde α = área de contribuição por unidade de largura, β = declividade

O acesso deu-se via canais de distribuição do IBGE, garantindo cobertura nacional contínua e licenciamento aberto.

#### **NASA POWER — Prediction Of Worldwide Energy Resources (power.larc.nasa.gov)**

Dados de reanálise MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, Version 2) provêm variáveis agrometeorológicas diárias para 11 estações de referência em PE:

- Precipitação corrigida (PRECTOTCORR)
- Temperatura (T2M, T2M_MAX, T2M_MIN, T2MDEW)
- Umidade relativa (RH2M) e específica (QV2M)
- Umidade do solo em 3 camadas (GWETTOP, GWETROOT, GWETPROF)
- Radiação solar (ALLSKY_SFC_SW_DWN, CLRSKY_SFC_SW_DWN)
- Vento (WS10M, WS50M, WD10M, WD50M)
- Pressão de superfície (PS)

Estes dados alimentam o painel de séries históricas, o cálculo de índice de saturação do solo e a correlação com eventos de inundação.

---

### 3. Fomento à Pesquisa e Bolsas de Iniciação Científica e Tecnológica

O desenvolvimento do ASI foi viabilizado por bolsas de Iniciação Científica e Tecnológica (IC/IT) concedidas pelas seguintes agências de fomento, que permitiram a dedicação discente e a aquisição de infraestrutura computacional:

| Agência            | Programa / Modalidade                                  | Papel no ASI                                                                                           |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| **FACEPE**    | PIBIC / PIBITI / BIC-JR                                | Bolsas de iniciação científica e tecnológica (estadual); apoio a eventos e publicações.          |
| **CNPq**      | PIBIC / PIBITI / PIC                                   | Bolsas federais de iniciação científica; cota de bolsas institucionais.                             |
| **CAPES**     | PROEX / DS / PROSUP                                    | Apoio a programas de pós-graduação stricto sensu; bolsas de mestrado/doutorado correlatas.          |
| **METRO SUL** | Programa de Inovação Metropolitana                   | Fomento a projetos aplicados à Região Metropolitana do Recife; integração com planejamento urbano. |
| **GRE**       | Grupo de Recursos Educacionais / Inovação Acadêmica | Infraestrutura de laboratório, licenças de software, suporte técnico e administrativo.              |

> **Nota:** A combinação dessas fontes de fomento permitiu a formação de equipe multidisciplinar (geografia, ciência da computação, engenharia civil, meteorologia) e a aquisição de recursos computacionais (GPU, armazenamento, licenças) essenciais para o processamento de grandes volumes de dados geoespaciais (GeoParquet, raster, vetoriais).


### 4. Tecnologias de Código Aberto (Open Source) — Créditos Técnicos

Embora não sejam "instituições" no sentido estrito, as seguintes comunidades e projetos de software livre são a base tecnológica do ASI e merecem reconhecimento explícito:

| Projeto                                     | Uso no ASI                                               |
| ------------------------------------------- | -------------------------------------------------------- |
| **Streamlit**                         | Framework principal da aplicação web                   |
| **Folium / Leaflet.js**               | Renderização de mapas interativos (motor folium)       |
| **Deck.gl + MapLibre GL**             | Componente React customizado (AsiMap) para WebGL 60fps   |
| **DuckDB + Polars + PyArrow**         | Camada de dados OLAP colunar, GeoParquet, queries sub-ms |
| **GeoPandas / Shapely / PyProj**      | Operações vetoriais, reprojeção, topologia           |
| **Pandas / NumPy / Plotly**           | Análise tabular, estatística, visualização           |
| **Pandera**                           | Validação de schemas de DataFrame (contratos de dados) |
| **OpenTelemetry / Prometheus Client** | Observabilidade (traces, metrics, logs)                  |
| **Vite / TypeScript / React**         | Build do componente AsiMap                               |
| **sidrapy**                           | Cliente Python para API SIDRA/IBGE                       |
| **gdown**                             | Download de assets do GitHub Releases                    |

---

## Conclusão

O ASI — Atlas de Suscetibilidade a Inundações não é produto de um único autor ou instituição, mas o resultado da convergência de **dados públicos de qualidade**, **infraestrutura de fomento à pesquisa** e **ecossistema de software livre maduro**. Cada camada do sistema — da base altimétrica (SRTM/IBGE) à validação empírica (SEPDEC/APAC), do uso do solo (MapBiomas) à vulnerabilidade social (IBGE SIDRA), do fomento discente (FACEPE/CNPq/CAPES/METRO SUL/GRE) à instituição formadora (FACEPE) — representa um elo indispensável na cadeia de valor que transforma dados brutos em informação acionável para a gestão de riscos de inundação.

Este documento visa garantir a **rastreabilidade**, a **reprodutibilidade** e a **transparência** do projeto, assegurando que qualquer usuário, auditor, pesquisador ou gestor público possa identificar a proveniência de cada dado, a licença de uso aplicável e a quem creditar em eventuais derivações, publicações ou políticas públicas baseadas no ASI.

---

## Agradecimentos e Créditos Finais

> **Aos órgãos públicos e instituições provedoras de dados oficiais,** pelo compromisso com a transparência, a abertura de dados e a manutenção de APIs e portais que permitem o acesso programático, confiável e gratuito à informação geoespacial e socioeconômica brasileira:
>
> - **IBGE** (Instituto Brasileiro de Geografia e Estatística)
> - **APAC** (Agência Pernambucana de Águas e Clima)
> - **SEPDEC** (Secretaria de Políticas de Prevenção e Defesa Civil de PE)
> - **INMET** (Instituto Nacional de Meteorologia)
> - **MapBiomas** (Projeto MapBiomas — Iniciativa multi-institucional)
> - **SRTM** (NASA / USGS / NGA — via distribuição IBGE)
> - **Prefeitura Municipal do Cabo de Santo Agostinho**
> - **SEINFRA-PE** (Secretaria de Infraestrutura de Pernambuco)
> - **CONDEPE-FIDEM** (Agência Estadual de Planejamento e Pesquisas de PE)
> - **NASA POWER** (Prediction Of Worldwide Energy Resources — NASA LaRC)
>
> **Às agências de fomento,** por acreditarem na formação de recursos humanos qualificados e no potencial de inovação tecnológica aplicada a problemas reais da sociedade:
>
> - **FACEPE** (Fundação de Amparo à Ciência e Tecnologia do Estado de Pernambuco)
> - **CNPq** (Conselho Nacional de Desenvolvimento Científico e Tecnológico)
> - **CAPES** (Coordenação de Aperfeiçoamento de Pessoal de Nível Superior)
> - **METRO SUL** (Programa de Inovação Metropolitana / Região Metropolitana do Recife)
> - **GRE** (Grupo de Recursos Educacionais / Inovação Acadêmica)
>
>
> **Às comunidades de software livre,** cuja colaboração global torna viável, acessível e auditável a construção de sistemas complexos como o ASI:
>
> - Streamlit, Folium, Deck.gl, MapLibre, DuckDB, Polars, GeoPandas, Pandera, OpenTelemetry, Prometheus, Vite, React, TypeScript, sidrapy, gdown, e centenas de outras bibliotecas listadas em `requirements.txt` e `pyproject.toml`.
>
> **Aos revisores, testadores e usuários iniciais,** cujo feedback contínuo aprimora a usabilidade, a robustez e a relevância científica do sistema.
>
> ---
>
> **Autor principal / Desenvolvedor:** Lucio Luiz de Lima
> **Instituição:** EEFSL - Escola Estadual Fernando Soares Lyra
> **Repositório:** https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes
> **Licença:** MIT (código) / CC-BY-4.0 (dados derivados, respeitando licenças das fontes originais) - APACHE 2.0
> **Versão do documento:** DCMD-v3.3.01 — Setembro 2026
>
> *Este documento deve ser atualizado a cada nova versão do ASI que incorpore fontes de dados, instituições parceiras ou agências de fomento adicionais.*
