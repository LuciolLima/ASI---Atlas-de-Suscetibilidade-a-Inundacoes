"""Theme Provider ASI — CSS Variables Generator + Dark/Light Toggle.

Gera CSS custom properties a partir dos tokens e injeta no Streamlit.
Toggle dark/light persistido em localStorage via JS inline.
"""

from __future__ import annotations

import streamlit as st
from .tokens import TOKENS, ColorTokens


def _generate_css_variables(tokens: dict, theme: Literal["dark", "light"] = "dark") -> str:
    """Gera CSS custom properties a partir dos tokens."""
    css_lines = [":root {"]

    # Colors - semantic (diferem entre dark/light)
    if theme == "light":
        css_lines.append("  --asi-bg: #f8fafc;")
        css_lines.append("  --asi-surface: #ffffff;")
        css_lines.append("  --asi-surface-elevated: #f1f5f9;")
        css_lines.append("  --asi-border: #d1dbe6;")
        css_lines.append("  --asi-border-strong: #a8b8cc;")
        css_lines.append("  --asi-text-primary: #1a2a3a;")
        css_lines.append("  --asi-text-secondary: #5a7a8a;")
        css_lines.append("  --asi-text-inverse: #ffffff;")
    else:
        # Dark theme (default) - usa tokens semantic
        color_tokens: ColorTokens = TOKENS["color"]
        for key, value in color_tokens.semantic.items():
            if key.startswith("bg-"):
                css_lines.append(f"  --asi-{key.replace('_', '-')}: {value};")
            elif key.startswith("border"):
                css_lines.append(f"  --asi-{key.replace('_', '-')}: {value};")
            elif key.startswith("text-"):
                css_lines.append(f"  --asi-{key.replace('_', '-')}: {value};")

    # Brand colors (same both themes)
    color_tokens: ColorTokens = TOKENS["color"]
    for key, value in color_tokens.brand.items():
        css_lines.append(f"  --asi-brand-{key}: {value};")

    # Spacing
    for key, value in TOKENS["spacing"].__dict__.items():
        css_lines.append(f"  --asi-space-{key}: {value};")

    # Radius
    for key, value in TOKENS["radius"].__dict__.items():
        css_lines.append(f"  --asi-radius-{key}: {value};")

    # Shadow
    for key, value in TOKENS["shadow"].__dict__.items():
        css_lines.append(f"  --asi-shadow-{key}: {value};")

    # Transition
    for key, value in TOKENS["transition"].__dict__.items():
        css_lines.append(f"  --asi-transition-{key}: {value};")

    # Typography
    typo = TOKENS["typography"]
    css_lines.append(f"  --asi-font-sans: {typo.font_family['sans']};")
    css_lines.append(f"  --asi-font-mono: {typo.font_family['mono']};")
    for key, value in typo.scale.items():
        css_lines.append(f"  --asi-text-{key}: {value};")

    # Breakpoints
    for key, value in TOKENS["breakpoint"].__dict__.items():
        css_lines.append(f"  --asi-bp-{key}: {value};")

    # Z-index
    for key, value in TOKENS["z_index"].__dict__.items():
        css_lines.append(f"  --asi-z-{key}: {value};")

    css_lines.append("}")
    return "\n".join(css_lines)


