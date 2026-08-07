# Roadmap: Project Budget Tracking & Inventory Management

## Overview

ITOTCloud's Zoho Creator-based project budget tracking and inventory management system. Starting from a complete implementation blueprint (19 modules, 28 Deluge automations) through delivery phases, then extending with AI-powered budget intelligence, predictive analytics, and smart procurement.

## Phases

- [ ] **Phase 1A: Foundation Modules** — Vendor Management, Project Master, Warehouses, Inventory Master
- [ ] **Phase 1B: Budget & Stock Engine** — Budget Planning, Budget Components, Inventory Transactions
- [ ] **Phase 1C: Spend & Requests** — Expense Management, Purchase Requisition
- [ ] **Phase 1D: Procurement Cycle** — Budget Approval, Purchase Orders (enhanced), Goods Receipt (enhanced), Supplier Credit Notes, Transfer Orders
- [ ] **Phase 1E: Revenue & Manufacturing** — BOM, Delivery Challan, Invoicing
- [ ] **Phase 1F: Reports & Dashboards** — Project P&L, KPIs, budget alerts
- [ ] **Phase 2: AI Integration — Smart Budget Intelligence** — AI-powered budget forecasting, anomaly detection, smart procurement recommendations, and natural language reporting

## Phase Details

### Phase 1A: Foundation Modules
**Goal**: Core data scaffolding — Vendors, Projects, Warehouses, Inventory Items
**Depends on**: Nothing
**Success Criteria**:
  1. Vendors (with contacts/documents), Projects, Warehouses, and Inventory Items forms exist with specs from IMPLEMENTATION_PLAN.md
  2. Auto-numbering works for Project Code, SKU, and Warehouse Code
  3. Lookup relationships are configured (Project → Account/Vendors)
**Plans**: 1 plan

Plans:
- [ ] 01A-01: Build foundation modules in Zoho Creator console

### Phase 1B: Budget & Stock Engine
**Goal**: Budget planning with component breakdown + inventory stock tracking
**Depends on**: Phase 1A
**Success Criteria**:
  1. Budget Plans and Budget Components forms capture per-project budgets
  2. Inventory Transactions update Item_Warehouse_Stock correctly
  3. Budget validation (sum components ≤ total budget) enforces correctly
**Plans**: 1 plan

### Phase 1C: Spend & Requests
**Goal**: Expense logging and purchase requisition workflow
**Depends on**: Phase 1B
**Success Criteria**:
  1. Expenses track actual spend against budget components
  2. Purchase Requisitions flow through multi-stage approval
  3. Overrun detection triggers approval workflow
**Plans**: 1 plan

### Phase 1D: Procurement Cycle
**Goal**: Complete procurement — approvals, POs, goods receipt, supplier credits, transfers
**Depends on**: Phase 1C
**Success Criteria**:
  1. Purchase Orders lifecycle works (Draft → Open → Closed)
  2. PO Receipt_Status auto-calculated per line item from GRN aggregations
  3. Goods Receipt auto-creates Stock In transactions, supports credit tracking
  4. Supplier Credit Notes track defective/rejected items post-QA/QC; auto-create Return to Vendor on disposition; link to PO
  5. Transfer Orders generate paired Stock Out/In
**Plans**: 1 plan

### Phase 1E: Revenue & Manufacturing
**Goal**: Invoicing, delivery challans, and bill of materials
**Depends on**: Phase 1D
**Success Criteria**:
  1. Invoices track revenue and sync with project totals
  2. Delivery Challans deduct stock on Ship
  3. BOM calculates total manufacturing cost
**Plans**: 1 plan

### Phase 1F: Reports & Dashboards
**Goal**: Executive KPIs, budget vs actual, stock alerts, project P&L
**Depends on**: Phase 1E
**Success Criteria**:
  1. Executive dashboard shows Budget Utilization %, Open PO Value, Inventory Value
  2. Budget vs Actual report is available per project
  3. Scheduled daily cron sends budget alerts at 80/90/100%
**Plans**: 1 plan

### Phase 2: AI Integration — Smart Budget Intelligence
**Goal**: AI-powered budget forecasting, anomaly detection, smart procurement recommendations, and natural language querying over project financials
**Depends on**: Phase 1F
**Success Criteria**:
  1. AI generates 30/60/90-day budget burn forecasts per project from historical data
  2. Anomaly detection flags unusual spending patterns vs. historical baselines
  3. Smart procurement recommends optimal reorder quantities and timing
  4. Natural language interface answers budget/project questions (e.g., "Which project is over budget?")
  5. System produces plain-English weekly budget summaries for project managers
**Plans**: TBD (to be determined during AI-SPEC)

## Progress

**Execution Order:**
Phases execute in numeric order: 1A → 1B → 1C → 1D → 1E → 1F → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1A. Foundation Modules | 0/1 | Not started | - |
| 1B. Budget & Stock Engine | 0/1 | Not started | - |
| 1C. Spend & Requests | 0/1 | Not started | - |
| 1D. Procurement Cycle | 0/1 | Not started | - |
| 1E. Revenue & Manufacturing | 0/1 | Not started | - |
| 1F. Reports & Dashboards | 0/1 | Not started | - |
| 2. AI Integration — Smart Budget Intelligence | 0/TBD | Not started | - |
