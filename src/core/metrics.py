"""Metrics & Observability — Prometheus metrics export + structured logging.

Fornece métricas Prometheus, histogramas de latência, contadores, gauges.
"""

from __future__ import annotations

import time
import functools
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Generator
from collections import defaultdict
from collections.abc import Mapping

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# METRICS REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

class MetricsRegistry:
    """Registry thread-safe para métricas Prometheus + fallback em memória."""
    
    def __init__(self, namespace: str = "asi"):
        self.namespace = namespace
        self._lock = threading.RLock()
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._prometheus_counters: Dict = {}
        self._prometheus_gauges: Dict = {}
        self._prometheus_histograms: Dict = {}
        
        if PROMETHEUS_AVAILABLE:
            self._registry = CollectorRegistry()
        else:
            self._registry = None
    
    # ── Counters ──────────────────────────────────────────────────────────
    
    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> "CounterWrapper":
        """Cria/retorna um counter."""
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._prometheus_counters and PROMETHEUS_AVAILABLE:
                self._prometheus_counters[key] = Counter(
                    name, f"Counter for {name}",
                    labelnames=list(labels.keys()) if labels else [],
                    namespace=self.namespace,
                    registry=self._registry,
                )
        
        return CounterWrapper(self, key, labels)
    
    def inc_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Incrementa counter."""
        key = self._make_key(name, labels)
        
        with self._lock:
            self._counters[key] += value
            
            if PROMETHEUS_AVAILABLE and key in self._prometheus_counters:
                counter = self._prometheus_counters[key]
                if labels:
                    counter.labels(**labels).inc(value)
                else:
                    counter.inc(value)
    
    # ── Gauges ────────────────────────────────────────────────────────────
    
    def gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> "GaugeWrapper":
        """Cria/retorna um gauge."""
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._prometheus_gauges and PROMETHEUS_AVAILABLE:
                self._prometheus_gauges[key] = Gauge(
                    name, f"Gauge for {name}",
                    labelnames=list(labels.keys()) if labels else [],
                    namespace=self.namespace,
                    registry=self._registry,
                )
        
        return GaugeWrapper(self, key, labels)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Define valor do gauge."""
        key = self._make_key(name, labels)
        
        with self._lock:
            self._gauges[key] = value
            
            if PROMETHEUS_AVAILABLE and key in self._prometheus_gauges:
                gauge = self._prometheus_gauges[key]
                if labels:
                    gauge.labels(**labels).set(value)
                else:
                    gauge.set(value)
    
    # ── Histograms ────────────────────────────────────────────────────────
    
    def histogram(self, name: str, buckets: Optional[list] = None, 
                  labels: Optional[Dict[str, str]] = None) -> "HistogramWrapper":
        """Cria/retorna um histogram."""
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._prometheus_histograms and PROMETHEUS_AVAILABLE:
                self._prometheus_histograms[key] = Histogram(
                    name, f"Histogram for {name}",
                    buckets=buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
                    labelnames=list(labels.keys()) if labels else [],
                    namespace=self.namespace,
                    registry=self._registry,
                )
        
        return HistogramWrapper(self, key, labels)
    
    def observe_histogram(self, name: str, value: float, 
                          labels: Optional[Dict[str, str]] = None) -> None:
        """Registra observação no histogram."""
        key = self._make_key(name, labels)
        
        with self._lock:
            self._histograms[key].append(value)
            
            if PROMETHEUS_AVAILABLE and key in self._prometheus_histograms:
                hist = self._prometheus_histograms[key]
                if labels:
                    hist.labels(**labels).observe(value)
                else:
                    hist.observe(value)
    
    # ── Timing Context Manager ──────────────────────────────────────────
    
    @contextmanager
    def time(self, name: str, labels: Optional[Dict[str, str]] = None) -> Generator[None, None, None]:
        """Context manager para medir tempo de execução."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000  # ms
            self.observe_histogram(f"{name}_duration_ms", value=elapsed, labels=labels)
            self.inc_counter(f"{name}_total", labels=labels)
    
    def timed(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Decorator para medir tempo de função."""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.time(name, labels):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # ── Export ────────────────────────────────────────────────────────────
    
    def export_prometheus(self) -> bytes:
        """Exporta métricas no formato Prometheus text format."""
        if not PROMETHEUS_AVAILABLE:
            return b"# Prometheus client not available\n"
        
        return generate_latest(self._registry)
    
    def export_json(self) -> Dict:
        """Exporta métricas em JSON (fallback sem Prometheus)."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "avg": sum(v) / len(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }
    
    # ── Helpers ──────────────────────────────────────────────────────────
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Gera chave única para nome + labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# ═══════════════════════════════════════════════════════════════════════════
# WRAPPER CLASSES
# ═══════════════════════════════════════════════════════════════════════════

class CounterWrapper:
    def __init__(self, registry: MetricsRegistry, key: str, labels: Optional[Dict[str, str]]):
        self._registry = registry
        self._key = key
        self._labels = labels
    
    def inc(self, value: float = 1.0) -> None:
        self._registry.inc_counter("", value, self._labels)


class GaugeWrapper:
    def __init__(self, registry: MetricsRegistry, key: str, labels: Optional[Dict[str, str]]):
        self._registry = registry
        self._key = key
        self._labels = labels
    
    def set(self, value: float) -> None:
        self._registry.set_gauge("", value, self._labels)
    
    def inc(self, value: float = 1.0) -> None:
        with self._registry._lock:
            current = self._registry._gauges.get(self._key, 0)
            self._registry.set_gauge("", current + value, self._labels)
    
    def dec(self, value: float = 1.0) -> None:
        self.inc(-value)


class HistogramWrapper:
    def __init__(self, registry: MetricsRegistry, key: str, labels: Optional[Dict[str, str]]):
        self._registry = registry
        self._key = key
        self._labels = labels
    
    def observe(self, value: float) -> None:
        self._registry.observe_histogram("", value, self._labels)


# ═══════════════════════════════════════════════════════════════════════════
# DECORATORS & CONTEXT MANAGERS
# ═══════════════════════════════════════════════════════════════════════════

def track_latency(registry: MetricsRegistry, name: str, 
                  labels: Optional[Dict[str, str]] = None):
    """Decorator para trackear latência de função."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                registry.observe_histogram(f"{name}_duration_ms", elapsed)
                registry.inc_counter(f"{name}_total")
        return wrapper
    return decorator


