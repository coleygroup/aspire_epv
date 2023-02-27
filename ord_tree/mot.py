import inspect
from copy import deepcopy
from typing import Any, Union, TypedDict, Tuple

import betterproto
import networkx as nx
from loguru import logger

from ord_betterproto import Reaction
from ord_tree import ord_classes
from ord_tree.mtt import get_mtt
from ord_tree.utils import NodePathDelimiter, RootNodePath, PrefixListIndex, PrefixDictKey, get_root, \
    get_leafs, is_arithmetic, import_string, get_class_string

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
        items = dict()
        for field_name in node_object._betterproto.sorted_field_names:
            v = node_object._Message__raw_get(field_name)
            if v is not betterproto.PLACEHOLDER:
                items[field_name] = v
        items = items.items()

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
        logger.debug(f"extending: {child_id}, {mot_get_path(tree, child_id)}, {child_node_attr['mot_value']}")
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
        mot_class_string = d['mot_class_string']
        mtt_class_string = mtt.nodes[d['mtt_element_name']]['mtt_class_string']
        mot_class = import_string(mot_class_string)
        mtt_class = import_string(mtt_class_string)
        try:
            assert mot_class == mtt_class
        except AssertionError:
            logger.debug(
                f"for node path: {mot_get_path(tree, n)} mtt_class: {mtt_class_string}, mot_class: {mot_class_string}")
            assert mtt_class in ord_classes.OrdEnumClasses
            assert mot_class in ord_classes.BuiltinLiteralClasses
    return tree


def _construct_from_leafs(tree: nx.DiGraph, visited_leafs: set[int] = None):
    if visited_leafs is None:
        visited_leafs = set()

    n_visited = len(visited_leafs)

    unvisited_leafs = set(tree.nodes).difference(visited_leafs)
    if len(unvisited_leafs) == 1:
        logger.debug("all nodes visited, stopping")
        return

    leaf = get_leafs(tree.subgraph(unvisited_leafs))[0]

    logger.debug(f"contracting leaf node: {leaf}")

    parent = next(tree.predecessors(leaf))

    parent_class = import_string(tree.nodes[parent]['mot_class_string'])
    assert inspect.isclass(parent_class)

    logger.debug(f"target parent: {parent_class}")

    children = list(tree.successors(parent))
    logger.debug(f"contracting with children: {children}")

    if parent_class in ord_classes.OrdMessageClasses:

        # this is better for `oneof` see `test/bug/betterproto_data.py`
        parent_object = parent_class()
        for child in children:
            attr = tree.nodes[child]['mot_value']
            attr_name = tree.edges[(parent, child)]['mot_value']
            setattr(parent_object, attr_name, attr)
            logger.debug(f"setting {mot_get_path(tree, child)} {attr_name}=={attr}")

        # kwargs = dict()
        # for child in children:
        #     attr = tree.nodes[child]['mot_value']
        #     attr_name = tree.edges[(parent, child)]['mot_value']
        #     logger.debug(f"setting {mot_get_path(tree, child)} {attr_name}=={attr} {type(attr)}")
        #     kwargs[attr_name] = attr
        # parent_object = parent_class(**kwargs)


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
        visited_leafs.add(child)
    tree.nodes[parent]['mot_value'] = parent_object
    logger.debug(f"visited: {n_visited} -> {len(visited_leafs)}")
    _construct_from_leafs(tree, visited_leafs)


def message_from_mot(tree: nx.DiGraph) -> betterproto.Message:
    assert nx.is_arborescence(tree)
    working_tree = deepcopy(tree)
    _construct_from_leafs(working_tree)
    root_node = get_root(working_tree)
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


def mot_get_path(mot: nx.DiGraph, node: int):
    root = get_root(mot)
    p = nx.shortest_path(mot, source=root, target=node)
    if len(p) == 1:
        return RootNodePath
    str_path = []
    for i in range(len(p) - 1):
        u = p[i]
        v = p[i + 1]
        u_class = import_string(mot.nodes[u]['mot_class_string'])
        if u_class == list:
            prefix = PrefixListIndex
        elif u_class == dict:
            prefix = PrefixDictKey
        else:
            prefix = ""
        str_p = str(mot.edges[(u, v)]["mot_value"])
        str_p = prefix + str_p
        str_path.append(str_p)
    return NodePathDelimiter.join(str_path)


