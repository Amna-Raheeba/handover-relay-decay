"""Notebook 1 (as a runnable script): one patient through the relay.

Shows a single synthetic patient's item set decaying across 8 relays
under the free-text policy, then under checklist + pinning + read-back.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from handover_relay_decay.census import generate_census
from handover_relay_decay.policies import get_policy
from handover_relay_decay.relay import simulate_patient
from handover_relay_decay.report import patient_trace_markdown


def main():
    patients = generate_census(n_patients=5, seed=7)
    patient = patients[0]
    for name in ("free_text", "checklist_pinning_readback"):
        policy = get_policy(name)
        rng = random.Random("7:%s:demo" % name)
        history = simulate_patient(patient, policy, rng, max_relays=8)
        print("Policy: %s" % name)
        print(patient_trace_markdown(patient, history))
        print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
