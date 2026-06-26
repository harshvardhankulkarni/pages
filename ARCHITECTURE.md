# Architecture Document — Chemsol Zoho Creator Application

---

## 1. Platform Overview

| Component | Technology |
|-----------|-----------|
| Application Platform | Zoho Creator (Low-code / No-code) |
| Automation Language | Deluge (Zoho proprietary scripting) |
| Database | Zoho Creator's built-in database (PostgreSQL-based) |
| Authentication | Zoho Creator native auth (OAuth-based) |
| Domain | India datacenter (`.in`) — all API calls use `https://creator.zoho.in` |
| Mobile Access | Zoho Creator mobile app (iOS / Android) |
| File Storage | Zoho Creator file attachment field (stored in Zoho cloud) |

---

## 2. Module Architecture

The application is organised into **8 module groups**, each with its own forms, reports, and workflows.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHEMSOL ZOHO CREATOR APP                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  ADMIN  │  │  SALES   │  │ PURCHASE │  │   STORE & LOG    │    │
│  │         │  │          │  │          │  │                  │    │
│  │ Item    │  │ SO/WO    │  │ PR       │  │ GRN              │    │
│  │ System  │  │ Customer │  │ Rate     │  │ MR               │    │
│  │ BOM     │  │ Master   │  │ PO       │  │ MIS              │    │
│  │ Supplier│  │          │  │ PO Amend │  │ Mat Return       │    │
│  │ Customer│  │          │  │ GRN      │  │ Mat Handover     │    │
│  │ Store   │  │          │  │          │  │ FG Receiving     │    │
│  │ Bin Loc │  │          │  │          │  │ Vehicle/Transport │    │
│  │ Access  │  │          │  │          │  │ Stock Ledger     │    │
│  └─────────┘  └──────────┘  └──────────┘  └──────────────────┘    │
│                                                                     │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ PRODUCTION │  │    QC    │  │ PROJECT  │  │   FINANCE    │    │
│  │            │  │          │  │          │  │              │    │
│  │ Prod Plan  │  │ QC/QA    │  │ Project  │  │ Payment      │    │
│  │ Prod Order │  │ Master   │  │ Tasks    │  │ Tracking     │    │
│  │ BMR        │  │          │  │ Machinery│  │ Customer/    │    │
│  │ RM Consump │  │          │  │ Labour   │  │ Supplier     │    │
│  │ Packing    │  │          │  │          │  │ Financials   │    │
│  └────────────┘  └──────────┘  └──────────┘  └──────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     REPORTS LAYER                           │   │
│  │  Purchase │ Store │ Production │ QC │ Sales │ Project      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model Relationships

### 3.1 Master Data (Admin Layer)

```
Item Master ◄───── BOM Master ────► System Master
     │                                      │
     ├── Supplier Master                     │
     ├── Customer Master                     │
     └── Store Master ──► Bin Location       │
                                             │
Supplier Master ◄────────────────────────────┘
Customer Master
```

### 3.2 Transactional Data Flows

```
PR ──► Rate Comparison ──► PO ──► GRN ──► QC
                                        │
                                        └──► Stock Ledger
                                                   │
System Master ──► SO/WO ──► Project ──► Tasks
                                        │
                                        └──► MR ──► MIS ──► Stock Ledger
                                                  │
BOM Master ──► Production Order ──► BMR ──► RM Consumption
                                                  │
                                                  ├── Packing Entry ──► FG Receiving
                                                  └── Stock Ledger
```

---

## 4. Deluge Automation Layer

### 4.1 Auto-Numbering Workflows

| Form | Pattern | Logic |
|------|---------|-------|
| PR | `PR-{year}-{serial}` | On Create |
| PO (Non-coding) | `RM-{year}-{serial}` | On Create, based on RM Type = "Non Coding" |
| PO (Coding) | `RMWAD-{year}-{serial}` | On Create, based on RM Type = "Coding" |
| GRN | `GRN-{year}-{serial}` | On Post (not on Create) |
| MR | `MR-{year}-{serial}` | On Create |
| MIS | `MIS-{serial}` | On Create, linked to MR |
| QC | `QC-{year}-{serial}` | On Create |
| SO | `SO-{year}-{serial}` | On Create (Supply mode) |
| WO | `WO-{year}-{serial}` | On Create (Supply+Apply mode) |

