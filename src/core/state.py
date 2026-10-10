"""ASI Streamlit State Machine — SelectionState + EventOrigin + debounce.

Machine de estados para cross-filter (mapa ↔ gráficos ↔ tabelas) sem loops
de re-render. Usa origem do evento + debounce por origem (150ms).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import streamlit as st


class EventOrigin(Enum):
    """Origem do evento — usada para debounce inteligente."""
    USER_MAP_CLICK = "map_click"
    USER_MAP_BOX = "map_box"
    USER_CHART_CLICK = "chart_click"
    USER_CHART_BRUSH = "chart_brush"
    USER_TABLE_SELECT = "table_select"
    USER_FILTER_CHANGE = "filter_change"
    PROGRAMMATIC = "programmatic"


@dataclass
class SelectionState:
    """Estado global de seleção + filtros + controle de loop."""

    # ── Seleção Ativa ──
    selected_point: dict | None = None
    selected_points: list[dict] = field(default_factory=list)

    # ── Filtros ──
    twi_threshold: float = 0.0
    selected_bairro: str = "Todos"
    active_layers: set = field(default_factory=lambda: {"points"})
    time_range: tuple[int, int] = (2000, 2030)

    # ── Controle de Loop ──
    last_origin: EventOrigin = EventOrigin.PROGRAMMATIC
    last_update_ts: float = 0
    debounce_ms: int = 150

    def update(self, **kwargs: Any) -> bool:
        """Atualiza estado se não for debounce/loop.

        Returns:
            bool: True se estado mudou, False se ignorado (debounce)
        """
        now = time.time() * 1000
        origin = kwargs.pop("_origin", EventOrigin.PROGRAMMATIC)

        # Verifica se algum valor realmente mudou ANTES do debounce
        values_changed = False
        for key, value in kwargs.items():
            if hasattr(self, key):
                current = getattr(self, key)
                if current != value:
                    values_changed = True
                    break

        # Debounce: ignora updates rápidos da MESMA origem com MESMOS valores
        # Exceções: cliques do usuário, updates programáticos (sempre processam)
        if (
            not values_changed
            and origin == self.last_origin
            and now - self.last_update_ts < self.debounce_ms
            and origin not in (
                EventOrigin.USER_MAP_CLICK,
                EventOrigin.USER_CHART_CLICK,
                EventOrigin.PROGRAMMATIC,
            )
        ):
            return False

        changed = False
        for key, value in kwargs.items():
            if hasattr(self, key):
                current = getattr(self, key)
                if current != value:
                    setattr(self, key, value)
                    changed = True

        if changed:
            self.last_origin = origin
            self.last_update_ts = now
        return changed

    def clear_selection(self) -> None:
        """Limpa seleção ativa."""
        self.selected_point = None
        self.selected_points = []


# ── Singleton no session_state ────────────────────────────────

def get_selection_state() -> SelectionState:
    """Retorna singleton no session_state."""
    if "asi_selection" not in st.session_state:
        st.session_state.asi_selection = SelectionState()
    return st.session_state.asi_selection