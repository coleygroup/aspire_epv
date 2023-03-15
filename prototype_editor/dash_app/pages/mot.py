import datetime
import json
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from typing import Union

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_defer_js_import as dji
import dash_renderjson
import networkx as nx
from bson.json_util import ObjectId
from dash import html, Input, Output, State, dcc, ctx, ALL, no_update, get_asset_url, MATCH, register_page, get_app, \
    ClientsideFunction
from pymongo import MongoClient

from dash_app_support.components import simple_open, PCI_MOT, get_cards_from_selected_nodes, \
    get_cards_from_selected_edges, JsonTheme
from dash_app_support.cyto_config import CYTO_STYLE_SHEET_MOT, CYTO_PLACEHOLDER_CLASS, CYTO_PRESET_CLASS
from dash_app_support.cyto_elements import cyto_to_mot, mot_to_cyto_element_list, BytesDump
from dash_app_support.fixtures import SampleReactionInstance
from ord_tree.mot import get_mot, pt_extend_node, pt_detach_node, pt_remove_node, mot_get_path, pt_to_dict, \
    PT_PLACEHOLDER, PT_PRESET
from ord_tree.ord_classes import BuiltinLiteralClasses, OrdEnumClasses
from ord_tree.utils import get_root, import_string

"""
1. use server side callback to edit element attributes
2. use client side callback to edit element classes
"""

app = get_app()
register_page(__name__, path_template="/edit/<prototype_id>", description="Prototype")
cyto.load_extra_layouts()

# TODO auth
MONGO_DB = MongoClient()['ord_prototype']
COLLECTION = "prototypes"


def get_sample_elements():
    init_mot = get_mot(SampleReactionInstance)
    return mot_to_cyto_element_list(init_mot)


def get_init_doc(pid):
    mot_data = MONGO_DB[COLLECTION].find_one({"_id": ObjectId(pid)})
    return mot_data


def log_string(s):
    return f"{datetime.now()}:\n{s}\n\n"


# TODO validate prototype (all leafs literal, no oneof conflict)
# TODO pop over for loading prototypes

MOT_CYTO_LAYOUT_OPTIONS = {
    'name': 'dagre',
    'nodeDimensionsIncludeLabels': True,
    'align': 'UL',
}

# define components

# client side dummies
cs_dummies = [
    html.Div(id="mot-dummy-0", style={'display': 'none'}),
    html.Div(id="mot-dummy-1", style={'display': 'none'}),
    html.Div(id="mot-dummy-2", style={'display': 'none'}),
    html.Div(id="mot-dummy-3", style={'display': 'none'}),
    html.Div(id="mot-dummy-4", style={'display': 'none'}),
    html.Div(id="mot-dummy-5", style={'display': 'none'}),
    html.Div(id="mot-dummy-6", style={'display': 'none'}),
    html.Div(id="mot-dummy-7",
             # style={'display': 'none'}
             ),
    html.Div(id="mot-dummy-8", style={'display': 'none'}),
]