### 4.2 Auto-Fetch Workflows

| Context | Trigger | Source | Target Fields |
|---------|---------|--------|--------------|
| PR Line Item | On Item Code/Name entry | Item Master | Item Name/Code, UOM, Lead Time |
| PO Header | On Supplier Code entry | Supplier Master | Supplier Name, GST, Address, Bank |
| PO Line Item | On Item Code entry | Item Master | Item Name, HSN, UOM, GST% |
| GRN Line Items | On PO Number selection | PO Master | All line items, quantities |
| GRN Supplier | On PO Number selection | PO Master | Supplier Code, Supplier Name |
| QC Header | On GRN Number selection | GRN Master | Supplier Name |
| MR Line Item | On Item Code entry | Item Master | Item Name, Category, UOM, Available Stock |
| SO/WO Header | On Customer Code | Customer Master | Client Org Name, Contact, GST, Address |
| SO/WO System | On System Code selection | System Master | System Name, Thickness, UOM |

### 4.3 Calculation Workflows

| Form | Calculation | Trigger |
|------|------------|---------|
| PO Line Item | Basic Amount = Qty × Rate | On Qty/Rate change |
| PO Line Item | GST Amount = Basic Amount × GST% / 100 | On Basic Amount change |
| PO Line Item | Total Amount = Basic Amount + GST Amount | On change |
| PO Footer | Sum of all line item totals | On any line item change |
| SO/WO Line Item | Amount = Area × Rate | On Area/Rate change |
| SO/WO Footer | Total Amount, Commission calculation | On line item change |

### 4.4 Stock Update Workflows

| Event | Action | Direction |
|-------|--------|-----------|
| GRN Posted | Add Received Qty to Warehouse stock | Stock In |
| MIS Posted | Deduct Issued Qty from RM store | Stock Out |
| FG Receiving Posted | Add FG Qty to FG store | Stock In |
| Material Return Posted | Add returned Qty back to RM store | Stock In |
| Material Handover Posted | Deduct from source, Add to destination | Transfer |

### 4.5 Approval Workflows

| Form | Flow | Method |
|------|------|--------|
| PR | Creator → Purchase Manager → (if > limit) Director | Zoho Creator Approval |
| Rate Comparison | Purchase Executive → Purchase Manager | Zoho Creator Approval |
| PO | Purchase Executive → Purchase Manager → (if > limit) Director | Zoho Creator Approval |
| MR | Production Executive → Production Manager | Zoho Creator Approval |
| GRN | Auto-post (no approval) | Direct |
| QC | QC Inspector → Auto (notification to Production) | Notification only |

---

## 5. Integration Points

### 5.1 Internal Integrations (Within Creator)

| Source Form | Target Form | Data Shared | Mechanism |
|-------------|-------------|-------------|-----------|
| SO/WO | Project | Project details, Systems | Deluge workflow on SO/WO create |
| PO | GRN | PO line items, supplier | Deluge lookup field |
| PR | Rate Comparison | PR items, quantities | Deluge lookup field |
| MR | MIS | MR items, quantities | Deluge lookup field |
| GRN | QC | Items, quantities, supplier | Deluge workflow on GRN post |
| BOM | BMR | BOM items, consumption rates | Deluge lookup field |

### 5.2 External Integrations (Future Scope)

| Integration | Purpose | Method |
|-------------|---------|--------|
| Zoho Books | Accounting, invoicing | Zoho CRM/Books connector |
| Zoho CRM | Lead-to-order pipeline | Zoho CRM connector |
| Zoho People | Employee data sync | People API |
| SMS/Email Gateway | Notifications | Zoho Deluge `sendmail`, SMS API |

---

## 6. Report Architecture

### 6.1 Report Types

| Type | Zoho Creator Feature | Used For |
|------|---------------------|----------|
| Summary Report | Report Builder | Dashboard KPIs, totals |
| Detailed Report | Report Builder | Line-item listings |
| Summary with Groups | Report Builder | Department-wise / supplier-wise grouping |
| Pivot Report | Report Builder | Cross-tabular analysis (e.g. item × month) |
| Printable Report | Page Builder + Deluge | PO Print, GRN Print |

