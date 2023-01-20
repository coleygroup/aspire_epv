from collections import defaultdict
from typing import Tuple

from ord_betterproto.ord_tree import *
from utils.tree_related import *


# a prototype tree has typing info and explicitly defined ListKey and DictKey
# prototype tree produces a list of **Literal** fields that the user needs to fill to construct a message
# prototype tree + user-input literal = message


class PrototypeTree:
    # TODO make `MSONable`
    def __init__(self, m_tree: nx.DiGraph, mt_tree: nx.DiGraph):
        self.m_tree = m_tree
        self.mt_tree = mt_tree
        assert self.mt_tree.in_degree(0) == 0  # 0 is root
        self.children_and_names_mt = self._get_node_to_children_and_names()

    def _get_node_to_children_and_names(self) -> dict[int, list[Tuple[int, str]]]:
        data = defaultdict(list)
        for u in self.mt_tree.nodes:
            for _, v, d in self.mt_tree.edges(u, data=True):
                data[u].append((v, d['label']))
        return data

    @classmethod
    def from_message_type(cls, mt: Type):
        return cls(nx.DiGraph(), mt_tree=message_type_to_tree(mt))

    def extend_m_tree(self, from_node: int = None):
        # TODO implement placeholder
        # TODO customize <DictKey>
        # TODO add dotpath

        if len(self.m_tree.nodes) == 0:
            # TODO relax this
            child_attr = {
                "label": self.mt_tree.nodes[0]['label'],
                "type": self.mt_tree.nodes[0]['type'],
                "type_string": self.mt_tree.nodes[0]['type_string'],
                "tot": self.mt_tree.nodes[0]["tot"],
                "map_to_mt": 0,
            }
            assert self.mt_tree.nodes[0]["tot"] == TypeOfType.Ord
            self.m_tree.add_node(0, **child_attr)
            return

        assert len(self.m_tree.nodes) > 0
        assert from_node in self.m_tree.nodes

        from_node_mt = self.m_tree.nodes[from_node]['map_to_mt']
        from_node_mt_data = self.mt_tree.nodes[from_node_mt]
        from_node_mt_tot = from_node_mt_data['tot']
        from_node_mt_tot: TypeOfType

        # if the mapped node is a literal, do nothing
        if from_node_mt_tot in (TypeOfType.Literal, TypeOfType.OptionalLiteral, TypeOfType.OrdEnum):
            return

        # otherwise add all children
        if from_node_mt_tot in (
                TypeOfType.Ord, TypeOfType.DictOrd, TypeOfType.DictLiteral, TypeOfType.ListOrd, TypeOfType.ListLiteral
        ):
            for mt_child, mt_edge_label in self.children_and_names_mt[from_node_mt]:
                # check on List
                if from_node_mt_tot in (TypeOfType.ListOrd, TypeOfType.ListLiteral):
                    existing_children = [v for _, v in self.m_tree.out_edges(from_node)]
                    edge_label = len(existing_children)
                    assert len(self.children_and_names_mt[from_node_mt]) == 1
                    assert "<ListIndex>" in mt_edge_label
                    assert "<ListIndex>" in self.mt_tree.nodes[mt_child]['dotpath']
                elif from_node_mt_tot in (TypeOfType.ListOrd, TypeOfType.ListLiteral):
                    existing_children = [v for _, v in self.m_tree.out_edges(from_node)]
                    edge_label = f"<DictKey: {len(existing_children)}>"
                    assert len(self.children_and_names_mt[from_node_mt]) == 1
                    assert "<DictKey>" in mt_edge_label
                    assert "<DictKey>" in self.mt_tree.nodes[mt_child]['dotpath']
                else:
                    edge_label = mt_edge_label

                child = len(self.m_tree)
                child_attr = {
                    "label": self.mt_tree.nodes[mt_child]['label'],
                    "type": self.mt_tree.nodes[mt_child]['type'],
                    "type_string": self.mt_tree.nodes[mt_child]['type_string'],
                    "tot": self.mt_tree.nodes[mt_child]["tot"],
                    "map_to_mt": mt_child,
                }
                self.m_tree.add_node(child, **child_attr)
                self.m_tree.add_edge(from_node, child, label=edge_label)
            return

        raise TypeError(f"unexpected tot: {from_node_mt_tot}")