# prototype operations
def pt_remove_node(mot_original: nx.DiGraph, node_to_remove: int, inplace=False):
    if inplace:
        mot = mot_original
    else:
        mot = deepcopy(mot_original)
    # if the node is an element of a list, reassign indices of the edges to its siblings
    parent = next(mot.predecessors(node_to_remove))
    parent_class = import_string(mot.nodes[parent]['mot_class_string'])
    if parent_class == list:
        children = list(mot.successors(parent))
        i = 0
        for child in children:
            if child == node_to_remove:
                continue
            edge = (parent, child)
            edge_attr = mot.edges[edge]
            edge_attr['mot_value'] = i
            i += 1
    for off in nx.descendants(mot, node_to_remove):
        mot.remove_node(off)
    mot.remove_node(node_to_remove)
    if not inplace:
        return mot


def pt_detach_node(mot: nx.DiGraph, new_root: int, inplace=False):
    new_tree = list(nx.descendants(mot, new_root))
    new_tree.append(new_root)
    if inplace:
        nodes_to_remove = [n for n in mot.nodes if n not in new_tree]
        for n in nodes_to_remove:
            mot.remove_node(n)
    else:
        return deepcopy(mot.subgraph(new_tree))


def pt_extend_node(mot_original: nx.DiGraph, from_node: int, inplace=False):
    if inplace:
        mot = mot_original
    else:
        mot = deepcopy(mot_original)
    # TODO if we are to extend a node in a detached tree,
    #  mtt_element_name field can have <ROOT> points to `Reaction` which is not present in the current mtt
    # mtt = get_mtt(import_string(mot.nodes[get_root(mot)]['mot_class_string']))
    mtt = get_mtt(Reaction)
    assert len(mot.nodes) > 0
    logger.info(
        f"extending node: {from_node} {mot_get_path(mot, from_node)}, current tree size: {len(mot.nodes)}"
    )
    from_node_class_string = mot.nodes[from_node]['mot_class_string']
    from_node_class = import_string(from_node_class_string)
    # if the mapped node is a literal, do nothing, note enum is here
    if from_node_class in ord_classes.BuiltinLiteralClasses + ord_classes.OrdEnumClasses:
        pass

    # otherwise, add children
    else:
        from_node_mtt = mot.nodes[from_node]['mtt_element_name']  # in which <ROOT> is Reaction!
        children_mtt = list(mtt.successors(from_node_mtt))
        for child_mtt in children_mtt:
            child_class_string = mtt.nodes[child_mtt]['mtt_class_string']
            child_class = import_string(child_class_string)
            new_child = max(mot.nodes) + 1
            child_attr = MotEleAttr(
                mot_element_id=new_child,
                mot_can_edit=child_class in ord_classes.BuiltinLiteralClasses + ord_classes.OrdEnumClasses,
                mot_state=PT_PLACEHOLDER,
                mot_value=None,
                mtt_element_name=child_mtt,
                mot_class_string=child_class_string,
            )
            existing_edge_values = [d['mot_value'] for _, _, d in mot.out_edges(from_node, data=True)]

            if from_node_class == list:
                assert len(children_mtt) == 1
                tmp_mot_can_edit = False
                tmp_mot_state = PT_PRESET
                tmp_mot_value = len(existing_edge_values)

            elif from_node_class == dict:
                assert len(children_mtt) == 1
                tmp_mot_can_edit = True
                tmp_mot_state = PT_PLACEHOLDER
                tmp_mot_value = f"{PrefixDictKey}{len(existing_edge_values)}"

            else:
                child_mtt_relation_to_parent = mtt.nodes[child_mtt]['mtt_relation_to_parent']
                if child_mtt_relation_to_parent in existing_edge_values:
                    logger.info(
                        f"extending an edge but its label already exists, skipping: {child_mtt_relation_to_parent}")
                    continue

                tmp_mot_can_edit = False
                tmp_mot_state = PT_PRESET
                tmp_mot_value = child_mtt_relation_to_parent

            edge_attr = MotEleAttr(
                mot_element_id=(from_node, new_child),
                mot_can_edit=tmp_mot_can_edit,
                mot_state=tmp_mot_state,
                mot_value=tmp_mot_value,
                mtt_element_name=(from_node_mtt, child_mtt),
                mot_class_string=(from_node_class_string, child_class_string),
            )

            logger.info(
                f"adding edge: ({from_node}, {new_child}) {mot_get_path(mot, from_node)}.{edge_attr['mot_value']}")
            mot.add_node(new_child, **child_attr)
            mot.add_edge(from_node, new_child, **edge_attr)
            logger.info(f"edge added, current tree size: {len(mot.nodes)}")
    if not inplace:
        return mot
