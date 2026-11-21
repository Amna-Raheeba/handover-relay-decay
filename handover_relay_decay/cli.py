"""Command line interface.

Usage:
  python -m handover_relay_decay demo [--policy NAME] [--patient N]
  python -m handover_relay_decay evaluate [--out DIR] [--patients N]
  python -m handover_relay_decay census [--patients N]
"""

import argparse
import random
import sys

from handover_relay_decay.census import census_stats, generate_census
from handover_relay_decay.evaluate import run_evaluation, write_results
from handover_relay_decay.policies import get_policy
from handover_relay_decay.relay import simulate_patient
from handover_relay_decay.report import patient_trace_markdown


def _cmd_demo(args):
    patients = generate_census(n_patients=max(args.patient + 1, 1),
                               seed=args.seed)
    patient = patients[args.patient]
    policy = get_policy(args.policy)
    rng = random.Random("%s:%s:demo" % (args.seed, policy.name))
    history = simulate_patient(patient, policy, rng,
                               max_relays=args.relays)
    print("Policy: %s" % policy.name)
    print(patient_trace_markdown(patient, history))
    return 0


def _cmd_evaluate(args):
    result = run_evaluation(n_patients=args.patients, seed=args.seed,
                            max_relays=args.relays)
    write_results(result, args.out)
    headline = result["headline"]["critical_survival_relay_4"]
    print("Critical-item survival at relay 4 (seed %d):" % args.seed)
    for name, value in headline.items():
        print("  %s: %.3f" % (name, value))
    print("Results written to %s" % args.out)
    return 0


def _cmd_census(args):
    patients = generate_census(n_patients=args.patients, seed=args.seed)
    stats = census_stats(patients)
    print("Patients: %d" % stats["n_patients"])
    print("Items: %d (critical: %d)"
          % (stats["total_items"], stats["critical_items"]))
    for item_type in sorted(stats["per_type"]):
        print("  %s: %d (critical: %d)" % (
            item_type, stats["per_type"][item_type],
            stats["per_type_critical"].get(item_type, 0)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="handover_relay_decay",
        description="Multi-shift handover relay decay simulation.")
    parser.add_argument("--seed", type=int, default=7)
    sub = parser.add_subparsers(dest="command")

    p_demo = sub.add_parser("demo")
    p_demo.add_argument("--policy", default="free_text")
    p_demo.add_argument("--patient", type=int, default=0)
    p_demo.add_argument("--relays", type=int, default=8)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--out", default="results")
    p_eval.add_argument("--patients", type=int, default=500)
    p_eval.add_argument("--relays", type=int, default=8)

    p_census = sub.add_parser("census")
    p_census.add_argument("--patients", type=int, default=500)

    args = parser.parse_args(argv)
    if args.command == "demo":
        return _cmd_demo(args)
    if args.command == "evaluate":
        return _cmd_evaluate(args)
    if args.command == "census":
        return _cmd_census(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
