import os

import dash
import dash_bootstrap_components as dbc
import flask
from dash import Dash, html

from cyto_app.components import get_navbar, navbar_callback

os.environ['LOGURU_LEVEL'] = 'WARNING'

server = flask.Flask(__name__)

app = Dash(
    name=__name__,
    title="Prototype Editor",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    server=server,
    suppress_callback_exceptions=True,
    assets_ignore=r'defer[A-z]*.js',
    # url_base_pathname='/prototype_editor/',
)

app_folder = os.path.dirname(os.path.abspath(__file__))
app._favicon = os.path.join(app_folder, "assets/favicon.ico")

nav_links = []
for page in dash.page_registry.values():
    description = page['description']
    href = page['relative_path']
    # skip things like "/prototype/<id>"
    if href.count("/") > 1:
        continue
    nav_link = dbc.NavLink(
        description, href=href, className="mx-2", active="exact", style={"color": "#ffffff"}
    )
    nav_links.append(nav_link)

navbar = get_navbar(nav_links, "DASH_CID_NAVBAR")
navbar_callback(app, "DASH_CID_NAVBAR")

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
    ],
    # trick from https://stackoverflow.com/questions/35513264
    style={"width": "100vw"}
)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8070, debug=True)
