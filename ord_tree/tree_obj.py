import inspect
from copy import deepcopy

import betterproto
import networkx as nx
from loguru import logger

from ord_tree import ord_classes
from ord_tree.utils import get_class_string, MessageObjectTreeError, get_leafs, _RootNodeId, _NodeDelimiter, \
    is_arithmetic, import_string

"""
convert a betterproto.message instance to an arborescence
- tree nodes are `|` delimited strings 
- node attributes:
    label=str(child_attr.__class__),
    node_class=child_attr.__class__,
    node_class_as_string=get_class_string(child_attr),
    node_object=child_attr,
"""

PrefixDictKey = "<DictKey>"
PrefixListIndex = "<ListIndex>"


def edge_label_to_dict_key(label: str):
    assert label.startswith(PrefixDictKey)
    return label.replace(PrefixDictKey, "")


def edge_label_to_list_index(label: str):
    assert label.startswith(PrefixListIndex)
    return int(label.replace(PrefixListIndex, ""))


def _extend_object_node(
        node_id: str, tree: nx.DiGraph, delimiter: str = _NodeDelimiter
):
    assert node_id in tree.nodes
    obj = tree.nodes[node_id]['node_object']

    edge_prefix = ""
    # stop if reached literal leafs
    if obj.__class__ in ord_classes.BuiltinLiteralClasses or obj is None:
        return

    # TODO double check this is right
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
        raise MessageObjectTreeError(f"unexpected class: {obj.__class__} of {obj}")

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
        child = f"{node_id}{delimiter}{edge_prefix}{field_name}"
        # TODO use dataclass?
        node_attr = dict(
            label=str(child_attr.__class__),
            node_class=child_attr.__class__,
            node_class_as_string=get_class_string(child_attr),
            node_object=child_attr,
        )
        # if child_attr.__class__ in ord_classes.BuiltinLiteralClasses or child_attr is None:
        #     node_attr['nodel_value'] = child_attr

        tree.add_node(child, **node_attr)
        tree.add_edge(node_id, child, label=f"{edge_prefix}{field_name}", field_name=field_name)
        _extend_object_node(child, tree)


def message_object_to_message_object_tree(message: betterproto.Message, ) -> nx.DiGraph:
    tree = nx.DiGraph()
    tree.add_node(
        _RootNodeId,
        label=str(message.__class__),
        node_object=message,
        node_class=message.__class__,
        node_class_as_string=get_class_string(message.__class__),  # for importing
    )
    _extend_object_node(_RootNodeId, tree)
    return tree


def _construct_from_leafs(tree: nx.DiGraph, leaf: str = None):
    tree_size_before = len(tree.nodes)
    if len(tree.nodes) == 1:
        logger.info("reaching the last node, stopping")
        return
    if leaf is None:
        leaf = get_leafs(tree)[0]
    logger.info(f"contracting leaf node: {leaf}")
    parent = next(tree.predecessors(leaf))
    parent_class = import_string(tree.nodes[parent]['node_class_as_string'])
    assert inspect.isclass(parent_class)
    logger.info(f"target parent: {parent_class}")
    children = list(tree.successors(parent))
    logger.info(f"contracting with children: {children}")

    if parent_class in ord_classes.OrdMessageClasses:
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['node_object']
            attr_name = tree.edges[(parent, child)]['field_name']
            setattr(parent_object, attr_name, attr)

    elif parent_class in ord_classes.OrdEnumClasses:
        raise MessageObjectTreeError(f"{parent_class} can only be leafs!")
    # # as we use ord_enum as leafs (so ord_enum will always be leafs), this is not necessary
    #     if len(children) != 1:
    #         raise MessageObjectTreeError(f"try to construct an Enum: {parent_class} from !=1 children")
    #     child = children[0]
    #     v = tree.nodes[child]['node_object']
    #     k = tree.edges[(parent, child)]['label']
    #     assert k == 'name'
    #     parent_object = parent_class[v]

    elif parent_class == list:
        parent_object = []
        children = sorted(children, key=lambda x: tree.edges[(parent, x)]['field_name'])
        assert is_arithmetic([tree.edges[(parent, c)]['field_name'] for c in children], known_delta=1)
        for child in children:
            attr = tree.nodes[child]['node_object']
            parent_object.append(attr)

    elif parent_class == dict:
        parent_object = dict()
        for child in children:
            attr = tree.nodes[child]['node_object']
            key_name = tree.edges[(parent, child)]['field_name']
            parent_object[key_name] = attr
    else:
        raise MessageObjectTreeError(f"unexpected parent class: {parent_class}")

    logger.info(f"parent object constructed: {parent_object}")
    for child in children:
        tree.remove_node(child)
    tree.nodes[parent]['node_object'] = parent_object
    logger.info(f"tree size contraction: {tree_size_before} -> {len(tree)}")
    _construct_from_leafs(tree)


def message_object_tree_to_message_object(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    assert len(working_tree.nodes) == 1
    root_node = list(working_tree.nodes)[0]
    return working_tree.nodes[root_node]['node_object']


def inspect_message_object_tree(tree: nx.DiGraph):
    logger.warning("inspecting a message_object_tree...")
    logger.info(f"is this a directed graph?: {nx.is_directed(tree)}")
    logger.info(f"is this a tree?: {nx.is_arborescence(tree)}")
    logger.info(f"how many nodes are there?: {len(tree.nodes)} ")
    leafs = get_leafs(tree, sort=True)
    logger.info(f"how many leafs are there?: {len(leafs)} ")
    leafs_valued = [leaf for leaf in leafs if "value" in tree.nodes[leaf]]
    logger.info(f"how many leafs have `value` field set?: {leafs_valued}")
