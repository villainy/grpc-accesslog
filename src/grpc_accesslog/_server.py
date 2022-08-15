"""gRPC access log server interceptor."""
import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional

import grpc
from grpc_interceptor import ServerInterceptor

from . import handlers as _handlers
from ._context import LogContext


class AccessLogInterceptor(ServerInterceptor):
    """Generates a log line for each RPC invocation."""

    def __init__(
        self,
        level: int = logging.INFO,
        name: str = __name__,
        handlers: Optional[Iterable[Callable[[LogContext], str]]] = None,
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
            self._handlers = (
                _handlers.peer,
                _handlers.time_received(),
                _handlers.request,
                _handlers.status,
                _handlers.response_size,
                _handlers.user_agent,
            )

    def intercept(
        self,
        method: Callable[[Any, grpc.ServicerContext], Any],
        request: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        """Intercept a gRPC server call.

        Args:
            method (Callable): RPC implementation or next interceptor
            request (Any): RPC request protobuf or generator
            context (grpc.ServicerContext): gRPC servicer context
            method_name (str): A string of the form "/protobuf.package.Service/Method"

        Returns:
            Any: RPC response or generator
        """
        start = datetime.now(timezone.utc)
        response = method(request, context)
        end = datetime.now(timezone.utc)

        log_context = LogContext(
            context,
            method_name,
            request,
            response,
            start,
            end,
        )

        log_args = []
        if self._handlers is not None:
            log_args = [handler(log_context) for handler in self._handlers]

        self._logger.log(
            self._level,
            self._separator.join(["%s"] * len(log_args)),
            *log_args,
        )

        return response
