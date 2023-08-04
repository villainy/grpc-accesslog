"""gRPC access log handlers."""

from datetime import timedelta
from typing import Callable
from typing import List

import grpc

from ._context import LogContext


THandler = Callable[[LogContext], str]


def time_received(
    format: str = "[%d/%b/%Y:%H:%M:%S %z]",
) -> THandler:
    """Parse RPC request received time into a strftime formatted string.

    Args:
        format (str): String format. Defaults to "[%d/%b/%Y:%H:%M:%S %z]".

    Returns:
        THandler: LogContext handler
    """

    def inner(context: LogContext) -> str:
        return context.start.strftime(format)

    return inner


def time_complete(
    format: str = "[%d/%b/%Y:%H:%M:%S %z]",
) -> THandler:
    """Parse RPC request completion time into a strftime formatted string.

    Args:
        format (str): String format. Defaults to "[%d/%b/%Y:%H:%M:%S %z]".

    Returns:
        THandler: LogContext handler
    """

    def inner(context: LogContext) -> str:
        return context.end.strftime(format)

    return inner


def rtt_ms(context: LogContext) -> str:
    """Return RPC round trip time in milliseconds.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: Round trip time in milliseconds
    """
    rtt = round((context.end - context.start) / timedelta(microseconds=1) / 1000)
    return str(rtt)


def request(context: LogContext) -> str:
    """Return fully qualified RPC name.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: RPC package and method
    """
    return context.method_name


def status(context: LogContext) -> str:
    """Return gRPC status code from server call.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: gRPC status code name
    """
    code = grpc.StatusCode.OK.name
    # TODO gRPC status code is not exposed publicly anywhere in the server
    # interceptor's context
    if getattr(context.server_context, "_state", None):
        if context.server_context._state.code:  # type: ignore
            code = context.server_context._state.code.name  # type: ignore

    return str(code)


def peer(context: LogContext) -> str:
    """Return parsed client IP when available.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: Client IP address
    """
    peer: str = context.server_context.peer()
    if peer.startswith("ipv"):
        _, _, peer = peer.partition(":")
        peer, _, _ = peer.rpartition(":")

    return peer


def response_size(context: LogContext) -> str:
    """Return expected size of serialized response protobuf in bytes.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: String representation of response size in bytes
    """
    size = 0
    # TODO This only handles unary responses. Streaming generator responses
    # will not be calculated.
    if hasattr(context.response, "ByteSize"):
        size = context.response.ByteSize()

    return f"{size}"


def user_agent(context: LogContext) -> str:
    """Return reported gRPC client user agent if available.

    Args:
        context (LogContext): RPC context data

    Returns:
        str: User agent string
    """
    for metadata in context.server_context.invocation_metadata():
        if getattr(metadata, "key", "").lower() == "user-agent":
            return str(getattr(metadata, "value", "-"))

    return "-"


DEFAULT_HANDLERS: List[THandler] = [
    peer,
    time_received(),
    request,
    status,
    response_size,
    user_agent,
]
