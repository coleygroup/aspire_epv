from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Type, Any, Union

import betterproto
from loguru import logger

from ord_tree.tree_obj import message_object_to_message_object_tree, PrefixDictKey, PrefixListIndex, \
    message_object_tree_to_message_object
from ord_tree.tree_type import message_type_to_message_type_tree
from ord_tree.type_hints import TypeOfTypeHint
from ord_tree.utils import nx, _NodeDelimiter, get_root, _RootNodeId


# TODO make classes serializable
# TODO DRY

class PrototypeTreeError(Exception): pass


class PtState(Enum):
    NodeNonLiteral = "NodeNonLiteral"  # for non-literal nodes
    NodePlaceholder = "NodePlaceholder"  # can be nodes or edges
    NodePreset = "NodePreset"  # can be nodes or edges
    EdgePlaceholder = "EdgePlaceholder"  # can be nodes or edges
    EdgePreset = "EdgePreset"  # can be nodes or edges
    EdgeAttrName = "EdgeAttrName"  # fixed edges


@dataclass
class PtEleAttr:
    label: str
    element_state: PtState  # pt state, indicating if the node has been preset, init as default, or placeholder
    element_value: Any
    map_to_mtt: Union[str, Tuple[str, str]]  # to which node in MTT it is being mapped to
    can_edit: bool  # literal nodes (builtin, enum, optional) or dict key, note list index is not one of these

    def as_dict(self):
        d = {
            "label": self.label,
            "element_state": self.element_state.value,
            "element_value": self.element_value,
            "map_to_mtt": self.map_to_mtt,
            "can_edit": self.can_edit,
        }
        return d


