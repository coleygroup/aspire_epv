from ord_betterproto import Data
# from ord_schema.proto.reaction_pb2 import Data

d = Data(float_value=2, integer_value=0, bytes_value=b'', description="sdf")
print(d)
print(d._betterproto.sorted_field_names)

dd = Data()
setattr(dd, 'float_value', 2)
setattr(dd, 'integer_value', 0)
setattr(dd, 'bytes_value', b'')
setattr(dd, 'description', 'lalala')
print(dd)
"""
Data(float_value=2, integer_value=0, bytes_value=b'', description='sdf')
Data(bytes_value=b'', description='lalala')  # ???
#  because it is `oneof` field......
"""

# print(d.to_json(indent=2))
# d_rec = Data().from_json(d.to_json(indent=2))
# print(d_rec)