# page layout
def layout(prototype_id=None):
    init_doc = get_init_doc(prototype_id)
    init_mot = nx.node_link_graph(init_doc['node_link_data'])
    init_elements = mot_to_cyto_element_list(init_mot)
    init_metadata = {k: v for k, v in init_doc.items() if k not in ('node_link_data', '_id')}

    component_cyto_mot = cyto.Cytoscape(
        id=PCI_MOT.MOT_CYTO,
        autoRefreshLayout=False,
        zoomingEnabled=True,
        maxZoom=2,
        minZoom=0.05,
        layout=MOT_CYTO_LAYOUT_OPTIONS,
        style={'width': '100%', 'height': '100%', 'min-height': '300px'},
        stylesheet=deepcopy(CYTO_STYLE_SHEET_MOT),
        elements=init_elements,
    )

    page_layout = html.Div(
        [
            *cs_dummies,
            dji.Import(src=get_asset_url("defer_cyto.js")),
            dcc.Store(id=PCI_MOT.MOT_STORE_UPDATE_ELEMENTS),
            dcc.Store(id=PCI_MOT.MOT_STORE_INIT_PROTOTYPE_DOC, data=init_metadata),
            dcc.Store(id=PCI_MOT.MOT_STORE_PROTOTYPE_DOC),
            dcc.Store(id=PCI_MOT.MOT_STORE_EDITABLE_NODES, data=[]),
            dcc.Store(id=PCI_MOT.MOT_STORE_EDITABLE_EDGES, data=[]),
            dcc.Store(id=PCI_MOT.MOT_STORE_ALL_NODES, data=[]),
            dcc.Store(id=PCI_MOT.MOT_STORE_ALL_EDGES, data=[]),
            dcc.Download(id=PCI_MOT.MOT_DOWNLOAD),
            dbc.Row(
                [
                    dbc.Card(
                        [
                            html.Div(
                                [
                                    # TODO Layout may be made display=none
                                    dbc.Button("Show Relations", id=PCI_MOT.MOT_BTN_SHOW_RELATIONS, active=False,
                                               outline=True, n_clicks=0,
                                               color="primary",
                                               className="mx-1 mt-3"),
                                    dbc.Button("Hide Non-successors", id=PCI_MOT.MOT_BTN_HIDE_NON_SUCCESSORS,
                                               color="primary", n_clicks=0,
                                               className="mx-1 mt-3"),
                                    dbc.Button("Show All", id=PCI_MOT.MOT_BTN_SHOW_ALL,
                                               color="primary", n_clicks=0,
                                               className="mx-1 mt-3"),
                                    dbc.Button("Run Layout", id=PCI_MOT.MOT_BTN_RELOAD_LAYOUT, class_name="mx-1 mt-3",
                                               n_clicks=0),
                                    dbc.Button("Fit Graph", id=PCI_MOT.MOT_BTN_CYTO_FIT, class_name="mx-1 mt-3",
                                               n_clicks=0),
                                    dbc.Button("Center Selected", id=PCI_MOT.MOT_BTN_CYTO_CENTER_SELECTED,
                                               class_name="mx-1 mt-3", n_clicks=0),
                                ],
                                className="text-center"
                            ),
                            html.Hr(),
                            component_cyto_mot,
                        ],
                        className="col-lg-8",
                        style={'height': 'calc(100vh - 100px)'},  # minus header bar height
                    ),
                    html.Div(
                        [

                            html.Div(
                                [
                                    dbc.Button(
                                        "Editor Log",
                                        id=PCI_MOT.MOT_EDITOR_LOG_BTN,
                                        className="me-3 mt-3",
                                        color="secondary",
                                        outline=True,
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Instructions",
                                        id=PCI_MOT.MOT_INSTRUCTION_BTN,
                                        className="me-3 mt-3",
                                        color="secondary",
                                        outline=True,
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Metadata",
                                        id=PCI_MOT.MOT_METADATA_BTN,
                                        className="me-3 mt-3",
                                        color="secondary",
                                        outline=True,
                                        n_clicks=0,
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Editor Log")),
                                            dbc.ModalBody(
                                                dcc.Textarea(value=log_string(f"Loaded {prototype_id}"), disabled=True,
                                                             style={"height": "400px", "width": "100%"},
                                                             id=PCI_MOT.MOT_EDITOR_LOG_TEXTAREA),
                                            ),
                                        ],
                                        id=PCI_MOT.MOT_EDITOR_LOG_COLLAPSE,
                                        is_open=False,
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Instructions")),
                                            dbc.ModalBody(
                                                dcc.Markdown(
                                                    """
                                                    - right click a node to hide/show its successors
                                                    """
                                                ),
                                            ),

                                        ],
                                        id=PCI_MOT.MOT_INSTRUCTION_COLLAPSE,
                                        is_open=False,
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(dbc.ModalTitle("Metadata")),
                                            dbc.ModalBody(
                                                dash_renderjson.DashRenderjson(data=init_metadata, max_depth=1,
                                                                               theme=JsonTheme, invert_theme=True),
                                            ),
                                        ],
                                        id=PCI_MOT.MOT_METADATA_COLLAPSE,
                                        is_open=False,
                                    ),
                                ], className="text-center"
                            ),

                            html.Hr(),

                            html.Div(
                                [
                                    dbc.Button(
                                        "Navigator",
                                        id=PCI_MOT.MOT_DROPDOWN_NAV_BTN,
                                        className="me-3",
                                        color="primary",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Save Prototype",
                                        id=PCI_MOT.MOT_SAVE_BTN,
                                        className="me-3",
                                        color="primary",
                                        n_clicks=0,
                                    ),
                                    dbc.Collapse(
                                        [
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "Node", "value": 'node'},
                                                    {"label": "Edge", "value": 'edge'},
                                                ],
                                                value='node',
                                                id=PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_0,
                                                inline=True, className="mt-3"
                                            ),
                                            dcc.Dropdown(
                                                id=PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_1,
                                                placeholder="Select element class...", className="mt-3",
                                            ),
                                            dcc.Dropdown(
                                                id=PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_2,
                                                placeholder="Select element path...", className="mt-3",
                                                optionHeight=100,
                                            ),
                                            dbc.Button(
                                                "Center",
                                                id=PCI_MOT.MOT_DROPDOWN_NAV_PAN_BTN,
                                                n_clicks=0, className="mt-3"
                                            ),
                                        ],
                                        id=PCI_MOT.MOT_DROPDOWN_NAV_COLLAPSE,
                                    ),
                                    dbc.Collapse(
                                        [
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("Name:"),
                                                    dbc.Input(placeholder="Enter prototype name...", type="text",
                                                              id=PCI_MOT.MOT_SAVE_NAME_INPUT, invalid=True),
                                                ],
                                                className="mt-3",
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("Version:"),
                                                    dbc.Input(placeholder="Enter prototype version...", type="text",
                                                              id=PCI_MOT.MOT_SAVE_VERSION_INPUT, invalid=True),
                                                ],
                                                className="mt-3",
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText("Is derived version:"),
                                                    dbc.InputGroupText(
                                                        dbc.Checkbox(id=PCI_MOT.MOT_SAVE_VERSION_INHERIT)),
                                                ],
                                                className="mt-3",
                                            ),
                                            dbc.Button("Download JSON", id=PCI_MOT.MOT_BTN_DOWNLOAD,
                                                       class_name="mx-1 mt-3",
                                                       color='success'),
                                            dbc.Button("Save to DB", id=PCI_MOT.MOT_BTN_SAVETODB,
                                                       class_name="mx-1 mt-3",
                                                       color='success', ),
                                        ],
                                        id=PCI_MOT.MOT_SAVE_COLLAPSE,
                                    ),
                                ],
                                className="text-center"
                            ),
                            html.Hr(),
                            html.Div(id=PCI_MOT.MOT_DIV_EDITOR, className="mt-3"),
                        ],
                        className="col-lg-4",
                    ),
                ]
            )

        ]
    )
    return page_layout


