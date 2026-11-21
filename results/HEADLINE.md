# Headline results

Critical-item survival at relay 4 (seed 7, 500 patients, synthetic census):

- free_text: 0.708 (half-life 8.6 relays)
- sbar: 0.742 (half-life 10.0 relays)
- checklist: 0.822 (half-life 14.4 relays)
- checklist_readback: 0.898 (half-life 27.7 relays)
- checklist_pinning: 0.973 (half-life 105.9 relays)
- checklist_pinning_readback: 0.986 (half-life 160.9 relays)

Free-text loses critical information fastest: survival falls from 0.919 at relay 1 to 0.708 at relay 4 and 0.522 at relay 8. Checklist + pinning + read-back holds 0.986 at relay 4.
