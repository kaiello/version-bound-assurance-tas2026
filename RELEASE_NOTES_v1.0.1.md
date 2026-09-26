# v1.0.1 — TAS 2026 Reproducibility Artifact

This release is the Zenodo-triggering archival release for the TAS 2026 reproducibility artifact.

**No scientific, algorithmic, fixture, or recorded-result changes were made from v1.0.0.** The executable checker, six synthetic fixtures, three negative controls, recorded results, environment metadata, and checksum-verified payload are unchanged. This release only updates publication metadata so the Zenodo-enabled repository can archive a release and issue a version-specific DOI.

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

CI verifies committed SHA-256 checksums, all six expected fixture-result vectors, all three negative controls, and equality of regenerated fixtures/results with the committed records.

## License

Apache License 2.0.