# TODO dry this
for toggle_triples in [
    [
        Output(PCI_MOT.MOT_EDITOR_LOG_COLLAPSE, "is_open"),
        Input(PCI_MOT.MOT_EDITOR_LOG_BTN, "n_clicks"),
        State(PCI_MOT.MOT_EDITOR_LOG_COLLAPSE, "is_open"),
    ],
    [
        Output(PCI_MOT.MOT_INSTRUCTION_COLLAPSE, "is_open"),
        Input(PCI_MOT.MOT_INSTRUCTION_BTN, "n_clicks"),
        State(PCI_MOT.MOT_INSTRUCTION_COLLAPSE, "is_open"),
    ],
    [
        Output(PCI_MOT.MOT_METADATA_COLLAPSE, "is_open"),
        Input(PCI_MOT.MOT_METADATA_BTN, "n_clicks"),
        State(PCI_MOT.MOT_METADATA_COLLAPSE, "is_open"),
    ],
    [
        Output(PCI_MOT.MOT_DROPDOWN_NAV_COLLAPSE, "is_open"),
        Input(PCI_MOT.MOT_DROPDOWN_NAV_BTN, "n_clicks"),
        State(PCI_MOT.MOT_DROPDOWN_NAV_COLLAPSE, "is_open"),
    ],
    [
        Output(PCI_MOT.MOT_SAVE_COLLAPSE, "is_open"),
        Input(PCI_MOT.MOT_SAVE_BTN, "n_clicks"),
        State(PCI_MOT.MOT_SAVE_COLLAPSE, "is_open"),
    ],
    [
        Output({'type': PCI_MOT.MOT_MODAL_UNION, 'index': MATCH}, 'is_open'),
        Input({'type': PCI_MOT.MOT_BTN_PT_UNION_OPEN_MODAL, 'index': MATCH}, 'n_clicks'),
        State({'type': PCI_MOT.MOT_MODAL_UNION, 'index': MATCH}, 'is_open'),
    ],
]:
    app.callback(*toggle_triples, prevent_initial_call=True, )(simple_open)


