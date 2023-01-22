from ord_betterproto import Reaction
from ord_betterproto.message_object_tree import message_object_to_message_object_tree, \
    message_object_tree_to_message_object
from ord_betterproto.utils import write_dot

if __name__ == '__main__':
    # write tree of a reaction from ord examples
    # https://github.com/open-reaction-database/ord-schema/blob/main/examples/submissions/3_Liu_Copper_OrgSyn/example_liu.ipynb
    with open("../ord_betterproto/reaction_ord.json", "r") as f:
        json_string = f.read()
    r = Reaction().from_json(json_string)
    tree = message_object_to_message_object_tree(r)
    write_dot(tree, "tree_liu.dot")

    r_rec = message_object_tree_to_message_object(tree)
    with open("tree_liu_rec.json", "w") as f:
        f.write(r_rec.to_json(indent=2))
    tree_rec = message_object_to_message_object_tree(r_rec)
    write_dot(tree_rec, "tree_liu_rec.dot")
