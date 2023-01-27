import importlib
import inspect
import json
import typing

import networkx as nx

from ord_tree.tree_obj import message_object_to_message_object_tree, message_object_tree_to_message_object
from ord_tree.tree_type import TypeOfTypeHint
from ord_tree.type_hints import get_toth
from ord_tree.utils import FilePath, get_class_string, import_string, read_file

# for constructing objects in tree
importlib.import_module('ord_betterproto')
importlib.import_module('builtins')


def string_to_type_hint(s: str):
    """ https://stackoverflow.com/questions/67500755 """
    return typing._eval_type(typing.ForwardRef(s), globals(), globals())


class MttEncoder(json.JSONEncoder):
    def default(self, z):
        if inspect.isclass(z):
            return get_class_string(z)
        elif z.__class__ == TypeOfTypeHint:
            return z.name
        elif z.__class__ == typing._GenericAlias:
            return str(z)
        elif z.__class__ == typing._UnionGenericAlias:
            return str(z)
        else:
            return super().default(z)


class MttDecoder(json.JSONDecoder):
    """ https://stackoverflow.com/questions/48991911 """

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if dct.__class__ != dict:
            return dct
        if 'type_hint' in dct:
            dct['type_hint'] = string_to_type_hint(dct['type_hint'])
        if 'node_class' in dct:
            dct['node_class'] = import_string(dct['node_class'])
        if 'node_class_toth' in dct:
            dct['node_class_toth'] = TypeOfTypeHint[dct['node_class_toth']]
        return dct


class MotEncoder(json.JSONEncoder):
    def default(self, z):
        if inspect.isclass(z):
            return get_class_string(z)
        # non-literal nodes will lose their `node_object`
        if get_toth(z.__class__) in (TypeOfTypeHint.OrdMessage,):
            return None
        return super().default(z)


class MotDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if dct.__class__ != dict:
            return dct
        if 'node_class' in dct:
            dct['node_class'] = import_string(dct['node_class'])
        return dct


def mtt_to_json(mtt: nx.DiGraph, fn: FilePath = None):
    td = nx.cytoscape_data(mtt)
    if fn is None:
        return json.dumps(td, cls=MttEncoder)
    with open(fn, "w") as f:
        f.write(json.dumps(td, cls=MttEncoder))


def mtt_from_json_string(s: str):
    d = json.loads(s, cls=MttDecoder)
    return nx.cytoscape_graph(d)


def mtt_from_json_file(fn: FilePath):
    s = read_file(fn)
    return mtt_from_json_string(s)


def mot_to_json(mot: nx.DiGraph, fn: FilePath):
    td = nx.cytoscape_data(mot)
    with open(fn, "w") as f:
        f.write(json.dumps(td, cls=MotEncoder))


def mot_from_json(fn: FilePath):
    s = read_file(fn)
    d = json.loads(s, cls=MotDecoder)
    mot = nx.cytoscape_graph(d)
    # this trick makes sure `node_object` are constructed
    m = message_object_tree_to_message_object(mot)
    return message_object_to_message_object_tree(m)
