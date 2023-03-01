import os

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, get_asset_url

from cyto_app.components import get_navbar, navbar_callback
from cyto_app.cyto_config import DASH_CID_NAVBAR

os.environ['LOGURU_LEVEL'] = 'WARNING'

app_folder = os.path.dirname(os.path.abspath(__file__))

app = Dash(
    name=__name__,
    title="Prototype Editor",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    # url_base_pathname='/prototype_editor/',
)
app._favicon = os.path.join(app_folder, "assets/favicon.ico")

navlinks = [
    dbc.NavLink(
        f"{page['description']}", href=page["relative_path"], className="mx-2", active='exact',
        style={"color": "#ffffff"}
    ) for page in dash.page_registry.values()
]

navbar = get_navbar(navlinks, DASH_CID_NAVBAR)
navbar_callback(app, DASH_CID_NAVBAR)

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "1rem 1rem",
    "z-index": "0",
}
content = html.Div(id="page-content", children=[dash.page_container], style=CONTENT_STYLE)

app.layout = html.Div(
    [
        navbar,
        content,
        dcc.Markdown("dummy", style={"display": "none"}, id="dummy"),
    ],
    # trick from https://stackoverflow.com/questions/35513264
    style={"width": "100vw"}
)

server = app.server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8070, debug=True)
