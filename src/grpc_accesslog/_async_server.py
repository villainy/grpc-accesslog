"""Asynchronous gRPC access log server interceptor."""

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Awaitable
from typing import Callable

import grpc

from ._server import AccessLogger
from ._server import _wrap_rpc_behavior


class AsyncAccessLogInterceptor(grpc.aio.ServerInterceptor, AccessLogger):
    """Generate a log line for each RPC invocation."""

    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """Intercept an RPC."""

        def logging_wrapper(
            behavior: Callable[[Any, grpc.ServicerContext], Any],
            request_streaming: bool,
            response_streaming: bool,
        ) -> Callable[[Any, grpc.ServicerContext], Any]:
            async def logging_interceptor(
                request_or_iterator: Any, context: grpc.ServicerContext
            ) -> Any:
                start = datetime.now(timezone.utc)
                response = None
                try:
                    response = await behavior(request_or_iterator, context)
                    return response
                finally:
                    end = datetime.now(timezone.utc)
                    self.log(
                        context,
                        handler_call_details.method,
                        request_or_iterator,
                        response,
                        start,
                        end,
                    )

            async def logging_interceptor_stream(
                request_or_iterator: Any, context: grpc.ServicerContext
            ) -> Any:
                start = datetime.now(timezone.utc)
                try:
                    async for response in behavior(request_or_iterator, context):
                        yield response
                finally:
                    end = datetime.now(timezone.utc)
                    self.log(
                        context,
                        handler_call_details.method,
                        request_or_iterator,
                        None,
                        start,
                        end,
                    )

            if response_streaming:
                return logging_interceptor_stream

            return logging_interceptor

        next_handler = await continuation(handler_call_details)
        return _wrap_rpc_behavior(next_handler, logging_wrapper)  # type: ignore
