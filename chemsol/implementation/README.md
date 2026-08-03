# Chemsol — Implementation Workspace

Build-ready artifacts for the Zoho Creator ERP. Console work happens in Zoho Creator (.in); this folder holds the paste-in Deluge and the executable verification harness.

```
implementation/
├── PROGRESS.md          ← phase loop log: implement → verify → fix → reverify
├── deluge/              ← paste-in Deluge scripts (house syntax: lookupRecords /
│   │                      createRecord{} / updateRecord{} / throw / sendmail)
│   ├── shared/          ← Phase 0: P1 number series, stock moves, F8 alerts
│   ├── procurement/     ← Phase 1: PO series/GST split, Post GRN (G5), PR notify
│   ├── costing/         ← Phase 2: P2 expansion, P3 chain, F7 stock, auto-PR
│   ├── mrGate/          ← Phase 3: auto-derive, P5 cross-validation, F5 auto-MIS, SLA
│   ├── production/      ← Phase 4: Post MIS (G4), P6 consume, FGHM (G6/C14), packing
│   └── site/            ← Phase 5: SCE (C21), MRT (C12), FG consumption, min/max
└── verify/
    └── flow_sim.py      ← executable oracle: mirrors ALL business logic, runs the
                            canonical UAT scenario, asserts every "Expected
                            automation" bullet grouped by phase
```

## The loop (required for every change)

1. Edit logic in `deluge/` AND mirror it in `verify/flow_sim.py`
2. Run `python verify/flow_sim.py` — must be 50/50 green
3. Any FAIL → fix doc/script/sim → rerun until green → log in PROGRESS.md
4. Only then paste into the Zoho console and tick the UAT step

## Build-time notes (from verification)

- BOM ratios are kg-per-kg-of-FG-output with full precision (0.3333, 0.5817 — C28); Section A computes `Required_Qty = round(Area × CompQty/sqm × Ratio, 1)`, `Amount = Required × Rate`
- `Fully_Consumed` fires only when ALL project allocations ≥ 100% (C29 — stays OFF in the canonical scenario)
- Numbering: every prefixed document via `numberSeries()` (P1); Auto Number field is numeric-only, `autogen()` not available in Creator (F1)
- Custom functions called by name (`numberSeries({...})`, `stockMoveRM({...})`) — wire as Function Tasks in the Workflow Builder if the console requires it
- F10 auto-release sets status directly from a schedule — verify Blueprint auto-transition at build (fallback documented in `mrSlaSchedules.deluge`)
- Deluge files use `input.X` for form fields, `item.X` for subform rows; field names match forms.html/automation.html (MR_Allocation, Consumed_Qty, 80%_Alert_Flag, …)
