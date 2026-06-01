"""
SISTEMA ASI - COMPONENTES DE UI
Versão: 3.0 — Hub de Integração de Dados Externos (API Hub)
"""

import streamlit as st
from src.sigweb import config

# ══════════════════════════════════════════════════════════════
#  INJEÇÃO GLOBAL DE CSS — GIS PROFESSIONAL THEME
# ══════════════════════════════════════════════════════════════

ASI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── Variáveis de tema ─────────────────────────────────── */
:root {
    --asi-bg:        #080c10;
    --asi-surface:   #0d1219;
    --asi-border:    #1c2a38;
    --asi-border-hi: #2e4a64;
    --asi-blue:      #2e86c1;
    --asi-blue-hi:   #3fa8e0;
    --asi-blue-dim:  #1a4a6e;
    --asi-cyan:      #00b4d8;
    --asi-text:      #c8d6e0;
    --asi-text-dim:  #5a7a8a;
    --asi-text-hi:   #e8f4f8;
    --asi-mono:      'IBM Plex Mono', monospace;
    --asi-sans:      'IBM Plex Sans', sans-serif;
}

/* ── App base ──────────────────────────────────────────── */
.stApp {
    background-color: var(--asi-bg) !important;
    font-family: var(--asi-sans) !important;
}

/* ── Título principal ──────────────────────────────────── */
.stApp h1 {
    font-family: var(--asi-sans) !important;
    font-weight: 600 !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.08em !important;
    color: var(--asi-text-hi) !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--asi-border-hi);
    padding-bottom: 8px;
}

/* ── Cabeçalhos h2, h3 ─────────────────────────────────── */
.stApp h2, .stApp h3 {
    font-family: var(--asi-sans) !important;
    font-weight: 500 !important;
    color: #d0dde6 !important;
    letter-spacing: 0.02em !important;
}

/* ── Texto corrido ─────────────────────────────────────── */
.stApp p, .stApp li {
    font-family: var(--asi-sans) !important;
    font-size: 0.88rem !important;
    color: var(--asi-text) !important;
    line-height: 1.6 !important;
}

/* ── Expanders — painel de controle ───────────────────── */
div[data-testid="stExpander"] {
    background: var(--asi-surface) !important;
    border: 1px solid var(--asi-border) !important;
    border-radius: 3px !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stExpander"]:hover {
    border-color: var(--asi-border-hi) !important;
}
div[data-testid="stExpander"] details summary {
    padding: 10px 14px !important;
}
div[data-testid="stExpander"] details summary p {
    font-family: var(--asi-mono) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--asi-blue-hi) !important;
}
div[data-testid="stExpander"] details summary:hover p {
    color: var(--asi-cyan) !important;
}

/* ── Seção label (markdown bold) ──────────────────────── */
.stApp strong {
    font-family: var(--asi-mono) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
}

/* ── Toggles ───────────────────────────────────────────── */
div[data-testid="stToggle"] label p {
    font-family: var(--asi-sans) !important;
    font-size: 0.84rem !important;
    color: var(--asi-text) !important;
    transition: color 0.15s ease !important;
}
div[data-testid="stToggle"]:hover label p {
    color: var(--asi-text-hi) !important;
}

/* ── Checkboxes ────────────────────────────────────────── */
div[data-testid="stCheckbox"] label p {
    font-family: var(--asi-sans) !important;
    font-size: 0.84rem !important;
    color: var(--asi-text) !important;
    transition: color 0.15s ease !important;
}
div[data-testid="stCheckbox"]:hover label p {
    color: var(--asi-text-hi) !important;
}

/* ── Selectbox ─────────────────────────────────────────── */
div[data-testid="stSelectbox"] label p {
    font-family: var(--asi-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: var(--asi-surface) !important;
    border: 1px solid var(--asi-border) !important;
    border-radius: 3px !important;
    font-family: var(--asi-sans) !important;
    font-size: 0.84rem !important;
    color: var(--asi-text) !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--asi-blue) !important;
}

/* ── Slider ────────────────────────────────────────────── */
div[data-testid="stSlider"] label p {
    font-family: var(--asi-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
}
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: var(--asi-text-dim) !important;
    font-family: var(--asi-mono) !important;
    font-size: 0.7rem !important;
}

/* ── Number input ──────────────────────────────────────── */
div[data-testid="stNumberInput"] label p {
    font-family: var(--asi-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
}

/* ── Botão primário ────────────────────────────────────── */
div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid var(--asi-blue-dim) !important;
    color: var(--asi-blue-hi) !important;
    font-family: var(--asi-mono) !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    background: var(--asi-blue-dim) !important;
    border-color: var(--asi-blue) !important;
    color: var(--asi-text-hi) !important;
    box-shadow: 0 0 12px rgba(46, 134, 193, 0.25) !important;
}

/* ── Divisor ───────────────────────────────────────────── */
hr {
    border-color: var(--asi-border) !important;
    margin: 10px 0 !important;
}

