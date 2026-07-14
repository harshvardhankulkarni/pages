# BRD / PRD / RFP — Project Budget Tracking & Inventory Management System

**Organization:** ITOTCloud Systems Pvt. Ltd.
**Document Version:** 1.0
**Date:** July 03, 2026
**Status:** Draft for Review
**Confidentiality:** Internal & Client-Facing Use

---

# PART I — BUSINESS REQUIREMENTS DOCUMENT (BRD)

## 1. Executive Summary

ITOTCloud Systems Pvt. Ltd. requires a comprehensive **Project Budget Tracking & Inventory Management System** to provide real-time budget-versus-actual visibility across projects, automated procurement workflows, and multi-warehouse inventory synchronization. The system will serve as an internal delivery blueprint and a deployable solution for clients across industries.

The system replaces fragmented manual tracking (spreadsheets, email-based approvals, siloed records) with an integrated low-code application built on Zoho Creator, encompassing 27 modules and 58+ automated Deluge workflows.

## 2. Business Context

ITOTCloud delivers Zoho-based implementation services. This system serves dual purposes:
1. **Internal operational tool** for managing ITOTCloud's own project budgets, procurement, and inventory
2. **Client delivery blueprint** — a repeatable, configurable solution deployable for clients needing budget tracking and inventory management

## 3. Business Problem Statement

| Problem | Impact | Frequency |
|---------|--------|-----------|
| No real-time visibility into budget consumption across projects | Overspend detected only at month-end reconciliation; corrective action too late | Daily |
| Manual purchase requisition and approval via email | Delayed procurement, lost requests, no audit trail | Weekly |
| Inventory stock levels tracked in spreadsheets | Stockouts causing project delays; overstock tying up capital | Daily |
| No integration between inventory consumption and budget tracking | Expenses booked without inventory deduction; inaccurate project P&L | Weekly |
| Multi-stage approvals lack structured workflow | Approval bottlenecks; no escalation path | Weekly |
| No automated alerts for budget thresholds (80/90/100%) | Overruns discovered after the fact | Monthly |

## 4. Business Objectives

| # | Objective | Success Metric | Current Baseline |
|---|-----------|----------------|------------------|
| 1 | Real-time budget vs actual tracking per project | Budget reports updated within 1 minute of transaction | 24-48 hour delay |
| 2 | Automated procurement lifecycle from requisition to PO | 100% of POs created from approved PRs without manual re-entry | Manual recreation |
| 3 | Multi-warehouse inventory with accurate stock levels | Stock accuracy > 98% | Unknown (spreadsheet) |
| 4 | Automated budget alerts at 80%, 90%, 100% consumption | Alerts sent within 5 minutes of threshold breach | No alerts exist |
| 5 | Project P&L visibility | Profit/Loss per project available on demand | Manual calculation |
| 6 | Reduction in procurement cycle time | 50% reduction from requisition to PO issuance | 5-7 days average |
| 7 | AI-powered budget forecasting (Phase 2) | 30/60/90-day burn forecasts within 10% accuracy | Not available |

## 5. Stakeholder Analysis

| Stakeholder | Role | Key Concern | Success Metric |
|-------------|------|-------------|----------------|
| Project Manager | Day-to-day project oversight | Budget visibility, expense approval | Real-time budget dashboard |
| Finance Manager | Financial control, approvals | Budget compliance, cost overruns | Automated alerts at thresholds |
| Procurement Team | Purchase requisitions & orders | Streamlined PR→PO workflow | 50% faster cycle time |
| Inventory Manager | Stock control across warehouses | Accurate stock levels, reorder alerts | Stock accuracy > 98% |
| Employees/Users | Submit expenses & purchase requests | Simple, intuitive forms | < 2 min to submit expense |
| System Administrator | System maintenance, user management | Role-based access, data integrity | Zero unauthorized access incidents |
| Client (when deployed) | End customer | Project cost transparency | On-demand P&L reports |

## 6. User Roles & Access

| Role | Modules | Key Permissions |
|------|---------|-----------------|
| Administrator | All | Full CRUD, user management, workflow configuration |
| Project Manager | Projects, Budgets, Expenses, Invoices | Create/edit projects, approve overruns, view reports |
| Finance Manager | Budgets, Expenses, Approvals, Invoices | Budget approvals, financial reports, invoice management |
| Procurement Team | Requisitions, POs, Vendors, Goods Receipt | Full procurement lifecycle |
| Inventory Manager | Inventory Items, Transactions, Transfers, Warehouses | Stock management, transfers, adjustments |
| Employee | Expenses, Purchase Requisitions | Submit expenses, create requisitions (own records) |

## 7. Business Process Flow (High-Level)

```
Project Setup → Budget Planning → Component Allocation
     ↓
Expense Submission → Budget Check → Auto-Approve or Overrun Workflow
     ↓
Procurement: PR → Multi-Stage Approval → Auto-PO → Vendor → Goods Receipt → Stock In
     ↕
Credit: QA/QC Rejection → Supplier Credit Note (Finance) → Disposition (Return/Scrap/Rework) → PO Credit Flag
     ↓
Inventory: Stock In/Out/Transfer/Adjustment → Sync Stock → Auto-Expense on Consumption
     ↓
Revenue: Invoice → Delivery Challan → Shipment → Stock Deduction → Project P&L
     ↓
Reporting: Budget vs Actual → KPI Dashboard → Alerts (80/90/100%)
```

## 8. Assumptions & Constraints

**Assumptions:**
- Zoho Creator Enterprise license is available
- Users have basic familiarity with Zoho ecosystem
- Internet connectivity is available for cloud access
- Client data migration will be a separate workstream

**Constraints:**
- **Platform:** Zoho Creator (low-code) — no custom backend code
- **No foreign keys:** All relationships use Lookup fields
- **No transactions:** Multi-step Deluge workflows need safety checks
- **Deluge runs per-record:** Use Scheduled Workflows for mass operations
- **Role-based access is per-form:** Not record-level; use form filters
- **Subform limit:** Max ~100 line items per subform
- **Formula fields:** Cannot reference external data — use Deluge instead

## 9. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Deluge timeouts on large datasets | Medium | High | Use scheduled workflows for mass updates |
| Negative stock due to out-of-sequence transactions | Low | High | Validate stock before deduction; enforce in Deluge |
| Lookup field shows stale inventory data | Medium | Medium | Use Formula Lookup (recalculated on load) |
| Concurrent users editing same budget component | Low | Medium | Zoho Creator record-level locking on submit |
| Email notifications flagged as spam | Medium | Low | Configure sender reputation; add to contacts |

