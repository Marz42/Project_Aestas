from app.services.ingestion.url_utils import normalize_url


def test_normalize_url_strips_fragment_and_lowercases_host() -> None:
    raw = "HTTPS://Example.COM/path?q=1#section"
    assert normalize_url(raw) == "https://example.com/path?q=1"
