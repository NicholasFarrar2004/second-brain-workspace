"""Behavioral tests use independently constructed temporary workspaces only."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_workspace.py'
spec = importlib.util.spec_from_file_location('workspace_checker', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='second-brain-test-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / 'example'
        self.project = 'Areas/Exhibit Projects/Poster Display'
        self.other = 'Areas/Workshop Projects'
        self.document = {'schema_version': 1, 'routes': {
            'poster-display': {'project': self.project, 'references': ['00_Resources/display-checklist.md']},
            'workshop-kit': {'project': self.other, 'references': []}}}
        for owner in ('', 'Areas/Exhibit Projects', self.project, self.other):
            for filename in ('AGENTS.md', 'MEMORY.md'):
                self.write(str(Path(owner) / filename), '# Fictional rules or facts\n')
        for owner in (self.project, self.other):
            self.write(owner + '/Handoff.md', '# State\nFictional draft ready.\n')
        self.write('00_Resources/display-checklist.md', '# Checklist\nCheck readability.\n')
        self.write('README.md', '[Checklist](00_Resources/display-checklist.md)\n')
        self.save_config()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def save_config(self):
        self.write('workspace.json', json.dumps(self.document))

    def check(self, route='poster-display'):
        return checker.check_workspace(self.root, route)

    def codes(self, result):
        return {item['code'] for item in result['errors']}

    def test_exact_context_order_and_sizes(self):
        result = self.check()
        self.assertTrue(result['ok'], result)
        expected = ['AGENTS.md', 'MEMORY.md', 'Areas/Exhibit Projects/AGENTS.md',
                    'Areas/Exhibit Projects/MEMORY.md', self.project + '/AGENTS.md',
                    self.project + '/MEMORY.md', self.project + '/Handoff.md',
                    '00_Resources/display-checklist.md']
        self.assertEqual([item['path'] for item in result['context']], expected)
        self.assertEqual(result['total_context_bytes'], sum((self.root / path).stat().st_size for path in expected))
        self.assertTrue(all(item['bytes'] == len((self.root / item['path']).read_bytes()) for item in result['context']))

    def test_no_route_has_no_implicit_context(self):
        result = self.check(None)
        self.assertTrue(result['ok'])
        self.assertEqual(result['context'], [])
        self.assertEqual(result['total_context_bytes'], 0)

    def test_missing_state_and_root_ownership(self):
        (self.root / self.project / 'Handoff.md').unlink()
        self.assertIn('missing_file', self.codes(self.check()))
        self.write(self.project + '/Handoff.md', '# Restored fictional state\n')
        (self.root / 'MEMORY.md').unlink()
        self.assertIn('missing_file', self.codes(self.check()))

    def test_unknown_route(self):
        result = self.check('imagined-route')
        self.assertFalse(result['ok'])
        self.assertEqual(result['context'], [])
        self.assertIn('unknown_route', self.codes(result))

    def test_schema_validation(self):
        for version in (2, True, '1'):
            with self.subTest(version=version):
                self.document['schema_version'] = version
                self.save_config()
                self.assertIn('invalid_schema', self.codes(self.check()))
        self.write('workspace.json', '{"schema_version":1,"schema_version":1,"routes":{}}')
        self.assertIn('invalid_schema', self.codes(self.check()))
        self.document['schema_version'] = 1
        self.document['routes']['poster-display']['references'] = 'not-a-list'
        self.save_config()
        self.assertIn('invalid_schema', self.codes(self.check()))

    def test_config_paths_cannot_escape(self):
        self.document['routes']['poster-display']['project'] = '../outside'
        self.save_config()
        result = self.check()
        self.assertFalse(result['ok'])
        self.assertEqual(result['context'], [])
        self.document['routes']['poster-display']['project'] = self.project
        self.document['routes']['poster-display']['references'] = [str(self.base / 'outside.md')]
        self.save_config()
        self.assertIn('path_escape', self.codes(self.check()))

    def test_references_required_and_context_deduplicated(self):
        self.document['routes']['poster-display']['references'] = ['AGENTS.md', 'AGENTS.md', 'missing.md']
        self.save_config()
        result = self.check()
        self.assertFalse(result['ok'])
        self.assertEqual([item['path'] for item in result['context']].count('AGENTS.md'), 1)
        self.assertIn('missing_file', self.codes(result))

    def test_unselected_branch_links_are_checked_but_context_not_selected(self):
        self.write(self.other + '/MEMORY.md', '[Missing](absent.md)\n')
        result = self.check()
        self.assertIn('broken_link', self.codes(result))
        self.assertFalse(any(item['path'].startswith(self.other) for item in result['context']))

    def test_local_link_cannot_escape(self):
        self.write('README.md', '[Outside](../outside.md)\n')
        (self.base / 'outside.md').write_text('Outside content')
        self.assertIn('path_escape', self.codes(self.check()))

    def test_markdown_forms_and_code_examples(self):
        self.write('00_Resources/guide (draft).md', '# Guide\n')
        self.write('00_Resources/guide(draft).md', '# Guide\n')
        text = r"""[Angle](<00_Resources/guide (draft).md> "title")
