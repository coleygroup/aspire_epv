import base64
from abc import ABCMeta, abstractmethod
from collections import Counter
from typing import Any, Iterable, Tuple, Type

import networkx as nx

from ord_tree.mot import MotEleAttr, PT_PLACEHOLDER
from ord_tree.mtt import MttNodeAttr
from ord_tree.ord_classes import OrdMessageClasses, BuiltinLiteralClasses, OrdEnumClasses
from ord_tree.utils import import_string
from .cyto_config import *

CYTO_COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]


class CytoElement(metaclass=ABCMeta):
    def __init__(
            self,
            data_id: str,
            data_label: str,
            data_ele_attrs: dict,
            data_kwargs: dict = None,
            selected: bool = False,
            selectable: bool = True,
            classes: Iterable[str] = (),
    ):
        self._data_kwargs = data_kwargs
        self.data_ele_attrs = data_ele_attrs
        self.data_id = data_id
        self.data_label = data_label
        self.selected = selected
        self.selectable = selectable
        self._classes = classes

    @property
    def data_kwargs(self):
        if self._data_kwargs is None:
            return dict()
        else:
            return self._data_kwargs

    @property
    @abstractmethod
    def data(self) -> dict:
        pass

    @property
    def classes(self):
        return " ".join(self._classes)

    @classmethod
    @abstractmethod
    def from_dict(cls, d: dict[str, Any]):
        pass

    def as_dict(self):
        pass


class CytoElementNode(CytoElement):

    def __init__(
            self,
            data_id: str,
            data_label: str,
            data_ele_attrs: dict,
            data_parent: str = None,
            data_kwargs: dict = None,
            position_x: float = None,
            position_y: float = None,
            selected: bool = False,
            selectable: bool = True,
            grabbable: bool = False,
            locked: bool = False,
            classes: Iterable[str] = (),
    ):
        super().__init__(data_id, data_label, data_ele_attrs, data_kwargs, selected, selectable, classes)
        self.data_parent = data_parent
        self.position_x = position_x
        self.position_y = position_y
        self.grabbable = grabbable
        self.locked = locked

    @property
    def position(self):
        if self.position_x is None or self.position_y is None:
            return None
        return {"x": self.position_x, "y": self.position_y}

    @property
    def data(self) -> dict:
        d = dict(id=self.data_id, label=self.data_label, parent=self.data_parent, ele_attrs=self.data_ele_attrs,
                 **self.data_kwargs)
        if self.data_parent is None:
            del d['parent']
        return d

    def as_dict(self) -> dict[str, Any]:
        d = dict(
            group="nodes",
            data=self.data,
            position=self.position,
            selected=self.selected,
            selectable=self.selectable,
            grabbable=self.grabbable,
            locked=self.locked,
            classes=self.classes,
        )
        if d['position'] is None:
            del d['position']
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        data = d['data']
        try:
            parent = d['parent']
        except KeyError:
            parent = None

        try:
            position = d['position']
        except KeyError:
            position = {'x': None, 'y': None}

        return cls(
            data_id=data['id'],
            data_label=data['label'],
            data_ele_attrs=data['ele_attrs'],
            data_parent=parent,
            data_kwargs={k: v for k, v in data.items() if k not in ('id', 'label', 'ele_attrs', 'parent')},
            position_x=position['x'],
            position_y=position['y'],
            selected=d['selected'],
            selectable=d['selectable'],
            grabbable=d['grabbable'],
            locked=d['locked'],
            classes=tuple(d['classes'].split()),
        )

    @staticmethod
    def derive_cyto_classes_from_node_class(node_class: Type) -> [str]:
        cyto_classes = []
        if node_class in (dict, list):
            cyto_classes.append(CYTO_MUTABLE_NODE_CLASS[1:])
        elif node_class in BuiltinLiteralClasses + OrdEnumClasses:
            cyto_classes.append(CYTO_LITERAL_NODE_CLASS[1:])
        elif node_class in OrdMessageClasses:
            cyto_classes.append(CYTO_MESSAGE_NODE_CLASS[1:])
        else:
            raise TypeError(f"illegal node class: {node_class}")
        return cyto_classes

    @staticmethod
    def derive_oneof_color_mtt(mtt: nx.DiGraph, child: str) -> dict[str, str]:
        v_attr = mtt.nodes[child]
        v_attr = MttNodeAttr(**v_attr)
        oneof_group = v_attr['mtt_relation_to_parent_oneof']

        try:
            parent = next(mtt.predecessors(child))
        except StopIteration:
            return dict()

        u_attr = mtt.nodes[parent]
        u_attr = MttNodeAttr(**u_attr)
        u_class = import_string(u_attr['mtt_class_string'])
        if u_class not in OrdMessageClasses:
            return dict()

        children = mtt.successors(parent)
        oneof_groups = [mtt.nodes[vv]['mtt_relation_to_parent_oneof'] for vv in children]
        oneof_groups = [og for og in oneof_groups if og is not None and Counter(oneof_groups)[og] > 1]
        oneof_groups = sorted(set(oneof_groups))
        assert len(oneof_groups) < len(CYTO_COLORS)
        try:
            i = oneof_groups.index(oneof_group)
            return dict(oneof_color=CYTO_COLORS[i])
        except ValueError:
            return dict()

    @classmethod
    def from_mtt_node(cls, mtt: nx.DiGraph, mtt_node: str):
        node_attr = mtt.nodes[mtt_node]
        node_attr: MttNodeAttr

        node_class = import_string(node_attr['mtt_class_string'])
        cyto_classes = CytoElementNode.derive_cyto_classes_from_node_class(node_class)

        oneof_color_dict = CytoElementNode.derive_oneof_color_mtt(mtt, mtt_node)
        oneof_color_dict.update({"relation": node_attr['mtt_relation_to_parent']})  # this is for label switch
        return cls(
            data_id=mtt_node, data_label=node_class.__name__, data_kwargs=oneof_color_dict,
            data_ele_attrs=node_attr,
            classes=cyto_classes,
        )

    @classmethod
    def from_mot_node(cls, mot: nx.DiGraph, mot_node: int):
        node_attrs = mot.nodes[mot_node]
        node_attrs: MotEleAttr
        node_class = import_string(node_attrs['mot_class_string'])
        cyto_classes = CytoElementNode.derive_cyto_classes_from_node_class(node_class)

        # everything should be jsonable
        if node_class == bytes:
            # TODO make sure this works
            try:
                node_attrs['mot_value'] = base64.b64encode(node_attrs['mot_value']).decode('ascii')
            except TypeError:
                node_attrs['mot_value'] = str(node_attrs['mot_value'])

        return cls(
            data_id=str(node_attrs['mot_element_id']),
            data_label=node_class.__name__,
            data_ele_attrs=node_attrs,
            classes=cyto_classes,
        )


