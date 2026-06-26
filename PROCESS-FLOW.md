# Process Flow Diagrams — Chemsol Zoho Creator

> Text-based process flows for key business cycles. These describe the end-to-end sequence of events, decision points, and system interactions.

---

## 1. Procurement Cycle: PR → PO → GRN

This is the primary purchase process covering material procurement for production.

### High-Level Flow

```
Start
  │
  ▼
[Create PR] ──► [PR Approval] ──► [Rate Comparison] ──► [PO Creation] ──► [PO Approval]
                                                                              │
                                                                              ▼
                                                                        [PO to Supplier]
                                                                              │
                                                                              ▼
                                                                        [GRN Creation]
                                                                              │
                                                                              ▼
                                                                        [QC Inspection]
                                                                              │
                                                                              ▼
                                                                        [Stock Update]
                                                                              │
                                                                              ▼
                                                                           End
```

### Step-by-Step

#### 1.1 Purchase Requisition (PR)

```
[Production / R&D identifies material need]
    │
    ▼
[Create PR in Creator]
    │  - PR Number: Auto-generated
    │  - PR Date: Today's Date
    │  - Department: Auto from login (Production / R&D)
    │  - Line Items: Item Code/Name (auto-fetch), Qty, UOM, Lead Time
    │
    ▼
[PR Submitted for Approval]
    │
    ├── Approved ──► PR status = "Approved" ──► Available for Rate Comparison
    │
    └── Rejected ──► PR status = "Rejected" ──► Notify requester with reason
```

**Decision Point**: PR Approval
- If Amount < ₹50,000: Purchase Manager can approve
- If Amount > ₹50,000: Director / Admin approval required

#### 1.2 Rate Comparison

```
[Approved PR available]
    │
    ▼
[Create Rate Comparison]
    │  - Date: Today's Date
    │  - Link PR Reference
    │  - Fetch line items from PR
    │
    ▼
[Quote from Suppliers 1-5]
    │  - Select supplier from dropdown
    │  - Enter Price and Credit terms
    │
    ▼
[Finalise Supplier & Rate]
    │
    ├── Supplier Finalised ──► Create PO reference
    │
    └── No suitable rate ──► PR re-scoped or sent for re-negotiation
```

#### 1.3 Purchase Order (PO)

```
[Finalised Rate Comparison]
    │
    ▼
[Create PO]
    │  - RM Type: Coding / Non-coding (determines PO series)
    │  - PO Number: Auto (RMWAD-xxx / RM-xxx)
    │  - PO Date: Today's Date
    │  - Supplier: From Rate Comparison (auto-fetch details)
    │  - Line Items: From Rate Comparison
    │  - Bill To / Ship To
    │  - Delivery Date, Payment Terms
    │  - Scope of Transport (Supplier/Own)
    │  - Mode of Transport
    │
    ▼
[PO Approval]
    │
    ├── Approved (within approver limit) ──► PO status = "Issued"
    │
    └── Escalated (exceeds limit) ──► Director approval
              │
              ▼
         PO status = "Issued" ──► PO sent to supplier (email/print)
```

**PO Auto-Numbering Rules**:
| RM Type | Prefix | Access |
|---------|--------|--------|
| Coding | RMWAD- | Purchase dept only |
| Non-coding | RM- | Purchase dept |

#### 1.4 Goods Receipt Note (GRN)

```
[Supplier delivers material]
    │
    ▼
[Create GRN against PO]
    │  - GRN Date: Today's Date
    │  - PO Number: Link to PO (auto-fetch supplier, items)
    │  - Vehicle Number
    │  - Warehouse: Select from master list
    │  - Invoice Number / Date
    │
    ▼
[Enter Received Quantities]
    │  - Checkbox per item (for partial GRN)
    │  - Received Qty (can be <= Ordered Qty)
    │  - Packing Quality
    │
    ▼
[Post GRN]
    │
    ├── GRN Posted ──► GRN Number generated
    │                 ├── Stock updated
    │                 ├── QC Pending flag set
    │                 └── Transport costs recorded (if in PO scope)
    │
    └── Draft saved ──► Can edit and post later
```

**Decision Point**: Partial GRN
- User checks only some items → partial GRN against PO
- Remaining items stay open for future GRN

