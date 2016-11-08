# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: data_sources.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='data_sources.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x12\x64\x61ta_sources.proto\"\x1e\n\tCondition\x12\x11\n\tcondition\x18\x01 \x01(\t\"\x19\n\x06Result\x12\x0f\n\x07message\x18\x01 \x01(\t2.\n\x0cQueryService\x12\x1e\n\x05Query\x12\n.Condition\x1a\x07.Result\"\x00\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_CONDITION = _descriptor.Descriptor(
  name='Condition',
  full_name='Condition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='condition', full_name='Condition.condition', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=22,
  serialized_end=52,
)


_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='Result.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=54,
  serialized_end=79,
)

DESCRIPTOR.message_types_by_name['Condition'] = _CONDITION
DESCRIPTOR.message_types_by_name['Result'] = _RESULT

Condition = _reflection.GeneratedProtocolMessageType('Condition', (_message.Message,), dict(
  DESCRIPTOR = _CONDITION,
  __module__ = 'data_sources_pb2'
  # @@protoc_insertion_point(class_scope:Condition)
  ))
_sym_db.RegisterMessage(Condition)

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), dict(
  DESCRIPTOR = _RESULT,
  __module__ = 'data_sources_pb2'
  # @@protoc_insertion_point(class_scope:Result)
  ))
_sym_db.RegisterMessage(Result)


import grpc
from grpc.beta import implementations as beta_implementations
from grpc.beta import interfaces as beta_interfaces
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities


class QueryServiceStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Query = channel.unary_unary(
        '/QueryService/Query',
        request_serializer=Condition.SerializeToString,
        response_deserializer=Result.FromString,
        )


class QueryServiceServicer(object):

  def Query(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_QueryServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Query': grpc.unary_unary_rpc_method_handler(
          servicer.Query,
          request_deserializer=Condition.FromString,
          response_serializer=Result.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'QueryService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class BetaQueryServiceServicer(object):
  """The Beta API is deprecated for 0.15.0 and later.

  It is recommended to use the GA API (classes and functions in this
  file not marked beta) for all further purposes. This class was generated
  only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
  def Query(self, request, context):
    context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


class BetaQueryServiceStub(object):
  """The Beta API is deprecated for 0.15.0 and later.

  It is recommended to use the GA API (classes and functions in this
  file not marked beta) for all further purposes. This class was generated
  only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
  def Query(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
    raise NotImplementedError()
  Query.future = None


def beta_create_QueryService_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
  """The Beta API is deprecated for 0.15.0 and later.

  It is recommended to use the GA API (classes and functions in this
  file not marked beta) for all further purposes. This function was
  generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
  request_deserializers = {
    ('QueryService', 'Query'): Condition.FromString,
  }
  response_serializers = {
    ('QueryService', 'Query'): Result.SerializeToString,
  }
  method_implementations = {
    ('QueryService', 'Query'): face_utilities.unary_unary_inline(servicer.Query),
  }
  server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
  return beta_implementations.server(method_implementations, options=server_options)


def beta_create_QueryService_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
  """The Beta API is deprecated for 0.15.0 and later.

  It is recommended to use the GA API (classes and functions in this
  file not marked beta) for all further purposes. This function was
  generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
  request_serializers = {
    ('QueryService', 'Query'): Condition.SerializeToString,
  }
  response_deserializers = {
    ('QueryService', 'Query'): Result.FromString,
  }
  cardinalities = {
    'Query': cardinality.Cardinality.UNARY_UNARY,
  }
  stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
  return beta_implementations.dynamic_stub(channel, 'QueryService', cardinalities, options=stub_options)
# @@protoc_insertion_point(module_scope)
