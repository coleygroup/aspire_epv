from typing import get_args, Type, get_origin

import networkx as nx

from ord_betterproto.type_hints import get_toth, TypeOfTypeHint, get_type_hints_without_private
from ord_betterproto.utils import get_class_string, MessageTypeTreeError, DotPathLabel, RootDotPath

"""
convert a betterproto.message class to an arborescence
this provides a skeleton for users to define a message instance
"""


def _extend_type_hint(
        type_hint, tree: nx.DiGraph, parent: int = None,
        relation_to_parent: str = None, delimiter: str = "."
):
    # parent
    if parent is None:
        dotpath = RootDotPath
    else:
        parent_dotpath = tree.nodes[parent][DotPathLabel]
        dotpath = parent_dotpath + delimiter + relation_to_parent

    # current node
    node = len(tree.nodes)
    node_toth = get_toth(type_hint)

    # get node class
    # if one of these, the node class is just the type hint
    if node_toth in (
            TypeOfTypeHint.OrdMessage,
            TypeOfTypeHint.BuiltinLiteral,
            TypeOfTypeHint.OrdEnum,
    ):
        node_class = type_hint
    # if one of these, the node class is the `origin` of type hint
    elif node_toth in (
            TypeOfTypeHint.DictOrdMessage, TypeOfTypeHint.DictBuiltinLiteral,
            TypeOfTypeHint.ListBuiltinLiteral, TypeOfTypeHint.ListOrdMessage,
    ):
        node_class = get_origin(type_hint)
    # if optional, the node class is the * in Optional[*]
    elif node_toth == TypeOfTypeHint.OptionalLiteral:
        node_class = get_args(type_hint)[0]
    else:
        raise MessageTypeTreeError(f"node class or toth cannot be identified from: {type_hint}")

    node_attr = dict(
        label=str(type_hint),
        label_info="str(type_hint)",
        type_hint=type_hint,
        node_class=node_class,
        node_class_as_string=get_class_string(node_class),
    )
    node_attr[DotPathLabel] = dotpath
    tree.add_node(node, **node_attr)
    if parent is not None:
        tree.add_edge(parent, node, label=relation_to_parent)

    # children
    if node_toth in (TypeOfTypeHint.ListOrdMessage, TypeOfTypeHint.ListBuiltinLiteral):
        attr_name = "<ListIndex>"
        attr_type = get_args(type_hint)[0]
        _extend_type_hint(attr_type, tree, parent=node, relation_to_parent=attr_name)
    elif node_toth in (TypeOfTypeHint.DictOrdMessage, TypeOfTypeHint.DictBuiltinLiteral):
        attr_name = "<DictKey>"
        attr_type = get_args(type_hint)[0]
        _extend_type_hint(attr_type, tree, parent=node, relation_to_parent=attr_name)
    elif node_toth in (TypeOfTypeHint.BuiltinLiteral, TypeOfTypeHint.OptionalLiteral, TypeOfTypeHint.OrdEnum):
        return
    else:
        for attr_name, attr_type in get_type_hints_without_private(type_hint).items():
            _extend_type_hint(attr_type, tree, parent=node, relation_to_parent=attr_name)


def message_type_to_message_type_tree(message: Type) -> nx.DiGraph:
    g = nx.DiGraph()
    _extend_type_hint(message, g)
    assert nx.is_arborescence(g)
    return g
