# Chemsol — Zoho Creator Application

Client: **Chemsol** (industrial flooring solutions — epoxy, PU, anti-static, ESD).

ITOTCloud builds and maintains this Zoho Creator app. All business requirements are defined in `Creator Forms Screen.xlsx`.

## Source of truth

- **`Creator Forms Screen.xlsx`** (project root) — Chemsol's requirement specification in form/screen format. Read this first before any implementation. Sheets cover:
  - `Integrations` — module relationships, departments, system code formats (EP, PU, DEM, ANTI, ESD, etc.)
  - `Screens` — full screen inventory by department (Admin, Purchase, Store, Production, Project)
  - `Project` — project management dashboard & entry screens
  - `Sheet2` — Create Project form, task structure (Transport, Application/Execution, Manpower, Tools, Additional Expenses)
  - `Sales Order Master` — SO/WO with Suppy+Apply / Suppy-only modes, system codes, payment terms
  - `Purchase Item Muster`, `Supplier Master`, `PR`, `PO`, `GRN` — procurement forms
  - `QC & QA`, `MR`, `MIS`, `Rate Comparison`, `Production Report`

## Architecture

- **Platform**: Zoho Creator (no local dev — build in Creator's UI)
- **Language**: Deluge scripts for workflows, functions, automation
- **Module scope**: Admin, Purchase, Store, Production, QC, Sales, Project Management, Finance
- **System codes** per product type: EP (epoxy), PU (polyurethane), DEM (demarcation), ARR (arrow marking), ANTI (anti-static), ESD (ESD), FIL (filling), COV (coving), NUM (numbering)
- **Execution modes**: Area-basis or Day-basis (set on Project)

## Key forms & flows

| Form | Department | Notes |
|------|-----------|-------|
| Item Master | Purchase/Store | All RM, PM, FG, consumables |
| System Master | Sales/Projects | 3mm Epoxy, 4mm PU, Demarcation, etc. |
| BOM Master | Production/QC | Material consumption per system |
| Sales/Work Order | Sales | Dual mode: Supply+Apply / Supply-only |
| PR → Rate Comparison → PO → GRN | Purchase | Sequential procurement flow |
| MR → MIS | Production/Store | Material requisition & issue |
| Batch Manufacturing Record | Production | RM/PM consumption tracking |
| Project | Project Mgmt | 5 task buckets: Transport, Application, Manpower, Tools, Additional Expenses |

## Deluge & Zoho Creator conventions

- **Datacenter**: India (`.in` domain for Zoho APIs)
- **Auto-numbering**: PR, PO (separate series for coding vs non-coding: `RMWAD` vs `RM`), GRN, MR, MIS, QC numbers are auto-generated
- **Field auto-fetch**: Item Code ↔ Item Name, UOM by item, supplier details on PO, stock on MR
- **GRN logic**: Partial GRN allowed (checkbox selection), stock updated post-GRN posting, transport subform visible if transport in PO scope
- **QC status**: On GRN items — Viscosity, Density, Color, Moisture results per batch
- **OAuth**: Zoho Creator handles auth natively; use `zoho.creator.getRecords`, `zoho.creator.createRecord`, etc. with connection parameters
- **All forms** follow: entry → search/review → edit → report generation pattern per department

## Reference: other repos

- `zoho-integration/` — Deluge scripts for CRM↔Books and Projects↔CRM sync patterns
- `zoho-essl/` — Zoho Catalyst job functions for biometric sync to Zoho People

## How to ask `@itot`

For architecture decisions, Deluge patterns, or understanding Chemsol business logic:
`@itot explain the procurement flow from PR to GRN for this Creator app`

## Working with the Excel spec

- `Creator Forms Screen.xlsx` is the contract — implement forms and fields as specified
- `*` prefix on fields = required/mandatory
- `Auto Fetch`, `Autogenerate`, `Today's Date` annotations specify field behavior
- Dropdown options are listed inline (e.g. Project Type: Industrial, Commercial)
- Subforms are indicated by indentation or numbered task lists

## GSD Workflow

This project uses GSD (Get Stuff Done) for structured planning and execution.

- `.planning/PROJECT.md` — project context and requirements
- `.planning/config.json` — workflow preferences (yolo mode, sequential execution)
- `.planning/research/` — domain research and architecture decisions
- `.planning/REQUIREMENTS.md` — 70 v1 requirements with REQ-IDs
- `.planning/ROADMAP.md` — 8-phase execution roadmap
- `.planning/STATE.md` — current project state

### GSD Commands

| Command | When to Use |
|---------|-------------|
| `/gsd-progress` | Check current phase status and what to do next |
| `/gsd-plan-phase 1` | Plan Phase 1 (Master Data & Admin) |
| `/gsd-execute-phase` | Execute the current phase's plans |
| `/gsd-verify-work` | Verify phase deliverables against requirements |
| `/gsd-transition` | Move to next phase after successful verification |

### Current Phase

Phase 1: Master Data & Admin — Build Item, System, BOM, Supplier, Customer, Store, Bin Location, User Access forms.
