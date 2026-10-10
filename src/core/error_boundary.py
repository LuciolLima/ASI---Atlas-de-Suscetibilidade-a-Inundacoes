"""Error Boundaries — Granular error handling with fallback UI.

Error boundaries isolados por seção: mapa, analytics, inspector, API hub.
"""

from __future__ import annotations

import streamlit as st
import traceback
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Optional, Any, TypeVar, ParamSpec
from dataclasses import dataclass

from .metrics import get_metrics_registry

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("asi.error_boundary")

T = TypeVar("T")
P = ParamSpec("P")


# ═══════════════════════════════════════════════════════════════════════════
# ERROR BOUNDARY CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ErrorBoundaryConfig:
    """Configuração do error boundary."""
    title: str = "Erro"
    fallback_message: str = "Ocorreu um erro inesperado nesta seção."
    show_details: bool = False
    log_level: int = logging.ERROR
    on_error: Callable[[Exception], None] = None


@contextmanager
def error_boundary(
    name: str,
    config: Optional[ErrorBoundaryConfig] = None,
    fallback_ui: Optional[Callable[[], None]] = None,
) -> Generator[None, None, None]:
    """
    Context manager para error boundary isolado.
    
    Args:
        name: Nome identificador do boundary (ex: "map", "analytics", "inspector")
        config: Configuração customizada
        fallback_ui: Função opcional para renderizar UI de fallback customizada
    
    Usage:
        with error_boundary("map", config=ErrorBoundaryConfig(title="Erro no Mapa")):
            render_map()
    """
    config = config or ErrorBoundaryConfig()
    registry = get_metrics_registry()
    
    try:
        yield
    except Exception as e:
        # Log estruturado
        logger.log(
            config.log_level,
            f"[{name}] {type(e).__name__}: {e}",
            extra={"boundary": name, "error_type": type(e).__name__},
            exc_info=True,
        )
        
        # Métricas
        get_metrics_registry().inc_counter(
            f"errors_{name}_total",
            labels={"error_type": type(e).__name__}
        )
        
        # Callback customizado
        if config.on_error:
            try:
                config.on_error(e)
            except Exception:
                pass
        
        # Fallback UI
        if fallback_ui:
            try:
                fallback_ui()
            except Exception:
                st.error(f"Erro crítico no fallback de {name}")
        else:
            _render_default_fallback(config, e, name)


def _render_default_fallback(config: ErrorBoundaryConfig, error: Exception, name: str) -> None:
    """Renderiza fallback padrão."""
    st.error(f"⚠️ {config.title}")
    st.markdown(config.fallback_message)
    
    if config.show_details:
        with st.expander("Detalhes técnicos"):
            st.code("".join(traceback.format_exception(type(error), error, error.__traceback__)))
    
    # Botão para recarregar seção
    if st.button(f"🔄 Tentar novamente", key=f"retry_{name}"):
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════

def with_error_boundary(
    name: str,
    config: Optional[ErrorBoundaryConfig] = None,
    fallback_ui: Optional[Callable[[], None]] = None,
) -> Callable[[Callable[P, T]], Callable[P, Optional[T]]]:
    """
    Decorator para aplicar error boundary a uma função.
    
    Usage:
        @with_error_boundary("map", config=ErrorBoundaryConfig(title="Erro no Mapa"))
        def render_map():
            ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, Optional[T]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            with error_boundary(name, config, fallback_ui=None):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_render(
    name: str,
    fallback: Any = None,
    config: Optional[ErrorBoundaryConfig] = None,
) -> Callable[[Callable[P, T]], Callable[P, Any]]:
    """
    Decorator que retorna valor de fallback em caso de erro.
    
    Usage:
        @safe_render("analytics", fallback=[])
        def get_analytics_data():
            ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, Any]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            try:
                with error_boundary(name, config):
                    return func(*args, **kwargs)
            except Exception:
                return fallback
        return wrapper
    return decorator


# ════════════════════════════════════════════════════════════════════════════
# STREAMLIT ERROR BOUNDARY COMPONENT
# ════════════════════════════════════════════════════════════════════════════

def analytics_error_boundary(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator específico para seções de analytics.
    
    Usage:
        @analytics_error_boundary("precipitacao")
        def render_precipitacao():
            ...
    """
    return with_error_boundary(
        name,
        config=ErrorBoundaryConfig(
            title=f"Erro em {name.title()}",
            fallback_message="Os dados de analytics não puderam ser carregados.",
            show_details=True,
        ),
    )


def map_error_boundary(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Error boundary específico para mapa."""
    return with_error_boundary(
        name,
        config=ErrorBoundaryConfig(
            title="Erro no Mapa",
            fallback_message="O mapa não pôde ser renderizado. Verifique a conexão e tente recarregar.",
        ),
    )


def report_error_boundary(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Error boundary específico para relatórios."""
    return with_error_boundary(
        name,
        config=ErrorBoundaryConfig(
            title="Erro no Relatório",
            fallback_message="Não foi possível gerar o relatório técnico.",
            show_details=True,
        ),
    )


# ════════════════════════════════════════════════════════════════════════════
# GLOBAL ERROR HANDLER
# ════════════════════════════════════════════════════════════════════════════

def setup_global_error_handler() -> None:
    """Configura handler global para exceções não capturadas."""
    import sys
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            "Exceção não tratada",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        
        # Métrica
        get_metrics_registry().inc_counter("unhandled_exceptions_total")
    
    sys.excepthook = handle_exception


# ════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════

__all__ = [
    "ErrorBoundaryConfig",
    "error_boundary",
    "with_error_boundary",
    "safe_render",
    "analytics_error_boundary",
    "map_error_boundary",
    "report_error_boundary",
    "setup_global_error_handler",
]