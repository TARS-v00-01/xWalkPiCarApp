#!/usr/bin/env bash
# Restore the assets pinned by each initialized application checkout.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for app in xWalk-arm64-app xWalk-pcx86-app; do
    if [[ -f "$root/$app/ci/assets.json" && -f "$root/$app/ci/fetch-assets.sh" ]]; then
        bash "$root/$app/ci/fetch-assets.sh" "$@"
    fi
done
