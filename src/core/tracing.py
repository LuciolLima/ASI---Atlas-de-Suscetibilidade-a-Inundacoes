"""OpenTelemetry Distributed Tracing — Instrumentação automática e manual.

Integração com OpenTelemetry para tracing distribuído, métricas e logs.
"""

from __future__ import annotations

import os
import functools
import contextvars
from contextlib import contextmanager
from typing import Callable, Optional, Dict, Any, Generator
from dataclasses import dataclass, field

try:
    from opentelemetry import trace, metrics, baggage
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased, ParentBasedTraceIdRatio
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.urllib import URLLibInstrumentor
    from opentelemetry.propagate import inject, extract
    from opentelemetry.trace import Status, StatusCode, SpanKind
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None
    metrics = None
    # Define SpanKind as a simple class when OTEL not available
    class SpanKind:
        INTERNAL = "internal"
        SERVER = "server"
        CLIENT = "client"
        PRODUCER = "producer"
        CONSUMER = "consumer"

from src.core.metrics import get_metrics_registry


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TracingConfig:
    """Configuração do tracing OpenTelemetry."""
    service_name: str = "asi"
    service_version: str = "3.2.0"
    environment: str = "production"
    otlp_endpoint: Optional[str] = None  # e.g., "http://otel-collector:4317"
    console_export: bool = False
    sample_rate: float = 1.0  # 1.0 = 100%
    enable_console_export: bool = False


# ════════════════════════════════════════════════════════════════════════════
# TRACING SETUP
# ═══════════════════════════════════════════════════════════════════════════

_tracer_provider: Optional[trace.TracerProvider] = None
_meter_provider: Optional[metrics.MeterProvider] = None
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None
_initialized = False


def init_tracing(config: Optional[TracingConfig] = None) -> None:
    """Inicializa OpenTelemetry tracing e metrics."""
    global _tracer_provider, _meter_provider, _tracer, _meter, _initialized
    
    if _initialized:
        return
    
    if not OTEL_AVAILABLE:
        print("⚠️ OpenTelemetry not available. Install: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")
        return
    
    config = config or TracingConfig()
    
    # Resource
    resource = Resource.create({
        SERVICE_NAME: config.service_name,
        SERVICE_VERSION: config.service_version,
        "deployment.environment": config.environment,
    })
    
    # ── Tracer Provider ──
    _tracer_provider = TracerProvider(
        resource=resource,
        sampler=ParentBased(TraceIdRatioBased(config.sample_rate)),
    )
    
    # Exporters
    if config.otlp_endpoint:
        span_exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint, insecure=True)
        _tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    
    if config.console_export or config.enable_console_export:
        _tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    
    trace.set_tracer_provider(_tracer_provider)
    _tracer = trace.get_tracer(config.service_name)
    
    # ── Meter Provider ──
    readers = []
    if config.otlp_endpoint:
        readers.append(PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=config.otlp_endpoint, insecure=True),
            export_interval_millis=30000,
        ))
    if config.console_export or config.enable_console_export:
        readers.append(PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=30000,
        ))
    
    _meter_provider = MeterProvider(
        resource=resource,
        metric_readers=readers,
    )
    metrics.set_meter_provider(_meter_provider)
    _meter = metrics.get_meter(config.service_name)
    
    # Auto-instrumentation
    RequestsInstrumentor().instrument()
    URLLibInstrumentor().instrument()
    
    _initialized = True


def get_tracer() -> Optional[trace.Tracer]:
    """Retorna tracer global."""
    return _tracer


def get_meter() -> Optional[metrics.Meter]:
    """Retorna meter global."""
    return _meter


def is_initialized() -> bool:
    return _initialized


# ════════════════════════════════════════════════════════════════════════════
# SPAN HELPERS
# ════════════════════════════════════════════════════════════════════════════

@contextmanager
def start_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
    links: Optional[list] = None,
) -> Generator[trace.Span, None, None]:
    """Context manager para criar span manual."""
    if not _initialized or not _tracer:
        yield None
        return
    
    span = _tracer.start_span(name, kind=kind, attributes=attributes, links=links)
    try:
        yield span
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise
    finally:
        span.end()


