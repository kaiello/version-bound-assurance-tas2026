# v1.0.0 — TAS 2026 Reproducibility Artifact

First frozen release of the reproducibility artifact accompanying:

**Kenneth D. Aiello. “Version-Bound Assurance at Agent Decision Boundaries: Binding Provenance, Execution, and Delegated Authority.” TAS 2026.**

## Included

- bounded executable specification (`code_appendix/check_fixtures.py`)
- six synthetic fixtures (`data_appendix/fixtures.json`)
- three negative controls
- recorded categorical outcomes (`results.json`)
- execution-environment record (`environment.json`)
- regression-verification record
- technical appendix
- SHA-256 checksums for the reproducibility payload
- GitHub Actions verification workflow

## Verification

The release checker is deterministic and uses the Python standard library only. CI verifies:

1. committed SHA-256 checksums,
2. all six expected fixture-result vectors,
3. all three negative controls, and
4. equality of regenerated fixtures/results with the committed records.

## Scope

This artifact demonstrates bounded checking behavior under the stated synthetic assumptions. It is not a production policy-enforcement point, live-agent benchmark, signature verifier, identity provider, latency benchmark, or general semantic-grounding engine.

## License

Apache License 2.0.