**Transport Subform** (visible only if PO scope = "Own"):
- Transporter Name
- Transportation Charges
- Local Transport
- Loading/Unloading

---

## 2. Quality Control Flow

```
[Material received via GRN]
    │
    ▼
[QC status = "Pending"]
    │
    ▼
[QC Inspector creates QC record]
    │  - QC Number: Auto-generated
    │  - Date: Today's Date
    │  - Link GRN Number (auto-fetch supplier + items)
    │
    ▼
[Perform Tests per Item]
    │  - Inspection Date
    │  - Viscosity Result
    │  - Density Result
    │  - Color Result
    │  - Moisture Result
    │
    ▼
[Enter QC Status]
    │
    ├── Pass ──► Accepted Qty = Received Qty
    │            Rejected Qty = 0
    │            Stock fully usable
    │
    ├── Fail ──► Rejected Qty = Received Qty
    │            Accepted Qty = 0
    │            Stock quarantined / returned
    │
    └── Partial ──► Accepted Qty < Received Qty
                    Rejected Qty > 0
                    Partial stock usable, partial returned
```

---

## 3. Material Requisition & Issue (MR → MIS)

```
[Production needs material]
    │
    ▼
[Create Material Requisition (MR)]
    │  - MR Number: Auto-generated
    │  - MR Date: Today's Date
    │  - Requisition Type: Dropdown (e.g. Production / R&D)
    │  - Batch Number: Optional link
    │  - Department: Auto from login
    │  - Requested By: Employee Name
    │  - Priority: Dropdown
    │  - Line Items: Item Code (auto-fetch Name, Category, UOM, Available Stock)
    │  - Required Qty (must be ≤ Available Stock?)
    │
    ▼
[MR Approved by Production Manager]
    │
    ├── Approved ──► MR sent to Store for processing
    │
    └── Rejected ──► Notify requester
              │
              ▼
[Store processes MR]
    │
    ▼
[Issue Material via MIS]
    │  - Link MR Number
    │  - MIS Number: Auto-generated against MR
    │  - Actual issued quantities (may differ from requested)
    │  - Stock reduced on posting
    │
    ▼
[MIS Posted ──► Inventory updated]
```

**Decision Point**: Stock Availability
- If Required Qty > Available Stock → flag "Shortage" on MR
- Partial issue possible

---

## 4. Sales & Work Order Flow

```
[Customer enquiry / order received]
    │
    ▼
[Select Order Type]
    │
    ├── Supply+Apply ──► Work Order (WO)
    │                     - System Code / System Name (from System Master)
    │                     - Thickness, Area, UOM, Rate, Amount
    │                     - Site details, Project Type
    │                     - Transportation, Warranty, Commission
    │
    └── Supply Only ───► Sales Order (SO)
                          - FG Name, Qty, UOM, Rate, Amount
                          - Billing / Shipping address
                          - Transportation scope
    │
    ▼
[Enter Customer Details]
    │  - Customer Code (auto-fetch Client Org Name, Contact, GST, PAN, Address)
    │  - Contact Person, Contact No, Email
    │
    ▼
[Set Terms]
    │  - Payment Terms
    │  - Transportation Scope + Amount
    │  - Lead Time (Days)
    │  - Warranty (if Supply+Apply)
    │  - Commission (checkbox: Percentage / Fix Amount)
    │  - Attach PO/BOQ (multiple files)
    │
    ▼
[Save SO/WO ──► Status = "Active"]
    │
    ├── Supply+Apply ──► Links to Project Management for execution
    │
    └── Supply Only ───► Links to Production Planning (if manufacturing)
                          Or direct dispatch from store (if FG in stock)
```

---

## 5. Production Flow

```
[Sales Order / Work Order received]
    │
    ▼
[Production Planning]
    │  - Planning No, Date, Period, Plant
    │  - Planner Name
    │  - Total SO/WO Qty vs FG Stock Available
    │
    ▼
[Create Production Order]
    │  - Authorises production of specific quantity
    │
    ▼
[Create Batch Manufacturing Record]
    │  - BOM based material consumption
    │  - RM consumption tracking (actual vs planned)
    │  - Yield calculation
    │
    ▼
[Create Material Requisition (MR)]
    │
    ▼
[Material Issued (MIS)]
    │
    ▼
[RM Consumption Entry]
    │  - Record actual RM consumed
    │
    ▼
[Packing Entry]
    │  - FG quantity packed
    │
    ▼
[FG Receiving in Store]
    │  - FG stock updated
    │
    ▼
[Dispatch to customer / site]
```

