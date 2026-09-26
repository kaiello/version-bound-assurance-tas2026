#!/usr/bin/env python3
"""Bounded, synthetic specification fixtures for the TAS v13 manuscript.

NOT a production assurance implementation. Identity, authorization, signature,
revocation, and runtime honesty are assumed-admitted inputs. This program checks
explicit graph structure, content identity, a structured set-inclusion grounding
rule, and a fixed-schema coverage rule. It does not execute an agent or effects,
measure end-to-end latency, or prove obligation coverage outside this fixture.
Paper mapping (v13): Section 2.2 / Equation (1): selected witness and manifest;
Section 3 / Equations (2)-(5): checks under stipulated trust inputs;
Section 4 / Table 1: K0, K1, six cases F0-F5 and three negative controls.
Only the SAT/non-SAT admission projection is implemented, with reason codes;
this is not a complete implementation of the three-valued verifier interface.
The symbolic evaluation-manifest identifier stands in for a policy-pinned digest.

Python 3.10+; standard library only. Run in this directory:
    python check_fixtures.py --output results.json --fixtures fixtures.json
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

Json = dict[str, Any]


def digest(value: Any) -> str:
    """Canonical representation for THIS JSON-only fixture, not a general standard."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build(commit: str, versions: list[int], *, extra_claim: bool = False) -> Json:
    """Section 4: create the fixed-schema source, graph and obligation manifest."""
    claims = {"api_support": {"versions": versions}}
    if extra_claim:
        claims["additional_support_claim"] = {"versions": [2]}
    artifact = {"commit": commit, "claims": claims}
    h = digest(artifact)
    source = {"supported_versions": [1], "exhaustive_for_fixture": True}
    request = {"instance": commit, "operation": "commit", "target": "Repo-A/feature/req-17",
               "principal": "producer", "policy": "v1"}
    rh = digest(request)
    nodes: Json = {
        "r": {"type": "Artifact", "content": artifact, "digest": h},
        "s": {"type": "Source", "content": source, "digest": digest(source)},
        "e": {"type": "Evidence", "source_digest": digest(source), "locator": "supported_versions",
              "versions": [1]},
        "t": {"type": "Action", "request": request, "dispatch": copy.deepcopy(request),
              "receipt_request_digest": rh, "artifact_digest": h},
        "a": {"type": "Authorization", "request_digest": rh},
        "g": {"type": "Grant"}, "d": {"type": "Principal"},
        "up": {"type": "Actor"}, "ue": {"type": "Actor"},
        "m": {"type": "Evaluation"},
        "z": {"type": "EvaluationResult", "artifact_digest": h, "evaluation_manifest": "unit-tests-v1",
              "context": "merge:Repo-A/main", "policy": "v1", "passed_required_checks": True},
        "reviewer": {"type": "Principal"},
        "qr": {"type": "Approval", "artifact_digest": h, "context": "merge:Repo-A/main", "policy": "v1"},
    }
    edges = [
        ["d", "delegates", "g"], ["a", "derivedFrom", "g"], ["a", "authorizes", "t"],
        ["r", "wasGeneratedBy", "t"], ["t", "performedBy", "up"],
        ["m", "evaluates", "r"], ["z", "generatedBy", "m"], ["m", "performedBy", "ue"],
        ["reviewer", "approves", "qr"], ["qr", "approvalRecordFor", "r"], ["s", "yields", "e"]
    ]
    for slot, claim in claims.items():
        cid = f"c:{slot}"
        nodes[cid] = {"type": "Claim", "slot": slot, "content": copy.deepcopy(claim), "artifact_digest": h}
        edges.extend([["e", "supports", cid], [cid, "claimBoundTo", "r"]])
    manifest = {"artifact_digest": h, "context": "merge:Repo-A/main", "policy": "v1", "selector": "all-schema-claims-v1",
                "claims": list(claims), "actions": ["t"], "requires_evaluation": True, "requires_approval": True}
    return {"nodes": nodes, "edges": edges, "manifest": manifest,
            "admitted_trace_actions": ["t"],
            "assumptions": "Identity, integrity, separation, grant validity, event ordering and complete capture are stipulated, not cryptographically or empirically verified."}


BASE_TYPES = {"r": "Artifact", "s": "Source", "e": "Evidence", "t": "Action", "a": "Authorization",
              "g": "Grant", "d": "Principal", "up": "Actor", "ue": "Actor", "m": "Evaluation",
              "z": "EvaluationResult", "reviewer": "Principal", "qr": "Approval"}
