import glob
import json
import os.path
from typing import TypedDict

_this_dir = os.path.dirname(os.path.abspath(__file__))


# pre saved mtt data
class MttData(TypedDict):
    mtt_dict: dict
    depth: int
    name: str
    n_literals: int
    doc: str


MttDataDict = dict()
for json_file in glob.glob(f"{_this_dir}/../json_mtt/*.json"):
    with open(json_file, "r") as f:
        data = MttData(**json.load(f))
        MttDataDict[data['name']] = data
