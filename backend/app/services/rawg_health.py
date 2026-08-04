"""
services/rawg_health.py — In-memory circuit breaker for the RAWG API.

States:
  CLOSED    — RAWG is healthy. All requests go to RAWG normally.
  OPEN      — RAWG is down. Requests fail-fast; Steam fallback is used.
  HALF_OPEN — Recovery timeout elapsed. One probe request is allowed through.
              If it succeeds  → circuit closes (RAWG is healthy again).
              If it fails     → circuit re-opens (RAWG is still down).

Configuration:
  FAILURE_THRESHOLD   — consecutive RAWG failures needed to open the circuit.
  RECOVERY_TIMEOUT_S  — seconds to wait in OPEN state before probing RAWG.
"""

import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)

FAILURE_THRESHOLD = 3       # trips the breaker after N consecutive failures
RECOVERY_TIMEOUT_S = 60     # seconds before HALF_OPEN probe is allowed


class _State:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class RawgCircuitBreaker:
    """Thread-safe in-memory circuit breaker for the RAWG upstream API."""

    def __init__(self) -> None:
        self._state = _State.CLOSED
        self._failures = 0
        self._opened_at: float = 0.0
        self._lock = Lock()

    # ── Public API ───────────────────────────────────────────────────────────

    @property
    def state(self) -> str:
        return self._state

    @property
    def is_open(self) -> bool:
        """True when RAWG should NOT be called (circuit is OPEN and not yet probing)."""
        with self._lock:
            if self._state == _State.OPEN:
                if self._recovery_timeout_elapsed():
                    # Transition to HALF_OPEN so one probe is allowed
                    self._state = _State.HALF_OPEN
                    logger.info(
                        "RAWG circuit breaker → HALF_OPEN (probing after %ds cooldown)",
                        RECOVERY_TIMEOUT_S,
                    )
                    return False   # let the probe through
                return True        # still OPEN, block
            return False           # CLOSED or HALF_OPEN

    def record_success(self) -> None:
        """Call this after a successful RAWG response."""
        with self._lock:
            if self._state != _State.CLOSED:
                logger.info(
                    "RAWG circuit breaker → CLOSED (RAWG is healthy again after %d failures)",
                    self._failures,
                )
            self._state = _State.CLOSED
            self._failures = 0

    def record_failure(self) -> None:
        """Call this after a failed RAWG request."""
        with self._lock:
            self._failures += 1
            if self._state == _State.HALF_OPEN:
                # Probe failed — re-open the circuit and reset the timer
                self._state = _State.OPEN
                self._opened_at = time.monotonic()
                logger.warning(
                    "RAWG circuit breaker → OPEN (probe failed; next retry in %ds)",
                    RECOVERY_TIMEOUT_S,
                )
            elif self._failures >= FAILURE_THRESHOLD:
                self._state = _State.OPEN
                self._opened_at = time.monotonic()
                logger.warning(
                    "RAWG circuit breaker → OPEN after %d consecutive failures "
                    "(next retry in %ds)",
                    self._failures,
                    RECOVERY_TIMEOUT_S,
                )

    # ── Internals ────────────────────────────────────────────────────────────

    def _recovery_timeout_elapsed(self) -> bool:
        return (time.monotonic() - self._opened_at) >= RECOVERY_TIMEOUT_S


# Singleton — import this instance everywhere
rawg_circuit = RawgCircuitBreaker()
