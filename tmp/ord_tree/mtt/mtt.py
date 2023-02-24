from ord_betterproto import Reaction, Compound, ReactionInput, ReactionWorkup
from ord_tree.mtt import get_mtt
from ord_tree.utils import write_dot

if __name__ == '__main__':
    # write tree of a Message type in dot format
    for mt in (Reaction, Compound, ReactionInput, ReactionWorkup):
        tree = get_mtt(mt)
        write_dot(tree, "tree_" + mt.__name__ + ".dot")
