#!/usr/bin/env python3
"""Install local asset hooks without replacing existing or shared custom hooks."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MARKER = '# xWalk pinned runtime asset hook'
HOOK = '''#!/usr/bin/env bash
# xWalk pinned runtime asset hook
set -euo pipefail
# The sourced environment restores once after Git, including unchanged revisions.
if [[ "${XWALK_ENV_UPDATING:-0}" == 1 || "${XWALK_SKIP_ASSETS:-0}" == 1 ]]; then
    exit 0
fi
# A path-only checkout does not select a new asset manifest.
if [[ "${3:-1}" == 0 ]]; then
    exit 0
fi
root="$(git rev-parse --show-toplevel)"
if [[ -f "$root/ci/assets.json" && -f "$root/ci/fetch-assets.sh" ]]; then
    bash "$root/ci/fetch-assets.sh"
fi
'''


def install(root):
    for app in ('xWalk-arm64-app', 'xWalk-pcx86-app', 'xWalk-pcx86-model'):
        module = root / app
        if not (module / '.git').exists():
            continue
        custom = subprocess.run(['git', '-C', str(module), 'config', '--get', 'core.hooksPath'],
                                capture_output=True, text=True)
        if custom.returncode == 0:
            print(f'WARNING {app}: custom hooks preserved; use update-submodules.sh to restore assets')
            continue
        path = subprocess.check_output(['git', '-C', str(module), 'rev-parse',
                                        '--git-path', 'hooks'], text=True).strip()
        directory = Path(path)
        if not directory.is_absolute():
            directory = module / directory
        directory.mkdir(parents=True, exist_ok=True)
        for name in ('post-checkout', 'post-merge'):
            hook = directory / name
            if hook.is_symlink() or (hook.exists() and MARKER not in hook.read_text()):
                print(f'WARNING {app}: existing {name} preserved; use update-submodules.sh')
                continue
            hook.write_text(HOOK)
            hook.chmod(0o755)
        print(f'INFO Asset hooks configured for {app}')


if __name__ == '__main__':
    install(ROOT)
