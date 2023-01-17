from aspire_api.utils import write_dot
from ord_betterproto import Reaction, Compound
from ord_betterproto.ord_tree import message_to_tree, message_type_to_tree

if __name__ == '__main__':
    # write tree of a Message type in dot format
    for mt in (Compound, Reaction):
        tree = message_type_to_tree(mt)
        write_dot(tree, "tree_" + mt.__name__ + ".dot")

    # write tree of a reaction from ord examples
    # https://github.com/open-reaction-database/ord-schema/blob/main/examples/submissions/3_Liu_Copper_OrgSyn/example_liu.ipynb
    with open("reaction_ord.json", "r") as f:
        json_string = f.read()
    r = Reaction().from_json(json_string)
    tree = message_to_tree(r)
    write_dot(tree, "tree_liu.dot")