class CytoElementEdge(CytoElement):
    def __init__(
            self,
            data_id: str,
            data_label: str,
            data_source: str,
            data_target: str,
            data_ele_attrs: dict,
            data_kwargs: dict[str, Any] = None,
            selected: bool = False,
            selectable: bool = True,
            classes: Iterable[str] = (),
    ):
        super().__init__(data_id, data_label, data_ele_attrs, data_kwargs, selected, selectable, classes)
        self.data_target = data_target
        self.data_source = data_source

    @property
    def data(self):
        return dict(
            id=self.data_id, label=self.data_label, source=self.data_source, target=self.data_target,
            ele_attrs=self.data_ele_attrs, **self.data_kwargs
        )

    def as_dict(self) -> dict[str, Any]:
        d = dict(
            group="edges",
            data=self.data,
            selected=self.selected,
            selectable=self.selectable,
            classes=self.classes,
        )
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        data = d['data']
        return cls(
            data_id=data['id'],
            data_label=data['label'],
            data_source=data['source'],
            data_target=data['target'],
            data_ele_attrs=data['ele_attrs'],
            data_kwargs={k: v for k, v in data.items() if k not in ('id', 'label', 'ele_attrs', 'source', 'target')},
            selected=d['selected'],
            selectable=d['selectable'],
            classes=tuple(d['classes'].split()),
        )

    @classmethod
    def from_mtt_edge(cls, mtt: nx.DiGraph, mtt_edge: Tuple[str, str]):
        u, v = mtt_edge
        v_attr = mtt.nodes[v]
        v_attr: MttNodeAttr
        u_attr = mtt.nodes[u]
        u_attr: MttNodeAttr
        edge_label = v_attr['mtt_relation_to_parent']

        return cls(
            data_id=str(mtt_edge),
            data_label=edge_label,
            data_source=u,
            data_target=v,
            data_ele_attrs={"u": u_attr, "v": v_attr},
        )

    @classmethod
    def from_mot_edge(cls, mot: nx.DiGraph, mot_edge: Tuple[int, int]):
        edge_attrs = mot.edges[mot_edge]
        edge_attrs: MotEleAttr
        u, v = edge_attrs['mot_element_id']
        mtt_u, mtt_v = edge_attrs['mtt_element_name']
        relation = mtt_v.replace(mtt_u, '')
        return cls(
            data_id=str(edge_attrs['mot_element_id']),
            data_label=relation,
            data_source=str(u),
            data_target=str(v),
            data_ele_attrs=edge_attrs,
        )


