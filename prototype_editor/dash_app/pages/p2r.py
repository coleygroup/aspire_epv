import json
import os

from dash_app_support.components import get_literal_node_value_input
from dash_app_support.cyto_elements import BytesDump

import dash_bootstrap_components as dbc
import dash_renderjson
import networkx as nx
from bson.objectid import ObjectId
from dash import html, Input, Output, dcc, ALL, register_page, get_app, State, ctx
from pymongo import MongoClient

from dash_app_support.components import JsonTheme
from dash_app_support.components import simple_open
from dash_app_support.db import ENV_MONGO_URI, ENV_MONGO_DB, ENV_MONGO_COLLECTION
from ord_tree.mot import PT_PLACEHOLDER, MotEleAttr, mot_get_path, message_from_mot
from ord_tree.utils import import_string, get_leafs

this_folder = os.path.dirname(os.path.abspath(__file__))
register_page(__name__, path_template="/instantiate/<prototype_id>", description="Instantiate")
app = get_app()
# TODO auth
MONGO_DB = MongoClient(ENV_MONGO_URI)[ENV_MONGO_DB]
COLLECTION = ENV_MONGO_COLLECTION


#

class PCI_P2R:
    CID_P2R_ELEMENT_INPUT = "CID_P2R_ELEMENT_INPUT"

    CID_P2R_STORE_LIVE_PT = "CID_P2R_STORE_LIVE_PT"
    CID_P2R_STORE_INIT_PT = "CID_P2R_STORE_INIT_PT"

    CID_P2R_BTN_OPEN_JSON_VIEWER_MODAL = "CID_P2R_BTN_OPEN_JSON_VIEWER_MODAL"
    CID_P2R_JSON_VIEWER_MODAL = "CID_P2R_JSON_VIEWER_MODAL"
    CID_P2R_DIV_JSON_VIEWER_IN_JSON_VIEWER_MODAL = "CID_P2R_DIV_JSON_VIEWER_IN_JSON_VIEWER_MODAL"

    CID_P2R_SELECT_PT = "CID_P2R_SELECT_PT"
    DASH_CID_P2R_PT_SELECTOR = "CID_P2R_PT_SELECTOR"


def get_init_doc(pid):
    mot_data = MONGO_DB[COLLECTION].find_one({"_id": ObjectId(pid)})
    return mot_data


def layout(prototype_id=None):
    init_doc = get_init_doc(prototype_id)
    init_pt_data = init_doc['node_link_data']
    init_pt_data = json.loads(json.dumps(init_pt_data, cls=BytesDump))
    init_metadata = {k: v for k, v in init_doc.items() if k not in ('node_link_data', '_id')}
    init_pt = nx.node_link_graph(init_pt_data)

    return html.Div(
        [
            dcc.Store(id=PCI_P2R.CID_P2R_STORE_INIT_PT, data=init_pt_data),
            dcc.Store(id=PCI_P2R.CID_P2R_STORE_LIVE_PT),
            html.Div(
                [
                    dbc.Button("JSON", id=PCI_P2R.CID_P2R_BTN_OPEN_JSON_VIEWER_MODAL, className="mb-3 me-3"),
                    dbc.Button(
                        "to Editor",
                        className="mb-3 me-3",
                        href=f'/edit/{prototype_id}'
                    ),
                    # dbc.Button("Reset", id=PCI_P2R.CID_P2R_BTN_RESET, className="mb-3"),
                ]
            ),
            dbc.Modal(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader("JSON viewer"),
                            dbc.CardBody(
                                dash_renderjson.DashRenderjson(
                                    id=PCI_P2R.CID_P2R_DIV_JSON_VIEWER_IN_JSON_VIEWER_MODAL,
                                    max_depth=-1,
                                    theme=JsonTheme,
                                    invert_theme=True
                                )
                            ),
                        ]
                    )
                ],
                is_open=False,
                id=PCI_P2R.CID_P2R_JSON_VIEWER_MODAL
            ),

            # get_reaction_input_card(pt_reaction_input=init_pt, pt_main=init_pt),
            html.Hr(className="mb-3"),
            get_leaf_inputs(pt_main=init_pt),
            html.Hr(className="mt-3 mb-3"),
            get_edge_inputs(pt_main=init_pt),
        ]
    )


app.callback(
    Output(PCI_P2R.CID_P2R_JSON_VIEWER_MODAL, 'is_open'),
    Input(PCI_P2R.CID_P2R_BTN_OPEN_JSON_VIEWER_MODAL, 'n_clicks'),
    State(PCI_P2R.CID_P2R_JSON_VIEWER_MODAL, 'is_open'),
    prevent_initial_call=True,
)(simple_open)




def get_edge_input_group(pt_main: nx.DiGraph, u: int, v:int):
    ele_attrs = pt_main.edges[(u, v)]
    ele_attrs: MotEleAttr
    element_class = str
    element_value = ele_attrs['mot_value']
    element_id = ele_attrs['mot_element_id']  # TODO make sure this is consistent with current tree
    cid = {'type': PCI_P2R.CID_P2R_ELEMENT_INPUT, 'index': f"{u} {v}"}
    if ele_attrs['mot_state'] == PT_PLACEHOLDER:
        disable_input = False
    else:
        disable_input = True
    value_input = get_literal_node_value_input(element_class, node_value=element_value, cid=cid, disabled=disable_input)

    path = mot_get_path(pt_main, v, with_node=False, delimiter="arrow", remove_last=True)
    return dbc.InputGroup(
        [
            dbc.InputGroupText(["EdgeTarget: ", path], className="d-block w-100 rounded-0"),
            value_input,
            dbc.InputGroupText(element_class.__name__),
        ],

        className="mt-4"
    )


