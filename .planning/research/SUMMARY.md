# Research Summary: Chemsol — Zoho Creator Application

**Domain:** Zoho Creator internal business application for industrial flooring company
**Researched:** 2026-06-24
**Overall confidence:** HIGH

## Executive Summary

Chemsol requires a Zoho Creator application digitising 8 departments with 15+ forms covering procurement, sales, production, project management, inventory, and quality control. The platform is Zoho Creator (low-code) with Deluge for automation — India datacenter.

The build order follows a clear dependency chain: master data first, then transactional workflows (procurement → sales → store → production → projects), with reports wrapping each module. The chief risks are Deluge timeout on bulk operations, lookup performance with large datasets, and silent stock inconsistencies from partial workflow failures. These are well-understood and can be mitigated with batch limits, careful lookup design, and transaction-style stock updates.

## Key Findings

**Stack:** Zoho Creator + Deluge — the only viable platform given client requirements. No alternative tech stack was seriously considered (Creator is the mandate).

**Architecture:** 8 module groups with sequential workflow chains (PR→PO→GRN, MR→MIS, SO→Production→FG). Key patterns: auto-numbering, auto-fetch via lookups, posting workflow for stock updates, native approval engine with limit-based escalation.

**Critical pitfall:** Deluge 5-minute timeout on workflows that iterate large datasets. Mitigate with batch processing and per-call limits.

**Table stakes:** Item Master, Supplier/Customer Masters, Purchase Order with GST, GRN with stock update, MR/MIS, SO/WO, Project with cost tracking, auto-numbering on all forms, role-based access.

**Differentiators:** SO/WO dual-mode (Supply+Apply / Supply-only), partial GRN, separate PO series for coding materials, Area/Day execution modes on projects, QC with batch-level testing, project dashboard with monthly costs.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Master Data & Admin** — Item, System, BOM, Supplier, Customer, Store masters. All other phases depend on these.
2. **Sales Order/Work Order** — Core revenue transaction. Establishes customer-facing workflow.
3. **Procurement (PR→PO→GRN)** — Sequential purchase chain. PR, Rate Comparison, PO, GRN with stock update.
4. **Quality Control** — QC linked to GRN. Viscosity, Density, Color, Moisture testing per batch.
5. **Store & Inventory** — MR, MIS, Material Return, Handover, FG Receiving. Stock management.
6. **Production** — Planning, Production Order, BMR, RM Consumption, Packing Entry.
7. **Project Management** — Project creation, 5 task buckets, dashboard with monthly costs.
8. **Reports, Dashboards & Permissions** — Wrap all modules with reporting, role-based access, final integration testing.

**Phase ordering rationale:** Master data before transactions. Procurement before store (items exist first). Sales early (revenue driver). QC after GRN (natural dependency). Production after materials available. Projects last (depends on everything else).

**Research flags for phases:**
- Phase 3 (Procurement): Complex GST calculations need careful Deluge implementation
- Phase 7 (Projects): Dashboard aggregation may need performance optimisation
- Phase 8 (Reports): Various report types (summary, pivot, printable) each need different approaches

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Zoho Creator mandate — no alternatives needed |
| Features | HIGH | All features from validated client requirements (Excel spec) |
| Architecture | HIGH | Well-understood Creator patterns with clear dependency chains |
| Pitfalls | MEDIUM | While standard pitfalls documented, actual performance depends on data volume |

## Gaps to Address

- Exact GST calculation logic (CGST/SGST split) depends on supplier GST state — needs domain expert input during Phase 3
- Project dashboard query complexity depends on eventual data model — may need pre-aggregation strategy in Phase 7
- User capacity planning (how many concurrent users per dept) affects form/report performance tuning
