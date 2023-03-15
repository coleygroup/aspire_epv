# import json
# from bson.objectid import ObjectId
# import os
#
# import dash_bootstrap_components as dbc
# import dash_renderjson
# import networkx as nx
# from dash import html, Input, Output, dcc, ALL, register_page, get_app, State, ctx, no_update
# from pymongo import MongoClient
# from cyto_app.prototype_components import JsonTheme
# from ord_tree.mot import PT_PLACEHOLDER, MotEleAttr, mot_get_path, message_from_mot
# from ord_tree.ord_classes import OrdEnumClasses
# from ord_tree.utils import import_string, enum_class_to_options
# from cyto_app.cyto_config import *
#
# this_folder = os.path.dirname(os.path.abspath(__file__))
# # register_page(__name__, path="/p2r", description="P2R")
# app = get_app()
#
# CID_P2R_INPUT = "CID_P2R_INPUT"
# CID_P2R_INPUT_PARENT = "CID_P2R_INPUT_PARENT"
# CID_P2R_JVIEWER = "CID_P2R_JVIEWER"
# CID_P2R_STORE_PT = "CID_P2R_STORE_PT"
# CID_P2R_SELECT_PT = "CID_P2R_SELECT_PT"
# DASH_CID_P2R_PT_SELECTOR = "CID_P2R_PT_SELECTOR"
#
#
# client = MongoClient()
# db = client['ord_prototype']
#
# PROTOTYPE_IDS = [str(d["_id"]) for d in db['prototypes'].find()]
#
#
#
# def load_sample_pt() -> nx.DiGraph:
#     with open(f"{this_folder}/prototype.json", "r") as f:
#         sample_pt_data = json.load(f)
#     pt = nx.node_link_graph(sample_pt_data)
#     return pt
#
#
#
# SAMPLE_PT = load_sample_pt()
#
#
# def get_input_from_pt(pt: nx.DiGraph):
#     cards = []
#     for n, d in pt.nodes(data=True):
#         d: MotEleAttr
#         if d["mot_state"] != PT_PLACEHOLDER:
#             continue
#         node_class = import_string(d['mot_class_string'])
#         node_value = d['mot_value']
#         # TODO type name as var
#         cid = {'type': CID_P2R_INPUT, 'index': n}
#
#         if node_class == str:
#             # value_input = dbc.Input(type='text', value=node_value, id=cid)
#             value_input = dbc.Textarea(value=node_value, id=cid)
#         elif node_class == bool:
#             value_input = dbc.InputGroupText(
#                 dbc.Switch(value=node_value, id=cid, className="position-absolute top-50 start-50 translate-middle"),
#                 className="position-relative flex-fill")
#         elif node_class in (int, float):
#             value_input = dbc.Input(type='number', value=node_value, id=cid)
#         elif node_class in OrdEnumClasses:
#             value_input = dbc.Select(options=enum_class_to_options(node_class),
#                                      value=node_value, id=cid)
#         elif node_class == bytes:
#             # TODO make this better
#             value_input = dbc.Textarea(value=str(node_value), id=cid)
#         else:
#             raise TypeError(f"illegal literal class: {node_class}")
#
#         card = dbc.Card(
#             [dbc.CardHeader([
#                 html.B("Node ", className="text-primary"),
#                 html.B(mot_get_path(pt, n, arrow=True)),
#             ],
#             ),
#                 dbc.CardBody(value_input)], className="mt-3"
#         )
#         cards.append(card)
#
#     for u, v, d in pt.edges(data=True):
#         d: MotEleAttr
#         if d["mot_state"] != PT_PLACEHOLDER:
#             continue
#         cid = {
#             'type': CID_P2R_INPUT,
#             'index': f"{u} {v}"
#         }
#         c2 = dbc.Textarea(value=d['mot_value'], id=cid)
#         card = dbc.Card(
#             [dbc.CardHeader(
#                 [
#                     html.B("Source ", className="text-primary"),
#                     html.B(mot_get_path(pt, u, arrow=True), ),
#                 ]
#             ),
#                 dbc.CardBody(c2),
#                 dbc.CardFooter(
#                     [
#                         html.B("Target ", className="text-primary"),
#                         html.B(mot_get_path(pt, v, arrow=True), ),
#                     ]
#
#                 )
#             ], className="mt-3"
#         )
#         cards.append(card)
#     return cards
#
#
# layout = html.Div(
#     [
#         dcc.Store(id=CID_P2R_STORE_PT),
#         html.Div(
#             [
#                 dbc.Button("Select prototype", id=CID_P2R_SELECT_PT),
#                 dcc.Dropdown(
#                     id=DASH_CID_P2R_PT_SELECTOR,
#                     # placeholder="select prototype...",
#                     options=[{"label": i, "value": i} for i in ["SAMPLE",] + PROTOTYPE_IDS], className="mt-3"
#                 ),
#                 html.Div(id=CID_P2R_INPUT_PARENT)
#             ],
#             className="col-lg-6"
#         ),
#         html.Div(
#             id=CID_P2R_JVIEWER,
#             className="col-lg-5"
#         )
#     ], className="row"
# )
#
# @app.callback(
#     Output(CID_P2R_JVIEWER, "children"),
#     Output(CID_P2R_INPUT_PARENT, 'children'),
#     Input(CID_P2R_STORE_PT, 'data'),
# )
# def update_cards(mot_data):
#     mot = nx.node_link_graph(mot_data)
#
#     m = message_from_mot(mot)
#     data = m.to_dict()
#     return get_input_from_pt(mot), dash_renderjson.DashRenderjson(id="input", data=data, max_depth=1, theme=JsonTheme, invert_theme=True)
#
#
# @app.callback(
#     Output(CID_P2R_STORE_PT, "data"),
#     Input({'type': CID_P2R_INPUT, 'index': ALL}, 'value'),
#     Input({'type': CID_P2R_INPUT, 'index': ALL}, 'id'),
#     Input(DASH_CID_P2R_PT_SELECTOR, 'value'),
#     State(CID_P2R_STORE_PT, "data"),
# )
# def update_jv(p2r_values, p2r_ids, mongo_id, pt_data):
#     if mongo_id is None:
#         return no_update
#
#     for it in ctx.triggered_prop_ids.values():
#         if isinstance(it, str):
#             if it == DASH_CID_P2R_PT_SELECTOR:
#                 mot_data = db['prototypes'].find_one({"_id": ObjectId(mongo_id)})['node_link_data']
#                 return mot_data
#
#     if pt_data is None:
#         return no_update
#     pt = nx.node_link_graph(pt_data)
#     for val, j in zip(p2r_values, p2r_ids):
#         i = j['index']
#         if not isinstance(i, int):
#             u, v = i.split()
#             u = int(u)
#             v = int(v)
#             edge = (u, v)
#             if val == "true":
#                 val = True
#             elif val == "false":
#                 val = False
#             pt.edges[edge]['mot_value'] = val
#         else:
#             n = int(i)
#             pt.nodes[n]['mot_value'] = val
#     return nx.node_link_data(pt)
#
# @app.callback(
#     Output(DASH_CID_P2R_PT_SELECTOR, "options"),
#     Input(CID_P2R_SELECT_PT, "n_clicks")
# )
# def refresh(n_clicks):
#     ids = [str(doc['_id']) for doc in db['prototypes'].find()]
#     return ids
