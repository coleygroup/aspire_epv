# convert proto to json schema
# make use of `jsonschema_opt` from https://github.com/chrusty/protoc-gen-jsonschema
mkdir jschema
protoc \
--jsonschema_out=jschema \
--proto_path=proto ../ord_betterproto/proto/dataset.proto \
--experimental_allow_proto3_optional \
--jsonschema_opt=enforce_oneof \
--jsonschema_opt=prefix_schema_files_with_package \
--jsonschema_opt=proto_and_json_fieldnames \
--jsonschema_opt=enums_as_strings_only

