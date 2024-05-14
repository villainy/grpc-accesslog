"""Server interceptor tests."""

import logging
from concurrent import futures
from unittest import mock

import grpc
import pytest
from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor

from ._server import Servicer
from .proto import test_service_pb2
from .proto import test_service_pb2_grpc


@pytest.fixture
def interceptor():
    """Provide a configured interceptor."""
    interceptor = AccessLogInterceptor(
        name="root",
        propagate=True,
    )

    return interceptor


@pytest.fixture
def client_stub(interceptor):
    """Provide a connected gRPC client stub."""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=1), interceptors=[interceptor]
    )
    port = server.add_insecure_port("localhost:0")
    servicer = Servicer()

    test_service_pb2_grpc.add_TestServiceServicer_to_server(servicer, server)

    server.start()

    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = test_service_pb2_grpc.TestServiceStub(channel)
        yield stub

    server.stop(grace=0)


def test_default_handlers() -> None:
    """Ensure default handlers are added."""
    interceptor: AccessLogInterceptor = AccessLogInterceptor()

    assert interceptor._handlers is not None
    assert len(list(interceptor._handlers)) > 0


def test_intercept_unaryunary(
    caplog: LogCaptureFixture,
    interceptor: AccessLogInterceptor,
    client_stub: test_service_pb2_grpc.TestServiceStub,
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor._handlers = (lambda _: "this", lambda _: "that")

    client_stub.UnaryUnary(test_service_pb2.Request(data="data"))

    assert "this that" in caplog.text


def test_intercept_unarystream(
    caplog: LogCaptureFixture,
    interceptor: AccessLogInterceptor,
    client_stub: test_service_pb2_grpc.TestServiceStub,
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor._handlers = (lambda _: "this", lambda _: "that")

    response = client_stub.UnaryStream(test_service_pb2.Request(data="data"))
    for _ in range(0, 4):
        assert "this that" not in caplog.text
        next(response)

    with pytest.raises(StopIteration):
        next(response)

    assert "this that" in caplog.text


def test_intercept_streamunary(
    caplog: LogCaptureFixture,
    interceptor: AccessLogInterceptor,
    client_stub: test_service_pb2_grpc.TestServiceStub,
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor._handlers = (lambda _: "this", lambda _: "that")

    client_stub.StreamUnary(
        iter(
            (
                test_service_pb2.Request(data="data"),
                test_service_pb2.Request(data="data"),
                test_service_pb2.Request(data="data"),
            )
        )
    )

    assert "this that" in caplog.text


def test_intercept_streamstream(
    caplog: LogCaptureFixture,
    interceptor: AccessLogInterceptor,
    client_stub: test_service_pb2_grpc.TestServiceStub,
):
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor._handlers = (lambda _: "this", lambda _: "that")

    response = client_stub.StreamStream(
        iter(
            (
                test_service_pb2.Request(data="data"),
                test_service_pb2.Request(data="data"),
                test_service_pb2.Request(data="data"),
                test_service_pb2.Request(data="data"),
            )
        )
    )
    for _ in range(0, 4):
        assert "this that" not in caplog.text
        next(response)

    with pytest.raises(StopIteration):
        next(response)

    assert "this that" in caplog.text


def test_intercept_no_handlers(
    caplog: LogCaptureFixture,
    interceptor: AccessLogInterceptor,
    client_stub: test_service_pb2_grpc.TestServiceStub,
) -> None:
    """Test interceptor behavior with no handlers does nothing."""
    caplog.set_level(logging.INFO, logger="root")

    interceptor._handlers = None

    client_stub.UnaryUnary(test_service_pb2.Request(data="data"))

    assert not caplog.text


def test_custom_logger(caplog: LogCaptureFixture) -> None:
    """Test setting custom logger."""
    logger = mock.Mock()

    interceptor = AccessLogInterceptor(logger=logger)

    assert interceptor._logger == logger
