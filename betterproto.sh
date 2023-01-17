# make sure protoc compiler is installed
# on debian do `sudo apt install protobuf-compiler`
whereami=$PWD

mkdir -p ord_betterproto/proto
cd ord_betterproto || exit
touch __init__.py
for protoname in reaction dataset
do
  wget https://raw.githubusercontent.com/open-reaction-database/ord-schema/main/ord_schema/proto/$protoname.proto
  if [[ $protoname == dataset ]]
  then
    sed -i 's/ord_schema\/proto\/reaction.proto/reaction.proto/' $protoname.proto
  fi
done

mkdir -p ord
protoc -I . --python_betterproto_out=ord dataset.proto --experimental_allow_proto3_optional
mv ord/ord/__init__.py ./
mv ./*.proto proto
rm -rf ord
cd "$whereami" || exit