@app.callback(
    Output({'type': PCI_MOT.MOT_LIST_GROUP_PT_UNION, 'index': MATCH}, 'children'),
    Input({'type': PCI_MOT.MOT_MODAL_UNION, 'index': MATCH}, 'is_open'),
    State({'type': PCI_MOT.MOT_MODAL_UNION, 'index': MATCH}, 'id'),
    State(PCI_MOT.MOT_CYTO, 'elements'),
)
def render_union_list(is_open, node_cid, elements):
    mot = cyto_to_mot(elements)
    node_id = node_cid['index']
    message_type = mot.nodes[node_id]['mot_class_string']
    if is_open:
        cursor = MONGO_DB[COLLECTION].find({'root_message_type': message_type}, {'_id': 1, "root_message_type": 1})
        docs = list(cursor)
        if len(docs) == 0:
            return dbc.Alert('No type matching prototypes.')

        table_header = [
            html.Thead(html.Tr([html.Th("_id"), html.Th("Node Class")]))
        ]
        rows = []
        for doc in docs:
            mid = str(doc['_id'])
            mtype = doc['root_message_type']
            rows.append(html.Tr([html.Td(
                # TODO distinguish different rows with unique ids
                dbc.Button(mid, id={
                    'type': PCI_MOT.MOT_BTN_PT_UNION, 'index': node_id
                })
            ), html.Td(mtype)]))
        table_body = [html.Tbody(rows)]
        table = dbc.Table(
            # using the same table as in the above example
            table_header + table_body,
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,
        )
        return table
    print("no up")
    return no_update


@app.callback(
    Output(PCI_MOT.MOT_STORE_ALL_NODES, 'data'),
    Output(PCI_MOT.MOT_STORE_ALL_EDGES, 'data'),
    Output(PCI_MOT.MOT_STORE_EDITABLE_NODES, 'data'),
    Output(PCI_MOT.MOT_STORE_EDITABLE_EDGES, 'data'),
    Input(PCI_MOT.MOT_CYTO, 'elements'),
)
def update_intermediate_elements(elements: list[dict]):
    nodes = []
    edges = []
    editable_nodes = []
    editable_edges = []
    for e in elements:
        if e['group'] == 'nodes':
            nodes.append(e)
            if e['data']['ele_attrs']['mot_can_edit']:
                editable_nodes.append(e)
        else:
            edges.append(e)
            if e['data']['ele_attrs']['mot_can_edit']:
                editable_edges.append(e)
    return nodes, edges, editable_nodes, editable_edges


