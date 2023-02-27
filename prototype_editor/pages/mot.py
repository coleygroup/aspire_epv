from copy import deepcopy
from typing import Type, Any, Union

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import html, Input, Output, State, dcc, ctx, ALL
from dash import register_page, get_app

from cyto_app.cyto_config import *
from cyto_app.cyto_config import CYTO_STYLE_SHEET_MTT
from cyto_app.cyto_elements import cyto_to_mot, mot_to_cyto_element_list
from cyto_app.fixtures import SampleReactionInstance
from ord_tree.mot import get_mot, MotEleAttr, PT_STATES, \
    pt_extend_node, pt_detach_node, pt_remove_node, mot_get_path
from ord_tree.mtt import OrdEnumClasses, BuiltinLiteralClasses
from ord_tree.utils import import_string

register_page(__name__, path="/mot", description="Prototype")
cyto.load_extra_layouts()
app = get_app()


def get_init_elements():
    init_mot = get_mot(SampleReactionInstance)
    return mot_to_cyto_element_list(init_mot)


# define components
COMPONENT_CYTO_MOT = cyto.Cytoscape(
    id=DASH_CID_MOT_CYTO,
    zoomingEnabled=True,
    maxZoom=2,
    minZoom=0.5,
    layout={
        'name': 'dagre',
        'nodeDimensionsIncludeLabels': True,
        'animate': True,
        'animationDuration': 1000,
        'align': 'UL',
    },
    style={'width': '100%', 'height': '100%', 'min-height': '600px'},
    stylesheet=deepcopy(CYTO_STYLE_SHEET_MTT),
    elements=get_init_elements(),
)

# page layout
layout = html.Div(
    [
        dcc.Store(id=DASH_CID_MOT_STORE_LIVE),
        dbc.Row(
            [
                dbc.Card(
                    COMPONENT_CYTO_MOT,
                    className="col-lg-8"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H6("ORD message prototype", className="text-center"),
                            ],
                            className="mb-3 mt-3"
                        ),
                        dbc.Checklist(
                            options=[
                                {"label": "Hide Literals", "value": 'Hide Literals'},
                                # TODO implement
                                {"label": "Placeholder Only", "value": 'Placeholder Only', "disabled": True},
                            ],
                            input_class_name="mx-2",
                            label_class_name="mx-2",
                            class_name="mtt-switch",
                            value=['Hide Literals'],
                            id=DASH_CID_MOT_SWITCHES,
                            switch=True,
                        ),
                        html.Div(
                            [
                                # TODO implement
                                dbc.Button("Download JSON", id=DASH_CID_MOT_BTN_DOWNLOAD, class_name="mx-3 mt-3",
                                           disabled=True),
                                # TODO implement
                                dbc.Button("Save to DB", id=DASH_CID_MOT_BTN_SAVETODB, class_name="mx-3 mt-3",
                                           disabled=True),
                            ],
                            className="text-center"
                        ),
                        html.Div(id=DASH_CID_MOT_DIV_EDITOR, className="mt-3"),
                    ],
                    className="col-lg-4",
                ),
            ]
        )

    ]
)


@app.callback(
    Output(DASH_CID_MOT_CYTO, 'stylesheet'),
    Input(DASH_CID_MOT_SWITCHES, "value"),
)
def update_cyto_stylesheet(switch_values):
    style_sheet = deepcopy(CYTO_STYLE_SHEET_MTT)
    if 'Hide Literals' in switch_values:
        style_sheet += [
            {
                'selector': CYTO_MESSAGE_NODE_LITERAL_CLASS,
                'style': {
                    'display': 'none',
                    'visibility': 'hidden',
                }
            }
        ]
    return style_sheet


