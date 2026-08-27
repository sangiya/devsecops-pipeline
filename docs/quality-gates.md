# Quality Gates

`quality-gate.yml` composes six stages. The final `gate` job only passes if
every stage below succeeded (a stage set to `soft-fail` reports findings
without blocking, noted below).

| Stage | Tool | Blocks the gate? | Threshold |
|---|---|---|---|
| Build/Test/Coverage | pytest + coverage.py | Yes | `--cov-fail-under` (default 90%) |
| Lint/Format | ruff | Yes | Zero violations |
| Type check | mypy (strict) | Yes, unless `enable-type-check: false` | Zero errors |
| SAST | bandit | Yes | Any finding at or above `fail-on-sast-severity` (default `medium`) |
| SCA | pip-audit | Yes | Any known vulnerability in a resolved dependency |
| Secrets | Gitleaks | Yes | Any match against the OSS ruleset, across full git history |
| SBOM | cyclonedx-py | No (informational) | N/A — generates and uploads an artifact, does not gate |
| Container scan | Trivy | Yes | Any `CRITICAL`/`HIGH` CVE (configurable via `fail-on-severity`) |
| IaC scan | Checkov | **No by default** (`soft-fail: true` in `quality-gate.yml`) | Configurable per consumer once a baseline exists |

## Why IaC scanning defaults to soft-fail

A consumer repo adopting this pipeline for the first time almost certainly
has pre-existing Terraform/Kubernetes manifests with some number of Checkov
findings already. Defaulting to a hard fail would make adoption itself the
first thing that breaks CI. `soft-fail: true` reports every finding (as a
SARIF upload to the repo's code scanning tab) without blocking merges,
so a team can triage and fix its existing findings on its own timeline,
then flip `soft-fail: false` once the backlog is clear — this pipeline
does not make that decision for a consumer.

## Why container scanning uses a `.trivyignore`, not just a threshold

Base-image OS packages routinely carry CVEs with no fix published yet
upstream — this repo's own `demo-app`, pinned to Debian 12 "bookworm" and
kept current with `apt-get upgrade`, still had four such findings (see
`demo-app/.trivyignore`) when this pipeline first ran for real. Lowering
`fail-on-severity` to make those go away would also hide *fixable* future
findings at the same severity; a `.trivyignore` accepts each one
individually, by CVE ID, with a written justification and a date it was
checked — visible in the file, not silently swallowed. Every finding still
uploads to the repo's code scanning tab (`.trivyignore` only affects the
gate's pass/fail, not what's reported) — see [that check-in's
reasoning](../demo-app/.trivyignore) for the format. Re-check ignored CVEs
periodically; the whole point is that they get removed once a fix ships.

## Why SBOM generation doesn't gate

An SBOM is evidence, not a pass/fail check by itself — nothing in a
CycloneDX document is inherently "wrong". It is generated and uploaded as
a build artifact on every run specifically so it exists when someone
needs it (an audit, an incident, a customer security questionnaire), not
because its contents should ever fail a build.

## Adjusting thresholds

Every numeric/severity threshold in this table is a `workflow_call` input
on the relevant reusable workflow (see each `.github/workflows/reusable-*.yml`
file's `inputs:` block) — a consumer overrides them at the call site in
their own `ci.yml`, without forking this repo.
