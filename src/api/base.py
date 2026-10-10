"""SISTEMA ASI — BASE PARA CLIENTES DE API EXTERNA
Versão: 1.0 — Arquitetura unificada com retry, rate limiting, cache e health checks
"""

from __future__ import annotations

import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, TypeVar

import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

T = TypeVar('T')

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class APIConfig:
    """Configuração imutável de uma API externa."""

    name: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5
    rate_limit_rps: float | None = None  # requests per second
    rate_limit_rpm: int | None = None    # requests per minute
    cache_ttl_seconds: int = 3600
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class APIResponse:
    """Resposta padronizada de uma chamada de API."""

    success: bool
    data: Any = None
    error: str | None = None
    status_code: int | None = None
    response_time_ms: float = 0.0
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.utcnow)
    from_cache: bool = False


class RateLimiter:
    """Rate limiter simples baseado em token bucket."""

    def __init__(self, rps: float | None = None, rpm: int | None = None):
        self.rps = rps
        self.rpm = rpm
        self._tokens = 1.0
        self._last_update = time.monotonic()
        self._minute_requests = 0
        self._minute_start = time.monotonic()

    def acquire(self) -> None:
        """Bloqueia até que um token esteja disponível."""
        now = time.monotonic()

        # Rate limit por segundo (token bucket)
        if self.rps is not None:
            elapsed = now - self._last_update
            self._tokens = min(1.0, self._tokens + elapsed * self.rps)
            if self._tokens < 1.0:
                sleep_time = (1.0 - self._tokens) / self.rps
                time.sleep(sleep_time)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0
            self._last_update = now

        # Rate limit por minuto
        if self.rpm is not None:
            elapsed_minute = now - self._minute_start
            if elapsed_minute >= 60:
                self._minute_requests = 0
                self._minute_start = now
            if self._minute_requests >= self.rpm:
                sleep_time = 60 - elapsed_minute
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self._minute_requests = 0
                self._minute_start = time.monotonic()
            self._minute_requests += 1


