"""Server interceptor tests."""
import logging
from unittest.mock import Mock

from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor


def test_default_handlers() -> None:
    """Ensure default handlers are added."""
    interceptor = AccessLogInterceptor()

    assert interceptor._handlers is not None
    assert len(list(interceptor._handlers)) > 0


def test_intercept(caplog: LogCaptureFixture) -> None:
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