@app.callback(
    Output(DASH_CID_MOT_CYTO, 'elements'),

    # see https://dash.plotly.com/pattern-matching-callbacks
    Input({'type': DASH_CID_MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'value'),
    State({'type': DASH_CID_MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'id'),

    Input({'type': DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'value'),
    State({'type': DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'id'),

    Input({'type': DASH_CID_MOT_BTN_PT_EXTEND, 'index': ALL}, 'n_clicks'),
    State({'type': DASH_CID_MOT_BTN_PT_EXTEND, 'index': ALL}, 'id'),

    Input({'type': DASH_CID_MOT_BTN_PT_DETACH, 'index': ALL}, 'n_clicks'),
    State({'type': DASH_CID_MOT_BTN_PT_DETACH, 'index': ALL}, 'id'),

    Input({'type': DASH_CID_MOT_BTN_PT_DELETE, 'index': ALL}, 'n_clicks'),
    State({'type': DASH_CID_MOT_BTN_PT_DELETE, 'index': ALL}, 'id'),

    State(DASH_CID_MOT_CYTO, 'elements'),
    # prevent_initial_call=True,
)
def update_cyto_elements(
        state_values, state_ids, value_values, value_ids,
        to_extend_btn_n_clicks, to_extend_btn_ids,
        to_detach_btn_n_clicks, to_detach_btn_ids,
        to_delete_btn_n_clicks, to_delete_btn_ids,
        current_elements,
):
    try:
        triggered_type = ctx.triggered_id['type']
    except TypeError:
        return current_elements

    def is_did_node(did: str):
        if "," in did:
            return False
        return True

    triggered_cid = ctx.triggered_id['index']  # the int node_id of mot
    triggered_cid: Union[int, str]
    if isinstance(triggered_cid, str):
        assert len(triggered_cid) > 1 and " " in triggered_cid  # edge triggered
        if triggered_type in (DASH_CID_MOT_INPUT_PT_ELEMENT_STATE, DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE):
            cid_to_elst_index = {e['data']['id'][1:-1].replace(",", ""): i for i, e in enumerate(current_elements) if
                                 not is_did_node(e['data']['id']) and e['group'] == 'edges'}
            if triggered_type == DASH_CID_MOT_INPUT_PT_ELEMENT_STATE:
                cid_to_set_value = dict(zip([si['index'] for si in state_ids], state_values))
                field = 'mot_state'
            elif triggered_type == DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE:
                cid_to_set_value = dict(zip([si['index'] for si in value_ids], value_values))
                field = 'mot_value'
            else:
                raise ValueError(f"unknown triggered type: {triggered_type}")
            current_elements[cid_to_elst_index[triggered_cid]]['data']['ele_attrs'][field] = cid_to_set_value[
                triggered_cid]
            current_elements = mot_to_cyto_element_list(
                cyto_to_mot(current_elements))  # this also re-derives cyto classes
    else:
        if triggered_type in (DASH_CID_MOT_INPUT_PT_ELEMENT_STATE, DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE):
            cid_to_elst_index = {int(e['data']['id']): i for i, e in enumerate(current_elements) if
                                 is_did_node(e['data']['id']) and e['group'] == 'nodes'}
            if triggered_type == DASH_CID_MOT_INPUT_PT_ELEMENT_STATE:
                cid_to_set_value = dict(zip([si['index'] for si in state_ids], state_values))
                field = 'mot_state'
            elif triggered_type == DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE:
                cid_to_set_value = dict(zip([si['index'] for si in value_ids], value_values))
                field = 'mot_value'
            else:
                raise ValueError(f"unknown triggered type: {triggered_type}")
            current_elements[cid_to_elst_index[triggered_cid]]['data']['ele_attrs'][field] = cid_to_set_value[
                triggered_cid]
            current_elements = mot_to_cyto_element_list(
                cyto_to_mot(current_elements))  # this also re-derives cyto classes

        elif triggered_type in (DASH_CID_MOT_BTN_PT_EXTEND, DASH_CID_MOT_BTN_PT_DELETE, DASH_CID_MOT_BTN_PT_DETACH):
            if triggered_type == DASH_CID_MOT_BTN_PT_EXTEND:
                btn_ids = to_extend_btn_ids
                btn_n_clicks = to_extend_btn_n_clicks
                pt_operation = pt_extend_node
            elif triggered_type == DASH_CID_MOT_BTN_PT_DELETE:
                btn_ids = to_delete_btn_ids
                btn_n_clicks = to_delete_btn_n_clicks
                pt_operation = pt_remove_node
            elif triggered_type == DASH_CID_MOT_BTN_PT_DETACH:
                btn_ids = to_detach_btn_ids
                btn_n_clicks = to_detach_btn_n_clicks
                pt_operation = pt_detach_node
            else:
                raise TypeError
            cid_to_n_clicks = dict(zip([si['index'] for si in btn_ids], btn_n_clicks))
            if cid_to_n_clicks[triggered_cid]:
                target_node_id = triggered_cid
                current_mot = cyto_to_mot(current_elements)
                pt_operation(current_mot, target_node_id, inplace=True)
                current_elements = mot_to_cyto_element_list(current_mot)

    return current_elements


@app.callback(
    Output(DASH_CID_MOT_DIV_EDITOR, 'children'),
    Input(DASH_CID_MOT_CYTO, 'selectedNodeData'),
    Input(DASH_CID_MOT_CYTO, 'selectedEdgeData'),
    Input(DASH_CID_MOT_SWITCHES, "value"),
    Input(DASH_CID_MOT_CYTO, "elements"),
    # prevent_initial_call=True
)
def update_element_editor(node_data, edge_data, switch_values, elements):
    hide_literals = False
    if 'Hide Literals' in switch_values:
        hide_literals = True

    if node_data is None:
        node_data = []
    if edge_data is None:
        edge_data = []

    if len(node_data) + len(edge_data) == 0:
        return []

    mot = cyto_to_mot(elements)
    cards_node = get_cards_from_selected_nodes(node_data, mot, hide_literals)
    cards_edge = get_cards_from_selected_edges(edge_data, mot)
    return cards_node + cards_edge


def enum_class_to_options(enum_class):
    options = [
        {"label": e.name, "value": e.value} for e in enum_class
    ]
    return options


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


def get_literal_editor_node(node_id: int, node_state: str, node_value: Any, node_class: Type,
                            relation_to_parent: str, ):
    editor = html.Div(
        [
            dbc.InputGroup(dbc.InputGroupText(relation_to_parent, className="w-100 d-inline bg-dark text-white")),
            dbc.InputGroup(
                [
                    dbc.InputGroupText(
                        [
                            dbc.Select(
                                options=PT_STATES,
                                value=node_state,
                                id={'type': DASH_CID_MOT_INPUT_PT_ELEMENT_STATE, 'index': node_id},
                            ),
                        ]
                    ),
                    get_literal_node_value_input(node_class, node_value,
                                                 {'type': DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE, 'index': node_id}
                                                 )
                ]
            ),
        ],
        className="mt-3"
    )
    return editor


def get_cards_from_selected_nodes(node_data, mot: nx.DiGraph, hide_literals=True):
    literal_nodes = [n for n in mot.nodes if
                     import_string(mot.nodes[n]['mot_class_string']) in BuiltinLiteralClasses + OrdEnumClasses]

    cards = []
    for node_d in node_data:
        node_id_str = node_d['id']
        node_id = int(node_id_str)
        # TODO this is a dirty fix for the bug where `node_id` doesn't exist after a deletion is made to cyto elements
        try:
            node_attr = mot.nodes[node_id]
        except KeyError:
            continue
        node_attr: MotEleAttr
        node_class = import_string(node_attr['mot_class_string'])

        # buttons bound to the current node
        lines = [
            html.Div(
                dbc.ButtonGroup(
                    [
                        dbc.Button("Extend", outline=True, color='primary',
                                   id={'type': DASH_CID_MOT_BTN_PT_EXTEND, 'index': node_id}, ),
                        dbc.Button("Detach", outline=True, color='primary',
                                   id={'type': DASH_CID_MOT_BTN_PT_DETACH, 'index': node_id}, ),
                        dbc.Button("Delete", outline=True, color='primary',
                                   id={'type': DASH_CID_MOT_BTN_PT_DELETE, 'index': node_id}, ),
                        dbc.Button("Hide", outline=True, color='primary',
                                   id={'type': DASH_CID_MOT_BTN_PT_HIDE, 'index': node_id}, ),
                        dbc.Button("ShowOnly", outline=True, color='primary',
                                   id={'type': DASH_CID_MOT_BTN_PT_SHOWONLY, 'index': node_id}, ),
                    ],
                ),
                className="text-center w-100"
            ),
        ]

        # if literal node, show editor
        if node_id in literal_nodes:
            u, v, edge_attr = list(mot.in_edges(node_id, data=True))[0]
            literal_editor = get_literal_editor_node(
                node_id, node_attr['mot_state'], node_attr['mot_value'], node_class,
                relation_to_parent=edge_attr['mot_value'],
            )
            lines.append(literal_editor)

        else:
            if not hide_literals:
                lines.append(dbc.Alert("This is not a literal node.", color="warning", className="text-center mt-3"))
            else:
                literal_children = [n for n in mot.successors(node_id) if n in literal_nodes]
                if len(literal_children) == 0:
                    lines.append(dbc.Alert("No Literal Children", color="warning", className="text-center mt-3"))
                else:
                    for literal_child in literal_children:
                        literal_child_attr = mot.nodes[literal_child]
                        literal_child_attr: MotEleAttr
                        literal_child_class = import_string(literal_child_attr['mot_class_string'])
                        _, _, literal_child_edge_attr = list(mot.in_edges(literal_child, data=True))[0]
                        literal_editor = get_literal_editor_node(
                            literal_child, literal_child_attr['mot_state'], literal_child_attr['mot_value'],
                            literal_child_class, literal_child_edge_attr['mot_value']
                        )
                        lines.append(literal_editor)

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
                    dbc.InputGroupText(
                        [
                            dbc.Select(
                                options=PT_STATES,
                                value=edge_state,
                                id={
                                    'type': DASH_CID_MOT_INPUT_PT_ELEMENT_STATE,
                                    'index': f"{u_id} {v_id}"
                                },
                            ),
                        ]
                    ),
                    dbc.Textarea(
                        value=edge_value,
                        id={
                            'type': DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE,
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

        card = dbc.Card(
            [
                dbc.CardHeader([html.B("TO: " + v_path, className="text-primary"), ]),
                dbc.CardBody(lines),
            ],
            className="mt-3"
        )
        cards.append(card)
    return cards
