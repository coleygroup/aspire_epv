import importlib
import inspect
import pathlib
import sys
import typing
from importlib import import_module
from typing import get_type_hints

import networkx as nx
import pygraphviz

# for `string_to_type_hint`
globals()['ord_betterproto'] = importlib.import_module('ord_betterproto')
globals()['builtins'] = importlib.import_module('builtins')

FilePath = typing.Union[str, pathlib.Path]
RootNodePath = "<ROOT>"
NodePathDelimiter = "|"
PrefixDictKey = "<DictKey>"
PrefixListIndex = "<ListIndex>"


def string_to_type_hint(s: str):
    """ https://stackoverflow.com/questions/67500755 """
    return typing._eval_type(typing.ForwardRef(s), globals(), globals())


def read_file(fn: FilePath) -> str:
    with open(fn, "r") as f:
        return f.read()


def write_file(s: str, fn: FilePath):
    with open(fn, "w") as f:
        f.write(s)


def get_path(tree: nx.DiGraph, node, edge_attr_name: str, root_path: str = RootNodePath):
    """
    get a string representation of the path from root to node

    :param tree:
    :param node:
    :param edge_attr_name:
    :param root_path:
    :return:
    """
    root = get_root(tree)
    p = nx.shortest_path(tree, source=root, target=node)
    if len(p) == 1:
        return root_path
    str_path = []
    for i in range(len(p) - 1):
        u = p[i]
        v = p[i + 1]
        str_p = str(tree.edges[(u, v)][edge_attr_name])
        str_path.append(str_p)
    return NodePathDelimiter.join(str_path)


def get_root(tree: nx.DiGraph):
    return [n for n, d in tree.in_degree() if d == 0][0]


def get_leafs(tree: nx.DiGraph, sort=True):
    assert nx.is_arborescence(tree)
    leafs = [n for n in tree.nodes if tree.out_degree(n) == 0]
    if sort:
        root_node = get_root(tree)
        leafs = sorted(leafs, key=lambda x: len(nx.shortest_path(tree, root_node, x)), reverse=True)
    return leafs


def is_leaf(tree: nx.DiGraph, node):
    return tree.out_degree(node) == 0


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
    """ if an array is arithmetic sequence """
    if known_delta:
        delta = known_delta
    else:
        delta = lst[1] - lst[0]
    for index in range(len(lst) - 1):
        if not (lst[index + 1] - lst[index] == delta):
            return False
    return True


def get_type_hints_without_private(obj):
    d = dict()
    for k, v in get_type_hints(obj).items():
        if k.startswith("_"):
            continue
        d[k] = v
    return d


def get_tree_depth(tree: nx.DiGraph):
    r = get_root(tree)
    deep = 0
    for n in tree.nodes:
        p = nx.shortest_path(tree, source=r, target=n)
        d = len(p) - 1
        if d > deep:
            deep = d
    return deep


def enum_class_to_options(enum_class):
    options = [
        {"label": e.name, "value": e.value} for e in enum_class
    ]
    return options
