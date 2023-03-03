from copy import deepcopy

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import html, Input, Output, State, dcc
from dash import register_page, get_app
from dash.dependencies import ClientsideFunction

from cyto_app.cyto_config import *
from cyto_app.cyto_elements import mtt_to_cyto, MttNodeAttr
from cyto_app.fixtures import MttDataDict, MttData
from ord_tree.mtt import mtt_from_dict, OrdEnumClasses, BuiltinLiteralClasses, OrdMessageClasses
from ord_tree.utils import import_string, NodePathDelimiter

register_page(__name__, path="/mtt", description="Message")
cyto.load_extra_layouts()
app = get_app()

# only visualize non-trivial mtt
# _MttDataDict = {k: v for k, v in MttDataDict.items() if v['depth'] > 3}
_MttDataDict = {k: v for k, v in MttDataDict.items()}

# define components
COMPONENT_CYTO_MTT = cyto.Cytoscape(
    id=DASH_CID_MTT_CYTO,
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
    # style={'width': '100%', 'height': '100%', 'min-height': '600px', 'max-height': '100vh'},
    style={'width': '100%', 'height': '100%', 'min-height': '300px'},
    stylesheet=CYTO_STYLE_SHEET_MTT,
    elements=[],
)

COMPONENT_MTT_SELECTOR = dcc.Dropdown(
    id=DASH_CID_MTT_SELECTOR,
    options=sorted([{"label": c, "value": c} for c in _MttDataDict], key=lambda x: x["label"]),
    value="Compound",
    placeholder="Select an ORD message type...",
)

# page layout
layout = html.Div(
    [
        # dummies for client-side callbacks
        html.Div(id="mtt-dummy-0", style={'display': 'none'}),
        html.Div(id="mtt-dummy-1", style={'display': 'none'}),

        dbc.Row(
            [
                dbc.Card(
                    COMPONENT_CYTO_MTT,
                    className="col-lg-8",
                    # style={'max-height': '100vh'},
                    style={'height': 'calc(100vh - 100px)'},  # minus header bar height
                ),
                html.Div(
                    [
                        html.H5("Visualizing ORD Data Model", className="text-center"),
                        html.Hr(),
                        html.Div(
                            [html.H6("ORD message type", className="text-center"), COMPONENT_MTT_SELECTOR],
                            className="mb-3 mt-3"
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H6("Viewport Control")),
                                dbc.CardBody(
                                    [
                                        dbc.Checklist(
                                            options=[
                                                {"label": "Hide Literals", "value": 'Hide Literals'},
                                                {"label": "Relation Label", "value": 'Relation Label'},
                                            ],
                                            input_class_name="mx-2",
                                            label_class_name="mx-2",
                                            class_name="mtt-switch",
                                            value=['Hide Literals'],
                                            id=DASH_CID_MTT_SWITCHES,
                                            switch=True,
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button("Fit Graph", id=DASH_CID_MTT_BTN_CYTO_FIT,
                                                           className="me-3 mt-3"),
                                                dbc.Button("Center Selected", id=DASH_CID_MTT_BTN_CYTO_CENTER_SELECTED,
                                                           className="me-3 mt-3"),
                                            ],
                                            className="text-center"
                                        )
                                    ]
                                ),
                            ],
                        ),
                        html.Div(id=DASH_CID_MTT_DIV_INFO_ELEMENT, className="mt-3"),
                    ],
                    className="col-lg-4",
                ),
            ]
        )

    ]
)


@app.callback(
    Output(DASH_CID_MTT_CYTO, "stylesheet"),
    Input(DASH_CID_MTT_SELECTOR, "value"),
    Input(DASH_CID_MTT_SWITCHES, "value"),
    Input(DASH_CID_MTT_CYTO, "selectedNodeData"),
)
def update_cyto_stylesheet(mtt_name, switch_values, node_data):
    style_sheet = deepcopy(CYTO_STYLE_SHEET_MTT)
    if not mtt_name:
        return style_sheet
    if 'Relation Label' in switch_values:
        assert style_sheet[1]['selector'] == 'node'
        style_sheet[1]['style']['content'] = 'data(relation)'

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

    # # method 1 use mtt
    # mtt_data = _MttDataDict[mtt_name]
    # mtt = mtt_from_dict(mtt_data['mtt_dict'])
    # root = get_root(mtt)
    # if node_data:
    #     for d in node_data:
    #         node_name = d['id']
    #         p = nx.shortest_path(mtt, source=root, target=node_name)
    #         n_edges = len(p) - 1
    #         for i in range(n_edges):
    #             u, v = p[i], p[i+1]
    #             path_style.append(
    #                 {
    #                     'selector': f'edge[target="{v}"]',
    #                     'style': {
    #                         'line-color': 'blue',
    #                         'z-index': 1000,
    #                     }
    #                 }
    #             )
    # style_sheet += path_style
    # return style_sheet


