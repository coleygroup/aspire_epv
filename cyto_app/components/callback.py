import plotly.graph_objects as go


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
