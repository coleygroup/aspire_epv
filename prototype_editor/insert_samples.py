# inserting sample data to mongodb
from loguru import logger
from pymongo import MongoClient

from dash_app_support.fixtures import SamplePrototypeDoc, SampleReactionInstance
from dash_app_support.db import ENV_MONGO_DB, ENV_MONGO_COLLECTION, ENV_MONGO_URI
from ord_tree.mot import get_mot, pt_to_dict

MONGO_DB = MongoClient(ENV_MONGO_URI)[ENV_MONGO_DB]
COLLECTION = ENV_MONGO_COLLECTION

doc0 = MONGO_DB[COLLECTION].insert_one(SamplePrototypeDoc)
logger.critical(f"inserted: {doc0.inserted_id}")

doc1 = {
    "name": "SAMPLE_REACTION",
    "version": "SAMPLE_REACTION",
    "node_link_data": pt_to_dict(get_mot(SampleReactionInstance)),
}  # some fields are intentionally left out
doc1 = MONGO_DB[COLLECTION].insert_one(doc1)
logger.critical(f"inserted: {doc1.inserted_id}")
