"""Streamlit dashboard for Handover Relay Decay.

Tabs: (1) Survival Curves — critical-item survival per policy across
8 relays; (2) Policy Comparison — relay-4/relay-8 survival and fitted
half-life per policy; (3) Item Types — per-type survival at relay 8.
"""

import json
import os

import streamlit as st

from handover_relay_decay.evaluate import run_evaluation
from handover_relay_decay.policies import POLICY_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results", "evaluation.json")


@st.cache_data
def load_results():
    if os.path.exists(RESULTS):
        with open(RESULTS, "r", encoding="utf-8") as handle:
            return json.load(handle)
    from handover_relay_decay.evaluate import evaluation_to_jsonable
    return evaluation_to_jsonable(run_evaluation(n_patients=100))


st.set_page_config(page_title="Handover Relay Decay", layout="wide")
st.title("Handover Relay Decay — critical information loss across shift chains")
st.caption(
    "Seeded synthetic census only. No real patient data. Survival "
    "parameters are declared simulation parameters.")

data = load_results()
runs = data["runs"]
summaries = data["summaries"]

tab_curves, tab_compare, tab_types = st.tabs(
    ["Survival Curves", "Policy Comparison", "Item Types"])

with tab_curves:
    st.subheader("Critical-item survival by relay")
    chart = {}
    for name in POLICY_ORDER:
        chart[name] = runs[name]["critical_survival"]
    st.line_chart(chart)
    st.write(
        "Relay 1 is single-handover completeness — the number most "
        "audits report. The curve shows what it hides: loss compounds "
        "across successive handovers.")

with tab_compare:
    st.subheader("Policy comparison")
    rows = []
    for name in POLICY_ORDER:
        s = summaries[name]
        half = s["critical_half_life_fitted"]
        rows.append({
            "policy": name,
            "critical @1": s["critical_survival_relay_1"],
            "critical @4": s["critical_survival_relay_4"],
            "critical @8": s["critical_survival_relay_8"],
            "all items @8": s["total_survival_relay_8"],
            "fitted half-life (relays)": half,
        })
    st.table(rows)

with tab_types:
    st.subheader("Per-type survival at relay 8")
    choice = st.selectbox("Policy", options=list(POLICY_ORDER))
    per_type = runs[choice]["per_type_survival"]
    values = dict(
        (item_type, curve[8]) for item_type, curve in per_type.items())
    st.bar_chart(values)
    st.write(
        "Routine notes decay fastest; pinned critical classes "
        "(allergies, infusions) decay slowest under pinning policies.")
