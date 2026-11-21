import random

from handover_relay_decay.census import generate_census
from handover_relay_decay.models import BASE_SURVIVAL, Item, Patient
from handover_relay_decay.policies import get_policy
from handover_relay_decay.relay import (
    simulate_census, simulate_patient, survival_probability)


def _patient():
    items = [
        Item("a", "allergy", "penicillin allergy", True),
        Item("b", "pending_result", "troponin result pending", True),
        Item("c", "routine_note", "mobilises with frame", False),
    ]
    return Patient("PX", items)


def test_survival_probability_free_text_equals_base():
    item = Item("a", "allergy", "x", True)
    p = survival_probability(item, get_policy("free_text"))
    assert abs(p - BASE_SURVIVAL["allergy"]) < 1e-12


def test_survival_probability_checklist_beats_free_text():
    item = Item("a", "watch_item", "x", False)
    assert (survival_probability(item, get_policy("checklist"))
            > survival_probability(item, get_policy("free_text")))


def test_pinning_helps_critical_more_than_routine():
    policy = get_policy("checklist_pinning")
    critical = Item("a", "allergy", "x", True)
    routine = Item("b", "routine_note", "y", False)
    gain_critical = (survival_probability(critical, policy)
                     - survival_probability(critical,
                                            get_policy("checklist")))
    gain_routine = (survival_probability(routine, policy)
                    - survival_probability(routine,
                                           get_policy("checklist")))
    assert gain_critical > gain_routine
    assert gain_routine == 0.0


def test_pinning_does_not_change_non_critical_probability():
    item = Item("a", "pending_result", "x", False)
    assert (survival_probability(item, get_policy("checklist_pinning"))
            == survival_probability(item, get_policy("checklist")))


def test_history_shape_and_monotone_shrinkage():
    rng = random.Random(1)
    history = simulate_patient(_patient(), get_policy("free_text"), rng,
                               max_relays=8)
    assert len(history) == 9
    sizes = [len(alive) for alive in history]
    assert sizes[0] == 3
    for earlier, later in zip(sizes, sizes[1:]):
        assert later <= earlier


def test_dropped_items_never_return():
    rng = random.Random(2)
    history = simulate_patient(_patient(), get_policy("free_text"), rng,
                               max_relays=8)
    seen_alive = set(item.item_id for item in history[0])
    for alive in history[1:]:
        ids = set(item.item_id for item in alive)
        assert ids <= seen_alive
        seen_alive = ids


def test_simulation_deterministic():
    patients = generate_census(n_patients=10, seed=7)
    policy = get_policy("sbar")
    a = simulate_census(patients, policy, seed=7)
    b = simulate_census(patients, policy, seed=7)
    assert a["critical_survival"] == b["critical_survival"]


def test_curves_start_at_one_and_stay_in_unit_interval():
    patients = generate_census(n_patients=20, seed=7)
    run = simulate_census(patients, get_policy("free_text"), seed=7)
    assert run["critical_survival"][0] == 1.0
    assert run["total_survival"][0] == 1.0
    for value in run["critical_survival"] + run["total_survival"]:
        assert 0.0 <= value <= 1.0


def test_critical_survival_decays_under_free_text():
    patients = generate_census(n_patients=100, seed=7)
    run = simulate_census(patients, get_policy("free_text"), seed=7)
    assert run["critical_survival"][8] < run["critical_survival"][4]
    assert run["critical_survival"][4] < run["critical_survival"][1]


def test_pinning_readback_beats_free_text_at_relay_8():
    patients = generate_census(n_patients=100, seed=7)
    best = simulate_census(
        patients, get_policy("checklist_pinning_readback"), seed=7)
    base = simulate_census(patients, get_policy("free_text"), seed=7)
    assert (best["critical_survival"][8]
            > base["critical_survival"][8])


def test_per_type_curves_present():
    patients = generate_census(n_patients=10, seed=7)
    run = simulate_census(patients, get_policy("sbar"), seed=7)
    for item_type in ("allergy", "pending_result", "watch_item"):
        assert item_type in run["per_type_survival"]
        assert len(run["per_type_survival"][item_type]) == 9
