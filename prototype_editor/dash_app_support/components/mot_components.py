from typing import Type, Any

import dash_bootstrap_components as dbc
import networkx as nx
from dash import html, dcc

from ord_tree.mot import MotEleAttr, mot_get_path, get_literal_nodes, PT_PLACEHOLDER
from ord_tree.mtt import OrdEnumClasses
from ord_tree.utils import import_string, NodePathDelimiter, enum_class_to_options


# page component ids
class PCI:
    # intermediates
    MOT_STORE_EDITABLE_NODES = "MOT_STORE_EDITABLE_NODES"
    MOT_STORE_EDITABLE_EDGES = "MOT_STORE_EDITABLE_EDGES"
    MOT_STORE_ALL_NODES = "MOT_STORE_ALL_NODES"
    MOT_STORE_ALL_EDGES = "MOT_STORE_ALL_EDGES"
    MOT_STORE_PROTOTYPE_DOC = "MOT_STORE_PROTOTYPE_DOC"
    MOT_STORE_INIT_PROTOTYPE_DOC = "MOT_STORE_INIT_PROTOTYPE_DOC"
    MOT_STORE_UPDATE_ELEMENTS = "MOT_STORE_UPDATE_ELEMENTS"

    # main cyto
    MOT_CYTO = "MOT_CYTO"

    # download the current prototype
    MOT_DOWNLOAD = "MOT_DOWNLOAD"

    # log box
    MOT_EDITOR_LOG_BTN = "MOT_EDITOR_LOG_BTN"
    MOT_EDITOR_LOG_TEXTAREA = "MOT_EDITOR_LOG_TEXTAREA"
    MOT_EDITOR_LOG_COLLAPSE = "MOT_EDITOR_LOG_COLLAPSE"

    # instructions
    MOT_INSTRUCTION_BTN = "MOT_INSTRUCTION_BTN"
    MOT_INSTRUCTION_COLLAPSE = "MOT_INSTRUCTION_COLLAPSE"

    # meta data
    MOT_METADATA_BTN = "MOT_METADATA_BTN"
    MOT_METADATA_COLLAPSE = "MOT_METADATA_COLLAPSE"

    # navigator
    MOT_DROPDOWN_NAV_BTN = "MOT_DROPDOWN_NAV_BTN"
    MOT_DROPDOWN_NAV_COLLAPSE = "MOT_DROPDOWN_NAV_COLLAPSE"
    MOT_DROPDOWN_NAV_SELECTOR_0 = "MOT_DROPDOWN_NAV_SELECTOR_0"
    MOT_DROPDOWN_NAV_SELECTOR_1 = "MOT_DROPDOWN_NAV_SELECTOR_1"
    MOT_DROPDOWN_NAV_SELECTOR_2 = "MOT_DROPDOWN_NAV_SELECTOR_2"
    MOT_DROPDOWN_NAV_PAN_BTN = "MOT_DROPDOWN_NAV_PAN_BTN"

    # save functions
    MOT_SAVE_BTN = "MOT_SAVE_BTN"
    MOT_SAVE_COLLAPSE = "MOT_SAVE_COLLAPSE"
    MOT_SAVE_NAME_INPUT = "MOT_SAVE_NAME_INPUT"
    MOT_SAVE_VERSION_INHERIT = "MOT_SAVE_VERSION_INHERIT"
    MOT_SAVE_VERSION_INPUT = "MOT_SAVE_VERSION_INPUT"

    # the div holds all inputs
    MOT_DIV_EDITOR = "CID_MOT_DIV_EDITOR"
    # under this div
    MOT_INPUT_PT_ELEMENT_STATE = "CID_MOT_INPUT_PT_ELEMENT_STATE"
    MOT_INPUT_PT_ELEMENT_VALUE = "CID_MOT_INPUT_PT_ELEMENT_VALUE"
    MOT_BTN_PT_EXTEND = "CID_MOT_BTN_PT_EXTEND"
    MOT_BTN_PT_DETACH = "CID_MOT_BTN_PT_DETACH"
    MOT_BTN_PT_DELETE = "CID_MOT_BTN_PT_DELETE"

    MOT_BTN_PT_UNION_OPEN_MODAL = "MOT_BTN_PT_UNION_OPEN_MODAL"
    MOT_BTN_PT_UNION = "MOT_BTN_PT_UNION"
    MOT_LIST_GROUP_PT_UNION = "MOT_LIST_GROUP_PT_UNION"
    MOT_MODAL_UNION = "MOT_MODAL_UNION"

    # buttons to save
    MOT_BTN_DOWNLOAD = "CID_MOT_BTN_DOWNLOAD"
    MOT_BTN_SAVETODB = "CID_MOT_BTN_SAVETODB"

    # view port buttons
    MOT_BTN_SHOW_RELATIONS = "MOT_BTN_SHOW_RELATIONS"
    MOT_BTN_SHOW_ALL = "MOT_BTN_SHOW_ALL"
    MOT_BTN_HIDE_NON_SUCCESSORS = "MOT_BTN_HIDE_NON_SUCCESSORS"
    MOT_BTN_RELOAD_LAYOUT = "CID_MOT_BTN_RELOAD_LAYOUT"
    MOT_BTN_CYTO_FIT = "CID_MOT_BTN_CYTO_FIT"
    MOT_BTN_CYTO_CENTER_SELECTED = "CID_MOT_BTN_CYTO_CENTER_SELECTED"

    # MOT_DIV_EDITOR_ELEMENT_STATE = "CID_MOT_DIV_EDITOR_ELEMENT_STATE"
    # MOT_SWITCHES = "CID_MOT_SWITCHES"
    # MOT_EDITABLE_ID_SELECTOR = "CID_MOT_EDITABLE_ID_SELECTOR"
    # MOT_INIT_SELECTOR = "CID_MOT_INIT_SELECTOR"
    #
    # MOT_BTN_PT_SHOWONLY = "CID_MOT_BTN_PT_SHOWONLY"
    # MOT_STORE_INIT = "CID_MOT_STORE_INIT"


