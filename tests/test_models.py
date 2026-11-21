import pytest

from handover_relay_decay.models import (
    ALWAYS_CRITICAL, BASE_SURVIVAL, ITEM_TYPES, Item, Patient)


def test_item_types_are_the_five_declared():
    assert set(ITEM_TYPES) == {
        "allergy", "pending_result", "active_infusion",
        "watch_item", "routine_note"}


def test_base_survival_covers_every_type():
    for item_type in ITEM_TYPES:
        assert 0.0 < BASE_SURVIVAL[item_type] < 1.0


def test_always_critical_types():
    assert set(ALWAYS_CRITICAL) == {"allergy", "active_infusion"}


def test_item_round_trip():
    item = Item("P0001-i01", "allergy", "penicillin allergy", True)
    clone = Item.from_dict(item.to_dict())
    assert clone.item_id == item.item_id
    assert clone.item_type == item.item_type
    assert clone.label == item.label
    assert clone.critical is True


def test_item_rejects_unknown_type():
    with pytest.raises(ValueError):
        Item("x", "diagnosis", "label", False)


def test_patient_critical_items_filter():
    items = [
        Item("a", "allergy", "x", True),
        Item("b", "routine_note", "y", False),
        Item("c", "watch_item", "z", True),
    ]
    patient = Patient("P1", items)
    assert [i.item_id for i in patient.critical_items()] == ["a", "c"]


def test_patient_items_of_type():
    items = [
        Item("a", "allergy", "x", True),
        Item("b", "allergy", "y", True),
        Item("c", "watch_item", "z", False),
    ]
    patient = Patient("P1", items)
    assert len(patient.items_of_type("allergy")) == 2
    assert len(patient.items_of_type("pending_result")) == 0


def test_patient_round_trip():
    items = [Item("a", "allergy", "x", True),
             Item("b", "routine_note", "y", False)]
    patient = Patient("P9", items)
    clone = Patient.from_dict(patient.to_dict())
    assert clone.patient_id == "P9"
    assert len(clone.items) == 2
    assert clone.items[0].label == "x"
