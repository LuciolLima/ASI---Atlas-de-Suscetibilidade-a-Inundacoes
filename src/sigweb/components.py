"""
SISTEMA ASI - COMPONENTES DE UI
Versão: 2.8 — Cluster, Hidrografia, Eventos, Ranking, Exportação
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

/* ── Alertas com pulse ─────────────────────────────────── */
@keyframes asi-pulse-error {
    0%, 100% { border-left-color: #e74c3c; }
    50%       { border-left-color: #ff6b6b; box-shadow: 0 0 8px rgba(231,76,60,0.4); }
}
@keyframes asi-pulse-warn {
    0%, 100% { border-left-color: #e67e22; }
    50%       { border-left-color: #f39c12; box-shadow: 0 0 8px rgba(230,126,34,0.3); }
}
div[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 2px !important;
    font-family: var(--asi-sans) !important;
    font-size: 0.83rem !important;
}
div[data-testid="stAlert"].st-emotion-cache-1wmy9n5 {
    animation: asi-pulse-error 2s ease-in-out infinite !important;
}

/* ── Dataframe ─────────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--asi-border) !important;
    border-radius: 2px !important;
}

/* ── Tabs ──────────────────────────────────────────────── */
div[data-testid="stTabs"] button {
    font-family: var(--asi-mono) !important;
    font-size: 0.74rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--asi-text-dim) !important;
    transition: color 0.2s ease !important;
}
div[data-testid="stTabs"] button:hover {
    color: var(--asi-blue-hi) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--asi-cyan) !important;
    border-bottom-color: var(--asi-cyan) !important;
}

/* ── Subexpanders — nível 2 ────────────────────────────── */
div[data-testid="stExpander"] div[data-testid="stExpander"] {
    background: #060a0e !important;
    border: 1px solid #111d27 !important;
    border-left: 2px solid #1c2a38 !important;
    border-radius: 0 !important;
    margin: 2px 0 !important;
}
div[data-testid="stExpander"] div[data-testid="stExpander"]:hover {
    border-left-color: var(--asi-blue-dim) !important;
}
div[data-testid="stExpander"] div[data-testid="stExpander"] details summary p {
    font-size: 0.70rem !important;
    color: var(--asi-text-dim) !important;
    letter-spacing: 0.14em !important;
}
div[data-testid="stExpander"] div[data-testid="stExpander"]:hover details summary p {
    color: var(--asi-blue-hi) !important;
}
div[data-testid="stExpander"] div[data-testid="stExpander"][open] details summary p {
    color: var(--asi-cyan) !important;
}


div[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid var(--asi-blue-dim) !important;
    color: var(--asi-cyan) !important;
    font-family: var(--asi-mono) !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: var(--asi-blue-dim) !important;
    box-shadow: 0 0 12px rgba(0, 180, 216, 0.2) !important;
}
</style>
"""


