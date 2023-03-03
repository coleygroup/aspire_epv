from copy import deepcopy
from typing import Type, Any, Union

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import html, Input, Output, State, dcc, ctx, ALL, no_update
from dash import register_page, get_app, ClientsideFunction

from cyto_app.cyto_config import *
from cyto_app.cyto_config import CYTO_STYLE_SHEET_MTT
from cyto_app.cyto_elements import cyto_to_mot, mot_to_cyto_element_list
from cyto_app.fixtures import SampleReactionInstance
from ord_tree.mot import get_mot, MotEleAttr, PT_STATES, \
    pt_extend_node, pt_detach_node, pt_remove_node, mot_get_path, get_literal_nodes, PT_PLACEHOLDER
from ord_tree.mtt import OrdEnumClasses
from ord_tree.utils import import_string, NodePathDelimiter

register_page(__name__, path="/mot", description="Prototype")
cyto.load_extra_layouts()
app = get_app()

MOT_CYTO_LAYOUT_OPTIONS = {
    'name': 'dagre',
    'nodeDimensionsIncludeLabels': True,
    # 'animate': True,
    # 'animationDuration': 1000,
    'align': 'UL',
}


def get_init_elements():
    init_mot = get_mot(SampleReactionInstance)
    return mot_to_cyto_element_list(init_mot)


# define components
# TODO cytoscape can set `cy.selectionType` to be 'single'
COMPONENT_CYTO_MOT = cyto.Cytoscape(
    id=DASH_CID_MOT_CYTO,
    autoRefreshLayout=False,
    zoomingEnabled=True,
    maxZoom=2,
    minZoom=0.05,
    layout=MOT_CYTO_LAYOUT_OPTIONS,
    style={'width': '100%', 'height': '100%', 'min-height': '300px'},
    stylesheet=deepcopy(CYTO_STYLE_SHEET_MTT),
    elements=get_init_elements(),
)

# client side dummies
cs_dummies = [
    html.Div(id="mot-dummy-0", style={'display': 'none'}),
    html.Div(id="mot-dummy-1", style={'display': 'none'}),
    html.Div(id="mot-dummy-2", style={'display': 'none'}),
    html.Div(id="mot-dummy-3", style={'display': 'none'}),
]

