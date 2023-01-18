import enum

import networkx as nx

from aspire_api.utils import write_dot, read_dot, import_string
from ord_betterproto.ord_tree import tree_to_message

if __name__ == '__main__':
    # read dot format tree back to message
    # dot format makes everything string...
    tree = read_dot("tree_liu.dot")
    tree = nx.relabel_nodes(tree, {x: int(x) for x in tree.nodes})
    for n in tree.nodes:
        type_string = tree.nodes[n]['type_string']
        tp = import_string(type_string)
        tree.nodes[n]['type'] = tp
        try:
            f = tree.nodes[n]['field']
            if issubclass(tp, enum.Enum):
                f = getattr(tp, f.split(".")[-1])
            tree.nodes[n]['field'] = f
        except KeyError:
            continue

    write_dot(tree, "tree_liu_back.dot")
    reaction = tree_to_message(tree)
    print(reaction.to_json())
