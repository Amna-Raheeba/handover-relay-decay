# Handover Relay Decay

## 1. What this is

A deterministic, offline simulation of a patient handover chain across
multiple shifts. Each synthetic patient enters the chain with a
structured item set (allergies, pending results, active infusions,
watch-items, routine notes). At every relay (one shift handover) each
surviving item can be dropped, depending on the compression policy in
force. The tool measures the **critical-item survival curve over 1–8
relays** — an information half-life per policy — instead of the
single-handover completeness number that handover audits usually
report.

Pure Python standard library. No API keys, no network, no real patient
data: the census is seeded synthetic data with declared simulation
parameters.

## 2. The novel mechanism

Handover research studies one handover at a time. This tool models a
handover as a **relay**: loss at each shift compounds on what the
previous shift already lost, so a policy that looks 92% complete on a
single handover can deliver barely half the critical items by the
eighth. The mechanism has three parts:

1. **Relay-chain survival curves** — pooled critical-item survival at
   every relay 0–8, per policy and per item type, against seeded
   ground truth (the entering item set is known exactly).
2. **Information half-life** — an exponential fit (least squares on
   log-survival) plus an empirical crossing point, per policy, so
   policies are compared by decay rate, not by one snapshot.
3. **Repair interventions as decay modifiers** — read-back (a dropped
   item can be recovered at the same relay) and critical-item pinning
   (critical items travel in a pinned section whose loss rate is cut
   to 8% of base) are modelled as separate, composable interventions,
   so their individual and combined effects are measurable.

## 3. Prior art and the differentiator

SBAR and handover studies are observational and single-handover:
PACU SBAR completeness audits score one handover's content, and ICU
SBAR checklist studies report missed items falling from 7.26% to
2.02% at one transition. None simulates a multi-shift relay chain,
none compares compression policies by critical-item half-life, and
none measures against seeded ground truth where the true entering
item set is known. The relay-decay framing — decay compounding across
successive handovers, with repair interventions that flatten the
curve — is the differentiator.

## 4. Policies compared

| Policy | Mechanism |
|---|---|
| `free_text` | Free-text summary; per-type base survival, unmodified |
| `sbar` | SBAR structure; loss rate × 0.78 |
| `checklist` | Checklist-forced; loss rate × 0.58 |
| `checklist_readback` | Checklist + read-back recovery (45% of drops) |
| `checklist_pinning` | Checklist + critical items pinned (loss × 0.08) |
| `checklist_pinning_readback` | Checklist + pinning + read-back |

Base per-relay survival by item type (declared parameters):
allergy 0.94, pending result 0.89, active infusion 0.96, watch item
0.86, routine note 0.80.

## 5. Measured headline results

Seeded synthetic census: 500 patients, 3,953 items (1,888 critical),
seed 7, 8 relays. Full tables in `results/`.

| Policy | Critical @1 | Critical @4 | Critical @8 | Fitted half-life |
|---|---|---|---|---|
| free_text | 0.919 | 0.708 | 0.522 | 8.6 relays |
| sbar | 0.925 | 0.742 | 0.575 | 10.0 relays |
| checklist | 0.953 | 0.822 | 0.680 | 14.4 relays |
| checklist_readback | 0.971 | 0.898 | 0.820 | 27.7 relays |
| checklist_pinning | 0.992 | 0.973 | 0.948 | 105.9 relays |
| checklist_pinning_readback | 0.997 | 0.986 | 0.967 | 160.9 relays |

The relay-1 column is the finding in miniature: at one handover the
worst and best policies differ by 0.078 of critical items; by relay 4
the gap is 0.278 and by relay 8 it is 0.445. Single-handover
completeness hides the compounding.

## 6. Honest limits

- **Synthetic data only.** The census is generated, and the survival
  parameters are declared design choices, not measurements from real
  handovers. The numbers show what the model implies, not what any
  ward experiences.
- **The policy ranking is partly built into the parameters.** SBAR
  and checklist loss scales (0.78, 0.58) are assumptions; the
  contribution is the relay-chain measurement and the size of the
  compounding gap, not proof that a real checklist cuts loss by 42%.
- **Fitted half-lives beyond the 8-relay window are extrapolations**
  of the fitted exponential (pinning policies barely decay inside
  the window, so their fitted half-lives are large and uncertain).
- **Items are independent.** Real handovers lose correlated bundles
  (a missed page loses everything on it); this model drops items
  independently, which understates tail risk.
- **A dropped item never returns** except through read-back at the
  same relay; real teams sometimes recover information from the
  chart later.

## 7. Quick start

```
python -m handover_relay_decay census          # census summary
python -m handover_relay_decay demo            # one patient, 8 relays
python -m handover_relay_decay evaluate        # full run -> results/
python scripts/reproduce_results.py            # drift-guarded check
streamlit run app.py                           # dashboard
```

## 8. Repository layout

- `handover_relay_decay/` — models, census generation, policies,
  relay simulation, metrics, evaluation, reporting, CLI
- `data/` — `census.json` (500 seeded patients), `hand_cases.json`
  (3 hand-written patients for hand-checking)
- `tests/` — pytest suite (run with plain `pytest`)
- `notebooks/` — demo and evaluation experiments as runnable scripts
- `examples/` — one demo patient, a runner, and a sample report
- `scripts/` — census builder and the drift-guarded reproducer
- `results/` — evaluation.json / .csv / summary / headline
- `app.py` — Streamlit dashboard (survival curves, policy
  comparison, per-type survival)

## 9. Author and licence

By Amna Raheeba. MIT licence (see `LICENSE`).
