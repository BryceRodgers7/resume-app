"""HTTP client for the FHIR-OMOP backend service.

The Streamlit page used to call ``DatabaseManager`` directly, which held a
Supabase connection inside the Streamlit websocket and routinely hung the
page when a handshake stalled. The backend service now owns every DB I/O
path; this module is a thin ``requests``-based client that mirrors its
endpoint surface 1:1.

Configuration
-------------
``FHIR_OMOP_API_URL`` — base URL of the backend (e.g.
``http://fhir-omop-api.flycast`` on Fly's private network, or
``http://localhost:8080`` locally). **Required** — the page renders a
configuration banner instead of working when this is unset.

``FHIR_OMOP_API_KEY`` — optional shared secret; sent as ``X-API-Key`` on
every request if present. Pair with ``API_SHARED_SECRET`` on the backend.

Retry semantics
---------------
Each public method tries once, and on a network error or 5xx response,
waits 2 seconds and tries once more. 4xx responses fail immediately — they
indicate a client mistake (bad payload, unknown endpoint) and retrying
won't help. The same ``Idempotency-Key`` is sent on the retry, so the
backend de-duplicates writes correctly even if the first attempt's commit
landed and only the response was lost.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


# Public exceptions ---------------------------------------------------------
class ApiNotConfiguredError(RuntimeError):
    """Raised when ``FHIR_OMOP_API_URL`` is missing.

    The page catches this at construction time and renders a configuration
    banner instead of trying to make requests.
    """


class ApiError(RuntimeError):
    """Backend returned a non-2xx response or the request could not complete."""


_DEFAULT_TIMEOUT_SECONDS = 30
_RETRY_DELAY_SECONDS = 2


class FhirOmopApiClient:
    """Thin HTTP client mirroring the backend's endpoint surface.

    One instance per Streamlit process — cache with ``@st.cache_resource``
    so the underlying ``requests.Session`` (and its keep-alive connection
    pool to the backend) survives across reruns.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ):
        self.base_url = (base_url or os.getenv("FHIR_OMOP_API_URL") or "").rstrip("/")
        if not self.base_url:
            raise ApiNotConfiguredError(
                "FHIR_OMOP_API_URL is not set. The FHIR-OMOP demo page "
                "delegates all database work to a backend service — set "
                "this env var to the backend's base URL."
            )
        self.api_key = api_key or os.getenv("FHIR_OMOP_API_KEY")
        self.timeout = timeout
        self._session = requests.Session()
        if self.api_key:
            self._session.headers["X-API-Key"] = self.api_key

    # -- Public methods --------------------------------------------------
    # ``on_retry`` (where supported) is invoked once with the failure
    # exception if the first attempt fails and a retry is about to happen.
    # Pages use it to update an ``st.status`` block with "retrying…" so the
    # user sees what's going on instead of a silent multi-second pause.
    def healthz(self) -> Dict[str, Any]:
        return self._request("GET", "/healthz")

    def reset(self, on_retry: Optional[Callable[[Exception], None]] = None) -> Dict[str, Any]:
        return self._request("POST", "/reset", on_retry=on_retry)

    def ingest_sample(
        self,
        idem_key: Optional[str] = None,
        on_retry: Optional[Callable[[Exception], None]] = None,
    ) -> Dict[str, Any]:
        return self._request("POST", "/ingest/sample", idem_key=idem_key, on_retry=on_retry)

    def ingest(
        self,
        bundles: List[dict],
        source_label: str = "Loaded uploaded bundles",
        idem_key: Optional[str] = None,
        on_retry: Optional[Callable[[Exception], None]] = None,
    ) -> Dict[str, Any]:
        return self._request(
            "POST", "/ingest",
            json={"bundles": bundles, "source_label": source_label},
            idem_key=idem_key,
            on_retry=on_retry,
        )

    def transform(
        self,
        idem_key: Optional[str] = None,
        on_retry: Optional[Callable[[Exception], None]] = None,
    ) -> Dict[str, Any]:
        return self._request("POST", "/transform", idem_key=idem_key, on_retry=on_retry)

    def dashboard(self) -> Dict[str, Any]:
        return self._request("GET", "/dashboard")

    @staticmethod
    def new_idempotency_key() -> str:
        return str(uuid.uuid4())

    # -- Internals -------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        idem_key: Optional[str] = None,
        on_retry: Optional[Callable[[Exception], None]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = {}
        if idem_key:
            headers["Idempotency-Key"] = idem_key

        last_err: Optional[Exception] = None
        for attempt in (1, 2):
            try:
                t0 = time.perf_counter()
                logger.info("api %s %s (attempt %d)", method, path, attempt)
                resp = self._session.request(
                    method, url,
                    json=json,
                    headers=headers or None,
                    timeout=self.timeout,
                )
                elapsed = time.perf_counter() - t0
                logger.info(
                    "api %s %s → %d in %.3fs",
                    method, path, resp.status_code, elapsed,
                )

                if 200 <= resp.status_code < 300:
                    return resp.json() if resp.content else {}

                if 400 <= resp.status_code < 500:
                    # Client error — retrying won't help.
                    raise ApiError(
                        f"{method} {path} returned {resp.status_code}: "
                        f"{resp.text[:500]}"
                    )

                last_err = ApiError(
                    f"{method} {path} returned {resp.status_code}: "
                    f"{resp.text[:500]}"
                )

            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = e

            if attempt == 1:
                logger.warning(
                    "api %s %s failed (%s) — retrying in %.1fs",
                    method, path, last_err, _RETRY_DELAY_SECONDS,
                )
                if on_retry is not None:
                    try:
                        on_retry(last_err)
                    except Exception:
                        logger.exception("on_retry callback raised — ignoring")
                time.sleep(_RETRY_DELAY_SECONDS)

        assert last_err is not None
        raise ApiError(f"{method} {path} failed after retry: {last_err}")
