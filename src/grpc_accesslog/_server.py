"""gRPC access log server interceptor."""

import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

import grpc

from ._context import LogContext
from .handlers import DEFAULT_HANDLERS
from .handlers import THandler


TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


def _wrap_rpc_behavior(
    handler: Union[grpc.RpcMethodHandler, None],
    continuation: Callable[
        [
            Callable[[TRequest, grpc.ServicerContext], TResponse],
            bool,
            bool,
        ],
        Callable[[TRequest, grpc.ServicerContext], TResponse],
    ],
) -> Union[grpc.RpcMethodHandler, None]:
    """Wrap an RPC call.

    From https://github.com/grpc/grpc/issues/18191#issuecomment-574735994
    """
    if handler is None:
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary
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


class AccessLogger:
    """Access log writer."""

    def __init__(
        self,
        level: int = logging.INFO,
        name: str = __name__,
        handlers: List[THandler] = DEFAULT_HANDLERS,
        separator: str = " ",
        propagate: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Create an access logging writer.

        Each provided handler will be called in order with a LogContext as
        the single positional argument. The resulting strings are joined
        using the provided separator to form the access log message.

        Args:
            level (int): Log level. Defaults to logging.INFO.
            name (str): Logger name. Defaults to __name__.
            handlers (List[THandler]): LogContext
                handlers collected in order. Defaults to None.
            separator (str): Log message separator. Defaults to " ".
            propagate (bool): Enable propagation to parent loggers. Defaults to False.
            logger (logging.Logger): The logger instance to use for access
                logs. Optional, defaults to None.
        """
        if logger is None:
            self._logger = logging.getLogger(name)
            self._logger.propagate = propagate
            self._logger.addHandler(logging.StreamHandler())
        else:
            self._logger = logger

        self._level = level
        self._handlers = handlers
        self._separator = separator

    def log(
        self,
        context: grpc.ServicerContext,
        method_name: str,
        request: Any,
        response: Optional[Any],
        start: datetime,
        end: datetime,
    ) -> None:
        """Write a log line to stdout."""
        log_context = LogContext(
            context,
            method_name,
            request,
            response,
            start,
            end,
        )

        if not self._handlers:
            return

        log_args = [handler(log_context) for handler in self._handlers]

        self._logger.log(
            self._level,
            self._separator.join(["%s"] * len(log_args)),
            *log_args,
        )


class AccessLogInterceptor(grpc.ServerInterceptor, AccessLogger):
    """Generate a log line for each RPC invocation."""

    def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails],
            Union[grpc.RpcMethodHandler, None],
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Union[grpc.RpcMethodHandler, None]:
        """Intercept an RPC."""

        def logging_wrapper(
            behavior: Callable[[Any, grpc.ServicerContext], Any],
            request_streaming: bool,
            response_streaming: bool,
        ) -> Callable[[Any, grpc.ServicerContext], Any]:
            def logging_interceptor(
                request_or_iterator: Any, context: grpc.ServicerContext
            ) -> Any:
                start = datetime.now(timezone.utc)
                response = None
                try:
                    response = behavior(request_or_iterator, context)
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

            def logging_interceptor_stream(
                request_or_iterator: Any, context: grpc.ServicerContext
            ) -> Any:
                start = datetime.now(timezone.utc)
                try:
                    yield from behavior(request_or_iterator, context)
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

        return _wrap_rpc_behavior(continuation(handler_call_details), logging_wrapper)
