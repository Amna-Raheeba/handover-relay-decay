"""Regenerate data/census.json from the seed."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from handover_relay_decay.census import generate_census, save_census

SEED = 7
N_PATIENTS = 500


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data", "census.json")
    patients = generate_census(n_patients=N_PATIENTS, seed=SEED)
    save_census(patients, SEED, out)
    print("Wrote %s (%d patients, seed %d)" % (out, len(patients), SEED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
