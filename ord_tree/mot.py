import inspect
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, Union

import betterproto
import networkx as nx
from loguru import logger

from ord_tree import ord_classes
from ord_tree.mtt import get_mtt
from ord_tree.utils import NodePathDelimiter, RootNodePath, PrefixListIndex, PrefixDictKey
from ord_tree.utils import get_leafs, is_arithmetic, import_string, get_class_string

"""
convert a betterproto.message instance to an arborescence
"""


@dataclass
class MotNodeAttr:
    mot_node_name: str  # same as node itself
    mot_map_to_mtt: str
    mot_is_literal: bool
    mot_node_object: Any  # if non-literal, this field is set to None when jsonfy

    def as_dict(self) -> dict:
        d = asdict(self)
        d['mot_node_object'] = self.mot_node_object
        return d

    def as_dict_with_mtt(self, mtt: nx.DiGraph) -> dict:
        d = self.as_dict()
        mtt_node = self.mot_map_to_mtt
        d.update(
            mtt.nodes[mtt_node]
        )
        return d

    @staticmethod
    def map_to_mtt(mot_node_name: str):
        relations = mot_node_name.split(NodePathDelimiter)
        for i, r in enumerate(relations):
            if r.startswith(PrefixListIndex):
                relations[i] = PrefixListIndex
            if r.startswith(PrefixDictKey):
                relations[i] = PrefixDictKey
        return NodePathDelimiter.join(relations)


@dataclass
class MotEdgeAttr:
    mot_relation: Union[str, int]  # attr_name, dict key, or list index
    mot_relation_representation: str

    def as_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def to_dict_key(relation_repr: str):
        assert relation_repr.startswith(PrefixDictKey)
        return relation_repr.replace(PrefixDictKey, "")

    @staticmethod
    def to_list_index(relation_repr: str):
        assert relation_repr.startswith(PrefixListIndex)
        return int(relation_repr.replace(PrefixListIndex, ""))


def _extend_object_node(
        node_name: str, tree: nx.DiGraph, mtt: nx.DiGraph
):
    assert node_name in tree.nodes
    obj = tree.nodes[node_name]['mot_node_object']

    edge_prefix = ""
    # stop if reached literal leafs
    if obj.__class__ in ord_classes.BuiltinLiteralClasses or obj is None:
        return

    elif obj.__class__ in ord_classes.OrdEnumClasses:
        # two ways to handle OrdEnum
        # 1. treat them as leafs
        return
        # 2. treat them as one level above leafs, initialized as Enum[name] when backward converting
        # see https://docs.python.org/3/library/enum.html#:~:text=Color.GREEN%3A%202%3E-,__getitem__,-(cls%2C
        # items = dict(name=obj.name).items()

    elif obj.__class__ in ord_classes.OrdMessageClasses:
        items = {field_name: getattr(obj, field_name) for field_name in obj._betterproto.sorted_field_names}.items()

    elif obj.__class__ == list:
        edge_prefix = PrefixListIndex
        items = {index: obj for index, obj in enumerate(obj)}.items()

    elif obj.__class__ == dict:
        edge_prefix = PrefixDictKey
        items = obj.items()
    else:
        raise TypeError(f"unexpected class: {obj.__class__} of {obj}")

    # do not extend the child attr if it's default
    items_used = []
    for field_name, child_attr in items:
        if child_attr.__class__ in ord_classes.OrdMessageClasses:
            if all(
                    getattr(child_attr, f) == child_attr._get_field_default(f)
                    for f in child_attr._betterproto.sorted_field_names
            ):
                continue
        elif child_attr.__class__ in (list, dict, str) and len(child_attr) == 0:
            continue
        elif child_attr is None:
            continue
        # special handling for enum not necessary
        items_used.append((field_name, child_attr))

    for field_name, child_attr in items_used:
        child = f"{node_name}{NodePathDelimiter}{edge_prefix}{field_name}"

        child_node_attr = MotNodeAttr(
            mot_node_name=child,
            mot_map_to_mtt=MotNodeAttr.map_to_mtt(child),
            mot_is_literal=child_attr.__class__ in ord_classes.BuiltinLiteralClasses or child_attr is None,
            mot_node_object=child_attr,
        )
        child_node_attr = child_node_attr.as_dict_with_mtt(mtt)
        tree.add_node(child, **child_node_attr)

        edge_attr = MotEdgeAttr(
            mot_relation=field_name,
            mot_relation_representation=f"{edge_prefix}{field_name}"
        )

        tree.add_edge(node_name, child, **edge_attr.as_dict())
        _extend_object_node(child, tree, mtt)


