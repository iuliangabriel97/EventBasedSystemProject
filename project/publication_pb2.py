# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: publication.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='publication.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x11publication.proto\"o\n\x0bPublication\x12\x11\n\tcar_model\x18\x01 \x02(\t\x12\x17\n\x0fproduction_date\x18\x02 \x02(\t\x12\x12\n\nhorsepower\x18\x03 \x02(\x05\x12\r\n\x05\x63olor\x18\x04 \x02(\t\x12\x11\n\tmax_speed\x18\x05 \x02(\x05'
)




_PUBLICATION = _descriptor.Descriptor(
  name='Publication',
  full_name='Publication',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='car_model', full_name='Publication.car_model', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='production_date', full_name='Publication.production_date', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='horsepower', full_name='Publication.horsepower', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='color', full_name='Publication.color', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='max_speed', full_name='Publication.max_speed', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=132,
)

DESCRIPTOR.message_types_by_name['Publication'] = _PUBLICATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Publication = _reflection.GeneratedProtocolMessageType('Publication', (_message.Message,), {
  'DESCRIPTOR' : _PUBLICATION,
  '__module__' : 'publication_pb2'
  # @@protoc_insertion_point(class_scope:Publication)
  })
_sym_db.RegisterMessage(Publication)


# @@protoc_insertion_point(module_scope)
