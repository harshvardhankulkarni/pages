# Chemsol — Zoho Creator ERP (Root AGENTS.md)

## What this repo holds

Planning documents and interactive HTML mockups for a Zoho Creator ERP system at **Chemsol** (flooring/construction materials). The main project is `chemsol/`. Separate projects live in `AdaniConneX/` (ZohoCRM) and `budget-tracking-handoff/`.

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

## Key architecture facts

- **MR is auto-derived from Costing Sheet** — zero manual re-entry. Standalone Costing Sheet module added before MR.
- **MR is the critical approval gate** — no MIS, production, or execution without MR Released
- **SO↔BOM↔MR cross-validation**: quantity mismatch >5% flags, >10% blocks
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

Task consumption tracked hourly/daily by area within each project via Site Consumption Entry form.

## What's NOT production code

- `chemsol/*.html` files (forms.html, flow.html, etc.) — interactive prototypes/mockups
- `zoho-ai-service/` — Phase 2 Python/FastAPI microservice (forecasting, anomaly detection); not connected yet
- Actual implementation happens in **Zoho Creator console** (.in instance), not in this repo