class APIClient(ABC):
    """Classe base abstrata para clientes de API externas."""

    def __init__(self, config: APIConfig):
        self.config = config
        self._session = self._create_session()
        self._rate_limiter = RateLimiter(config.rate_limit_rps, config.rate_limit_rpm)
        self._cache: dict[str, tuple[Any, datetime]] = {}

    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(self.config.headers)
        return session

    def _get_cache_key(self, endpoint: str, params: dict[str, Any] | None) -> str:
        """Gera chave de cache determinística."""
        param_str = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        return f"{endpoint}?{param_str}"

    def _get_from_cache(self, cache_key: str) -> Any | None:
        """Recupera do cache se não expirado."""
        if cache_key in self._cache:
            data, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < timedelta(seconds=self.config.cache_ttl_seconds):
                return data
            del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Armazena no cache com timestamp."""
        self._cache[cache_key] = (data, datetime.utcnow())

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> APIResponse:
        """Executa requisição HTTP com retry, rate limiting e cache."""
        correlation_id = str(uuid.uuid4())[:8]
        cache_key = self._get_cache_key(endpoint, params)

        # Verifica cache
        if use_cache and method == "GET":
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                logger.debug(f"[{self.config.name}] Cache hit: {cache_key} [{correlation_id}]")
                return APIResponse(
                    success=True,
                    data=cached,
                    correlation_id=correlation_id,
                    from_cache=True,
                )

        # Rate limiting
        self._rate_limiter.acquire()

        base = self.config.base_url.rstrip('/')
        if endpoint:
            url = f"{base}/{endpoint.lstrip('/')}"
        else:
            url = base
        start_time = time.monotonic()

        try:
            logger.info(f"[{self.config.name}] {method} {url} [{correlation_id}]")
            logger.debug(f"[{self.config.name}] Params: {params} [{correlation_id}]")
            
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.config.timeout,
            )
            response_time_ms = (time.monotonic() - start_time) * 1000

            # Log response info
            logger.debug(f"[{self.config.name}] Response status: {response.status_code}, time: {response_time_ms:.1f}ms [{correlation_id}]")

            if response.status_code == 200:
                try:
                    data = response.json()
                    # Verifica se a resposta indica erro (algumas APIs retornam 200 com erro no body)
                    if isinstance(data, dict) and (data.get("error") or data.get("status") == "error"):
                        error_msg = data.get("error") or data.get("message") or "API returned error in body"
                        logger.warning(f"[{self.config.name}] HTTP 200 but error in body: {error_msg} [{correlation_id}]")
                        return APIResponse(
                            success=False,
                            error=f"API error: {error_msg}",
                            status_code=response.status_code,
                            response_time_ms=response_time_ms,
                            correlation_id=correlation_id,
                        )
                    
                    if use_cache and method == "GET":
                        self._set_cache(cache_key, data)
                    logger.info(
                        f"[{self.config.name}] Success: {response.status_code} "
                        f"({response_time_ms:.1f}ms) [{correlation_id}]"
                    )
                    return APIResponse(
                        success=True,
                        data=data,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        correlation_id=correlation_id,
                    )
                except ValueError as e:
                    # Não é JSON válido
                    logger.warning(f"[{self.config.name}] Invalid JSON response: {response.text[:200]} [{correlation_id}]")
                    return APIResponse(
                        success=False,
                        error=f"Invalid JSON response: {e}",
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        correlation_id=correlation_id,
                    )
            
            # HTTP error status
            error_text = response.text[:500] if response.text else "No response body"
            logger.warning(
                f"[{self.config.name}] HTTP {response.status_code}: {error_text} [{correlation_id}]"
            )
            return APIResponse(
                success=False,
                error=f"HTTP {response.status_code}: {error_text}",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                correlation_id=correlation_id,
            )

        except requests.exceptions.Timeout:
            response_time_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"[{self.config.name}] Timeout after {self.config.timeout}s [{correlation_id}]")
            return APIResponse(
                success=False,
                error=f"Timeout after {self.config.timeout}s",
                response_time_ms=response_time_ms,
                correlation_id=correlation_id,
            )
        except requests.exceptions.ConnectionError as e:
            response_time_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"[{self.config.name}] Connection error: {e} [{correlation_id}]")
            return APIResponse(
                success=False,
                error=f"Connection error: {e}",
                response_time_ms=response_time_ms,
                correlation_id=correlation_id,
            )
        except requests.exceptions.RequestException as e:
            response_time_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"[{self.config.name}] Request failed: {e} [{correlation_id}]")
            return APIResponse(
                success=False,
                error=str(e),
                response_time_ms=response_time_ms,
                correlation_id=correlation_id,
            )
        except Exception as e:
            response_time_ms = (time.monotonic() - start_time) * 1000
            logger.exception(f"[{self.config.name}] Unexpected error [{correlation_id}]")
            return APIResponse(
                success=False,
                error=f"Unexpected error: {e}",
                response_time_ms=response_time_ms,
                correlation_id=correlation_id,
            )

    def get(self, endpoint: str, params: dict[str, Any] | None = None, use_cache: bool = True) -> APIResponse:
        """GET request com cache."""
        return self._make_request("GET", endpoint, params=params, use_cache=use_cache)

    def post(self, endpoint: str, json_data: dict[str, Any] | None = None, use_cache: bool = False) -> APIResponse:
        """POST request (sem cache por padrão)."""
        return self._make_request("POST", endpoint, json_data=json_data, use_cache=use_cache)

    @abstractmethod
    def health_check(self) -> APIResponse:
        """Verifica se a API está acessível."""
        ...

    @abstractmethod
    def fetch_data(self, **kwargs: Any) -> APIResponse:
        """Busca dados principais da API."""
        ...


def streamlit_cache_data(ttl_seconds: int = 3600, show_spinner: str = "Carregando...") -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator para cache nativo do Streamlit com configuração consistente."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @st.cache_data(show_spinner=show_spinner, ttl=ttl_seconds)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)
        return wrapper
    return decorator
