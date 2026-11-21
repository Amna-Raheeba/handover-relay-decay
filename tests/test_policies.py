import pytest

from handover_relay_decay.policies import (
    PIN_LOSS_SCALE, POLICIES, POLICY_ORDER, get_policy)


def test_policy_order_covers_all_policies():
    assert set(POLICY_ORDER) == set(POLICIES.keys())
    assert len(POLICY_ORDER) == 6


def test_free_text_is_the_unmodified_baseline():
    policy = get_policy("free_text")
    assert policy.loss_scale == 1.0
    assert policy.readback_recovery == 0.0
    assert not policy.pin_critical


def test_structured_policies_lose_less_than_free_text():
    for name in ("sbar", "checklist"):
        assert get_policy(name).loss_scale < 1.0


def test_readback_policies_have_recovery():
    assert get_policy("checklist_readback").readback_recovery > 0.0
    assert get_policy("checklist_pinning_readback").readback_recovery > 0.0


def test_pinning_policies_pin():
    assert get_policy("checklist_pinning").pin_critical
    assert get_policy("checklist_pinning_readback").pin_critical
    assert not get_policy("checklist_readback").pin_critical


def test_pin_loss_scale_is_small():
    assert 0.0 < PIN_LOSS_SCALE < 0.2


def test_unknown_policy_raises():
    with pytest.raises(ValueError):
        get_policy("carrier_pigeon")


def test_policy_to_dict_round_trip_fields():
    data = get_policy("sbar").to_dict()
    assert data["name"] == "sbar"
    assert data["loss_scale"] == 0.78
    assert "description" in data
