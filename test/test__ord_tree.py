import glob
import json
import os.path

import networkx as nx
import pytest

from ord_tree import OrdMessageClasses, read_file, import_string, get_mtt, write_dot, mtt_to_dict, write_file, \
    mtt_from_dict, get_mot, mot_to_dict, mot_from_dict, message_from_mot


@pytest.fixture
def ord_jsons():
    d = dict()
    for jf in glob.glob("fixture/ORD_*.json"):
        js = read_file(jf)
        t = os.path.basename(jf)
        t = t[4:].replace(".json", "")
        d[t] = js
    return d


class TestOrdBetterproto:

    def test__init(self):
        for c in OrdMessageClasses:
            c()

    def test__jsons_rw(self, ord_jsons):
        for t, js in ord_jsons.items():
            m = import_string(f"ord_betterproto.{t}")
            msg = m().from_json(js)
            js_rec = msg.to_json(indent=2)
            assert js_rec == js


class TestOrdTree:

    def test__get_mtt(self, ord_jsons):
        for t, js in ord_jsons.items():
            m = import_string(f"ord_betterproto.{t}")
            message = m().from_json(js)
            mtt = get_mtt(message.__class__)
            write_dot(mtt, f"output/mtt_{t}.dot")
            mtt_dict = mtt_to_dict(mtt)
            write_file(json.dumps(mtt_dict), f"output/mtt_{t}.json")

    def test__mtt_json_load(self, ord_jsons):
        for t, js in ord_jsons.items():
            mtt_json_file = f"output/mtt_{t}.json"
            mtt_dict = json.loads(read_file(mtt_json_file))
            mtt = mtt_from_dict(mtt_dict)
            assert nx.is_arborescence(mtt)

    def test__get_mot(self, ord_jsons):
        for t, js in ord_jsons.items():
            m = import_string(f"ord_betterproto.{t}")
            message = m().from_json(js)
            mot = get_mot(message)
            write_dot(mot, f"output/mot_{t}.dot")
            d = mot_to_dict(mot)
            write_file(json.dumps(d, indent=2), f"output/mot_{t}.json")

    def test__mot_json_load(self, ord_jsons):
        for t, js in ord_jsons.items():
            msg = import_string(f"ord_betterproto.{t}")
            message = msg().from_json(js)

            mot_json_file = f"output/mot_{t}.json"
            mot_dict = json.loads(read_file(mot_json_file))
            mot = mot_from_dict(mot_dict)
            assert nx.is_arborescence(mot)
            m = message_from_mot(mot)
            assert m.to_json() == message.to_json()
