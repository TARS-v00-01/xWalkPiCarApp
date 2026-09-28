"""Exercise real Git submodule hooks using local fixture repositories."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

CI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('asset_hooks', CI / 'install-asset-hooks.py')
hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hooks)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.STDOUT).strip()


class AssetWorkflowTests(unittest.TestCase):
    def test_submodule_checkout_and_unchanged_update(self):
        for app in ('xWalk-arm64-app', 'xWalk-pcx86-app', 'xWalk-pcx86-model'):
            with self.subTest(app=app):
                self.check_submodule_checkout_and_unchanged_update(app)

    def check_submodule_checkout_and_unchanged_update(self, app):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / 'source'
            source.mkdir()
            git(source, 'init')
            git(source, 'config', 'user.name', 'Test')
            git(source, 'config', 'user.email', 'test@example.invalid')
            (source / 'ci').mkdir()
            (source / 'ci/assets.json').write_text('{}')
            (source / 'ci/fetch-assets.sh').write_text('#!/bin/sh\ncd "$(dirname "$0")/.."\nprintf restored > asset\n')
            git(source, 'add', '.')
            git(source, 'commit', '-m', 'First')
            first = git(source, 'rev-parse', 'HEAD')
            (source / 'revision').write_text('second')
            git(source, 'add', '.')
            git(source, 'commit', '-m', 'Second')
            root = base / 'integration'
            root.mkdir()
            git(root, 'init')
            git(root, '-c', 'protocol.file.allow=always', 'submodule', 'add', str(source), app)
            module = root / app
            hooks.install(root)
            git(module, 'checkout', first)
            self.assertEqual((module / 'asset').read_text(), 'restored')
            (module / 'asset').unlink()
            git(root, 'submodule', 'update', '--no-fetch')
            self.assertEqual((module / 'asset').read_text(), 'restored')
            (module / 'asset').unlink()
            shutil.copytree(CI, root / 'ci', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(CI.parent / 'update-submodules.sh', root)
            subprocess.run(['bash', str(root / 'update-submodules.sh'), '--no-fetch'], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual((module / 'asset').read_text(), 'restored')
            hook = Path(git(module, 'rev-parse', '--git-path', 'hooks')) / 'post-checkout'
            hook.write_text('#!/bin/sh\n# existing user hook\n')
            hooks.install(root)
            self.assertIn('existing user hook', hook.read_text())


if __name__ == '__main__':
    unittest.main()
