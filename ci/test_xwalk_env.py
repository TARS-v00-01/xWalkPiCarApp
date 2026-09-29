"""Verify the sourced environment against local Git repositories without network or real assets."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'xwalk_env.sh'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True,
                                   stderr=subprocess.STDOUT,
                                   env=dict(os.environ, GIT_CONFIG_NOSYSTEM='1',
                                            GIT_CONFIG_GLOBAL='/dev/null')).strip()


def init(root):
    root.mkdir()
    git(root, 'init', '-b', 'master')
    git(root, 'config', 'user.name', 'Test')
    git(root, 'config', 'user.email', 'test@example.invalid')


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / 'component-source'
        init(self.source)
        (self.source / 'ci').mkdir()
        (self.source / 'ci/assets.json').write_text('{}')
        (self.source / 'ci/fetch-assets.sh').write_text(
            '#!/bin/bash\ncd "$(dirname "$0")/.."\n'
            '[[ ! -f fail-assets ]] || exit 23\n'
            'printf restored > asset\n')
        (self.source / '.gitignore').write_text('asset\nrestore-count\nfail-assets\n')
        git(self.source, 'add', '.')
        git(self.source, 'commit', '-m', 'First')
        self.first = git(self.source, 'rev-parse', 'HEAD')
        self.root = self.base / 'integration with spaces'
        init(self.root)
        git(self.root, '-c', 'protocol.file.allow=always', 'submodule', 'add',
            str(self.source), 'component')
        shutil.copy2(SCRIPT, self.root)
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-m', 'Integration')
        self.module = self.root / 'component'
        self.env = dict(os.environ, XWALK_TEST_ROOT=str(self.root),
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
        # Fixture tests must not inherit caller credentials or asset behavior switches.
        for name in ('HF_TOKEN', 'XWALK_SKIP_ASSETS', 'XWALK_ENV_UPDATING'):
            self.env.pop(name, None)

    def shell(self, code, cwd=None):
        return subprocess.run(['bash', '--noprofile', '--norc', '-c', code],
                              cwd=cwd or self.root, env=self.env, text=True, capture_output=True)

    def test_setup_and_unchanged_update_restore(self):
        result = self.shell('source ./xwalk_env.sh && rm component/asset && git submodule update')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.module / 'asset').read_text(), 'restored')

    def test_activation_has_no_download_and_supports_c_option(self):
        result = self.shell('source "$XWALK_TEST_ROOT/xwalk_env.sh" --activate && '
                            'test ! -e "$XWALK_TEST_ROOT/component/asset" && '
                            'git -C "$XWALK_TEST_ROOT" submodule update', self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.module / 'asset').exists())

    def test_unchanged_pull_and_failed_git(self):
        upstream = self.base / 'upstream'
        git(self.base, 'clone', '--bare', str(self.root), str(upstream))
        git(self.root, 'remote', 'add', 'origin', str(upstream))
        git(self.root, 'fetch', 'origin')
        git(self.root, 'branch', '--set-upstream-to=origin/master', 'master')
        dry = self.shell('source ./xwalk_env.sh --activate && git pull --dry-run')
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse((self.module / 'asset').exists())
        result = self.shell('source ./xwalk_env.sh --activate && git pull --ff-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.module / 'asset').exists())
        (self.module / 'asset').unlink()
        result = self.shell('source ./xwalk_env.sh --activate && git pull missing-remote')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.module / 'asset').exists())

    def test_restore_failure_is_reported_after_successful_git(self):
        (self.module / 'fail-assets').touch()
        result = self.shell('source ./xwalk_env.sh --activate && git submodule update')
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertIn('Git succeeded', result.stderr)
        strict = self.shell('set -e; source ./xwalk_env.sh --activate; git submodule update')
        self.assertEqual(strict.returncode, 23, strict.stderr)
        self.assertIn('Git succeeded', strict.stderr)
        self.assertEqual(git(self.module, 'rev-parse', 'HEAD'), self.first)

    def test_source_only_and_unrelated_commands(self):
        result = self.shell('source ./xwalk_env.sh --activate && '
                            'XWALK_SKIP_ASSETS=1 git submodule update && git status --short')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.module / 'asset').exists())
        result = self.shell('source "$XWALK_TEST_ROOT/xwalk_env.sh" --activate && git status --short',
                            self.source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.source / 'asset').exists())

    def test_existing_function_is_preserved(self):
        result = self.shell('git() { printf custom; }; source ./xwalk_env.sh --activate; git')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'custom')
        self.assertIn('existing git shell function', result.stderr)

    def test_multiple_integrations_and_shell_state(self):
        other = self.base / 'second-integration'
        init(other)
        (other / '.gitmodules').touch()
        shutil.copy2(SCRIPT, other)
        self.env['XWALK_TEST_SECOND'] = str(other)
        result = self.shell('set -u; before="$PWD"; '
                            'source ./xwalk_env.sh --activate && '
                            'source "$XWALK_TEST_SECOND/xwalk_env.sh" --activate && '
                            'source ./xwalk_env.sh --activate && '
                            'test "$PWD" = "$before" && '
                            'git -C "$XWALK_TEST_SECOND" submodule update && git submodule update')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.module / 'asset').exists())

    def test_custom_hooks_are_not_replaced(self):
        hookdir = self.root / 'custom-hooks'
        hookdir.mkdir()
        hook = hookdir / 'post-checkout'
        original = '#!/bin/sh\nprintf custom > custom-marker\n'
        hook.write_text(original)
        hook.chmod(0o755)
        git(self.module, 'config', 'core.hooksPath', str(hookdir))
        (self.source / 'next').touch()
        git(self.source, 'add', '.')
        git(self.source, 'commit', '-m', 'Next')
        git(self.module, 'fetch', 'origin')
        git(self.module, 'checkout', 'origin/master')
        result = self.shell('source ./xwalk_env.sh --activate && git submodule update')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(hook.read_text(), original)
        self.assertTrue((self.module / 'custom-marker').exists())
        self.assertTrue((self.module / 'asset').exists())


if __name__ == '__main__':
    unittest.main()
