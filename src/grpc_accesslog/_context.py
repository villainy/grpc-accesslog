"""gRPC logging context."""

from datetime import datetime
from typing import Any
from typing import NamedTuple

import grpc


class LogContext(NamedTuple):
    """Data available to gRPC log handlers."""

    server_context: grpc.ServicerContext
    method_name: str
    request: Any
    response: Any
    start: datetime
    end: datetime
