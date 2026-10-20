import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rumor_sim.cli import init_files, main
from rumor_sim.config import smoke_config, single_event_config, validate_config
from rumor_sim.runner import execute, load_event_file, attach_donor_profiles
from rumor_sim.storage import read_json
from rumor_sim.report import build_report, collect_report_data
from rumor_sim.provider import MockDecisionProvider, BudgetExceeded
from rumor_sim import core


class SingleEventTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        init_files(self.root)
        self.event, _ = load_event_file(self.root / 'data/synthetic_event.json')
        self.config = smoke_config()
        self.config['social'] = single_event_config()['social']

    def tearDown(self): self.tmp.cleanup()

    def test_single_continuous_run_risk_set_and_resume(self):
        out = self.root / 'timeline'
        results = execute(self.event, [], self.config, out, mode='timeline', tg=20, allow_synthetic=True)
        self.assertEqual(len(results), 1)
        folders = list((out / 'runs').iterdir())
        self.assertEqual(len(folders), 1)
        manifest = read_json(folders[0] / 'manifest.json')
        self.assertIsNone(manifest['prefix_path'])
        self.assertEqual(manifest['initial_round'], 0)
        before = read_json(folders[0] / 'rounds/00019.json.gz')['state']
        after = read_json(folders[0] / 'rounds/00020.json.gz')['state']
        self.assertEqual(after['risk_ids'], sorted(aid for aid,a in before['agents'].items() if a['belief_state']=='accept'))
        for path in sorted((folders[0] / 'rounds').glob('*.json.gz'))[:19]:
            record = read_json(path)
            for d in record['decisions']:
                self.assertNotIn('policy', d['view'])
                self.assertTrue(all(p['author_id']!='GOV' for p in d['view']['visible_posts']))
        resumed = MockDecisionProvider()
        self.assertEqual(execute(self.event, [], self.config, out, mode='timeline', tg=20,
            allow_synthetic=True, provider=resumed), results)
        self.assertEqual(resumed.decisions, 0)

    def test_report_preserves_mode_rounds_and_escapes_text(self):
        event = copy.deepcopy(self.event)
        event['rumor_text'] += '</script><script>throw new Error("injected")</script>'
        out = self.root / 'report'
        execute(event, [], self.config, out, mode='timeline', allow_synthetic=True)
        run = next((out / 'runs').iterdir())
        data = collect_report_data(run)
        self.assertEqual(data['mode'], 'mock')
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(len(data['metrics']), 80)
        self.assertEqual(sum(len(a['states']) for a in data['agents'].values()), 800)
        self.assertEqual(sum(len(a['decisions']) for a in data['agents'].values()), data['summary']['decision_calls'])
        result = build_report(run)
        text = Path(result['report']).read_text(encoding='utf-8')
        self.assertNotIn('</script><script>throw new Error', text)
        self.assertIn('离线流程演示', text)
        self.assertNotIn('raw_user_id', text)

    def test_partial_run_report_is_explicit_and_resumable(self):
        class Stops(MockDecisionProvider):
            def decide(self, view, call_identity):
                if self.decisions >= 9: raise BudgetExceeded('Offline fixture stop')
                return super().decide(view, call_identity)
        out = self.root / 'partial'
        with self.assertRaises(BudgetExceeded):
            execute(self.event, [], self.config, out, mode='timeline', allow_synthetic=True, provider=Stops())
        run = next((out / 'runs').iterdir())
        data = collect_report_data(run)
        self.assertEqual(data['status'], 'budget_exhausted')
        self.assertFalse(data['summary']['complete'])
        self.assertLess(data['last_round'], 80)
        build_report(run)
        execute(self.event, [], self.config, out, mode='timeline', allow_synthetic=True)
        self.assertEqual(collect_report_data(run)['status'], 'completed')

    def test_social_config_validation_and_http_requires_budget(self):
        validate_config(single_event_config())
        bad = copy.deepcopy(self.config); bad['social']['thread_comment_slots'] = 6
        with self.assertRaises(ValueError): validate_config(bad)
        code = main(['single-event','--config',str(self.root/'config/smoke.json'),
            '--event',str(self.root/'data/synthetic_event.json'),'--allow-synthetic',
            '--provider','http','--output',str(self.root/'no_calls')])
        self.assertEqual(code, 2)
        self.assertFalse((self.root/'no_calls').exists())


if __name__=='__main__': unittest.main()
