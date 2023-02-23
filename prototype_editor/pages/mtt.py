import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, Input, Output, State
from dash import register_page, get_app

from ord_tree.cyto_app.cyto_config import DASH_CID_CYTO, CYTO_STYLE_SHEET, DASH_CID_MTT_DIV_INFO_ELEMENT, \
    DASH_CID_MTT_DIV_INFO_TREE, \
    DASH_CID_MTT_BUTTON_GROUP
from ord_tree.cyto_app.cyto_elements import mtt_to_cyto
from ord_tree.cyto_app.fixtures import MttDataDict, MttData
from ord_tree.mtt import mtt_from_dict

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
        'align': 'UL',
        'rankSep': 80,
        'edgeSep': 80,
    },
    style={'width': '100%', 'height': '600px'},
    stylesheet=CYTO_STYLE_SHEET,
    elements=[],
)

COMPONENT_MTT_BUTTON_GROUP = html.Div(
    [
        dbc.RadioItems(
            id=DASH_CID_MTT_BUTTON_GROUP,
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary mt-3",
            labelCheckedClassName="active",
            options=sorted([{"label": c, "value": c} for c in _MttDataDict], key=lambda x: x["label"]),
            value="Reaction",
        ),
    ],
    className="radio-group",
)

# page layout
layout = html.Div(
    [
        html.H2("Message Tree Visualization"),
        html.Hr(),
        COMPONENT_MTT_BUTTON_GROUP,
        dbc.Row(
            [
                html.Div(COMPONENT_CYTO_MAIN, className="col-lg-8 border-primary border"),
                html.Div(
                    [
                        html.Div(id=DASH_CID_MTT_DIV_INFO_TREE, ),
                        html.Div(id=DASH_CID_MTT_DIV_INFO_ELEMENT, ),
                    ],
                    className="col-lg-4",
                ),
            ]
        )

    ]
)


@app.callback(
    Output(DASH_CID_CYTO, "elements"),
    Output(DASH_CID_MTT_DIV_INFO_TREE, "children"),
    Input(DASH_CID_MTT_BUTTON_GROUP, "value"),
)
def update_cyto_elements(mtt_name):
    mtt_data = _MttDataDict[mtt_name]
    mtt_data = MttData(**mtt_data)
    mtt = mtt_from_dict(mtt_data['mtt_dict'])

    tree_info = html.P(
        ["Message Type: ", html.B(mtt_data['name']), f" (N{len(mtt.nodes)}@E{len(mtt.edges)})"],
        className="text-center"
    )
    return mtt_to_cyto(mtt, hide_literal=True), tree_info


@app.callback(
    Output(DASH_CID_MTT_DIV_INFO_ELEMENT, "children"),
    Input(DASH_CID_CYTO, "selectedNodeData"),
    Input(DASH_CID_CYTO, "selectedEdgeData"),
    State(DASH_CID_MTT_BUTTON_GROUP, "value"),
)
def update_div_info(node_data, edge_data, mtt_name):
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
    for attrs in node_attrs + edge_attrs:
        lines = []
        for k, v in attrs.items():
            c1 = dbc.InputGroupText(k)
            c2 = dbc.Input(type="text", value=v, disabled=True)
            lines.append(dbc.InputGroup([c1, c2], className="mt-3"))
        blocks.append(html.Div(lines, className="mt-3 border border-primary"))
    return blocks
