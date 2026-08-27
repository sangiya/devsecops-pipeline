# devsecops-pipeline

A reusable, composable GitHub Actions DevSecOps pipeline: build, test,
coverage, SAST (bandit), SCA (pip-audit), secrets scanning (Gitleaks), SBOM
generation (CycloneDX), container scanning (Trivy), IaC scanning (Checkov),
DAST (OWASP ZAP), and a single quality-gate status check any consumer repo
can require — all as `workflow_call` reusable workflows, not a monolithic
script to copy-paste.

## Problem and motivation

Most "DevSecOps pipeline" reference repos are either a single giant YAML
file nobody can safely change, or a wall of tool names with no working
example behind them. This repo takes the opposite approach: nine small,
independently testable reusable workflows, each with typed inputs and a
documented default, composed by one orchestrator (`quality-gate.yml`) —
and a real, minimal FastAPI app (`demo-app/`) bundled specifically so
every stage has something genuine to build, test, and scan rather than a
placeholder.

## Independent, non-proprietary disclaimer

`demo-app` is a fabricated three-endpoint service written solely to give
this pipeline something real to run against; it is not derived from any
employer codebase.

## Business scenario

A platform team wants every service repo in their org to get the same
security/quality bar without hand-maintaining nine copies of the same
YAML. A consuming repo adds one small `ci.yml` that calls
`sangiya/devsecops-pipeline/.github/workflows/quality-gate.yml@main` with
its own working directory and thresholds; this repo demonstrates that
exact call against its own bundled `demo-app`.

## Architecture

```
devsecops-pipeline/
├── .github/
│   ├── actions/setup-python-cached/       Composite action: cached Python setup
│   └── workflows/
│       ├── reusable-build-test.yml            Lint, format, type-check, test+coverage
│       ├── reusable-sast-sca.yml                  bandit (SAST) + pip-audit (SCA)
│       ├── reusable-secrets-scan.yml                  Gitleaks over full git history
│       ├── reusable-sbom.yml                              CycloneDX SBOM from the built environment
│       ├── reusable-container-scan.yml                        Trivy against a built Docker image
│       ├── reusable-iac-scan.yml                                  Checkov against Terraform/K8s/Helm
│       ├── reusable-dast.yml                                          OWASP ZAP baseline against a running app
│       ├── quality-gate.yml                                              Orchestrator: composes all of the above
│       └── ci.yml                                                            Example caller, run against demo-app
├── demo-app/                                                                     Real FastAPI target app + tests
├── terraform-examples/                                                               Real, hardened Terraform for the IaC stage
└── docs/quality-gates.md                                                                 What blocks the gate and why
```

## Key design decisions

- **Nine small reusable workflows, one orchestrator.** Each
  `reusable-*.yml` file is independently callable and independently
  testable; `quality-gate.yml` composes them so a consumer gets one
  required status check instead of managing nine.
