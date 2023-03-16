from copy import deepcopy

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_defer_js_import as dji
from dash import html, Input, Output, State, dcc, register_page, get_app, get_asset_url
from dash.dependencies import ClientsideFunction
from dash_iconify import DashIconify

from dash_app_support.components import simple_open, PCI_MTT, get_node_attr_block, get_edge_attr_block
from dash_app_support.cyto_config import CYTO_STYLE_SHEET_MTT
from dash_app_support.cyto_elements import mtt_to_cyto
from dash_app_support.fixtures import MttData, MttDataDict
from ord_tree.mtt import mtt_from_dict
from ord_tree.utils import NodePathDelimiter

register_page(__name__, path="/data_model", description="Data Model")
cyto.load_extra_layouts()
app = get_app()

# region define components
COMPONENT_CYTO_MTT = cyto.Cytoscape(
    id=PCI_MTT.MTT_CYTO,
    zoomingEnabled=True,
    maxZoom=2,
    minZoom=0.1,
    layout={
        'name': 'dagre',
        'nodeDimensionsIncludeLabels': True,
        'animate': True,
        'animationDuration': 1000,
        'align': 'UL',
    },
    style={'width': '100%', 'height': '100%', 'min-height': '300px'},
    stylesheet=CYTO_STYLE_SHEET_MTT,
    elements=[],
)

COMPONENT_MTT_SELECTOR = dcc.Dropdown(
    id=PCI_MTT.MTT_SELECTOR,
    options=sorted([{"label": c, "value": c} for c in MttDataDict], key=lambda x: x["label"]),
    value="Compound",
    placeholder="Select an ORD message type...",
)

# dummies for client-side callbacks
DUMMIES = [
    html.Div(id="mtt-dummy-0", style={'display': 'none'}),
    html.Div(id="mtt-dummy-1", style={'display': 'none'}),
    html.Div(id="mtt-dummy-2", style={'display': 'none'}),
    html.Div(id="mtt-dummy-3", style={'display': 'none'}),
    html.Div(id="mtt-dummy-4", style={'display': 'none'}),
]

COMPONENT_VIEWPORT_BUTTONS = html.Div(
    [
        dbc.Button("Hide Literals", id=PCI_MTT.MTT_BTN_HIDE_LITERALS, active=True, outline=True,
                   color="primary",
                   className="me-3 mt-3"),
        dbc.Button("Show Relations", id=PCI_MTT.MTT_BTN_SHOW_RELATIONS, active=False, outline=True,
                   color="primary",
                   className="me-3 mt-3"),
        dbc.Button("Fit Graph", id=PCI_MTT.MTT_BTN_CYTO_FIT,
                   className="me-3 mt-3"),
        dbc.Button("Center Selected", id=PCI_MTT.MTT_BTN_CYTO_CENTER_SELECTED,
                   className="me-3 mt-3"),
        dbc.Button("Run Layout", id=PCI_MTT.MTT_BTN_CYTO_RUN_LAYOUT, n_clicks=0,
                   className="me-3 mt-3"),
    ],
    className="text-center"
)

# icons from https://stackoverflow.com/questions/59081062
COMPONENT_LEGEND = html.Div(
    [
        html.B(
            [
                DashIconify(icon="mdi:octagon-outline", width=30, className="me-1"),
                "Mutable"
            ],
            className="me-3"
        ),
        html.B(
            [
                DashIconify(icon="material-symbols:square-outline", width=30, className="me-1"),
                "Message"
            ],
            className="me-3"
        ),
        html.B(
            [
                DashIconify(icon="ic:twotone-square", width=30, className="me-1"),
                "Literal"
            ],
            className="me-3"
        ),
    ],
    className="mt-3 d-flex justify-content-center"
)
# endregion

# region page layout
layout = html.Div(
    [
        dji.Import(src=get_asset_url("defer_cyto.js")),
        *DUMMIES,
        dbc.Row(
            [
                dbc.Card(
                    [
                        COMPONENT_VIEWPORT_BUTTONS,
                        html.Hr(),
                        COMPONENT_CYTO_MTT,
                    ],
                    className="col-lg-8",
                    style={'height': 'calc(100vh - 100px)'},  # minus header bar height
                ),
                html.Div(
                    [
                        html.H5("Visualizing ORD Data Model", className="text-center mt-3"),
                        html.Hr(),
                        COMPONENT_LEGEND,
                        html.Hr(),
                        html.Div(
                            [html.H6("ORD message type", className="text-center"), COMPONENT_MTT_SELECTOR],
                            className="mb-3 mt-3"
                        ),
                        html.Div(id=PCI_MTT.MTT_DIV_INFO_ELEMENT, className="mt-3"),
                    ],
                    className="col-lg-4",
                ),
            ]
        )

    ]
)
# endregion

