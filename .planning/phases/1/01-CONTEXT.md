# Phase 1: Master Data & Admin - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers 8 master data forms plus 2 cross-cutting automations (auto-numbering, auto-fetch lookups):

1. **Item Master** — Central RM/PM/FG/consumables repository
2. **System Master** — Flooring system definitions (Epoxy, PU, Demarcation, etc.)
3. **BOM Master** — Material consumption per system
4. **Supplier Master** — Vendor/supplier details for procurement
5. **Customer Master** — Customer/site details
6. **Store Master** — Physical store location definitions (RM/FG/QC/Site)
7. **Bin Location Master** — Rack-shelf-bin mapping within stores
8. **User Access & Approval Matrix** — Roles, departments, PR/PO approval limits

These forms have no upstream dependencies and are prerequisites for all subsequent phases (Sales, Purchase, Production, Project Management).

**In scope:** Form creation, field definitions, auto-numbering, auto-fetch lookups, form-level permission mapping, validation rules, report generation per form.
**Out of scope:** Workflow automations beyond basic field behavior (deferred to later phases), integration with external systems, multi-level BOMs, custom search UIs.

</domain>

<decisions>
## Implementation Decisions

### Item Code Auto-Generation
- **D-01:** Item Code format: `{CategoryPrefix}-{3-digit sequential}` (e.g., RM-001, PM-001, FG-001). Category-prefixed for instant visual identification of item type.
- **D-02:** Item categories (fixed dropdown): RM (Raw Material), PM (Packing Material), FG (Finished Good), CON (Consumable), SVC (Service).

### System Code Auto-Generation
- **D-03:** System Code format: `{Prefix}-{3-digit sequential}` (e.g., EP-001, PU-001, DEM-001). Prefixes per BRD: EP, PU, DEM, NUM, ARR, ANTI, ESD, FIL, COV.
- **D-04:** System name is user-entered, not derived from code. Thickness is a free-text field (e.g., "3mm", "4mm", "100 micron").

### BOM Master Design
- **D-05:** Single-level BOM (one System -> multiple RM/PM items). Chemsol flooring systems are pre-mixed formulations, not multi-stage assemblies.
- **D-06:** BOM is a subform on System Master (or a linked form with System Code as parent). Quantity field is decimal — per unit of the system UOM.
- **D-07:** UOM auto-fetches from Item Master on item selection. Item Code triggers Item Name + UOM auto-fetch.

### Supplier & Customer Codes
- **D-08:** Supplier Code format: `SUP-{3-digit sequential}`.
- **D-09:** Customer Code format: `CUS-{3-digit sequential}`.

### Store & Bin Location
- **D-10:** Store Type is a fixed dropdown: RM, FG, QC, Site (as specified in BRD). Not configurable.
- **D-11:** Bin Location uses fixed 3-level hierarchy: Rack -> Shelf -> Bin (as specified in BRD). Each is a text field.

### UOM List (Standard for All Forms)
- **D-12:** UOM dropdown values: Sq.Ft, Sq.Mtr, Kg, Litre, Nos, Meter, Roll, Packet, Bag, Drum, Set, Hour, Day.

### User Access & Approval Matrix
- **D-13:** Use Zoho Creator's built-in profile system for form-level CRUD permissions. Department + Role are custom fields (dropdowns) for reporting and workflow targeting.
- **D-14:** PR Approval Limit and PO Approval Limit are Currency fields on the User Access form. Admin sets limits per user. Deluge workflow in later phases will check these limits on PR/PO submission.

