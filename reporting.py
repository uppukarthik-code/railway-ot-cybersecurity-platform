"""
reporting.py

PERSISTENT EVIDENCE REPORTING LAYER (read-only).

Purpose
-------
Serialize the findings already produced by the existing engines into
durable, machine-readable assessment artifacts for IRSE / IEC 62443 /
EN 50159 / TS 50701 evidence and independent peer review.

DESIGN PRINCIPLES
-----------------
- Reporting layer ONLY. This module NEVER generates, mutates, suppresses
  or reclassifies findings. It consumes the outputs of:
      validator.validate(topology)        -> list[dict]
      risk_engine.analyze_risk(topology)   -> list[dict]
      validators.* (topology)              -> list[str]
      ontology_validator.validate_ontology() -> dict[str, list[str]]
- No security / ontology / validator / risk / protocol / trust / replay /
  encryption / safety logic lives here.
- Standard library only (json, csv, datetime, pathlib, io, contextlib,
  copy). No new dependencies.
- Silent: internal validator/ontology calls are stdout-suppressed so the
  host pipeline's console output is unchanged.
"""

import csv
import io
import json
import copy
import contextlib
from datetime import datetime
from pathlib import Path


# ============================================================
# HELPERS
# ============================================================


@contextlib.contextmanager
def _silent():
    """Suppress stdout/stderr from read-only validator/ontology calls so
    the host pipeline console output is not altered."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        yield


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _ensure_dir(out_dir):
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _count_severities(findings):
    counts = {}
    for f in findings:
        sev = str(f.get("severity", "")).upper()
        counts[sev] = counts.get(sev, 0) + 1
    return counts


# ============================================================
# RISK REGISTER
# ============================================================


def save_risk_register(risk_findings, out_dir):
    """Persist risk_engine.analyze_risk() output verbatim."""
    out = _ensure_dir(out_dir)
    sev = _count_severities(risk_findings)
    payload = {
        "generated_at": _now(),
        "source": "risk_engine.analyze_risk",
        "total_findings": len(risk_findings),
        "critical": sev.get("CRITICAL", 0),
        "high": sev.get("HIGH", 0),
        "medium": sev.get("MEDIUM", 0),
        "low": sev.get("LOW", 0),
        "findings": risk_findings,
    }
    path = out / "risk_register.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ============================================================
# VALIDATION REPORT
# ============================================================


def save_validation_report(validator_findings, subvalidator_results, out_dir):
    """Persist core validator results + sub-validator message lists."""
    out = _ensure_dir(out_dir)
    passed = [f for f in validator_findings if f.get("status") == "PASS"]
    failed = [f for f in validator_findings if f.get("status") == "FAIL"]
    payload = {
        "generated_at": _now(),
        "validator_summary": {
            "source": "validator.validate",
            "total_rules": len(validator_findings),
            "passed": len(passed),
            "failed": len(failed),
            "failed_rules": [f.get("rule") for f in failed],
            "rules": validator_findings,
        },
    }
    for name, results in subvalidator_results.items():
        payload[name] = {
            "count": len(results),
            "errors": results,
        }
    path = out / "validation_report.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ============================================================
# ONTOLOGY REPORT
# ============================================================


def save_ontology_report(out_dir):
    """Run ontology_validator.validate_ontology() (read-only) and persist.

    Never raises: on failure, writes a {status: failed, error: ...}
    artifact so the host pipeline cannot crash on ontology validation.
    """
    out = _ensure_dir(out_dir)
    path = out / "ontology_report.json"
    try:
        with _silent():
            import ontology_validator

            result = ontology_validator.validate_ontology()
        total = sum(len(v) for v in result.values())
        payload = {
            "generated_at": _now(),
            "status": "ok",
            "source": "ontology_validator.validate_ontology",
            "total_errors": total,
            **result,
        }
    except Exception as exc:  # reporting must never crash the pipeline
        payload = {
            "generated_at": _now(),
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ============================================================
# RESIDUAL RISK CSV
# ============================================================


def save_residual_risk_csv(risk_findings, validator_findings, out_dir):
    """Flat residual-risk register combining risk-engine findings and
    failed validator rules. Mitigation_Status defaults to OPEN (these are
    the open assessment backlog); the column exists for downstream
    engineering triage and is not derived from any suppression logic."""
    out = _ensure_dir(out_dir)
    path = out / "residual_risk_register.csv"
    rows = []
    idx = 0
    for f in risk_findings:
        idx += 1
        rows.append(
            {
                "ID": f"R-{idx:03d}",
                "Category": f.get("type", ""),
                "Severity": f.get("severity", ""),
                "Source": "risk_engine",
                "Asset_or_Link": ";".join(f.get("affected_assets", []) or []),
                "Description": f.get("message", ""),
                "Mitigation_Status": "OPEN",
            }
        )
    for f in validator_findings:
        if f.get("status") != "FAIL":
            continue
        idx += 1
        rows.append(
            {
                "ID": f"V-{idx:03d}",
                "Category": f.get("rule", ""),
                "Severity": f.get("severity", ""),
                "Source": "validator",
                "Asset_or_Link": "",
                "Description": f.get("message", ""),
                "Mitigation_Status": "OPEN",
            }
        )
    fields = [
        "ID",
        "Category",
        "Severity",
        "Source",
        "Asset_or_Link",
        "Description",
        "Mitigation_Status",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ============================================================
# ASSESSMENT SUMMARY (Markdown)
# ============================================================


def save_assessment_summary(
    validator_findings,
    risk_findings,
    subvalidator_results,
    ontology_path,
    out_dir,
):
    out = _ensure_dir(out_dir)
    path = out / "assessment_summary.md"

    failed_rules = [f for f in validator_findings if f.get("status") == "FAIL"]
    sev = _count_severities(risk_findings)

    # Read back the persisted ontology report for the summary totals.
    onto_total = "n/a"
    onto_status = "n/a"
    try:
        onto = json.loads(Path(ontology_path).read_text(encoding="utf-8"))
        onto_status = onto.get("status", "n/a")
        onto_total = onto.get("total_errors", "n/a")
    except Exception:
        pass

    lines = []
    lines.append("# Assessment Summary")
    lines.append("")
    lines.append(f"_Generated: {_now()}_")
    lines.append("")
    lines.append(
        "Persistent evidence artifacts generated by the reporting layer "
        "from existing engine outputs. No findings were created, modified, "
        "suppressed or reclassified."
    )
    lines.append("")

    lines.append("## Architecture / Security Findings")
    lines.append("")
    lines.append(f"- Validator rules: {len(validator_findings)} "
                 f"({len(failed_rules)} FAIL)")
    for f in failed_rules:
        lines.append(f"  - **{f.get('rule')}** [{f.get('severity')}]: "
                     f"{f.get('message')}")
    lines.append("")

    lines.append("## Safety / Compliance Findings (risk engine)")
    lines.append("")
    by_type = {}
    for f in risk_findings:
        by_type.setdefault(f.get("type"), 0)
        by_type[f.get("type")] += 1
    for t, n in sorted(by_type.items()):
        lines.append(f"- {t}: {n}")
    lines.append("")

    lines.append("## Ontology Findings")
    lines.append("")
    lines.append(f"- ontology_validator status: {onto_status}")
    lines.append(f"- total ontology errors: {onto_total}")
    lines.append("")

    lines.append("## Validation Statistics")
    lines.append("")
    lines.append(f"- risk findings: {len(risk_findings)} "
                 f"(CRITICAL {sev.get('CRITICAL', 0)}, HIGH {sev.get('HIGH', 0)})")
    for name, results in subvalidator_results.items():
        lines.append(f"- {name}: {len(results)}")
    lines.append("")

    lines.append("## Residual Risks")
    lines.append("")
    lines.append(
        f"- {len(risk_findings)} risk-engine findings + "
        f"{len(failed_rules)} failed validator rules "
        f"-> see residual_risk_register.csv (all Mitigation_Status = OPEN)"
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ============================================================
# ORCHESTRATOR
# ============================================================


def generate_reports(topology, validator_findings, risk_findings, out_dir):
    """Generate all five evidence artifacts. Silent and read-only.

    validator_findings / risk_findings are the ALREADY-COMPUTED outputs
    from the host pipeline (passed in, not recomputed). Sub-validators and
    ontology_validator are invoked here on an isolated deep copy with
    stdout suppressed, so neither the topology nor the console is touched.
    Never raises.
    """
    written = {}
    try:
        out = _ensure_dir(out_dir)

        # Sub-validators: read-only, on an isolated copy, stdout-suppressed.
        sub = {}
        try:
            safe_topo = copy.deepcopy(topology)
            with _silent():
                from validators import (
                    validate_assets,
                    validate_links,
                    validate_zones,
                    validate_purdue,
                    validate_protocols,
                    validate_rendering,
                )

                sub = {
                    "validate_assets": validate_assets(safe_topo),
                    "validate_links": validate_links(safe_topo),
                    "validate_zones": validate_zones(safe_topo),
                    "validate_purdue": validate_purdue(safe_topo),
                    "validate_protocols": validate_protocols(safe_topo),
                    "validate_rendering": validate_rendering(safe_topo),
                }
        except Exception as exc:
            sub = {"_error": [f"{type(exc).__name__}: {exc}"]}

        written["risk_register"] = str(
            save_risk_register(risk_findings, out)
        )
        written["validation_report"] = str(
            save_validation_report(validator_findings, sub, out)
        )
        onto_path = save_ontology_report(out)
        written["ontology_report"] = str(onto_path)
        written["residual_risk_register"] = str(
            save_residual_risk_csv(risk_findings, validator_findings, out)
        )
        written["assessment_summary"] = str(
            save_assessment_summary(
                validator_findings,
                risk_findings,
                sub,
                onto_path,
                out,
            )
        )
    except Exception:
        # Reporting must never crash the host pipeline.
        pass
    return written
