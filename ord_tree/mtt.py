import inspect
import typing
from typing import get_args, Type, get_origin, Optional, TypedDict, Union

import networkx as nx
from betterproto import ProtoClassMetadata

from ord_tree.ord_classes import BuiltinLiteralClasses, OrdEnumClasses, OrdMessageClasses
from ord_tree.utils import get_class_string, NodePathDelimiter, RootNodePath, PrefixListIndex, PrefixDictKey, \
    import_string, get_root, get_type_hints_without_private

"""
message type tree
"""


class MttNodeAttr(TypedDict):
    mtt_node_name: str  # same as node itself
    mtt_type_hint_string: str
    mtt_class_string: str
    mtt_parent: str
    mtt_relation_to_parent: str
    mtt_relation_to_parent_oneof: Union[None, str]


def _extend_mtt(
        type_hint, tree: nx.DiGraph, parent: str = None,
        relation_to_parent: str = None,
        relation_to_parent_oneof: str = None,
):
    """ recursively extending mtt """
    if parent is None:
        node_name = RootNodePath
    else:
        node_name = parent + NodePathDelimiter + relation_to_parent

    if inspect.isclass(type_hint):
        node_class = type_hint
    else:
        node_class = get_origin(type_hint)
        if node_class not in (list, dict):
            # this can only be Optional[*]
            assert type_hint.__class__ == typing._UnionGenericAlias and type_hint.__name__ == Optional.__name__
            node_class = get_args(type_hint)[0]

    node_attr = MttNodeAttr(
        mtt_type_hint_string=str(type_hint),
        mtt_class_string=get_class_string(node_class),
        mtt_relation_to_parent=relation_to_parent,
        mtt_parent=parent,
        mtt_node_name=node_name,
        mtt_relation_to_parent_oneof=relation_to_parent_oneof,
    )

    tree.add_node(node_name, **node_attr)
    if parent is not None:
        tree.add_edge(parent, node_name)

    # children
    if node_class == list:
        attr_name = PrefixListIndex
        attr_type = get_args(type_hint)[0]
        _extend_mtt(attr_type, tree, parent=node_name, relation_to_parent=attr_name)
    elif node_class == dict:
        attr_name = PrefixDictKey
        attr_type = get_args(type_hint)[1]
        _extend_mtt(attr_type, tree, parent=node_name, relation_to_parent=attr_name)
    elif node_class in BuiltinLiteralClasses + OrdEnumClasses:
        return
    else:
        assert node_class in OrdMessageClasses
        pcm = ProtoClassMetadata(node_class)
        for attr_name, attr_type in get_type_hints_without_private(type_hint).items():
            try:
                group_name = pcm.oneof_group_by_field[attr_name]
            except KeyError:
                group_name = None
            _extend_mtt(attr_type, tree, parent=node_name, relation_to_parent=attr_name,
                        relation_to_parent_oneof=group_name)


def get_mtt(message: Type) -> nx.DiGraph:
    assert inspect.isclass(message) and message in OrdMessageClasses
    g = nx.DiGraph()
    _extend_mtt(message, g)
    assert nx.is_arborescence(g)
    return g


def mtt_to_dict(mtt: nx.DiGraph) -> dict:
    return nx.node_link_data(mtt)


def mtt_from_dict(d: dict) -> nx.DiGraph:
    return nx.node_link_graph(d, directed=True)


def get_mtt_node_class(mtt: nx.DiGraph, node: str) -> Type:
    c = import_string(mtt.nodes[node]['mtt_class_string'])
    assert inspect.isclass(c)
    return c


def get_mtt_root_class(mtt: nx.DiGraph) -> Type:
    root = get_root(mtt)
    return get_mtt_node_class(mtt, root)


if __name__ == '__main__':
    from ord_tree.utils import write_file, get_tree_depth
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
