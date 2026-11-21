"""Reproduce the headline results and guard against drift.

Re-runs the full evaluation from the seed and compares the headline
numbers against results/evaluation.json. Exits non-zero if any
headline number moved by more than the tolerance.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from handover_relay_decay.evaluate import evaluation_to_jsonable, run_evaluation

TOLERANCE = 1e-6


def compare(saved, fresh, path=""):
    problems = []
    if isinstance(saved, dict):
        for key in saved:
            if key not in fresh:
                problems.append("missing key: %s%s" % (path, key))
            else:
                problems.extend(
                    compare(saved[key], fresh[key], "%s%s." % (path, key)))
    elif isinstance(saved, float) or isinstance(fresh, float):
        if saved is None or fresh is None:
            if saved is not fresh:
                problems.append("None mismatch at %s" % path)
        elif abs(float(saved) - float(fresh)) > TOLERANCE:
            problems.append(
                "drift at %s: saved %s vs fresh %s" % (path, saved, fresh))
    else:
        if saved != fresh:
            problems.append(
                "mismatch at %s: saved %r vs fresh %r" % (path, saved, fresh))
    return problems


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    saved_path = os.path.join(here, "..", "results", "evaluation.json")
    with open(saved_path, "r", encoding="utf-8") as handle:
        saved = json.load(handle)
    fresh_result = run_evaluation(
        n_patients=saved["n_patients"], seed=saved["seed"],
        max_relays=saved["max_relays"])
    fresh = evaluation_to_jsonable(fresh_result)
    problems = []
    problems.extend(compare(saved["headline"], fresh["headline"],
                            "headline."))
    problems.extend(compare(saved["summaries"], fresh["summaries"],
                            "summaries."))
    if problems:
        print("DRIFT DETECTED (%d problems):" % len(problems))
        for problem in problems[:20]:
            print("  %s" % problem)
        return 1
    print("OK: headline and summary numbers reproduce exactly "
          "(tolerance %g)." % TOLERANCE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
