"""Server interceptor tests."""
import logging
from unittest.mock import Mock

from grpc_accesslog import AccessLogInterceptor


def test_default_handlers():
    """Ensure default handlers are added."""
    interceptor = AccessLogInterceptor()

    assert len(interceptor._handlers) > 0


def test_intercept(caplog):
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=(
            lambda _: "this",
            lambda _: "that",
        ),
        propagate=True,
    )

    interceptor.intercept(Mock(), Mock(), Mock(), "/abc/Test")

    assert "this that" in caplog.text
