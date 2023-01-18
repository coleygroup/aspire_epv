import inspect
from copy import deepcopy
from enum import Enum
from typing import get_type_hints, List, get_args, Dict, Type, Optional, Union

import betterproto
import networkx as nx

import ord_betterproto
from utils.tree_related import get_class_string

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


def get_type_hints_better(obj):
    d = dict()
    for k, v in get_type_hints(obj).items():
        if k.startswith("_"):
            continue
        d[k] = v
    return d


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


def _add_type_to_tree(
        tp: Type, tree: nx.DiGraph, parent: int = None,
        relation_to_parent: str = None, delimiter: str = "."
):
    # parent
    if parent is None:
        dotpath = ""
    else:
        parent_dotpath = tree.nodes[parent]["dotpath"]
        parent_tot = tree.nodes[parent]["tot"]
        if parent_tot in (TypeOfType.ListOrd, TypeOfType.ListLiteral):
            relation_to_parent = "<ListIndex>" + delimiter + relation_to_parent
        elif parent_tot in (TypeOfType.DictOrd, TypeOfType.DictLiteral):
            relation_to_parent = "<DictKey>" + delimiter + relation_to_parent
        elif parent_tot == TypeOfType.OptionalLiteral:
            relation_to_parent = "<Optional>" + delimiter + relation_to_parent
        dotpath = parent_dotpath + delimiter + relation_to_parent

    # self
    node = len(tree.nodes)
    node_tot = get_tot(tp)
    node_attr = {
        # "label": tp.__name__,
        "label": str(tp),
        "type": tp,
        "type_string": get_class_string(tp),
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

    for attr_name, attr_type in get_type_hints_better(self_tp).items():
        _add_type_to_tree(attr_type, tree, parent=node, relation_to_parent=attr_name)


def message_type_to_tree(message: Type) -> nx.DiGraph:
    g = nx.DiGraph()
    _add_type_to_tree(message, g)
    assert nx.is_arborescence(g)
    return g


def _add_attr_to_tree(
        attr: Union[betterproto.Message, List, Dict],
        tree: nx.DiGraph,
):
    if len(tree) == 0:
        tree.add_node(
            0,
            # label=attr.__class__.__name__,
            label=str(attr),
            type=attr.__class__,
            type_string=get_class_string(attr)
        )
    attr_node = len(tree) - 1

    if issubclass(attr.__class__, Enum) or attr.__class__ in LiteralClasses or attr is None:
        return
    elif attr.__class__ in OrdBetterprotoClasses:
        items = {field_name: getattr(attr, field_name) for field_name in attr._betterproto.sorted_field_names}.items()
    elif isinstance(attr, List):
        items = {index: obj for index, obj in enumerate(attr)}.items()
    elif isinstance(attr, Dict):
        items = attr.items()
    else:
        raise TypeError(f"unexpected type: {attr.__class__} of {attr}")

    items_used = []
    for field_name, child_attr in items:
        # TODO not sure these are the safe ways to ignore default
        if child_attr.__class__ in OrdBetterprotoClasses:
            if issubclass(child_attr.__class__, Enum):
                pass
            elif all(getattr(child_attr, f) == child_attr._get_field_default(f) for f in
                     child_attr._betterproto.sorted_field_names):
                continue
        elif any(isinstance(child_attr, c) for c in (List, Dict, str)) and len(child_attr) == 0:
            continue
        elif child_attr is None:
            continue
        items_used.append((field_name, child_attr))

    for field_name, child_attr in items_used:
        child = len(tree)
        # this captures `Enum` classes
        if issubclass(child_attr.__class__, LiteralClasses) or child_attr is None:
            node_attr = {
                # "label": child_attr.__class__.__name__,
                "label": str(child_attr.__class__),
                "field": child_attr,
                "type": child_attr.__class__,
                "type_string": get_class_string(child_attr),
            }
        else:
            # only literals can have field
            node_attr = {
                # "label": child_attr.__class__.__name__,
                "label": str(child_attr.__class__),
                "type": child_attr.__class__,
                "type_string": get_class_string(child_attr),
            }

        tree.add_node(child, **node_attr)
        tree.add_edge(attr_node, child, label=field_name)
        _add_attr_to_tree(child_attr, tree)


def message_to_tree(
        message: betterproto.Message,
        delimiter: str = ".",
) -> nx.DiGraph:
    tree = nx.DiGraph()
    _add_attr_to_tree(message, tree)
    for n in tree.nodes:
        path_to_root = nx.shortest_path(tree, 0, n)
        if n == 0:
            dotpath = ""
        else:
            edge_path = list(zip(path_to_root[:-1], path_to_root[1:]))
            dotpath = delimiter.join([str(tree.edges[e]['label']) for e in edge_path])
        tree.nodes[n]["dotpath"] = dotpath
    return tree


def get_leafs(tree: nx.DiGraph, sort=True):
    assert nx.is_arborescence(tree)
    leafs = [n for n in tree.nodes if tree.out_degree(n) == 0]
    if sort:
        leafs = sorted(leafs, key=lambda x: len(nx.shortest_path(tree, 0, x)), reverse=True)
    return leafs


def _construct_from_leafs(tree: nx.DiGraph):
    if len(tree.nodes) == 1:
        return

    leaf = get_leafs(tree)[0]
    parent = next(tree.predecessors(leaf))
    parent_class = tree.nodes[parent]['type']
    children = list(tree.successors(parent))

    if parent_class in OrdBetterprotoClasses:
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['field']
            attr_name = tree.edges[(parent, child)]['label']
            setattr(parent_object, attr_name, attr)
    elif parent_class == list:
        parent_object = []
        children = sorted(children, key=lambda x: tree.edges[(parent, x)]['label'])
        for child in children:
            attr = tree.nodes[child]['field']
            parent_object.append(attr)
    elif parent_class == dict:
        parent_object = dict()
        for child in children:
            attr = tree.nodes[child]['field']
            key_name = tree.edges[(parent, child)]['label']
            parent_object[key_name] = attr
    else:
        raise TypeError(f"unexpected type: {parent_class}")

    for child in children:
        tree.remove_node(child)
    tree.nodes[parent]['field'] = parent_object
    _construct_from_leafs(tree)


def tree_to_message(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    leafs = get_leafs(tree, sort=True)
    assert all(issubclass(tree.nodes[leaf]['type'], LiteralClasses) for leaf in leafs)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    return working_tree.nodes[0]['field']
