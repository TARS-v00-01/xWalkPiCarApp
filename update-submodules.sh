#!/usr/bin/env bash
# Update pinned component sources, then restore their pinned runtime assets.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Git errors stop the workflow before asset installation. Never force local changes.
git -C "$root" submodule update --init --recursive "$@"
python3 "$root/ci/install-asset-hooks.py"
bash "$root/ci/restore-app-assets.sh"
