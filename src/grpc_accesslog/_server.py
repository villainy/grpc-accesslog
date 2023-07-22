"""gRPC access log server interceptor."""
from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Callable
from typing import Iterable
from typing import Iterator

import grpc

from . import handlers as _handlers
from ._context import LogContext


if TYPE_CHECKING:
    ServerInterceptor = grpc.ServerInterceptor[grpc.TRequest, grpc.TResponse]
else:
    ServerInterceptor = grpc.ServerInterceptor


def _wrap_rpc_behavior(
    handler: grpc.RpcMethodHandler[grpc.TRequest, grpc.TResponse] | None,
    continuation: Callable[
        [
            Callable[[grpc.TRequest, grpc.ServicerContext], grpc.TResponse],
            bool,
            bool,
        ],
        Callable[[grpc.TRequest, grpc.ServicerContext], grpc.TResponse],
    ],
) -> grpc.RpcMethodHandler[grpc.TRequest, grpc.TResponse] | None:
    """Wrap an RPC call.

    From https://github.com/grpc/grpc/issues/18191#issuecomment-574735994
    """
    if handler is None:
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary  # type: ignore
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream  # type: ignore
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary  # type: ignore
        handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(
        continuation(
            behavior_fn,  # type: ignore
            handler.request_streaming,
            handler.response_streaming,
        ),
        request_deserializer=handler.request_deserializer,
        response_serializer=handler.response_serializer,
    )


class AccessLogInterceptor(ServerInterceptor):
    """Generate a log line for each RPC invocation."""

    def __init__(
        self,
        level: int = logging.INFO,
        name: str = __name__,
        handlers: Iterable[Callable[[LogContext], str]] | None = None,
        separator: str = " ",
        propagate: bool = False,
    ) -> None:
        """Create a logging interceptor.

        Each provided handler will be called in order with a LogContext as
        the single positional argument. The resulting strings are joined
        using the provided separator to form the access log message.

        Args:
            level (int): Log level. Defaults to logging.INFO.
            name (str): Logger name. Defaults to __name__.
            handlers (Iterable[Callable[[LogContext], str]]): LogContext
                handlers collected in order. Defaults to None.
            separator (str): Log message separator. Defaults to " ".
            propagate (bool): Enable propagation to parent loggers. Defaults to False.
        """
        super().__init__()

        self._logger = logging.getLogger(name)
        self._logger.propagate = propagate
        self._logger.addHandler(logging.StreamHandler())

        self._level = level
        self._format = format
        self._handlers = handlers
        self._separator = separator

        if handlers is None:
            self._handlers = [
                _handlers.peer,
                _handlers.time_received(),
                _handlers.request,
                _handlers.status,
                _handlers.response_size,
                _handlers.user_agent,
            ]

    def _write_log(
        self,
        context: grpc.ServicerContext,
        method_name: str,
        request: grpc.TRequest,
        response: grpc.TResponse | None,
        start: datetime,
        end: datetime,
    ) -> None:
        log_context = LogContext(
            context,
            method_name,
            request,
            response,
            start,
            end,
        )

        if self._handlers is None:
            return

        log_args = [handler(log_context) for handler in self._handlers]

        self._logger.log(
            self._level,
            self._separator.join(["%s"] * len(log_args)),
            *log_args,
        )

    # Work around grpc-stubs typing bug. The continuation param and return value
    # are documented as optional but do not allow None in typing stubs.
    def intercept_service(  # type: ignore
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails],
            grpc.RpcMethodHandler[grpc.TRequest, grpc.TResponse] | None,
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler[grpc.TRequest, grpc.TResponse] | None:
        """Intercept an RPC."""

        def logging_wrapper(
            behavior: Callable[[grpc.TRequest, grpc.ServicerContext], grpc.TResponse],
            request_streaming: bool,
            response_streaming: bool,
        ) -> Callable[[grpc.TRequest, grpc.ServicerContext], grpc.TResponse]:
            def logging_interceptor(
                request_or_iterator: grpc.TRequest, context: grpc.ServicerContext
            ) -> grpc.TResponse:
                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(  # type: ignore
                        behavior,  # type: ignore
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )

                start = datetime.now(timezone.utc)
                response = None
                try:
                    response = behavior(request_or_iterator, context)
                    return response
                finally:
                    end = datetime.now(timezone.utc)
                    self._write_log(
                        context,
                        handler_call_details.method,
                        request_or_iterator,
                        response,
                        start,
                        end,
                    )

            return logging_interceptor

        return _wrap_rpc_behavior(continuation(handler_call_details), logging_wrapper)

    def _intercept_server_stream(
        self,
        behavior: Callable[
            [grpc.TRequest, grpc.ServicerContext], Iterator[grpc.TResponse]
        ],
        handler_call_details: grpc.HandlerCallDetails,
        request_or_iterator: grpc.TRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[grpc.TResponse]:
        start = datetime.now(timezone.utc)
        try:
            yield from behavior(request_or_iterator, context)
        finally:
            end = datetime.now(timezone.utc)
            self._write_log(
                context,
                handler_call_details.method,
                request_or_iterator,
                # TODO what to do with streaming responses?
                None,
                start,
                end,
            )
