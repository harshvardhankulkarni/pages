# Domain Pitfalls

**Domain:** Zoho Creator / Deluge business application development
**Researched:** 2026-06-24

## Critical Pitfalls

### Pitfall 1: Deluge timeout on large datasets
**What goes wrong:** Workflow that loops over hundreds of records exceeds 5-minute timeout
**Why it happens:** Deluge has a hard 5-minute execution limit per function call
**Consequences:** Partial data processing, silent failures, data inconsistency
**Prevention:** Batch operations (max 100 records per call), use `while` loops with `break`, avoid iterating all records in one function
**Detection:** Workflow fails silently; check audit logs for incomplete runs

### Pitfall 2: Lookup field performance degradation
**What goes wrong:** Forms with many cross-module lookups become slow to load
**Why it happens:** Each lookup fetches related records on form open
**Consequences:** 5-10 second form load times, poor mobile UX
**Prevention:** Limit lookups to essential fields only; use Deluge `zoho.creator.getRecords` on-demand instead of always-on lookups
**Detection:** Form load time >3 seconds

### Pitfall 3: Silent stock inconsistencies
**What goes wrong:** Stock balance drifts over time due to missing transactions
**Why it happens:** Stock updates are triggered by individual Deluge workflows that may fail silently
**Consequences:** Negative stock, incorrect reorder triggers, production delays
**Prevention:** Always use transaction-style updates (check before deduct, log failures), run periodic reconciliation reports (physical count vs system)
**Detection:** Stock ledger report with negative quantities

## Moderate Pitfalls

### Pitfall 1: Approval workflow deadlocks
**What goes wrong:** PR/PO stuck in approval because approver is on leave
**Prevention:** Configure alternate approvers and escalation timeouts in Creator Approval engine

### Pitfall 2: Partial GRN data entry errors
**What goes wrong:** User checks wrong items in partial GRN, causing incorrect stock updates
**Prevention:** Clear checkbox selection UX, confirm before posting, allow GRN reversal (with audit trail)

### Pitfall 3: Auto-number conflicts after data import
**What goes wrong:** Manual data import creates records with IDs that conflict with auto-numbering
**Prevention:** Set auto-number start after import range, or use separate number series for imported records

## Minor Pitfalls

### Pitfall 1: Field label changes break lookup references
**What goes wrong:** Renaming a form field breaks auto-fetch workflows
**Prevention:** Use API names (never display names) in Deluge code; document field API names

### Pitfall 2: Multi-user concurrent edits
**What goes wrong:** Two users edit same PO simultaneously, last save wins
**Prevention:** Use Creator's built-in optimistic locking; add "Locked for editing" status field

### Pitfall 3: Duplicate supplier/customer entries
**What goes wrong:** Same supplier entered twice with different codes
**Prevention:** GSTIN/PAN uniqueness check on create; search-before-create UX pattern

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Master Data forms | Lookup field performance with 500+ items | Limit lookups, use search-browse pattern |
| PO with GST calc | Incorrect CGST/SGST/IGST split based on supplier state | Hardcode split formula verified with CA |
| GRN + Stock update | Posting failure leaves stock inconsistent | Add audit log entry before stock update |
| Project Dashboard | Monthly cost aggregation slow with 50+ projects | Pre-aggregate at month-end via scheduled Deluge |
| Deluge (all forms) | Timeout on bulk operations | Loop limits, batch size ≤100 |
