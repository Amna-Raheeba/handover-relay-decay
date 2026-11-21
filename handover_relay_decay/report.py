"""Markdown reporting for evaluation results."""

from handover_relay_decay.policies import POLICY_ORDER


def _fmt(value, digits=3):
    if value is None:
        return "n/a"
    return "%.*f" % (digits, value)


def _half_life_text(value, max_relays):
    if value is None:
        return "> %d (no decay fitted)" % max_relays
    return "%.1f relays" % value


def summary_markdown(result):
    lines = []
    lines.append("# Evaluation summary")
    lines.append("")
    lines.append(
        "Seeded synthetic census: %d patients, seed %d, %d relays. "
        "All data is synthetic; survival parameters are declared "
        "simulation parameters, not measurements from real handovers."
        % (result["n_patients"], result["seed"], result["max_relays"]))
    lines.append("")
    lines.append(
        "Census: %d items entered the chain, %d of them critical."
        % (result["census"]["total_items"],
           result["census"]["critical_items"]))
    lines.append("")
    lines.append(
        "| Policy | Critical @1 | Critical @4 | Critical @8 | "
        "All items @8 | Fitted half-life |")
    lines.append("|---|---|---|---|---|---|")
    for name in POLICY_ORDER:
        s = result["summaries"][name]
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            name,
            _fmt(s["critical_survival_relay_1"]),
            _fmt(s["critical_survival_relay_4"]),
            _fmt(s["critical_survival_relay_8"]),
            _fmt(s["total_survival_relay_8"]),
            _half_life_text(s["critical_half_life_fitted"],
                            result["max_relays"]),
        ))
    lines.append("")
    lines.append(
        "Relay 1 is single-handover completeness: the number most "
        "handover audits report. The relay-4 and relay-8 columns show "
        "what that number hides once handovers compound across a "
        "multi-shift chain.")
    lines.append("")
    return "\n".join(lines)


def headline_markdown(result):
    summaries = result["summaries"]
    free = summaries["free_text"]
    best = summaries["checklist_pinning_readback"]
    lines = []
    lines.append("# Headline results")
    lines.append("")
    lines.append(
        "Critical-item survival at relay 4 (seed %d, %d patients, "
        "synthetic census):" % (result["seed"], result["n_patients"]))
    lines.append("")
    for name in POLICY_ORDER:
        s = summaries[name]
        lines.append("- %s: %s (half-life %s)" % (
            name,
            _fmt(s["critical_survival_relay_4"]),
            _half_life_text(s["critical_half_life_fitted"],
                            result["max_relays"]),
        ))
    lines.append("")
    lines.append(
        "Free-text loses critical information fastest: survival falls "
        "from %s at relay 1 to %s at relay 4 and %s at relay 8. "
        "Checklist + pinning + read-back holds %s at relay 4."
        % (
            _fmt(free["critical_survival_relay_1"]),
            _fmt(free["critical_survival_relay_4"]),
            _fmt(free["critical_survival_relay_8"]),
            _fmt(best["critical_survival_relay_4"]),
        ))
    lines.append("")
    return "\n".join(lines)


def patient_trace_markdown(patient, history):
    """A short human-readable trace of one patient's relay history."""
    lines = []
    lines.append("Patient %s entered with %d items (%d critical)."
                 % (patient.patient_id, len(patient.items),
                    len(patient.critical_items())))
    for relay, alive in enumerate(history):
        critical_alive = len([i for i in alive if i.critical])
        lines.append(
            "After relay %d: %d items remain, %d of them critical."
            % (relay, len(alive), critical_alive))
    return "\n".join(lines)