class PrototypeTree:
    def __init__(
            self, tree: nx.DiGraph, mtt: nx.DiGraph,
    ):
        """
        - a prototype tree P contains typing info and explicitly defined List/Dict sizes
        - it defines the underlying tree for reaction instances such that,
          let R be an arbitrary reaction tree of this prototype, R is isomorphic to P
        - prototype tree contains pre-defined literal fields, so the user just needs to fill the rest
        - a node can have one of the following states:
            - default
            - preset to a value
            - placeholder

        :param tree: integer nodes
        :param mtt: ord message type tree
        """
        self.tree = tree
        self.mtt = mtt
        self.mtt_n2ce = self._get_n2ce(self.mtt)

    @property
    def placeholder_nodes(self):
        return [k for k, d in nx.get_node_attributes(self.tree, "element_state").items() if
                d['element_state'] == PtState.NodePlaceholder.value]

    @property
    def placeholder_edges(self):
        return [(u, v) for (u, v), d in nx.get_edge_attributes(self.tree, "element_state").items() if
                d['element_state'] == PtState.EdgePlaceholder.value]

    def get_nodes_in_toths(self, toths: list[TypeOfTypeHint]):
        nodes = []
        for n in self.tree.nodes:
            mtt_node = self.tree.nodes[n]['map_to_mtt']
            mtt_toth = self.mtt.nodes[mtt_node]['node_class_toth']
            if mtt_toth in toths:
                nodes.append(n)
        return nodes

    @property
    def nodes_list_class(self):
        return self.get_nodes_in_toths([TypeOfTypeHint.ListOrdMessage, TypeOfTypeHint.ListBuiltinLiteral])

    @property
    def nodes_dict_class(self):
        return self.get_nodes_in_toths([TypeOfTypeHint.DictOrdMessage, TypeOfTypeHint.DictBuiltinLiteral])

    def check(self):
        # TODO implement
        # all dict key edges should be set
        # all dict keys of one parent should be unique
        # all list index edges should be set
        # list indices of one parent should be arithmetic sequence
        pass

    def get_path(self, node: int):
        root = get_root(self.tree)
        p = nx.shortest_path(self.tree, source=root, target=node)
        if len(p) == 1:
            return _RootNodeId
        str_path = []
        for i in range(len(p) - 1):
            u = p[i]
            v = p[i + 1]
            mtt_u = self.tree.nodes[u]['map_to_mtt']
            mtt_v = self.tree.nodes[v]['map_to_mtt']
            e = self.mtt.edges[(mtt_u, mtt_v)]['label']
            if e.startswith(PrefixDictKey) or e.startswith(PrefixListIndex):
                str_p = str(self.tree.edges[(u, v)]['element_value'])
            else:
                str_p = e
            str_path.append(str_p)
        return _NodeDelimiter.join(str_path)

    @staticmethod
    def _get_n2ce(mtt: nx.DiGraph) -> dict[str, list[Tuple[str, str]]]:
        """ node to [(child1, edge_label1), (child2, edge_label2), ...] """
        data = defaultdict(list)
        for u in mtt.nodes:
            for _, v, d in mtt.edges(u, data=True):
                data[u].append((v, d['label']))
        return data

    @staticmethod
    def get_mapped_mtt_node(mot_node: str, mtt: nx.DiGraph) -> str:
        paths = mot_node.split(_NodeDelimiter)
        for i, p in enumerate(paths):
            if p.startswith(PrefixListIndex):
                paths[i] = PrefixListIndex
            elif p.startswith(PrefixDictKey):
                paths[i] = PrefixDictKey
        node = _NodeDelimiter.join(paths)
        assert node in mtt.nodes
        return node

    @classmethod
    def from_message(cls, m: betterproto.Message):
        mot = message_object_to_message_object_tree(m)
        return PrototypeTree.from_mot(mot, m.__class__)

    @classmethod
    def from_mot(cls, mot: nx.DiGraph, message_type: Type):
        mtt = message_type_to_message_type_tree(message_type)
        pt = nx.DiGraph()
        pt_node_to_mot_node = dict()
        mot_node_to_pt_node = dict()
        for i, mot_node in enumerate(mot.nodes):
            pt_node = i
            pt_node_to_mot_node[i] = mot_node
            mot_node_to_pt_node[mot_node] = i
            mtt_node = PrototypeTree.get_mapped_mtt_node(mot_node, mtt)
            mot_node_attr = mot.nodes[mot_node]
            mtt_node_attr = mtt.nodes[mtt_node]
            mot_node_object = mot_node_attr['node_object']
            pt_node_attr = PtEleAttr(
                label=mot_node_attr['label'],
                element_state=PtState.NodePreset,
                element_value=mot_node_object,
                map_to_mtt=mtt_node,
                can_edit=True
            )
            if mtt_node_attr['node_class_toth'] not in (
                    TypeOfTypeHint.OptionalLiteral, TypeOfTypeHint.BuiltinLiteral, TypeOfTypeHint.OrdEnum):
                pt_node_attr.element_state = PtState.NodeNonLiteral
                pt_node_attr.element_value = None
                pt_node_attr.can_edit = False
            pt.add_node(pt_node, **pt_node_attr.as_dict())
        for mot_u, mot_v, mot_d in mot.edges(data=True):
            mtt_u = PrototypeTree.get_mapped_mtt_node(mot_u, mtt)
            mtt_v = PrototypeTree.get_mapped_mtt_node(mot_v, mtt)
            mtt_edge_label = mtt.edges[(mtt_u, mtt_v)]['label']
            pt_edge_attr = PtEleAttr(
                label=mtt_edge_label,
                element_state=PtState.EdgeAttrName,
                element_value=mtt_edge_label,
                map_to_mtt=(mtt_u, mtt_v),
                can_edit=False
            )
            if mtt_edge_label.startswith(PrefixDictKey):
                pt_edge_attr.element_state = PtState.EdgePreset
                pt_edge_attr.element_value = mot_d['field_name']
                pt_edge_attr.can_edit = True
            elif mtt_edge_label.startswith(PrefixListIndex):
                pt_edge_attr.element_state = PtState.EdgePreset
                pt_edge_attr.element_value = mot_d['field_name']
                pt_edge_attr.can_edit = False
            pt.add_edge(mot_node_to_pt_node[mot_u], mot_node_to_pt_node[mot_v], **pt_edge_attr.as_dict())
        return cls(pt, mtt)

    @classmethod
    def from_mtt(cls, mtt: nx.DiGraph):
        pt = nx.DiGraph()
        pt_node_to_mtt_node = dict()
        mtt_node_to_pt_node = dict()
        for i, mtt_node in enumerate(mtt.nodes):
            pt_node = i
            pt_node_to_mtt_node[i] = mtt_node
            mtt_node_to_pt_node[mtt_node] = i
            mtt_node_attr = mtt.nodes[mtt_node]
            pt_node_attr = PtEleAttr(
                label=mtt_node_attr['label'],
                element_state=PtState.NodePlaceholder,
                element_value=None,
                map_to_mtt=mtt_node,
                can_edit=True
            )
            if mtt_node_attr['node_class_toth'] not in (
                    TypeOfTypeHint.OptionalLiteral, TypeOfTypeHint.BuiltinLiteral, TypeOfTypeHint.OrdEnum):
                pt_node_attr.element_state = PtState.NodeNonLiteral
                pt_node_attr.element_value = None
                pt_node_attr.can_edit = False
            pt.add_node(pt_node, **pt_node_attr.as_dict())
        for mtt_u, mtt_v, mtt_d in mtt.edges(data=True):
            mtt_edge_label = mtt.edges[(mtt_u, mtt_v)]['label']
            pt_edge_attr = PtEleAttr(
                label=mtt_edge_label,
                element_state=PtState.EdgeAttrName,
                element_value=mtt_edge_label,
                map_to_mtt=(mtt_u, mtt_v),
                can_edit=False
            )
            if mtt_edge_label.startswith(PrefixDictKey):
                pt_edge_attr.element_state = PtState.EdgePlaceholder
                pt_edge_attr.element_value = None
                pt_edge_attr.can_edit = True
            elif mtt_edge_label.startswith(PrefixListIndex):
                pt_edge_attr.element_state = PtState.EdgePreset
                pt_edge_attr.element_value = 0
                pt_edge_attr.can_edit = False
            pt.add_edge(mtt_node_to_pt_node[mtt_u], mtt_node_to_pt_node[mtt_v], **pt_edge_attr.as_dict())
        return cls(pt, mtt)

    def to_mot(self):
        mot = nx.DiGraph()
        node_pt_to_mot = dict()
        for node in self.tree.nodes:
            mot_node = self.get_path(node)
            mtt_node_attr = self.mtt.nodes[self.tree.nodes[node]['map_to_mtt']]
            mot_node_attr = dict(
                label=str(mtt_node_attr['node_class']),
                node_class=mtt_node_attr['node_class'].__class__,
                node_class_as_string=mtt_node_attr['node_class_as_string'],
                node_object=self.tree.nodes[node]['element_value'],
            )
            mot.add_node(mot_node, **mot_node_attr)
            node_pt_to_mot[node] = mot_node
        for u, v, d in self.tree.edges(data=True):
            mot_u = node_pt_to_mot[u]
            mot_v = node_pt_to_mot[v]
            if self.mtt.nodes[self.tree.nodes[u]['map_to_mtt']]['node_class'] == list:
                prefix = PrefixListIndex
            elif self.mtt.nodes[self.tree.nodes[u]['map_to_mtt']]['node_class'] == dict:
                prefix = PrefixDictKey
            else:
                prefix = ""
            d = dict(
                label=f"{prefix}{d['element_value']}",
                field_name=d['element_value']
            )
            mot.add_edge(mot_u, mot_v, **d)
        return mot

    def to_message(self):
        mot = self.to_mot()
        return message_object_tree_to_message_object(mot)

    def change_element_state(self, element: Union[int, Tuple[int, int]], state: PtState):
        if isinstance(element, int):
            if self.tree.nodes[element]['element_state'] == PtState.NodeNonLiteral:
                logger.warning(f"changing state of a {PtState.NodeNonLiteral} node, ignoring this operation")
                return None
            self.tree.nodes[element]['element_state'] = state
        else:
            if self.tree.edges[element]['element_state'] == PtState.EdgeAttrName:
                logger.warning(f"changing state of a {PtState.EdgeAttrName} edge, ignoring this operation")
                return None
            self.tree.edges[element]['element_state'] = state

    def change_element_value(self, element: Union[int, Tuple[int, int]], value: Any):
        if isinstance(element, int):
            if self.tree.nodes[element]['element_state'] == PtState.NodeNonLiteral:
                logger.warning(f"changing value of a {PtState.NodeNonLiteral} node, ignoring this operation")
                return None
            self.tree.nodes[element]['element_value'] = value
        else:
            if self.tree.edges[element]['element_state'] == PtState.EdgeAttrName:
                logger.warning(f"changing value of a {PtState.EdgeAttrName} edge, ignoring this operation")
                return None
            self.tree.edges[element]['element_state'] = value

    def get_toth(self, node: int):
        return self.mtt.nodes[self.tree.nodes[node]['map_to_mtt']]['node_class_toth']

    def remove_node(self, node_to_remove: int):
        # if the node is an element of a list, reassign indices of the edges to its siblings
        parent = next(self.tree.predecessors(node_to_remove))
        if self.get_toth(parent) in (TypeOfTypeHint.ListOrdMessage, TypeOfTypeHint.ListBuiltinLiteral):
            children = list(self.tree.successors(parent))
            i = 0
            for child in children:
                if child == node_to_remove:
                    continue
                edge = (parent, child)
                edge_attr = self.tree.edges[edge]
                edge_attr['element_value'] = i
                edge_attr['label'] = f"{PrefixListIndex}{i}"
        for off in nx.descendants(self.tree, node_to_remove):
            self.tree.remove_node(off)
        self.tree.remove_node(node_to_remove)

    def extend_tree(self, from_node: int):
        if len(self.tree.nodes) == 0:
            mtt_node_attr = self.mtt.nodes[_RootNodeId]
            assert mtt_node_attr['node_class_toth'] == TypeOfTypeHint.OrdMessage
            root_attr = PtEleAttr(
                label=mtt_node_attr['label'],
                element_state=PtState.NodeNonLiteral,
                element_value=None,
                map_to_mtt=_RootNodeId,
                can_edit=False
            )
            self.tree.add_node(0, **root_attr.as_dict())
            return

        assert len(self.tree.nodes) > 0
        logger.info(
            f"extending node: {from_node} {self.get_path(from_node)}, current tree size: {len(self.tree.nodes)}")

        from_node_mtt = self.tree.nodes[from_node]['map_to_mtt']
        from_node_mtt_toth = self.mtt.nodes[from_node]['node_class_toth']
        from_node_mtt_toth: TypeOfTypeHint

        # if the mapped node is a literal, do nothing, note enum is here
        if from_node_mtt_toth in (
                TypeOfTypeHint.BuiltinLiteral,
                TypeOfTypeHint.OptionalLiteral,
                TypeOfTypeHint.OrdEnum
        ):
            pass
        # otherwise, add children
        else:
            for mtt_child, mtt_edge_label in self.mtt_n2ce[from_node_mtt]:
                # check on List
                if from_node_mtt_toth in (TypeOfTypeHint.ListOrdMessage, TypeOfTypeHint.ListBuiltinLiteral):
                    existing_children = [v for _, v in self.tree.out_edges(from_node)]
                    edge_attr = PtEleAttr(
                        label=f"{PrefixListIndex}{len(existing_children)}",
                        element_state=PtState.EdgePreset,
                        element_value=len(existing_children),
                        map_to_mtt=(from_node_mtt, mtt_child),
                        can_edit=False
                    )
                    assert len(self.mtt_n2ce[from_node_mtt]) == 1
                    assert mtt_edge_label.startswith(PrefixListIndex)
                elif from_node_mtt_toth in (TypeOfTypeHint.DictOrdMessage, TypeOfTypeHint.DictBuiltinLiteral):
                    existing_children = [v for _, v in self.tree.out_edges(from_node)]
                    edge_attr = PtEleAttr(
                        label=f"{PrefixDictKey}{len(existing_children)}",
                        element_state=PtState.EdgePreset,
                        element_value=f"{PrefixDictKey}{len(existing_children)}",
                        map_to_mtt=(from_node_mtt, mtt_child),
                        can_edit=True
                    )
                    assert len(self.mtt_n2ce[from_node_mtt]) == 1
                    assert mtt_edge_label.startswith(PrefixDictKey)
                else:
                    if mtt_edge_label in [d['label'] for _, _, d in self.tree.out_edges(from_node, data=True)]:
                        logger.info(f"extending an edge but its label already exists, skipping: {mtt_edge_label}")
                        continue
                    edge_attr = PtEleAttr(
                        label=mtt_edge_label,
                        element_state=PtState.EdgeAttrName,
                        element_value=mtt_edge_label,
                        map_to_mtt=(from_node_mtt, mtt_child),
                        can_edit=False
                    )

                child = len(self.tree)
                mtt_child_attr = self.mtt.nodes[mtt_child]
                child_attr = PtEleAttr(
                    label=mtt_child_attr['label'],
                    element_state=PtState.NodeNonLiteral,
                    element_value=None,
                    map_to_mtt=mtt_child,
                    can_edit=False
                )
                if mtt_child_attr['node_class_toth'] in (
                        TypeOfTypeHint.BuiltinLiteral, TypeOfTypeHint.OptionalLiteral, TypeOfTypeHint.OrdEnum):
                    child_attr.element_state = PtState.NodePlaceholder
                    child_attr.can_edit = True
                logger.info(f"adding edge: ({from_node}, {child}) {self.get_path(from_node)}.{edge_attr.label}")
                self.tree.add_node(child, **child_attr.as_dict())
                self.tree.add_edge(from_node, child, **edge_attr.as_dict())
                logger.info(f"edge added, current tree size: {len(self.tree.nodes)}")