BASE_EDGES = [
    ["d", "delegates", "g"], ["a", "derivedFrom", "g"], ["a", "authorizes", "t"],
    ["r", "wasGeneratedBy", "t"], ["t", "performedBy", "up"], ["m", "evaluates", "r"],
    ["z", "generatedBy", "m"], ["m", "performedBy", "ue"], ["reviewer", "approves", "qr"],
    ["qr", "approvalRecordFor", "r"], ["s", "yields", "e"]]


def connectivity(f: Json) -> bool:
    """Section 4, K0: selected role nodes connect to r in the untyped incidence graph."""
    n, b = f["nodes"], f["manifest"]
    required = set(BASE_TYPES) | {f"c:{slot}" for slot in b["claims"]}
    if not required <= set(n):
        return False
    adj: dict[str, set[str]] = {k: set() for k in n}
    for src, _, dst in f["edges"]:
        if src not in adj or dst not in adj:
            return False
        adj[src].add(dst); adj[dst].add(src)
    seen: set[str] = set(); queue = ["r"]
    while queue:
        v = queue.pop()
        if v not in seen:
            seen.add(v); queue.extend(adj[v] - seen)
    return required <= seen


def typed_connectivity(f: Json) -> bool:
    # Section 4, K1: supplement incidence connectivity with typed directed edges.
    """K1: K0 plus required role types and directed, labeled relations."""
    if not connectivity(f):
        return False
    expected = dict(BASE_TYPES)
    expected.update({f"c:{slot}": "Claim" for slot in f["manifest"]["claims"]})
    if any(f["nodes"][node].get("type") != kind for node, kind in expected.items()):
        return False
    required = list(BASE_EDGES)
    for slot in f["manifest"]["claims"]:
        required += [["e", "supports", f"c:{slot}"], [f"c:{slot}", "claimBoundTo", "r"]]
    present = {tuple(e) for e in f["edges"]}
    return all(tuple(e) in present for e in required)


def closure(f: Json) -> tuple[bool, list[str]]:
    # Equations (1)-(5): bounded acceptance checks, not a general witness search.
    """Bounded checks for SELECTED obligations, under explicitly admitted inputs."""
    if not typed_connectivity(f):
        return False, ["TYPE_OR_RELATION_MISMATCH"]
    n, b = f["nodes"], f["manifest"]
    h = digest(n["r"]["content"])
    errors: list[str] = []
    if n["r"]["digest"] != h or b["artifact_digest"] != h:
        errors.append("CANDIDATE_BINDING")
    if n["s"]["digest"] != digest(n["s"]["content"]) or n["e"]["source_digest"] != n["s"]["digest"]:
        errors.append("SOURCE_BINDING")
    if n["e"]["locator"] != "supported_versions" or n["e"]["versions"] != n["s"]["content"]["supported_versions"]:
        errors.append("EXTRACTION_INVALID")
    for slot in b["claims"]:
        claim = n[f"c:{slot}"]
        if claim["content"] != n["r"]["content"]["claims"].get(slot) or claim["artifact_digest"] != h:
            errors.append("CLAIM_BINDING")
        if not n["s"]["content"]["exhaustive_for_fixture"]:
            errors.append("SUPPORT_RULE_UNAVAILABLE")
        elif not set(claim["content"]["versions"]) <= set(n["e"]["versions"]):
            errors.append("GROUNDING_UNSUPPORTED")
    rh = digest(n["t"]["request"])
    if not (rh == n["a"]["request_digest"] == digest(n["t"]["dispatch"]) == n["t"]["receipt_request_digest"]):
        errors.append("REQUEST_RECEIPT_BINDING")
    for node, reason in [("z", "EVALUATION_BINDING"), ("qr", "APPROVAL_BINDING")]:
        if (n[node]["artifact_digest"], n[node]["context"], n[node]["policy"]) != (h, b["context"], b["policy"]):
            errors.append(reason)
    if n["z"]["evaluation_manifest"] != "unit-tests-v1" or n["z"]["passed_required_checks"] is not True:
        errors.append("EVALUATION_NOT_PASSED")
    return not errors, sorted(set(errors))


