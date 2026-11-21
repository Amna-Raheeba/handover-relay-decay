"""Run one demo patient through the relay under two policies."""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from handover_relay_decay.census import census_from_dict
from handover_relay_decay.policies import get_policy
from handover_relay_decay.relay import simulate_patient
from handover_relay_decay.report import patient_trace_markdown

import json


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "demo_patient.json"), "r",
              encoding="utf-8") as handle:
        data = json.load(handle)
    patient = census_from_dict({"patients": [data]})[0]
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
