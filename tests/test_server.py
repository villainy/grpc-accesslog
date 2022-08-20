"""Server interceptor tests."""
import logging
import re
from unittest.mock import Mock

from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor
from grpc_accesslog import handlers
from grpc_accesslog._context import LogContext


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


def test_intercept_unary_stream(caplog: LogCaptureFixture) -> None:
    """Test server-streaming interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    def _handler(context: LogContext):
        return context.method_name

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=[
            _handler,
        ],
        propagate=True,
    )

    method = Mock(name="method")

    def _response():
        logging.info("test1")
        yield 0
        logging.info("test2")
        yield 1

    method.return_value = _response()

    request = Mock(name="request")
    context = Mock(name="context")

    for _ in interceptor.intercept(method, request, context, "method_name"):
        pass

    assert re.match(
        r"^.*test1.*test2.*method_name.*", caplog.text, re.MULTILINE | re.DOTALL
    )


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
