# Experiment Planning and Visualization module


## dev dependencies (debian)
Some packages in `requirements.txt` depend on the following:
```shell
# graphviz
sudo apt install -y python3-dev graphviz libgraphviz-dev

# protobuf
sudo apt install -y protobuf-compiler

# pg_config for psycopg2 required by ord_schema
sudo apt install -y libpq-dev
```

## docker compose
```shell
sudo docker compose --env-file ./prototype_editor/.env up  --build --force-recreate
```