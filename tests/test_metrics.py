import math

import pytest

from handover_relay_decay.metrics import (
    curve_auc, empirical_half_life, fit_half_life, summarise_run,
    survival_at)


def _exp_curve(rate, relays=8):
    return [math.exp(-rate * k) for k in range(relays + 1)]


def test_fit_half_life_recovers_known_exponential():
    curve = _exp_curve(0.1)
    fitted = fit_half_life(curve)
    assert fitted is not None
    assert abs(fitted - math.log(2.0) / 0.1) < 0.2


def test_fit_half_life_faster_decay_is_shorter():
    fast = fit_half_life(_exp_curve(0.3))
    slow = fit_half_life(_exp_curve(0.05))
    assert fast < slow


def test_fit_half_life_flat_curve_is_none():
    assert fit_half_life([1.0] * 9) is None


def test_fit_half_life_short_curve_is_none():
    assert fit_half_life([1.0]) is None


def test_empirical_half_life_exact_crossing():
    curve = [1.0, 0.8, 0.6, 0.4, 0.3]
    value = empirical_half_life(curve)
    assert value is not None
    assert 2.0 < value < 3.0


def test_empirical_half_life_never_crossing_is_none():
    assert empirical_half_life([1.0, 0.9, 0.8]) is None


def test_empirical_half_life_interpolation_value():
    curve = [1.0, 0.75, 0.25]
    # Crossing between relay 1 (0.75) and relay 2 (0.25):
    # fraction = (0.75 - 0.5) / (0.75 - 0.25) = 0.5 -> 1.5
    assert abs(empirical_half_life(curve) - 1.5) < 1e-9


def test_curve_auc_of_perfect_survival_is_one():
    assert abs(curve_auc([1.0] * 9) - 1.0) < 1e-12


def test_curve_auc_bounds():
    value = curve_auc(_exp_curve(0.2))
    assert 0.0 < value < 1.0


def test_survival_at_reads_and_guards():
    curve = [1.0, 0.5, 0.25]
    assert survival_at(curve, 2) == 0.25
    with pytest.raises(ValueError):
        survival_at(curve, 3)


def test_summarise_run_fields():
    run = {
        "policy": "free_text",
        "max_relays": 8,
        "critical_survival": _exp_curve(0.1),
        "total_survival": _exp_curve(0.15),
    }
    summary = summarise_run(run)
    assert summary["policy"] == "free_text"
    assert summary["critical_survival_relay_1"] == _exp_curve(0.1)[1]
    assert summary["critical_half_life_fitted"] is not None
