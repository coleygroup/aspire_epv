import inspect
from enum import Enum
from typing import get_type_hints, List, get_args, Dict, Type, Optional

import networkx as nx

import ord_betterproto
from ord_betterproto import Reaction

"""
convert a betterproto.message class to an arborescence
"""

LiteralClasses = (str, float, int, bool, bytes)
NumericClasses = (float, int)
OrdBetterprotoClasses = tuple(dict(
    (
        inspect.getmembers(
            ord_betterproto, lambda member: inspect.isclass(member) and member.__module__ == ord_betterproto.__name__
        )
    )
).values())


class TypeOfType(Enum):
    Literal = "Literal"
    Ord = "Ord"
    ListOrd = "ListOrd"
    ListLiteral = "ListLiteral"
    DictOrd = "DictOrd"
    DictLiteral = "DictLiteral"
    OptionalLiteral = "OptionalLiteral"


def get_tot(tp: Type) -> TypeOfType:
    if tp in LiteralClasses:
        return TypeOfType.Literal
    if tp in OrdBetterprotoClasses:
        return TypeOfType.Ord
    if tp.__name__ == List.__name__:
        args_tps = get_args(tp)
        assert len(args_tps) == 1, f"type hint for List has len(args) != 1, this is not expected: {args_tps}"
        arg_tp = args_tps[0]
        if arg_tp in OrdBetterprotoClasses:
            return TypeOfType.ListOrd
        elif arg_tp in LiteralClasses:
            return TypeOfType.ListLiteral
        else:
            raise TypeError(f"unexpected tot: {arg_tp}")
    if tp.__name__ == Dict.__name__:
        args_tps = get_args(tp)
        assert len(args_tps) == 2, f"type hint for Dict has len(args) != 2, this is not expected: {args_tps}"
        assert args_tps[0] == str
        arg_tp = args_tps[1]
        if arg_tp in OrdBetterprotoClasses:
            return TypeOfType.DictOrd
        elif arg_tp in LiteralClasses:
            return TypeOfType.DictLiteral
        else:
            raise TypeError(f"unexpected tot: {arg_tp}")
    if tp.__name__ == Optional.__name__:
        assert get_args(tp)[0] in LiteralClasses, f"found an optional field of non-literal class: {tp}"
        return TypeOfType.OptionalLiteral
    raise TypeError(f"unidentifiable type: {tp}")


def _add_type_to_tree(tp: Type, tree: nx.DiGraph, parent: int = None, relation_to_parent: str = None):
    # parent
    if parent is None:
        dotpath = ""
    else:
        parent_dotpath = tree.nodes[parent]["dotpath"]
        parent_tot = tree.nodes[parent]["tot"]
        if parent_tot in (TypeOfType.ListOrd, TypeOfType.ListLiteral):
            relation_to_parent = "<ListIndex>." + relation_to_parent
        elif parent_tot in (TypeOfType.DictOrd, TypeOfType.DictLiteral):
            relation_to_parent = "<DictKey>." + relation_to_parent
        elif parent_tot == TypeOfType.OptionalLiteral:
            relation_to_parent = "<Optional>." + relation_to_parent
        dotpath = parent_dotpath + "." + relation_to_parent

    # self
    node = len(tree.nodes)
    node_tot = get_tot(tp)
    node_attr = {
        "label": str(tp),
        "type": tp,
        "tot": node_tot,
        "dotpath": dotpath
    }
    tree.add_node(node, **node_attr)
    if parent is not None:
        tree.add_edge(parent, node, label=relation_to_parent)

    # children
    if node_tot in (TypeOfType.ListOrd, TypeOfType.ListLiteral):
        self_tp = get_args(tp)[0]
    elif node_tot in (TypeOfType.DictOrd, TypeOfType.DictLiteral):
        self_tp = get_args(tp)[1]
    elif node_tot == TypeOfType.OptionalLiteral:
        self_tp = get_args(tp)[0]
    elif node_tot == TypeOfType.Literal:
        return
    else:
        self_tp = tp

    for attr_name, attr_type in get_type_hints(self_tp).items():
        if attr_name.startswith("_"):
            continue
        _add_type_to_tree(attr_type, tree, parent=node, relation_to_parent=attr_name)


def message_type_to_tree(message: Type) -> nx.DiGraph:
    g = nx.DiGraph()
    _add_type_to_tree(message, g)
    assert nx.is_arborescence(g)
    return g


if __name__ == '__main__':
    reaction_graph = message_type_to_tree(Reaction)
    nx.drawing.nx_agraph.write_dot(reaction_graph, "reaction.dot")
