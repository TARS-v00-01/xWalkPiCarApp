# xWalkPiCarApp Git guide

Follow each workflow below in order. Commands identify where they must run.
Use Bash 4.4+, Git, Python 3.9+, and GitHub CLI for the authentication example.
The parent `MyPiCarX` directory is a workspace; `xWalkPiCarApp` is the integration Git repository.

- New checkout: [First-time setup](#first-time-setup).
- Existing checkout: [Everyday updates](#everyday-updates).
- Request access or propose a GitHub pull request: [Contribution guide](CONTRIBUTING.md).
- Make a change: [Configure Gerrit contribution](#configure-gerrit-contribution).
- Save work: [Preserve work and recover from common problems](#preserve-work-and-recover-from-common-problems).

## First-time setup

### Step 1: Authenticate GitHub access

Location: any directory. Your GitHub account needs read access to all private components listed at the end
of this guide. A public integration clone does not grant access to those components.

```bash
gh auth login --hostname github.com --git-protocol https
gh auth setup-git
```

Expected result: Git can fetch the private component repositories using your authenticated account.
Gerrit access is not needed to clone.

### Step 2: Clone and enter the integration

Location: the directory where you want to create `xWalkPiCarApp`.

```bash
git clone https://github.com/TARS-v00-01/xWalkPiCarApp.git
cd xWalkPiCarApp
```

Expected result: you are in the integration root containing `.gitmodules` and `xwalk_env.sh`.
The environment script in Step 4 will initialize the component checkouts.
If you already have this checkout, do not clone it again; enter its directory and continue with Step 3.

### Step 3: Prepare asset access

The setup restores assets from these private Hugging Face datasets:

- `joxjoh24/xWalk-arm64-app-assets`
- `joxjoh24/xWalk-pcx86-app-assets`
- `joxjoh24/xWalkTrafficDataset`

Use a read token authorized for all three datasets. Keep it in your existing `huggingface.co` entry in
`~/.netrc`, or enter it privately for this terminal:

```bash
read -r -s -p "Hugging Face read token: " HF_TOKEN
export HF_TOKEN
```

The input is hidden. Do not put the token in Git files or type it directly into a command saved in shell history.
Reserve disk space for application media, traffic inputs, and the verified download cache.

### Step 4: Set up the environment

Location: the integration root from Step 2.

```bash
source ./xwalk_env.sh
```

Expected result: pinned submodules are initialized, manifest-owned assets are verified/restored, and the
terminal prints `xWalk environment ready` with your checkout path. Resolve any reported errors before proceeding.
The script preserves custom Git hooks and uses `HF_TOKEN` or `~/.netrc` without saving credentials.
It does not install application dependencies, train models, or operate hardware.

Use `source`, because the Git shell function must be installed in your current terminal.
Executing `bash ./xwalk_env.sh` cannot activate its parent terminal. Build and application setup are separate;
follow the [main README](README.md) and the owning component README when you are ready to build or run.

For a checkout containing only source, follow the source-only instructions in the
[environment setup](README.md#set-up-the-update-environment) instead of restoring assets.

## Everyday updates

### Step 1: Open the checkout and activate this terminal

Location: your existing integration root. Replace `/path/to/xWalkPiCarApp` with its actual path.

```bash
cd /path/to/xWalkPiCarApp
source ./xwalk_env.sh --activate
```

`--activate` enables automatic asset restoration without fetching or downloading anything immediately.
Run it once per new Bash terminal. You may add the absolute-path source command with `--activate` to your own
`~/.bashrc` to activate future terminals automatically. Source each integration's script to register both.
An existing `git` alias or shell function must be reconciled first; setup will not replace it.

### Step 2: Check and preserve local work

Location: the integration root.

```bash
git status --short
git branch --show-current
git submodule foreach 'git status --short'
```

Expected result: you understand any local changes before updating. Use the integration's `master` branch for
this workflow. Finish or save edits in each dirty repository using the preservation steps below before
switching branches or updating. A stash in the parent does not save edits inside a submodule.

### Step 3: Pull and update

Location: the integration root, with the environment active.

```bash
git pull
git submodule update
```

These are the two everyday update commands. You do not need to type `--recursive`.
The first updates the integration; the second checks out the exact pinned commits of initialized components.
The active shell function restores pinned Hugging Face assets after each successful command, including when
Git reports no source changes. Missing files can therefore be repaired by repeating `git submodule update`.

If a new component is added, rerun `source ./xwalk_env.sh` to initialize it. If checkout URLs change,
run `git submodule sync` or rerun setup. Do not use `--remote`: it selects upstream revisions instead of the
integration's reviewed pins. If Git reports divergent branches, inspect the history before resolving them.

### Step 4: Verify the result

Location: the integration root.

```bash
git submodule status
git status --short
git submodule foreach 'git status --short'
```

A submodule-status line beginning with a space has the expected commit; `-` means uninitialized, `+` means a
different commit, and `U` means a conflict. File edits may still exist at a matching commit; inspect status too.

If restoration fails, the command returns nonzero and explains that Git succeeded but the assets did not.
Fix Hugging Face access, network, or cache availability, then rerun `git submodule update`. The Git update is
not rolled back. The shell function is active only in sourced Bash sessions; IDE Git and `command git` bypass it.
Existing checkout hooks can run in those clients, but Git does not run them for unchanged revisions.

## Configure Gerrit contribution

These steps are for submitting a change. GitHub provides clone/fetch access; Gerrit owns review and submission.
For direct Gerrit contribution, push only to Gerrit. Contributors without Gerrit access may instead open
a pull request from their own fork as described in [CONTRIBUTING.md](CONTRIBUTING.md); maintainers import
accepted proposals into Gerrit. Never push directly to or merge into the upstream GitHub repository.

### Step 1: Configure review transport from the integration root

Replace the example path with your checkout path. Your Gerrit account, registered SSH key, trusted server
host key, and any non-secret machine settings must already be configured.

```bash
cd /path/to/xWalkPiCarApp
xwalk_checkout_root="$PWD"
source xWalk-rpi5-tool/shell-agent/env-tool/git.sh
```

This configures Gerrit push transport for the integration and initialized components while retaining GitHub
fetch access. It may start an installed local Gerrit stack on push when automatic startup is enabled.
Non-secret overrides belong in `~/.config/xwalk/git-env.local.sh`; keep credentials outside Git.

### Step 2: Enter the repository that owns your change

For a component README change, this example starts from the integration root set in Step 1:

```bash
cd "$xwalk_checkout_root/xWalk-pcx86-app"
git status --short
git switch -c docs/readme-update
```

Choose a unique branch name. Submodules normally start at detached HEAD; the branch gives your work a durable
name. For an integration-owned README, Git guide, or CI change, stay in `$xwalk_checkout_root` and create the
branch there instead. Read the applicable `AGENTS.md` and project guidelines before editing.
Remain in this selected repository for Steps 3 through 7.

### Step 3: Check identity, push destination, and commit hook

```bash
git config user.name
git config user.email
git config --get core.hooksPath
git rev-parse --git-path hooks
git remote get-url --push origin
```

An unset `core.hooksPath` is normal. Configure your own author name/email if missing. The Gerrit `commit-msg`
hook adds the `Change-Id` used to match patch sets. Install it in each repository where you create review
commits, after sourcing the helper above. Use Git to resolve the hook path: a submodule's `.git` is normally a
file, so `.git/hooks/commit-msg` is not a valid submodule path.

For an absent hook, the following command creates its directory and downloads the hook from your configured
Gerrit server. It refuses to replace an existing file or symbolic link. If a hook already exists, inspect it
and integrate Gerrit's hook with the existing behavior instead. Do not disable hooks for review commits.

```bash
xwalk_commit_hook="$(git rev-parse --git-path hooks/commit-msg)"
test ! -e "$xwalk_commit_hook" && test ! -L "$xwalk_commit_hook" && mkdir -p -- "$(dirname -- "$xwalk_commit_hook")" && scp -O -p -P "$GERRIT_SSH_PORT" "${GERRIT_USER}@${GERRIT_SERVER_HOST}:hooks/commit-msg" "$xwalk_commit_hook" && chmod 0755 "$xwalk_commit_hook"
```

`scp -O` selects the SCP protocol used by Gerrit's SSH endpoint. Use the trusted host key established during
account setup. When a custom hooks directory is configured, confirm whether it is shared with other
repositories before adding a hook there.

The push destination must be the configured Gerrit project or xWalk Gerrit connector, never GitHub.
Re-source the helper after initializing additional components if their push transport is not configured.

### Step 4: Edit, validate, and stage the intended files

Make the change and run the owning component's relevant host checks. For a README-only edit:

```bash
git diff -- README.md
git diff --check
git add -- README.md
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Expected result: the staged diff contains exactly your intended changes. Substitute the actual file names
for other work. Component files must be committed inside that component; staging its parent pointer does
not commit those files. Physical hardware tests require separate explicit authorization and a safe setup.

### Step 5: Commit and inspect the message

```bash
git commit -s -m "docs: clarify setup and source checkout"
git log -1 --format=full
```

Replace the example message with an accurate description. `-s` adds your sign-off.
Verify that the commit message contains its Gerrit `Change-Id` footer before continuing.
If it is absent, fix the commit hook and amend this unsubmitted commit before uploading.

### Step 6: Upload one review

For an active review that starts CI:

```bash
git push origin HEAD:refs/for/master
```

Alternatively, upload as work in progress to defer CI:

```bash
git push origin HEAD:refs/for/master%wip
```

Choose one upload command. Expected result: Gerrit returns a review link. Open that review to inspect the
patch set and verification results. **Mark As Active** starts CI for a WIP review's current patch set.
Moving an active review into WIP does not start CI.

### Step 7: Address feedback and submit

For another patch set of the same unsubmitted review, make the requested edits, run relevant checks, stage
those files, and then:

```bash
git commit --amend --no-edit
git push origin HEAD:refs/for/master
```

Keep the original `Change-Id`. Wait for current-patch-set `Verified +1`, authorized `Code-Review +2`, resolved
blocking comments, and all remaining Gerrit submit requirements before submission. CI does not submit the
change. Do not amend an already submitted review; create a new commit and review for follow-up work.

### Step 8: Wait for integration and update your checkout

A submitted component change receives a separate gitlink uplift review. It changes the component pointer
rather than copying source. Shared IW and tooling submissions create one uplift in each integration;
application components target `xWalkPiCarApp`, and hardware components target `xWalkPiCarAI`.

Each uplift must pass complete integration CI and receive approval before submission. The synchronization
service publishes submitted components and the exact submitted integration revision to GitHub. Component pins
must be available there before integration publication. Never replace this process with a direct GitHub push.

After publication, return to the integration root. If you changed the integration itself on a topic branch,
first preserve remaining work and return to its `master` branch with `git switch master`.
Then follow the everyday update workflow:

```bash
cd "$xwalk_checkout_root"
git pull
git submodule update
```

Keep component topic branches until their submitted work has been verified.

## Preserve work and recover from common problems

### Step 1: Save edits in each dirty repository

Run inside the repository whose files you want to preserve:

```bash
git stash push -u -m "Before integration update"
git stash list
```

Repeat separately in each dirty component and then the integration if necessary. `-u` includes untracked
files, but not ignored datasets, build outputs, or environments. Record the stash entry associated with your work.

### Step 2: Restore the saved work on its branch

Return to the branch that owns the edits, inspect its stashes, and apply the selected one:

```bash
git stash list
git stash apply 'stash@{0}'
git status --short
```

Replace `stash@{0}` if your work is in a different entry. Applying retains the backup. Resolve conflicts and
review the restored files before dropping the matching stash. Avoid blanket `git clean -fdx` or
`git reset --hard` as an update procedure.

| Problem | Next action |
| --- | --- |
| Private clone denied | Check GitHub authentication and access to the failing component. |
| Asset restore failed | Fix Hugging Face read access/network/cache, then repeat `git submodule update`. |
| Detached HEAD with edits | Create a branch before committing or updating the component. |
| Unexpected submodule revision | Compare the checkout with the integration pin and preserve local commits. |
| Push points to GitHub | Source the integration Git helper and inspect the push URL before uploading. |
| Missing Change-Id | Configure the Gerrit hook and amend the unsubmitted commit. |

## Repository ownership reference

The public integration owns documentation, CI configuration, metadata, and exact component commit pointers.
Each private component has its own history and Gerrit reviews. Integration-owned files are reviewed in
`xWalkPiCarApp`.

| Component checkout path | Gerrit project |
| --- | --- |
| `xWalk-rpi5-iw` | `xWalk-rpi5-iw` |
| `xWalk-rpi5-tool` | `xWalk-rpi5-tool` |
| `xWalk-arm64-app` | `xWalk-arm64-app` |
| `xWalk-pcx86-app` | `xWalk-pcx86-app` |
| `xWalk-pcx86-model` | `xWalk-pcx86-model` |
