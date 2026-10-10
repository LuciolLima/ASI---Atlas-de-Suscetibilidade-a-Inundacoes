"""Organism Components — DashboardGrid, ReportDrawer, MapPanel, AnalyticsPanel.

Componentes complexos compostos de moléculas, prontos para uso em páginas.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
from typing import Any, Callable, Literal, Optional, Generator
from contextlib import contextmanager
from dataclasses import dataclass

from ..molecules import get_asi_layout, chart_container, show_toast
from ..atoms import asi_skeleton_chart, asi_skeleton_metric, asi_skeleton_title


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD GRID
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class GridItem:
    """Item do grid dashboard."""
    content: callable
    span: int = 1  # colunas que ocupa (1-4)
    height: int = 400
    title: str = ""
    actions: list = None


class DashboardGrid:
    """Grid responsivo auto-fit para dashboards analytics."""

    def __init__(
        self,
        min_card_width: str = "380px",
        gap: str = "var(--asi-space-md)",
        cols_max: int = 4,
    ):
        self.min_card_width = min_card_width
        self.gap = gap
        self.cols_max = cols_max
        self.items = []

    def add_item(
        self,
        content: callable,
        span: int = 1,
        height: int = 400,
        title: str = "",
        actions: list = None,
    ) -> "DashboardGrid":
        """Adiciona item ao grid (fluent interface)."""
        self.items.append({
            "content": content,
            "span": min(span, 4),
            "height": height,
            "title": title,
            "actions": actions,
        })
        return self

    def render(self) -> None:
        """Renderiza o grid completo."""
        if not self.items:
            st.info("Nenhum item no dashboard.")
            return

        # CSS Grid auto-fit
        st.markdown(
            f"""
            <style>
            .asi-dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax({self.min_card_width}, 1fr));
                gap: {self.gap};
            }}
            .asi-grid-card {{
                background: var(--asi-surface);
                border: 1px solid var(--asi-border);
                border-radius: var(--asi-radius-md);
                padding: var(--asi-space-md);
                height: 100%;
                display: flex;
                flex-direction: column;
            }}
            .asi-grid-card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--asi-space-sm);
                padding-bottom: var(--asi-space-xs);
                border-bottom: 1px solid var(--asi-border);
            }}
            .asi-grid-card-title {{
                font-family: var(--asi-font-sans);
                font-weight: 500;
                font-size: var(--asi-text-body);
                color: var(--asi-text-primary);
            }}
            .asi-grid-card-content {{
                flex: 1;
                overflow: auto;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Container grid
        st.markdown('<div class="asi-dashboard-grid">', unsafe_allow_html=True)

        for item in self.items:
            with st.container():
                st.markdown('<div class="asi-grid-card">', unsafe_allow_html=True)

                if item["title"]:
                    st.markdown(
                        f'<div class="asi-grid-card-header">'
                        f'<span class="asi-grid-card-title">{item["title"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown('<div class="asi-grid-card-content">', unsafe_allow_html=True)
                item["content"]()
                st.markdown('</div>', unsafe_allow_html=True)  # content
                st.markdown('</div>', unsafe_allow_html=True)  # card

        st.markdown('</div>', unsafe_allow_html=True)  # grid


# ════════════════════════════════════════════════════════════════════════════
# REPORT DRAWER (Slide-over panel)
# ════════════════════════════════════════════════════════════════════════════

@contextmanager
def report_drawer(
    title: str,
    open: bool = True,
    width: str = "400px",
    position: Literal["right", "left"] = "right",
    on_close: callable = None,
) -> Generator[None, None, None]:
    """Drawer slide-over para relatórios/inspeção lateral.

    Args:
        title: Título do drawer
        open: Se está aberto
        width: Largura (desktop). Mobile = 100% bottom sheet
        position: "right" ou "left"
        on_close: Callback ao fechar
    """
    if not open:
        yield
        return

    # CSS do drawer
    st.markdown(
        f"""
        <style>
        .asi-drawer-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.3);
            z-index: var(--asi-z-modal);
            animation: fade-in 0.2s ease-out;
        }}
        .asi-drawer {{
            position: fixed;
            top: 0;
            bottom: 0;
            {position}: 0;
            width: {width};
            max-width: 100vw;
            background: var(--asi-surface);
            border-left: 1px solid var(--asi-border);
            z-index: var(--asi-z-modal);
            display: flex;
            flex-direction: column;
            animation: slide-in-{position} 0.3s ease-out;
            overflow-y: auto;
        }}
        @keyframes slide-in-right {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes slide-in-left {{
            from {{ transform: translateX(-100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes fade-in {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .asi-drawer-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--asi-space-md);
            border-bottom: 1px solid var(--asi-border);
            position: sticky;
            top: 0;
            background: var(--asi-surface);
            z-index: 1;
        }}
        .asi-drawer-title {{
            font-family: var(--asi-font-sans);
            font-weight: 600;
            font-size: var(--asi-text-h3);
            color: var(--asi-text-primary);
        }}
        .asi-drawer-close {{
            background: transparent;
            border: 1px solid var(--asi-border);
            border-radius: var(--asi-radius-sm);
            padding: 4px 8px;
            font-family: var(--asi-font-mono);
            font-size: var(--asi-text-caption);
            color: var(--asi-text-secondary);
            cursor: pointer;
            transition: all var(--asi-transition-fast);
        }}
        .asi-drawer-close:hover {{
            border-color: var(--asi-brand-500);
            color: var(--asi-brand-500);
        }}
        .asi-drawer-content {{
            flex: 1;
            padding: var(--asi-space-md);
            overflow-y: auto;
        }}
        .asi-drawer-footer {{
            padding: var(--asi-space-md);
            border-top: 1px solid var(--asi-border);
            background: var(--asi-surface);
        }}
        @media (max-width: 640px) {{
            .asi-drawer {{ width: 100%; bottom: 0; top: auto; height: 70vh; border-radius: var(--asi-radius-xl) var(--asi-radius-xl) 0 0; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Overlay + Drawer
    st.markdown(
        f"""
        <div class="asi-drawer-overlay" id="asi-drawer-overlay"></div>
        <div class="asi-drawer" id="asi-drawer">
            <div class="asi-drawer-header">
                <h3 class="asi-drawer-title">{title}</h3>
                <button class="asi-drawer-close" onclick="document.getElementById('asi-drawer-overlay').remove(); document.getElementById('asi-drawer').remove();">✕ Fechar</button>
            </div>
            <div class="asi-drawer-content" id="asi-drawer-content">
            </div>
        </div>
        <script>
        // Fecha ao clicar no overlay
        document.getElementById('asi-drawer-overlay').addEventListener('click', () => {{
            document.getElementById('asi-drawer-overlay').remove();
            document.getElementById('asi-drawer').remove();
            {f"window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{type: 'drawer_close'}}}}, '*')" if False else ''}
        }});
        // ESC para fechar
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                document.getElementById('asi-drawer-overlay')?.remove();
                document.getElementById('asi-drawer')?.remove();
            }}
        }});
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Content placeholder
    content_placeholder = st.empty()

    try:
        with content_placeholder.container():
            yield
    finally:
        content_placeholder.empty()