def render_top_navigation(df):
    st.markdown(ASI_CSS, unsafe_allow_html=True)

    c_tools, c_filters, c_meta = st.columns([1, 1.2, 1])
    config_dict = {}

    # ── 1. CARTOGRAFIA ───────────────────────────────────────
    with c_tools:
        with st.expander("// CARTOGRAFIA", expanded=False):

            # ── Submenu: Tileset Base ─────────────────────
            with st.expander("TILESET BASE", expanded=False):
                t_padrao = st.toggle("OSM · Topográfico",     value=True)
                t_claro  = st.toggle("CartoDB · Positron",    value=False)
                t_escuro = st.toggle("CartoDB · Dark Matter", value=False)

                ativos = sum([t_padrao, t_claro, t_escuro])
                if ativos > 1:
                    st.error("Conflito — selecione apenas um tileset.")
                    config_dict['block_ui']  = True
                    config_dict['map_style'] = "ERROR"
                elif ativos == 0:
                    config_dict['block_ui']  = True
                    config_dict['map_style'] = "NONE"
                else:
                    config_dict['block_ui'] = False
                    if t_padrao: config_dict['map_style'] = "PADRAO"
                    elif t_claro: config_dict['map_style'] = "CLARO"
                    else:         config_dict['map_style'] = "DARK"

            # ── Submenu: Overlay de Camadas ───────────────
            with st.expander("OVERLAY DE CAMADAS", expanded=False):
                config_dict['show_geojson']     = st.toggle("Malha Municipal — PE",          value=False)
                config_dict['show_points']      = st.toggle("Dataset TWI · Pontos",          value=False)
                config_dict['show_heatmap']     = st.toggle("Kernel Density · Heatmap",      value=False)
                config_dict['show_hidrografia'] = st.toggle("Rede Hidrográfica",             value=False)
                config_dict['show_eventos']     = st.toggle("Registro de Eventos · SEPDEC",  value=False)

            # ── Submenu: Performance ──────────────────────
            with st.expander("PERFORMANCE", expanded=False):
                config_dict['use_cluster'] = st.toggle(
                    "MarkerCluster · Agrupamento",
                    value=False,
                    help="Agrupa vetores próximos. ⚠️ Desabilita inspeção individual."
                )
                if config_dict['use_cluster']:
                    st.caption("› cluster ativo — inspeção vetorial desabilitada")

    # ── 2. FILTRAGEM VETORIAL ────────────────────────────────
    with c_filters:
        with st.expander("// FILTRAGEM VETORIAL", expanded=False):
            bairros_disponiveis = ["Todos"]
            if not df.empty and 'NM_BAIRRO' in df.columns:
                bairros_disponiveis += sorted(df['NM_BAIRRO'].dropna().unique().tolist())
            elif not df.empty and 'LAYER' in df.columns:
                bairros_disponiveis += sorted(df['LAYER'].dropna().unique().tolist())

            status_disabled = config_dict.get('block_ui', False)

            # ── Submenu: Recorte Espacial ─────────────────
            with st.expander("RECORTE ESPACIAL", expanded=True):
                config_dict['selected_bairro'] = st.selectbox(
                    "Unidade de Análise",
                    options=bairros_disponiveis,
                    disabled=status_disabled
                )

            # ── Submenu: Parâmetro TWI ────────────────────
            with st.expander("PARÂMETRO TWI", expanded=True):
                twi_min = float(df['twi'].min()) if not df.empty else 0.0
                twi_max = float(df['twi'].max()) if not df.empty else 20.0
                config_dict['twi_threshold'] = st.slider(
                    "Limiar Mínimo",
                    min_value=twi_min,
                    max_value=twi_max,
                    value=twi_min,
                    disabled=status_disabled
                )

            # ── Submenu: Janela Temporal (condicional) ────
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

            # ── Submenu: Inspeção ─────────────────────────
            with st.expander("INSPEÇÃO VETORIAL", expanded=False):
                config_dict['inspect_mode'] = st.toggle(
                    "Inspeção · Ponto",
                    value=False,
                    disabled=status_disabled or cluster_on,
                    help="Desabilitado quando MarkerCluster está ativo."
                )
                config_dict['tech_mode'] = st.toggle(
                    "Notação Geomorfométrica",
                    value=False,
                    disabled=status_disabled
                )

            # ── Submenu: Painéis ──────────────────────────
            with st.expander("PAINÉIS ANALÍTICOS", expanded=False):
                config_dict['analytics_mode'] = st.checkbox(
                    "Dashboard Geoestatístico",
                    value=False,
                    disabled=status_disabled
                )
                config_dict['ranking_mode'] = st.checkbox(
                    "Ranking IRA · Por Bairro",
                    value=False,
                    disabled=status_disabled
                )

            # ── Submenu: Output ───────────────────────────
            with st.expander("OUTPUT", expanded=False):
                config_dict['export_csv'] = st.button(
                    "⬇ Export · CSV Filtrado",
                    disabled=status_disabled,
                    use_container_width=True
                )

    return config_dict


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