import glob
import json
# inserting sample data to mongodb
from loguru import logger
from pymongo import MongoClient

from dash_app_support.db import ENV_MONGO_DB, ENV_MONGO_COLLECTION, ENV_MONGO_URI


MONGO_DB = MongoClient(ENV_MONGO_URI)[ENV_MONGO_DB]
COLLECTION = ENV_MONGO_COLLECTION

for jf in glob.glob("samples/sample_prototype_*.json"):
    with open(jf, "r") as f:
        doc = json.load(f)
        doc_inserted = MONGO_DB[COLLECTION].insert_one(doc)
        logger.critical(f"inserted: {doc_inserted.inserted_id}")

