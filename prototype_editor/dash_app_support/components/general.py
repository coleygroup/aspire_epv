import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, html

BAR_STYLE = {
    "z-index": "1",
}


def get_navbar(nav_links: list[dbc.NavLink], navbar_id="pvis_navbar"):
    bar = dbc.Row(
        [
            dbc.Col(nl, width="auto") for nl in nav_links
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="right",
    )

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(
                                src="https://raw.githubusercontent.com/Open-Reaction-Database/ord-schema/main/logos/logo.svg",
                                height="30px")),
                            dbc.Col(dbc.NavbarBrand("Prototype Editor", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://open-reaction-database.org/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id=f"{navbar_id}-toggler", n_clicks=0),
                dbc.Collapse(
                    bar,
                    id=f"{navbar_id}-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
        ),
        color="dark",
        dark=True,
        className="mb-3",
        style=BAR_STYLE,
    )
    return navbar


def navbar_callback(app, navbar_id: str):
    app.callback(
        Output(f"{navbar_id}-collapse", "is_open"),
        [Input(f"{navbar_id}-toggler", "n_clicks")],
        [State(f"{navbar_id}-collapse", "is_open")],
    )(simple_open)


def simple_open(n, is_open):
    if n:
        return not is_open
    return is_open


def close_other_components(is_open, *args):
    if is_open:
        return [False for _ in args]


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


JsonTheme = {
    "scheme": "monokai",
    "author": "wimer hazenberg (http://www.monokai.nl)",
    "base00": "#272822",
    "base01": "#383830",
    "base02": "#49483e",
    "base03": "#75715e",
    "base04": "#a59f85",
    "base05": "#f8f8f2",
    "base06": "#f5f4f1",
    "base07": "#f9f8f5",
    "base08": "#f92672",
    "base09": "#fd971f",
    "base0A": "#f4bf75",
    "base0B": "#a6e22e",
    "base0C": "#a1efe4",
    "base0D": "#66d9ef",
    "base0E": "#ae81ff",
    "base0F": "#cc6633",
}