---

# PART II — PRODUCT REQUIREMENTS DOCUMENT (PRD)

## 1. Product Vision

A unified, low-code project budget tracking and inventory management system that provides real-time financial control, automated procurement, and multi-warehouse stock synchronization — enabling organizations to prevent overspend, eliminate stockouts, and make data-driven project decisions.

## 2. Target Audience

| Persona | Description | Needs |
|---------|-------------|-------|
| **Project Manager** | Oversees project delivery, budget health | Real-time budget vs actual, overrun alerts |
| **Finance Manager** | Controls budgets, approves spending | Automated approval workflows, financial reports |
| **Procurement Officer** | Handles purchasing | Streamlined PR→PO, vendor management |
| **Inventory Manager** | Manages stock across locations | Multi-warehouse tracking, reorder alerts |
| **Team Member** | Submits expenses, requests purchases | Simple forms, status tracking |

## 3. Core Modules — Functional Requirements

### Module 1: Project Master (`Projects`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-PROJ-01 | P0 | Auto-generate unique Project Code on creation (e.g., `PROJ-0001`) |
| FR-PROJ-02 | P0 | Capture: Project Name, Account, Start/End Dates, PM, Total Budget, Status |
| FR-PROJ-03 | P1 | Validate no pending expenses/POs before marking Completed |
| FR-PROJ-04 | P1 | Auto-create final Invoice on completion for unbilled items |
| FR-PROJ-05 | P1 | Custom buttons: Create Invoice, Request Part Repair |

### Module 2: Vendor Management (`Vendors`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-VEN-01 | P0 | Capture vendor details: Name, Company, Email, Phone, Tax ID, PAN, Addresses |
| FR-VEN-02 | P0 | Vendor categorization: Raw Material, Service, Equipment, Logistics, Consulting |
| FR-VEN-03 | P0 | Embedded subforms for contacts and documents |
| FR-VEN-04 | P1 | Vendor performance rating (Excellent → Poor) |
| FR-VEN-05 | P1 | Payment terms configuration (Due on Receipt, Net 15/30/45/60) |

### Module 3: Account/Customer Management (`Accounts`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-ACC-01 | P0 | Capture customer/client details separate from vendors |
| FR-ACC-02 | P0 | Embedded subforms for contacts and documents |
| FR-ACC-03 | P1 | Payment terms, currency, tax configuration |

### Module 4: Warehouses (`Warehouses`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-WH-01 | P0 | Multi-warehouse support with auto-numbered codes |
| FR-WH-02 | P0 | Default "Main Warehouse" seeded on setup |
| FR-WH-03 | P1 | Address, city, state, country, phone, status fields |

### Module 5: Inventory Master (`Inventory_Items`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-INV-01 | P0 | SKU auto-numbering, item categorization, unit of measure |
| FR-INV-02 | P0 | Goods vs Services distinction (services bypass stock tracking) |
| FR-INV-03 | P0 | Per-warehouse stock tracking via embedded `Item_Warehouse_Stock` subform |
| FR-INV-04 | P0 | Current Stock maintained by Deluge (not on-demand aggregation) |
| FR-INV-05 | P0 | Reorder level, preferred vendor, purchase price |
| FR-INV-06 | P1 | HSN/SAC codes, tax configuration |
| FR-INV-07 | P1 | Stock Value formula (Current Stock × Purchase Price) |

### Module 6: Budget Planning (`Budget_Plans`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-BGT-01 | P0 | One active budget plan per project |
| FR-BGT-02 | P0 | Total Budget Amount validation against Project's Approved Budget |
| FR-BGT-03 | P0 | Component allocation via embedded `Budget_Components` subform |
| FR-BGT-04 | P1 | Status: Draft → Active → Revised → Closed |

### Module 7: Budget Components (`Budget_Components`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-BC-01 | P0 | Component Name, Allocated Amount, Spent Amount |
| FR-BC-02 | P0 | Formula fields: Remaining, Consumption % |
| FR-BC-03 | P0 | Auto-status: Within Budget / 80% Alert / 90% Alert / Exceeded |
| FR-BC-04 | P0 | Spent Amount updated automatically on expense approval |

### Module 8: Expense Management (`Expenses`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-EXP-01 | P0 | Auto-numbered expenses linked to Project + Budget Component |
| FR-EXP-02 | P0 | Auto-budget-check on submit: approve if within budget, trigger overrun workflow if exceeded |
| FR-EXP-03 | P0 | Supporting document upload |
| FR-EXP-04 | P1 | Expense types: Material, Labour, Equipment, Travel, Subcontract, Overhead |
| FR-EXP-05 | P1 | Status: Draft → Submitted → Approved / Overrun-Pending Approval / Rejected |

### Module 9: Budget Approval Workflow (`Budget_Approvals`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-BA-01 | P0 | Auto-created when expense exceeds budget component |
| FR-BA-02 | P0 | Capture: Original Budget, Expense Amount, Exceeded Amount |
| FR-BA-03 | P0 | Approval decision: Approve (with optional budget increase), Reject, Request Modification |
| FR-BA-04 | P1 | Email notification to PM + Finance Manager on overrun |
| FR-BA-05 | P1 | Audit trail of all approval actions |

### Module 10: Inventory Transactions (`Inventory_Transactions`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-IT-01 | P0 | Transaction types: Stock In, Stock Out, Adjustment, Return to Vendor, Reservation, Release |
| FR-IT-02 | P0 | Auto-update `Item_Warehouse_Stock.Current_Stock` and `Reserved_Qty` on every transaction |
| FR-IT-03 | P0 | Negative stock prevention validation |
| FR-IT-04 | P0 | Stock Out + Project → auto-create Expense record (closes budget-inventory loop) |
| FR-IT-05 | P1 | Rate/Unit Cost at time of transaction, Total Value |

### Module 11: Transfer Orders (`Transfer_Orders`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-TO-01 | P0 | From/To warehouse, line items subform |
| FR-TO-02 | P0 | Status = Completed → auto-generate paired Stock Out + Stock In transactions |
| FR-TO-03 | P1 | Status: Draft → In Transit → Completed → Cancelled |

