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
with open(f"{_this_dir}/sample_prototype.json", "r") as f:
    SamplePrototypeDoc = json.load(f)

if __name__ == '__main__':
    # generate mtt json in `json_mtt`
    from ord_tree.utils import write_file, get_tree_depth
    from ord_tree.ord_classes import OrdMessageClasses, BuiltinLiteralClasses, OrdEnumClasses
    from ord_tree.mtt import get_mtt, mtt_to_dict, import_string
    import json

    for m in OrdMessageClasses:
        mtt = get_mtt(m)
        data = {
            "mtt_dict": mtt_to_dict(mtt),
            "depth": get_tree_depth(mtt),
            "name": m.__name__,
            "doc": m.__doc__,
            "n_literals": len(
                [
                    n for n in mtt.nodes if
                    import_string(mtt.nodes[n]['mtt_class_string']) in BuiltinLiteralClasses + OrdEnumClasses
                ]
            ),
        }
        j = json.dumps(data)
        write_file(j, f"json_mtt/{m.__name__}.json")
