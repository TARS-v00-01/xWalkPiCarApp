# xWalk PiCar applications

xWalkPiCarApp integrates the Python desktop GUI, native Android application and PC model training tools
with their IW schemas and development tools.
This public repository owns integration metadata, documentation, its licence, and CI configuration.
Component code stays in five private repositories; this repository pins their submitted commits as submodules.
The hardware integration is [xWalkPiCarAI](https://github.com/TARS-v00-01/xWalkPiCarAI).

## Clone and build

Your GitHub account needs read access to all five components and the private protocol reference repositories
xWalkLibrary, xWalk-rpi5-trace, and xWalk-rpi5-node. Authenticate before cloning:

```bash
gh auth login --hostname github.com --git-protocol https
gh auth setup-git
git clone --recurse-submodules https://github.com/TARS-v00-01/xWalkPiCarApp.git
cd xWalkPiCarApp
./update-submodules.sh
python3 -B xWalk-rpi5-tool/py-agent/gerrit-tool/py-src/xWalkAppIntegration.py references .
```

The reference helper fetches three pinned protocol contracts into ignored `build/protocol-contracts` for validation.
`INTEGRATION.json` records only their source revisions, paths, and blob identifiers. No reference code is
committed here. Follow the component guides after restoring these build references:

| Component | Purpose |
| --- | --- |
| [xWalk-rpi5-iw](xWalk-rpi5-iw/README.md) | Shared Protobuf schemas |
| [xWalk-rpi5-tool](xWalk-rpi5-tool/README.md) | Development, verification, and Gerrit tooling |
| [xWalk-arm64-app](xWalk-arm64-app/README.md) | Android application and build instructions |
| [xWalk-pcx86-app](xWalk-pcx86-app/README.md) | Python desktop GUI and setup instructions |
| [xWalk-pcx86-model](xWalk-pcx86-model/README.md) | Model training, dataset preparation and validation |

For an existing clone, fetch the integration revision and initialize its exact component commits:

```bash
git submodule sync --recursive
./update-submodules.sh
python3 -B xWalk-rpi5-tool/py-agent/gerrit-tool/py-src/xWalkAppIntegration.py references .
```

Do not use `git submodule update --remote` for a reproducible integration build.

`update-submodules.sh` restores Android and desktop assets and the model input dataset after source updates,
even when their source revisions are unchanged. It installs local `post-checkout` and `post-merge` hooks
so subsequent plain `git submodule update` commands restore assets when a component revision changes.
Git does not run these hooks for an unchanged submodule; use the update script to repair missing assets.
Existing hooks and custom hook directories are preserved. Hooks are local Git configuration and need
installation in each clone; the update script handles this automatically.

Downloads use each component's pinned `ci/assets.json` revision, with SHA-256 verification and cached reuse.
The model input dataset is restored to `xWalk-pcx86-model/xWalkModelResources/xWalkInput`.
Set `HF_TOKEN` or configure the Hugging Face entry in `~/.netrc` for private dataset access on new machines
and CI runners. A download failure returns a nonzero exit status; rerun the update script after fixing access.
For an asset-only offline restore, run `bash ci/restore-app-assets.sh --offline`.


## Quality and publication

Gerrit and GitHub share the Preparation, IW, tooling, Python, model, Android, xWalk Quality,
and Host Quality Gate jobs.
They check schema compatibility, tooling regressions, Python tests, Android provisioning, JVM tests, lint,
and APK builds. Host CI never connects to robot hardware. Run the shared graph locally with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B xWalk-rpi5-tool/py-agent/gerrit-tool/py-src/xWalkAppIntegrationCi.py .
```

The managed GitHub runner fetches exact submitted component commits from Gerrit with its pinned SSH identity.
Develop changes in their owning component repositories. Upload to Gerrit, wait for CI Verified +1, obtain
Code-Review +2, and submit. Submitted component commits then enter this repository through gitlink uplift
reviews. Uplifts change the owning submodule pointer; they do not copy its source files.
The synchronization service publishes only the exact submitted integration commit to GitHub.
Never push source changes directly to GitHub.

## Licence

This integration uses [GPL-3.0-only](LICENSE), following xWalkPiCarAI. Components retain their own copyright
and licence notices. Public integration metadata does not grant access to the private component repositories.

Shared IW and tooling submissions each open one uplift review here and one in `xWalkPiCarAI`.
GitHub Host Quality exposes schema validation, Python host tests, Android provisioning, lint, JVM tests,
and APK builds through named steps from the same check definitions used by Gerrit.

## Python and Java quality matrix

The required `xWalk Quality` job waits for both app jobs and uses the same checks as Gerrit:

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
