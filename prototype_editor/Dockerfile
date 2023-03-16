FROM python:3.10-slim AS base
RUN apt-get update \
    && apt-get upgrade -y \
    && apt install -y build-essential \
    && apt install -y graphviz libgraphviz-dev \
    && apt install -y protobuf-compiler \
    && apt install -y libpq-dev \
    && apt-get autoremove -y

WORKDIR /home/code
COPY ord_betterproto/ ./ord_betterproto/
COPY ord_tree/ ./ord_tree/
COPY requirements.txt ./requirements.txt
COPY prototype_editor/ ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt