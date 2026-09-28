# Submitted component checkout

This action fetches the integration's exact component revisions from authenticated Gerrit remotes.
Each revision must be reachable from its component's submitted `master` history.
The five app components include tooling itself; a newer tool master must not replace its pinned revision.
After checkout, the tool restores the private protocol references recorded by `INTEGRATION.json`.

Self-hosted runners reuse their workspaces. Before switching an initialized component to its pinned
revision, the action preserves tracked edits, staged edits, and untracked files with `git stash
push --include-untracked`. It reports the component path and stash commit in the job log. Stashes
remain local under the integration's `.git/modules` metadata and are excluded from source artifacts.
Ignored build files are not stashed. An already clean component does not create another stash.

Automatic preservation requires `GITHUB_ACTIONS=true` and `GITHUB_WORKSPACE` to match the integration
root exactly. Outside that workspace, a dirty component stops checkout without modifying its files.
Credential, host-key, mapping, and submitted-history validation remain required.

To inspect preserved changes, use the component path and stash commit reported by the failed or
recovered job. For example, from the runner's integration checkout:

```bash
git -C xWalk-rpi5-tool stash list
git -C xWalk-rpi5-tool stash show --include-untracked --patch <stash-commit>
```

Do not restore those changes into a running CI job. Recover them into a separate development checkout
after reviewing their contents. Rerunning an older workflow still uses that commit's checkout script;
the corrected behavior applies to workflows containing this action version.

The host-only regression tests use temporary repositories and a local SSH stand-in:

```bash
python3 .github/actions/checkout-private-submodules/test_checkout.py
```
