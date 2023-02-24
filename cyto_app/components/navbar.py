import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from .callback import simple_open

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
                            dbc.Col(html.Img(src="https://raw.githubusercontent.com/Open-Reaction-Database/ord-schema/main/logos/logo.svg", height="30px")),
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
