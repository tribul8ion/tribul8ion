"""Static SVG regression + GitHub API fixture tests. Zero network access."""
import importlib.util
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parent.parent
SPEC=importlib.util.spec_from_file_location('renderer', ROOT/'scripts/render_widgets.py')
R=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)

class WidgetTests(unittest.TestCase):
    def test_all_empty_cards_have_valid_svg(self):
        cards=R.render({})
        self.assertEqual(set(cards), {'signal.svg','heatmap.svg','languages.svg','activity.svg',
                                     'mobile/signal.svg','mobile/heatmap.svg','mobile/languages.svg','mobile/activity.svg'})
        for name,src in cards.items():
            root=ElementTree.fromstring(src)
            self.assertEqual(root.attrib['viewBox'].split()[2], str(R.MW if name.startswith('mobile/') else R.W), name)
            self.assertIn('<title>',src)
            self.assertNotIn('<script>',src)
        self.assertIn('AWAITING FIRST SYNC',cards['signal.svg'])
        self.assertNotIn('843',cards['signal.svg'])

    def test_local_fixture_renders_all_cards(self):
        data=json.loads((ROOT/'tests/preview-fixture.json').read_text('utf-8'))
        for card in R.render(data).values():
            ElementTree.fromstring(card)
        self.assertIn('PYTHON',R.render(data)['languages.svg'].upper())

    def test_user_data_is_xml_escaped_and_control_chars_removed(self):
        dirty='<script>\u202e & "danger"'
        card=R.activity({'events':[{'action':dirty,'repo':'user/a&b','when':'2026-11-10'}]})
        ElementTree.fromstring(card)
        self.assertNotIn('<script>',card)
        self.assertNotIn('\u202e',card)
        self.assertIn('user/a&amp;b',card)

    def test_unexpected_event_does_not_leak(self):
        self.assertIsNone(R.parse_event({'type':'SecretEvent','repo':{'name':'private/stuff'}}))
        x=R.parse_event({'type':'PushEvent','repo':{'name':'pub/repo'},'created_at':'2026-11-10T00:00:00Z'})
        self.assertEqual(x['action'],'PUSH / COMMITS')

    def test_heatmap_handles_sparse_and_large_counts(self):
        src=R.heatmap({'contribution_days':[{'date':'2026-11-09','count':999999},
                                                  {'date':'2026-11-10','count':0}],
                              'annual_contributions':999999})
        ElementTree.fromstring(src)
        self.assertIn('999,999',src)

    def test_no_remote_dependencies_in_production_widgets(self):
        for name,content in R.render({}).items():
            stripped=content.replace('http://www.w3.org/2000/svg','')
            self.assertFalse(re.search(r'https?://|<script|<foreignObject|data:',stripped,re.I),name)

    def test_repo_placements_exist(self):
        readme=(ROOT/'README.md').read_text('utf-8')
        for path in re.findall(r'\./(assets/[\w/.-]+\.svg)',readme):
            self.assertTrue((ROOT/path).exists(),path)

    def test_fallback_is_not_fictional(self):
        for name,src in R.render({}).items():
            self.assertNotIn('example/public',src)
            self.assertIn('AWAITING FIRST SYNC',src)


    def test_widget_cache_keys_are_content_addressed_and_idempotent(self):
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        cards=R.render({})
        first=R.versioned_readme(source,cards)
        self.assertEqual(first,R.versioned_readme(first,cards))
        for name,content in cards.items():
            key='./assets/widgets/'+name+'?v='+R.widget_revision(content)
            self.assertIn(key,first)
        modified=dict(cards)
        modified['signal.svg']=cards['signal.svg']+'\\n'
        second=R.versioned_readme(first,modified)
        self.assertNotEqual(first,second)
        self.assertEqual(R.versioned_readme(second,modified),second)
        self.assertIn('./assets/widgets/signal.svg?v='+R.widget_revision(modified['signal.svg']),second)
        self.assertIn('./assets/widgets/mobile/signal.svg?v='+R.widget_revision(cards['mobile/signal.svg']),second)

    def test_tracked_readme_cache_keys_match_public_widget_files(self):
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        for name in R.render({}):
            svg=(ROOT/'assets/widgets'/name).read_text(encoding='utf-8')
            expected='./assets/widgets/'+name+'?v='+R.widget_revision(svg)
            self.assertIn(expected,source)

    def test_palette_contrast(self):
        def lum(h):
            rgb=[int(h[i:i+2],16)/255 for i in (1,3,5)]
            c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
            return .2126*c[0]+.7152*c[1]+.0722*c[2]
        bg=lum(R.C['panel'])
        for fg in ('bone','body','muted','subtle','oxide'):
            v=lum(R.C[fg]);ratio=(max(v,bg)+.05)/(min(v,bg)+.05)
            self.assertGreaterEqual(ratio,4.5,(fg,ratio))

if __name__=='__main__':unittest.main()
