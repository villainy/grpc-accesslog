"""Server interceptor tests."""
import logging
import re
from concurrent import futures
from typing import Iterator
from unittest.mock import Mock

import grpc
import pytest
from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor
from grpc_accesslog import handlers
from grpc_accesslog._context import LogContext

from .proto import test_service_pb2
from .proto import test_service_pb2_grpc


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

    interceptor.intercept_service(
        Mock(
            return_value=Mock(
                name="RpcMethodHandler",
                request_streaming=False,
                response_streaming=False,
            )
        ),
        Mock(name="HandlerCallDetails"),
    )

    assert "this that" in caplog.text


def test_intercept_no_handlers(caplog: LogCaptureFixture) -> None:
    """Test interceptor behavior with no handlers does nothing."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=None,
        propagate=True,
    )

    interceptor._handlers = None

    interceptor.intercept(Mock(), Mock(), Mock(), "/abc/Test")

    assert not caplog.text


def test_intercept_unary_stream(caplog: LogCaptureFixture) -> None:
    """Test server-streaming interceptor."""
    caplog.set_level(logging.INFO)

    def _handler(context: LogContext) -> str:
        return context.method_name

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=[
            _handler,
        ],
        propagate=True,
    )

    method = Mock(name="method")

    def _response() -> Iterator[int]:
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


def test_testerson(caplog):
    """Testing the testersons."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor = AccessLogInterceptor(
        name="root",
        handlers=(
            lambda _: "this",
            lambda _: "that",
        ),
        propagate=True,
    )

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=1), interceptors=[interceptor]
    )
    port = server.add_insecure_port("localhost:0")
    servicer = test_service_pb2_grpc.TestServiceServicer()

    test_service_pb2_grpc.add_TestServiceServicer_to_server(servicer, server)

    server.start()

    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = test_service_pb2_grpc.TestServiceStub(channel)
        with pytest.raises(grpc.RpcError, match="UNIMPLEMENTED"):
            stub.UnaryUnary(test_service_pb2.Request())

    server.stop(grace=0)

    assert "this that" in caplog.text