@app.callback(
    Output(PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_1, 'options'),
    Output(PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_2, 'options'),
    Input(PCI_MOT.MOT_STORE_ALL_NODES, 'data'),
    Input(PCI_MOT.MOT_STORE_ALL_EDGES, 'data'),
    Input(PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_0, 'value'),
    Input(PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_1, 'value'),
)
def update_navigator_selector_options(
        nodes, edges, element_group, element_class,
):
    mot = cyto_to_mot(nodes + edges)
    class_to_nx_ids = defaultdict(set)
    if element_group == 'node':
        for e in nodes:
            # TODO nav can find hidden elements, the following does not fix it as hiding does not update elements
            # if CYTO_MESSAGE_NODE_TMP_HIDE in e['classes']:
            #     continue
            node_id = int(e['data']['id'])
            class_string = mot.nodes[node_id]['mot_class_string']
            label = class_string.split(".")[-1]
            class_to_nx_ids[label].add(node_id)
    else:
        for e in edges:
            u_id = int(e['data']['source'])
            v_id = int(e['data']['target'])
            u_class_string = mot.nodes[u_id]['mot_class_string']
            u_label = u_class_string.split(".")[-1]
            v_class_string = mot.nodes[v_id]['mot_class_string']
            v_label = v_class_string.split(".")[-1]
            label = f"{u_label} || {v_label}"
            class_to_nx_ids[label].add((u_id, v_id))

    options_1 = sorted(class_to_nx_ids.keys())
    options_2 = []

    if not element_class:
        return options_1, options_2
    else:
        nx_ids = class_to_nx_ids[element_class]
        for i in nx_ids:
            if isinstance(i, int):
                label = mot_get_path(mot, i, arrow=True)
                value = str(i)
            else:
                u, v = i
                label_v = mot_get_path(mot, v, arrow=True)
                label = label_v
                value = f"{u} {v}"
            options_2.append({"label": label, "value": value})
        return options_1, options_2


@app.callback(
    Output(PCI_MOT.MOT_SAVE_NAME_INPUT, 'invalid'),
    Input(PCI_MOT.MOT_SAVE_NAME_INPUT, 'value')
)
def input_validation(s):
    if isinstance(s, str) and len(s) > 0:
        return False
    return True


@app.callback(
    Output(PCI_MOT.MOT_SAVE_VERSION_INPUT, 'invalid'),
    Input(PCI_MOT.MOT_SAVE_VERSION_INPUT, 'value')
)
def input_validation(s):
    if isinstance(s, str) and len(s) > 0:
        return False
    return True


@app.callback(
    Output(PCI_MOT.MOT_BTN_DOWNLOAD, 'disabled'),
    Output(PCI_MOT.MOT_BTN_SAVETODB, 'disabled'),
    Input(PCI_MOT.MOT_SAVE_NAME_INPUT, 'invalid'),
    Input(PCI_MOT.MOT_SAVE_VERSION_INPUT, 'invalid'),
)
def save_validation(iv1, iv2):
    if not iv1 and not iv2:
        return False, False
    return True, True


@app.callback(
    Output(PCI_MOT.MOT_STORE_PROTOTYPE_DOC, 'data'),
    Input(PCI_MOT.MOT_CYTO, 'elements'),
    Input(PCI_MOT.MOT_SAVE_NAME_INPUT, 'value'),
    Input(PCI_MOT.MOT_SAVE_VERSION_INPUT, 'value'),
    Input(PCI_MOT.MOT_SAVE_VERSION_INHERIT, 'value'),
    State(PCI_MOT.MOT_STORE_INIT_PROTOTYPE_DOC, 'data'),
)
def update_current_prototype_document(elements, name, version, inherit, init_data):
    mot = cyto_to_mot(elements)
    d = json.loads(json.dumps(pt_to_dict(mot), cls=BytesDump))
    doc = {
        'name': name,
        'version': version,
        'node_link_data': d,
        'root_message_type': mot.nodes[get_root(mot)]['mot_class_string'],
        'time_modified': datetime.now(),
        'time_created': datetime.now(),
    }
    if inherit:
        doc['from_version'] = init_data['version']
    else:
        doc['from_version'] = None
    return doc