def get_literal_node_value_input(node_class: Type, node_value: Any, cid: dict[str, Any]):
    if node_class == str:
        # value_input = dbc.Input(type='text', value=node_value, id=cid)
        value_input = dbc.Textarea(value=node_value, id=cid)
    elif node_class == bool:
        value_input = dbc.InputGroupText(
            dbc.Switch(value=node_value, id=cid, className="position-absolute top-50 start-50 translate-middle"),
            className="position-relative flex-fill")
    elif node_class in (int, float):
        value_input = dbc.Input(type='number', value=node_value, id=cid)
    elif node_class in OrdEnumClasses:
        value_input = dbc.Select(options=enum_class_to_options(node_class),
                                 value=node_value, id=cid)
    elif node_class == bytes:
        # TODO make this better
        value_input = dbc.Textarea(value=str(node_value), id=cid)
    else:
        raise TypeError(f"illegal literal class: {node_class}")
    return value_input


def get_non_literal_editor_node(node_id: int, node_state: str, node_class: Type, ):
    editor = dbc.ListGroupItem(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Is placeholder:"),
                    dbc.InputGroupText(dbc.Checkbox(
                        id={
                            'type': PCI.MOT_INPUT_PT_ELEMENT_STATE,
                            'index': node_id
                        }, value=node_state == PT_PLACEHOLDER
                    )),
                ]
            ),
        ],
    )
    return editor


def get_literal_editor_node(node_id: int, node_state: str, node_value: Any, node_class: Type,
                            relation_to_parent: str, ):
    editor = dbc.ListGroupItem(
        [
            html.H6(relation_to_parent),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Is placeholder:"),
                    dbc.InputGroupText(dbc.Checkbox(
                        id={
                            'type': PCI.MOT_INPUT_PT_ELEMENT_STATE,
                            'index': node_id
                        }, value=node_state == PT_PLACEHOLDER
                    )),
                    get_literal_node_value_input(node_class, node_value,
                                                 {'type': PCI.MOT_INPUT_PT_ELEMENT_VALUE, 'index': node_id}
                                                 )
                ]
            ),
        ],
    )
    return editor


