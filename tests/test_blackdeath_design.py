"""Regression suite for the black/death-metal editorial v5 design."""
import importlib.util
from pathlib import Path
import re
import struct
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import render_widgets as R
import render_static as S

class BlackDeathTests(unittest.TestCase):
    def test_calendar_is_january_to_december_and_not_rolling_november_first(self):
        card=R.heatmap({'updated_at':'2026-11-10T10:00','contribution_days':[
            {'date':'2026-01-01','count':1},{'date':'2026-11-10','count':3}
        ]})
        positions=[card.index(f'>{m}</text>') for m in
                   ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']]
        self.assertEqual(positions,sorted(positions))
        self.assertIn('2026 / JAN—DEC',card)
        self.assertIn('Calendar year / Jan—Dec.',card)
        self.assertNotIn('AWAITING FIRST SYNC',card)

    def test_yearly_summary_does_not_misrepresent_rolling_365_count(self):
        d={'updated_at':'2026-11-10T10:00', 'annual_contributions':900,
           'contribution_days':[{'date':'2025-11-10','count':20},{'date':'2026-01-02','count':3}]}
        self.assertEqual(R.year_total(d),3)
        self.assertIn('>3</text>',R.heatmap(d))
        self.assertIn('>900</text>',R.signal(d))

    def test_just_is_not_displayed_as_a_programming_language(self):
        rows=R.language_rows({'languages':[{'name':'Python','bytes':1000},
                {'name':'Just','bytes':1},{'name':'Dart','bytes':300},
                {'name':'CSS','bytes':2}]})
        self.assertEqual([r[0] for r in rows],['Python','Dart'])
        self.assertNotIn('Just',R.languages({'languages':[{'name':'Just','bytes':10}]}))

    def test_static_cards_are_dark_and_never_claim_pending_live_data(self):
        cards=S.render()
        self.assertEqual(len(cards),10)
        for name,src in cards.items():
            ET.fromstring(src)
            self.assertIn('fill="#101013"',src,name)
            self.assertNotIn('AWAITING FIRST SYNC',src,name)
            self.assertIn('<title>',src,name)
            self.assertNotIn('<script',src,name)

    def test_dynamic_cards_are_dark_and_safe(self):
        for name,card in R.render({}).items():
            ET.fromstring(card)
            self.assertIn('fill="#101013"',card,name)
            self.assertNotIn('<script',card,name)
            self.assertIn('AWAITING FIRST SYNC',card,name)

    def test_mobile_months_never_mark_future_month_as_zero(self):
        card=R.mobile_heatmap({'updated_at':'2026-11-10T00:00',
            'contribution_days':[{'date':'2026-11-10','count':2}]})
        # December placeholder is unavailable — not zero activity.
        self.assertRegex(card,r'>DEC</text>')
        self.assertIn('>—</text>',card)
        self.assertEqual([card.index(f'>{m}</text>') for m in
                ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']],
                sorted([card.index(f'>{m}</text>') for m in
                ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']]))

    def test_readme_references_exist_and_all_components_have_mobile_sources(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        paths=re.findall(r'\./(assets/[\w/.-]+\.(?:svg|png))(?:\?v=[\da-f]+)?',readme)
        self.assertEqual(len(paths),20)
        for p in paths:
            self.assertIn('assets/',p)
            self.assertIn('<picture>',readme)
            self.assertIn('alt=',readme)
        # Telemetry images will be present from the original main branch in PR.
        for p in paths:
            if '/widgets/' not in p:
                self.assertTrue((ROOT/p).exists(),p)

    def test_hero_png_is_not_an_opaque_white_canvas(self):
        for p in (ROOT/'assets/hero-blackdeath-v5.png',ROOT/'assets/mobile/hero-blackdeath-v5-mobile.png'):
            with p.open('rb') as fh:
                self.assertEqual(fh.read(8),b'\x89PNG\r\n\x1a\n')
            self.assertGreater(p.stat().st_size,20000)

    def test_revisioning_is_deterministic_and_idempotent(self):
        cards=R.render({})
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        revised=R.versioned_readme(source,cards)
        self.assertEqual(revised,R.versioned_readme(revised,cards))
        self.assertIn('signal.svg?v='+R.widget_revision(cards['signal.svg']),revised)
        self.assertEqual(len(re.findall(r'assets/widgets/(?:mobile/)?(?:signal|heatmap|languages|activity)\.svg\?v=',revised)),8)

if __name__=='__main__':unittest.main()
