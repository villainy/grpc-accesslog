Usage
=====

Generating access logs
^^^^^^^^^^^^^^^^^^^^^^

Inject an instance of the interceptor when creating a gRPC server:

.. code-block:: python

   from concurrent import futures
   import grpc
   from grpc_accesslog import AccessLogInterceptor

   interceptors = [AccessLogInterceptor()]
   server = grpc.server(
      futures.ThreadPoolExecutor(max_workers=10),
      interceptors=interceptors
   )

Or with an asyncio server:

.. code-block:: python

   from concurrent import futures
   import grpc.aio
   from grpc_accesslog import AsyncAccessLogInterceptor

   interceptors = [AsyncAccessLogInterceptor()]
   server = grpc.aio.server(
      futures.ThreadPoolExecutor(max_workers=10),
      interceptors=interceptors
   )

The server interceptor includes a complete default configuration. By default logs will be generated with the following format::

   [::1] [03/Apr/2021:17:19:41 +0000] /grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo OK 0 grpc-go/1.35.0

* gRPC Peer IP
* Request received timestamp
* Full RPC service and method path
* String representation of gRPC Status Code
* Size (in bytes) of serialized response message
* gRPC user-agent string from invocation metadata (if available)

Configuring log fields
^^^^^^^^^^^^^^^^^^^^^^

The contents of the access log are configuable by providing a tuple of log handlers and a separator string. The output of each handler will be joined in order by the separator.

.. code-block:: python

   from grpc_accesslog import AccessLogInterceptor, handler

   interceptor = AccessLogInterceptor(
      handlers=(
         handler.peer,
         handler.time_received(),
         handler.request,
         handler.status,
         handler.response_size,
         handler.user_agent,
      ),
      separator=" ",
   )

Several handlers are built into the `grpc_accesslog.handler` module.

* peer -- gRPC client IP address
* request -- Full RPC service and method path
* response_size -- Size of serialized gRPC response message, in bytes
* rtt_ms -- Delta of time_received and time_complete, in milliseconds
* status -- String representation of gRPC status code
* time_received(format) -- Timestamp of received request, formatted with `strftime` with `format`
* time_complete(format) -- Timestamp of completed RPC execution, formatted with `strftime` with `format`
* user_agent -- gRPC user agent from invocation metadata

Writing custom handlers
^^^^^^^^^^^^^^^^^^^^^^^

An access log handler is simply a `Callable` that accepts a `grpc_accesslog.LogContext` as its single argument and returns a string. The `LogContext` exposes all information available to the server interceptor:

.. code-block:: python

   class LogContext(NamedTuple):
      """Data available to gRPC log handlers."""

      server_context: grpc.ServicerContext
      method_name: str
      request: Message
      response: Union[Message, Generator]
      start: datetime
      end: datetime

Custom handlers can be written easily and added to the handler list.

.. code-block:: python

   from grpc_accesslog import AccessLogInterceptor, LogContext

   def custom_metadata(log_context: LogContext) -> str:
      for md in log_context.server_context.invocation_metadata():
         if md.key == "my_custom_field":
               return md.value

      return "-"

   interceptor = AccessLogInterceptor(
      handlers=(custom_metadata,),
   )
