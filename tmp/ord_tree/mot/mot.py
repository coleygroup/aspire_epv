import pprint

from ord_betterproto import Reaction
# from ord_tree.tree_obj import message_object_to_message_object_tree, message_object_tree_to_message_object
from ord_tree.mot import get_mot, message_from_mot, mot_from_dict, mot_to_dict
from ord_tree.utils import write_dot, read_file

if __name__ == '__main__':
    # write tree of a reaction from ord examples
    # https://github.com/open-reaction-database/ord-schema/blob/main/examples/submissions/3_Liu_Copper_OrgSyn/example_liu.ipynb
    json_string = read_file("../../ord_betterproto/reaction_ord.json")
    r = Reaction().from_json(json_string)
    tree = get_mot(r)
    write_dot(tree, "tree_liu.dot")

    r_rec = message_from_mot(tree)
    with open("tree_liu_rec.json", "w") as f:
        f.write(r_rec.to_json(indent=2))
    tree_rec = get_mot(r_rec)
    write_dot(tree_rec, "tree_liu_rec.dot")

    import json
    json.dumps(mot_to_dict(tree_rec))
    d = mot_to_dict(tree)
    tree_rec_rec = mot_from_dict(d)

