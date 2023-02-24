import glob
import json
import os.path
from typing import TypedDict

from ord_betterproto import Reaction
from ord_tree.utils import read_file

_this_dir = os.path.dirname(os.path.abspath(__file__))


# pre saved mtt data
class MttData(TypedDict):
    mtt_dict: dict
    depth: int
    name: str
    n_literals: int
    doc: str


MttDataDict = dict()
for json_file in glob.glob(f"{_this_dir}/json_mtt/*.json"):
    with open(json_file, "r") as f:
        data = MttData(**json.load(f))
        MttDataDict[data['name']] = data

SampleReactionInstance = Reaction().from_json(value=read_file(f"{_this_dir}/ORD_Reaction.json"))
