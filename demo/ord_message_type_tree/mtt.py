from ord_betterproto import Reaction, Compound, ReactionInput, ReactionWorkup
from ord_betterproto.message_type_tree import message_type_to_message_type_tree
from ord_betterproto.utils import write_dot

if __name__ == '__main__':
    # write tree of a Message type in dot format
    for mt in (Reaction, Compound, ReactionInput, ReactionWorkup):
        tree = message_type_to_message_type_tree(mt)
        write_dot(tree, "tree_" + mt.__name__ + ".dot")
