"""Molecule Components — ChartWrapper, FilterBar, DataTable, Toast.

Componentes moleculares compostos de átomos, reutilizáveis em dashboards.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Callable, Literal, Optional
from dataclasses import dataclass


# ════════════════════════════════════════════════════════════════════════════
# CHART WRAPPER
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ChartConfig:
    """Configuração padrão para gráficos Plotly estilo ASI."""
    height: int = 400
    theme: Literal["dark", "light"] = "dark"
    show_toolbar: bool = False
    responsive: bool = True
    margin: dict = None

    def __post_init__(self):
        if self.margin is None:
            self.margin = {"l": 60, "r": 30, "t": 50, "b": 50}


def get_asi_layout(title: str = "", height: int = 400, **kwargs) -> dict:
    """Retorna layout padrão ASI para gráficos Plotly."""
    colors = {
        'background': '#080C10',
        'surface': '#0D1219',
        'border': '#1C2A38',
        'border_hi': '#2E4A64',
        'text': '#C8D6E0',
        'text_dim': '#5A7A8A',
        'primary': '#2E86C1',
    }

    layout = {
        'title': {
            'text': title,
            'font': {'family': 'IBM Plex Sans', 'size': 14, 'color': '#C8D6E0'},
            'x': 0.02,
        },
        'paper_bgcolor': colors['background'],
        'plot_bgcolor': colors['surface'],
        'font': {'family': 'IBM Plex Sans', 'color': colors['text'], 'size': 11},
        'height': height,
        'margin': {'l': 60, 'r': 30, 't': 50, 'b': 50},
        'xaxis': {
            'gridcolor: '#1C2A38',
            'zerolinecolor': '#1C2A38',
            'linecolor': '#2E4A64',
            'title_font': {'family': 'IBM Plex Mono', 'size': 11, 'color': '#5A7A8A'},
            'tickfont': {'family': 'IBM Plex Mono', 'size': 10, 'color': '#5A7A8A'},
        },
        'yaxis': {
            'gridcolor': '#1C2A38',
            'zerolinecolor': '#1C2A38',
            'linecolor': '#2E4A64',
            'title_font': {'family': 'IBM Plex Mono', 'size': 11, 'color': '#5A7A8A'},
            'tickfont': {'family': 'IBM Plex Mono', 'size': 10, 'color': '#5A7A8A'},
        },
        'legend': {
            'bgcolor': 'rgba(13,18,25,0.8)',
            'bordercolor': '#1C2A38',
            'borderwidth': 1,
            'font': {'family': 'IBM Plex Sans', 'size': 10, 'color': '#C8D6E0'},
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.15,
            'xanchor': 'center',
            'x': 0.5,
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': '#0D1219',
            'bordercolor': '#1C2A38',
            'font': {'family': 'IBM Plex Sans', 'size': 11},
        },
    }
    layout.update(kwargs)
    return layout


def apply_asi_style(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    """Aplica estilo ASI a uma figura existente."""
    fig.update_layout(get_asi_layout(title, height))
    return fig


def chart_container(
    fig: go.Figure,
    title: str,
    key: str,
    height: int = 400,
    actions: list = None,
    fullscreen: bool = True,
    export: bool = True,
    skeleton: bool = False,
) -> None:
    """Wrapper completo para gráfico: skeleton loading, header, actions, export."""
    container = st.container()

    with container:
        # Header com título e actions
        col_title, col_actions = st.columns([0.85, 0.15])

        with col_title:
            st.markdown(
                f'<h3 style="font-family: var(--asi-font-sans); font-weight: 500; '
                f'color: var(--asi-text-secondary); margin: 0; font-size: 1rem;">{title}</h3>',
                unsafe_allow_html=True,
            )

        with col_actions:
            if actions or fullscreen or export:
                cols = st.columns(len([a for a in [fullscreen, export] if a]) + len(actions or []))
                idx = 0
                if fullscreen:
                    with cols[idx]:
                        if st.button("⛶", key=f"{key}_fullscreen", help="Fullscreen"):
                            st.markdown(
                                "<script>document.documentElement.requestFullscreen();</script>",
                                unsafe_allow_html=True,
                            )
                        idx += 1
                if export:
                    with cols[idx]:
                        st.download_button(
                            "📥",
                            data="",  # Preenchido pelo callback real
                            file_name=f"{title.lower().replace(' ', '_')}.png",
                            mime="image/png",
                            key=f"{key}_export",
                            help="Exportar PNG",
                            disabled=True,  # Requer implementação real
                        )
                        idx += 1
                for action in actions or []:
                    with cols[idx]:
                        st.button(action["label"], key=f"{key}_{action['key']}",
                                  on_click=action.get("on_click"))
                        idx += 1

        # Skeleton loading
        if skeleton:
            st.markdown(
                f'<div class="asi-skeleton asi-skeleton-chart" style="height: {height}px;"></div>',
                unsafe_allow_html=True,
            )
        else:
            st.plotly_chart(fig, use_container_width=True, key=key)


def render_chart(
    df,
    chart_type: Literal["line", "bar", "scatter", "box", "histogram", "pie"],
    x: str,
    y: str = None,
    color: str = None,
    title: str = "",
    height: int = 400,
    **kwargs,
) -> go.Figure:
    """Factory para criar gráficos Plotly padrão ASI."""
    fig = go.Figure()

    if chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color, **kwargs)
    elif chart_type == "bar":
        fig = px.bar(df, x=x, y=y, color=color, **kwargs)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color, **kwargs)
    elif chart_type == "box":
        fig = px.box(df, x=x, y=y, color=color, **kwargs)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x, color=color, **kwargs)
    elif chart_type == "pie":
        fig = px.pie(df, values=y, names=x, **kwargs)

    fig.update_layout(get_asi_layout(title, height))
    return fig


# ════════════════════════════════════════════════════════════════════════════
# FILTER BAR
# ════════════════════════════════════════════════════════════════════════════

def filter_bar(
    filters: list[dict],
    key: str,
    on_change: callable = None,
    clear_label: str = "Limpar filtros",
) -> dict:
    """Barra de filtros com chips ativos e clear all."""
    active_filters = {}
    changed = False

    # Render filtros
    cols = st.columns(len(filters))
    for i, f in enumerate(filters):
        with cols[i]:
            ftype = f.get("type", "select")

            if ftype == "select":
                val = st.selectbox(
                    f["label"],
                    f["options"],
                    index=f.get("index", 0),
                    key=f"{key}_{f['key']}",
                    on_change=on_change,
                    disabled=f.get("disabled", False),
                )
                if val != f.get("default"):
                    active_filters[f["key"]] = val

            elif ftype == "slider":
                val = st.slider(
                    f["label"],
                    min_value=f["min"],
                    max_value=f["max"],
                    value=f.get("value", (f["min"], f["max"])),
                    step=f.get("step", 1.0),
                    key=f"{key}_{f['key']}",
                    on_change=on_change,
                    disabled=f.get("disabled", False),
                )
                if val != f.get("default"):
                    active_filters[f["key"]] = val

            elif ftype == "multiselect":
                val = st.multiselect(
                    f["label"],
                    f["options"],
                    default=f.get("default", []),
                    key=f"{key}_{f['key']}",
                    on_change=on_change,
                    disabled=f.get("disabled", False),
                )
                if val != f.get("default"):
                    active_filters[f["key"]] = val

            elif ftype == "date_range":
                val = st.date_input(
                    f["label"],
                    value=f.get("value", ()),
                    key=f"{key}_{f['key']}",
                    on_change=on_change,
                    disabled=f.get("disabled", False),
                )
                if val != f.get("default"):
                    active_filters[f["key"]] = val

    # Chips de filtros ativos + clear
    if active_filters:
        st.markdown("**Filtros ativos:**")
        chip_cols = st.columns(len(active_filters) + 1)
        for i, (k, v) in enumerate(active_filters.items()):
            with chip_cols[i]:
                st.markdown(
                    f'<span class="asi-filter-chip">{k}: {v}</span>',
                    unsafe_allow_html=True,
                )
        with chip_cols[-1]:
            if st.button("🗑️ Limpar", key=f"{key}_clear"):
                st.rerun()

    return active_filters


# ════════════════════════════════════════════════════════════════════════════
# DATA TABLE (wrapper para st.dataframe / aggrid)
# ════════════════════════════════════════════════════════════════════════════

def render_data_table(
    df,
    key: str,
    height: int = 400,
    selection_mode: Literal["single", "multi", "none"] = "single",
    page_size: int = 20,
    sortable: bool = True,
    filterable: bool = True,
    column_config: dict = None,
    on_select: callable = None,
) -> list:
    """Wrapper para tabela de dados com seleção, ordenação, paginação."""
    if df is None or df.empty:
        st.info("Nenhum dado disponível.")
        return []

    # Configuração padrão de colunas
    if column_config is None:
        column_config = {}

    # Seleção via session_state
    if "selected_rows" not in st.session_state:
        st.session_state.selected_rows = []

    selected = st.dataframe(
        df,
        use_container_width=True,
        height=height,
        selection_mode=selection_mode,
        on_select="rerun",
        column_config=column_config,
        key=key,
        hide_index=True,
    )

    if on_select and selected:
        on_select(selected)

    return selected


# ════════════════════════════════════════════════════════════════════════════
# TOAST / NOTIFICATIONS
# ════════════════════════════════════════════════════════════════════════════

def show_toast(
    message: str,
    toast_type: Literal["success", "warning", "error", "info"] = "info",
    duration: int = 4000,
) -> None:
    """Exibe toast notification usando CSS-only animation."""
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
    }
    icon = icons.get(toast_type, "ℹ️")

    html = f"""
    <div class="asi-toast-container" id="asi-toast-container">
        <div class="asi-toast asi-toast-{toast_type}">
            {icon} {message}
        </div>
    </div>
    <script>
    setTimeout(function() {{
        const container = document.getElementById('asi-toast-container');
        if (container) {{
            const toast = container.querySelector('.asi-toast');
            if (toast) {{
                toast.style.animation = 'slide-in 0.3s ease-out reverse';
                setTimeout(() => container.remove(), 300);
            }}
        }}
    }}, {duration});
    </script>
    """
    st.markdown(html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# BREADCRUMB
# ════════════════════════════════════════════════════════════════════════════

def breadcrumb(items: list[dict], separator: str = "›") -> None:
    """Navegação breadcrumb."""
    html = '<nav class="asi-breadcrumb" style="font-family: var(--asi-font-mono); font-size: var(--asi-text-caption); color: var(--asi-text-dim);">'
    for i, item in enumerate(items):
        if i > 0:
            html += f'<span style="margin: 0 8px;">{separator}</span>'
        if item.get("href"):
            html += f'<a href="{item["href"]}" style="color: var(--asi-brand-500); text-decoration: none;">{item["label"]}</a>'
        else:
            html += f'<span style="color: var(--asi-text-primary);">{item["label"]}</span>'
    html += '</nav>'
    st.markdown(html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════

__all__ = [
    "ChartConfig",
    "get_asi_layout",
    "apply_asi_style",
    "chart_container",
    "render_chart",
    "filter_bar",
    "render_data_table",
    "show_toast",
    "breadcrumb",
]