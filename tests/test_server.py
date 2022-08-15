"""Server interceptor tests."""
import logging
import re
from unittest.mock import Mock

from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor
from grpc_accesslog import handlers


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


def test_rtt_handler_succeeds(caplog: LogCaptureFixture) -> None:
    """Test RTT handler should not raise errors through interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=(
            lambda _: "this",
            handlers.rtt_ms,
        ),
        propagate=True,
    )

    interceptor.intercept(Mock(), Mock(), Mock(), "/abc/Test")

    assert re.match(r"^.*this \d+", caplog.text)