# ═════════════════════════════════════════════════════════════════════════════
# MAP PANEL (Wrapper para componente Deck.gl)
# ════════════════════════════════════════════════════════════════════════════

@contextmanager
def map_panel(
    twi_df,
    conf: dict,
    highlight_point: dict = None,
    height: int = 600,
    key: str = "asi_deck_gl",
) -> Generator[dict, None, None]:
    """Wrapper para mapa Deck.gl com inspector lateral.

    Args:
        twi_df: DataFrame com dados TWI
        conf: Config do sidebar
        highlight_point: Ponto destacado (lat/lon)
        height: Altura do mapa
        key: Chave Streamlit
    """
    from ..organisms.deck_map_panel import render_deck_gl_map

    col_map, col_inspector = st.columns([0.7, 0.3], gap="medium")

    with col_map:
        result = render_deck_gl_map(
            twi_df,
            conf=conf,
            highlight_point=highlight_point,
            height=height,
            key=key,
        )

    with col_inspector:
        inspector_placeholder = st.empty()

    yield {
        "map_result": result,
        "inspector": inspector_placeholder,
    }


# ════════════════════════════════════════════════════════════════════════════
# ANALYTICS PANEL
# ════════════════════════════════════════════════════════════════════════════

@contextmanager
def analytics_panel(
    df,
    conf: dict,
    df_precipitacao=None,
) -> Generator[None, None, None]:
    """Painel analytics com tabs: Composição, Frequência, Uso do Solo."""
    from ..molecules import chart_container, get_asi_layout

    st.markdown("### Análise Geoestatística de Área")

    tab1, tab2, tab3 = st.tabs([
        "Composição Proporcional",
        "Distribuição de Frequência",
        "Matriz de Uso do Solo",
    ])

    tema = "plotly_dark" if conf.get('map_style') == 'DARK' else "plotly_white"

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            if not df.empty:
                df_pie = df['Classe_Risco_Cod'].value_counts().reset_index()
                df_pie.columns = ['Classe', 'Quantidade']

                fig_pie = go.Figure(go.Pie(
                    labels=df_pie['Classe'],
                    values=df_pie['Quantidade'],
                    hole=0.4,
                    marker_colors=[],  # usar cores padrão
                    textinfo='label+percent',
                    hovertemplate='%{label}<br>%{value} (%{percent})<extra></extra>',
                ))
                fig_pie.update_layout(get_asi_layout(
                    "Composição Proporcional de Suscetibilidade",
                    height=400,
                ))
                st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            if conf.get('tech_mode'):
                st.success(
                    "**Fundamentação Teórica:** A segmentação amostral é estruturada mediante os "
                    "limiares hidrogeológicos estabelecidos para o TWI. Amostragens designadas como "
                    "'Críticas' ou 'Altas' corroboram para áreas de convergência hídrica, denotando "
                    "elevada suscetibilidade à saturação pedológica."
                )
            else:
                st.info("Habilite 'Exibir Fundamentação Teórica' para visualização do descritivo técnico.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            if not df.empty:
                fig_hist = go.Figure(go.Histogram(
                    x=df['twi'],
                    nbinsx=40,
                    marker_color='#1E90FF',
                    name='Frequência',
                ))
                fig_hist.update_layout(get_asi_layout(
                    "Frequência Estatística (TWI)",
                    height=400,
                ))
                st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            if not df.empty:
                fig_scatter = go.Figure(go.Scatter(
                    x=df['longitude'],
                    y=df['twi'],
                    mode='markers',
                    marker=dict(
                        color=df['Classe_Risco_Cod'].map({
                            'CRITICO': '#8B0000',
                            'ALTO': '#FF4500',
                            'MODERADO': '#FFD700',
                            'BAIXO': '#1E90FF',
                            'MUITO_BAIXO': '#ADD8E6',
                        }),
                        size=4,
                        opacity=0.7,
                    ),
                    hovertemplate='Lon: %{x:.4f}<br>TWI: %{y:.2f}<extra></extra>',
                ))
                fig_scatter.update_layout(get_asi_layout(
                    "Dispersão Espacial vs Saturação",
                    height=400,
                ))
                st.plotly_chart(fig_scatter, use_container_width=True)

        if conf.get('tech_mode'):
            st.success(
                "**Fundamentação Teórica:** A distribuição de frequência consolida o comportamento "
                "hidrológico da região em análise. A assimetria à direita na distribuição do TWI "
                "sinaliza predominância de áreas secas com zonas restritas de saturação extrema."
            )

    with tab3:
        if 'Uso_Solo_Desc' in df.columns:
            df_grp = df.groupby(['Uso_Solo_Desc', 'Classe_Risco_Cod']).size().reset_index(name='Contagem')

            fig_bar = go.Figure()
            for classe in ['CRITICO', 'ALTO', 'MODERADO', 'BAIXO', 'MUITO_BAIXO']:
                subset = df_grp[df_grp['Classe_Risco_Cod'] == classe]
                if not subset.empty:
                    fig_bar.add_trace(go.Bar(
                        y=subset['Uso_Solo_Desc'],
                        x=subset['Contagem'],
                        name=classe,
                        orientation='h',
                        marker_color={
                            'CRITICO': '#8B0000',
                            'ALTO': '#FF4500',
                            'MODERADO': '#FFD700',
                            'BAIXO': '#1E90FF',
                            'MUITO_BAIXO': '#ADD8E6',
                        }.get(classe, '#808080'),
                    ))

            fig_bar.update_layout(
                get_asi_layout(
                    "Correlação: Vulnerabilidade vs Cobertura Pedológica",
                    height=max(350, len(df['Uso_Solo_Desc'].unique()) * 28),
                ),
                barmode='stack',
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            if conf.get('tech_mode'):
                st.success(
                    "**Fundamentação Teórica:** A matriz de correlação evidencia o risco inerente à "
                    "ocupação antrópica em zonas de alta convergência hídrica, servindo como embasamento "
                    "empírico para o planejamento do ordenamento territorial."
                )

    yield


# ════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════

__all__ = [
    "DashboardGrid",
    "report_drawer",
    "map_panel",
    "analytics_panel",
]