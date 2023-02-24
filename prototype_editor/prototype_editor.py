import os.path

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from ord_tree.cyto_app.components import get_navbar, navbar_callback
from ord_tree.cyto_app.cyto_config import DASH_CID_NAVBAR

app_folder = os.path.dirname(os.path.abspath(__file__))

app = Dash(
    name=__name__,
    title="Prototype Editor",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    # url_base_pathname='/prototype_editor/',
)

navlinks = [
    dbc.NavLink(
        f"{page['description']}", href=page["relative_path"], className="mx-2", active='exact', style={"color": "#ffffff"}
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
    ]
)

server = app.server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8070, debug=True)