[Encoded](00_Resources/guide%20%28draft%29.md#section)
[Reference][check]
[check]: 00_Resources/display-checklist.md "Checklist"
![Image](00_Resources/display-checklist.md)
[Escaped](00_Resources/guide\(draft\).md)
[Online](https://example.invalid/no-request)
`[Code](missing-inline.md)`
```markdown
[Fenced](missing-fenced.md)
```
    [Indented](missing-indented.md)
"""
        self.write('README.md', text)
        self.assertTrue(self.check()['ok'], self.check())
        self.write('README.md', '[Reference][lost]\n[lost]: missing-reference.md\n')
        self.assertIn('broken_link', self.codes(self.check()))

    def test_other_branch_does_not_change_chosen_context(self):
        before = self.check()['context']
        self.write(self.other + '/MEMORY.md', '# Unrelated workshop facts\n' * 40)
        after = self.check()
        self.assertTrue(after['ok'])
        self.assertEqual(before, after['context'])

    def test_unicode_bytes_are_not_characters_or_tokens(self):
        self.write(self.project + '/MEMORY.md', 'Paper lantern: café 🏮\n')
        result = self.check()
        item = next(item for item in result['context'] if item['path'] == self.project + '/MEMORY.md')
        text = (self.root / item['path']).read_text()
        self.assertEqual(item['bytes'], len(text.encode('utf-8')))
        self.assertGreater(item['bytes'], len(text))

    def test_symlink_ancestor_not_followed(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'secret.md').write_text('External sentinel')
        try:
            (self.root / 'linked').symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation unavailable on this host')
        self.document['routes']['poster-display']['references'] = ['linked/secret.md']
        self.save_config()
        result = self.check()
        self.assertIn('symlink', self.codes(result))
        self.assertFalse(any(item['path'].startswith('linked/') for item in result['context']))
        self.assertNotIn('External sentinel', json.dumps(result))

    def test_tree_bytes_unchanged(self):
        def snapshot():
            return {path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.root.rglob('*') if path.is_file()}
        before = snapshot()
        self.assertTrue(self.check()['ok'])
        self.assertEqual(before, snapshot())

    def test_cli_default_is_independent_of_working_directory(self):
        scripts = self.base / 'scripts'
        scripts.mkdir()
        copied_script = scripts / 'check_workspace.py'
        shutil.copyfile(SCRIPT, copied_script)
        elsewhere = self.base / 'elsewhere'
        elsewhere.mkdir()
        env = dict(os.environ)
        env.pop('PYTHONPATH', None)
        command = [sys.executable, '-B', str(copied_script), '--route', 'poster-display', '--json']
        result = subprocess.run(command, cwd=elsewhere, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)['ok'])
        (self.root / self.project / 'Handoff.md').unlink()
        result = subprocess.run(command, cwd=elsewhere, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing_file', self.codes(json.loads(result.stdout)))


if __name__ == '__main__':
    unittest.main()