def inject_global_theme() -> None:
    """Injeta tema global + toggle dark/light persistido.

    - CSS variables em classes ESTÁVEIS do Streamlit
    - Dark/Light toggle persistido em localStorage
    - Font IBM Plex via Google Fonts
    """
    # CSS variables for both themes
    css = _generate_css_variables(TOKENS, "dark")
    css += _generate_css_variables(TOKENS, "light").replace(":root {", "[data-theme=\"light\"] {")

    # Overrides apenas em classes ESTÁVEIS do Streamlit (data-testid, :root, [data-theme])
    css += """
    /* ── Font Import ───────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    /* ── App base ──────────────────────────────────────────── */
    .stApp {
        background-color: var(--asi-bg) !important;
        font-family: var(--asi-font-sans) !important;
    }

    /* ── Header ────────────────────────────────────────────── */
    .stApp h1 {
        font-family: var(--asi-font-sans) !important;
        font-weight: 600 !important;
        font-size: var(--asi-text-h1) !important;
        letter-spacing: 0.08em !important;
        color: var(--asi-text-primary) !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid var(--asi-border-strong);
        padding-bottom: 8px;
    }
    .stApp h2, .stApp h3 {
        font-family: var(--asi-font-sans) !important;
        font-weight: 500 !important;
        color: var(--asi-text-secondary) !important;
        letter-spacing: 0.02em !important;
    }
    .stApp p, .stApp li {
        font-family: var(--asi-font-sans) !important;
        font-size: var(--asi-text-body) !important;
        color: var(--asi-text-primary) !important;
        line-height: 1.6 !important;
    }

    /* ── Expanders (painel controle) ───────────────────────── */
    div[data-testid="stExpander"] {
        background: var(--asi-surface) !important;
        border: 1px solid var(--asi-border) !important;
        border-radius: var(--asi-radius-md) !important;
        transition: border-color var(--asi-transition-normal) !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: var(--asi-border-strong) !important;
    }
    div[data-testid="stExpander"] details summary {
        padding: 10px 14px !important;
    }
    div[data-testid="stExpander"] details summary p {
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        font-weight: 500 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--asi-brand-500) !important;
    }
    div[data-testid="stExpander"] details summary:hover p {
        color: var(--asi-brand-100) !important;
    }

    /* ── Toggles/Checkboxes ────────────────────────────────── */
    div[data-testid="stToggle"] label p,
    div[data-testid="stCheckbox"] label p {
        font-family: var(--asi-font-sans) !important;
        font-size: var(--asi-text-body-sm) !important;
        color: var(--asi-text-primary) !important;
        transition: color var(--asi-transition-fast) !important;
    }
    div[data-testid="stToggle"]:hover label p,
    div[data-testid="stCheckbox"]:hover label p {
        color: var(--asi-text-primary) !important;
    }

    /* ── Selectbox ─────────────────────────────────────────── */
    div[data-testid="stSelectbox"] label p {
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--asi-text-secondary) !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background: var(--asi-surface) !important;
        border: 1px solid var(--asi-border) !important;
        border-radius: var(--asi-radius-sm) !important;
        font-family: var(--asi-font-sans) !important;
        font-size: var(--asi-text-body-sm) !important;
        color: var(--asi-text-primary) !important;
        transition: border-color var(--asi-transition-normal) !important;
    }
    div[data-testid="stSelectbox"] > div > div:hover {
        border-color: var(--asi-brand-500) !important;
    }

    /* ── Slider ────────────────────────────────────────────── */
    div[data-testid="stSlider"] label p {
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--asi-text-secondary) !important;
    }
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
        color: var(--asi-text-secondary) !important;
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
    }

    /* ── Botão primário ────────────────────────────────────── */
    div[data-testid="stButton"] button {
        background: transparent !important;
        border: 1px solid var(--asi-brand-700) !important;
        color: var(--asi-brand-100) !important;
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        border-radius: var(--asi-radius-sm) !important;
        transition: all var(--asi-transition-normal) !important;
    }
    div[data-testid="stButton"] button:hover {
        background: var(--asi-brand-700) !important;
        border-color: var(--asi-brand-500) !important;
        color: var(--asi-text-inverse) !important;
        box-shadow: var(--asi-shadow-glow) !important;
    }

    /* ── Divisor ───────────────────────────────────────────── */
    hr {
        border-color: var(--asi-border) !important;
        margin: var(--asi-space-sm) 0 !important;
    }

    /* ── Caption / texto auxiliar ──────────────────────────── */
    div[data-testid="stCaptionContainer"] p {
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        color: var(--asi-text-secondary) !important;
        letter-spacing: 0.05em !important;
    }

    /* ── Métricas ───────────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: var(--asi-surface) !important;
        border: 1px solid var(--asi-border) !important;
        border-left: 3px solid var(--asi-brand-500) !important;
        border-radius: var(--asi-radius-sm) !important;
        padding: var(--asi-space-sm) var(--asi-space-md) !important;
        transition: border-color var(--asi-transition-normal) !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: var(--asi-border-strong) !important;
        border-left-color: var(--asi-brand-100) !important;
    }
    div[data-testid="stMetric"] label {
        font-family: var(--asi-font-mono) !important;
        font-size: var(--asi-text-caption) !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--asi-text-secondary) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: var(--asi-font-mono) !important;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        color: var(--asi-text-primary) !important;
    }

    /* ── Skeleton Loading ───────────────────────────────────── */
    .asi-skeleton {
        background: linear-gradient(90deg, var(--asi-border) 25%, var(--asi-border-strong) 50%, var(--asi-border) 75%);
        background-size: 200% 100%;
        animation: skeleton-shimmer 1.5s infinite;
        border-radius: var(--asi-radius-sm);
    }
    @keyframes skeleton-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .asi-skeleton-map {
        height: 400px;
        width: 100%;
        border: 1px solid var(--asi-border);
        border-radius: var(--asi-radius-md);
    }
    .asi-skeleton-chart {
        height: 300px;
        width: 100%;
        border: 1px solid var(--asi-border);
        border-radius: var(--asi-radius-md);
    }
    .asi-skeleton-metric {
        height: 60px;
        width: 100%;
        border-radius: var(--asi-radius-sm);
    }
    .asi-skeleton-title {
        height: 16px;
        width: 60%;
        margin-bottom: var(--asi-space-sm);
    }
    .asi-skeleton-table-row {
        height: 12px;
        width: 100%;
        margin-bottom: var(--asi-space-xs);
    }

    /* ── Toast Notifications ────────────────────────────────── */
    .asi-toast-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: var(--asi-z-toast);
        display: flex;
        flex-direction: column;
        gap: var(--asi-space-xs);
    }
    .asi-toast {
        padding: var(--asi-space-sm) var(--asi-space-md);
        border-radius: var(--asi-radius-md);
        font-family: var(--asi-font-sans);
        font-size: var(--asi-text-body-sm);
        animation: slide-in 0.3s ease-out;
        box-shadow: var(--asi-shadow-md);
    }
    @keyframes slide-in {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    .asi-toast-success { background: #1e6b3a; color: #e8f8ef; border-left: 4px solid #2ecc71; }
    .asi-toast-warning { background: #8a6b1e; color: #fef8e8; border-left: 4px solid #f39c12; }
    .asi-toast-error { background: #8a1e1e; color: #fde8e8; border-left: 4px solid #e74c3c; }
    .asi-toast-info { background: #1e4a6b; color: #e8f4f8; border-left: 4px solid #2e86c1; }

    /* ── Light theme overrides ──────────────────────────────── */
    [data-theme="light"] {
        --asi-bg: #f8fafc;
        --asi-surface: #ffffff;
        --asi-surface-elevated: #f1f5f9;
        --asi-border: #d1dbe6;
        --asi-border-strong: #a8b8cc;
        --asi-text-primary: #1a2a3a;
        --asi-text-secondary: #5a7a8a;
        --asi-text-inverse: #080c10;
    }
    """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Dark/Light toggle JS (inserido no body)
    js = """
    <script>
    (function() {
      const STORAGE_KEY = 'asi_theme';
      const root = document.documentElement;
      const toggleBtn = document.createElement('div');
      toggleBtn.className = 'asi-theme-toggle';
      toggleBtn.title = 'Alternar tema claro/escuro';
      document.body.appendChild(toggleBtn);
      function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        toggleBtn.innerHTML = theme === 'light' ? '🌙 Dark' : '☀️ Light';
      }
      const saved = localStorage.getItem('asi_theme') || 'dark';
      applyTheme(saved);
      toggleBtn.addEventListener('click', () => {
        const current = root.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem('asi_theme', next);
        applyTheme(next);
      });
    })();
    </script>
    <style>
    .asi-theme-toggle {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        z-index: 9999;
        padding: 0.5rem 0.75rem;
        background: var(--asi-surface);
        border: 1px solid var(--asi-border);
        border-radius: var(--asi-radius-md);
        font-family: var(--asi-font-mono);
        font-size: 0.7rem;
        cursor: pointer;
        transition: all var(--asi-transition-fast);
        box-shadow: var(--asi-shadow-md);
    }
    .asi-theme-toggle:hover {
        border-color: var(--asi-brand-500);
        transform: translateY(-2px);
        box-shadow: var(--asi-shadow-lg);
    }
    </style>
    """
    st.markdown(js, unsafe_allow_html=True)


def get_theme() -> str:
    """Retorna tema atual ('dark' ou 'light') - para uso em componentes."""
    # No Streamlit bare mode, default para dark
    return "dark"