def mtt_to_cyto(mtt: nx.DiGraph, hide_literal=True) -> Tuple[
    dict[str, CytoElementNode],
    dict[Tuple[str, str], CytoElementEdge],
]:
    elements_node = dict()
    included = []
    for n in mtt.nodes:
        e = CytoElementNode.from_mtt_node(mtt, n)
        node_attr = mtt.nodes[n]
        node_attr: MttNodeAttr
        if hide_literal and import_string(node_attr['mtt_class_string']) in BuiltinLiteralClasses + OrdEnumClasses:
            continue
        elements_node[n] = e
        included.append(n)

    elements_edge = dict()
    for e in mtt.edges:
        u, v = e
        if u in included and v in included:
            e = CytoElementEdge.from_mtt_edge(mtt, e)
            elements_edge[(u, v)] = e
    return elements_node, elements_edge


def mot_to_cyto(mot: nx.DiGraph) -> Tuple[
    dict[str, CytoElementNode],
    dict[Tuple[str, str], CytoElementEdge],
]:
    elements_node = dict()
    n_to_class = {n: import_string(mot.nodes[n]['mot_class_string']) for n in mot.nodes}
    for n in mot.nodes:
        e = CytoElementNode.from_mot_node(mot, n)
        node_class = n_to_class[n]
        if node_class in BuiltinLiteralClasses + OrdEnumClasses:
            e._classes = [*e._classes] + [CYTO_MESSAGE_NODE_LITERAL_CLASS[1:]]

        # check class related to literals
        has_literal_children = False
        has_literal_children_placeholder = False
        for c in mot.successors(n):
            if n_to_class[c] in BuiltinLiteralClasses + OrdEnumClasses:
                has_literal_children = True
                if mot.nodes[c]['mot_state'] == PT_PLACEHOLDER:
                    has_literal_children_placeholder = True
        if has_literal_children:
            e._classes = [*e._classes] + [CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_CLASS[1:]]
            if has_literal_children_placeholder:
                e._classes = [*e._classes] + [CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PLACEHOLDER_CLASS[1:]]
            else:
                e._classes = [*e._classes] + [CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PRESET_CLASS[1:]]
        elements_node[n] = e

    elements_edge = dict()
    for e in mot.edges:
        u, v = e
        e = CytoElementEdge.from_mot_edge(mot, e)
        if e.data_ele_attrs['mot_can_edit']:
            e._classes = [*e._classes] + [CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS[1:]]
            if e.data_ele_attrs['mot_state'] == PT_PLACEHOLDER:
                e._classes = [*e._classes] + [CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS[1:]]
            else:
                e._classes = [*e._classes] + [CYTO_MESSAGE_EDGE_PRESET_CLASS[1:]]
        elements_edge[(u, v)] = e
    return elements_node, elements_edge


def mot_to_cyto_element_list(mot: nx.DiGraph) -> list[dict]:
    elements_node, elements_edge = mot_to_cyto(mot)
    elements_node.update(elements_edge)
    return [e.as_dict() for e in elements_node.values()]


def cyto_to_mot(elements: list[dict]):
    node_element_dict = dict()
    edge_element_dict = dict()
    for e in elements:
        if e['group'] == 'nodes':
            node_element_dict[e['data']['id']] = e
        elif e['group'] == 'edges':
            edge_element_dict[e['data']['id']] = e

    mot = nx.DiGraph()
    for node, node_dict in node_element_dict.items():
        node_id = int(node)
        data_ele_attrs = node_dict['data']['ele_attrs']
        data_ele_attrs: MotEleAttr
        # this can only happen for nodes, not edges
        if import_string(data_ele_attrs['mot_class_string']) == bytes:
            data_ele_attrs['mot_value'] = base64.b64decode(data_ele_attrs['mot_value'])
        mot.add_node(node_id, **data_ele_attrs)
    for edge, edge_dict in edge_element_dict.items():
        u = int(edge_dict['data']['source'])
        v = int(edge_dict['data']['target'])
        data_ele_attrs = edge_dict['data']['ele_attrs']
        mot.add_edge(u, v, **data_ele_attrs)
    return mot