### Module 12: Purchase Requisition (`Purchase_Requisitions`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-PR-01 | P0 | Multi-stage approval: Dept Manager → Finance → Procurement |
| FR-PR-02 | P0 | Auto-email notification to next approver on stage change |
| FR-PR-03 | P0 | Final approval → auto-create Purchase Order (Draft) with line items copied |
| FR-PR-04 | P1 | Urgency levels, delivery date, justification |
| FR-PR-05 | P1 | Request types: General, Part Repair, Service |

### Module 13: Purchase Orders (`Purchase_Orders`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-PO-01 | P0 | Complete PO lifecycle: Draft → Open → Partially Invoiced → Billed → Closed → Cancelled |
| FR-PO-02 | P0 | Line-level items with discount, tax, and total calculations |
| FR-PO-03 | P0 | Auto-email vendor on Status = Open with PO details |
| FR-PO-04 | P1 | Validate no linked GRN before cancellation |
| FR-PO-05 | P1 | POs flagged for manual close review after 30 days in Open status |

### Module 14: Goods Receipt (`Goods_Receipts`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-GRN-01 | P0 | Accepted vs Rejected quantity per line item |
| FR-GRN-02 | P0 | Status = Open → auto-create Stock In for accepted quantities |
| FR-GRN-03 | P1 | Reason for rejection, condition notes, warehouse assignment per line |

### Module 15: Invoicing (`Invoices`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-INV-01 | P0 | Revenue tracking per project with line item details |
| FR-INV-02 | P0 | Status: Draft → Sent → Partially Paid → Paid → Overdue → Cancelled |
| FR-INV-03 | P0 | Formula fields: Balance Due, Total, Tax Total |
| FR-INV-04 | P1 | Custom "Create DC" button → auto-create Delivery Challan from invoice line items |
| FR-INV-05 | P1 | Auto-mark Overdue when Due Date passed |

### Module 16: Delivery Challan (`Delivery_Challans`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-DC-01 | P0 | Track physical dispatch: customer, vehicle, driver, date |
| FR-DC-02 | P0 | Status = Shipped → auto-create Stock Out for all line items |
| FR-DC-03 | P1 | Validate stock availability before creation |
| FR-DC-04 | P1 | Prompt invoice creation if no linked invoice |

### Module 17: BOM — Bill of Materials (`BOM`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-BOM-01 | P1 | Define component structure for manufactured items |
| FR-BOM-02 | P1 | Auto-calculate: Total Component Cost, Total Manufacturing Cost (incl. labor + overhead) |
| FR-BOM-03 | P1 | Version tracking, revision management |

### Module 18: Vendor Bills — AP Sub-ledger (`Vendor_Bills`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-VBILL-01 | P0 | Record vendor invoices against Purchase Orders with embedded Bill_Line_Items subform |
| FR-VBILL-02 | P0 | 3-way match validation: PO Ordered Qty ≥ Bill Qty, GRN Accepted Qty ≥ Bill Qty |
| FR-VBILL-03 | P0 | Auto-numbered bills (BILL-{0000}), Status lifecycle: Draft → Received → Matched → Approved → Partially Paid → Paid → Cancelled |
| FR-VBILL-04 | P0 | Balance Due formula tracking, auto-updated by Payments |
| FR-VBILL-05 | P1 | Purchase Price Variance (PPV) tracking — compare GRN Actual Cost vs PO Rate per line item |
| FR-VBILL-06 | P1 | AP Aging report — Bills grouped by Due Date (Current, 1-30, 31-60, 61-90, 90+) |

### Module 19: Payments — Unified AP/AR (`Payments`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-PMT-01 | P0 | Record both outgoing vendor payments (AP) and incoming customer receipts (AR) |
| FR-PMT-02 | P0 | Auto-update linked Bill/Invoice Amount_Paid, Balance_Due, and Status on completion |
| FR-PMT-03 | P0 | Payment methods: Bank Transfer, Cheque, Cash, Credit Card, UPI |
| FR-PMT-04 | P0 | Overpayment prevention — validate Amount ≤ Balance Due of linked document |
| FR-PMT-05 | P1 | Payment reversal with automatic rollback of Amount_Paid on linked document |
| FR-PMT-06 | P1 | Payment Register report — filterable by Type, Vendor, Customer, date range |

### Module 20: Reports & Dashboards

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-RPT-01 | P0 | Executive Dashboard with KPI cards: Budget Utilization %, Open PO Value, Inventory Value |
| FR-RPT-02 | P0 | Budget vs Actual report (pivot by component and month) |
| FR-RPT-03 | P0 | Project P&L (Total Invoiced − Total Expenses) |
| FR-RPT-04 | P0 | Low Stock Alert (Current Stock ≤ Reorder Level) |
| FR-RPT-05 | P1 | Monthly Spend Trend chart, Vendor Spend analysis |
| FR-RPT-06 | P1 | Invoice Aging report, DC Register, BOM Cost Summary |
| FR-RPT-07 | P0 | Scheduled daily KPI refresh (midnight cron) |
| FR-RPT-08 | P0 | Budget alerts at 80%, 90%, 100% consumption (email notification) |
| FR-RPT-09 | P0 | Low stock alerts (email notification) |

### Module 21: Currency Exchange Rates (`Currency_Rates`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-FX-01 | P0 | Define exchange rates: Base Currency, Target Currency, Rate, Effective Date |
| FR-FX-02 | P0 | Auto-populate FX_Rate on Bills, Invoices, Payments from nearest prior rate |
| FR-FX-03 | P1 | FX Gain/Loss calculation when payment rate differs from bill/invoice rate |
| FR-FX-04 | P1 | FX Gain/Loss Register and Currency Exposure reports |

### Module 22: Accounting Periods (`Accounting_Periods`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-AP-01 | P0 | Define accounting periods (Monthly/Quarterly/Yearly) with Open/Closing/Closed status |
| FR-AP-02 | P0 | Reject financial transactions posted to closed periods |
| FR-AP-03 | P0 | GRNI accrual reporting — goods received but not invoiced at month-end |
| FR-AP-04 | P1 | Trial Balance by Period report |
| FR-AP-05 | P1 | Period Close Checklist dashboard |

