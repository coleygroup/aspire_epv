from typing import Union

import dash_bootstrap_components as dbc
from dash import html


class BtnPop:

    def __init__(
            self, name: str,
            button: dbc.Button,
            popover: dbc.Popover,
            selectors: list[Union[dbc.RadioItems, dbc.Checklist]]
    ):
        self.popover = popover
        self.button = button
        self.name = name
        self.selectors = selectors
        self.div_id = f"{name}__btnpop"

    def get_div(self):
        return html.Div([self.button, self.popover], id=self.div_id, className="d-inline")

    @classmethod
    def from_selectors(
            cls,
            name,
            btn_label: str,
            popover_header: str,
            selectors: list[Union[dbc.RadioItems, dbc.Checklist]],
    ):
        btn_id = f"{name}__btn"
        popover_id = f"{name}__popover"
        btn = dbc.Button(
            children=btn_label,
            id=btn_id,
            color="primary",
            className="mb-3 mx-3",
            n_clicks=0,
        )
        popover = dbc.Popover(
            [
                dbc.PopoverHeader(popover_header),
                dbc.PopoverBody(
                    selectors
                ),
            ],
            id=popover_id,
            target=btn_id,
            placement="bottom",
            is_open=False,
        )
        return cls(name, btn, popover, selectors)
