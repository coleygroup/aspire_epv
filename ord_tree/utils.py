import inspect
import pathlib
import sys
import typing
from importlib import import_module

import networkx as nx
import pygraphviz

FilePath = typing.Union[str, pathlib.Path]


def read_file(fn: FilePath) -> str:
    with open(fn, "r") as f:
        return f.read()


_RootNodeId = "<ROOT>"
_NodeDelimiter = "|"


class MessageTypeTreeError(Exception): pass


class MessageObjectTreeError(Exception): pass


def get_root(tree: nx.DiGraph):
    return [n for n, d in tree.in_degree() if d == 0][0]


def get_leafs(tree: nx.DiGraph, sort=True):
    assert nx.is_arborescence(tree)
    leafs = [n for n in tree.nodes if tree.out_degree(n) == 0]
    if sort:
        root_node = get_root(tree)
        leafs = sorted(leafs, key=lambda x: len(nx.shortest_path(tree, root_node, x)), reverse=True)
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


def is_arithmetic(lst, known_delta=None):
    if known_delta:
        delta = known_delta
    else:
        delta = lst[1] - lst[0]
    for index in range(len(lst) - 1):
        if not (lst[index + 1] - lst[index] == delta):
            return False
    return True
