# Chemsol — Zoho Creator Application

## What This Is

A Zoho Creator application for **Chemsol**, an industrial flooring solutions company (epoxy, PU, anti-static, ESD). The app digitises operations across Admin, Purchase, Store, Production, Sales, Project Management, and Quality Control — replacing manual/offline tracking with a centralised system. ITOTCloud Systems Pvt. Ltd. builds and maintains the app.

## Core Value

Chemsol's entire business operations — procurement, inventory, production, sales, project execution, and quality assurance — run through a single, accurate Zoho Creator system that replaces manual tracking and eliminates data silos between departments.

## Requirements

### Validated

- ✓ Business requirements documented in `Creator Forms Screen.xlsx` — 15+ forms across 8 departments — from client
- ✓ BRD: Module-by-module spec covering all forms, fields, business rules, system codes (EP, PU, DEM, ANTI, ESD, etc.)
- ✓ Process flows: PR→PO→GRN, MR→MIS, SO/WO, Production, Project Execution, Inventory, QC
- ✓ User roles & permissions matrix: 13 roles × form-level C/R/U/D permissions, field-level restrictions
- ✓ Architecture doc: Platform (Zoho Creator + Deluge), India datacenter, auto-numbering, auto-fetch, stock update workflows
- ✓ Test cases: 150+ TC-IDs across all modules with expected results

### Active

- [ ] **ADM-01**: Item Master form — all RM, PM, FG, consumables with auto-fetch
- [ ] **ADM-02**: System Master — flooring systems (3mm Epoxy, 4mm PU, Demarcation) with system codes
- [ ] **ADM-03**: BOM Master — material consumption per system/product
- [ ] **ADM-04**: Supplier Master — vendor details with auto-generated codes
- [ ] **ADM-05**: Customer Master — customer/site details
- [ ] **ADM-06**: Store Master — RM/FG/QC/Site store definitions
- [ ] **ADM-07**: Bin Location Master — rack/shelf/bin mapping
- [ ] **ADM-08**: User Access & Approval Matrix
- [ ] **SAL-01**: Sales/Work Order — Supply+Apply and Supply-only dual-mode form
- [ ] **PUR-01**: Purchase Requisition (PR) with auto-fetch line items
- [ ] **PUR-02**: Rate Comparison against PR
- [ ] **PUR-03**: Purchase Order (PO) — dual series (RMWAD/RM), GST calc, printable
- [ ] **PUR-04**: PO Amendment workflow
- [ ] **PUR-05**: Goods Receipt Note (GRN) — partial GRN, stock update on post, transport subform
- [ ] **QC-01**: QC/QA Master — Viscosity, Density, Color, Moisture per batch
- [ ] **STO-01**: Material Requisition (MR) with stock availability display
- [ ] **STO-02**: Material Issue Slip (MIS) — stock deduction on issue
- [ ] **STO-03**: Material Return, Material Handover, FG Receiving, Vehicle & Transport
- [ ] **PROD-01**: Production Planning form
- [ ] **PROD-02**: Production Order & Batch Manufacturing Record (BMR)
- [ ] **PROD-03**: RM Consumption Entry & Packing Entry
- [ ] **PRJ-01**: Create/Edit Project with 5 task buckets (Transport, Application, Manpower, Tools, Expenses)
- [ ] **PRJ-02**: Project Dashboard with margin tracking, monthly costs, execution vs targets
- [ ] **RPT-01**: Department-wise reports (Purchase, Store, Production, Project, QC)
- [ ] **INT-01**: Deluge workflows — auto-numbering, auto-fetch, calculations, stock updates
- [ ] **INT-02**: Approvals — PR, Rate Comparison, PO, MR approval chains
- [ ] **SEC-01**: Role-based form/field/report permissions per matrix

### Out of Scope

- Payroll processing — not part of Creator app scope
- Fixed asset management — not in Chemsol's requirements
- HR/employee lifecycle management — handled externally
- External Zoho integrations (CRM, Books, People) — future phase

## Context

- **Client**: Chemsol — industrial flooring (epoxy, PU, anti-static, ESD, demarcation, coving)
- **Developer**: ITOTCloud Systems Pvt. Ltd. — Zoho Premium Partner & Creator Partner
- **Platform**: Zoho Creator (low-code/no-code, India datacenter `.in`)
- **Automation language**: Deluge (Zoho proprietary scripting)
- **Existing assets**: Business requirement spec (`Creator Forms Screen.xlsx`), full BRD, architecture doc, process flows, user roles matrix, test cases
- **Departments using the app**: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1, Project Manager 2
- **System codes**: EP (Epoxy), PU (Polyurethane), DEM (Demarcation), ARR (Arrow), ANTI (Anti-static), ESD (ESD), FIL (Filling), COV (Coving), NUM (Numbering)

## Constraints

- **Platform**: Zoho Creator only — no custom backend, no external hosting
- **Language**: Deluge only — no Python/Node.js server-side code
- **Datacenter**: India (`.in`) — all API calls use `creator.zoho.in`
- **Mobile**: Must work on Zoho Creator mobile app (iOS/Android)
- **Approvals**: Must use Zoho Creator's native approval engine
- **Field behavior**: `*` = mandatory, `Auto Fetch`/`Autogenerate`/`Today's Date` annotations per spec

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Zoho Creator over custom dev | Faster delivery, built-in mobile, lower TCO | ✓ Good |
| India datacenter (.in) | Client is India-based | ✓ Good |
| Separate PO series (RM / RMWAD) | Coding materials require stricter purchase control | — Pending |
| GRN posting = stock update (not save) | Prevents accidental stock updates | — Pending |
| Partial GRN via checkbox per line | Supports real-world partial deliveries | — Pending |
| Execution mode on Project (Area / Day) | Matches Chemsol's variable project types | — Pending |
| SO/WO dual mode | Different business models with different field sets | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-24 after initialization*