### Module 23: Audit Log (`Audit_Log`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-AUD-01 | P0 | Immutable audit log for all P0 financial forms |
| FR-AUD-02 | P0 | Auto-capture: status changes, amount edits, record creation |
| FR-AUD-03 | P0 | Write-only via Deluge — users cannot modify audit records |
| FR-AUD-04 | P1 | Audit reports: by date, by module, by user, by record ID |

### Module 24: Expense Allocations (Enhanced Expenses)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-ALLOC-01 | P0 | Split expense across multiple Budget Components via embedded subform |
| FR-ALLOC-02 | P0 | Validate sum of allocations = total expense amount |
| FR-ALLOC-03 | P0 | Each allocation updates its respective Budget Component's Spent Amount |
| FR-ALLOC-04 | P1 | Legacy single-component mode preserved when no allocations exist |

### Module 25: Budget Revisions (Enhanced Budget_Plans)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-REV-01 | P0 | Auto-create revision record when Budget_Approval modifies budget amount |
| FR-REV-02 | P0 | Track: Previous Amount, New Amount, Change Amount, Reason, Approved By |
| FR-REV-03 | P1 | Budget Revision History and Component Change Log reports |

### Module 26: Customer Credit Notes (`Customer_Credit_Notes`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-CCN-01 | P1 | Record customer returns/credit — CCN reduces Invoice Balance Due when issued |
| FR-CCN-02 | P1 | Embedded CCN_Line_Items subform for goods/service return lines |
| FR-CCN-03 | P1 | For goods returns, auto-create Stock In (Return to Customer) inventory transaction |
| FR-CCN-04 | P1 | Status: Draft → Issued → Applied → Cancelled |
| FR-CCN-05 | P1 | CCN cancellation reverses Invoice Balance Due adjustment |

### Module 27: Manufacturing Orders (`Manufacturing_Orders`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-MO-01 | P1 | Production lifecycle: Draft → Released → In Progress → Completed → Cancelled |
| FR-MO-02 | P1 | MO_Components subform for raw material requirements |
| FR-MO-03 | P1 | On Release: validate stock availability, reserve component quantities |
| FR-MO-04 | P1 | On Complete: issue components via Stock Out, receive finished goods via Stock In |
| FR-MO-05 | P1 | On Cancel: release all reserved component stock |

### Module 28: Sales Orders (`Sales_Orders`)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-SO-01 | P1 | Customer order management with embedded SO_Line_Items subform |
| FR-SO-02 | P1 | Status: Draft → Confirmed → In Progress → Shipped → Invoiced → Completed → Cancelled |
| FR-SO-03 | P1 | On Confirm: reserve stock for all line items |
| FR-SO-04 | P1 | On Ship: auto-create Stock Out for each line item |
| FR-SO-05 | P1 | Custom button "Create Invoice" — creates Invoice from uninvoiced line items |
| FR-SO-06 | P1 | Custom button "Create DC" — creates Delivery Challan from undelivered line items |
| FR-SO-07 | P1 | Cancellation guard — blocked if partial delivery or invoicing exists |

## 4. Automation Requirements (Deluge Workflows)

| # | Workflow | Trigger | Priority |
|---|----------|---------|----------|
| 1 | Generate Project Code | Project Create (On Submit) | P0 |
| 2 | Budget Validation (sum components ≤ total) | Budget Plan Submit | P0 |
| 3 | Expense Budget Check (auto-approve or overrun) | Expense Submit | P0 |
| 4 | Create Budget Approval on overrun | Expense Submit (overrun) | P0 |
| 5 | Update Expense on Approval Status Change | Budget Approval status change | P0 |
| 6 | Sync Stock on Inventory Transaction | Inventory Transaction Submit | P0 |
| 7 | Auto-create Expense from Stock Out | Stock Out + Project set | P0 |
| 8 | Paired Stock Out/In on Transfer Complete | Transfer Order Status = Completed | P0 |
| 9 | Stock In from Goods Receipt | GRN Status = Open | P0 |
| 10 | Email Vendor on PO Open | PO Status = Open | P0 |
| 11 | Notify Next Approver on PR Stage Change | PR stage change | P0 |
| 12 | Daily Cron: alerts, KPI refresh, overdue mark | Scheduled (midnight) | P0 |
| 13 | Update Project Total Invoiced on Invoice Sent | Invoice Submit | P1 |
| 14 | Update Amount Paid on Invoice Payment | Invoice Submit | P1 |
| 15 | Auto-create Stock Out on DC Shipped | DC Status = Shipped | P0 |
| 16 | Calculate BOM Component + Mfg Costs | BOM Submit | P1 |
| 17 | Auto-create PO from Approved PR | PR final approval | P0 |
| 18 | Stock Reservation — increment Reserved_Qty | Reservation transaction | P1 |
| 19 | Auto-create DC from Invoice | Custom Button on Invoice | P1 |
| 20 | Auto-final Invoice on Project Completed | Project Status = Completed | P1 |
| 21 | Prevent Negative Stock | Inventory Transaction Submit | P0 |
| 22 | Validate No Linked GRN Before PO Cancellation | PO Status = Cancelled | P1 |
| 23 | Validate No Open Items Before Project Completion | Project Status = Completed | P1 |
| 24 | Flag Aged POs for Manual Close Review | Scheduled workflow | P2 |
| 25 | 3-Way Match Validation | Bill Status = Matched | P0 |
| 26 | Update Bill Payment Status | Payment Completed (AP) | P0 |
| 27 | Update Invoice Payment Status | Payment Completed (AR) | P0 |
| 28 | Reverse Payment on linked document | Payment Reversed | P1 |
| 29 | Calculate Weighted Average Cost | Inventory Transaction (Stock In) | P1 |
| 30 | FX Rate Auto-Population | Bill/Invoice/Payment Create (On Load) | P1 |
| 31 | FX Gain/Loss Calculation | Payment Submit | P1 |
| 32 | Period Lock Validation | All Financial Forms Submit | P0 |
| 33 | Audit Log — Status Change | All P0 Forms Submit | P0 |
| 34 | Audit Log — Financial Edit | All P0 Forms Submit | P1 |
| 35 | Expense Allocation Validation | Expense Submit | P0 |
| 36 | Budget Revision Auto-Create | Budget Approval Submit | P1 |
| 37 | GRNI Accrual Check | Scheduled (Month-end) | P1 |
| 38 | PO Budget Check — validate available budget before Open | PO Status = Pending Approval | P0 |
| 39 | PO Budget Commit — increment Committed_Amount | PO Status = Open | P0 |
| 40 | PO Budget Release — decrement Committed_Amount | PO Status = Cancelled | P0 |
| 41 | Bill Pending Approval — route to Finance Manager after 3-way match | Bill Status = Matched | P0 |
| 42 | Payment Approval Routing — threshold-based auto-approve | Payment Submit | P0 |
| 43 | PR Budget Check — validate before PO auto-creation | PR Final Approval | P0 |
| 44 | CCN Issued — reduce Invoice Balance Due, create return inventory | CCN Status = Issued | P1 |
| 45 | CCN Cancelled — reverse Invoice adjustments | CCN Status = Cancelled | P1 |
| 46 | MO Released — reserve component stock | MO Status = Released | P1 |
| 47 | MO Completed — issue components, receive finished goods | MO Status = Completed | P1 |
| 48 | MO Cancelled — release reserved stock | MO Status = Cancelled | P1 |
| 49 | SO → Create Invoice — custom button | Button click | P1 |
| 50 | SO → Create DC — custom button | Button click | P1 |

