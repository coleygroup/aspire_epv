export PYTHONPATH="$(pwd):$PYTHONPATH"
export PYTHONPATH="$(pwd)/../:$PYTHONPATH"
export MONGO_DB="ord_prototype"
export MONGO_COLLECTION="prototypes"
export MONGO_URI="mongodb://0.0.0.0:27017/?retryWrites=true&w=majority"
#uvicorn api_main:app --workers 4
uvicorn api_main:app --reload