def traced(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator para auto-trace de função."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        span_name = name or f"{func.__module__}.{func.__qualname__}"
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _initialized or not _tracer:
                return func(*args, **kwargs)
            
            with _tracer.start_as_current_span(
                span_name,
                kind=kind,
                attributes=attributes,
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        return wrapper
    return decorator


@contextmanager
def trace_operation(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    kind: SpanKind = SpanKind.INTERNAL,
) -> Generator[trace.Span, None, None]:
    """Context manager para operação traced."""
    with start_span(name, attributes=attributes, kind=kind) as span:
        yield span


# ════════════════════════════════════════════════════════════════════════════
# BAGGAGE / CONTEXT PROPAGATION
# ════════════════════════════════════════════════════════════════════════════

def set_baggage(key: str, value: str) -> None:
    """Define baggage item."""
    if not OTEL_AVAILABLE:
        return
    ctx = baggage.set_baggage(key, value)
    baggage.set_baggage(key, value)


def get_baggage(key: str) -> Optional[str]:
    """Obtém baggage item."""
    if not OTEL_AVAILABLE:
        return None
    return baggage.get_baggage(key)


def inject_context(carrier: Dict[str, str]) -> None:
    """Injecta contexto de trace em carrier (headers)."""
    if not OTEL_AVAILABLE:
        return
    inject(carrier)


def extract_context(carrier: Dict[str, str]) -> Any:
    """Extrai contexto de trace de carrier (headers)."""
    if not OTEL_AVAILABLE:
        return None
    return extract(carrier)


# ════════════════════════════════════════════════════════════════════════════
# CUSTOM METRICS (OpenTelemetry)
# ════════════════════════════════════════════════════════════════════════════

class OTelMetrics:
    """Wrapper para métricas OpenTelemetry."""
    
    def __init__(self, meter: Optional[metrics.Meter] = None):
        self.meter = meter or get_meter()
        self._counters: Dict = {}
        self._histograms: Dict = {}
        self._gauges: Dict = {}
    
    def counter(self, name: str, description: str = "", unit: str = "1") -> Any:
        key = name
        if key not in self._counters and self.meter:
            self._counters[key] = self.meter.create_counter(
                name=name,
                description=description,
                unit=unit,
            )
        return self._counters.get(key)
    
    def histogram(self, name: str, description: str = "", unit: str = "ms") -> Any:
        key = name
        if key not in self._histograms and self.meter:
            self._histograms[key] = self.meter.create_histogram(
                name=name,
                description=description,
                unit=unit,
            )
        return self._histograms.get(key)
    
    def gauge(self, name: str, description: str = "", unit: str = "1") -> Any:
        key = name
        if key not in self._gauges and self.meter:
            self._gauges[key] = self.meter.create_gauge(
                name=name,
                description=description,
                unit=unit,
            )
        return self._gauges.get(key)


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH EXISTING METRICS
# ════════════════════════════════════════════════════════════════════════════

def bridge_to_otel() -> None:
    """Ponte entre métricas customizadas e OpenTelemetry."""
    # O registry customizado já exporta para Prometheus
    # Aqui poderíamos sincronizar contadores se necessário
    pass


# ════════════════════════════════════════════════════════════════════════════
# CONTEXT VARIABLES FOR TRACE ID
# ════════════════════════════════════════════════════════════════════════════

_current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)
_current_span_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("span_id", default=None)


def get_current_trace_id() -> Optional[str]:
    return _current_trace_id.get()


def get_current_span_id() -> Optional[str]:
    return _current_span_id.get()


def set_current_span(span: Optional[Any]) -> None:
    if span and hasattr(span, "get_span_context"):
        ctx = span.get_span_context()
        _current_trace_id.set(format(ctx.trace_id, "032x"))
        _current_span_id.set(format(ctx.span_id, "016x"))
    else:
        _current_trace_id.set(None)
        _current_span_id.set(None)


# ════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════

__all__ = [
    "TracingConfig",
    "init_tracing",
    "get_tracer",
    "get_meter",
    "is_initialized",
    "start_span",
    "traced",
    "trace_operation",
    "set_baggage",
    "get_baggage",
    "inject_context",
    "extract_context",
    "OTelMetrics",
    "bridge_to_otel",
    "get_current_trace_id",
    "get_current_span_id",
    "set_current_span",
]