## 5. Non-Functional Requirements

| # | Requirement | Specification | Priority |
|---|-------------|---------------|----------|
| NFR-01 | Performance | Form submit response < 3 seconds for standard workflows | P0 |
| NFR-02 | Performance | Scheduled workflows complete within 5 minutes for < 10,000 records | P1 |
| NFR-03 | Scalability | Support up to 50 concurrent users, 100,000+ transactions | P1 |
| NFR-04 | Security | Role-based access per form; no record-level sharing | P0 |
| NFR-05 | Data Integrity | All inventory transactions include safety checks for negative stock | P0 |
| NFR-06 | Availability | Zoho Creator uptime SLA (99.9%) as per Zoho's standard terms | P1 |
| NFR-07 | Usability | Forms follow consistent layout; subform entry for all line items | P0 |
| NFR-08 | Auditability | All status changes on budget approvals logged; Creator built-in audit available | P1 |
| NFR-09 | Backup | Zoho Creator auto-backup; export plan as documented procedure | P2 |
| NFR-10 | Mobile | Native Zoho Creator mobile forms (no standalone mobile app) | P1 |

## 6. Release Criteria

All Phase 1 modules must be verified against:
1. Each form creates/saves records correctly with field-level validation
2. All 50 Deluge workflows execute without errors for expected inputs
3. Lookup relationships return correct data
4. Role-based access restricts unauthorized actions
5. Reports and dashboards display correct aggregate values
6. Budget alerts trigger at correct thresholds
7. Inventory stock calculations are accurate (±0 tolerance on test data)
8. PR → PO auto-creation copies all line items correctly
9. Goods Receipt → Stock In chain executes end-to-end
10. Transfer Order → paired transactions complete correctly
11. Vendor Bill 3-way match validation works correctly (PO × GRN × Bill)
12. Payment updates linked Bill/Invoice Amount_Paid and Balance_Due correctly
13. PPV (Purchase Price Variance) calculated correctly per line item
14. Audit Log captures all status changes correctly across financial forms
15. Period lock prevents posting to closed periods
16. Expense allocation validation prevents misallocation (sum != amount)
17. Budget revisions are created automatically on overrun approval

## 7. Future Scope (Phase 2 — AI Integration)

| Feature | Description | Target |
|---------|-------------|--------|
| AI Budget Forecasting | 30/60/90-day burn forecasts from historical data | Phase 2 |
| Anomaly Detection | Flag unusual spending vs historical baselines | Phase 2 |
| Smart Procurement | Optimal reorder quantities and timing recommendations | Phase 2 |
| Natural Language Reporting | Q&A over project financials (e.g., "Which project is over budget?") | Phase 2 |
| Weekly AI Summaries | Plain-English budget summaries for PMs | Phase 2 |
| Zoho Projects Integration | Link tasks to budget tracking; log time as expense | Phase 2 |
| Zoho Analytics | Advanced dashboards with cross-filter drill-down | Phase 2 |
| Zoho Books/Inventory | Full accounting and inventory integration | Phase 2 |
| Vendor Self-Service Portal | External vendor access for PO acceptance and invoicing | Phase 2 |

---

# PART III — REQUEST FOR PROPOSAL (RFP)

## 1. RFP Overview

**RFP Title:** Project Budget Tracking & Inventory Management System — Zoho Creator Implementation
**Issuing Organization:** ITOTCloud Systems Pvt. Ltd.
**RFP Number:** ITOTCLOUD-BTIM-2026-001
**Issue Date:** July 03, 2026
**Submission Deadline:** August 15, 2026
**Contact:** Implementation Lead — procurement@itotcloud.com

## 2. Organization Background

ITOTCloud Systems Pvt. Ltd. is a Zoho implementation services company. This RFP seeks proposals from qualified vendors/partners to implement a 18-module Project Budget Tracking & Inventory Management system on Zoho Creator, as specified in this document.

## 3. Scope of Work

### 3.1 What is In Scope

| Workstream | Description | Est. Effort |
|------------|-------------|-------------|
| Phase 1A — Foundation | Vendors, Accounts, Projects, Warehouses, Inventory Items | 5–7 days |
| Phase 1B — Budget & Stock Engine | Budget Plans, Budget Components, Inventory Transactions | 5–7 days |
| Phase 1C — Spend & Requests | Expenses, Purchase Requisitions | 4–5 days |
| Phase 1D — Procurement Cycle | Budget Approvals, Purchase Orders (enhanced), Goods Receipt (enhanced), Supplier Credit Notes, Transfers | 8–12 days |
| Phase 1E — Revenue & Manufacturing | BOM, Delivery Challans, Invoicing | 5–7 days |
| Phase 1F — Reports & Dashboards | KPI dashboards, 17+ reports, scheduled alerts | 5–7 days |
| Phase 1G — AP/AR Sub-ledger | Vendor Bills, Payments, AP Aging, PPV Register | 4–6 days |
| Phase 1H — Financial Controls | FX Rates, Accounting Periods, Tax/GST enhancements | 5–7 days |
| Phase 1I — Governance | Audit Log, Expense Allocations, Budget Revisions | 4–6 days |
| Phase 1J — Approvals & Controls | PO/Bill/Payment approval workflows, committed budget, SoD | 5–7 days |
| Phase 1K — Gaps Closure | Customer Credit Notes, Manufacturing Orders, Sales Orders | 5–7 days |
| **Phase 1 Total** | **27 modules, 58+ Deluge workflows** | **56–82 days** |
| Phase 2 — AI Integration (Optional) | AI forecasting, anomaly detection, NLP reporting | TBD (separate SOW) |

