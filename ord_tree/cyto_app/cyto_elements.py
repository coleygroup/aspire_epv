from abc import ABCMeta, abstractmethod
from collections import Counter
from typing import Any, Iterable, Tuple

import networkx as nx

from ord_tree.mtt import MttNodeAttr
from ord_tree.ord_classes import OrdMessageClasses, BuiltinLiteralClasses, OrdEnumClasses
from ord_tree.utils import import_string
from .cyto_config import CYTO_MUTABLE_NODE_CLASS, CYTO_LITERAL_NODE_CLASS, CYTO_MESSAGE_NODE_CLASS

CYTO_COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]


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


class CytoElement(metaclass=ABCMeta):
    def __init__(
            self,
            data_id: str,
            data_label: str,
            data_kwargs: dict[str, Any] = None,
            selected: bool = False,
            selectable: bool = True,
            classes: Iterable[str] = (),
            additional_data: dict = None,
    ):
        self.data_id = data_id
        self.data_label = data_label
        self._data_kwargs = data_kwargs
        self.selected = selected
        self.selectable = selectable
        self._classes = classes
        if additional_data is None:
            additional_data = dict()
        self.additional_data = additional_data

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
            data_kwargs: dict[str, Any] = None,
            position_x: float = None,
            position_y: float = None,
            parent: str = None,
            selected: bool = False,
            selectable: bool = True,
            grabbable: bool = False,
            locked: bool = False,
            classes: Iterable[str] = (),
            additional_data: dict = None,
    ):
        super().__init__(data_id, data_label, data_kwargs, selected, selectable, classes, additional_data)
        self.position_x = position_x
        self.position_y = position_y
        self.parent = parent
        self.grabbable = grabbable
        self.locked = locked

    @property
    def position(self):
        if self.position_x is None or self.position_y is None:
            return None
        return {"x": self.position_x, "y": self.position_y}

    @property
    def data(self) -> dict:
        return dict(id=self.data_id, label=self.data_label, **self.data_kwargs)

    def as_dict(self) -> dict[str, Any]:
        d = dict(
            group="nodes",
            data=self.data,
            parent=self.parent,
            position=self.position,
            selected=self.selected,
            selectable=self.selectable,
            grabbable=self.grabbable,
            locked=self.locked,
            classes=self.classes,
        )
        delete_ks = []
        for k, v in d.items():
            if v is None:
                delete_ks.append(k)
        for k in delete_ks:
            del d[k]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        data = d['data']
        try:
            position = d['position']
            position_x = position['x']
            position_y = position['y']
        except KeyError:
            position_x = None
            position_y = None
        try:
            parent = d['parent']
        except KeyError:
            parent = None

        return cls(
            data_id=data['id'],
            data_label=data['label'],
            data_kwargs={k: v for k, v in data.items() if k not in ('id', 'label')},
            position_x=position_x,
            position_y=position_y,
            parent=parent,
            selected=d['selected'],
            selectable=d['selectable'],
            grabbable=d['grabbable'],
            locked=d['locked'],
            classes=tuple(d['classes'].split()),
        )

    @classmethod
    def from_mtt_node(cls, mtt: nx.DiGraph, mtt_node: str):
        node_attr = mtt.nodes[mtt_node]
        node_attr = MttNodeAttr(**node_attr)

        node_class = import_string(node_attr['mtt_class_string'])
        cyto_classes = []
        if node_class in (dict, list):
            cyto_classes.append(CYTO_MUTABLE_NODE_CLASS[1:])
        elif node_class in BuiltinLiteralClasses + OrdEnumClasses:
            cyto_classes.append(CYTO_LITERAL_NODE_CLASS[1:])
        elif node_class in OrdMessageClasses:
            cyto_classes.append(CYTO_MESSAGE_NODE_CLASS[1:])
        else:
            raise TypeError(f"illegal node class: {node_class}")
        oneof_color = derive_oneof_color_mtt(mtt, mtt_node)
        oneof_color.update({'relation': node_attr['mtt_relation_to_parent']})
        return cls(
            data_id=mtt_node, data_label=node_class.__name__, parent=node_attr['mtt_parent'],
            classes=cyto_classes, additional_data=node_attr, data_kwargs=oneof_color
        )


class CytoElementEdge(CytoElement):
    def __init__(
            self,
            data_id: str,
            data_label: str,
            data_source: str,
            data_target: str,
            data_kwargs: dict[str, Any] = None,
            selected: bool = False,
            selectable: bool = True,
            classes: Iterable[str] = (),
            additional_data: dict = None,
    ):
        super().__init__(data_id, data_label, data_kwargs, selected, selectable, classes, additional_data)
        self.data_target = data_target
        self.data_source = data_source

    @property
    def data(self):
        return dict(
            id=self.data_id, label=self.data_label, source=self.data_source, target=self.data_target, **self.data_kwargs
        )

    def as_dict(self) -> dict[str, Any]:
        d = dict(
            group="edges",
            data=self.data,
            selected=self.selected,
            selectable=self.selectable,
            classes=self.classes,
        )
        delete_ks = []
        for k, v in d.items():
            if v is None:
                delete_ks.append(k)
        for k in delete_ks:
            del d[k]

        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        data = d['data']
        return cls(
            data_id=data['id'],
            data_label=data['label'],
            data_source=data['source'],
            data_target=data['target'],
            data_kwargs={k: v for k, v in data.items() if k not in ('id', 'label')},
            selected=d['selected'],
            selectable=d['selectable'],
            classes=tuple(d['classes'].split()),
        )

    @classmethod
    def from_mtt_edge(cls, mtt: nx.DiGraph, mtt_edge: Tuple[str, str]):
        u, v = mtt_edge
        v_attr = mtt.nodes[v]
        v_attr = MttNodeAttr(**v_attr)
        u_attr = mtt.nodes[u]
        u_attr = MttNodeAttr(**u_attr)
        edge_label = v_attr['mtt_relation_to_parent']

        return cls(
            data_id=str(mtt_edge),
            data_label=edge_label,
            data_source=u,
            data_target=v,
            additional_data={"u_attr": u_attr, "v_attr": v_attr},
        )


def mtt_to_cyto(mtt: nx.DiGraph, hide_literal=True):
    elements = dict()
    included = []
    for n in mtt.nodes:
        e = CytoElementNode.from_mtt_node(mtt, n)
        node_attr = MttNodeAttr(**mtt.nodes[n])
        if hide_literal and import_string(node_attr['mtt_class_string']) in BuiltinLiteralClasses + OrdEnumClasses:
            continue
        elements[n] = e
        included.append(n)

    for e in mtt.edges:
        u, v = e
        if u in included and v in included:
            e = CytoElementEdge.from_mtt_edge(mtt, e)
            elements[(u, v)] = e
    return [e.as_dict() for e in elements.values()]
