"""excrtx-source-cnpj — consulta cadastral pública de CNPJs."""

from .collector import CNPJCollector, Cache
from .schemas import make_envelope, normalize_cnpj, now_utc, parse_br_date, parse_capital_social

__all__ = [
    "CNPJCollector",
    "Cache",
    "make_envelope",
    "normalize_cnpj",
    "now_utc",
    "parse_br_date",
    "parse_capital_social",
]
__version__ = "1.0.0"