---

## 6. Project Execution Flow

```
[Work Order (Supply+Apply) created]
    │
    ▼
[Create Project]
    │  - Project ID: Auto
    │  - Project Name, Address, Manager
    │  - Execution Base: Area Basis / Day Basis
    │  - Start Date, End Date, Project Cost
    │  - Systems (Subform): System Name, Area, UOM
    │
    ▼
[Define Tasks (5 Buckets)]
    │
    ├── 1. Transportation
    │      ├── Budget (top-level)
    │      └── Sub-tasks: Dispatch 1/2/3+
    │          ├── From / To
    │          └── Transport Charges
    │
    ├── 2. Application/Execution (if Area Basis)
    │      └── Sub-tasks A/B/C+
    │          ├── Area
    │          ├── Cost
    │          └── MP (Manpower)
    │
    ├── 3. Manpower (if Day Basis)
    │      ├── Manpower Budget
    │      └── Manpower Count
    │
    ├── 4. Tools
    │      └── Budget for Tools
    │
    └── 5. Additional Expenses
    │
    ▼
[Project Execution & Monitoring]
    │  - Dashboard: Open Projects, Active PO's
    │  - Running Status updates
    │  - Track margins vs budget
    │  - Issues logging
    │
    ▼
[Project Completion]
    │  - Execution Target vs Achieve
    │  - Actual Manpower Cost vs Budget
    │  - Actual Transportation vs Budget
    │  - Loading/Unloading charges
    │
    ▼
[Project Closed]
```

### Execution Mode Decision

```
Execution Base?
    │
    ├── Area Basis ──► Task 2 (Application) uses Area/Cost/MP per sub-task
    │                   Task 3 (Manpower) may not apply separately
    │
    └── Day Basis ───► Task 3 (Manpower) uses Budget + Count
                         Task 2 may use day-rate costing
```

---

## 7. Inventory Flow (Stock Movement)

```
[Stock In]
    │
    ├── Via GRN ──► RM/PM received from supplier
    │                Stock added to warehouse
    │                QC pending → QC pass → Available
    │
    ├── Via FG Receiving ──► FG from production
    │                        Stock added to FG store
    │
    └── Via Material Return ──► Unused material returned from production
                               Stock added back
    │
    ▼
[Stock Out]
    │
    ├── Via MIS ──► Material issued to production
    │                Stock reduced from RM store
    │
    ├── Via Material Handover ──► Stock transferred between stores / to site
    │
    └── Via Dispatch ──► FG dispatched to customer against SO
    │
    ▼
[Stock Ledger]
    ├── Every transaction recorded
    ├── Real-time stock balance per item per store
    └── Reorder alert when stock < Min Stock
```

---

## 8. Key System Integrations

```
Item Master ◄──► PR
    │              │
    ▼              ▼
Supplier Master ◄──► PO ◄──► GRN ◄──► QC
                        │
                        ▼
Rate Comparison ◄──► PR
                        │
                        ▼
System Master ◄──► SO/WO (Supply+Apply mode)
    │
    ▼
BOM Master ◄──► Batch Manufacturing Record
    │
    ▼
MR ◄──► MIS ◄──► Stock Ledger
    │
    ▼
Project ──► Tasks (Transport, Application, Manpower, Tools, Expenses)
```

---

## 9. Report Generation Triggers

| Report | Data Sources | Trigger |
|--------|-------------|---------|
| Open PO Register | PO (status = Issued, not fully GRNed) | On-demand filter |
| PO vs GRN Pending | PO + GRN (qty comparison) | On-demand |
| Vendor Performance | PO + GRN + QC (delivery + quality scores) | Periodic |
| Daily Production Report | BMR + Packing Entry | Daily |
| BOM vs Actual Consumption | BOM + RM Consumption Entry | Per batch close |
| Production Loss Report | Planned vs Actual yield | Per batch close |
| Project Margins | Project Budget vs Actual costs | On-demand |
| Material Consumption Report | MIS + BMR | Periodic |