/* ── Caption / texto auxiliar ─────────────────────────── */
div[data-testid="stCaptionContainer"] p {
    font-family: var(--asi-mono) !important;
    font-size: 0.70rem !important;
    color: var(--asi-text-dim) !important;
    letter-spacing: 0.05em !important;
}

/* ── Métricas ──────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: var(--asi-surface) !important;
    border: 1px solid var(--asi-border) !important;
    border-left: 3px solid var(--asi-blue) !important;
    border-radius: 2px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--asi-border-hi) !important;
    border-left-color: var(--asi-cyan) !important;
}
div[data-testid="stMetric"] label {
    font-family: var(--asi-mono) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: var(--asi-mono) !important;
    font-size: 1.5rem !important;
    font-weight: 500 !important;
    color: var(--asi-text-hi) !important;
}
</style>
"""


def render_top_navigation(df_raw):
    """Barra de navegação superior com controles de mapa e filtros."""
    st.markdown(ASI_CSS, unsafe_allow_html=True)
    config_dict = {}

    c_mapa, c_filter, c_meta = st.columns([1.2, 1.5, 1.3])

    # ── 1. MODELO CARTOGRÁFICO ───────────────────────────────
    with c_mapa:
        with st.expander("// MODELO CARTOGRÁFICO", expanded=False):
            estilo = st.radio(
                "Base Cartográfica",
                options=["PADRAO", "DARK", "CLARO", "NONE"],
                horizontal=True,
                index=0
            )
            config_dict['map_style'] = estilo
            config_dict['block_ui']  = (estilo == "NONE")

            st.markdown("**Camadas Vetoriais**")
            config_dict['show_geojson']    = st.checkbox("Malha Territorial (Bairros)", value=False)
            config_dict['show_points']     = st.checkbox("Amostras TWI (Pontos)", value=False)
            config_dict['show_heatmap']    = st.checkbox("Mapa de Calor (Risco Elevado)", value=False)
            config_dict['show_hidrografia']= st.checkbox("Hidrografia (Rede de Drenagem)", value=False)
            config_dict['show_eventos']    = st.checkbox("Eventos Históricos de Inundação", value=False)
            config_dict['use_cluster']     = st.checkbox("MarkerCluster (Agrupamento Espacial)", value=False)

    # ── 2. FILTROS ESPACIAIS ─────────────────────────────────
    with c_filter:
        with st.expander("// FILTROS ESPACIAIS", expanded=False):
            status_disabled = config_dict.get('block_ui', False)

            bairros_opcoes = ['Todos']
            if 'NM_BAIRRO' in df_raw.columns:
                bairros_opcoes += sorted(df_raw['NM_BAIRRO'].dropna().unique().tolist())
            elif 'LAYER' in df_raw.columns:
                bairros_opcoes += sorted(df_raw['LAYER'].dropna().unique().tolist())

            config_dict['selected_bairro'] = st.selectbox(
                "Unidade Espacial de Análise",
                options=bairros_opcoes,
                disabled=status_disabled
            )

            twi_min = float(df_raw['twi'].min()) if not df_raw.empty else 0.0
            twi_max = float(df_raw['twi'].max()) if not df_raw.empty else 20.0

            config_dict['twi_threshold'] = st.slider(
                "Limiar Mínimo",
                min_value=twi_min,
                max_value=twi_max,
                value=twi_min,
                disabled=status_disabled
            )

            if config_dict.get('show_eventos'):
                with st.expander("JANELA TEMPORAL · EVENTOS", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        config_dict['ano_inicio'] = st.number_input(
                            "Início", min_value=1980, max_value=2030,
                            value=2000, step=1, disabled=status_disabled
                        )
                    with col_b:
                        config_dict['ano_fim'] = st.number_input(
                            "Término", min_value=1980, max_value=2030,
                            value=2030, step=1, disabled=status_disabled
                        )

    # ── 3. MÓDULOS ANALÍTICOS ────────────────────────────────
    with c_meta:
        with st.expander("// MÓDULOS ANALÍTICOS", expanded=False):
            cluster_on = config_dict.get('use_cluster', False)

            with st.expander("INSPEÇÃO VETORIAL", expanded=False):
                config_dict['inspect_mode'] = st.toggle(
                    "Inspeção de Ponto",
                    value=False,
                    disabled=status_disabled or cluster_on,
                    help="Desabilitado quando MarkerCluster está ativo."
                )
                config_dict['tech_mode'] = st.toggle(
                    "Notação Geomorfométrica",
                    value=False,
                    disabled=status_disabled
                )

            with st.expander("PAINÉIS ANALÍTICOS", expanded=False):
                config_dict['analytics_mode'] = st.checkbox(
                    "Dashboard Geoestatístico",
                    value=False,
                    disabled=status_disabled
                )
                config_dict['ranking_mode'] = st.checkbox(
                    "Ranking IRA — Por Unidade Espacial",
                    value=False,
                    disabled=status_disabled
                )
                config_dict['correlacao_mode'] = st.checkbox(
                    "Correlação TWI × Defesa Civil",
                    value=False,
                    disabled=status_disabled
                )

            # ── NOVO: Hub de Integração de Dados Externos ────
            with st.expander("HUB DE DADOS EXTERNOS", expanded=False):
                config_dict['api_hub_mode'] = st.checkbox(
                    "Integração via API — Nowcasting e Diagnóstico Social",
                    value=False,
                    disabled=status_disabled,
                    help=(
                        "Ativa o módulo de consumo de APIs públicas: "
                        "Open-Meteo (precipitação em tempo real), "
                        "IBGE SIDRA (vulnerabilidade demográfica — Censo 2022), "
                        "NASA POWER (em desenvolvimento)."
                    )
                )

            with st.expander("OUTPUT", expanded=False):
                config_dict['export_csv'] = st.button(
                    "Export — CSV Filtrado",
                    disabled=status_disabled,
                    use_container_width=True
                )

    return config_dict


def render_sidebar():
    """Sidebar reservada para uso futuro ou expansão de filtros."""
    return {}


def render_twi_legend(active_class=None):
    """Legenda de suscetibilidade TWI — estilo GIS profissional."""
    academic_texts = {
        'CRITICO':    "Zonas de convergência de fluxo extremo. Probabilidade quase certa de saturação e alagamento durante eventos pluviométricos. Intervenção infraestrutural obrigatória.",
        'ALTO':       "Áreas de forte acúmulo hídrico. A capacidade de infiltração é rapidamente superada, gerando escoamento superficial volumoso.",
        'MODERADO':   "Transição hidrológica. Podem ocorrer poças e alagamentos pontuais dependendo da intensidade da chuva e tipo de solo.",
        'BAIXO':      "Zonas de dissipação de fluxo. A inclinação do terreno favorece o escoamento sem retenção significativa, mitigando riscos.",
        'MUITO_BAIXO':"Cumeadas ou áreas de alta declividade. O escoamento é acelerado, inviabilizando o acúmulo hídrico natural."
    }

    html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

@keyframes pulse-crit {
    0%, 100% { box-shadow: 0 0 4px rgba(139,0,0,0.4); }
    50%       { box-shadow: 0 0 10px rgba(139,0,0,0.8); }
}

.asi-legend-wrap {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 12px;
    background: #0d1219;
    padding: 12px 14px;
    border: 1px solid #1c2a38;
    border-top: 2px solid #2e86c1;
}
.asi-legend-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.asi-legend-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #2e86c1;
}
.asi-legend-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1c2a38, transparent);
}
.asi-twi-card-wrap {
    flex: 1;
    min-width: 110px;
}
.asi-twi-card {
    background: #080c10;
    border: 1px solid #1c2a38;
    border-left: 3px solid;
    padding: 7px 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: default;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
}
.asi-twi-card:hover {
    background: #0d1219;
    transform: translateY(-1px);
}
.asi-twi-label {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    color: #c8d6e0;
    letter-spacing: 0.02em;
    transition: color 0.2s ease;
}
.asi-twi-card:hover .asi-twi-label {
    color: #e8f4f8;
}
.asi-twi-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.asi-twi-panel {
    background: #080c10;
    border-left: 2px solid;
    margin-top: 0;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.78rem;
    line-height: 1.5;
    color: #7a9aaa;
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    padding: 0 10px;
    transition: max-height 0.35s ease, opacity 0.35s ease, padding 0.35s ease;
}
.asi-twi-card-wrap:hover .asi-twi-panel,
.asi-panel-active {
    max-height: 200px;
    opacity: 1;
    padding: 8px 10px;
}
.asi-dimmed { opacity: 0.25; }
.asi-active-card {
    background: #0d1219 !important;
}
</style>

<div class="asi-legend-wrap">
    <div class="asi-legend-header">
        <span class="asi-legend-title">TWI · Índice de Suscetibilidade</span>
        <div class="asi-legend-line"></div>
    </div>
"""

    for classe, label in config.CLASS_LABELS.items():
        if classe == 'NEUTRO':
            continue

        cor         = config.COLORS[classe]
        texto_acad  = academic_texts.get(classe, "")
        nome_curto  = label.split(' (')[0]

        card_extra  = ""
        panel_extra = ""

        if active_class:
            if classe == active_class:
                card_extra  = " asi-active-card"
                panel_extra = " asi-panel-active"
                if classe == 'CRITICO':
                    card_extra += '" style="animation: pulse-crit 2s ease-in-out infinite;'
            else:
                card_extra = " asi-dimmed"

        html += f"""
<div class="asi-twi-card-wrap">
  <div class="asi-twi-card{card_extra}" style="border-left-color:{cor};">
    <div class="asi-twi-dot" style="background:{cor};box-shadow:0 0 4px {cor}80;"></div>
    <span class="asi-twi-label">{nome_curto}</span>
  </div>
  <div class="asi-twi-panel{panel_extra}" style="border-left-color:{cor}40;">
    <span style="color:{cor};font-weight:500;font-size:0.72rem;letter-spacing:0.08em;">
      &#9656; {nome_curto.upper()}
    </span><br>{texto_acad}
  </div>
</div>
"""

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)