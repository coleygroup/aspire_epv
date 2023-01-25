from ord_betterproto import Reaction, Compound, ReactionInput, ReactionWorkup
from ord_tree.tree_type import message_type_to_message_type_tree
from ord_tree.utils import write_dot

if __name__ == '__main__':
    # write tree of a Message type in dot format
    for mt in (Reaction, Compound, ReactionInput, ReactionWorkup):
        tree = message_type_to_message_type_tree(mt)
        write_dot(tree, "tree_" + mt.__name__ + ".dot")
