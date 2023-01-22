import inspect
from copy import deepcopy

import betterproto
import networkx as nx

from ord_betterproto import ord_classes
from ord_betterproto.utils import get_class_string, MessageObjectTreeError, get_leafs, assign_dotpath

"""
convert a betterproto.message instance to an arborescence
"""


def _extend_object_node(obj_node: int, tree: nx.DiGraph, ):
    assert obj_node in tree.nodes
    obj = tree.nodes[obj_node]['node_object']

    # stop if reached literal leafs
    if obj.__class__ in ord_classes.BuiltinLiteralClasses or obj is None:
        return

    # TODO double check this is right
    # two ways to handle OrdEnum
    elif obj.__class__ in ord_classes.OrdEnumClasses:
        # 1. treat them as leafs
        # return
        # 2. treat them as one level above leafs, initialized as Enum[name] when backward converting
        # see https://docs.python.org/3/library/enum.html#:~:text=Color.GREEN%3A%202%3E-,__getitem__,-(cls%2C
        items = dict(name=obj.name).items()

    elif obj.__class__ in ord_classes.OrdMessageClasses:
        items = {field_name: getattr(obj, field_name) for field_name in obj._betterproto.sorted_field_names}.items()

    elif obj.__class__ == list:
        items = {index: obj for index, obj in enumerate(obj)}.items()

    elif obj.__class__ == dict:
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
        child = len(tree)
        node_attr = dict(
            label=str(child_attr.__class__),
            label_info="str(child_attr.__class__)",
            node_class=child_attr.__class__,
            node_class_as_string=get_class_string(child_attr),
            node_object=child_attr,
        )
        # if child_attr.__class__ in ord_classes.BuiltinLiteralClasses or child_attr is None:
        #     node_attr['nodel_value'] = child_attr

        tree.add_node(child, **node_attr)
        tree.add_edge(obj_node, child, label=field_name)
        _extend_object_node(child, tree)


def message_object_to_message_object_tree(
        message: betterproto.Message,
        delimiter: str = ".",
) -> nx.DiGraph:
    tree = nx.DiGraph()
    tree.add_node(
        0,
        label=str(message.__class__),
        label_info="str(obj.__class__)",
        node_object=message,
        node_class=message.__class__,
        node_class_as_string=get_class_string(message.__class__),
    )
    _extend_object_node(0, tree)
    assign_dotpath(tree, delimiter=delimiter, root=0, edge_attr="label", node_attr="dotpath")
    return tree


def _construct_from_leafs(tree: nx.DiGraph):
    if len(tree.nodes) == 1:
        return

    leaf = get_leafs(tree)[0]
    parent = next(tree.predecessors(leaf))
    parent_class = tree.nodes[parent]['node_class']
    assert inspect.isclass(parent_class)
    children = list(tree.successors(parent))

    if parent_class in ord_classes.OrdMessageClasses:
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['node_object']
            attr_name = tree.edges[(parent, child)]['label']
            setattr(parent_object, attr_name, attr)

    elif parent_class in ord_classes.OrdEnumClasses:
        if len(children) != 1:
            raise MessageObjectTreeError(f"try to construct an Enum: {parent_class} from !=1 children")
        child = children[0]
        v = tree.nodes[child]['node_object']
        k = tree.edges[(parent, child)]['label']
        assert k == 'name'
        parent_object = parent_class[v]

    elif parent_class == list:
        parent_object = []
        children = sorted(children, key=lambda x: tree.edges[(parent, x)]['label'])
        for child in children:
            attr = tree.nodes[child]['node_object']
            parent_object.append(attr)

    elif parent_class == dict:
        parent_object = dict()
        for child in children:
            attr = tree.nodes[child]['node_object']
            key_name = tree.edges[(parent, child)]['label']
            parent_object[key_name] = attr
    else:
        raise MessageObjectTreeError(f"unexpected parent class: {parent_class}")

    for child in children:
        tree.remove_node(child)
    tree.nodes[parent]['node_object'] = parent_object
    _construct_from_leafs(tree)


def message_object_tree_to_message_object(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    return working_tree.nodes[0]['node_object']


def inspect_message_object_tree(tree: nx.DiGraph):
    from loguru import logger
    logger.warning("inspecting a message_object_tree...")
    logger.info(f"is this a directed graph?: {nx.is_directed(tree)}")
    logger.info(f"is this a tree?: {nx.is_arborescence(tree)}")
    logger.info(f"how many nodes are there?: {len(tree.nodes)} ")
    leafs = get_leafs(tree, sort=True)
    logger.info(f"how many leafs are there?: {len(leafs)} ")
    leafs_valued = [leaf for leaf in leafs if "value" in tree.nodes[leaf]]
    logger.info(f"how many leafs have `value` field set?: {leafs_valued}")