### 3.2 What is Out of Scope

- Full Zoho Books/Inventory integration
- Standalone mobile application (Zoho Creator mobile forms are sufficient)
- External vendor self-service portal
- Zoho Analytics advanced dashboards (Phase 2)
- Zoho Projects integration (Phase 2)

### 3.3 Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|-------------------|
| D1 | Zoho Creator application with all 27 modules configured | All forms, fields, lookups per IMPLEMENTATION_PLAN.md specs |
| D2 | Deluge automation workflows (58+) | Each workflow passes test scenarios without errors |
| D3 | Role-based access configuration | 10 user roles with correct form-level permissions |
| D4 | Reports & Dashboards | 20+ reports + Executive Dashboard with KPI cards |
| D5 | Budget alert system | Alerts trigger at 80%/90%/100% consumption thresholds |
| D6 | Documentation | Updated implementation plan reflecting any design changes |
| D7 | Seed data | Default warehouse, sample budget categories, test records |
| D8 | User training | Documentation or sessions for each user role |

## 4. Technical Requirements

### 4.1 Platform

| Requirement | Specification | Mandatory |
|-------------|---------------|-----------|
| Development Platform | Zoho Creator Enterprise | Yes |
| Programming Language | Deluge script (Zoho proprietary) | Yes |
| Data Storage | Zoho Creator native database | Yes |
| Reports Engine | Zoho Creator Reports + Dashboard widgets | Yes |
| Authentication | Zoho Creator user management + SSO | Yes |
| Email Notifications | Zoho Creator workflow email | Yes |

### 4.2 Integration Requirements (Phase 2, Optional)

- Zoho Books API integration
- Zoho Inventory API integration
- Zoho Projects API integration
- Zoho Analytics API integration
- Custom AI service (Python/FastAPI for forecasting and NLP)

### 4.3 Vendor Qualifications

| Criteria | Requirement |
|----------|-------------|
| Experience | Minimum 3 Zoho Creator implementations delivered |
| Team Composition | Zoho Creator Developer, Deluge Specialist, QA Engineer |
| Certifications | Zoho Creator Certified (preferred) |
| Reference Projects | At least 2 similar budget/inventory management implementations |
| SLA | Bug fixes within 48 hours; critical issues within 8 hours |
| Language | English (fluent written and verbal) |
| Time Zone Overlap | Minimum 4 hours overlap with IST (UTC+5:30) |

## 5. Proposal Submission Requirements

### 5.1 Proposal Structure

Vendors must submit proposals containing:

| Section | Content Required |
|---------|-----------------|
| Executive Summary | Understanding of requirements, proposed approach, differentiators |
| Technical Approach | Architecture, implementation methodology, Deluge design patterns |
| Project Plan | Phase-wise timeline, milestones, resource allocation |
| Team Profile | Key personnel, roles, experience, certifications |
| Previous Work | 2-3 case studies of similar Zoho Creator implementations |
| Commercial Proposal | Fixed price per phase, total project cost, payment milestones |
| Support & Maintenance | Post-deployment support model, SLA terms |
| Risks | Identified risks and proposed mitigations |

### 5.2 Evaluation Criteria

| Criteria | Weight |
|----------|--------|
| Technical Approach & Methodology | 30% |
| Relevant Experience & Track Record | 25% |
| Team Qualifications | 15% |
| Commercial Competitiveness | 20% |
| Support & SLA Commitment | 10% |

## 6. Commercial Framework

### 6.1 Pricing Model

All proposals must be submitted as **fixed-price per phase** with the following pricing structure:

| Phase | Description | Expected Price Range (USD) |
|-------|-------------|---------------------------|
| Phase 1A | Foundation (5 modules) | $3,000 – $5,000 |
| Phase 1B | Budget & Stock Engine (3 modules) | $3,000 – $5,000 |
| Phase 1C | Spend & Requests (2 modules) | $2,500 – $4,000 |
| Phase 1D | Procurement Cycle (5 modules incl. Supplier Credit Notes) | $4,500 – $7,000 |
| Phase 1E | Revenue & Manufacturing (3 modules) | $3,000 – $5,000 |
| Phase 1F | Reports & Dashboards | $3,000 – $5,000 |
| Phase 1G | AP/AR Sub-ledger | $2,500 – $4,000 |
| Phase 1H | Financial Controls | $3,000 – $5,000 |
| Phase 1I | Governance & Audit | $2,500 – $4,000 |
| Phase 1J | Approvals & Controls (SoD) | $3,000 – $5,000 |
| Phase 1K | Customer Credit Notes, MO, SO | $3,000 – $5,000 |
| **Phase 1 Total** | **27 modules** | **$34,000 – $55,000** |
| Phase 2 | AI Integration (Optional) | TBD |

### 6.2 Payment Milestones

| Milestone | Payment % | Trigger |
|-----------|-----------|---------|
| Contract Signing | 20% | Signed agreement |
| Phase 1A Completion | 10% | Foundation modules verified |
| Phase 1B Completion | 10% | Budget & stock engine verified |
| Phase 1C Completion | 10% | Spend & requests verified |
| Phase 1D Completion | 15% | Procurement cycle verified |
| Phase 1E Completion | 10% | Revenue & manufacturing verified |
| Phase 1F Completion | 15% | Reports & dashboards verified |
| Phase 1G Completion | 10% | AP/AR sub-ledger verified |
| Phase 1H Completion | 5% | Financial controls verified |
| Phase 1I Completion | 5% | Governance & audit verified |
| Phase 1J Completion | 5% | Approvals & controls verified |
| Phase 1K Completion | 5% | Gaps closure verified |
| Final Acceptance & UAT Sign-off | 10% | All 27 modules accepted, training completed |

## 7. Timeline & Milestones

