# Version-Bound Assurance — TAS 2026 Reproducibility Artifact

This repository contains the bounded executable specification supporting the TAS 2026 paper **“Version-Bound Assurance at Agent Decision Boundaries: Binding Provenance, Execution, and Delegated Authority.”**

## Scope

The artifact evaluates six synthetic fixtures and three negative controls that distinguish:

- untyped connectivity (K0),
- typed directed connectivity (K1),
- selected-obligation closure, and
- Gate 2 manifest admission plus closure.

It is intentionally small. It does **not** implement a production policy-enforcement point, signature verifier, identity provider, live agent runtime, latency benchmark, or general semantic-grounding engine. Identity, authorization validity, record integrity, separation, ordering, and complete capture are stipulated where described in the technical appendix.

## Reproduce the reported fixture outcomes

Requirements:

- Python 3.10 or newer
- Python standard library only
- optimization disabled (do not use `python -O` or `PYTHONOPTIMIZE`)

From the repository root:

```bash
python code_appendix/check_fixtures.py \
  --output replay/results.json \
  --fixtures replay/fixtures.json
```

The runner raises on any mismatch in the six expected result vectors. Three additional assertions test missing evidence, a changed dispatch target, and an unavailable support rule.

The recorded reproduction used CPython 3.13.5. See `environment.json` and `TECHNICAL_APPENDIX.md` for details.

## Repository contents

```text
.
├── README.md
├── CITATION.cff
├── LICENSE
├── TECHNICAL_APPENDIX.md
├── SHA256SUMS.txt
├── environment.json
├── regression_verification.json
├── results.json
├── run_stdout.txt
├── code_appendix/
│   └── check_fixtures.py
└── data_appendix/
    └── fixtures.json
```

## Result summary

| Case | Deliberate condition | K0 | K1 | Closure | Gate 2 |
|---|---|---:|---:|---:|---|
| F0 | Valid candidate | true | true | true | ALLOW |
| F1 | Stale evaluation and approval | true | true | false | HOLD |
| F2 | Observation in evaluation-result role | true | false | false | HOLD |
| F3 | Unsupported current-version claim | true | true | false | HOLD |
| F4 | Corrected claim and refreshed bindings | true | true | true | ALLOW |
| F5 | Material claim omitted from manifest | true | true | true | HOLD |

These are deterministic specification checks, not population-level performance measurements.

## Paper mapping

- Paper §2.2 / Eq. (1): obligation selection, joint witness, and manifest admission
- Paper §3 / Eqs. (2)–(5): bounded predicate checks under stated trust assumptions
- Paper §4 / Table 1: K0, K1, F0–F5, and the negative controls
- Technical appendix: exact fixture constants, replay procedure, and environment

## Citation and release

`CITATION.cff` provides machine-readable citation metadata. The publication artifact is frozen as GitHub release/tag `v1.0.1` and archived by Zenodo.

**Version-specific DOI:** https://doi.org/10.5281/zenodo.22981118

Repository: https://github.com/kaiello/version-bound-assurance-tas2026

## License

Unless otherwise noted, the repository contents, including the checker, documentation, and synthetic fixture data, are distributed under the **Apache License 2.0**. See `LICENSE`.

The artifact has been approved for public release. The release record preserves the exact commit associated with `v1.0.1`, the recorded outputs, and `SHA256SUMS.txt`.
