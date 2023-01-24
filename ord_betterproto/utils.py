import inspect
import pathlib
import sys
import typing
from importlib import import_module

import networkx as nx
import pygraphviz

FilePath = typing.Union[str, pathlib.Path]
DotPathLabel = "DotPath"
RootDotPath = "ROOT"


class MessageTypeTreeError(Exception): pass


class MessageObjectTreeError(Exception): pass


def get_leafs(tree: nx.DiGraph, sort=True):
    assert nx.is_arborescence(tree)
    leafs = [n for n in tree.nodes if tree.out_degree(n) == 0]
    if sort:
        leafs = sorted(leafs, key=lambda x: len(nx.shortest_path(tree, 0, x)), reverse=True)
    return leafs


def write_dot(g: nx.Graph, fn: FilePath = None):
    ag = nx.nx_agraph.to_agraph(g)
    ag.graph_attr['splines'] = 'curved'
    ag.graph_attr['rankdir'] = "LR"
    if fn is None:
        return ag.to_string()
    with open(fn, "w") as f:
        f.write(ag.to_string())


def read_dot(fn: FilePath) -> typing.Union[nx.Graph, nx.DiGraph]:
    with open(fn, "r") as f:
        s = f.read()
    ag = pygraphviz.AGraph().from_string(s)
    return nx.nx_agraph.from_agraph(ag)


def get_class_string(o):
    if inspect.isclass(o):
        c = o
    else:
        c = o.__class__
    m_name = c.__module__
    c_name = c.__name__
    return f"{m_name}.{c_name}"


# copied from https://docs.djangoproject.com/en/dev/_modules/django/utils/module_loading/
def cached_import(module_path, class_name):
    # Check whether module is loaded and fully initialized.
    if not (
            (module := sys.modules.get(module_path))
            and (spec := getattr(module, "__spec__", None))
            and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path)
    return getattr(module, class_name)


# copied from https://docs.djangoproject.com/en/dev/_modules/django/utils/module_loading/
def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    try:
        return cached_import(module_path, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


def assign_dotpath(
        tree: nx.DiGraph, node_subset=None,
        delimiter=".", root_dotpath=RootDotPath, root=0, edge_attr="label", node_attr=DotPathLabel
):
    """ add dotpath to tree nodes """
    if node_subset is None:
        node_subset = tree.nodes
    for n in node_subset:
        path_to_root = nx.shortest_path(tree, root, n)
        if n == root:
            dotpath = root_dotpath
        else:
            edge_path = list(zip(path_to_root[:-1], path_to_root[1:]))
            dotpath = delimiter.join([str(tree.edges[e][edge_attr]) for e in edge_path])
        tree.nodes[n][node_attr] = dotpath


def get_dotpath_dict(tree: nx.DiGraph, dict_type: typing.Literal["n2p", "p2n", "e2p", "p2e"]) -> dict:
    if "n" in dict_type:
        d = nx.get_node_attributes(tree, DotPathLabel)
        if dict_type == "p2n":
            d = {v: k for k, v in d.items()}
        assert len(set(d.keys())) == len(set(d.values())) == len(tree.nodes)
    elif "e" in dict_type:
        d = nx.get_edge_attributes(tree, DotPathLabel)
        if dict_type == "p2e":
            d = {v: k for k, v in d.items()}
        assert len(set(d.keys())) == len(set(d.values())) == len(tree.edges)
    else:
        raise ValueError(f'`dict_type` must be one of {["n2p", "p2n", "e2p", "p2e"]}')
    return d