@app.callback(
    Output(DASH_CID_MTT_CYTO, "elements"),
    Input(DASH_CID_MTT_SELECTOR, "value"),
    Input(DASH_CID_MTT_SWITCHES, "value")
)
def update_cyto_elements(mtt_name, switch_values):
    if not mtt_name:
        return []
    mtt_data = _MttDataDict[mtt_name]
    mtt_data = MttData(**mtt_data)
    mtt = mtt_from_dict(mtt_data['mtt_dict'])

    hide_literals = False
    if 'Hide Literals' in switch_values:
        hide_literals = True
    elements_node, elements_edge = mtt_to_cyto(mtt, hide_literal=hide_literals)
    elements_node.update(elements_edge)
    return [e.as_dict() for e in elements_node.values()]


@app.callback(
    Output(DASH_CID_MTT_DIV_INFO_ELEMENT, "children"),
    Input(DASH_CID_MTT_CYTO, "selectedNodeData"),
    Input(DASH_CID_MTT_CYTO, "selectedEdgeData"),
    State(DASH_CID_MTT_SELECTOR, "value"),
)
def update_div_info(node_data, edge_data, mtt_name):
    if not mtt_name:
        return []
    mtt_data = _MttDataDict[mtt_name]
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


def get_edge_attr_block(u: str, v: str, mtt: nx.DiGraph):
    u_attrs = MttNodeAttr(**mtt.nodes[u])
    v_attrs = MttNodeAttr(**mtt.nodes[v])

    items = []
    for attrs, st in zip((u_attrs, v_attrs), ('Source Path', 'Target Path')):
        path = attrs['mtt_node_name']
        path = dcc.Markdown(
            " &rarr; ".join([f"_{p}_" for p in path.split(NodePathDelimiter)])
        )
        item_path = dbc.ListGroupItem([html.H6(st), path])
        items.append(item_path)

    list_group = dbc.ListGroup(items)

    relation = v_attrs['mtt_relation_to_parent']
    block = dbc.Card(
        [
            dbc.CardHeader([html.B(relation, className="text-primary"), ]),
            dbc.CardBody(list_group),
        ],
        className="mb-3"
    )
    return block


def get_node_attr_block(mtt_node_attr: MttNodeAttr, mtt: nx.DiGraph):
    node_class = import_string(mtt_node_attr['mtt_class_string'])
    class_name = node_class.__name__

    # node path
    path = mtt_node_attr['mtt_node_name']
    path = dcc.Markdown(
        " &rarr; ".join([f"_{p}_" for p in path.split(NodePathDelimiter)])
    )
    item_path = dbc.ListGroupItem([html.H6("Node Path"), path])

    # node children
    item_children = [html.H6("Children"), ]
    show_children = False
    markdown_text = ""
    for child in mtt.successors(mtt_node_attr['mtt_node_name']):
        child_attrs = MttNodeAttr(**mtt.nodes[child])
        child_class = import_string(child_attrs['mtt_class_string'])
        relation = child_attrs['mtt_relation_to_parent']
        if child_class in BuiltinLiteralClasses:
            suffix = "[BuiltinLiteral]"
        elif child_class in OrdEnumClasses:
            suffix = "[OrdEnum]"
        elif child_class in OrdMessageClasses:
            suffix = "[OrdMessage]"
        else:
            assert child_class in (list, dict)
            continue
        oneof_group = mtt_node_attr['mtt_relation_to_parent_oneof']
        if oneof_group:
            suffix += f"({oneof_group})"
        show_children = True
        markdown_text += f"* _{relation}_ @ `{child_class.__name__}{suffix}`\n"
    item_children.append(dcc.Markdown(markdown_text))
    item_children = dbc.ListGroupItem(item_children)

    list_items = []
    list_items.append(item_path)
    if show_children:
        list_items.append(item_children)

    list_group = dbc.ListGroup(list_items)

    ref_link = "https://docs.python.org/3/tutorial/datastructures.html"
    if node_class in OrdMessageClasses:
        ref_link = f"https://github.com/open-reaction-database/ord-schema/blob/main/proto/reaction.proto#:~:text=message-,{class_name}"
    elif node_class in OrdEnumClasses:
        ref_link = f"https://github.com/open-reaction-database/ord-schema/blob/main/proto/reaction.proto#:~:text=enum%20{class_name}"

    block = dbc.Card(
        [
            dbc.CardHeader([html.B(class_name, className="text-primary"),
                            dbc.CardLink("Definition", href=ref_link, style={"float": "right"})]),
            dbc.CardBody(list_group),
        ],
        className="mb-3"
    )
    return block


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_center_selected',
    ),
    Output('mtt-dummy-0', 'children'),
    Input(DASH_CID_MTT_BTN_CYTO_CENTER_SELECTED, 'n_clicks'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='cy_fit',
    ),
    Output('mtt-dummy-1', 'children'),
    Input(DASH_CID_MTT_BTN_CYTO_FIT, 'n_clicks'),
)
