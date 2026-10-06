# xWalk PiCar applications

See the [Git guide](GIT_GUIDE.md) for cloning, source-only updates, submodules, and Gerrit reviews.

xWalkPiCarApp integrates the Python desktop GUI, native Android application, PC model training tools
and Yocto image tooling
with their IW schemas and development tools.
This public repository owns integration metadata, documentation, its licence, and CI configuration.
Component code stays in six private repositories; this repository pins their submitted commits as submodules.
The hardware integration is [xWalkPiCarAI](https://github.com/TARS-v00-01/xWalkPiCarAI).

## Request access and contribute

[Request private module access](https://github.com/TARS-v00-01/xWalkPiCarApp/issues/new?template=access-request.yml)
and follow the [contribution guide](CONTRIBUTING.md). Maintainers manually approve read-only access to selected
repositories. Approved contributors can propose fixes through private-fork pull requests; accepted changes
still go through Gerrit review, CI, and submission.

## Components

| Component | Purpose |
| --- | --- |
| [xWalk-rpi5-iw](xWalk-rpi5-iw/README.md) | Shared Protobuf schemas |
| [xWalk-rpi5-tool](xWalk-rpi5-tool/README.md) | Development, verification, and Gerrit tooling |
| [xWalk-arm64-app](xWalk-arm64-app/README.md) | Native Android application |
| [xWalk-pcx86-app](xWalk-pcx86-app/README.md) | Python desktop mobility application |
| [xWalk-pcx86-model](xWalk-pcx86-model/README.md) | Dataset packing, model training and image/video validation |
| [xWalk-rpi5-yocto](xWalk-rpi5-yocto/README.md) | Pi image builds, imager HUD and image validation |

## Start here

- For source review and editing, use [Source-only checkout](#source-only-checkout).
- To build or run applications, use [Clone and initialize](#clone-and-initialize).
- Follow the component READMEs above for Android, desktop mobility, or model training.
- For CI and contribution rules, see [Quality and publication](#quality-and-publication).

## Source-only checkout

Git stores source, configuration templates, notebooks, asset manifests, and integration metadata.
Large runtime assets and training datasets are restored separately. A workspace-level `traffic_dataset/`
directory is not required by this integration.

After authenticating GitHub access to the private components, run:

```bash
git clone https://github.com/TARS-v00-01/xWalkPiCarApp.git
cd xWalkPiCarApp
XWALK_SKIP_ASSETS=1 git -c core.hooksPath=/dev/null submodule update --init
```

For an existing checkout, preserve local edits before updating its pinned sources:

```bash
XWALK_SKIP_ASSETS=1 git -c core.hooksPath=/dev/null pull
XWALK_SKIP_ASSETS=1 git -c core.hooksPath=/dev/null submodule update
```

The per-command hook override skips checkout/merge hooks, including previously installed asset hooks,
without changing saved Git configuration. These commands fetch Git content without restoring Hugging Face
assets. They do not remove assets already present. Hugging Face credentials are unnecessary for source review.

`update-submodules.sh` always restores assets, including model inputs. Use it when preparing a full runtime
checkout. Application setup, Android builds, and mobility GUI startup can also restore assets; see each
component's requirements before running them.

## Set up the update environment

Use Bash 4.4+ and Python 3.9+; source [xwalk_env.sh](xwalk_env.sh) from this integration root once for initial setup:

```bash
source ./xwalk_env.sh
```

The script initializes the pinned submodules and restores assets from each initialized component that owns
`ci/assets.json` and `ci/fetch-assets.sh`. It uses the existing verified asset downloader, `HF_TOKEN` or
`~/.netrc`, and `XWALK_ASSET_CACHE` (default `~/.cache/xwalk-assets`). It does not store credentials or install
application/system dependencies. Follow the component setup instructions for build tools and Python packages.

After setup, the everyday update commands in that Bash session are:

```bash
git pull
git submodule update
```

These two commands update initialized components and restore their pinned assets. Save local work before
updating. If an integration update adds a new component, rerun `source ./xwalk_env.sh` to initialize it.
The environment setup handles recursive initialization; you do not need that flag for everyday updates.
The script adds a shell function that delegates to Git and restores pinned assets only after a successful
pull or submodule update in a registered integration. It also supports `git -C /path/to/checkout ...`.
Unrelated repositories and other Git commands retain normal behavior. Existing custom hooks are preserved.

Git checkout hooks do not run for unchanged revisions. The shell function covers that case, so rerunning
`git submodule update` repairs missing assets even when source is already current. A download failure returns
nonzero and reports that Git succeeded; resolve credentials/network/cache access and rerun the command.
Source and manifest verification remain separate: an asset failure does not roll back the Git update.

In each new terminal, activate without fetching or downloading:

```bash
source /path/to/xWalkPiCarApp/xwalk_env.sh --activate
```

Replace the path with your checkout. To enable this in every interactive Bash terminal, add that line to your
own `~/.bashrc`. Source both integrations' scripts to register both in one shell. If you already define a `git`
alias or function, reconcile it first; the script refuses to replace it. It preserves the working directory
and shell options. Running `bash ./xwalk_env.sh` performs setup, but cannot activate the calling terminal.

For a source-only update in an activated shell:

```bash
XWALK_SKIP_ASSETS=1 git -c core.hooksPath=/dev/null pull
XWALK_SKIP_ASSETS=1 git -c core.hooksPath=/dev/null submodule update
```

This per-command override skips hooks and asset restoration without deleting existing files. Do not use the
hook override for commits or review uploads. `command git` bypasses the shell function; other shells, IDE Git
clients, and subprocesses do not inherit it. Their existing checkout hooks only run when Git checks out a
revision. Keep using the sourced Bash session for automatic restoration on unchanged updates.

The application integration restores Android and desktop runtime assets and the model traffic inputs.
Configure Hugging Face read access before initial setup. These downloads require additional disk space.
The older `update-submodules.sh` wrapper remains available for scripts and shells without activation.

## Access and prerequisites

Your GitHub account needs read access to all six private components and the protocol reference repositories
`xWalkLibrary`, `xWalk-rpi5-trace`, and `xWalk-rpi5-node`. A public integration clone alone does not grant
component access. Source checkout requires Git and authenticated GitHub access; asset restoration uses Python 3.
Follow each component README for its build dependencies, Android SDK, or Python environment setup.

For a full runtime checkout, configure `HF_TOKEN` in your environment or the `huggingface.co` entry in
`~/.netrc` with a token that can read these private Hugging Face datasets. Keep credentials outside Git.

| Dataset | Restored content |
| --- | --- |
| `joxjoh24/xWalk-arm64-app-assets` | Android artwork, video, map and inference assets |
| `joxjoh24/xWalk-pcx86-app-assets` | Desktop artwork, video, map and inference assets |
| `joxjoh24/xWalkTrafficDataset` | Model image/video inputs and dataset audit |

## Clone and initialize

This path prepares all three applications, including the model input dataset. For a code-only checkout,
use [Source-only checkout](#source-only-checkout) instead.

Run these commands from the directory where you want to create the checkout:

```bash
gh auth login --hostname github.com --git-protocol https
gh auth setup-git
git clone https://github.com/TARS-v00-01/xWalkPiCarApp.git
cd xWalkPiCarApp
source ./xwalk_env.sh
python3 -B xWalk-rpi5-tool/py-agent/gerrit-tool/py-src/xWalkAppIntegration.py references .
```

The environment script initializes the exact pinned submodules and restores their assets. It does not install
application dependencies or start training. The reference helper fetches three pinned protocol contracts into
ignored `build/protocol-contracts`; `INTEGRATION.json` records their revisions, paths and blob identifiers.
No reference source is committed to this integration.

To start the model desktop after initialization:

```bash
cd xWalk-pcx86-model
./setup.sh
./xWalkModel --gui
```

For headless training, packing and validation, follow the model's [CLI guide](xWalk-pcx86-model/CLI_GUIDE.md).
Android and mobility application setup remain documented in their component READMEs.

## Update an existing checkout

Run from a clean integration checkout on `master`:

```bash
source ./xwalk_env.sh --activate
git pull
git submodule update
```

If protocol-reference pins change and you need build/CI validation, refresh them separately with the
`references .` command shown in [Clone and initialize](#clone-and-initialize).

Preserve local work before updating. Do not use `git submodule update --remote` for a reproducible build:
the integration pins exact submitted component revisions.
These commands restore all application assets. Use the [source-only commands](#source-only-checkout) when
you only need code. See the [Git guide](GIT_GUIDE.md#preserve-work-and-recover-from-common-problems) for saving
changes inside individual component repositories before updating.

## Automatic assets and model inputs

`update-submodules.sh` restores assets even when source revisions are unchanged. Each component's
`ci/assets.json` pins the Hugging Face revision, file sizes and SHA-256 checksums. Valid local files are reused;
missing or mismatched files are restored from a verified cache or downloaded before atomic replacement.
The default cache is `~/.cache/xwalk-assets`; `XWALK_ASSET_CACHE` selects another cache directory.

The model inputs are restored under:

```text
xWalk-pcx86-model/xWalkModelResources/xWalkInput/
    xWalkTrafficDataset/       Images, YOLO labels and split metadata
    xWalkTrafficVideos/        Videos and frame annotations
    xWalkDatasetAudit.json     Dataset audit
```

These are raw packing inputs. Packed training datasets, trained weights and generated reports are separate
local resources; restoring inputs does not create them. See the [model README](xWalk-pcx86-model/README.md).

The wrapper installs local `post-checkout` and `post-merge` hooks for the three applications. Once installed,
plain `git submodule update` restores assets when it checks out a different component revision. Git does not
run these hooks when the revision is unchanged; use the wrapper to repair missing assets in that case.
Existing hooks and custom hook directories are preserved. Every new clone needs its own hook installation.

For asset-only operations from the integration root:

```bash
bash ci/restore-app-assets.sh
bash ci/restore-app-assets.sh --check
bash ci/restore-app-assets.sh --offline
```

`--check` verifies local files without downloads. `--offline` restores only from valid local files and cache
entries. Missing credentials, unavailable files or checksum failures return a nonzero status; fix the cause and
rerun the restore. Asset restoration does not contact the robot or start training.

## Quality and publication

Gerrit and GitHub share the Preparation, IW, tooling, Python, model, Yocto, Android, xWalk Quality,
and Host Quality Gate jobs.
They check schema compatibility, tooling regressions, Python tests, model Python/notebook syntax and asset
restoration tests, Yocto builder/validator/offscreen GUI checks, Android provisioning, JVM tests, lint,
and APK builds. Host CI never connects to robot hardware.
Run the shared graph locally with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B xWalk-rpi5-tool/py-agent/gerrit-tool/py-src/xWalkAppIntegrationCi.py .
```

The managed GitHub runner fetches exact submitted component commits from Gerrit with its pinned SSH identity.
Develop changes in their owning component repositories. Upload to Gerrit, wait for CI Verified +1, obtain
Code-Review +2, and submit. Submitted component commits then enter this repository through gitlink uplift
reviews. Uplifts change the owning submodule pointer; they do not copy its source files.
The synchronization service publishes submitted component commits to their private GitHub repositories.
After complete integration CI, approval and submission, it publishes the exact integration commit to GitHub.
Never push source changes directly to GitHub.

Yocto submissions open an app uplift and run the complete app graph. The dedicated Yocto host checks never
run bitbake or flash an SD card. Schema-2 metadata requires its exact submitted gitlink.

Shared IW and tooling submissions each open one uplift review here and one in `xWalkPiCarAI`.
GitHub Host Quality exposes schema validation, Python host tests, Android provisioning, lint, JVM tests,
and APK builds through named steps from the same check definitions used by Gerrit.

## Python and Java quality matrix

The required `xWalk Quality` job waits for the mobility Python and Android jobs and uses the same checks as
Gerrit. The separate model job checks its host dependencies, Python/notebook syntax, asset downloader and model
regressions. Both jobs must pass the final Host Quality Gate. The mobility/Android quality matrix is:

| Python | Java / Android |
| --- | --- |
| Ruff syntax, control-flow and undefined-name analysis | Debug and Release Android Lint |
| All host tests with branch coverage (minimum 75%) | Release APK build and JVM tests |
| 50 races with eight simultaneous duplicate responses | 100 races with eight simultaneous duplicate responses |
| Seeded malformed-input and calibration probes | 5,000 seeded malformed-Protobuf and calibration probes |
| Retained allocation and sample-bound regression | JaCoCo reports with whole-app and critical-class limits |

Every check has its own duration, status, log, and report artifacts. GitHub publishes logs and XML summaries;
source-annotated coverage HTML stays in the private CI workspace. Failures block the Host Quality Gate.
Generated bindings are excluded from coverage; handwritten GUI code remains included. JVM whole-app baselines
are 13% lines and 15% branches because UI lifecycle execution needs separate emulator tests. ResponseGate requires
95% line/branch coverage; SpeedEstimator requires 90% lines and 75% branches. Python's threshold combines statement
and branch coverage. These are regression limits, not claims that all application behavior is tested.

Input probes use fixed seeds and bounded corpora. They are smoke tests, not coverage-guided Jazzer/Atheris runs.
The memory probe checks Python odometry retention; it is not a general leak detector or an Android LeakCanary run.
No robot, broker, emulator, or hardware tests are started by this job.

## Licence

This integration uses [GPL-3.0-only](LICENSE), following xWalkPiCarAI. Components retain their own copyright
and licence notices. Public integration metadata does not grant access to the private component repositories.
