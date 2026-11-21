# Evaluation summary

Seeded synthetic census: 500 patients, seed 7, 8 relays. All data is synthetic; survival parameters are declared simulation parameters, not measurements from real handovers.

Census: 3953 items entered the chain, 1888 of them critical.

| Policy | Critical @1 | Critical @4 | Critical @8 | All items @8 | Fitted half-life |
|---|---|---|---|---|---|
| free_text | 0.919 | 0.708 | 0.522 | 0.389 | 8.6 relays |
| sbar | 0.925 | 0.742 | 0.575 | 0.459 | 10.0 relays |
| checklist | 0.953 | 0.822 | 0.680 | 0.561 | 14.4 relays |
| checklist_readback | 0.971 | 0.898 | 0.820 | 0.729 | 27.7 relays |
| checklist_pinning | 0.992 | 0.973 | 0.948 | 0.698 | 105.9 relays |
| checklist_pinning_readback | 0.997 | 0.986 | 0.967 | 0.795 | 160.9 relays |

Relay 1 is single-handover completeness: the number most handover audits report. The relay-4 and relay-8 columns show what that number hides once handovers compound across a multi-shift chain.
