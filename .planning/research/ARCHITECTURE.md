# Architecture Patterns

**Domain:** Zoho Creator internal business application
**Researched:** 2026-06-24

## Recommended Architecture

### Module Structure

The application is organised into 8 module groups, each with its own forms, reports, and Deluge workflows.

```
┌─────────────────────────────────────────────────────┐
│                 CHEMSOL ZOHO CREATOR                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ADMIN      SALES     PURCHASE    STORE             │
│  ─────      ─────     ────────    ─────             │
│  Item       SO/WO     PR          GRN               │
│  System     Customer  Rate Comp   MR                │
│  BOM        Master    PO          MIS               │
│  Supplier             PO Amend    Mat Return        │
│  Customer             GRN         Mat Handover      │
│  Store                           FG Receiving       │
│  Bin Loc                         Vehicle/Transport  │
│  Access                          Stock Ledger       │
│                                                     │
│  PRODUCTION   QC       PROJECT      FINANCE         │
│  ──────────   ──       ───────      ───────         │
│  Prod Plan    QC/QA    Project      Payment         │
│  Prod Order   Master   Tasks        Tracking        │
│  BMR                   Machinery    Financials       │
│  RM Consump            Labour                       │
│  Packing                                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow Patterns

**Master → Transaction chain:**
- Item Master feeds PR, PO, MR, SO/WO line items
- Supplier Master feeds PO, Rate Comparison
- Customer Master feeds SO/WO
- System Master feeds SO/WO (Supply+Apply) and BOM

**Sequential workflow chain:**
- PR → Rate Comparison → PO → GRN → QC
- MR → MIS → Stock deduction
- SO/WO → Production Planning → BMR → RM Consumption → Packing → FG Receiving
- SO/WO (Supply+Apply) → Project → Tasks

### Key Architecture Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| GRN posting = stock update | Post action (not save) | Prevents accidental stock updates before verification |
| Partial GRN | Checkbox per line item | Supports real-world partial deliveries |
| PO series per RM Type | Separate RMWAD/RM prefixes | Coding materials need stricter control |
| SO/WO mode switch | Conditional field visibility | Single form handles both business models |
| Auto-fetch via lookup fields | Native Creator lookups | No custom Deluge needed for simple lookups |
| Approvals via native engine | Zoho Creator Approval | Built-in escalation, history, notifications |

## Patterns to Follow

### Pattern 1: Auto-Numbering
**What:** Auto-generate document numbers on form creation
**Implementation:** Deluge workflow on form Create event
**Format:** `{PREFIX}-{YEAR}-{SERIAL}` (e.g., PR-2026-001, PO-2026-001)

### Pattern 2: Auto-Fetch
**What:** Populate related fields when a key field changes
**Implementation:** Native Creator lookup fields (preferred) or Deluge on field change
**Examples:**
- Item Code → Item Name, UOM, HSN, GST%
- Supplier Code → Supplier Name, Address, GST
- PO Number → All GRN line items

### Pattern 3: Posting Workflow
**What:** Two-phase form — Draft (save) then Post (finalize)
**Implementation:** Status field ("Draft"/"Posted") + Deluge on status change
**Used by:** GRN (stock updates on Post, not Save)

### Pattern 4: Approval Chain
**What:** Sequential approval with limit-based escalation
**Implementation:** Zoho Creator Approval engine
**Limits:** PR ≤ ₹50K (Manager), > ₹50K (Director); PO ≤ ₹2L (Manager), > ₹2L (Director)

## Anti-Patterns to Avoid

### Anti-Pattern 1: Deeply nested subforms
**What:** More than 2 levels of subform nesting
**Why bad:** Creator performance degrades, UI becomes unusable on mobile
**Instead:** Flatten with separate linked forms where possible

### Anti-Pattern 2: Heavy calculations in form load
**What:** Complex Deluge workflows on form load
**Why bad:** Slow form rendering, poor UX, 5-minute timeout risk
**Instead:** Defer calculations to save/submit actions

### Anti-Pattern 3: Over-reliance on single Deluge function
**What:** One monolithic function handling all automation
**Why bad:** Hard to debug, no code reuse, exceeds size limits
**Instead:** Split into small focused functions per form/per action

## Scalability Considerations

| Concern | At 10 users | At 50 users | At 100+ users |
|---------|-------------|-------------|---------------|
| Form load time | Instant | <1 second with lookups | Consider report-only views |
| Report performance | Instant | <3 seconds | Pre-aggregated summary views |
| Deluge execution | <1 second | <30 seconds | Batch large operations, avoid loops >500 records |
| File attachments | Fine | 20MB limit per file | Consider Zoho Docs for large attachments |