### Report Generation
- **D-15:** Every form gets a standard list report with filters (Zoho Creator's default report builder). Item Master gets a full listing report as specified.

### Form Behavior Patterns
- **D-16:** All auto-generated codes use Zoho Creator's auto-number field type with custom format strings.
- **D-17:** All auto-fetch fields (Item Name from Item Code, UOM from Item Code, System Name from System Code) use Zoho Creator's "Lookup" field behavior with cascading select / on-load fetch.
- **D-18:** Today's Date fields use Zoho Creator's "Default Value = Current Date/Time" setting.

### Claude's Discretion
- Field ordering within forms (follow logical grouping, not strictly left-to-right from BRD tables).
- Form layout (single-section vs. section-grouped). Standard approach: single section for <10 fields, grouped sections for 10+ fields.
- Report layout and filter columns.
- Validation rule implementation (field-level via Creator's built-in validation vs. Deluge). Standard: use built-in validation where possible, Deluge only when business logic requires it.

### Folded Todos
Nobody found to fold.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Business Requirements
- `BRD.md §3.1.1` — Item Master field spec (Category, Code, Name, UOM, HSN, GST, Min/Max Stock, Standard Rate, Preferred Supplier, Lead Time)
- `BRD.md §3.1.2` — System Master field spec (System Code, Name, Thickness, Description, UOM) + prefix table
- `BRD.md §3.1.3` — BOM Master field spec (System Code/Name, Item Code/Name, Quantity, UOM)
- `BRD.md §3.1.4` — Supplier Master field spec (13 fields including GSTIN, PAN, Bank details, Payment Terms, Credit Days)
- `BRD.md §3.1.5` — Customer Master field spec (11 fields including GST, PAN, addresses)
- `BRD.md §3.1.6` — Store Master field spec (Store Code/Name/Type/Location)
- `BRD.md §3.1.7` — Bin Location Master field spec (Store Name, Rack/Shelf/Bin No)
- `BRD.md §3.1.8` — User Access field spec (User Name, Department, Role, PR/PO Approval Limits)

### User Roles & Permissions
- `USER-ROLES.md §2.1` — Admin form-level permissions matrix (all 8 forms × all 13 roles)

### Architecture
- `ARCHITECTURE.md §4` — Deluge automation patterns (auto-numbering, auto-fetch, validation)
- `ARCHITECTURE.md §3` — Data model: master data on Zoho Creator, relational via lookup fields
- `ARCHITECTURE.md §2.3` — India datacenter .in domain for Zoho API calls

### Requirements
- `REQUIREMENTS.md` requirements mapped to Phase 1: ADM-01 through ADM-08, AUT-01, AUT-02

### Client Specification (Source of Truth)
- `Creator Forms Screen.xlsx` — Admin sheets for full field-level spec including dropdown options, field annotations, subform indicators

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
None — Phase 1 is greenfield (first phase, no prior code).

### Established Patterns
No established patterns yet — this phase will set the conventions for all subsequent phases.

### Integration Points
- Item Master is referenced by BOM Master (lookup), PR/PO (line items), MR/MIS (material issue), GRN (receiving), BMR (consumption).
- System Master is referenced by BOM Master, Sales/Work Order, Project tasks.
- Supplier Master is referenced by PR, Rate Comparison, PO.
- Customer Master is referenced by SO/WO, Project.
- Store Master and Bin Location are referenced by Stock, Material movement forms.

</code_context>

<specifics>
## Specific Ideas

- Item Master should have a "Category of Purchase Item" dropdown that drives the auto-number prefix (e.g., selecting "RM" generates "RM-001").
- System Master's "UOM" is distinct from Item UOM — systems use Sq.Ft / Sq.Mtr (area-based), items use Kg / Litre / Nos (consumption-based). BOM bridges the two.
- Supplier Master's "Payment Terms" should be a dropdown (not free text) for consistency in PO workflow. Options: Advance, 7 Days, 15 Days, 30 Days, 45 Days, 60 Days, On Delivery.
- Customer Master should have separate address fields per BRD (Regd, Billing, Shipping) — all multi-line.
- Approval Matrix is embedded in User Access form (not a separate form) — PR and PO limits are fields on the user record.
- User Access form's Department and Role dropdowns must match the values in `USER-ROLES.md §1`.
- All master data forms should have: Created By, Created Date, Modified By, Modified Date via Zoho Creator's standard audit fields.

</specifics>

<deferred>
## Deferred Ideas

- Multi-level BOM (for future if Chemsol needs sub-assemblies) — not needed now.
- Item Master barcode/QR code integration — not in scope.
- Supplier portal (self-service) — future enhancement.
- Approval workflow Deluge logic (read approval limits during PR/PO submission) — belongs in Phase 2/3 when PR and PO forms are built.
- Inter-form Deluge validations (e.g., "Can't delete item referenced in BOM") — deferred to Phase 2/3 when BOM has downstream consumers.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Master Data & Admin*
*Context gathered: 2026-06-26*
