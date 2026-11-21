"""The relay simulation.

Each patient enters relay 0 with their full item set. At every relay
(shift handover) each surviving item is kept with the probability given
by its base survival modified by the policy, or dropped. A dropped item
can be recovered at the same relay when the policy includes read-back.
Once dropped and not recovered, an item never returns: loss compounds
down the chain, which is the phenomenon this project measures.
"""

import random

from handover_relay_decay.models import BASE_SURVIVAL
from handover_relay_decay.policies import PIN_LOSS_SCALE


def survival_probability(item, policy):
    """Per-relay survival probability of one item under one policy."""
    base = BASE_SURVIVAL[item.item_type]
    loss = 1.0 - base
    if policy.pin_critical and item.critical:
        loss = loss * PIN_LOSS_SCALE
    else:
        loss = loss * policy.loss_scale
    return 1.0 - loss


def simulate_patient(patient, policy, rng, max_relays=8):
    """Simulate one patient. Returns the surviving items per relay.

    The result is a list of length max_relays + 1: index 0 is the
    entering set, index k is the set handed on after relay k.
    """
    alive = list(patient.items)
    history = [list(alive)]
    for _relay in range(max_relays):
        nxt = []
        for item in alive:
            p = survival_probability(item, policy)
            if rng.random() < p:
                nxt.append(item)
            elif policy.readback_recovery > 0.0:
                if rng.random() < policy.readback_recovery:
                    nxt.append(item)
        alive = nxt
        history.append(list(alive))
    return history


def simulate_census(patients, policy, seed=7, max_relays=8):
    """Simulate a whole census under one policy.

    Returns per-relay pooled counts: for each relay, how many items of
    each class survive out of how many entered. Pooling (rather than
    averaging per-patient rates) is the stated convention: every item
    counts once.
    """
    rng = random.Random("%s:%s" % (seed, policy.name))
    initial_total = 0
    initial_critical = 0
    initial_per_type = {}
    initial_per_type_critical = {}
    for patient in patients:
        for item in patient.items:
            initial_total += 1
            initial_per_type[item.item_type] = (
                initial_per_type.get(item.item_type, 0) + 1)
            if item.critical:
                initial_critical += 1
                initial_per_type_critical[item.item_type] = (
                    initial_per_type_critical.get(item.item_type, 0) + 1)

    total_curve = []
    critical_curve = []
    per_type_curves = {}
    per_type_critical_curves = {}
    histories = []
    for patient in patients:
        histories.append(
            simulate_patient(patient, policy, rng, max_relays=max_relays))

    for relay in range(max_relays + 1):
        total_alive = 0
        critical_alive = 0
        per_type_alive = {}
        per_type_critical_alive = {}
        for history in histories:
            for item in history[relay]:
                total_alive += 1
                per_type_alive[item.item_type] = (
                    per_type_alive.get(item.item_type, 0) + 1)
                if item.critical:
                    critical_alive += 1
                    per_type_critical_alive[item.item_type] = (
                        per_type_critical_alive.get(item.item_type, 0) + 1)
        total_curve.append(
            float(total_alive) / initial_total if initial_total else 0.0)
        critical_curve.append(
            float(critical_alive) / initial_critical
            if initial_critical else 0.0)
        for item_type, denom in initial_per_type.items():
            curve = per_type_curves.setdefault(item_type, [])
            curve.append(float(per_type_alive.get(item_type, 0)) / denom)
        for item_type, denom in initial_per_type_critical.items():
            curve = per_type_critical_curves.setdefault(item_type, [])
            curve.append(
                float(per_type_critical_alive.get(item_type, 0)) / denom)

    return {
        "policy": policy.name,
        "max_relays": max_relays,
        "initial_total": initial_total,
        "initial_critical": initial_critical,
        "total_survival": total_curve,
        "critical_survival": critical_curve,
        "per_type_survival": per_type_curves,
        "per_type_critical_survival": per_type_critical_curves,
    }