def get_node_input_group(pt_main: nx.DiGraph, node: int, path_width=None):
    ele_attrs = pt_main.nodes[node]
    ele_attrs: MotEleAttr
    element_class = import_string(ele_attrs['mot_class_string'])
    element_value = ele_attrs['mot_value']
    element_id = ele_attrs['mot_element_id']  # TODO make sure this is consistent with current tree
    cid = {'type': PCI_P2R.CID_P2R_ELEMENT_INPUT, 'index': element_id}
    if ele_attrs['mot_state'] == PT_PLACEHOLDER:
        disable_input = False
    else:
        disable_input = True
    value_input = get_literal_node_value_input(element_class, node_value=element_value, cid=cid, disabled=disable_input)

    path = mot_get_path(pt_main, node, with_node=False, delimiter="arrow")
    if path_width:
        width = f"{path_width}px"
        style = {"width": width}
    else:
        style = {}
    return dbc.InputGroup(
        [
            dbc.InputGroupText(path, style=style),
            value_input,
            dbc.InputGroupText(element_class.__name__),
        ],

        className="mt-4"
    )


def get_leaf_inputs(pt_main: nx.DiGraph):
    shown_leafs = []
    shown_leafs_paths = []
    for leaf in get_leafs(pt_main, sort=True):
        if pt_main.nodes[leaf]['mot_state'] != PT_PLACEHOLDER:
            continue
        shown_leafs.append(leaf)
        shown_leafs_paths.append(mot_get_path(pt_main, leaf))
    if len(shown_leafs) == 0:
        return dbc.Alert("No placeholder nodes found in this prototype!", color="warning")
    path_max = max([len(p) for p in shown_leafs_paths])

    input_divs = []
    for leaf in shown_leafs:
        input_div = get_node_input_group(pt_main, leaf, path_max * 10 + 5)
        input_divs.append(input_div)
    return html.Div(input_divs)


def get_edge_inputs(pt_main: nx.DiGraph):
    shown_edges = []
    shown_edges_paths = []
    for u, v, d in pt_main.edges(data=True):
        if d['mot_state'] != PT_PLACEHOLDER:
            continue
        shown_edges.append((u, v, d))
        shown_edges_paths.append(mot_get_path(pt_main, v))
    if len(shown_edges) == 0:
        return dbc.Alert("No placeholder edges found in this prototype!", color="warning")

    input_divs = []
    for u, v, d in shown_edges:
        input_div = get_edge_input_group(pt_main, u, v)
        input_divs.append(input_div)
    return html.Div(input_divs)



@app.callback(
    Output(PCI_P2R.CID_P2R_STORE_LIVE_PT, 'data'),
    Input({'type': PCI_P2R.CID_P2R_ELEMENT_INPUT, 'index': ALL}, 'value'),
    Input({'type': PCI_P2R.CID_P2R_ELEMENT_INPUT, 'index': ALL}, 'id'),
    Input(PCI_P2R.CID_P2R_STORE_INIT_PT, "data"),
)
def update_live_store_pt(p2r_values, p2r_ids, init_pt_data):
    for it in ctx.triggered_prop_ids.values():
        if isinstance(it, str):
            if it == PCI_P2R.CID_P2R_STORE_INIT_PT:
                return init_pt_data

    pt = nx.node_link_graph(init_pt_data)
    for val, j in zip(p2r_values, p2r_ids):
        i = j['index']
        if not isinstance(i, int):
            u, v = i.split()
            u = int(u)
            v = int(v)
            edge = (u, v)
            if val == "true":
                val = True
            elif val == "false":
                val = False
            pt.edges[edge]['mot_value'] = val
        else:
            n = int(i)
            pt.nodes[n]['mot_value'] = val
    return nx.node_link_data(pt)


@app.callback(
    Output(PCI_P2R.CID_P2R_DIV_JSON_VIEWER_IN_JSON_VIEWER_MODAL, "data"),
    Input(PCI_P2R.CID_P2R_STORE_LIVE_PT, 'data')
)
def update_jv(mot_data):
    mot = nx.node_link_graph(mot_data)
    m = message_from_mot(mot)
    # TODO m can also be a list/dict of message!
    try:
        data = m.to_dict()
        return data
    except AttributeError:
        return {}

# # TODO modularize these classes
# CUSTOM_CARD_CLASSES = [Compound, ReactionInput, ReactionOutcome, ProductCompound]
# def get_reaction_input_card(pt_reaction_input: nx.DiGraph, pt_main: nx.DiGraph):
#     # make sure this is a reaction input prototype
#     root_node = get_root(pt_reaction_input)
#     root_node_class_string = pt_reaction_input.nodes[root_node]['mot_class_string']
#     assert root_node_class_string == get_class_string(ReactionInput), f"expecting {get_class_string(ReactionInput)}," \
#                                                                       f" was given {root_node_class_string}"
#     for u, v, d in pt_reaction_input.edges(data=True):
#         d: MotEleAttr
#         assert d['mot_state'] != PT_PLACEHOLDER
#
#     input_divs = []
#     for leaf in get_leafs(pt_reaction_input, sort=True):
#         input_div = get_element_input(pt_main, leaf)
#         input_divs.append(input_div)
#
#     card = dbc.Card(
#         [dbc.CardHeader([
#             html.B("Reaction Input: ", className="text-primary"),
#             html.B(mot_get_path(pt_main, root_node, delimiter='dot')),
#         ],
#         ),
#             dbc.CardBody(input_divs)], className="mt-3"
#     )
#     return card


