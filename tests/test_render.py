import importlib.util
import pathlib
import unittest
from xml.etree import ElementTree

SCRIPT=pathlib.Path(__file__).resolve().parent.parent / 'scripts' / 'render_widgets.py'
spec=importlib.util.spec_from_file_location('render_widgets',SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class WidgetTests(unittest.TestCase):
    def test_empty_cards_valid_svg(self):
        for fn in (mod.signal,mod.heatmap,mod.langs,mod.recent):
            svg=fn({})
            ElementTree.fromstring(svg)
            self.assertNotIn('<script',svg)
    def test_svg_escapes_activity(self):
        svg=mod.recent({'events':[{'action':'PR <script>','repo':'mine/a&b','when':'2026-11-10'}]})
        ElementTree.fromstring(svg)
        self.assertIn('mine/a&amp;b',svg)
        self.assertNotIn('<script>',svg)
    def test_calendar_example(self):
        svg=mod.heatmap({'annual_contributions':2,'contribution_days':[
            {'date':'2026-11-08','count':1},{'date':'2026-11-09','count':1}
        ]})
        ElementTree.fromstring(svg)
    def test_event_whitelist(self):
        self.assertIsNone(mod.parse_event({'type':'SecretPrivateEvent'}))
        self.assertEqual(mod.parse_event({'type':'PushEvent','repo':{'name':'pub/repo'},'created_at':'2026-11-09T00:00:00Z'})['action'],'PUSH / MAINLINE')

if __name__=='__main__':unittest.main()