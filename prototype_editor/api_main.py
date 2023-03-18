from typing import List
import os
import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from api_models import OrdPrototypeModel, UpdateOrdPrototypeModel
from fastapi.middleware.cors import CORSMiddleware

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
# client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['ord_prototype']


@app.post("/prototype", response_description="Add new ORD prototype", response_model=OrdPrototypeModel)
async def create_prototype(ord_prototype: OrdPrototypeModel = Body(...)):
    ord_prototype = jsonable_encoder(ord_prototype)  # this makes `_id` to be string which is inconsistent with dash app
    ord_prototype['_id'] = ObjectId(ord_prototype['_id'])
    new = await db["prototypes"].insert_one(ord_prototype)
    created = await db["prototypes"].find_one({"_id": str(new.inserted_id)})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@app.get("/prototype", response_description="List all prototypes", response_model=List[OrdPrototypeModel])
async def list_prototypes():
    # TODO pagination
    prototypes = [doc async for doc in db["prototypes"].find()]
    return prototypes


@app.get("/prototype_ids", response_description="List all prototype ids", response_model=List[str])
async def list_prototypes():
    # TODO pagination
    prototypes = [str(doc['_id']) async for doc in db["prototypes"].find()]
    return prototypes


@app.get("/prototype/{id}", response_description="Get a single prototype", response_model=OrdPrototypeModel)
async def show_prototype(id: str):
    if (pt := await db["prototypes"].find_one({"_id": ObjectId(id)})) is not None:
        return pt
    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


@app.put("/prototype/{id}", response_description="Update a prototype", response_model=OrdPrototypeModel)
async def update_prototype(id: str, prototype: UpdateOrdPrototypeModel = Body(...)):
    prototype = {k: v for k, v in prototype.dict().items() if v is not None}

    if len(prototype) >= 1:
        update_result = await db["prototypes"].update_one({"_id": ObjectId(id)}, {"$set": prototype})

        if update_result.modified_count == 1:
            if (
                    updated_student := await db["prototypes"].find_one({"_id": ObjectId(id)})
            ) is not None:
                return updated_student

    if (existing_prototype := await db["prototypes"].find_one({"_id": ObjectId(id)})) is not None:
        return existing_prototype

    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


@app.delete("/prototype/{id}", response_description="Delete a prototype")
async def delete_prototype(id: str):
    delete_result = await db["prototypes"].delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Prototype {id} not found")


# mount dash app
# https://github.com/rusnyder/fastapi-plotly-dash/
from dash_app.prototype_editor import create_dashapp
from fastapi.middleware.wsgi import WSGIMiddleware

dash_app = create_dashapp(prefix="/prototype_editor/")
app.mount("/", WSGIMiddleware(dash_app.server))
