import inspect
import typing
from typing import get_args, Type, get_origin, Optional, TypedDict

import networkx as nx

from ord_tree.ord_classes import BuiltinLiteralClasses, OrdEnumClasses
from ord_tree.type_hints import get_type_hints_without_private
from ord_tree.utils import get_class_string, NodePathDelimiter, RootNodePath, PrefixListIndex, PrefixDictKey, \
    import_string

"""
message type tree
- node == sting path from root
"""


class MttNodeAttr(TypedDict):
    mtt_type_hint_string: str
    mtt_class_string: str
    mtt_relation_to_parent: str
    mtt_parent: str
    mtt_node_name: str  # same as node itself


def _extend_mtt(
        type_hint, tree: nx.DiGraph, parent: str = None,
        relation_to_parent: str = None
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
        for attr_name, attr_type in get_type_hints_without_private(type_hint).items():
            _extend_mtt(attr_type, tree, parent=node_name, relation_to_parent=attr_name)


def get_mtt(message: Type) -> nx.DiGraph:
    g = nx.DiGraph()
    _extend_mtt(message, g)
    assert nx.is_arborescence(g)
    return g


def mtt_to_dict(mtt: nx.DiGraph):
    return nx.to_dict_of_dicts(mtt)


def mtt_from_dict(d: dict):
    return nx.from_dict_of_dicts(d)


def get_mtt_node_class(mtt: nx.DiGraph, node: str) -> Type:
    c = import_string(mtt.nodes[node]['mtt_class_string'])
    assert inspect.isclass(c)
    return c