def get_mot(message: betterproto.Message, ) -> nx.DiGraph:
    assert message.__class__ in ord_classes.OrdMessageClasses
    mtt = get_mtt(message.__class__)
    tree = nx.DiGraph()
    root_node_attr = MotNodeAttr(
        mot_node_name=RootNodePath,
        mot_map_to_mtt=RootNodePath,
        mot_is_literal=False,
        mot_node_object=message,
    )
    tree.add_node(
        RootNodePath, **root_node_attr.as_dict_with_mtt(mtt)
    )
    _extend_object_node(RootNodePath, tree, mtt)
    return tree


def _construct_from_leafs(tree: nx.DiGraph, leaf: str = None):
    tree_size_before = len(tree.nodes)

    if len(tree.nodes) == 1:
        logger.debug("reaching the last node, stopping")
        return

    if leaf is None:
        leaf = get_leafs(tree)[0]

    logger.debug(f"contracting leaf node: {leaf}")

    parent = next(tree.predecessors(leaf))

    parent_class = import_string(tree.nodes[parent]['mtt_class_string'])
    assert inspect.isclass(parent_class)

    logger.debug(f"target parent: {parent_class}")

    children = list(tree.successors(parent))
    logger.debug(f"contracting with children: {children}")

    if parent_class in ord_classes.OrdMessageClasses:
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['mot_node_object']
            attr_name = tree.edges[(parent, child)]['mot_relation']
            setattr(parent_object, attr_name, attr)

    elif parent_class in ord_classes.OrdEnumClasses:
        raise RuntimeError(f"{parent_class} can only be leafs!")
    # # as we use ord_enum as leafs (so ord_enum will always be leafs), this is not necessary
    #     if len(children) != 1:
    #         raise MessageObjectTreeError(f"try to construct an Enum: {parent_class} from !=1 children")
    #     child = children[0]
    #     v = tree.node_elements[child]['node_object']
    #     k = tree.edges[(parent, child)]['relation_repr']
    #     assert k == 'name'
    #     parent_object = parent_class[v]

    elif parent_class == list:
        parent_object = []
        children = sorted(children, key=lambda x: tree.edges[(parent, x)]['mot_relation'])
        assert is_arithmetic([tree.edges[(parent, c)]['mot_relation'] for c in children], known_delta=1)
        for child in children:
            attr = tree.nodes[child]['mot_node_object']
            parent_object.append(attr)

    elif parent_class == dict:
        parent_object = dict()
        for child in children:
            attr = tree.nodes[child]['mot_node_object']
            key_name = tree.edges[(parent, child)]['mot_relation']
            parent_object[key_name] = attr
    else:
        raise TypeError(f"unexpected parent class: {parent_class}")

    logger.debug(f"parent object constructed: {parent_object}")
    for child in children:
        tree.remove_node(child)
    tree.nodes[parent]['mot_node_object'] = parent_object
    logger.debug(f"tree size contraction: {tree_size_before} -> {len(tree)}")
    _construct_from_leafs(tree)


def message_from_mot(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    assert len(working_tree.nodes) == 1
    root_node = list(working_tree.nodes)[0]
    return working_tree.nodes[root_node]['mot_node_object']


def mot_to_dict(mot: nx.DiGraph):
    m = message_from_mot(mot)
    root_class_string = get_class_string(m.__class__)
    d = {'message': m.to_dict(), 'root_class_string': root_class_string}
    return d


def mot_from_dict(d):
    m_class = d['root_class_string']
    m_class = import_string(m_class)
    m = m_class()
    m.from_dict(d['message'])
    return get_mot(m)