def get_cards_from_selected_nodes(node_data, mot: nx.DiGraph):
    cards = []
    literal_nodes = get_literal_nodes(mot)
    for node_d in node_data:
        node_id_str = node_d['id']
        node_id = int(node_id_str)
        # TODO this is a dirty fix for the bug where `node_id` doesn't exist after a deletion is made to cyto elements
        if node_id not in mot.nodes:
            continue

        # buttons bound to the current node
        lines = [
            html.Div(
                [
                    html.Div(
                        [
                            dbc.Button("Extend", outline=True, color='primary', className="mx-2",
                                       id={'type': PCI.MOT_BTN_PT_EXTEND, 'index': node_id}, ),
                            dbc.Button("Detach", outline=True, color='primary', className="mx-2",
                                       id={'type': PCI.MOT_BTN_PT_DETACH, 'index': node_id}, ),
                            dbc.Button("Delete", outline=True, color='primary', className="mx-2",
                                       id={'type': PCI.MOT_BTN_PT_DELETE, 'index': node_id}, ),
                            dbc.Button("Union", outline=True, color='primary', className="mx-2",
                                       id={'type': PCI.MOT_BTN_PT_UNION_OPEN_MODAL, 'index': node_id}, n_clicks=0),
                            dbc.Modal(
                                [dbc.ModalHeader('Union with an existing prototype'), dbc.ModalBody(
                                    dbc.ListGroup(id={'type': PCI.MOT_LIST_GROUP_PT_UNION, 'index': node_id}))],
                                id={'type': PCI.MOT_MODAL_UNION, 'index': node_id},
                                is_open=False
                            ),
                        ],
                        className="mt-1 text-center",
                    ),
                ],
                className="text-center", ),
        ]

        node_attr = mot.nodes[node_id]
        node_attr: MotEleAttr
        node_class = import_string(node_attr['mot_class_string'])

        path = mot_get_path(mot, node_id)
        path = dcc.Markdown(
            " &rarr; ".join([f"_{p}_" for p in path.split(NodePathDelimiter)])
        )

        item_path = dbc.ListGroupItem([html.H6("Path"), path])
        list_items = [item_path, ]

        # if literal node, show editor
        if node_id in literal_nodes:
            u, v, edge_attr = list(mot.in_edges(node_id, data=True))[0]
            literal_editor = get_literal_editor_node(
                node_id, node_attr['mot_state'], node_attr['mot_value'], node_class,
                relation_to_parent=edge_attr['mot_value'],
            )
            list_items.append(literal_editor)
        else:
            non_literal_editor = get_non_literal_editor_node(
                node_id, node_attr['mot_state'], node_class,
            )
            list_items.append(non_literal_editor)
            # list_items.append(dbc.Alert("This is not a literal node.", color="warning", className="text-center mt-3"))

        list_group = dbc.ListGroup(list_items, className="mt-3")
        lines.append(list_group)
        card = dbc.Card(
            [
                dbc.CardHeader([html.B(node_class.__name__, className="text-primary"), ]),
                dbc.CardBody(lines),
            ],
            className="mt-3"
        )
        cards.append(card)
    return cards


def get_literal_editor_edge(edge_header: str, u_id: int, v_id: int, edge_state: str, edge_value: Any):
    editor = html.Div(
        [
            dbc.InputGroup(dbc.InputGroupText(edge_header, className="w-100 d-inline bg-dark text-white")),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Is placeholder:"),
                    dbc.InputGroupText(dbc.Checkbox(
                        id={
                            'type': PCI.MOT_INPUT_PT_ELEMENT_STATE,
                            'index': f"{u_id} {v_id}"
                        }, value=edge_state == PT_PLACEHOLDER
                    )),
                    dbc.Textarea(
                        value=edge_value,
                        id={
                            'type': PCI.MOT_INPUT_PT_ELEMENT_VALUE,
                            'index': f"{u_id} {v_id}"
                        }
                    ),
                ]
            ),
        ],
        className="mt-3"
    )
    return editor


def get_cards_from_selected_edges(edge_data, mot: nx.DiGraph):
    cards = []
    for edge_d in edge_data:
        u_id_str = edge_d['source']
        v_id_str = edge_d['target']
        u_id = int(u_id_str)
        v_id = int(v_id_str)
        u_path = mot_get_path(mot, u_id)
        v_path = mot_get_path(mot, v_id)

        # TODO this is a dirty fix for the bug where `node_id` doesn't exist after a deletion is made to cyto elements
        try:
            edge_attr = mot.edges[(u_id, v_id)]
        except KeyError:
            continue

        lines = []
        edge_attr: MotEleAttr
        # if dictkey node, show editor
        if edge_attr['mot_can_edit']:
            literal_editor = get_literal_editor_edge(
                v_path.replace(u_path, ""),
                u_id, v_id, edge_state=edge_attr['mot_state'], edge_value=edge_attr['mot_value']
            )
            lines.append(literal_editor)
        else:
            lines.append(dbc.Alert("This is not an editable edge.", color="warning", className="text-center mt-3"))

        card = dbc.Card(
            [
                dbc.CardHeader([html.B("TO: " + v_path, className="text-primary"), ]),
                dbc.CardBody(lines),
            ],
            className="mt-3"
        )
        cards.append(card)
    return cards

# def derive_relation(elements, mot=None):
#     if mot is None:
#         mot = cyto_to_mot(elements)
#     for e in elements:
#         try:
#             nid = int(e['data']['id'])
#         except ValueError:
#             continue
#         assert nid in mot.nodes
#         parents = list(mot.predecessors(nid))
#         if len(parents) == 1:
#             v = parents[0]
#             e['data']['relation'] = mot.edges[(v, nid)]['mot_value']
#         else:
#             e['data']['relation'] = RootNodePath
#     return elements
