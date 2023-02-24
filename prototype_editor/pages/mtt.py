import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import html, Input, Output, State, dcc
from dash import register_page, get_app
from copy import deepcopy

from cyto_app.cyto_config import DASH_CID_CYTO, CYTO_STYLE_SHEET, DASH_CID_MTT_DIV_INFO_ELEMENT, \
    DASH_CID_MTT_SELECTOR, DASH_CID_MTT_SWITCHES
from cyto_app.cyto_elements import mtt_to_cyto, MttNodeAttr
from cyto_app.fixtures import MttDataDict, MttData
from ord_tree.mtt import mtt_from_dict, OrdEnumClasses, BuiltinLiteralClasses, OrdMessageClasses
from ord_tree.utils import import_string, NodePathDelimiter

register_page(__name__, path="/mtt", description="Message")
cyto.load_extra_layouts()
app = get_app()

# only visualize non-trivial mtt
_MttDataDict = {k: v for k, v in MttDataDict.items() if v['depth'] > 3}

# define components
COMPONENT_CYTO_MAIN = cyto.Cytoscape(
    id=DASH_CID_CYTO,
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
    stylesheet=CYTO_STYLE_SHEET,
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
        # html.H2("Tree Visualization"),
        # html.Hr(),
        dbc.Row(
            [
                dbc.Card(
                    COMPONENT_CYTO_MAIN,
                    className="col-lg-8"
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H6("ORD message type", className="text-center"), COMPONENT_MTT_SELECTOR],
                            className="mb-3 mt-3"
                        ),
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
                        html.Div(id=DASH_CID_MTT_DIV_INFO_ELEMENT, className="mt-2"),
                    ],
                    className="col-lg-4",
                ),
            ]
        )

    ]
)

@app.callback(
    Output(DASH_CID_CYTO, "stylesheet"),
    Input(DASH_CID_MTT_SWITCHES, "value")
)
def update_cyto_stylesheet(switch_values):
    style_sheet = deepcopy(CYTO_STYLE_SHEET)
    if 'Relation Label' in switch_values:
        assert style_sheet[1]['selector'] == 'node'
        style_sheet[1]['style']['content'] = 'data(relation)'
    return style_sheet

@app.callback(
    Output(DASH_CID_CYTO, "elements"),
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
    return mtt_to_cyto(mtt, hide_literal=hide_literals)


@app.callback(
    Output(DASH_CID_MTT_DIV_INFO_ELEMENT, "children"),
    Input(DASH_CID_CYTO, "selectedNodeData"),
    Input(DASH_CID_CYTO, "selectedEdgeData"),
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
            dbc.CardHeader([html.B(relation, className="text-primary"),]),
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
