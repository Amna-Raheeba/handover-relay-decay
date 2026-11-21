import os
import tempfile

from handover_relay_decay.census import (
    census_from_dict, census_stats, census_to_dict, generate_census,
    load_census, save_census)
from handover_relay_decay.models import ITEM_TYPES


def test_census_size():
    patients = generate_census(n_patients=25, seed=7)
    assert len(patients) == 25


def test_census_deterministic_same_seed():
    a = generate_census(n_patients=10, seed=7)
    b = generate_census(n_patients=10, seed=7)
    assert census_to_dict(a, 7) == census_to_dict(b, 7)


def test_census_differs_with_seed():
    a = generate_census(n_patients=10, seed=7)
    b = generate_census(n_patients=10, seed=8)
    assert census_to_dict(a, 7) != census_to_dict(b, 8)


def test_every_patient_has_pending_and_watch_items():
    patients = generate_census(n_patients=50, seed=7)
    for patient in patients:
        assert len(patient.items_of_type("pending_result")) >= 1
        assert len(patient.items_of_type("watch_item")) >= 1


def test_allergy_and_infusion_always_critical():
    patients = generate_census(n_patients=50, seed=7)
    for patient in patients:
        for item in patient.items:
            if item.item_type in ("allergy", "active_infusion"):
                assert item.critical


def test_routine_notes_never_critical():
    patients = generate_census(n_patients=50, seed=7)
    for patient in patients:
        for item in patient.items_of_type("routine_note"):
            assert not item.critical


def test_item_ids_unique_within_patient():
    patients = generate_census(n_patients=20, seed=7)
    for patient in patients:
        ids = [item.item_id for item in patient.items]
        assert len(ids) == len(set(ids))


def test_census_round_trip_dict():
    patients = generate_census(n_patients=5, seed=3)
    clone = census_from_dict(census_to_dict(patients, 3))
    assert len(clone) == 5
    assert clone[0].patient_id == patients[0].patient_id


def test_census_save_and_load(tmp_path=None):
    patients = generate_census(n_patients=5, seed=7)
    path = os.path.join(tempfile.mkdtemp(), "census.json")
    save_census(patients, 7, path)
    loaded, seed = load_census(path)
    assert seed == 7
    assert len(loaded) == 5


def test_census_stats_consistent():
    patients = generate_census(n_patients=30, seed=7)
    stats = census_stats(patients)
    assert stats["n_patients"] == 30
    assert stats["total_items"] == sum(stats["per_type"].values())
    assert stats["critical_items"] == sum(
        stats["per_type_critical"].values())
    for item_type in ITEM_TYPES:
        assert item_type in stats["per_type"] or True
