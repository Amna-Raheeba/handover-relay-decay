"""Notebook 2 (as a runnable script): the evaluation experiment, small.

Runs the headline experiment on a reduced census (100 patients) so it
finishes quickly, and prints the critical-item survival table. The
full 500-patient run lives in results/ and is reproduced by
scripts/reproduce_results.py.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from handover_relay_decay.evaluate import run_evaluation
from handover_relay_decay.policies import POLICY_ORDER


def main():
    result = run_evaluation(n_patients=100, seed=7, max_relays=8)
    print("Critical-item survival (100 patients, seed 7):")
    print("%-28s %6s %6s %6s" % ("policy", "@1", "@4", "@8"))
    for name in POLICY_ORDER:
        s = result["summaries"][name]
        print("%-28s %6.3f %6.3f %6.3f" % (
            name,
            s["critical_survival_relay_1"],
            s["critical_survival_relay_4"],
            s["critical_survival_relay_8"],
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
