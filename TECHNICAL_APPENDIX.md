# Technical Appendix: Bounded Specification Fixtures

Companion to **Version-Bound Assurance at Agent Decision Boundaries: Binding Provenance, Execution, and Delegated Authority**, camera-ready revision v20.

## A. Scope and relation to the paper

This appendix documents the small executable specification behind Section 4 and Table 1. It is a set of deliberately constructed counterexamples and controls, not a benchmark of deployed agents. Six fixed fixtures distinguish untyped connectivity, typed connectivity, selected-obligation acceptance, and manifest admission. No live action is dispatched; no model, CI service, identity provider, signature verifier, policy service, or network resource is contacted.

The architecture in Sections 2–3 is broader than this checker. Identity authenticity, grant validity, revocation, decision-before-dispatch ordering, evaluator separation, record integrity, and complete capture are stipulated inputs, not verified cryptographically or empirically. The executable checks only the SAT/non-SAT acceptance projection of the three-valued interface, with diagnostic reason codes. It does not implement a general three-valued inference engine or a search over alternative witness subgraphs.

The evaluation manifest is represented by the fixed symbolic identifier `unit-tests-v1`; it stands in for the policy-pinned manifest digest in Equation (4). The fixture's JSON serialization is explicitly defined below and is not claimed to implement a general canonicalization standard.

## B. Contents and replay

`code_appendix/check_fixtures.py` contains all generation, preprocessing, verification, expected-vector comparison, and negative-control code. `data_appendix/fixtures.json` contains all six generated graphs and their expected outcomes. `results.json` records the categorical decisions and reasons. `environment.json` records the observed execution environment. `regression_verification.json` confirms that the executable syntax tree, excluding comments/docstrings, and result JSON remain unchanged from the earlier fixture implementation.

From the root of this package, run Python 3.10 or newer without optimization:

```sh
python code_appendix/check_fixtures.py --output replay/results.json --fixtures replay/fixtures.json
```

The main fixture comparisons raise an exception on a mismatch. The three negative controls use Python assertions, so do not run with `python -O` or `PYTHONOPTIMIZE` enabled. The documented reproduction used CPython 3.13.5 with optimization flag 0. No installation beyond Python's standard library is required.

Compare parsed JSON, not operating-system-specific file metadata. The stored expected result vectors are fixed before executing the checks; no thresholds or parameters are fitted to experimental data.

## C. Exact cases and verification configurations

| Case | Deliberate condition | K0 | K1 | Closure | Gate 2 |
|---|---|---|---|---|---|
| F0 | Valid candidate | true | true | true | ALLOW |
| F1 | Candidate changed; evaluation and approval retain old digest | true | true | false | HOLD |
| F2 | Evaluation-result role contains an Observation | true | false | false | HOLD |
| F3 | Current claim asserts versions 1 and 2; source admits only 1 | true | true | false | HOLD |
| F4 | Claim corrected and affected bindings refreshed | true | true | true | ALLOW |
| F5 | Additional material claim omitted from manifest | true | true | true | HOLD |

**K0** requires the selected role nodes to be connected to the candidate in the undirected incidence graph; it discards edge direction and labels. **K1** additionally verifies required node types and directed, labeled relations. **Closure** performs the specified structural, digest, extraction, set-inclusion, and evaluation/approval binding checks for the selected obligations. **Gate 2** requires both closure and the fixed manifest-reconciliation rule. These ablations are not benchmarks against fully configured GitHub, in-toto, SLSA, or other policy engines.

The primary comparison is exact equality between each expected and observed four-verdict vector, retaining the case-level outputs and decisive reasons. There are six vectors and 24 reported configuration-level verdicts, not 24 independent stochastic trials. One runner invocation generated the stored reproduction results; each vector is reported once. Three additional negative controls check removal of the evidence node, a changed dispatch target, and loss of the source field's declared exhaustiveness. All six expected vectors matched and all three controls passed. This confirms bounded checking behavior, not a population error rate.

## D. Fixed data and policy constants

The artifact has a commit identifier and a `claims` map. The primary claim slot is `api_support`. F5 additionally contains `additional_support_claim`, with versions `[2]`, but omits that slot from the manifest. The admitted source field is `supported_versions=[1]`, with `exhaustive_for_fixture=true`. The evidence locator is exactly `supported_versions`; evidence records the source digest and extracted version list. Grounding is accepted exactly when the claimed integer-version set is a subset of the source set, given the stipulated source admission and explicit exhaustiveness condition.

The policy identifier is `v1`; promotion context is `merge:Repo-A/main`; the authorized commit target is `Repo-A/feature/req-17`. The selector identifier is `all-schema-claims-v1`; selected and independently admitted action sets are both `['t']`; evaluation and approval are both required. The evaluation-manifest identifier is `unit-tests-v1`. The fixed actor/principal and relation dictionaries are in the code appendix. These are test fixtures, not learned hyperparameters. There was no random sampling, seed, training, tuning sweep, optimization objective, or held-out split.

`digest(value)` computes SHA-256 over UTF-8 encoding of Python `json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)`. The checker recomputes applicable candidate/source/request digests. No RFC-wide canonicalization or cryptographic identity proof is claimed.

Controlled fixtures are used because the question is whether the configurations produce distinct decisions under a precisely isolated change. Public agent-task datasets do not, by themselves, supply the matched authorization, approval, coverage, and policy witnesses required by these counterexamples. This is not an argument that public datasets are unsuitable for a future instrumented trace study.

## E. Execution environment

The recorded reproduction used CPython 3.13.5, Linux kernel 6.18.44, x86-64, with an AMD EPYC 9V74 80-Core Processor identified by the execution container. Five logical CPUs were exposed; the CPU cgroup quota was 400000/100000 (four CPU-equivalents). The memory cgroup limit was 4294967296 bytes (4 GiB), while `/proc/meminfo` exposed 6090736 kB. These are container-exposed resources, not a claim of dedicated machine allocation. No GPU was used. All imports are from the Python standard library; there are no third-party framework dependencies.

This metadata supports reproducibility of categorical outputs. CPU time, peak memory, storage inflation, throughput, latency distributions, false-blocking rates, and statistical significance were not measured. No confidence interval or significance test is appropriate to infer deployment performance from these six purpose-built cases.

## F. Availability

All code and synthetic inputs required for the reported fixture results are contained in the reproducibility artifact hosted at `https://github.com/kaiello/version-bound-assurance-tas2026`. The checker, documentation, and synthetic fixture data are distributed under the Apache License 2.0.

For publication, the artifact should be cited by its frozen `v1.0.1` release rather than the mutable `main` branch. If the enabled Zenodo integration assigns a version-specific DOI to that release, the camera-ready manuscript should cite that DOI. The release record should preserve the exact source commit, recorded outputs, execution metadata, and SHA-256 checksums distributed with the artifact.

With public availability and the Apache-2.0 license in place, reproducibility checklist items 3.4 and 4.5 can be updated from **no** to **yes** for this artifact.
