"""Base Layout System — Layouts nativos usando st.columns/st.container.

Sem CSS Grid hacks — usa primitivas nativas do Streamlit que sobrevivem a updates.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Literal, Optional

import streamlit as st

from ..theme import inject_global_theme, get_theme


@contextmanager
def base_layout(
    title: str = "ASI | Atlas de Suscetibilidade a Inundações",
    sidebar_collapsible: bool = True,
) -> Generator[dict, None, None]:
    """Layout base com header, sidebar e main area.

    Args:
        title: Título da aplicação
        sidebar_collapsible: Se a sidebar pode ser colapsada

    Yields:
        dict com referências para áreas: header, sidebar, main
    """
    # Injeta tema global (CSS + JS toggle)
    inject_global_theme()

    # Configura página
    st.set_page_config(
        page_title=title,
        layout="wide",
        initial_sidebar_state="collapsed" if not sidebar_collapsible else "expanded",
    )

    # Header fixo via container
    header_container = st.container()
    with header_container:
        _render_header(title)

    # Sidebar nativa (colapsável via [aria-expanded] CSS)
    with st.sidebar:
        sidebar_placeholder = st.empty()

    # Main area
    main_placeholder = st.empty()

    yield {
        "header": header_container,
        "sidebar": sidebar_placeholder,
        "main": main_placeholder,
    }


def _render_header(title: str) -> None:
    """Renderiza header com logo, título e ações globais."""
    col_logo, col_title, col_actions = st.columns([1, 4, 2], gap="medium")

    with col_logo:
        st.markdown(
            '<div style="font-family: var(--asi-font-mono); font-size: var(--asi-text-caption); '
            'color: var(--asi-brand-500); font-weight: 600;">ASI</div>',
            unsafe_allow_html=True,
        )

    with col_title:
        st.markdown(
            f'<h1 style="margin: 0;">{title}</h1>',
            unsafe_allow_html=True,
        )

    with col_actions:
        col_theme, col_fullscreen, col_help = st.columns(3)
        with col_theme:
            # Theme toggle é injetado via JS no theme.py
            pass
        with col_fullscreen:
            if st.button("⛶", key="fullscreen_btn", help="Fullscreen"):
                st.markdown(
                    "<script>document.documentElement.requestFullscreen();</script>",
                    unsafe_allow_html=True,
                )
        with col_help:
            if st.button("❓", key="help_btn", help="Ajuda"):
                st.toast("Documentação técnica disponível na seção Docs", icon="ℹ️")


@contextmanager
def map_centric_layout(
    map_ratio: float = 0.7,
    inspector_ratio: float = 0.3,
) -> Generator[dict, None, None]:
    """Layout mapa-centrico: mapa (esquerda) + inspector (direita).

    Mobile: stack vertical (mapa em cima, inspector embaixo como drawer).
    Desktop: side-by-side com proporção configurável.
    """
    col_map, col_inspector = st.columns(
        [map_ratio, inspector_ratio],
        gap="medium",
        vertical_alignment="top",
    )

    yield {
        "map": col_map,
        "inspector": col_inspector,
    }


@contextmanager
def analytics_layout(
    cols: int = 3,
    min_card_width: str = "380px",
) -> Generator[dict, None, None]:
    """Layout dashboard analytics — CSS Grid auto-fit responsivo.

    Args:
        cols: Número máximo de colunas
        min_card_width: Largura mínima de cada card (CSS Grid minmax)

    Yields:
        dict com 'grid' (container) e helpers para adicionar cards
    """
    # Container com CSS Grid auto-fit
    grid_container = st.container()

    with grid_container:
        st.markdown(
            f"""
            <style>
            .asi-dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax({min_card_width}, 1fr));
                gap: var(--asi-space-md);
            }}
            </style>
            <div class="asi-dashboard-grid" id="asi-dashboard-grid"></div>
            """,
            unsafe_allow_html=True,
        )

    # Placeholder para cards (serão renderizados via st.columns dentro do container)
    cols_placeholder = st.columns(cols, gap="medium")

    yield {
        "grid": grid_container,
        "cols": cols_placeholder,
        "add_card": lambda content, span=1: _add_card_to_grid(cols_placeholder, content, span),
    }


def _add_card_to_grid(cols_placeholder, content, span: int = 1) -> None:
    """Helper para adicionar card ao grid (simplificado)."""
    # Em implementação real, usaria um sistema de slots
    pass


@contextmanager
def report_layout(
    title: str,
    full_width: bool = True,
) -> Generator[dict, None, None]:
    """Layout para relatórios técnicos — largura total, tipografia otimizada."""
    report_container = st.container()

    with report_container:
        st.markdown(
            f"""
            <div class="asi-report" style="
                max-width: {'none' if full_width else '900px'};
                margin: 0 auto;
                padding: var(--asi-space-lg);
                font-family: var(--asi-font-sans);
                line-height: 1.7;
            ">
                <h1 style="font-family: var(--asi-font-sans); font-weight: 600;
                           color: var(--asi-text-primary); border-bottom: 2px solid var(--asi-brand-500);
                           padding-bottom: var(--asi-space-sm); margin-bottom: var(--asi-space-lg);">
                    {title}
                </h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

        content_placeholder = st.empty()

    yield {
        "container": report_container,
        "content": content_placeholder,
    }


# ── Helper para renderizar componentes dentro de layouts ──

def render_in_sidebar(content_func, *args, **kwargs) -> None:
    """Executa função de conteúdo dentro da sidebar."""
    with st.sidebar:
        content_func(*args, **kwargs)


def render_in_main(content_func, *args, **kwargs) -> None:
    """Executa função de conteúdo na área principal."""
    # Em implementação real, usaria placeholder do main
    content_func(*args, **kwargs)


def render_in_inspector(content_func, *args, **kwargs) -> None:
    """Executa função de conteúdo no inspector (painel lateral direito)."""
    # Em implementação real, usaria placeholder do inspector
    content_func(*args, **kwargs)