@app.callback(
    Output(PCI_MOT.MOT_DIV_EDITOR, 'children'),
    Input(PCI_MOT.MOT_CYTO, 'selectedNodeData'),
    Input(PCI_MOT.MOT_CYTO, 'selectedEdgeData'),
    Input(PCI_MOT.MOT_CYTO, "elements"),
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


@app.callback(
    Output(PCI_MOT.MOT_DOWNLOAD, 'data'),
    Input(PCI_MOT.MOT_BTN_DOWNLOAD, 'n_clicks'),
    State(PCI_MOT.MOT_STORE_PROTOTYPE_DOC, 'data'),
    prevent_initial_call=True,
)
def download_json(n_clicks, data):
    if n_clicks:
        s = json.dumps(data, cls=BytesDump)
        return dict(content=s, filename="prototype.json")
    return no_update


@app.callback(
    Output('mot-dummy-4', 'children'),
    Input(PCI_MOT.MOT_BTN_SAVETODB, 'n_clicks'),
    State(PCI_MOT.MOT_STORE_PROTOTYPE_DOC, 'data'),
)
def save_to_database(n_clicks, data):
    if n_clicks:
        doc_inserted = MONGO_DB[COLLECTION].insert_one(data)
        return no_update
    return no_update


@app.callback(
    Output(PCI_MOT.MOT_CYTO, "stylesheet"),
    Input(PCI_MOT.MOT_BTN_SHOW_RELATIONS, "active"),
    prevent_initial_call=True,
)
def update_cyto_stylesheet(show_relations):
    style_sheet = deepcopy(CYTO_STYLE_SHEET_MOT)

    for style in style_sheet:
        if style['selector'] == 'node':
            if show_relations:
                style['style']['content'] = 'data(relation)'
            else:
                style['style']['content'] = 'data(label)'
            break

    return style_sheet


@app.callback(
    Output(PCI_MOT.MOT_BTN_SHOW_RELATIONS, "active"),
    Input(PCI_MOT.MOT_BTN_SHOW_RELATIONS, "n_clicks"),
    State(PCI_MOT.MOT_BTN_SHOW_RELATIONS, "active"),
    prevent_initial_call=True,
)
def update_show_relation_active(n_clicks, active):
    if n_clicks:
        return not active
    return active


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_pan_to_element',
    ),
    Output('mot-dummy-0', 'children'),
    Input(PCI_MOT.MOT_DROPDOWN_NAV_SELECTOR_2, 'value'),
    Input(PCI_MOT.MOT_DROPDOWN_NAV_PAN_BTN, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_run_mot_layout',
    ),
    Output('mot-dummy-1', 'children'),
    Input(PCI_MOT.MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_center_selected',
    ),
    Output('mot-dummy-2', 'children'),
    Input(PCI_MOT.MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_fit',
    ),
    Output('mot-dummy-3', 'children'),
    Input(PCI_MOT.MOT_BTN_CYTO_FIT, 'n_clicks'),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_hide_non_successors',
    ),
    Output('mot-dummy-5', 'children'),
    Input(PCI_MOT.MOT_BTN_HIDE_NON_SUCCESSORS, 'n_clicks'),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_show_all',
    ),
    Output('mot-dummy-6', 'children'),
    Input(PCI_MOT.MOT_BTN_SHOW_ALL, 'n_clicks'),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_derive_relations',
    ),
    Output('mot-dummy-8', 'children'),
    Input(PCI_MOT.MOT_BTN_SHOW_RELATIONS, 'active')
)


# # 2023/03/14it turns out dash_cyto.elements will not be updated when clientside elements got updated
# # so we update elements (preset and placeholder classes) on server side only, the following is deprecated
# # one could also use pure client side to do these...
# # https://community.plotly.com/t/clientside-callback-with-pattern-matching/45657/2
# app.clientside_callback(
#     ClientsideFunction(namespace='clientside_client', function_name='cy_mot_editor',),
#     Output('mot-dummy-7', 'children'),
#     Input({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'value'),
#     Input({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'value'),
#     State({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'id'),
#     State({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'id'),
#     prevent_initial_call=True,
# )