| Milestone | Target Date |
|-----------|-------------|
| RFP Issued | July 03, 2026 |
| Vendor Q&A Deadline | July 25, 2026 |
| Proposal Submission Deadline | August 15, 2026 |
| Shortlisting & Demos | August 20–30, 2026 |
| Contract Award | September 05, 2026 |
| Phase 1A Go-Live | October 15, 2026 |
| Phase 1B Go-Live | November 01, 2026 |
| Phase 1C Go-Live | November 15, 2026 |
| Phase 1D Go-Live | December 10, 2026 |
| Phase 1E Go-Live | December 25, 2026 |
| Phase 1F Go-Live | January 15, 2027 |
| Full UAT & Go-Live | January 31, 2027 |

## 8. Terms & Conditions (Summary)

| Clause | Detail |
|--------|--------|
| **Intellectual Property** | All code, forms, workflows become property of ITOTCloud upon full payment |
| **Confidentiality** | NDA required before access to detailed design documents |
| **Warranty** | 90 days post-UAT sign-off for bug fixes at no additional cost |
| **Data Security** | Vendor must follow Zoho Creator security best practices |
| **Change Orders** | Scope changes beyond 10% of phase value require separate change order |
| **Termination** | 30-day written notice; payment due for work completed up to termination date |
| **Governing Law** | Laws of India |

## 9. Proposal Evaluation & Award Process

```
Step 1: RFP Issued — July 03
Step 2: Vendor Q&A — July 03–25 (written questions via email)
Step 3: Proposals Due — August 15 (submitted via email to procurement@itotcloud.com)
Step 4: Initial Screening — August 16–20 (eligibility check)
Step 5: Technical Evaluation — August 20–25 (scoring against criteria)
Step 6: Shortlisted Vendor Demos — August 25–30
Step 7: Commercial Negotiation — September 01–05
Step 8: Contract Award — September 05
```

## 10. Contact Information

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Procurement Contact | Implementation Lead | procurement@itotcloud.com | — |
| Technical Queries | Delivery Team Lead | delivery@itotcloud.com | — |

**ITOTCloud Systems Pvt. Ltd.**
Aston Plaza, Ambegaon BK, Pune — 411046, India

---

## Appendix A: Module Inventory

| # | Module | Form Name | Subforms | Key Automations |
|---|--------|-----------|----------|-----------------|
| 1 | Project Master | `Projects` | — | Auto-code, completion validation, final invoice |
| 2 | Vendor Management | `Vendors` | `Vendor_Contacts`, `Vendor_Documents` | — |
| 3 | Account Management | `Accounts` | `Account_Contacts`, `Account_Documents` | — |
| 4 | Warehouses | `Warehouses` | — | Default warehouse seed |
| 5 | Inventory Master | `Inventory_Items` | `Item_Warehouse_Stock` | Current Stock rollup |
| 6 | Budget Planning | `Budget_Plans` | `Budget_Components`, `Budget_Revisions` | Sum validation |
| 7 | Budget Components | `Budget_Components` | — | Auto-status based on consumption |
| 8 | Expense Management | `Expenses` | Expense_Allocations | Budget check, overrun workflow |
| 9 | Budget Approval | `Budget_Approvals` | — | Audit trail, email notifications |
| 10 | Inventory Transactions | `Inventory_Transactions` | — | Stock sync, auto-expense |
| 11 | Transfer Orders | `Transfer_Orders` | `TO_Line_Items` | Paired Stock Out/In |
| 12 | Purchase Requisition | `Purchase_Requisitions` | `PR_Line_Items` | Multi-stage approval, auto-PO |
| 13 | Purchase Orders | `Purchase_Orders` | `PO_Line_Items` | Vendor email, lifecycle mgmt |
| 14 | Goods Receipt | `Goods_Receipts` | `GRN_Line_Items` | Auto Stock In, PO Receipt Status update, credit tracking |
| 15 | **Supplier Credit Notes** | `Supplier_Credit_Notes` | `SCN_Line_Items` | **Credit/debit note vs supplier; auto Return to Vendor; PO credit flag; GRN credit tracking** |
| 16 | Invoicing | `Invoices` | `Invoice_Line_Items` | Revenue sync, Create DC |
| 17 | Delivery Challan | `Delivery_Challans` | `DC_Line_Items` | Auto Stock Out |
| 18 | BOM | `BOM` | `BOM_Line_Items` | Cost calculation |
| 19 | Reports & Dashboards | — | — | KPIs, alerts, 20+ reports |
| 20 | Vendor Bills (AP) | `Vendor_Bills` | `Bill_Line_Items` | 3-way match, PPV calculation, AP Aging |
| 21 | Payments | `Payments` | — | AP/AR unified, auto-update Bill/Invoice, overpayment prevention |
| 22 | Currency Exchange Rates | `Currency_Rates` | — | FX rate management, auto-population |
| 23 | Accounting Periods | `Accounting_Periods` | — | Period close, locking, GRNI |
| 24 | Audit Log | `Audit_Log` | — | Immutable audit trail for financial forms |
| 25 | Customer Credit Notes | `Customer_Credit_Notes` | `CCN_Line_Items` | Reduce Invoice Balance Due, auto Stock In for goods returns |
| 26 | Manufacturing Orders | `Manufacturing_Orders` | `MO_Components` | Reserve/issue/receive stock, production lifecycle |
| 27 | Sales Orders | `Sales_Orders` | `SO_Line_Items` | Order management, custom Invoice/DC buttons |

## Appendix B: Deluge Automation Catalog

