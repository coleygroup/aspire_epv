from __future__ import annotations

import os
from typing import List

import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Body
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

from api_models import OrdPrototypeModel, UpdateOrdPrototypeModel
from dash_app_support.db import ENV_MONGO_DB, ENV_MONGO_COLLECTION

app = FastAPI(
    title="ORD Prototype API",
    version="0.0.1",
    contact={
        "name": "Qianxiang Ai",
        "email": "qai@mit.edu",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://3.144.235.89",
    "http://3.144.235.89:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
db = client[ENV_MONGO_DB]

from datetime import datetime, timedelta
from typing import Annotated, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ["FASTAPI_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from loguru import logger
import pymongo

auth_client = pymongo.MongoClient(os.environ["MONGO_URI"])
auth_db = auth_client[ENV_MONGO_DB]
fake_users_db = {
    "qai": {k: v for k, v in auth_db["USER"].find_one({"_id": "qai"}).items() if k != "_id"}
}
logger.critical(fake_users_db)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.post("/prototype", response_description="Add new ORD prototype", response_model=OrdPrototypeModel)
async def create_prototype(ord_prototype: OrdPrototypeModel = Body(...)):
    ord_prototype = jsonable_encoder(ord_prototype)  # this makes `_id` to be string which is inconsistent with dash app
    ord_prototype['_id'] = ObjectId(ord_prototype['_id'])
    new = await db[ENV_MONGO_COLLECTION].insert_one(ord_prototype)
    created = await db[ENV_MONGO_COLLECTION].find_one({"_id": str(new.inserted_id)})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@app.get("/users/me/prototype", response_description="List all prototypes", response_model=List[OrdPrototypeModel])
async def list_prototypes(current_user: Annotated[User, Depends(get_current_active_user)]):
    # TODO pagination
    prototypes = [doc async for doc in db[ENV_MONGO_COLLECTION].find()]
    # return {"prototype_list": prototypes, "owner": current_user.username}
    return prototypes


@app.get("/compound", response_description="List all compounds", response_model=List[OrdPrototypeModel])
async def list_compounds():
    prototypes = [doc async for doc in db[ENV_MONGO_COLLECTION].find({'root_message_type': ''})]
    return prototypes


@app.get("/users/me/prototype_ids", response_description="List all prototype ids")
async def list_prototype_ids(current_user: Annotated[User, Depends(get_current_active_user)]):
    # TODO pagination
    prototypes = [str(doc['_id']) async for doc in db[ENV_MONGO_COLLECTION].find()]
    return {"prototype_list": prototypes, "owner": current_user.username}


@app.get("/prototype/{id}", response_description="Get a single prototype", response_model=OrdPrototypeModel)
async def show_prototype(id: str):
    if (pt := await db[ENV_MONGO_COLLECTION].find_one({"_id": ObjectId(id)})) is not None:
        return pt
    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


@app.put("/prototype/{id}", response_description="Update a prototype", response_model=OrdPrototypeModel)
async def update_prototype(id: str, prototype: UpdateOrdPrototypeModel = Body(...)):
    prototype = {k: v for k, v in prototype.dict().items() if v is not None}

    if len(prototype) >= 1:
        update_result = await db[ENV_MONGO_COLLECTION].update_one({"_id": ObjectId(id)}, {"$set": prototype})

        if update_result.modified_count == 1:
            if (
                    updated_student := await db[ENV_MONGO_COLLECTION].find_one({"_id": ObjectId(id)})
            ) is not None:
                return updated_student

    if (existing_prototype := await db[ENV_MONGO_COLLECTION].find_one({"_id": ObjectId(id)})) is not None:
        return existing_prototype

    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


@app.delete("/prototype/{id}", response_description="Delete a prototype")
async def delete_prototype(id: str):
    delete_result = await db[ENV_MONGO_COLLECTION].delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


# mount dash app
# https://github.com/rusnyder/fastapi-plotly-dash/
from dash_app.prototype_editor import create_dashapp
from fastapi.middleware.wsgi import WSGIMiddleware

dash_app = create_dashapp(prefix="/prototype_editor/")
app.mount("/", WSGIMiddleware(dash_app.server))
