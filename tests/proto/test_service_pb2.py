# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tests/proto/test_service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder


# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1etests/proto/test_service.proto"\x17\n\x07Request\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t"\x18\n\x08Response\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t2\xa5\x01\n\x0bTestService\x12!\n\nUnaryUnary\x12\x08.Request\x1a\t.Response\x12$\n\x0bUnaryStream\x12\x08.Request\x1a\t.Response0\x01\x12$\n\x0bStreamUnary\x12\x08.Request\x1a\t.Response(\x01\x12\'\n\x0cStreamStream\x12\x08.Request\x1a\t.Response(\x01\x30\x01\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "tests.proto.test_service_pb2", _globals
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_REQUEST"]._serialized_start = 34
    _globals["_REQUEST"]._serialized_end = 57
    _globals["_RESPONSE"]._serialized_start = 59
    _globals["_RESPONSE"]._serialized_end = 83
    _globals["_TESTSERVICE"]._serialized_start = 86
    _globals["_TESTSERVICE"]._serialized_end = 251
# @@protoc_insertion_point(module_scope)
