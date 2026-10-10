"""Atomic Components — Button, Input, Badge, Icon, Tooltip, Skeleton.

Componentes atômicos reutilizáveis com design tokens ASI.
"""

from __future__ import annotations

import streamlit as st
from typing import Literal, Optional, Callable


# ════════════════════════════════════════════════════════════════════════════
# BUTTON
# ════════════════════════════════════════════════════════════════════════════

def asi_button(
    label: str,
    key: str,
    variant: Literal["primary", "ghost", "danger", "success"] = "primary",
    icon: Optional[str] = None,
    disabled: bool = False,
    on_click: Optional[Callable] = None,
    use_container_width: bool = False,
    **kwargs,
) -> bool:
    """Botão estilizado com design tokens ASI.

    Args:
        label: Texto do botão
        key: Chave única Streamlit
        variant: primary|ghost|danger|success
        icon: Emoji/ícone opcional
        disabled: Se desabilitado
        on_click: Callback opcional
        use_container_width: Se expande para largura do container
    """
    variant_styles = {
        "primary": {
            "bg": "transparent",
            "border": "var(--asi-brand-700)",
            "color": "var(--asi-brand-100)",
            "hover_bg": "var(--asi-brand-700)",
            "hover_border": "var(--asi-brand-500)",
            "hover_color": "var(--asi-text-inverse)",
        },
        "ghost": {
            "bg": "transparent",
            "border": "var(--asi-border)",
            "color": "var(--asi-text-secondary)",
            "hover_bg": "var(--asi-surface)",
            "hover_border": "var(--asi-border-strong)",
            "hover_color": "var(--asi-text-primary)",
        },
        "danger": {
            "bg": "transparent",
            "border": "#8a1e1e",
            "color": "#fde8e8",
            "hover_bg": "#8a1e1e",
            "hover_border": "#e74c3c",
            "hover_color": "white",
        },
        "success": {
            "bg": "transparent",
            "border": "#1e6b3a",
            "color": "#e8f8ef",
            "hover_bg": "#1e6b3a",
            "hover_border": "#2ecc71",
            "hover_color": "white",
        },
    }

    style = variant_styles.get(variant, variant_styles["primary"])
    if disabled:
        style = {**style, "opacity": "0.5", "cursor": "not-allowed"}

    icon_html = f'<span style="margin-right: var(--asi-space-xs);">{icon}</span>' if icon else ""

    html = f"""
    <button id="{key}" class="asi-btn asi-btn-{variant}"
            style="
                font-family: var(--asi-font-mono);
                font-size: var(--asi-text-caption);
                letter-spacing: 0.1em;
                text-transform: uppercase;
                border-radius: var(--asi-radius-sm);
                padding: var(--asi-space-xs) var(--asi-space-sm);
                display: inline-flex;
                align-items: center;
                gap: var(--asi-space-xs);
                cursor: {'not-allowed' if disabled else 'pointer'};
                border: 1px solid {style['border']};
                background: {style['bg']};
                color: {style['color']};
                transition: all var(--asi-transition-normal);
                width: {'100%' if use_container_width else 'auto'};
            "
            {'disabled' if disabled else ''}>
        {icon_html}{label}
    </button>
    <style>
        .asi-btn-{variant} {{
            background: {style['bg']};
            border-color: {style['border']};
            color: {style['color']};
        }}
        .asi-btn-{variant}:hover:not(:disabled) {{
            background: {style['hover_bg']};
            border-color: {style['hover_border']};
            color: {style['hover_color']};
            box-shadow: var(--asi-shadow-glow);
        }}
        .asi-btn-{variant}:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }}
    </style>
    """
    st.markdown(html, unsafe_allow_html=True)

    # Botão real do Streamlit (invisível, só para callback)
    return st.button(
        "",
        key=f"{key}_real",
        on_click=on_click,
        disabled=disabled,
        use_container_width=use_container_width,
    )


# ════════════════════════════════════════════════════════════════════════════
# INPUT / SELECT / SLIDER
# ════════════════════════════════════════════════════════════════════════════

