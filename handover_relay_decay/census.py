"""Seeded synthetic census generation.

The census is fully synthetic: labels come from fixed generic pools,
counts and criticality flags are drawn from a seeded generator. No real
patient data is used anywhere in this project.
"""

import json
import random

from handover_relay_decay.models import ALWAYS_CRITICAL, Item, Patient

LABEL_POOLS = {
    "allergy": [
        "penicillin allergy",
        "latex allergy",
        "contrast dye allergy",
        "sulfonamide allergy",
        "peanut allergy",
    ],
    "pending_result": [
        "troponin result pending",
        "blood culture result pending",
        "CT report pending",
        "potassium recheck pending",
        "wound swab result pending",
    ],
    "active_infusion": [
        "insulin infusion running",
        "heparin infusion running",
        "noradrenaline infusion running",
        "IV fluids running",
        "antibiotic infusion running",
    ],
    "watch_item": [
        "watch urine output",
        "watch oxygen saturation trend",
        "watch drain output",
        "watch confusion score",
        "watch temperature trend",
    ],
    "routine_note": [
        "prefers tea without sugar",
        "mobilises with frame",
        "family visits in evenings",
        "hearing aid in left ear",
        "nil by mouth from midnight",
    ],
}

# (min, max) item counts per patient, by type.
COUNT_RANGES = {
    "allergy": (0, 2),
    "pending_result": (1, 3),
    "active_infusion": (0, 2),
    "watch_item": (1, 3),
    "routine_note": (1, 3),
}

# Probability that a pending result or watch item is flagged critical.
FLAGGED_CRITICAL_PROB = {
    "pending_result": 0.5,
    "watch_item": 0.4,
}


def _make_item(rng, patient_id, index, item_type):
    pool = LABEL_POOLS[item_type]
    label = pool[rng.randrange(len(pool))]
    if item_type in ALWAYS_CRITICAL:
        critical = True
    elif item_type in FLAGGED_CRITICAL_PROB:
        critical = rng.random() < FLAGGED_CRITICAL_PROB[item_type]
    else:
        critical = False
    item_id = "%s-i%02d" % (patient_id, index)
    return Item(item_id, item_type, label, critical)


def generate_census(n_patients=500, seed=7):
    """Generate a deterministic synthetic census."""
    rng = random.Random(seed)
    patients = []
    for n in range(n_patients):
        patient_id = "P%04d" % (n + 1)
        items = []
        index = 0
        for item_type in (
            "allergy",
            "pending_result",
            "active_infusion",
            "watch_item",
            "routine_note",
        ):
            low, high = COUNT_RANGES[item_type]
            count = rng.randint(low, high)
            for _ in range(count):
                index += 1
                items.append(_make_item(rng, patient_id, index, item_type))
        patients.append(Patient(patient_id, items))
    return patients


def census_to_dict(patients, seed):
    return {
        "seed": seed,
        "n_patients": len(patients),
        "patients": [patient.to_dict() for patient in patients],
    }


def census_from_dict(data):
    return [Patient.from_dict(raw) for raw in data["patients"]]


def save_census(patients, seed, path):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(census_to_dict(patients, seed), handle, indent=1)


def load_census(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return census_from_dict(data), data["seed"]


def census_stats(patients):
    """Summary counts used by the CLI and the evaluation."""
    total_items = 0
    critical_items = 0
    per_type = {}
    per_type_critical = {}
    for patient in patients:
        for item in patient.items:
            total_items += 1
            per_type[item.item_type] = per_type.get(item.item_type, 0) + 1
            if item.critical:
                critical_items += 1
                per_type_critical[item.item_type] = (
                    per_type_critical.get(item.item_type, 0) + 1)
    return {
        "n_patients": len(patients),
        "total_items": total_items,
        "critical_items": critical_items,
        "per_type": per_type,
        "per_type_critical": per_type_critical,
    }
