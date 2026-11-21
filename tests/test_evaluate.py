import json
import os

from handover_relay_decay.evaluate import (
    evaluation_to_jsonable, run_evaluation, write_results)
from handover_relay_decay.policies import POLICY_ORDER


def _small():
    return run_evaluation(n_patients=40, seed=7, max_relays=8)


def test_evaluation_covers_all_policies():
    result = _small()
    assert set(result["summaries"].keys()) == set(POLICY_ORDER)


def test_headline_relay4_free_text_below_pinning_readback():
    result = _small()
    headline = result["headline"]["critical_survival_relay_4"]
    assert (headline["free_text"]
            < headline["checklist_pinning_readback"])


def test_headline_contains_half_lives():
    result = _small()
    half = result["headline"]["critical_half_life_fitted"]
    assert half["free_text"] is not None
    assert (half["checklist_pinning_readback"] is None
            or half["checklist_pinning_readback"] > half["free_text"])


def test_relay1_hides_compounding():
    # Single-handover completeness overstates what survives a chain:
    # the relay-1 gap between worst and best policy is smaller than
    # the relay-4 gap.
    result = _small()
    s = result["summaries"]
    gap1 = (s["checklist_pinning_readback"]["critical_survival_relay_1"]
            - s["free_text"]["critical_survival_relay_1"])
    gap4 = (s["checklist_pinning_readback"]["critical_survival_relay_4"]
            - s["free_text"]["critical_survival_relay_4"])
    assert gap4 > gap1


def test_evaluation_deterministic():
    a = evaluation_to_jsonable(_small())
    b = evaluation_to_jsonable(_small())
    assert a["headline"] == b["headline"]
    assert a["summaries"] == b["summaries"]


def test_jsonable_is_json_serialisable():
    jsonable = evaluation_to_jsonable(_small())
    text = json.dumps(jsonable)
    assert "free_text" in text


def test_write_results_creates_four_files(tmp_path):
    out = str(tmp_path)
    write_results(_small(), out)
    for name in ("evaluation.json", "evaluation.csv",
                 "evaluation_summary.md", "HEADLINE.md"):
        assert os.path.exists(os.path.join(out, name))


def test_written_json_matches_in_memory(tmp_path):
    result = _small()
    write_results(result, str(tmp_path))
    with open(os.path.join(str(tmp_path), "evaluation.json"),
              encoding="utf-8") as handle:
        saved = json.load(handle)
    assert saved["headline"] == evaluation_to_jsonable(result)["headline"]