def manifest_ok(f: Json) -> tuple[bool, list[str]]:
    """Section 2.2: fixed-schema manifest admission, NOT a completeness oracle."""
    b = f["manifest"]
    errors: list[str] = []
    if set(b["claims"]) != set(f["nodes"]["r"]["content"]["claims"]):
        errors.append("COVERAGE_CLAIM_MISMATCH")
    if set(b["actions"]) != set(f["admitted_trace_actions"]):
        errors.append("COVERAGE_ACTION_MISMATCH")
    if len(b["claims"]) != len(set(b["claims"])) or len(b["actions"]) != len(set(b["actions"])):
        errors.append("DUPLICATE_MANIFEST_ENTRY")
    if b["selector"] != "all-schema-claims-v1" or b["requires_evaluation"] is not True or b["requires_approval"] is not True:
        errors.append("MANDATORY_OBLIGATION_FLOOR")
    if (b["artifact_digest"], b["context"], b["policy"]) != (digest(f["nodes"]["r"]["content"]), "merge:Repo-A/main", "v1"):
        errors.append("MANIFEST_BINDING")
    return not errors, errors


def make_cases() -> list[Json]:
    """Section 4, Table 1: original six controlled cases; no fitted parameters."""
    valid = build("commit-h1", [1])
    stale = build("commit-h2", [1])
    stale["nodes"]["z"]["artifact_digest"] = valid["nodes"]["r"]["digest"]
    stale["nodes"]["qr"]["artifact_digest"] = valid["nodes"]["r"]["digest"]
    wrong_type = build("commit-wrong-type", [1]); wrong_type["nodes"]["z"]["type"] = "Observation"
    unsupported = build("commit-grounding", [1, 2])
    repaired = build("commit-repair", [1])
    omitted = build("commit-omitted", [1], extra_claim=True)
    omitted["manifest"]["claims"] = ["api_support"]
    values = [
        ("F0", "Valid candidate", valid, [True, True, True, True]),
        ("F1", "Stale evaluation and approval", stale, [True, True, False, False]),
        ("F2", "Observation in evaluation-result role", wrong_type, [True, False, False, False]),
        ("F3", "Unsupported current-version claim", unsupported, [True, True, False, False]),
        ("F4", "Corrected claim; all affected bindings refreshed", repaired, [True, True, True, True]),
        ("F5", "Additional material claim omitted from manifest", omitted, [True, True, True, False]),
    ]
    return [{"id": i, "description": d, "fixture": f, "expected": ex} for i, d, f, ex in values]


def run() -> tuple[list[Json], Json]:
    """Check each expected four-verdict vector and the three negative controls."""
    cases = make_cases(); results: list[Json] = []
    for c in cases:
        f = c["fixture"]
        closed, ce = closure(f); admitted, me = manifest_ok(f)
        values = [connectivity(f), typed_connectivity(f), closed, admitted and closed]
        if values != c["expected"]:
            raise AssertionError(f"{c['id']}: expected {c['expected']}; got {values}")
        results.append({"id": c["id"], "description": c["description"], "K0": values[0], "K1": values[1],
                        "closure": closed, "manifest_admitted": admitted, "gate2": "ALLOW" if values[3] else "HOLD",
                        "closure_reasons": ce, "manifest_reasons": me})
    # Additional negative controls protect the example's crucial distinctions.
    missing = copy.deepcopy(cases[0]["fixture"]); missing["nodes"].pop("e")
    assert not typed_connectivity(missing)
    changed_target = copy.deepcopy(cases[0]["fixture"]); changed_target["nodes"]["t"]["dispatch"]["target"] = "Repo-A/main"
    assert "REQUEST_RECEIPT_BINDING" in closure(changed_target)[1]
    unavailable_rule = copy.deepcopy(cases[0]["fixture"])
    unavailable_rule["nodes"]["s"]["content"]["exhaustive_for_fixture"] = False
    unavailable_rule["nodes"]["s"]["digest"] = digest(unavailable_rule["nodes"]["s"]["content"])
    unavailable_rule["nodes"]["e"]["source_digest"] = unavailable_rule["nodes"]["s"]["digest"]
    assert "SUPPORT_RULE_UNAVAILABLE" in closure(unavailable_rule)[1]
    return cases, {"scope": "Synthetic, bounded specification checks only; no recorded agents, live PEP, signatures, or performance benchmark.",
                   "fixture_count": len(cases), "negative_control_count": 3, "all_expected_outcomes_match": True, "results": results}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("results.json"))
    p.add_argument("--fixtures", type=Path, default=Path("fixtures.json"))
    args = p.parse_args()
    cases, results = run()
    for path, data in [(args.output, results), (args.fixtures, cases)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()