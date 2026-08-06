# Chemsol — Zoho Creator ERP (Root AGENTS.md)

Planning repo for a Zoho Creator ERP at Chemsol (flooring/construction materials). Contains specs, Deluge automation scripts, HTML mockups, and a Python verification harness. Actual deployment is in Zoho Creator (.in), not in this repo.

## What this repo holds

- `chemsol/` — main project: specs, automations, mockups, verification
- `AdaniConneX/` — separate ZohoCRM project
- `budget-tracking-handoff/` — separate handoff project
- `zoho-ai-service/` — Phase 2 Python/FastAPI microservice (not connected yet)
- Root `*.html` files — interactive prototypes/mockups (not production)

## Core process flow

```
SO (Sales Order)
  → Costing Sheet (Costing team: 5-section auto-expanded from SO × BOM)
    → Costing Approved → auto-create Project + Production Plan
      → Production Plan Released → auto-PR for stock shortages
        → MR auto-derived from Costing Sheet (4 cost pre-filled; Draft → Pending Production Verification → Production Verified → Costing Approved)
          → MR Released [CRITICAL GATE]
            → auto-MIS → Store issues RM to Production
              → Production (BMR → RM Consumption → Packing)
                → FGHM (FG Handover → FG Stock +)
                  → Site Consumption Entry (hourly/daily per area)
                    → Material Return (unused RM back to Store)
                      → Project Close → P&L
```

**Stream A (no Project ID):** PR → PO → GRN → QC — stock procurement
**Stream B (Project ID root):** SO(Supply+Apply) → Costing Sheet → Production Plan → MR → MIS → Production → FGHM → Site Consumption → Material Return

SO(Supply Only) = direct FG sale, NO Project created.

## Source-of-truth files (read before building)

| File | What it contains |
|------|-----------------|
| `chemsol/IMPLEMENTATION_PLAN.md` | Field-level specs for all 18+ modules, automations, numbering series |
| `chemsol/AGENTS.md` | Two-stream architecture, form inventory, consumption tracking rules |
| `chemsol/BRD_PRD_RFP.md` | Full BRD, PRD, RFP — constraints, Deluge automation catalog |
| `chemsol/Creator Forms Screen.xlsx` | 18-sheet Excel — sole source of truth for form fields and rules |
| `chemsol/UAT_VERIFICATION_PLAN.md` | Full UAT walkthrough with sample data and expected outcomes |

## Key architecture facts

- **MR is auto-derived from Costing Sheet** — zero manual re-entry. Standalone Costing Sheet module added before MR.
- **MR is the critical approval gate** — no MIS, production, or execution without MR Released
- **MR 5-state Blueprint**: Draft → Pending Production Verification → Production Verified → Costing Approved → Released
- **SO↔BOM↔MR cross-validation**: quantity mismatch >5% flags, >10% blocks (per-RM, not aggregate)
- **Consumption tracking**: BMR, RM Consumption, and **Site Consumption Entry** (hourly/daily per area) resolve to MR Allocation line matched by `Project ID + Item Code`
- **80% alert**: real-time — fires within 1 min of threshold breach (pop-up + dashboard + email)
- **100% alert**: "Allocation Exhausted" → PM + Purchase
- **Project = root entity** for all Stream B forms; Stream A forms carry NO Project ID
- **PO numbering**: Coding materials = `RMWAD-YYYY-XXXX`, Non-coding = `RM-YYYY-XXXX`
- **System codes**: EP=Epoxy, PU=PU Flooring, DEM=Demarcation, ANTI=Anti Static, ESD, FIL=Coving
- **Available Stock** for Production Plan = physical stock − Σ(Assigned Qty from all unreleased MRs) — prevents double-allocation
- **Inventory per project**: MR records Assigned Qty per RM; consumption deducted from project allocation, not generic pool

## Project inventory tracking

Each project tracks in real time:
- **Assigned Qty** (from MR Material Allocation)
- **Issued Qty** (from MIS)
- **Consumed Qty** (from BMR + Site Consumption entries)
- **Returned Qty** (from Material Return)
- **Remaining** = Assigned Qty − Consumed Qty + Returned Qty
- Reports show consumed vs remaining per project for P&L

