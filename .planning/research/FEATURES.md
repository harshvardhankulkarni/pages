# Feature Landscape

**Domain:** Zoho Creator internal business application for industrial flooring company
**Researched:** 2026-06-24

## Table Stakes

Features users expect. Missing = app feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Item Master with auto-fetch | Every Creator app needs master data | Low | Item Code ↔ Name, UOM auto-population |
| Supplier/Customer Master | Vendor/client management core to business | Low | Auto-generated codes, GST/PAN validation |
| Purchase Order with GST calc | Regulatory requirement for all Indian businesses | Medium | CGST/SGST/IGST split, total in words |
| GRN with stock update | Fundamental inventory operation | Medium | Partial GRN, posting workflow |
| Material Requisition & Issue | Production needs materials from store | Medium | Stock visibility at MR creation |
| Sales Order/Work Order | Revenue-generating transaction | Medium | Dual mode (Supply+Apply vs Supply-only) |
| Project with cost tracking | Project-based business model | High | 5 task buckets, budget vs actual |
| Auto-numbering on all docs | Business document standards | Low | PR, PO (RM/RMWAD), GRN, MR, MIS, QC, SO/WO |
| Role-based access | Multiple departments, data sensitivity | Medium | Form-level C/R/U/D, field-level restrictions |

## Differentiators

Features that add value beyond basic functionality.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| SO/WO dual mode (Supply+Apply / Supply) | Single form handles both business models | Medium | Conditional field visibility based on mode |
| Partial GRN with checkbox selection | Supports real-world partial deliveries | Low | Per-line-item checkbox before posting |
| Separate PO series (RMWAD/RM) | Stricter control for coding materials | Low | Different prefixes, access control by department |
| Execution mode on Project (Area/Day basis) | Matches Chemsol's variable project types | Medium | Different task structures per mode |
| QC with batch-level testing | Quality control for received materials | Medium | Viscosity, Density, Color, Moisture per batch |
| Project Dashboard with monthly costs | Real-time margin visibility | High | Labour, transport monthly breakdowns |
| Auto-fetch available stock on MR | Prevents over-requisitioning | Low | Real-time stock display during MR creation |

## Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Real-time inventory sync with external ERP | Out of scope — no external ERP integration | Stock updates only within Creator (GRN/MIS/FG Receiving) |
| Barcode/RFID scanning | Not in Chemsol requirements | Manual bin location tracking |
| Online payment gateway | B2B business — invoices/POs, no ecommerce | Track payment terms and credit days |
| Multi-currency support | India-only operations | All transactions in INR |

## Feature Dependencies

```
Item Master → BOM Master (BOM references items)
System Master → BOM Master (BOM references systems)
Supplier Master → Rate Comparison → PO → GRN (sequential)
Customer Master → SO/WO (customer reference)
BOM Master → Batch Manufacturing Record (consumption rates)
Item Master → MR → MIS → Stock (material flow)
SO/WO → Project (Supply+Apply links)
PR → Rate Comparison → PO (procurement chain)
GRN → QC (quality check after receipt)
```

## Suggested Build Order

1. **Master data first** — Items, Systems, Suppliers, Customers (all forms depend on these)
2. **Procurement** — PR → Rate Comparison → PO → GRN (sequential workflow)
3. **Sales** — SO/WO dual mode (revenue driver)
4. **QC** — QC/QA linked to GRN
5. **Store** — MR → MIS → Stock management
6. **Production** — Planning → BMR → Consumption
7. **Project Management** — Project → Tasks → Dashboard
8. **Reports & Dashboards** — All modules need reporting
