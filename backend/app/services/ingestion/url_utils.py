import hashlib
from urllib.parse import urlparse, urlunparse


def canonicalize_url(url: str) -> str:
    """Normalize URL for display/storage comparison (strip fragment, lowercase host)."""
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return url.strip()
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.params,
            parsed.query,
            "",
        )
    )


def normalize_url(url: str) -> str:
    """Stable dedup key — fixed-length SHA-256 of canonical URL (fits varchar(128))."""
    canonical = canonicalize_url(url)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