def asi_selectbox(
    label: str,
    key: str,
    options: list,
    index: int = 0,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    help: Optional[str] = None,
) -> str:
    """Selectbox com estilo ASI."""
    return st.selectbox(
        label,
        options,
        index=index,
        key=key,
        disabled=disabled,
        on_change=on_change,
        help=help,
    )


def asi_slider(
    label: str,
    key: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    value: float = 0.0,
    step: float = 1.0,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    help: Optional[str] = None,
) -> float:
    """Slider com estilo ASI."""
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        disabled=disabled,
        on_change=on_change,
        help=help,
    )


def asi_text_input(
    label: str,
    key: str,
    value: str = "",
    placeholder: str = "",
    disabled: bool = False,
    on_change: Optional[Callable] = None,
    type: Literal["default", "password"] = "default",
) -> str:
    """Text input com estilo ASI."""
    return st.text_input(
        label,
        value=value,
        key=key,
        placeholder=placeholder,
        disabled=disabled,
        on_change=on_change,
        type=type,
    )


def asi_number_input(
    label: str,
    key: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    value: float = 0.0,
    step: float = 1.0,
    disabled: bool = False,
    on_change: Optional[Callable] = None,
) -> float:
    """Number input com estilo ASI."""
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        disabled=disabled,
        on_change=on_change,
    )


# ════════════════════════════════════════════════════════════════════════════
# BADGE / STATUS INDICATOR
# ════════════════════════════════════════════════════════════════════════════

def asi_badge(
    label: str,
    variant: Literal["critical", "high", "moderate", "low", "very-low", "success", "warning", "info", "neutral"] = "neutral",
    size: Literal["sm", "md", "lg"] = "md",
) -> None:
    """Badge/Status indicator com cores semânticas ASI."""
    variant_colors = {
        "critical": ("var(--asi-critical)", "var(--asi-text-inverse)"),
        "high": ("var(--asi-high)", "var(--asi-text-inverse)"),
        "moderate": ("var(--asi-moderate)", "var(--asi-text-inverse)"),
        "low": ("var(--asi-low)", "var(--asi-text-inverse)"),
        "very-low": ("var(--asi-very-low)", "var(--asi-text-inverse)"),
        "success": ("var(--asi-success)", "var(--asi-text-inverse)"),
        "warning": ("var(--asi-warning)", "var(--asi-text-inverse)"),
        "info": ("var(--asi-info)", "var(--asi-text-inverse)"),
        "neutral": ("var(--asi-border)", "var(--asi-text-secondary)"),
    }

    bg, color = variant_colors.get(variant, variant_colors["neutral"])

    size_styles = {
        "sm": "font-size: var(--asi-text-caption); padding: 2px 8px;",
        "md": "font-size: var(--asi-text-body-sm); padding: 4px 10px;",
        "lg": "font-size: var(--asi-text-body); padding: 6px 14px;",
    }

    html = f"""
    <span class="asi-badge asi-badge-{variant}"
          style="
            display: inline-flex;
            align-items: center;
            border-radius: var(--asi-radius-full);
            background: {v};
            color: {color};
            font-family: var(--asi-font-mono);
            font-weight: 500;
            {size_styles[size]}
            letter-spacing: 0.05em;
            text-transform: uppercase;
        ">
        {label}
    </span>
    """.replace("{v}", bg).replace("{color}", color)

    st.markdown(html, unsafe_allow_html=True)


