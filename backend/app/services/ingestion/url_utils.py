from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Stable dedup key from article URL (strip fragment, lowercase host)."""
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