@contextmanager
def track_operation(registry: MetricsRegistry, operation: str,
                    labels: Optional[Dict[str, str]] = None):
    """Context manager para trackear operação."""
    start = time.perf_counter()
    try:
        yield
    except Exception as e:
        registry.inc_counter(f"{operation}_errors", labels=labels)
        raise
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        registry.observe_histogram(f"{operation}_duration_ms", elapsed, labels=labels)
        registry.inc_counter(f"{operation}_total", labels=labels)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL REGISTRY & CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

_global_registry: Optional[MetricsRegistry] = None
_registry_lock = threading.Lock()


def get_metrics_registry(namespace: str = "asi") -> MetricsRegistry:
    """Retorna registry global (singleton)."""
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = MetricsRegistry(namespace)
        return _global_registry


def get_metrics_registry_for_test() -> MetricsRegistry:
    """Cria novo registry para testes (não singleton)."""
    return MetricsRegistry("asi_test")


# Convenience functions usando registry global
def inc_counter(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
    get_metrics_registry().inc_counter(name, value, labels)

def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    get_metrics_registry().set_gauge(name, value, labels)

def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    get_metrics_registry().observe_histogram(name, value, labels)

@contextmanager
def time_operation(name: str, labels: Optional[Dict[str, str]] = None):
    with get_metrics_registry().time(name, labels):
        yield

def timed(name: str, labels: Optional[Dict[str, str]] = None):
    return get_metrics_registry().timed(name, labels)