# region clienside callback
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_run_mtt_layout',
    ),
    Output('mtt-dummy-0', 'children'),
    Input(PCI_MTT.MTT_BTN_CYTO_RUN_LAYOUT, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_center_selected',
    ),
    Output('mtt-dummy-1', 'children'),
    Input(PCI_MTT.MTT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_viewport',
        function_name='cy_fit',
    ),
    Output('mtt-dummy-2', 'children'),
    Input(PCI_MTT.MTT_BTN_CYTO_FIT, 'n_clicks'),
)
# endregion

# region static simple callbacks
app.callback(
    Output(PCI_MTT.MTT_BTN_HIDE_LITERALS, 'active'),
    Input(PCI_MTT.MTT_BTN_HIDE_LITERALS, 'n_clicks'),
    State(PCI_MTT.MTT_BTN_HIDE_LITERALS, 'active'),
    prevent_initial_call=True,
)(simple_open)

app.callback(
    Output(PCI_MTT.MTT_BTN_SHOW_RELATIONS, 'active'),
    Input(PCI_MTT.MTT_BTN_SHOW_RELATIONS, 'n_clicks'),
    State(PCI_MTT.MTT_BTN_SHOW_RELATIONS, 'active'),
    prevent_initial_call=True,
)(simple_open)


# endregion

# region server callbacks
@app.callback(
    Output(PCI_MTT.MTT_CYTO, "stylesheet"),
    Input(PCI_MTT.MTT_BTN_SHOW_RELATIONS, "active"),
    Input(PCI_MTT.MTT_CYTO, "selectedNodeData"),
    prevent_initial_call=True,
)
def update_cyto_stylesheet(show_relations, node_data):
    style_sheet = deepcopy(CYTO_STYLE_SHEET_MTT)  # TODO necessary?

    for style in style_sheet:
        if style['selector'] == 'node':
            if show_relations:
                style['style']['content'] = 'data(relation)'
            else:
                style['style']['content'] = 'data(label)'
            break

    # highlight path to selected nodes
    path_style = []

    # method 2 use node name (path)
    if node_data:
        for d in node_data:
            node_name = d['id']
            p = node_name.split(NodePathDelimiter)
            for i in range(len(p)):
                v = NodePathDelimiter.join(p[:i + 1])
                path_style.append(
                    {
                        'selector': f'edge[target="{v}"]',
                        'style': {
                            'line-color': 'blue',
                            'z-index': 1000,
                        }
                    }
                )
    style_sheet += path_style
    return style_sheet


@app.callback(
    Output(PCI_MTT.MTT_CYTO, "elements"),
    Input(PCI_MTT.MTT_SELECTOR, "value"),
    Input(PCI_MTT.MTT_BTN_HIDE_LITERALS, "active"),
)
def update_cyto_elements(mtt_name, hide_literals):
    if not mtt_name:
        return []
    mtt_data = MttDataDict[mtt_name]
    mtt_data = MttData(**mtt_data)
    mtt = mtt_from_dict(mtt_data['mtt_dict'])

    elements_node, elements_edge = mtt_to_cyto(mtt, hide_literal=hide_literals)
    elements_node.update(elements_edge)
    return [e.as_dict() for e in elements_node.values()]


@app.callback(
    Output(PCI_MTT.MTT_DIV_INFO_ELEMENT, "children"),
    Input(PCI_MTT.MTT_CYTO, "selectedNodeData"),
    Input(PCI_MTT.MTT_CYTO, "selectedEdgeData"),
    State(PCI_MTT.MTT_SELECTOR, "value"),
)
def update_div_info(node_data, edge_data, mtt_name):
    if not mtt_name:
        return []
    mtt_data = MttDataDict[mtt_name]
    mtt = mtt_from_dict(mtt_data['mtt_dict'])
    node_attrs = []
    edge_attrs = []
    if node_data:
        for d in node_data:
            node_attrs.append(mtt.nodes[d['id']])
    if edge_data:
        for d in edge_data:
            u = d['source']
            v = d['target']
            attrs = {
                "source": u,
                "target": v,
            }
            edge_attrs.append(attrs)
    blocks = []
    for attrs in node_attrs:
        blocks.append(get_node_attr_block(attrs, mtt))
    for attrs in edge_attrs:
        blocks.append(get_edge_attr_block(attrs['source'], attrs['target'], mtt))
    return blocks
# endregion