## Implementation workspace (`chemsol/implementation/`)

Paste-in Deluge scripts + executable verification harness for the Zoho Creator console.

```
chemsol/implementation/
├── PROGRESS.md            ← phase loop log: implement → verify → fix → reverify
├── deluge/                ← paste-in Deluge scripts (26 files, 6 subdirs)
│   ├── shared/            ← Phase 0: numberSeries, stockMoveRM/FG, checkAllocationAlert
│   ├── procurement/       ← Phase 1: poSeriesPrefix, poGstSplit, postGRN, prStatusNotify
│   ├── costing/           ← Phase 2: expandCosting, costingApproveChain, getAvailableStock, planReleaseAutoPR, costingSlaEscalate
│   ├── mrGate/            ← Phase 3: mrDerive, crossValidate, mrReleaseAutoMIS, mrSlaSchedules
│   ├── production/        ← Phase 4: postMIS, consumeAllocation, bmrSubmit, fghmAccept, packingDeduct
│   └── site/              ← Phase 5: sceSubmit, materialReturn, fgConsumption, inventoryAlerts
└── verify/
    └── flow_sim.py        ← executable oracle: mirrors ALL business logic, 72 assertions
```

## Build & test

The only executable is the verification harness (Python 3, no deps):

```
python chemsol/implementation/verify/flow_sim.py
```

Must exit 0 with **72/72 green**. Any FAIL → fix Deluge script + mirror fix in `flow_sim.py` → rerun → log in PROGRESS.md.

**Loop discipline** (required for every change):
1. Edit logic in `deluge/` AND mirror it in `verify/flow_sim.py`
2. Run `python verify/flow_sim.py` — must be 72/72 green
3. Any FAIL → fix doc/script/sim → rerun until green → log in PROGRESS.md
4. Only then paste into the Zoho console and tick the UAT step

## Deluge conventions

- Files use `input.X` for form fields, `item.X` for subform rows
- Field names match `chemsol/forms.html` and `chemsol/automation.html` (MR_Allocation, Consumed_Qty, 80%_Alert_Flag, etc.)
- Custom functions called by name: `numberSeries({...})`, `stockMoveRM({...})` — wire as Function Tasks in Workflow Builder
- BOM ratios are kg-per-kg-of-FG-output with full precision (0.3333, 0.5817 — not rounded to 2dp)
- Section A computes: `Required_Qty = round(Area × CompQty/sqm × Ratio, 1)`, `Amount = Required × Rate`
- F10 auto-release sets status directly from a schedule — verify Blueprint auto-transition at build (fallback in `mrSlaSchedules.deluge`)

## Git conventions

- Commit messages: `module: description` — e.g. `C32/C33: fix 8 deluge bugs + new costingSlaEscalate.deluge`
- Findings prefixed `C##` (corrections) or `F##` (findings) — cross-referenced in PROGRESS.md
- Branch: `main` — GitHub Pages auto-deploys from main

## Pitfalls

- **BOM precision**: Ratios must be 4dp (0.3333, not 0.33). Rounded ratios break Section A totals and downstream cross-validation. This was C28.
- **MR 5-state**: Don't assume Draft→Released is 2 steps. It's 5 states; SLA reminders only fire in Draft, not after state transitions move the MR out.
- **Cross-validation is per-RM, not aggregate**: A single line +6% flags, +11% blocks. Aggregate pass masks individual line errors (C31).
- **`Fully_Consumed` flag**: Only fires when ALL project allocations ≥ 100%. FGHM accept on 1 line with another at 99.6% keeps it OFF (C29).
- **`flow_sim.py` is the source of truth for assertions**: If a Deluge script changes, the sim must change too. Never commit a Deluge fix without updating the sim.
- **No CI test gate**: GitHub Pages deploys on push to main with no validation. Run `flow_sim.py` locally before committing.
- **SLA reminder fires once**: The guard in `mrSlaSchedules.deluge` prevents re-reminder after the first fires. Don't remove the guard (C32 fix).
