"""The headline experiment.

Seeded synthetic census (500 patients, seed 7) carried through 8
relays under six policies: free-text, SBAR, checklist, and the
checklist combined with read-back, critical-item pinning, or both.
The baseline that hides the compounding is single-handover
completeness: survival at relay 1.
"""

import csv
import json
import os

from handover_relay_decay.census import census_stats, generate_census
from handover_relay_decay.metrics import summarise_run
from handover_relay_decay.policies import POLICY_ORDER, get_policy
from handover_relay_decay.relay import simulate_census

DEFAULT_PATIENTS = 500
DEFAULT_SEED = 7
DEFAULT_RELAYS = 8
HEADLINE_RELAY = 4


def run_evaluation(n_patients=DEFAULT_PATIENTS, seed=DEFAULT_SEED,
                   max_relays=DEFAULT_RELAYS, patients=None):
    if patients is None:
        patients = generate_census(n_patients=n_patients, seed=seed)
    stats = census_stats(patients)
    summaries = {}
    runs = {}
    for name in POLICY_ORDER:
        policy = get_policy(name)
        run = simulate_census(patients, policy, seed=seed,
                              max_relays=max_relays)
        runs[name] = run
        summaries[name] = summarise_run(run)
    headline = {
        "critical_survival_relay_4": dict(
            (name, summaries[name]["critical_survival_relay_4"])
            for name in POLICY_ORDER),
        "critical_survival_relay_1": dict(
            (name, summaries[name]["critical_survival_relay_1"])
            for name in POLICY_ORDER),
        "critical_half_life_fitted": dict(
            (name, summaries[name]["critical_half_life_fitted"])
            for name in POLICY_ORDER),
    }
    return {
        "seed": seed,
        "n_patients": len(patients),
        "max_relays": max_relays,
        "census": stats,
        "headline": headline,
        "summaries": summaries,
        "runs": runs,
    }


def _round(value, digits=6):
    if value is None:
        return None
    return round(float(value), digits)


def evaluation_to_jsonable(result):
    """A JSON-safe copy of the evaluation with rounded floats."""
    out = {
        "seed": result["seed"],
        "n_patients": result["n_patients"],
        "max_relays": result["max_relays"],
        "census": result["census"],
        "headline": dict(
            (key, dict((name, _round(val)) for name, val in vals.items()))
            for key, vals in result["headline"].items()),
        "summaries": dict(
            (name, dict((k, _round(v) if isinstance(v, float) else v)
                        for k, v in summary.items()))
            for name, summary in result["summaries"].items()),
        "runs": dict(
            (name, {
                "policy": run["policy"],
                "max_relays": run["max_relays"],
                "initial_total": run["initial_total"],
                "initial_critical": run["initial_critical"],
                "total_survival": [_round(v) for v in run["total_survival"]],
                "critical_survival": [
                    _round(v) for v in run["critical_survival"]],
                "per_type_survival": dict(
                    (t, [_round(v) for v in curve])
                    for t, curve in run["per_type_survival"].items()),
                "per_type_critical_survival": dict(
                    (t, [_round(v) for v in curve])
                    for t, curve in
                    run["per_type_critical_survival"].items()),
            })
            for name, run in result["runs"].items()),
    }
    return out


def write_results(result, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    jsonable = evaluation_to_jsonable(result)
    with open(os.path.join(out_dir, "evaluation.json"), "w",
              encoding="utf-8") as handle:
        json.dump(jsonable, handle, indent=1, sort_keys=True)

    csv_path = os.path.join(out_dir, "evaluation.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "policy", "critical_survival_relay_1",
            "critical_survival_relay_4", "critical_survival_relay_8",
            "total_survival_relay_4", "total_survival_relay_8",
            "critical_half_life_fitted", "critical_half_life_empirical",
            "critical_curve_auc",
        ])
        for name in POLICY_ORDER:
            s = jsonable["summaries"][name]
            writer.writerow([
                name,
                s["critical_survival_relay_1"],
                s["critical_survival_relay_4"],
                s["critical_survival_relay_8"],
                s["total_survival_relay_4"],
                s["total_survival_relay_8"],
                s["critical_half_life_fitted"],
                s["critical_half_life_empirical"],
                s["critical_curve_auc"],
            ])

    from handover_relay_decay.report import (
        headline_markdown, summary_markdown)
    with open(os.path.join(out_dir, "evaluation_summary.md"), "w",
              encoding="utf-8") as handle:
        handle.write(summary_markdown(result))
    with open(os.path.join(out_dir, "HEADLINE.md"), "w",
              encoding="utf-8") as handle:
        handle.write(headline_markdown(result))
    return jsonable
