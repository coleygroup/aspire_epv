# deprecated this, use the modified betterproto to generate dataclasses

## make sure protoc compiler is installed
## on debian do `sudo apt install protobuf-compiler`
## remember to install `pip install "betterproto[compiler]"`
#whereami=$PWD
#
#mkdir -p ord_betterproto/proto
#cd ord_betterproto || exit
#touch __init__.py
#for protoname in reaction dataset
#do
#  wget https://raw.githubusercontent.com/open-reaction-database/ord-schema/main/proto/$protoname.proto
#  if [[ $protoname == dataset ]]
#  then
#    sed -i 's/ord-schema\/proto\/reaction.proto/reaction.proto/' $protoname.proto
#  fi
#done
#
#mkdir -p ord
#
## this requires `protoc-gen-python_betterproto` in you PATH, if you use a venv this should be in `venv/bin`
#protoc -I . --plugin=protoc-gen-custom=/home/qai/local/miniconda3/envs/aspire_epv/lib/python3.10/site-packages/betterproto/plugin/main.py --custom_opt=pydantic_dataclasses --python_betterproto_out=ord dataset.proto --experimental_allow_proto3_optional
#
#mv ord/ord/__init__.py ./
#mv ./*.proto proto
#rm -rf ord
#cd "$whereami" || exit
