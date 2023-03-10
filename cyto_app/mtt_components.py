import dash_bootstrap_components as dbc
import networkx as nx
from dash import html, dcc

from cyto_app.cyto_elements import MttNodeAttr
from ord_tree.mtt import OrdEnumClasses, BuiltinLiteralClasses, OrdMessageClasses
from ord_tree.utils import import_string, NodePathDelimiter


def get_edge_attr_block(u: str, v: str, mtt: nx.DiGraph):
    u_attrs = MttNodeAttr(**mtt.nodes[u])
    v_attrs = MttNodeAttr(**mtt.nodes[v])

    items = []
    for attrs, st in zip((u_attrs, v_attrs), ('Source Path', 'Target Path')):
        path = attrs['mtt_node_name']
        path = dcc.Markdown(
            " &rarr; ".join([f"_{p}_" for p in path.split(NodePathDelimiter)])
        )
        item_path = dbc.ListGroupItem([html.H6(st), path])
        items.append(item_path)

    list_group = dbc.ListGroup(items)

    relation = v_attrs['mtt_relation_to_parent']
    block = dbc.Card(
        [
            dbc.CardHeader([html.B(relation, className="text-primary"), ]),
            dbc.CardBody(list_group),
        ],
        className="mb-3"
    )
    return block


def get_node_attr_block(mtt_node_attr: MttNodeAttr, mtt: nx.DiGraph):
    node_class = import_string(mtt_node_attr['mtt_class_string'])
    class_name = node_class.__name__

    # node path
    path = mtt_node_attr['mtt_node_name']
    path = dcc.Markdown(
        " &rarr; ".join([f"_{p}_" for p in path.split(NodePathDelimiter)])
    )
    item_path = dbc.ListGroupItem([html.H6("Node Path"), path])

    # node children
    item_children = [html.H6("Children"), ]
    show_children = False
    markdown_text = ""
    for child in mtt.successors(mtt_node_attr['mtt_node_name']):
        child_attrs = MttNodeAttr(**mtt.nodes[child])
        child_class = import_string(child_attrs['mtt_class_string'])
        relation = child_attrs['mtt_relation_to_parent']
        if child_class in BuiltinLiteralClasses:
            suffix = "[BuiltinLiteral]"
        elif child_class in OrdEnumClasses:
            suffix = "[OrdEnum]"
        elif child_class in OrdMessageClasses:
            suffix = "[OrdMessage]"
        else:
            assert child_class in (list, dict)
            continue
        oneof_group = mtt_node_attr['mtt_relation_to_parent_oneof']
        if oneof_group:
            suffix += f"({oneof_group})"
        show_children = True
        markdown_text += f"* _{relation}_ @ `{child_class.__name__}{suffix}`\n"
    item_children.append(dcc.Markdown(markdown_text))
    item_children = dbc.ListGroupItem(item_children)

    list_items = []
    list_items.append(item_path)
    if show_children:
        list_items.append(item_children)

    list_group = dbc.ListGroup(list_items)

    ref_link = "https://docs.python.org/3/tutorial/datastructures.html"
    if node_class in OrdMessageClasses:
        ref_link = f"https://github.com/open-reaction-database/ord-schema/blob/main/proto/reaction.proto#:~:text=message-,{class_name}"
    elif node_class in OrdEnumClasses:
        ref_link = f"https://github.com/open-reaction-database/ord-schema/blob/main/proto/reaction.proto#:~:text=enum%20{class_name}"

    block = dbc.Card(
        [
            dbc.CardHeader([html.B(class_name, className="text-primary"),
                            dbc.CardLink("Definition", href=ref_link, style={"float": "right"})]),
            dbc.CardBody(list_group),
        ],
        className="mb-3"
    )
    return block
