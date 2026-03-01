"""
SISTEMA ASI - DOCUMENTAÇÃO E RESPONSABILIDADE TÉCNICA
Módulo responsável pela exibição do dossiê metodológico e fontes de dados espaciais.
"""

import streamlit as st
import os

def load_academic_md():
    """Lê o arquivo de documentação pesada."""
    # Caminho base para a sua pasta Docs
    path = "Docs/academic_context/DTM_doc.md"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "O Arquivo `DTM_doc.md` não foi encontrado na pasta de documentação acadêmica. Por favor, atualize a página e se o problema persistir, entre em contato com o administrador do sistema."

def render_technical_docs():
    st.markdown("---")
    st.subheader("Documentação Técnica e Metodológica (DTM)")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Fundamentação Algorítmica (TWI)", 
        "Pipeline de Geoprocessamento (ETL)",
        "Ecossistema de Dados Oficiais", 
        "Termo de Responsabilidade",
        "Documentação Técnica Complementar (Markdown)"
    ])
    
    # ABA 1: METODOLOGIA MATEMÁTICA E FÍSICA
    with tab1:
        st.markdown("**Índice Topográfico de Umidade (Topographic Wetness Index - TWI)**")
        st.write(
            "O Sistema ASI embasa sua modelagem preditiva no TWI, um descritor físico-matemático "
            "que quantifica o controle topográfico sobre processos hidrológicos. Diferente de abordagens "
            "puramente estocásticas, o algoritmo fundamenta-se nas propriedades geomorfométricas do terreno "
            "para prever a propensão natural ao acúmulo de escoamento superficial."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.latex(r"TWI = \ln\left(\frac{a}{\tan \beta}\right)")
            st.markdown("""
            **Variáveis da Equação:**
            * **a (Área de contribuição específica):** Representa a área a montante que drena para um ponto específico, dividida pela largura do contorno (m²/m). Estima o volume de fluxo de água.
            * **tan β (Tangente da declividade):** O gradiente local do terreno. Estima o potencial de drenagem impulsionado pela gravidade.
            """)
        with col2:
            st.info(
                "A relação é inversamente proporcional ao declive: áreas planas com grandes bacias de contribuição "
                "(alto 'a' e baixo 'tan β') resultam em altos valores de TWI, identificando zonas críticas de "
                "saturação e formação de planícies de inundação."
            )

    # ABA 2: PIPELINE DE DADOS (A mágica da programação)
    with tab2:
        st.markdown("**Arquitetura de Extração, Transformação e Carga (ETL)**")
        st.write(
            "O ambiente analítico do SIGWeb não opera com dados estáticos simples. Todo o acervo vetorial "
            "passa por um rigoroso pipeline de sanitização e estruturação automatizada em linguagem Python (via Pandas e PyProj)."
        )
        st.markdown("""
        **Fases do Processamento:**
        1.  **Ingestão (Extract):** Leitura de tabelas de atributos de alta densidade (milhares de instâncias vetoriais).
        2.  **Reprojeção Cartográfica (Transform):** Conversão dinâmica de coordenadas do Sistema Projetado UTM (Sirgas 2000 Fuso 25S - EPSG:31985) para o Sistema Geodésico Global (WGS84 - EPSG:4326), garantindo interoperabilidade web.
        3.  **Classificação Condicional:** Aplicação de regras de negócio baseadas em quartis e limiares críticos para categorização de risco (Muito Baixo a Crítico).
        4.  **Otimização de Renderização (Load):** Injeção controlada na engine do Folium via processamento em lote, mitigando gargalos de memória no navegador.
        """)

    # ABA 3: FONTES DE DADOS
    with tab3:
        st.markdown("**Infraestrutura de Dados Espaciais (IDE)**")
        st.write(
            "A acurácia do diagnóstico espacial depende intrinsecamente da qualidade das matrizes de dados utilizadas. "
            "A calibração e alimentação deste sistema integram informações dos seguintes órgãos oficiais:"
        )
        st.markdown(
            "- **Prefeitura Municipal do Cabo de Santo Agostinho:** Base cartográfica primária, limites territoriais e zoneamento urbano.\n"
            "- **APAC (Agência Pernambucana de Águas e Clima):** Parâmetros de bacias hidrográficas e modelagem de precipitação.\n"
            "- **IBGE (Instituto Brasileiro de Geografia e Estatística):** Modelos Digitais de Elevação (MDE/MDS) via missões SRTM e base censitária.\n"
            "- **SEINFRA-PE / CONDEPE-FIDEM:** Diretrizes de infraestrutura estadual e macrozoneamento territorial.\n"
            "- **Projeto MapBiomas:** Histórico de cobertura e uso e ocupação do solo para cálculo de permeabilidade e atrito superficial."
        )

    # ABA 4: AVISO LEGAL E LIMITAÇÕES
    with tab4:
        st.warning("Limitações do Modelo e Uso Adequado da Plataforma")
        st.write(
            "O Atlas de Suscetibilidade a Inundações (ASI) opera como uma ferramenta de suporte à tomada de decisão "
            "com foco em planejamento macro e análise espacial preliminar. O modelo hidrogeomorfométrico pressupõe "
            "condições topográficas contínuas e não contabiliza, de forma nativa e em tempo real, obstruções antrópicas "
            "em sistemas de microdrenagem (ex: assoreamento, pavimentação irregular ou bloqueio de galerias pluviais)."
        )
        st.write(
            "Sob nenhuma hipótese, as projeções e diagnósticos gerados por este sistema substituem vistorias in loco, "
            "sondagens geotécnicas ou laudos técnicos emitidos por profissionais de engenharia e geociências "
            "para licenciamento civil ou elaboração de rotas de fuga definitivas."
        )
        
    with tab5:
        academic_content = load_academic_md()
        st.markdown(academic_content)