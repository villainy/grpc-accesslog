"""Test RPC logging handlers."""

from datetime import datetime
from datetime import timezone
from unittest.mock import Mock

import grpc
import pytest

from grpc_accesslog import LogContext
from grpc_accesslog import handlers


@pytest.fixture
def servicer_context() -> Mock:
    """Mock gRPC servicer context."""
    context = Mock(
        grpc.ServicerContext,
        name="ServicerContext",
        peer=Mock(return_value="ipv4:192.168.0.1:58111"),
        _state=Mock(
            code=grpc.StatusCode.NOT_FOUND,
        ),
    )

    return context


@pytest.fixture
def log_context(servicer_context: Mock) -> LogContext:
    """Mock LogContext."""
    context = LogContext(
        servicer_context,
        "/abc.test/GetTest",
        Mock(name="Request"),
        Mock(name="Response", ByteSize=Mock(return_value=10)),
        datetime(2021, 4, 3, 0, 0, 0, 0, timezone.utc),
        datetime(2021, 4, 3, 0, 1, 0, 0, timezone.utc),
    )

    return context


@pytest.mark.parametrize(
    ("format", "expected"),
    [
        pytest.param("[%d/%b/%Y:%H:%M:%S %z]", "[03/Apr/2021:00:00:00 +0000]"),
        pytest.param("%Y%m%d%H%M%S", "20210403000000"),
    ],
)
def test_time_received(format: str, expected: str, log_context: LogContext) -> None:
    """Test parsing received time."""
    result = handlers.time_received(format)(log_context)

    assert result == expected


@pytest.mark.parametrize(
    ("format", "expected"),
    [
        pytest.param("[%d/%b/%Y:%H:%M:%S %z]", "[03/Apr/2021:00:01:00 +0000]"),
        pytest.param("%Y%m%d%H%M%S", "20210403000100"),
    ],
)
def test_time_complete(format: str, expected: str, log_context: LogContext) -> None:
    """Test parsing received time."""
    result = handlers.time_complete(format)(log_context)

    assert result == expected


def test_rtt_ms(log_context: LogContext) -> None:
    """Test parsing received time."""
    result = handlers.rtt_ms(log_context)

    assert result == "60000"


def test_request(log_context: LogContext) -> None:
    """Test returning RPC name."""
    assert handlers.request(log_context) == log_context.method_name


def test_status(log_context: LogContext) -> None:
    """Test returning gRPC status code."""
    assert handlers.status(log_context) == grpc.StatusCode.NOT_FOUND.name


def test_peer(log_context: LogContext) -> None:
    """Test returning peer IP address."""
    assert handlers.peer(log_context) == "192.168.0.1"


def test_response_size(log_context: LogContext) -> None:
    """Test returning gRPC response byte size."""
    assert handlers.response_size(log_context) == "10"


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        pytest.param(Mock(key="user-agent", value="test"), "test"),
        pytest.param(Mock(), "-"),
    ],
)
def test_user_agent(metadata: Mock, expected: str, log_context: LogContext) -> None:
    """Test parsing and returning gRPC user agent from metadata."""
    mock_metadata = Mock(return_value=(metadata,))

    log_context.server_context.invocation_metadata = mock_metadata  # type: ignore
    assert handlers.user_agent(log_context) == expected
