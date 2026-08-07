# Chemsol Implementation Progress Log

## 2026-08-06 — Client Change Round (82/82 green)

### Client Changes Incorporated

| # | Change | Spec Reference | Deluge Updated | Sim Tests |
|---|--------|----------------|----------------|-----------|
| 1 | **No SO Approval Process** — Costing Sheet auto-created directly from SO (Supply+Apply), Project still only at Costing approval | A-07, C2 | `expandCosting.deluge` (SO status removed) | P2: "No SO approval: Costing Sheet Draft auto-created from SO" |
| 2 | **Costing FG-based** — Section A lists FG products (Area × Qty/sqm), costed at BOM roll-up; NO RM rows in costing | A-09, A-15 | `expandCosting.deluge`, `mrDerive.deluge` | P2: "Costing Sec A FG-based: FG-002 150 kg / FG-003 300 kg", "2 FG lines (no RM rows in costing)" |
| 3 | **Production Planning FG-wise** — Plan lines are FG products; RM shortage for auto-PR derived via BOM roll-up | A-14 | `planReleaseAutoPR.deluge` | P2: "Plan FG-wise: 2 FG lines", "RM-001 shortage 75 kg -> auto-PR" |
| 4 | **MR Change History + Dept Notification** — Any MR change logs to `MR_Change_History` subform; emails Production & Inventory | New (client 2026-08-06) | `mrChangeHistory.deluge` (new) | P3: "MR Change History subform logged change", "MR Change notified Production & Inventory depts" |
| 5 | **Reports subform-focused** — Open PR report returns PR_Line_Items subform details | New (client 2026-08-06) | (Report query logic; no Deluge workflow change) | REP: "R4 subform report focus: Open PR report returns PR item subform details (RM-001, Qty 75)" |

### Canonical Numbers Preserved (all downstream stays green)

- SO Total: **₹175,000** (500 sqm × ₹350, EP02)
- Costing Section A: **₹103,000** (FG-002 150 kg @ ₹310 = ₹46,500; FG-003 300 kg @ ₹188.33 = ₹56,500)
- Costing Sheet Total: **₹146,000** (Sec A+B+C+D+E = 103k+30k+7.5k+3.5k+2k)
- MR 4 Components: **₹144,000** (Material 103k + Application 30k + Transport 7.5k + Tools 3.5k; Sec E excluded)
- Allocation: **RM-001 275 kg (68.75%), RM-002 125 kg (31.25%)**
- P&L: **+₹31,000** (175k - 144k)

### Files Changed

```
chemsol/implementation/deluge/costing/expandCosting.deluge      ← FG-based costing
chemsol/implementation/deluge/costing/planReleaseAutoPR.deluge  ← FG-wise plan auto-PR
chemsol/implementation/deluge/mrGate/mrDerive.deluge            ← MR derives RM from FG costing
chemsol/implementation/deluge/mrGate/mrChangeHistory.deluge     ← NEW: MR change history + notify
chemsol/implementation/verify/flow_sim.py                       ← All 5 changes mirrored (82/82)
```

### Verification

```bash
python chemsol/implementation/verify/flow_sim.py
# Result: 82 passed, 0 failed
```

### Next Steps

1. Push to GitHub Pages (main branch auto-deploys)
2. Send change summary to Medha Desawale via Cliq
3. Medha replicates in Zoho Creator console
4. Client UAT meeting with updated data-flow documentation

---

## Verify pass (2026-08-07) — Chemsol V2 .ds edits mirrored in flow_sim

Ran `python verify/flow_sim.py` after applying the V2 .ds changes. Result: **82 passed, 0 failed** (exit 0). Verdict per AGENTS.md loop discipline for each change made this session:

| Change | Sim mirror | Green? |
|--------|-----------|--------|
| Autonumber prefixes now `-YYYY-` (12 series: SO, PRJ, PR, GRN, QC, MR, Cost, BOM, Comp, CUST, PLAN, JOB) | `number_series(prefix, year)` already returns `{prefix}-{year}-{seq:04d}` → matches | ✅ |
| A8 MIS issue → RM ledger (`MIS_Issued`+, `Closing_Stock`−) + log OUT | `post_mis` + `stock_move` + "Post MIS: 2 movement log OUT entries" | ✅ |
| A11 GRN → RM ledger (`GRN_Received`+, `Closing_Stock`+) + log IN | `post_grn` + `stock_move` + "stock movement log IN entry exists (qty 75)" | ✅ |
| A15 Material Return → RM ledger (`Returns`+, `Closing_Stock`+) + log IN | `material_return` + "MRT: Good condition restores stock → RM-001 10 / RM-002 285" | ✅ |
| Ghost `MR_Line_Items` grid removed | sim has zero references to it (never used) | ✅ |
| New forms `User_Access`, `Approval_Matrix`; `Prepared_By`/`Reviewed_By`; Costing `Project_ID` text→lookup; `MR_Status` | pure schema — no business logic to mirror | ✅ |

Note: AGENTS.md says "72/72" but the harness has grown to **82 assertions**; 82 is the authoritative count now.