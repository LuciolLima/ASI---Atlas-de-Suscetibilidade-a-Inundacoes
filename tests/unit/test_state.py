"""Testes unitários para SelectionState + EventOrigin + debounce."""

from __future__ import annotations

import time
import pytest
from src.core.state import SelectionState, EventOrigin


def test_debounce_same_origin():
    """Updates rápidos da mesma origem COM MESMO VALOR são ignorados (debounce)."""
    state = SelectionState()
    state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE)
    time.sleep(0.05)  # 50ms < 150ms
    changed = state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE)  # mesmo valor
    assert changed is False  # debounced


def test_debounce_different_values_not_ignored():
    """Updates rápidos com valores DIFERENTES não sofrem debounce."""
    state = SelectionState()
    state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE)
    time.sleep(0.05)  # 50ms < 150ms
    changed = state.update(twi_threshold=6.0, _origin=EventOrigin.USER_FILTER_CHANGE)  # valor diferente
    assert changed is True  # não debounced - valor mudou


def test_click_never_debounced():
    """Cliques de usuário SEMPRE passam (sem debounce)."""
    state = SelectionState()
    state.update(selected_point={"lat": 1, "lon": 2}, _origin=EventOrigin.USER_MAP_CLICK)
    time.sleep(0.05)
    changed = state.update(selected_point={"lat": 3, "lon": 4}, _origin=EventOrigin.USER_MAP_CLICK)
    assert changed is True  # cliques sempre processados


def test_different_origins_no_debounce():
    """Origens diferentes não sofrem debounce."""
    state = SelectionState()
    state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE)
    time.sleep(0.05)
    changed = state.update(selected_point={"lat": 1, "lon": 2}, _origin=EventOrigin.USER_MAP_CLICK)
    assert changed is True  # origem diferente = sem debounce


def test_programmatic_no_debounce():
    """Updates internos (PROGRAMMATIC) não sofrem debounce."""
    state = SelectionState()
    state.update(twi_threshold=5.0, _origin=EventOrigin.PROGRAMMATIC)
    time.sleep(0.05)
    changed = state.update(twi_threshold=6.0, _origin=EventOrigin.PROGRAMMATIC)
    assert changed is True  # interno não debounce


def test_clear_selection():
    """Limpa seleção ativa."""
    state = SelectionState()
    state.update(selected_point={"lat": 1, "lon": 2}, _origin=EventOrigin.USER_MAP_CLICK)
    state.clear_selection()
    assert state.selected_point is None
    assert state.selected_points == []


def test_update_returns_changed_flag():
    """update() retorna True se mudou, False se ignorado."""
    state = SelectionState()
    # Primeira vez = mudou
    assert state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE) is True
    # Mesmo valor = não mudou
    assert state.update(twi_threshold=5.0, _origin=EventOrigin.USER_FILTER_CHANGE) is False
    # Valor diferente = mudou
    assert state.update(twi_threshold=6.0, _origin=EventOrigin.USER_FILTER_CHANGE) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])