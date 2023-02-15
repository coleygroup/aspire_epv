import inspect
from copy import deepcopy
from typing import Any, Union, TypedDict, Tuple

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

PT_PLACEHOLDER = "PT_PLACEHOLDER"
PT_PRESET = "PT_PRESET"
PT_STATES = (PT_PLACEHOLDER, PT_PRESET)


def _node_path_mot_to_mtt(mot_node_path: str):
    relations = mot_node_path.split(NodePathDelimiter)
    for i, r in enumerate(relations):
        if r.startswith(PrefixListIndex):
            relations[i] = PrefixListIndex
        if r.startswith(PrefixDictKey):
            relations[i] = PrefixDictKey
    return NodePathDelimiter.join(relations)

    # def as_dict(self) -> dict:
    #     return asdict(self)
    #
    # @staticmethod
    # def to_dict_key(relation_repr: str):
    #     assert relation_repr.startswith(PrefixDictKey)
    #     return relation_repr.replace(PrefixDictKey, "")
    #
    # @staticmethod
    # def to_list_index(relation_repr: str):
    #     assert relation_repr.startswith(PrefixListIndex)
    #     return int(relation_repr.replace(PrefixListIndex, ""))


class MotEleAttr(TypedDict):
    mot_element_id: Union[int, Tuple[int, int]]
    mot_can_edit: bool  # is_literal for nodes, is DictKey for edges
    mot_state: str
    mot_value: Union[int, float, str, bytes, None]  # if not is_literal, this is set to None
    mtt_element_name: Union[str, Tuple[str, str]]
    mot_class_string: Union[str, Tuple[str, str]]


def _extend_object(
        node_id: int, tree: nx.DiGraph, node_object: Any, node_path: str
):
    assert node_id in tree.nodes

    mtt_node = _node_path_mot_to_mtt(node_path)

    edge_prefix = ""
    # stop if reached literal leafs
    if node_object.__class__ in ord_classes.BuiltinLiteralClasses or node_object is None:
        return

    elif node_object.__class__ in ord_classes.OrdEnumClasses:
        # two ways to handle OrdEnum
        # 1. treat them as leafs
        return
        # 2. treat them as one level above leafs, initialized as Enum[name] when backward converting
        # see https://docs.python.org/3/library/enum.html#:~:text=Color.GREEN%3A%202%3E-,__getitem__,-(cls%2C
        # items = dict(name=obj.name).items()

    elif node_object.__class__ in ord_classes.OrdMessageClasses:
        items = {field_name: getattr(node_object, field_name) for field_name in
                 node_object._betterproto.sorted_field_names}.items()

    elif node_object.__class__ == list:
        edge_prefix = PrefixListIndex
        items = {index: obj for index, obj in enumerate(node_object)}.items()

    elif node_object.__class__ == dict:
        edge_prefix = PrefixDictKey
        items = node_object.items()
    else:
        raise TypeError(f"unexpected class: {node_object.__class__} of {node_object}")

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
        child_id = len(tree.nodes)
        child_node_path = f"{node_path}{NodePathDelimiter}{edge_prefix}{field_name}"
        child_mtt_node = _node_path_mot_to_mtt(child_node_path)
        is_child_literal = child_attr.__class__ in ord_classes.BuiltinLiteralClasses + ord_classes.OrdEnumClasses  # or child_attr is None
        if is_child_literal:
            child_value = child_attr
        else:
            child_value = None
        child_node_attr = MotEleAttr(
            mot_element_id=child_id,
            mot_can_edit=is_child_literal,
            mot_state=PT_PRESET,
            mot_value=child_value,
            mtt_element_name=child_mtt_node,
            mot_class_string=get_class_string(child_attr)
        )
        tree.add_node(child_id, **child_node_attr)

        edge_attr = MotEleAttr(
            mot_element_id=(node_id, child_id),
            mot_can_edit=node_object.__class__ == dict,
            mot_state=PT_PRESET,
            mot_value=field_name,
            mtt_element_name=(mtt_node, child_mtt_node),
            mot_class_string=(get_class_string(node_object), get_class_string(child_attr)),
        )

        tree.add_edge(node_id, child_id, **edge_attr)
        _extend_object(child_id, tree, node_object=child_attr, node_path=child_node_path)


def get_mot(message: betterproto.Message, ) -> nx.DiGraph:
    assert message.__class__ in ord_classes.OrdMessageClasses
    tree = nx.DiGraph()
    root_node_attr = MotEleAttr(
        mot_element_id=0,
        mot_can_edit=False,
        mot_state=PT_PRESET,
        mot_value=None,
        mtt_element_name=RootNodePath,
        mot_class_string=get_class_string(message),
    )
    tree.add_node(
        0, **root_node_attr
    )
    _extend_object(0, tree, message, RootNodePath)

    # verify mapping
    mtt = get_mtt(message.__class__)
    for n, d in tree.nodes(data=True):
        assert d['mtt_element_name'] in mtt.nodes
    return tree


def _construct_from_leafs(tree: nx.DiGraph):
    tree_size_before = len(tree.nodes)

    if len(tree.nodes) == 1:
        logger.debug("reaching the last node, stopping")
        return

    leaf = get_leafs(tree)[0]

    logger.debug(f"contracting leaf node: {leaf}")

    parent = next(tree.predecessors(leaf))

    parent_class = import_string(tree.nodes[parent]['mot_class_string'])
    assert inspect.isclass(parent_class)

    logger.debug(f"target parent: {parent_class}")

    children = list(tree.successors(parent))
    logger.debug(f"contracting with children: {children}")

    if parent_class in ord_classes.OrdMessageClasses:
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['mot_value']
            attr_name = tree.edges[(parent, child)]['mot_value']
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
        children = sorted(children, key=lambda x: tree.edges[(parent, x)]['mot_value'])
        assert is_arithmetic([tree.edges[(parent, c)]['mot_value'] for c in children], known_delta=1)
        for child in children:
            attr = tree.nodes[child]['mot_value']
            parent_object.append(attr)

    elif parent_class == dict:
        parent_object = dict()
        for child in children:
            attr = tree.nodes[child]['mot_value']
            key_name = tree.edges[(parent, child)]['mot_value']
            parent_object[key_name] = attr
    else:
        raise TypeError(f"unexpected parent class: {parent_class}")

    logger.debug(f"parent object constructed: {parent_object}")
    for child in children:
        tree.remove_node(child)
    tree.nodes[parent]['mot_value'] = parent_object
    logger.debug(f"tree size contraction: {tree_size_before} -> {len(tree)}")
    _construct_from_leafs(tree)


def message_from_mot(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    assert len(working_tree.nodes) == 1
    root_node = list(working_tree.nodes)[0]
    return working_tree.nodes[root_node]['mot_value']


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