### 6.2 Key Report Queries

```
Open PO Register:
  SELECT FROM PO WHERE Status = "Issued" AND Total GRN Qty < Ordered Total

PO vs GRN Pending:
  SELECT PO.*, SUM(GRN.Received Qty) FROM PO LEFT JOIN GRN GROUP BY PO

Vendor Performance:
  SELECT Supplier, AVG(Delivery Delay), AVG(QC Pass %) FROM PO + GRN + QC GROUP BY Supplier

Stock Ledger:
  SELECT Item, Store, SUM(In) - SUM(Out) AS Balance FROM All Stock Movements GROUP BY Item, Store

Project Margins:
  SELECT Project, Project Cost - SUM(Task Actual) AS Margin FROM Project + Tasks GROUP BY Project
```

---

## 7. Security Architecture

### 7.1 Authentication

- Zoho Creator native authentication
- SSO via Zoho Directory (if configured)
- Session management handled by Zoho

### 7.2 Authorization Layers

| Layer | Mechanism |
|-------|-----------|
| Form-level | Zoho Creator form permissions (C/R/U/D) per role/profile |
| Field-level | Deluge-based field visibility/editable logic |
| Record-level | Zoho Creator criteria-based sharing rules |
| Report-level | Zoho Creator report sharing per role |
| Dashboard-level | Zoho Creator dashboard permissions per role |

### 7.3 Audit Trail

- Every Create/Update/Delete recorded in Zoho Creator's audit log
- GRN posting timestamp recorded in a dedicated backend field
- All approval actions logged in Creator's approval history

---

## 8. Performance Considerations

| Area | Strategy |
|------|----------|
| Large datasets | Zoho Creator pagination (max 200 records per page) |
| Auto-fetch lookups | Use Creator's native lookup fields (indexed) |
| Reports | Pre-aggregated summary views for dashboards |
| Deluge functions | Keep under 5-minute timeout; batch large operations |
| File attachments | Zoho Creator's native file storage (max 20MB per file) |

---

## 9. Deployment Architecture

```
            ┌──────────────────────────────┐
            │    Zoho Creator Cloud (IN)   │
            │                              │
            │  ┌────────────────────────┐  │
            │  │   Creator Forms Layer  │  │
            │  │  (UI / Mobile Forms)   │  │
            │  └───────────┬────────────┘  │
            │              │               │
            │  ┌───────────▼────────────┐  │
            │  │   Deluge Automation    │  │
            │  │  (Workflows, Functions) │  │
            │  └───────────┬────────────┘  │
            │              │               │
            │  ┌───────────▼────────────┐  │
            │  │   Creator Database     │  │
            │  │   (PostgreSQL-based)   │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │   Reports & Pages     │  │
            │  └────────────────────────┘  │
            │                              │
            └──────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Desktop │  │  Mobile  │  │  Tablet  │
    │  Browser │  │   App    │  │  Browser │
    └──────────┘  └──────────┘  └──────────┘
```

---

## 10. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Platform | Zoho Creator over custom dev | Faster delivery, built-in mobile, lower TCO |
| Language | Deluge over external scripts | Native Creator integration, no infra |
| Datacenter | India (.in) | Client is India-based |
| PO Series | Separate RM / RMWAD | Coding materials require stricter control |
| GRN Posting | Post = stock update (not save) | Prevents accidental stock updates |
| Partial GRN | Checkbox per line item | Supports real-world partial deliveries |
| Execution Mode | Area / Day basis on Project | Matches Chemsol's variable project types |
| SO/WO Mode | Supply+Apply / Supply only | Different business models with different fields |

---

## 11. Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Mandatory field missing | Zoho Creator native validation |
| Duplicate entry (e.g. Item Code) | Creator unique field constraint |
| Stock insufficient on MIS | Deluge validation: block if issue qty > available |
| PO after GRN | Block PO deletion/amendment |
| Invalid GST | Format validation in Deluge |
| API timeout | Retry logic in Deluge (max 3 attempts) |
| Concurrent edits | Creator's optimistic locking |
