from datetime import datetime

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, get_app, Output, Input
from dash import register_page, dash_table
from dateutil.parser import parse
from dash_app_support.db import ENV_MONGO_COLLECTION, ENV_MONGO_DB, ENV_MONGO_URI
from pymongo import MongoClient

# TODO version history

MONGO_DB = MongoClient(ENV_MONGO_URI)[ENV_MONGO_DB]

register_page(__name__, path='/', description="Editor Home")
TABLE_PAGE_SIZE = 10


class PCI:  # page component ids
    PROTOTYPE_LIST = "HOME_PROTOTYPE_LIST"
    PROTOTYPE_LIST_REFRESH_BTN = "PROTOTYPE_LIST_REFRESH_BTN"
    PAGINATION = "HOME_PAGINATION"


layout = html.Div(
    [
        html.H3([
            "Prototype List",
            dbc.Button(
                id=PCI.PROTOTYPE_LIST_REFRESH_BTN,
                className="ms-3"
            ),
        ]),
        html.Hr(),
        dbc.Pagination(
            id=PCI.PAGINATION,
            max_value=2,
            active_page=1,
            min_value=1,
            fully_expanded=False,
            first_last=True,
            previous_next=True,
        ),
        html.Div(
            dash_table.DataTable(
                id=PCI.PROTOTYPE_LIST,
                markdown_options={'html': True},
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode='multi',
                row_selectable=False,
                row_deletable=False,
                page_action='native',
                page_current=0,
                page_size=TABLE_PAGE_SIZE,
                css=[dict(selector= "p", rule= "margin: 0; text-align: center")],

                style_as_list_view=True,
                style_cell={'padding': '5px'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Date', 'Region']
                ],

            ),
            className="mt-3"
        ),
    ]
)

app = get_app()


@app.callback(
    Output(PCI.PROTOTYPE_LIST, "data"),
    Output(PCI.PROTOTYPE_LIST, "columns"),
    Output(PCI.PROTOTYPE_LIST_REFRESH_BTN, "children"),
    Output(PCI.PAGINATION, "max_value"),
    Input(PCI.PAGINATION, "active_page"),
    Input(PCI.PROTOTYPE_LIST_REFRESH_BTN, "n_clicks"),
)
def change_page(page, n_clicks):
    page_size = TABLE_PAGE_SIZE
    n = MONGO_DB[ENV_MONGO_COLLECTION].count_documents({})
    df = get_prototype_dataframe(db=MONGO_DB, collection=ENV_MONGO_COLLECTION, page=page, page_size=page_size)
    data = df.to_dict('records')
    prefix = app.config['url_base_pathname']
    for d in data:
        object_id = d['_id']
        object_id_link_edit = f"[edit]({prefix}/edit/{object_id})".replace("//", "/")
        object_id_link_ins = f"[instantiate]({prefix}/instantiate/{object_id})".replace("//", "/")
        d['action'] = object_id_link_edit + " / " + object_id_link_ins
    df = pd.DataFrame.from_records(data)
    columns = [{"name": i, "id": i, "presentation": "markdown"} for i in df.columns]
    return data, columns, f"\u27F3 updated {datetime.now().strftime('%H:%M:%S')}", n // page_size + 1


def get_prototype_dataframe(db, collection=ENV_MONGO_COLLECTION, page=1, page_size=10):
    records = []
    to_skip = (page - 1) * page_size
    projection = {
        "_id": 1,
        "name": 1,
        "root_message_type": 1,
        "version": 1,
        "time_modified": 1,
    }
    for doc in db[collection].find({}, projection).skip(to_skip).limit(page_size):
        doc['_id'] = str(doc['_id'])
        try:
            d = doc['time_modified']
        except KeyError:
            records.append(doc)
            continue
        if isinstance(d, str):
            d = parse(d)
        doc['time_modified'] = d.strftime("%Y-%m-%d %H:%M:%S")
        records.append(doc)
    df = pd.DataFrame.from_records(records)
    return df
