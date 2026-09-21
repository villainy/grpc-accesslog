"""gRPC logging context."""

from datetime import datetime
from typing import Any
from typing import NamedTuple

import grpc


class _ServicerContext:  # pragma: no cover
    """Minimal context shadowing upstream."""

    def __init__(self, context: grpc.ServicerContext):
        """Construct a shadow context."""
        self._invocation_metadata = context.invocation_metadata()
        self._peer = context.peer()
        self._peer_identities = context.peer_identities()
        self._peer_identity_key = context.peer_identity_key()
        self._auth_context = context.auth_context()
        self._trailing_metadata = context.trailing_metadata()
        self._code = context.code()
        self._details = context.details()

    def invocation_metadata(self):
        """Accesses the metadata sent by the client."""
        return self._invocation_metadata

    def peer(self):
        """Identifies the peer that invoked the RPC being serviced."""
        return self._peer

    def peer_identities(self):
        """Gets one or more peer identity(s)."""
        return self._peer_identities

    def peer_identity_key(self):
        """The auth property used to identify the peer."""
        return self._peer_identity_key

    def auth_context(self):
        """Gets the auth context for the call."""
        return self._auth_context

    def trailing_metadata(self):
        """Access value to be used as trailing metadata upon RPC completion."""
        return self._trailing_metadata

    def code(self):
        """Accesses the value to be used as status code upon RPC completion."""
        return self._code

    def details(self):
        """Accesses the value to be used as detail string upon RPC completion."""
        return self._details


class LogContext(NamedTuple):
    """Data available to gRPC log handlers."""

    server_context: _ServicerContext
    method_name: str
    request: Any
    response: Any
    start: datetime
    end: datetime
