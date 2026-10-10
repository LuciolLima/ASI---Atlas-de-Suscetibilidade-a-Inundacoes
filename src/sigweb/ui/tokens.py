"""Design Tokens ASI — Single Source of Truth para cores, espaçamento, tipografia, etc.

Tokens tipados (dataclasses frozen) — imutáveis, serializáveis, single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ColorTokens:
    """Tokens de cor — paleta semântica + brand."""
    # Brand colors (azul ASI)
    brand: dict[str, str] = None

    # Cores semânticas (usadas nos componentes)
    semantic: dict[str, str] = None

    # Cores para data visualization
    data_viz: list[str] = None

    def __post_init__(self):
        if self.brand is None:
            object.__setattr__(self, "brand", {
                "50": "#e8f4fd",
                "100": "#d1e8fa",
                "200": "#a3d1f4",
                "300": "#75baef",
                "400": "#47a3e9",
                "500": "#2E86C1",  # Primary
                "600": "#1d6bb8",
                "700": "#1B4F72",
                "800": "#153a54",
                "900": "#0D2B3E",
            })
        if self.semantic is None:
            object.__setattr__(self, "semantic", {
                # Backgrounds
                "bg-primary": "#080C10",
                "bg-surface": "#0D1219",
                "bg-elevated": "#131A22",
                # Borders
                "border": "#1C2A38",
                "border-strong": "#2E4A64",
                # Text
                "text-primary": "#C8D6E0",
                "text-secondary": "#5A7A8A",
                "text-inverse": "#080C10",
                # Status / Risk
                "critical": "#8B0000",
                "high": "#FF4500",
                "moderate": "#FFD700",
                "low": "#1E90FF",
                "very-low": "#ADD8E6",
                # Feedback
                "success": "#2ECC71",
                "warning": "#F39C12",
                "info": "#2E86C1",
            })
        if self.data_viz is None:
            object.__setattr__(self, "data_viz", [
                "#2E86C1", "#00B4D8", "#E74C3C", "#F39C12",
                "#2ECC71", "#9B59B6", "#E67E22", "#1ABC9C",
            ])


@dataclass(frozen=True)
class SpacingTokens:
    """Tokens de espaçamento — escala base 4px."""
    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


@dataclass(frozen=True)
class TypographyTokens:
    """Tokens de tipografia — famílias, escala, pesos."""
    font_family: dict[str, str] = None
    scale: dict[str, str] = None
    weight: dict[str, int] = None

    def __post_init__(self):
        if self.font_family is None:
            object.__setattr__(self, "font_family", {
                "sans": "'IBM Plex Sans', system-ui, -apple-system, sans-serif",
                "mono": "'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace",
                "display": "'IBM Plex Sans', system-ui, -apple-system, sans-serif",
            })
        if self.scale is None:
            object.__setattr__(self, "scale", {
                "display-xl": "clamp(2.5rem, 5vw, 4rem)",
                "display-lg": "clamp(2rem, 4vw, 3rem)",
                "h1": "clamp(1.75rem, 3vw, 2.25rem)",
                "h2": "clamp(1.5rem, 2.5vw, 1.875rem)",
                "h3": "1.25rem",
                "body-lg": "1.125rem",
                "body": "1rem",
                "body-sm": "0.875rem",
                "caption": "0.75rem",
                "code": "0.875rem",
            })
        if self.weight is None:
            object.__setattr__(self, "weight", {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700,
            })


@dataclass(frozen=True)
class RadiusTokens:
    """Tokens de border radius."""
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


@dataclass(frozen=True)
class ShadowTokens:
    """Tokens de sombra/elevação."""
    sm: str = "0 1px 2px rgba(0,0,0,0.3)"
    md: str = "0 4px 12px rgba(0,0,0,0.4)"
    lg: str = "0 8px 24px rgba(0,0,0,0.5)"
    glow: str = "0 0 20px rgba(46,134,193,0.3)"


@dataclass(frozen=True)
class TransitionTokens:
    """Tokens de transição/animação."""
    fast: str = "150ms ease"
    normal: str = "250ms ease"
    slow: str = "350ms ease"


@dataclass(frozen=True)
class BreakpointTokens:
    """Breakpoints responsivos (mobile-first)."""
    mobile: str = "640px"
    tablet: str = "1024px"
    desktop: str = "1280px"
    wide: str = "1536px"


@dataclass(frozen=True)
class ZIndexTokens:
    """Camadas z-index."""
    dropdown: int = 100
    sticky: int = 200
    modal: int = 300
    popover: int = 400
    toast: int = 500
    tooltip: int = 600


# ── Instância única (Singleton) ──

TOKENS = {
    "color": ColorTokens(),
    "spacing": SpacingTokens(),
    "typography": TypographyTokens(),
    "radius": RadiusTokens(),
    "shadow": ShadowTokens(),
    "transition": TransitionTokens(),
    "breakpoint": BreakpointTokens(),
    "z_index": ZIndexTokens(),
}


def get_token(path: str) -> str | int | list:
    """Acessa token por path dot-notation: 'color.semantic.bg-primary'."""
    keys = path.split(".")
    value = TOKENS
    for key in keys:
        value = getattr(value, key) if hasattr(value, key) else value.get(key)
        if value is None:
            raise KeyError(f"Token not found: {path}")
    return value