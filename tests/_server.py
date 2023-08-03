"""Test servicer implementation."""

from __future__ import annotations

import time
from typing import Iterator

import grpc

from tests.proto.test_service_pb2 import Request
from tests.proto.test_service_pb2 import Response
from tests.proto.test_service_pb2_grpc import TestServiceServicer


class Servicer(TestServiceServicer):
    """Servicer implementation."""

    def UnaryUnary(  # noqa: N802
        self, request: Request, context: grpc.ServicerContext
    ) -> Response:
        """Handle a UnaryUnary request."""
        return Response(data=request.data)

    def UnaryStream(  # noqa: N802
        self, request: Request, context: grpc.ServicerContext
    ) -> Iterator[Response]:
        """Handle a UnaryStream request."""
        for char in request.data:
            yield Response(data=char)
            time.sleep(0.1)

    def StreamUnary(  # noqa: N802
        self, request_iterator: Iterator[Request], context: grpc.ServicerContext
    ) -> Response:
        """Handle a StreamUnary request."""
        return Response(data="".join([request.data for request in request_iterator]))

    def StreamStream(  # noqa: N802
        self, request_iterator: Iterator[Request], context: grpc.ServicerContext
    ) -> Iterator[Response]:
        """Handle a StreamStream request."""
        for request in request_iterator:
            yield Response(data=request.data)
            time.sleep(0.1)
