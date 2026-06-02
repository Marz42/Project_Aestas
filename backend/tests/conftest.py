import pytest

from app.core.database import check_sync_db


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: tests that require Postgres and external network",
    )


@pytest.fixture(scope="session")
def postgres_available() -> bool:
    try:
        check_sync_db()
        return True
    except Exception:
        return False
