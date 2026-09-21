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


class ServicerContext(grpc.ServicerContext):
    """A context object passed to method implementations."""

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

    def set_compression(self, compression):
        """Set the compression algorithm to be used for the entire call."""
        raise NotImplementedError()

    def send_initial_metadata(self, initial_metadata):
        """Sends the initial metadata value to the client."""
        raise NotImplementedError()

    def set_trailing_metadata(self, trailing_metadata):
        """Sets the trailing metadata for the RPC."""
        raise NotImplementedError()

    def trailing_metadata(self):
        """Access value to be used as trailing metadata upon RPC completion."""
        return self._trailing_metadata

    def abort(self, code, details):
        """Raises an exception to terminate the RPC with a non-OK status."""
        raise NotImplementedError()

    def abort_with_status(self, status):
        """Raises an exception to terminate the RPC with a non-OK status."""
        raise NotImplementedError()

    def set_code(self, code):
        """Sets the value to be used as status code upon RPC completion."""
        raise NotImplementedError()

    def set_details(self, details):
        """Sets the value to be used as detail string upon RPC completion."""
        raise NotImplementedError()

    def code(self):
        """Accesses the value to be used as status code upon RPC completion."""
        return self._code

    def details(self):
        """Accesses the value to be used as detail string upon RPC completion."""
        return self._details

    def disable_next_message_compression(self):
        """Disables compression for the next response message."""
        raise NotImplementedError()