def asi_risk_chip(
    risk_class: str,
    show_icon: bool = True,
) -> None:
    """Chip de classe de risco ASI (CRITICO, ALTO, MODERADO, BAIXO, MUITO_BAIXO)."""
    icons = {
        "CRITICO": "🔴",
        "ALTO": "🟠",
        "MODERADO": "🟡",
        "BAIXO": "🔵",
        "MUITO_BAIXO": "🟢",
    }
    colors = {
        "CRITICO": "var(--asi-critical)",
        "ALTO": "var(--asi-high)",
        "MODERADO": "var(--asi-moderate)",
        "BAIXO": "var(--asi-low)",
        "MUITO_BAIXO": "var(--asi-very-low)",
    }

    color = colors.get(risk_class, "var(--asi-border)")
    icon = icons.get(risk_class, "")

    html = f"""
    <span class="asi-risk-chip"
          style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: var(--asi-radius-full);
            background: {colors.get(risk_class, 'var(--asi-border)')};
            color: var(--asi-text-inverse);
            font-family: var(--asi-font-mono);
            font-size: var(--asi-text-caption);
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        ">
        {icon if show_icon else ''}
        {risk_class}
    </span>
    """
    st.markdown(html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ICON (Lucide/Phosphor SVG inline)
# ════════════════════════════════════════════════════════════════════════════

ICONS = {
    "map": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>',
    "layers": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 1 4.6 9a1.65 1.65 0 0 1-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 1 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 1-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
    "refresh": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="8"></line></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "home": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
}


def asi_icon(name: str, size: int = 16) -> str:
    """Retorna SVG inline do ícone."""
    svg = ICONS.get(name, ICONS.get("info", ""))
    if 'width="16"' in svg:
        svg = svg.replace('width="16"', f'width="{size}"').replace('height="16"', f'height="{size}"')
    return svg


# ════════════════════════════════════════════════════════════════════════════
# TOOLTIP / POPOVER
# ════════════════════════════════════════════════════════════════════════════

def asi_tooltip(
    content: str,
    trigger: str,
    position: Literal["top", "bottom", "left", "right"] = "top",
) -> None:
    """Tooltip simples via CSS (hover)."""
    html = f"""
    <div class="asi-tooltip-wrapper" style="position: relative; display: inline-block;">
        {trigger}
        <div class="asi-tooltip"
             style="
                 position: absolute;
                 {position}: 100%;
                 left: 50%;
                 transform: translateX(-50%);
                 padding: 6px 10px;
                 border-radius: var(--asi-radius-sm);
                 background: var(--asi-surface);
                 border: 1px solid var(--asi-border);
                 font-family: var(--asi-font-sans);
                 font-size: var(--asi-text-body-sm);
                 color: var(--asi-text-primary);
                 white-space: nowrap;
                 opacity: 0;
                 visibility: hidden;
                 transition: all var(--asi-transition-fast);
                 z-index: var(--asi-z-tooltip);
                 box-shadow: var(--asi-shadow-md);
             ">
            {content}
        </div>
    </div>
    <style>
        .asi-tooltip-wrapper:hover .asi-tooltip {{
            opacity: 1;
            visibility: visible;
            {position}: calc(100% + 8px);
        }}
    </style>
    """
    st.markdown(html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SKELETON LOADERS
# ════════════════════════════════════════════════════════════════════════════

def asi_skeleton_map(height: int = 400) -> None:
    """Skeleton loader para mapa."""
    st.markdown(
        f'<div class="asi-skeleton asi-skeleton-map" style="height: {height}px;"></div>',
        unsafe_allow_html=True,
    )


def asi_skeleton_chart(height: int = 300) -> None:
    """Skeleton loader para gráfico."""
    st.markdown(
        f'<div class="asi-skeleton asi-skeleton-chart" style="height: {height}px;"></div>',
        unsafe_allow_html=True,
    )


def asi_skeleton_metric() -> None:
    """Skeleton loader para métrica."""
    st.markdown(
        '<div class="asi-skeleton asi-skeleton-metric"></div>',
        unsafe_allow_html=True,
    )


def asi_skeleton_title(width: str = "60%") -> None:
    """Skeleton loader para título."""
    st.markdown(
        f'<div class="asi-skeleton asi-skeleton-title" style="width: {width};"></div>',
        unsafe_allow_html=True,
    )


def asi_skeleton_table_row() -> None:
    """Skeleton loader para linha de tabela."""
    st.markdown(
        '<div class="asi-skeleton asi-skeleton-table-row"></div>',
        unsafe_allow_html=True,
    )


def asi_skeleton_card(height: int = 200) -> None:
    """Skeleton loader para card completo."""
    st.markdown(
        f"""
        <div class="asi-skeleton" style="height: {height}px; width: 100%; border-radius: var(--asi-radius-md);"></div>
        """,
        unsafe_allow_html=True,
    )