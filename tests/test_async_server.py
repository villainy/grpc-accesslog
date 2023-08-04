"""Async server interceptor tests."""

import contextlib
import logging
from concurrent import futures
from typing import AsyncContextManager
from typing import Callable

import grpc
import pytest
from pytest import LogCaptureFixture

from grpc_accesslog import AccessLogInterceptor
from grpc_accesslog import AsyncAccessLogInterceptor

from ._server import AsyncServicer
from .proto import test_service_pb2
from .proto import test_service_pb2_grpc


@pytest.fixture
def aio_interceptor():
    """Provide a configured interceptor."""
    interceptor = AsyncAccessLogInterceptor(
        name="root",
        propagate=True,
    )

    return interceptor


@pytest.fixture
def aio_client_stub(aio_interceptor):
    """Provide a connected gRPC client stub."""

    @contextlib.asynccontextmanager
    async def inner():
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=1), interceptors=[aio_interceptor]
        )
        port = server.add_insecure_port("localhost:0")
        servicer = AsyncServicer()

        test_service_pb2_grpc.add_TestServiceServicer_to_server(servicer, server)

        await server.start()

        async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
            stub = test_service_pb2_grpc.TestServiceStub(channel)
            yield stub

        await server.stop(grace=0)

    return inner


@pytest.mark.asyncio
async def test_aio_intercept_unaryunary(
    caplog: LogCaptureFixture,
    aio_interceptor: AsyncAccessLogInterceptor,
    aio_client_stub: Callable[
        [], AsyncContextManager[test_service_pb2_grpc.TestServiceStub]
    ],
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    aio_interceptor._handlers = (lambda _: "this", lambda _: "that")  # type: ignore

    async with aio_client_stub() as stub:
        await stub.UnaryUnary(test_service_pb2.Request(data="data"))

        assert "this that" in caplog.text


@pytest.mark.asyncio
async def test_aio_intercept_unarystream(
    caplog: LogCaptureFixture,
    aio_interceptor: AccessLogInterceptor,
    aio_client_stub: Callable[
        [], AsyncContextManager[test_service_pb2_grpc.TestServiceStub]
    ],
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    aio_interceptor._handlers = (lambda _: "this", lambda _: "that")  # type: ignore

    async with aio_client_stub() as stub:
        async for _ in stub.UnaryStream(test_service_pb2.Request(data="data")):
            ...

        assert caplog.text.count("this that") == 1


@pytest.mark.asyncio
async def test_aio_intercept_streamunary(
    caplog: LogCaptureFixture,
    aio_interceptor: AccessLogInterceptor,
    aio_client_stub: Callable[
        [], AsyncContextManager[test_service_pb2_grpc.TestServiceStub]
    ],
) -> None:
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    aio_interceptor._handlers = (lambda _: "this", lambda _: "that")  # type: ignore

    async with aio_client_stub() as stub:
        await stub.StreamUnary(
            iter(
                (
                    test_service_pb2.Request(data="data"),
                    test_service_pb2.Request(data="data"),
                    test_service_pb2.Request(data="data"),
                )
            )
        )

        assert "this that" in caplog.text


@pytest.mark.asyncio
async def test_aio_intercept_streamstream(
    caplog: LogCaptureFixture,
    aio_interceptor: AccessLogInterceptor,
    aio_client_stub: Callable[
        [], AsyncContextManager[test_service_pb2_grpc.TestServiceStub]
    ],
):
    """Test interceptor."""
    caplog.set_level(logging.INFO, logger="root")

    aio_interceptor._handlers = (lambda _: "this", lambda _: "that")  # type: ignore

    async with aio_client_stub() as stub:
        async for _ in stub.StreamStream(
            iter(
                (
                    test_service_pb2.Request(data="data"),
                    test_service_pb2.Request(data="data"),
                    test_service_pb2.Request(data="data"),
                    test_service_pb2.Request(data="data"),
                )
            )
        ):
            ...

        assert caplog.text.count("this that") == 1