| ID | Automation | Trigger | Type | Priority |
|----|-----------|---------|------|----------|
| D-01 | Generate Project Code | Project On Create | Form Workflow | P0 |
| D-02 | Validate Budget Components ≤ Total | Budget Plan Submit | Form Workflow | P0 |
| D-03 | Expense Budget Check & Approval | Expense Submit | Form Workflow | P0 |
| D-04 | Create Overrun Approval Record | Expense Overrun | Form Workflow | P0 |
| D-05 | Update Expense on Approval Decision | Budget Approval Status Change | Form Workflow | P0 |
| D-06 | Sync Item_Warehouse_Stock | Inventory Transaction Submit | Form Workflow | P0 |
| D-07 | Auto-Create Expense from Stock Out | Stock Out Transaction | Form Workflow | P0 |
| D-08 | Paired Stock Out/In on Transfer | Transfer Order Completed | Form Workflow | P0 |
| D-09 | Stock In from Goods Receipt | GRN Open | Form Workflow | P0 |
| D-10 | Email Vendor on PO Open | PO Status = Open | Form Workflow | P1 |
| D-11 | Notify Next PR Approver | PR Stage Change | Form Workflow | P0 |
| D-12 | Daily Cron: KPIs, Alerts, Overdue | Scheduled (Midnight) | Scheduled | P0 |
| D-13 | Update Project Revenue on Invoice Sent | Invoice Submit | Form Workflow | P1 |
| D-14 | Update Payment on Invoice Paid | Invoice Submit | Form Workflow | P1 |
| D-15 | Auto Stock Out on DC Shipped | DC Status = Shipped | Form Workflow | P0 |
| D-16 | Calculate BOM Costs | BOM Submit | Form Workflow | P1 |
| D-17 | Auto-Create PO from Approved PR | PR Final Approval | Form Workflow | P0 |
| D-18 | Reserve Stock | Reservation Transaction | Form Workflow | P1 |
| D-19 | Auto-Create DC from Invoice | Invoice Custom Button | Custom Action | P1 |
| D-20 | Auto-Final Invoice on Project Complete | Project Status Change | Form Workflow | P1 |
| D-21 | Negative Stock Prevention | Inventory Transaction Submit | Form Workflow | P0 |
| D-22 | Validate PO Cancellation | PO Status = Cancelled | Form Workflow | P1 |
| D-23 | Validate Project Completion | Project Status = Completed | Form Workflow | P1 |
| D-24 | Flag Aged POs | Scheduled (Weekly) | Scheduled | P2 |
| D-25 | SCN Issued — Update PO credits + auto Return to Vendor | SCN Status = Issued | Form Workflow | P0 |
| D-26 | SCN Settled — Clear PO credit flag | SCN Status = Settled | Form Workflow | P1 |
| D-27 | SCN Cancelled — Reverse credits | SCN Status = Cancelled | Form Workflow | P1 |
| D-28 | PO Receipt Status recalculation per line item | GRN Submit (Status = Open) | Form Workflow | P0 |
| D-29 | 3-Way Match Validation | Bill Status = Matched | Form Workflow | P0 |
| D-30 | Update Bill on Payment | Payment Completed (AP) | Form Workflow | P0 |
| D-31 | Update Invoice on Receipt | Payment Completed (AR) | Form Workflow | P0 |
| D-32 | Reverse Payment | Payment Reversed | Form Workflow | P1 |
| D-33 | Weighted Average Cost Calculation | Inventory Transaction (Stock In) | Form Workflow | P1 |
| D-34 | FX Rate Auto-Population | Bill/Invoice/Payment Create | Form Workflow | P1 |
| D-35 | FX Gain/Loss Calculation | Payment Submit | Form Workflow | P1 |
| D-36 | Period Lock Validation | All Financial Forms | Form Workflow | P0 |
| D-37 | Audit Log — Status Change | All P0 Forms | Form Workflow | P0 |
| D-38 | Audit Log — Financial Edit | All P0 Forms | Form Workflow | P1 |
| D-39 | Expense Allocation Validation | Expense Submit | Form Workflow | P0 |
| D-40 | Budget Revision Auto-Create | Budget Approval Submit | Form Workflow | P1 |
| D-41 | GRNI Accrual | Scheduled (Month-end) | Scheduled | P1 |
| D-42 | PO Budget Check — validate available budget | PO Pending Approval | Form Workflow | P0 |
| D-43 | PO Budget Commit — increment Committed_Amount | PO Open | Form Workflow | P0 |
| D-44 | PO Budget Release — decrement Committed_Amount | PO Cancelled | Form Workflow | P0 |
| D-45 | Bill Pending Approval — route to Finance Manager | Bill Matched | Form Workflow | P0 |
| D-46 | Payment Approval Routing — threshold-based | Payment Pending Approval | Form Workflow | P0 |
| D-47 | PR Budget Check — validate before auto-PO | PR Final Approval | Form Workflow | P0 |
| D-48 | CCN Issued — reduce Invoice Balance Due, return inventory | CCN Issued | Form Workflow | P1 |
| D-49 | CCN Cancelled — reverse Invoice adjustments | CCN Cancelled | Form Workflow | P1 |
| D-50 | MO Released — reserve component stock | MO Released | Form Workflow | P1 |
| D-51 | MO Completed — issue components, receive goods | MO Completed | Form Workflow | P1 |
| D-52 | MO Cancelled — release reserved stock | MO Cancelled | Form Workflow | P1 |
| D-53 | SO → Create Invoice (custom button) | Button click | Custom Action | P1 |
| D-54 | SO → Create DC (custom button) | Button click | Custom Action | P1 |

## Appendix C: Key Lookup Relationships

```
Projects → Accounts
Budget_Plans → Projects
Budget_Components → Budget_Plans, Projects
Expenses → Projects, Budget_Components, Vendors
Budget_Approvals → Expenses, Projects, Budget_Components
Inventory_Transactions → Inventory_Items, Warehouses, Projects
Transfer_Orders → Warehouses (From/To)
Purchase_Requisitions → Projects
Purchase_Orders → Vendors, Projects, Purchase_Requisitions
Goods_Receipts → Purchase_Orders
Supplier_Credit_Notes → Vendors, Purchase_Orders, Goods_Receipts
Invoices → Projects, Accounts
Delivery_Challans → Projects, Accounts
BOM → Inventory_Items (Finished Item)
Item_Warehouse_Stock → Inventory_Items, Warehouses
Vendor_Bills → Vendors, Purchase_Orders, Goods_Receipts
Payments → Vendor_Bills (AP), Invoices (AR), Vendors, Accounts
Supplier_Credit_Notes → Vendor_Bills (via Bill_Reference)
Currency_Rates (standalone — no inbound lookups)
Accounting_Periods (lookup target from all financial forms)
Audit_Log (standalone — write-only via Deluge)
Expenses (enhanced) → Expense_Allocations → Budget_Components
Budget_Plans (enhanced) → Budget_Revisions → Budget_Components
Customer_Credit_Notes → Accounts, Invoices
Manufacturing_Orders → Inventory_Items (Production_Item + Component_Item), BOM, Projects, Warehouses
Sales_Orders → Accounts, Projects
SO_Line_Items → Inventory_Items
CCN_Line_Items → Inventory_Items
MO_Components → Inventory_Items
```

---

**Document Prepared By:** ITOTCloud Systems Pvt. Ltd.
**Confidential — © 2026 — All Rights Reserved**
