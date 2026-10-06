import pytest

from src.security.url_validation import is_safe_http_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://localhost/internal",
        "file:///etc/passwd",
        "ftp://example.com/x",
        "http://169.254.169.254/latest/meta-data/",
    ],
)
def test_rejects_unsafe_urls(url: str):
    assert is_safe_http_url(url, resolve_dns=False) is False


def test_accepts_public_https():
    assert is_safe_http_url("https://example.com/about", resolve_dns=False) is True
