"""excrtx-source-google-trends — consulta Google Trends via endpoints públicos."""

from __future__ import annotations

from .collector import GoogleTrendsCollector
from .schemas import (
    decode_period,
    empty_data,
    make_envelope,
    make_error,
    normalize_term,
    today_utc,
)

__all__ = [
    "GoogleTrendsCollector",
    "decode_period",
    "empty_data",
    "make_envelope",
    "make_error",
    "normalize_term",
    "today_utc",
]
__version__ = "1.0.0"