@app.callback(
    Output(PCI_MOT.MOT_CYTO, 'elements'),
    Output(PCI_MOT.MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    Output(PCI_MOT.MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),

    Input({'type': PCI_MOT.MOT_BTN_PT_EXTEND, 'index': ALL}, 'n_clicks'),
    State({'type': PCI_MOT.MOT_BTN_PT_EXTEND, 'index': ALL}, 'id'),

    Input({'type': PCI_MOT.MOT_BTN_PT_DETACH, 'index': ALL}, 'n_clicks'),
    State({'type': PCI_MOT.MOT_BTN_PT_DETACH, 'index': ALL}, 'id'),

    Input({'type': PCI_MOT.MOT_BTN_PT_DELETE, 'index': ALL}, 'n_clicks'),
    State({'type': PCI_MOT.MOT_BTN_PT_DELETE, 'index': ALL}, 'id'),

    Input({'type': PCI_MOT.MOT_BTN_PT_UNION, 'index': ALL}, 'n_clicks'),
    State({'type': PCI_MOT.MOT_BTN_PT_UNION, 'index': ALL}, 'id'),
    State({'type': PCI_MOT.MOT_BTN_PT_UNION, 'index': ALL}, 'children'),

    Input({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'value'),
    Input({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'value'),
    State({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE, 'index': ALL}, 'id'),
    State({'type': PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE, 'index': ALL}, 'id'),

    Input(PCI_MOT.MOT_CYTO, 'elements'),
    State(PCI_MOT.MOT_BTN_RELOAD_LAYOUT, 'n_clicks'),
    State(PCI_MOT.MOT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
    prevent_initial_call=True,
)
def update_cyto_elements(
        # operations that would trigger a center action and a layout reload action
        to_extend_btn_n_clicks, to_extend_btn_ids,
        to_detach_btn_n_clicks, to_detach_btn_ids,
        to_delete_btn_n_clicks, to_delete_btn_ids,
        to_union_btn_n_clicks, to_union_btn_ids, to_union_mid,

        # operations that would only update element style classes
        set_state_values, set_value_values,
        set_state_ids, set_value_ids,

        current_elements,
        current_n_clicks_reload_layout,
        current_n_clicks_center,
):
    triggered_cids = []
    triggered_types = []
    for it in ctx.triggered_prop_ids.values():
        triggered_cids.append(it['index'])
        triggered_types.append(it['type'])

    # trigger type can only be one
    if len(triggered_types) != 1:
        return no_update

    # one trigger
    assert len(set(triggered_cids)) == 1

    triggered_cid = triggered_cids[0]

    triggered_type = triggered_types[0]

    triggered_cid: Union[int, str]  # int for node_id, str for edge of "u v"

    do_union = False
    pt_operation = None
    if triggered_type == PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE:
        same_type_ids = set_state_ids
        same_type_props = set_state_values
    elif triggered_type == PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE:
        same_type_ids = set_value_ids
        same_type_props = set_value_values
    elif triggered_type == PCI_MOT.MOT_BTN_PT_EXTEND:
        same_type_ids = to_extend_btn_ids
        same_type_props = to_extend_btn_n_clicks
        pt_operation = pt_extend_node
    elif triggered_type == PCI_MOT.MOT_BTN_PT_DELETE:
        same_type_ids = to_delete_btn_ids
        same_type_props = to_delete_btn_n_clicks
        pt_operation = pt_remove_node
    elif triggered_type == PCI_MOT.MOT_BTN_PT_DETACH:
        same_type_ids = to_detach_btn_ids
        same_type_props = to_detach_btn_n_clicks
        pt_operation = pt_detach_node
    elif triggered_type == PCI_MOT.MOT_BTN_PT_UNION:
        same_type_ids = to_union_btn_ids
        same_type_props = to_union_btn_n_clicks
        do_union = True
    else:
        raise TypeError

    id_to_prop = dict(zip([si['index'] for si in same_type_ids], same_type_props))
    prop = id_to_prop[triggered_cid]
    # TODO DRY this
    if triggered_type == PCI_MOT.MOT_INPUT_PT_ELEMENT_STATE:
        for e in current_elements:
            if e['data']['id'] == str(triggered_cid):
                if prop:
                    e['data']['ele_attrs']['mot_state'] = PT_PLACEHOLDER
                    if CYTO_PLACEHOLDER_CLASS not in e['classes']:
                        e['classes'] += " " + CYTO_PLACEHOLDER_CLASS
                    e['classes'] = e['classes'].replace(CYTO_PRESET_CLASS, "")
                    # remove successors if a non-literal is marked as placeholder
                    # TODO make this work without importing
                    if import_string(
                            e['data']['ele_attrs']['mot_class_string']) not in OrdEnumClasses + BuiltinLiteralClasses:
                        mot = cyto_to_mot(current_elements)
                        successors = [nn for nn in nx.descendants(mot, triggered_cid) if nn != triggered_cid]
                        for s in successors:
                            mot.remove_node(s)
                        current_elements = mot_to_cyto_element_list(mot)
                else:
                    e['data']['ele_attrs']['mot_state'] = PT_PRESET
                    if CYTO_PRESET_CLASS not in e['classes']:
                        e['classes'] += " " + CYTO_PRESET_CLASS
                    e['classes'] = e['classes'].replace(CYTO_PLACEHOLDER_CLASS, "")
                    # non-literal is by default preset
                    if import_string(
                            e['data']['ele_attrs']['mot_class_string']) not in OrdEnumClasses + BuiltinLiteralClasses:
                        e['classes'] = e['classes'].replace(CYTO_PRESET_CLASS, "")
                break
        # TODO this and the following set_value would trigger reload_layout and center even n_clicks do not change
        return current_elements, current_n_clicks_reload_layout, current_n_clicks_center
    elif triggered_type == PCI_MOT.MOT_INPUT_PT_ELEMENT_VALUE:
        for e in current_elements:
            if e['data']['id'] == str(triggered_cid):
                e['data']['ele_attrs']['mot_value'] = prop
                break
        return current_elements, current_n_clicks_reload_layout, current_n_clicks_center
    else:
        if prop:
            current_mot = cyto_to_mot(current_elements)
            target_node_id = triggered_cid
            if do_union:
                # do not do union if it has existing children
                if len([*current_mot.successors(triggered_cid)]) > 0:
                    return current_elements, current_n_clicks_reload_layout, current_n_clicks_center

                other_graph = MONGO_DB[COLLECTION].find_one({"_id": ObjectId(to_union_mid[0])})
                other_graph = other_graph['node_link_data']
                other_graph = nx.node_link_graph(other_graph, directed=True)
                baseline = max(current_mot.nodes) + 1
                other_graph_mapping = dict()
                for n in other_graph.nodes:
                    other_graph_mapping[n] = n + baseline
                nx.relabel_nodes(other_graph, other_graph_mapping, copy=False)
                other_graph_root = get_root(other_graph)
                other_graph_mapping = {other_graph_root: target_node_id}
                nx.relabel_nodes(other_graph, other_graph_mapping, copy=False)

                # missing_edge = (next(current_mot.predecessors(target_node_id)), target_node_id)
                # missing_edge_attrs = current_mot.edges[missing_edge]
                for n in other_graph.nodes:
                    other_graph.nodes[n]['mot_element_id'] = n
                for e in other_graph.edges:
                    other_graph.edges[e]['mot_element_id'] = e

                merged_mot = nx.compose(current_mot, other_graph)
                # merged_mot.add_edge(*missing_edge, **missing_edge_attrs)
                current_elements = mot_to_cyto_element_list(merged_mot)
            else:
                pt_operation(current_mot, target_node_id, inplace=True)
                current_elements = mot_to_cyto_element_list(current_mot)
            current_n_clicks_reload_layout += 1
            current_n_clicks_center += 1

        return current_elements, current_n_clicks_reload_layout, current_n_clicks_center
