
# DOCUMENTAÇÃO TÉCNICA E METODOLÓGICA (DTM)

## Sistema ASI – Atlas de Suscetibilidade a Inundações

### 1. Introdução e Justificativa

O Sistema ASI (Atlas de Suscetibilidade a Inundações) constitui uma ferramenta de suporte à decisão desenvolvida para mitigar os impactos de eventos hidrológicos extremos no município do Cabo de Santo Agostinho. Diante do cenário de mudanças climáticas e do avanço da urbanização sobre planícies de inundação, o projeto aplica métodos de Ciência de Dados Espaciais para transformar dados altimétricos em inteligência territorial. O objetivo central é fornecer subsídios técnicos para a otimização de infraestruturas públicas e a salvaguarda da população em áreas de vulnerabilidade.

### 2. Fundamentação Teórica e Modelagem Matemática

O modelo computacional baseia-se no Índice Topográfico de Umidade (do inglês, *Topographic Wetness Index* - TWI). Este índice de estado estacionário quantifica a tendência de acúmulo de água no solo, estabelecendo uma relação matemática entre a área de captação e a capacidade de escoamento superficial.

A formulação do TWI depende diretamente de duas variáveis geomorfométricas fundamentais:

* **Área de Contribuição Específica (**$a$**):** Representa o acúmulo de fluxo a montante, calculado por meio de algoritmos de direção de fluxo que modelam a convergência topográfica das encostas.
* **Tangente da Declividade (**$\tan \beta$**):** Atua como o gradiente hidráulico local. Em terrenos com inclinação próxima a zero, a minimização do denominador resulta em valores exponenciais de TWI, indicando zonas de alta propensão à saturação hídrica.

### 3. Arquitetura do Sistema e Engenharia de Dados (Pipeline ETL)

A infraestrutura de processamento foi projetada segundo os padrões de processamento de Big Data Geospacial, estruturando-se em três camadas fundamentais:

#### 3.1. Ingestão e Extração de Dados (Extract)

A leitura de extensas tabelas de atributos vetoriais é operacionalizada por meio da biblioteca  **Pandas** . Esta abordagem garante alta eficiência no processamento de milhares de amostras em lote, assegurando a integridade dos dados durante a etapa de *parsing* e minimizando a perda de informações altimétricas.

#### 3.2. Transformação e Processamento Espacial (Transform)

As rotinas de geoprocessamento avançado englobam:

* **Transformação de Sistemas de Referência de Coordenadas (CRS):** Utilização da biblioteca **PyProj** para a reprojeção automatizada de coordenadas planas (UTM) para o sistema geodésico WGS84. Este procedimento é imperativo para a sobreposição precisa dos dados analíticos sobre bases cartográficas globais em plataformas web.
* **Normalização e Classificação Estatística:** Tendo em vista a variância logarítmica inerente ao TWI, aplicam-se filtros estatísticos para discretizar os resultados contínuos em cinco classes de suscetibilidade. Esta categorização viabiliza a geração de mapas de calor qualitativos (variando de suscetibilidade baixa a crítica).

#### 3.3. Carregamento e Renderização (Load)

A visualização geoespacial é implementada sob a interface  **Folium/Leaflet** . O uso deste motor de renderização garante otimização de performance via aceleração de hardware nos navegadores, permitindo a fluidez na interação com mapas dinâmicos e vetores complexos, inclusive em dispositivos móveis.

### 4. Integração de Dados e Matriz Institucional

O rigor analítico do Sistema ASI é sustentado pela integração de múltiplas bases de dados oficiais:

* **Modelo Digital de Elevação (MDE):** Dados topográficos basais adquiridos via sensores SRTM ( *Shuttle Radar Topography Mission* ).
* **Dados Pluviométricos (APAC):** Séries históricas de precipitação empregadas na calibração e validação dos limiares críticos de escoamento.
* **Cobertura do Solo (MapBiomas):** Mapeamento do uso e ocupação do solo, vital para identificar zonas de alta impermeabilização antrópica que potencializam a suscetibilidade inerente ao relevo.

### 5. Metodologia de Geoprocessamento

O fluxo de trabalho metodológico para a geração da cartografia de suscetibilidade obedece às seguintes etapas padronizadas:

1. **Aquisição de Dados:** Extração vetorial e tabular de modelos altimétricos.
2. **Pré-processamento Geométrico:** Identificação e preenchimento de depressões espúrias ( *sink fill* ) no MDE, mitigando falsos positivos na modelagem hidrológica.
3. **Matriz de Direção de Fluxo:** Determinação do roteamento hídrico entre as células da matriz matricial.
4. **Modelagem Matemática:** Cômputo do algoritmo TWI sobre a grade processada.
5. **Análise Estatística:** Classificação dos níveis de suscetibilidade adotando a divisão por quartis.
6. **Saída Cartográfica:** Renderização geoestatística para a interface do usuário final.

### 6. Limitações do Modelo e Considerações Finais

O Sistema ASI constitui um modelo de base hidrogeomorfométrica, projetado para apontar as tendências de acúmulo de água baseadas unicamente nas condicionantes do relevo. Sendo assim, o sistema apresenta limitações naturais quanto à modelagem de inundações provocadas por colapsos de infraestrutura urbana, tais como falhas no sistema de microdrenagem ou rompimentos de tubulações. Ressalta-se que a ferramenta possui caráter estritamente analítico e de suporte à pesquisa, devendo as ações de intervenção civil ou planos de evacuação serem deliberados exclusivamente pelos órgãos oficiais de Defesa Civil.

### 7. Perspectivas Futuras (Roadmap de Pesquisa)

O escopo evolutivo do projeto prevê as seguintes atualizações tecnológicas:

* **Versão 4.0:** Incorporação de algoritmos de Aprendizado de Máquina, especificamente o modelo  *Random Forest* , para análises preditivas.
* **Versão 4.1:** Conexão direta com redes de sensores telemétricos de nível de rio via Internet das Coisas (IoT).
* **Versão 6.0:** Desenvolvimento de um módulo hidrodinâmico para a simulação de manchas de inundação baseadas em Tempos de Retorno (TR) de 10, 50 e 100 anos.

### 8. Referências Técnicas e Institucionais

* **Orientação:** Dr. Renilson (Pesquisador Especialista em Análise Ambiental e Geoprocessamento).
* **Orientação Escolar:** Prof.ª Bruna Kelly (Professora de Biologia), Prof.ª Gabrielly Simões (Professora de Química), Prof. Renilson Ramos (Professor em Geografia).
* **Pesquisa e Desenvolvimento:** Lúcio (Implementação Algorítmica e Engenharia de Dados).
* **Fontes de Dados:** IBGE, APAC, Prefeitura Municipal do Cabo de Santo Agostinho, Google Earth Engine.
* **Referência Teórica Principal:** Beven, K. J., & Kirkby, M. J. (1979).  *A physically based, variable contributing area model of basin hydrology* . Hydrological Sciences Bulletin.
