from app.services.ingestion.url_utils import canonicalize_url, normalize_url

LONG_TWZ = (
    "https://www.twz.com/news-features/cost-to-link-lucas-kamikaze-drones-to-starlink-"
    "highlights-pentagons-ever-growing-dependence-on-spacex"
)


def test_canonicalize_url_strips_fragment_and_lowercases_host() -> None:
    raw = "HTTPS://Example.COM/path?q=1#section"
    assert canonicalize_url(raw) == "https://example.com/path?q=1"


def test_normalize_url_same_for_equivalent_urls() -> None:
    a = normalize_url("HTTPS://Example.COM/path?q=1#section")
    b = normalize_url("https://example.com/path?q=1")
    assert a == b


def test_normalize_url_fits_dedup_key_column() -> None:
    key = normalize_url(LONG_TWZ)
    assert len(key) == 64
    assert len(key) <= 128


def test_normalize_url_stable_across_calls() -> None:
    assert normalize_url(LONG_TWZ) == normalize_url(LONG_TWZ)