- **A real demo app, not a stub.** `demo-app` has input validation
  (`GreetRequest`'s regex-anchored `name` field), a health endpoint, real
  tests reaching 100% coverage, and was scanned locally with bandit
  (zero findings) and pip-audit (zero findings, after upgrading the
  venv's own `pip`/`setuptools` — see "What was and wasn't verified") —
  it exists to prove every stage actually runs against something, not to
  illustrate a vulnerability.
- **IaC scanning defaults to soft-fail; everything else hard-fails.** See
  `docs/quality-gates.md` for the reasoning — adoption shouldn't be the
  first thing IaC scanning breaks.
- **SBOM generation never gates the build.** An SBOM is evidence to keep,
  not a pass/fail signal — see `docs/quality-gates.md`.
- **`reusable-dast.yml` starts the target app itself** (via a
  caller-supplied `start-command`) rather than assuming one is already
  running, so the DAST stage is self-contained in CI.

## Functional capabilities

- Lint, format-check, strict type-check, and coverage-gated testing for
  a Python project.
- SAST via bandit and SCA via pip-audit, each independently callable.
- Full-history secrets scanning via Gitleaks.
- CycloneDX SBOM generation from the actual built environment (not a
  static requirements-file guess).
- Container image scanning via Trivy with SARIF upload to GitHub code
  scanning.
- IaC scanning via Checkov (Terraform/Kubernetes/Helm) with SARIF upload.
- DAST via OWASP ZAP's baseline scan against a self-started target.
- One composed quality gate a branch protection rule can require.

## Security and threat model

- **Secrets scanning covers full git history** (`fetch-depth: 0`), since
  a secret committed and later deleted is still a leak an attacker with
  clone access can recover.
- **Every scan stage uploads SARIF where the tool supports it**, so
  findings land in GitHub's native code scanning UI rather than being
  buried in a job log.
- **This repo's own CI (`ci.yml`) is the same call a consumer would
  make** — dogfooding, not a separate "trust us" example.
- **Out of scope:** this pipeline does not manage secrets themselves
  (rotation, vaulting) — only scans for accidentally committed ones — and
  does not include a runtime WAF or admission controller; those belong to
  the workload's own infrastructure (see `ai-cloud-platform`).

## AI/ML methodology and evaluation

Not applicable — this repo is CI/CD tooling, not an AI/ML component.

## API specification

Not applicable — `demo-app`'s three endpoints (`/healthz`, `/greet`,
`/version`) exist solely as a scan target; the pipeline itself has no API,
only `workflow_call` inputs (documented per-workflow above).

## Data model

Not applicable.

## Testing pyramid

- **`demo-app` has its own real test suite** (`demo-app/tests/`) —
  6 tests, 100% branch coverage, including negative cases (script-injection
  characters and digits rejected by the `GreetRequest` validator).
- **The pipeline's own workflows are validated structurally**: every
  workflow/action YAML file parses cleanly (checked with PyYAML; no
  `actionlint` binary was available in the environment this repo was
  built in — see "What was and wasn't verified").
- **`ci.yml` is a live integration test of the whole pipeline**: every
  push/PR to this repo actually runs `quality-gate.yml` against
  `demo-app`, so the composition itself is continuously exercised.

## CI/CD and DevSecOps pipeline

This repo *is* the CI/CD pipeline — see Architecture above. `ci.yml` is
its own example consumer.

## Deployment

Not a deployable service. A consumer repo "deploys" this pipeline by
adding a workflow that does:

```yaml
jobs:
  quality-gate:
    uses: sangiya/devsecops-pipeline/.github/workflows/quality-gate.yml@main
    with:
      working-directory: .
      dockerfile-directory: .
      iac-directory: infra
```

## Observability

Every stage uploads its findings as a build artifact or SARIF report
(coverage XML, bandit JSON, SBOM JSON, Trivy/Checkov SARIF) — see each
`reusable-*.yml`'s `upload-artifact`/`upload-sarif` step.

## Performance benchmarks

Not applicable in the traditional sense — see `performance-engineering-lab`
for TPS/latency benchmarking of an actual running service. This pipeline's
own runtime cost is bounded by each tool's own execution time, which was
not separately benchmarked.

## Cost considerations

All tooling used (bandit, pip-audit, Gitleaks OSS, cyclonedx-py, Trivy,
Checkov, OWASP ZAP) is free and open-source; the only cost is GitHub
Actions minutes, which scale with how many of the (independently toggle-able)
stages a consumer enables.

## What was and wasn't verified

- `demo-app`'s tests (pytest), lint/format (ruff), types (mypy), SAST
  (bandit), and SCA (pip-audit) were all **actually run locally** against
  a real virtual environment — see the results captured in this repo's
  own commit history and the coverage/scan output referenced above.
  pip-audit's first run found real known CVEs in the venv's bootstrapped
  `pip`/`setuptools` (not `demo-app`'s own dependencies, which were
  already clean); upgrading them resolved every finding.
- A real CycloneDX SBOM (84 components, spec version 1.6) was generated
  locally from `demo-app`'s environment with `cyclonedx-py`, proving that
  stage's command works end-to-end.
- Terraform in `terraform-examples/` passes `terraform validate` and
  `terraform fmt -check` (no AWS credentials needed).
- **The first real push to GitHub actually ran the full pipeline** (Gitleaks,
  Trivy, Checkov, and OWASP ZAP were not available to test locally, so this
  was the first real execution) and it found three genuine bugs, all now
  fixed:
  - `aquasecurity/trivy-action@0.28.0` was pinned to a version tag that
    doesn't exist — corrected to the real latest release, `v0.36.0`.
  - The container-scan and iac-scan jobs' SARIF upload steps failed with
    `Resource not accessible by integration` — the default `GITHUB_TOKEN`
    permissions don't include `security-events: write`. Fixed by adding an
    explicit `permissions:` block to both jobs.
  - The fresh Ubuntu runner's own bundled `setuptools` (79.0.1) had a real
    CVE (`PYSEC-2026-3447`) — the same class of finding hit locally against
    the dev venv's `pip`/`setuptools`. Fixed by upgrading pip/setuptools as
    the first step of the SCA job, before installing the project.
  - Checkov also caught a real, legitimate gap in `terraform-examples/main.tf`
    (no lifecycle configuration on the example bucket) — fixed by adding one,
    rather than being silently allowed through by `soft-fail: true`.
  - Every other stage (build/test/coverage, SAST, secrets scan, SBOM
    generation) passed on the very first real run, unmodified.

## Failure modes and disaster recovery

Not applicable in the infrastructure sense — a failing quality gate simply
blocks a merge; there is no running service or data store for this repo
to lose.

## Roadmap

- SonarQube/SonarCloud integration as an alternative or complement to the
  bandit+ruff combination, once a server is available to point at.
- A composite action wrapping the ZAP + start-app pattern for reuse
  outside Python targets.
- Policy-as-code (OPA/Conftest) for the IaC stage as a Checkov alternative.

## Technical article / research outputs

None yet.

## Development

```bash
cd demo-app
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --cov --cov-report=term-missing
ruff check . && ruff format --check .
mypy
bandit -r src
pip-audit
```

## License

MIT © sangiya
