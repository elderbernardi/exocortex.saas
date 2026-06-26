"""excrtx-source-reclameaqui — coletor de reputação pública no Reclame Aqui."""

from .collector import ReclameAquiCollector
from .schemas import make_envelope, now_utc, slugify_query

__all__ = [
    "ReclameAquiCollector",
    "make_envelope",
    "now_utc",
    "slugify_query",
]
__version__ = "1.0.0"
