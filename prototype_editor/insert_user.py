# inserting sample data to mongodb
from pymongo import MongoClient
from loguru import logger
from dash_app_support.db import ENV_MONGO_DB, ENV_MONGO_URI

MONGO_DB = MongoClient(ENV_MONGO_URI)[ENV_MONGO_DB]
COLLECTION = "USER"

user = {
        "username": "qai",
        "full_name": "Qianxiang Ai",
        "email": "qai@mit.edu",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        "disabled": False,
    }

doc_inserted = MONGO_DB[COLLECTION].insert_one(user)
logger.critical(f"inserted: {doc_inserted.inserted_id}")