# page layout
layout = html.Div(
    [
        *cs_dummies,
        dcc.Store(id=DASH_CID_MOT_STORE_LIVE),
        dcc.Store(id=DASH_CID_MOT_STORE_LAYOUT_OPTIONS, data=MOT_CYTO_LAYOUT_OPTIONS),
        dbc.Row(
            [
                dbc.Card(
                    [
                        COMPONENT_CYTO_MOT,
                        html.Div(
                            [
                                # TODO implement
                                dbc.Button("Download JSON", id=DASH_CID_MOT_BTN_DOWNLOAD, class_name="mx-1 mt-3",
                                           disabled=True),
                                # TODO implement
                                dbc.Button("Save to DB", id=DASH_CID_MOT_BTN_SAVETODB, class_name="mx-1 mt-3",
                                           disabled=True),
                            ],
                            className="text-center"
                        ),
                    ],
                    className="col-lg-8",
                    style={'height': 'calc(100vh - 100px)'},  # minus header bar height
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                # TODO Layout may be made display=none
                                dbc.Button("Layout", id=DASH_CID_MOT_BTN_RELOAD_LAYOUT, class_name="mx-1 mt-3",
                                           n_clicks=0),
                                dbc.Button("Fit", id=DASH_CID_MOT_BTN_CYTO_FIT, class_name="mx-1 mt-3", n_clicks=0),
                                dbc.Button("Center", id=DASH_CID_MOT_BTN_CYTO_CENTER_SELECTED,
                                           class_name="mx-1 mt-3", n_clicks=0),
                            ],
                            className="text-center"
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=DASH_CID_MOT_EDITABLE_PATH_SELECTOR,
                                    placeholder="Select editable path...",
                                    className="mt-1",
                                    optionHeight=100,
                                ),
                            ],
                            className="mt-3"
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
    Output(DASH_CID_MOT_EDITABLE_PATH_SELECTOR, 'options'),
    Input(DASH_CID_MOT_CYTO, 'elements'),
)
def update_path_selector_options(elements):
    mot = cyto_to_mot(elements)
    editable_nodes = []
    editable_edges = []
    for n, d in mot.nodes(data=True):
        if d['mot_can_edit']:
            editable_nodes.append({"label": mot_get_path(mot, n, arrow=True), "value": str(n)})
    for u, v, d in mot.edges(data=True):
        if d['mot_can_edit']:
            label = f"S: {mot_get_path(mot, u, arrow=True)} R: {d['mot_value']}"
            editable_edges.append({"label": label, "value": str((u, v))})
    return editable_nodes + editable_edges


@app.callback(
    Output(DASH_CID_MOT_CYTO, 'elements'),
    Output(DASH_CID_MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    Output(DASH_CID_MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),

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

    Input({'type': DASH_CID_MOT_SWITCH_SHOW_HIDE_BRANCH, 'index': ALL}, 'value'),
    State({'type': DASH_CID_MOT_SWITCH_SHOW_HIDE_BRANCH, 'index': ALL}, 'id'),

    State(DASH_CID_MOT_CYTO, 'elements'),
    State(DASH_CID_MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    State(DASH_CID_MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
    prevent_initial_call=True,
)
def update_cyto_elements(
        state_values, state_ids,
        value_values, value_ids,
        to_extend_btn_n_clicks, to_extend_btn_ids,
        to_detach_btn_n_clicks, to_detach_btn_ids,
        to_delete_btn_n_clicks, to_delete_btn_ids,
        to_show_hide_branch_switches, to_show_hide_branch_ids,
        current_elements,
        current_n_clicks_reload_layout,
        current_n_clicks_center,
):
    triggered_cids = []
    triggered_types = []
    for it in ctx.triggered_prop_ids.values():
        triggered_cids.append(it['index'])
        triggered_types.append(it['type'])

    if len(triggered_types) != 1:
        return no_update

    assert len(set(triggered_cids)) == 1
    triggered_cid = triggered_cids[0]  # the int node_id of mot

    triggered_type = triggered_types[0]

    def is_did_node(did: str):
        if "," in did:
            return False
        return True

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
            # TODO DRY
            edge_attrs = current_elements[cid_to_elst_index[triggered_cid]]['data']['ele_attrs']
            edge_ele = current_elements[cid_to_elst_index[triggered_cid]]
            edge_attrs[field] = cid_to_set_value[triggered_cid]
            if edge_attrs['mot_state'] == PT_PLACEHOLDER:
                add_class = CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS[1:]
                minus_class = CYTO_MESSAGE_EDGE_PRESET_CLASS[1:]
            else:
                add_class = CYTO_MESSAGE_EDGE_PRESET_CLASS[1:]
                minus_class = CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS[1:]
            if add_class not in edge_ele['classes']:
                edge_ele['classes'] += " " + add_class
                edge_ele['classes'] = edge_ele['classes'].replace(minus_class, "")
            # current_elements = mot_to_cyto_element_list(
            #     cyto_to_mot(current_elements))  # this also re-derives cyto classes
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

            node_ele = current_elements[cid_to_elst_index[triggered_cid]]
            node_attrs = node_ele['data']['ele_attrs']
            node_attrs[field] = cid_to_set_value[triggered_cid]
            if node_attrs['mot_state'] == PT_PLACEHOLDER:
                add_class = CYTO_MESSAGE_NODE_LITERAL_PLACEHOLDER_CLASS[1:]
                minus_class = CYTO_MESSAGE_NODE_LITERAL_PRESET_CLASS[1:]
            else:
                add_class = CYTO_MESSAGE_NODE_LITERAL_PRESET_CLASS[1:]
                minus_class = CYTO_MESSAGE_NODE_LITERAL_PLACEHOLDER_CLASS[1:]
            if add_class not in node_ele['classes']:
                node_ele['classes'] += " " + add_class
                node_ele['classes'] = node_ele['classes'].replace(minus_class, "")
            # current_elements = mot_to_cyto_element_list(
            #     cyto_to_mot(current_elements))  # this also re-derives cyto classes

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
                current_n_clicks_reload_layout += 1
                current_n_clicks_center += 1

        # TODO DRY
        elif triggered_type == DASH_CID_MOT_SWITCH_SHOW_HIDE_BRANCH:
            cid_to_switch_values = dict(
                zip([si['index'] for si in to_show_hide_branch_ids], to_show_hide_branch_switches))
            target_node_id = triggered_cid
            current_mot = cyto_to_mot(current_elements)
            desc = nx.descendants(current_mot, target_node_id)
            hide_nodes = []
            reveal_nodes = []
            if 'Hide Branch' in cid_to_switch_values[triggered_cid]:
                hide_nodes += [*desc]
            else:
                reveal_nodes += [*desc]
            if 'Show Branch Only' in cid_to_switch_values[triggered_cid]:
                hide_nodes += [n for n in current_mot.nodes if n not in desc and n != target_node_id]
            else:
                reveal_nodes += [n for n in current_mot.nodes if n not in desc and n != target_node_id]
            for e in current_elements:
                if e['group'] == 'nodes':
                    if int(e['data']['id']) in hide_nodes:
                        e['classes'] = e['classes'].replace(CYTO_MESSAGE_NODE_TMP_HIDE[1:], "")
                        e['classes'] += " " + CYTO_MESSAGE_NODE_TMP_HIDE[1:]
                    if int(e['data']['id']) in reveal_nodes:
                        e['classes'] = e['classes'].replace(CYTO_MESSAGE_NODE_TMP_HIDE[1:], "")

    # TODO no sure if this is a bug: reload_layout and center got triggered even n_clicks do not change
    return current_elements, current_n_clicks_reload_layout, current_n_clicks_center


@app.callback(
    Output(DASH_CID_MOT_DIV_EDITOR, 'children'),
    Input(DASH_CID_MOT_CYTO, 'selectedNodeData'),
    Input(DASH_CID_MOT_CYTO, 'selectedEdgeData'),
    State(DASH_CID_MOT_CYTO, "elements"),
)
def update_element_editor(node_data, edge_data, elements):
    if node_data is None:
        node_data = []
    if edge_data is None:
        edge_data = []

    if len(node_data) + len(edge_data) == 0:
        return []

    mot = cyto_to_mot(elements)
    cards_node = get_cards_from_selected_nodes(node_data, mot)
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
    editor = dbc.ListGroupItem(
        [
            html.H6(relation_to_parent),
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
                                       id={'type': DASH_CID_MOT_BTN_PT_EXTEND, 'index': node_id}, ),
                            dbc.Button("Detach", outline=True, color='primary', className="mx-2",
                                       id={'type': DASH_CID_MOT_BTN_PT_DETACH, 'index': node_id}, ),
                            dbc.Button("Delete", outline=True, color='primary', className="mx-2",
                                       id={'type': DASH_CID_MOT_BTN_PT_DELETE, 'index': node_id}, ),
                        ], className="mt-1 text-center"
                    ),
                    html.Div(
                        [
                            dbc.Checklist(
                                options=[
                                    {"label": "Hide Branch", "value": 'Hide Branch'},
                                    {"label": "Show Branch Only", "value": 'Show Branch Only'},
                                ],
                                input_class_name="mx-2",
                                label_class_name="mx-2",
                                class_name="mtt-switch",
                                value=[],
                                id={'type': DASH_CID_MOT_SWITCH_SHOW_HIDE_BRANCH, 'index': node_id},
                                switch=True,
                            ),
                        ], className="mt-3 text-center"
                    ),

                ],
                className="text-center"
            ),
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
            list_items.append(dbc.Alert("This is not a literal node.", color="warning", className="text-center mt-3"))

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


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_run_layout',
    ),
    Output('mot-dummy-0', 'children'),
    Input(DASH_CID_MOT_STORE_LAYOUT_OPTIONS, 'data'),
    Input(DASH_CID_MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_center_selected',
    ),
    Output('mot-dummy-1', 'children'),
    Input(DASH_CID_MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_fit',
    ),
    Output('mot-dummy-2', 'children'),
    Input(DASH_CID_MOT_BTN_CYTO_FIT, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_select_element',
    ),
    Output('mot-dummy-3', 'children'),
    Input(DASH_CID_MOT_EDITABLE_PATH_SELECTOR, 'value'),
)
