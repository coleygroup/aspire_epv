from dash import register_page, dcc, html
import os

register_page(__name__, path='/', description="Home")
app_folder = os.path.dirname(os.path.abspath(__file__)) + "/../"

with open(f"{app_folder}/readme.md", "r") as f:
    readme = f.read()

layout = html.Div(
    [
        dcc.Markdown(readme),
    ]
)
