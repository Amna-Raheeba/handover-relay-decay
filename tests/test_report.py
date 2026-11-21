import random

from handover_relay_decay.census import generate_census
from handover_relay_decay.evaluate import run_evaluation
from handover_relay_decay.policies import get_policy
from handover_relay_decay.relay import simulate_patient
from handover_relay_decay.report import (
    headline_markdown, patient_trace_markdown, summary_markdown)


def test_summary_markdown_lists_every_policy():
    result = run_evaluation(n_patients=20, seed=7)
    text = summary_markdown(result)
    for name in ("free_text", "sbar", "checklist",
                 "checklist_pinning_readback"):
        assert name in text


def test_summary_markdown_states_synthetic_caveat():
    result = run_evaluation(n_patients=20, seed=7)
    assert "synthetic" in summary_markdown(result).lower()


def test_headline_markdown_mentions_relay_4():
    result = run_evaluation(n_patients=20, seed=7)
    text = headline_markdown(result)
    assert "relay 4" in text


def test_patient_trace_counts_critical():
    patients = generate_census(n_patients=3, seed=7)
    patient = patients[0]
    rng = random.Random(0)
    history = simulate_patient(patient, get_policy("free_text"), rng)
    text = patient_trace_markdown(patient, history)
    assert patient.patient_id in text
    assert "After relay 8" in text
