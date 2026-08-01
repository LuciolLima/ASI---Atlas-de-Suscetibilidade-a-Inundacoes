#!/usr/bin/env python3
"""Benchmark ASI Data Layer — Mede latência de queries espaciais.

Uso:
    python scripts/benchmark.py

Métricas alvo:
    - get_buffer_analysis + get_events_nearby < 50ms (P95)
    - Zero I/O disco no hot path
    - Cache hit rate > 99%
"""

from __future__ import annotations

import time
import statistics
import tracemalloc
from src.processing.data_layer import get_data_layer


def benchmark_clicks(n: int = 500) -> list[float]:
    """Simula N cliques no mapa medindo latência end-to-end."""
    dl = get_data_layer()
    lat, lon = -8.28, -35.03  # Cabo de Santo Agostinho

    times = []
    for i in range(n):
        start = time.perf_counter()
        
        # Hot path: buffer analysis + eventos próximos
        dl.get_buffer_analysis(lat, lon, 500)
        dl.get_events_nearby(lat, lon, 500)
        
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
        
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{n} completados...")

    return times


def benchmark_ranking(n: int = 50) -> list[float]:
    """Mede query de ranking de bairros (DuckDB aggregation)."""
    dl = get_data_layer()
    times = []
    for _ in range(n):
        start = time.perf_counter()
        dl.get_ranking_bairros()
        times.append((time.perf_counter() - start) * 1000)
    return times


def check_memory_leak(iterations: int = 1000) -> None:
    """Verifica se há vazamento de memória no hot path."""
    dl = get_data_layer()
    lat, lon = -8.28, -35.03

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    for _ in range(iterations):
        dl.get_buffer_analysis(lat, lon, 500)

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print("\n[MEMÓRIA] Top 5 alocações:")
    for stat in top_stats[:5]:
        print(f"  {stat}")


def print_percentiles(times: list[float], label: str) -> None:
    """Imprime percentis formatados."""
    if not times:
        return
    sorted_times = sorted(times)
    n = len(times)
    print(f"\n[{label}] N={n}")
    print(f"  P50 (mediana): {statistics.median(times):.2f}ms")
    print(f"  P90:           {sorted_times[int(n * 0.90)]:.2f}ms")
    print(f"  P95:           {sorted_times[int(n * 0.95)]:.2f}ms")
    print(f"  P99:           {sorted_times[int(n * 0.99)]:.2f}ms")
    print(f"  Max:           {max(times):.2f}ms")
    print(f"  Mean:          {statistics.mean(times):.2f}ms")


def main() -> None:
    print("=" * 60)
    print("ASI DATA LAYER BENCHMARK")
    print("=" * 60)

    # Warmup (JIT DuckDB, cache Python)
    print("\n[Warmup] 10 iterações...")
    dl = get_data_layer()
    for _ in range(10):
        dl.get_buffer_analysis(-8.28, -35.03, 500)
        dl.get_events_nearby(-8.28, -35.03, 500)

    # Benchmark principal
    print("\n[Benchmark] 500 cliques simulados (buffer + events)...")
    click_times = benchmark_clicks(500)
    print_percentiles(click_times, "CLICK → BUFFER + EVENTS")

    print("\n[Benchmark] 50 rankings de bairros...")
    ranking_times = benchmark_ranking(50)
    print_percentiles(ranking_times, "RANKING BAIRROS")

    # Verificação de memória
    print("\n[Verificação] Memory leak test (1000 iterações)...")
    check_memory_leak(1000)

    # Critérios de aceite
    print("\n" + "=" * 60)
    print("CRITÉRIOS DE ACEITE")
    print("=" * 60)
    p95_click = sorted(click_times)[int(len(click_times) * 0.95)]
    p95_ranking = sorted(ranking_times)[int(len(ranking_times) * 0.95)]

    ok_click = p95_click < 50
    ok_ranking = p95_ranking < 100

    print(f"  Click P95 < 50ms:     {'✓ PASS' if ok_click else '✗ FAIL'} ({p95_click:.1f}ms)")
    print(f"  Ranking P95 < 100ms:  {'✓ PASS' if ok_ranking else '✗ FAIL'} ({p95_ranking:.1f}ms)")
    print(f"  Overall:              {'✓ TODOS PASSAM' if (ok_click and ok_ranking) else '✗ ALGUNS FALHAM'}")


if __name__ == "__main__":
    main()