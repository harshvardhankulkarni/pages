# Business Requirements Document — Chemsol Zoho Creator Application

> **Client**: Chemsol (Industrial Flooring Solutions — Epoxy, PU, Anti-Static, ESD)
> **Prepared by**: ITOTCloud Systems Pvt. Ltd.
> **Version**: 1.0

---

## 1. Executive Summary

Chemsol requires a **Zoho Creator** application to digitise and streamline its business operations across Admin, Purchase, Store, Production, Sales, Project Management, and Quality Control departments. The application replaces manual/offline tracking with a centralised digital system covering procurement, inventory, production, project execution, sales orders, and quality assurance.

---

## 2. Scope

### In Scope

| Department | Modules |
|-----------|---------|
| Admin | Item Master, System Master, BOM Master, Supplier Master, Customer Master, Store Master, Bin Location Master, User Access, Approval Matrix |
| Purchase | Purchase Requisition (PR), Rate Comparison, Purchase Order (PO), PO Amendment, Goods Receipt Note (GRN) |
| Store & Logistics | GRN, Material Issue Slip (MIS), Material Return, Material Handover, FG Receiving, Vehicle & Transport, Stock Management |
| Production | Production Planning, Production Order, Batch Manufacturing Record (BMR), Material Requisition (MR), RM Consumption Entry, Packing Entry |
| Sales | Sales/Work Order (SO/WO) — Supply+Apply and Supply-only modes |
| Project Management | Create/Edit Project, Task Management (Transport, Application, Manpower, Tools, Additional Expenses) |
| Quality Control | QC/QA for RM — Viscosity, Density, Color, Moisture testing |
| Finance | Payment tracking, Customer/Supplier financial data |
| Reports | Department-wise reports (Purchase, Store, Production, Sales, Project, QC) |

### Out of Scope

- Payroll processing
- Fixed asset management
- HR/employee lifecycle management

---

## 3. Module Specifications

### 3.1 Admin

#### 3.1.1 Item Master

**Purpose**: Central repository of all Raw Materials (RM), Packing Materials (PM), Finished Goods (FG), and consumables.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Category of Purchase Item | Dropdown | Yes | — |
| Purchase Item Code | Text | Yes | Auto-generated / Manual |
| Purchase Item Name | Text | Yes | — |
| UOM | Dropdown | Yes | Unit of Measure |
| HSN Code | Text | Yes | — |
| GST % | Decimal | No | — |
| Min Stock | Number | Yes | Reorder trigger |
| Max Stock | Number | No | — |
| Standard Rate | Decimal | No | — |
| Preferred Supplier | Lookup | No | Link to Supplier Master |
| Lead Time | Number (Days) | No | — |

**Access**: Purchase, Stores, Production, QC — Full. Sales — View only.

**Reports**: Purchase Item Master (full listing with filters)

#### 3.1.2 System Master

**Purpose**: Define flooring systems (e.g. 3mm Epoxy, 4mm PU, Demarcation, etc.)

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| System Code | Text | Yes | Auto-generated (EP-xxx, PU-xxx, DEM-xxx, etc.) |
| System Name | Text | Yes | — |
| Thickness | Text | No | — |
| Description | Multi-line | No | — |
| UOM | Dropdown | Yes | Sq. Ft. / Sq. Mtr. |

**Access**: Sales, Projects, Production

**System Code Prefixes**:
| Code | Type |
|------|------|
| EP | Epoxy Flooring |
| PU | Polyurethane Flooring |
| DEM | Demarcation Line |
| NUM | Numbering |
| ARR | Arrow Marking |
| ANTI | Anti-Static Flooring |
| ESD | ESD Flooring |
| FIL | Filling |
| COV | Coving |

#### 3.1.3 BOM Master

**Purpose**: Material consumption per system/product. Defines what RM/PM quantities are needed per unit of FG.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| System Code | Lookup | Yes | From System Master |
| System Name | Auto-fetch | Yes | From System Code |
| Item Code | Lookup | Yes | From Item Master |
| Item Name | Auto-fetch | Yes | From Item Code |
| Quantity | Decimal | Yes | Per unit of system |
| UOM | Auto-fetch | Yes | From Item Code |

**Access**: Production, QC, Costing

#### 3.1.4 Supplier Master

**Purpose**: Vendor/supplier details for procurement.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Supplier Code | Text | Yes | Auto-generated |
| Supplier Name | Text | Yes | — |
| Supplier Type | Dropdown | No | — |
| GSTIN | Text | Yes | — |
| PAN No | Text | Yes | — |
| Contact Person | Text | Yes | — |
| Mobile No | Text | Yes | + Alternate field |
| Email ID | Text | Yes | — |
| Address | Multi-line | Yes | — |
| Pincode | Text | No | — |
| Bank Name | Text | Yes | — |
| Account No | Text | Yes | — |
| IFSC Code | Text | Yes | — |
| Payment Terms | Text | Yes | — |
| Credit Days | Number | Yes | — |

**Access**: Purchase, Finance

#### 3.1.5 Customer Master

**Purpose**: Customer/site details.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Customer Code | Text | Yes | Auto-generated |
| Client Org Name | Text | Yes | — |
| Contact Person | Text | Yes | — |
| Contact No | Text | Yes | — |
| Alt Contact No | Text | No | — |
| Email | Text | Yes | — |
| GST No | Text | Yes | — |
| PAN | Text | Yes | — |
| Regd Address | Multi-line | Yes | — |
| Billing Address | Multi-line | No | — |
| Shipping Address | Multi-line | No | — |

**Access**: Sales, Projects, Finance

#### 3.1.6 Store Master

**Purpose**: Define physical store locations.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Store Code | Text | Yes | Auto-generated |
| Store Name | Text | Yes | — |
| Store Type | Dropdown | Yes | RM / FG / QC / Site |
| Location | Text | No | — |

**Access**: Stores, Production

#### 3.1.7 Bin Location Master

**Purpose**: Rack/shelf/bin mapping within stores.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Store Name | Lookup | Yes | From Store Master |
| Rack No | Text | Yes | — |
| Shelf No | Text | Yes | — |
| Bin No | Text | Yes | — |

**Access**: Stores

#### 3.1.8 User Access & Approval Matrix

**Purpose**: Define user roles, department assignments, approvers, and approval limits (PI/PR/PO).

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| User Name | Lookup | Yes | From Zoho Creator users |
| Department | Dropdown | Yes | — |
| Role | Dropdown | Yes | — |
| PR Approval Limit | Currency | No | — |
| PO Approval Limit | Currency | No | — |

**Access**: All Departments (Admin only for editing)

---

### 3.2 Sales

#### 3.2.1 Sales/Work Order (SO/WO) Master

**Purpose**: Create Sales Orders (material only) or Work Orders (supply + apply with installation). Two modes selected at creation.

**Mode: Supply+Apply**
| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Date | Date | Yes | Today's Date |
| Employee Name | Text | No | Logged-in user |
| Customer Code | Lookup | No | From Customer Master |
| Client Org Name | Text | Yes | — |
| Contact Person | Text | Yes | — |
| Contact No | Text | Yes | — |
| Alt Contact No | Text | Yes | — |
| Email | Text | Yes | — |
| GST No | Text | Yes | — |
| PAN | Text | Yes | — |
| Regd Address | Multi-line | Yes | — |
| Work Order No | Text | Yes | Auto-generated |
| Work Order Date | Date | Yes | — |
| Site Name | Text | Yes | — |
| Site Address | Multi-line | Yes | — |
| Site Manager/Incharge | Text | No | — |
| Contact No | Text | No | — |
| Project Type | Dropdown | Yes | Industrial / Commercial |

**Line Items (Subform)**: System Code, System Name (Auto-fetch), Thickness, Area, UOM (Conditional dropdown), Rate, Amount

**Totals**: Total Work Order Amount, Payment Terms, Transportation Scope + Amount, Warranty, Is Proper System Required (checkbox), Lead Time (Days), Commission (checkbox — Percentage / Fix Amount + Amount), PO/BOQ Attachment (Multiple), Remark

**Mode: Supply only (Material Sales)**
| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Date | Date | Yes | Today's Date |
| Employee Name | Text | No | Logged-in user |
| Customer Code | Lookup | No | — |
| Client Org Name | Text | Yes | — |
| Contact Person | Text | Yes | — |
| Contact No | Text | Yes | — |
| Alt Contact No | Text | Yes | — |
| Email | Text | Yes | — |
| GST No | Text | Yes | — |
| PAN | Text | Yes | — |
| Regd Address | Multi-line | Yes | — |
| Sales Order No | Text | Yes | Auto-generated |
| Sales Order Date | Date | Yes | — |
| Billing Address | Multi-line | Yes | — |
| Shipping Address | Multi-line | Yes | — |

**Line Items (Subform)**: FG Name, Quantity, UOM, Rate, Amount

**Totals**: Total Sales Order Amount, Payment Terms, Transportation Scope + Amount, Lead Time (Days), Remark, PO/BOQ Attachment (Multiple)

---

### 3.3 Purchase

#### 3.3.1 Purchase Requisition (PR)

**Purpose**: Internal request for materials from Production / R&D.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| PR Number | Text | Yes | Auto-generated |
| PR Date | Date | Yes | Today's Date |
| Reference | Text | No | — |
| Department | Text | Yes | As per user login (Production / R&D) |
| Approved By | Text | No | Approval workflow |

**Line Items (Subform)**:
| Field | Behavior |
|-------|----------|
| Sr | Auto-number |
| Item Code | Manual entry; auto-fetches Item Name |
| Item Name | Manual entry; auto-fetches Item Code |
| Qty | Manual entry |
| Item Description | Manual entry |
| UOM | Auto-fetch from Item Master |
| Lead Time | Auto-fetch from Item Master (Days) |

**Notes**:
- Item Code OR Item Name — enter either, the other auto-fills
- UOM auto-fetched from Item Master
- Lead Time in days

#### 3.3.2 Rate Comparison

**Purpose**: Compare supplier rates before issuing PO.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Date | Date | Yes | Today's Date |
| PR Reference No | Lookup | Yes | From PR Master |
| Product No | Text | Yes | From PR line item |
| Product Name | Text | Yes | From PR line item |
| Supplier 1-5 | Dropdown | No | From Supplier Master |
| Price (per supplier) | Currency | No | — |
| Credit (per supplier) | Text | No | — |
| Finalised Supplier | Dropdown | Yes | Selected from quoted suppliers |
| Final Rate | Currency | Yes | — |
| PO No | Lookup | No | After PO creation |
| PO Release Date | Date | No | — |

#### 3.3.3 Purchase Order (PO)

**Purpose**: Formal purchase order to supplier.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| RM Type | Dropdown | Yes | Coding / Non Coding |
| PO Number | Text | Yes | Auto-generated (RM for Non-coding, RMWAD for Coding) |
| PO Date | Date | Yes | Today's Date |
| Supplier Code | Lookup | Yes | From Supplier Master |
| Supplier Name | Auto-fetch | Yes | From Supplier Code |
| PR Reference | Lookup | No | From PR Master |
| Bill To | Dropdown | Yes | — |
| Ship To | Dropdown | Yes | — |

**Line Items (Subform)**:
| Field | Behavior |
|-------|----------|
| Sr No | Auto-number |
| Item Code | From Item Master |
| Item Name | Auto-fetch + sub-textbox for description |
| HSN | Auto-fetch |
| Quantity | Manual |
| UOM | Auto-fetch |
| Rate | Manual |
| Basic Amount | Calculated (Qty × Rate) |
| GST % | Auto-fetch from Item Master |
| GST Amount | Calculated |
| Total Amount | Calculated |

**Totals**: Basic, CGST, SGST, IGST, Total Amount (in words)

**Other Fields**: Delivery Date, Payment Terms, Scope of Transport (Supplier/Own), Mode of Transport, T&C (standard purchase terms)

**Auto-numbering**: Separate PO series — `RM-` for Non-coding materials, `RMWAD-` for Coding materials (coding materials accessible only by Purchase dept.)

#### 3.3.4 PO Amendment

**Purpose**: Amend an existing PO (quantity, rate, delivery).

**Access**: Purchase dept.

#### 3.3.5 Goods Receipt Note (GRN)

**Purpose**: Record receipt of materials against PO.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| GRN Date | Date | Yes | Today's Date |
| PO Number | Lookup | Yes | From PO Master |
| Supplier Code | Auto-fetch | Yes | From PO |
| Supplier Name | Auto-fetch | Yes | From PO |
| Vehicle Number | Text | Yes | — |
| Warehouse | Dropdown | Yes | Wadki w/h, Main w/h 1, Neelo w/h 2, Gurgaon, Bangalore, Client Site |
| If Client Site | Text | Conditional | Visible if Warehouse = Client Site |
| Invoice Number | Text | Yes | — |
| Invoice Date | Date | Yes | — |

**Line Items (Subform)**:
| Field | Behavior |
|-------|----------|
| Checkbox | Selection for partial GRN |
| Item Code | Auto-fill from PO |
| Item Name | Auto-fill from PO |
| Ordered Qty | Auto-fill from PO |
| Received Qty | Manual entry |
| QC Status | Pending / Pass / Fail (links to QC) |
| Packing Quality | Manual entry |

**Transport Subform** (visible if PO transport scope = Own):
| Field | Type |
|-------|------|
| Transporter Name | Text |
| Transportation Charges | Currency |
| Local Transport | Currency |
| Loading/Unloading | Currency |

**Key Logic**:
- Checkbox per line item allows **partial GRN**
- GRN number generated **after posting** (not on create)
- Stock updated after GRN posting
- GRN posting timestamp recorded in backend

---

### 3.4 Quality Control

#### 3.4.1 QC/QA Master (for RM)

**Purpose**: Quality inspection of received raw materials.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| QC Number | Text | Yes | Auto-generated |
| Date | Date | Yes | Today's Date |
| GRN Number | Lookup | Yes | From GRN Master |
| Supplier Name | Auto-fetch | Yes | From GRN |

**Line Items (Subform)**:
| Field | Behavior |
|-------|----------|
| Item No. | Auto-fetch from GRN |
| Item Name | Auto-fetch from GRN |
| Inspection Date | Manual |
| Viscosity Result | Text |
| Density Result | Text |
| Color Result | Text |
| Moisture Result | Text |
| Accepted Qty | Number |
| Rejected Qty | Number |
| Packaging Quality | Text |
| QC Status | Pass / Fail / Pending |

---

### 3.5 Store

#### 3.5.1 Material Requisition (MR)

**Purpose**: Request materials from store for production.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| MR Number | Text | Yes | Auto-generated |
| MR Date | Date | Yes | Today's Date |
| Requisition Type | Dropdown | Yes | — |
| Batch Number | Lookup | No | From Batch Manufacturing |
| Department | Text | Yes | Auto-fetch as per user login (Production / R&D) |
| Requested By | Text | Yes | Employee Name |
| Priority | Dropdown | Yes | — |

**Line Items (Subform)**:
| Field | Behavior |
|-------|----------|
| Sr No. | Auto-number |
| Item Code | Manual; auto-fetches rest |
| Item Name | Auto-fetch |
| Category | Auto-fetch |
| UOM | Auto-fetch |
| Available Stock | Auto-fetch from inventory |
| Required Qty | Manual |
| Remarks | Text |

#### 3.5.2 Material Issue Slip (MIS)

**Purpose**: Record actual issue of materials from store to production.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| MR No. | Lookup | Yes | From MR Master |
| MIS Number | Text | Yes | Auto-generated against MR |
| Date | Date | Yes | — |

#### 3.5.3 Material Return

**Purpose**: Record return of unused materials from production to store.

#### 3.5.4 Material Handover

**Purpose**: Record handover of materials between stores or to site.

#### 3.5.5 FG Receiving

**Purpose**: Record receipt of finished goods from production into store.

#### 3.5.6 Vehicle & Transport

**Purpose**: Record vehicle and transport details for logistics.

---

### 3.6 Production

#### 3.6.1 Production Planning

**Purpose**: Plan production runs based on SO/WO demands.

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Planning No | Text | Yes | Auto-generated |
| Planning Date | Date | Yes | — |
| Planning Period | Text | No | — |
| Plant | Text | No | — |
| Planner Name | Text | No | — |
| Status | Dropdown | No | — |
| Remarks | Text | No | — |
| Total SO/WO Qty | Number | No | — |
| FG Stock Available | Number | No | — |

#### 3.6.2 Production Order

**Purpose**: Authorise production of specific quantity of a product.

**Fields**: Order No, Order Date, Product/System, Planned Qty, Status, etc.

#### 3.6.3 Batch Manufacturing Record (BMR)

**Purpose**: Track RM/PM consumption for each production batch.

**Fields**: Batch No, Production Order Ref, RM/PM consumed (from BOM), Actual vs Planned consumption, Yield, Operator details.

#### 3.6.4 RM Consumption Entry

**Purpose**: Record actual RM consumption during production.

#### 3.6.5 Packing Entry

**Purpose**: Record packing details and FG output.

---

### 3.7 Project Management

#### 3.7.1 Create Project

| Field | Type | Required | Behavior |
|-------|------|----------|----------|
| Project ID | Text | Yes | Auto-generated |
| Project Name | Text | Yes | — |
| Address | Multi-line | Yes | — |
| Project Manager | Lookup | Yes | Employee |
| Execution Base | Dropdown | Yes | Area Basis / Day Basis |
| Start Date | Date | Yes | — |
| End Date | Date | Yes | — |
| Project Cost | Currency | Yes | — |
| Systems | Subform | Yes | System, Area, UOM |
| Description | Multi-line | No | — |
| Adjustments | Currency | No | — |

**Task Structure** (5 buckets):

| # | Task | Details |
|---|------|---------|
| 1 | Transportation | Budget + Sub-tasks (Dispatch 1/2/3+ : From, To, Transport Charges) |
| 2 | Application/Execution | Sub-tasks per area (if Area Basis: Area, Cost, MP) |
| 3 | Manpower | Budget + Count (if Day Basis) |
| 4 | Tools | Budget for Tools |
| 5 | Additional Expenses | Miscellaneous costs |

**Dashboard Metrics**:
- Open Projects
- Active PO's
- Running Status
- Project Margins
- Issues
- Execution Target vs Achieve
- Manpower Cost Monthly
- Transportation Monthly
- Loading/Unloading Charges

**Sub-modules**: Machinery & Equipments (Add/Search/Records), Labour (Manpower Cost/Count)

---

### 3.8 Reports

#### Purchase Department
- Purchase Item Master, PR, PO, PO Amendment, GRN
- Open PO Register
- PO vs GRN Pending
- Vendor Performance
- Purchase by Item Group
- Price Comparison Report
- Transportation Reports

#### Store Department
- Store Master, Material Issue, Material Return
- FG Receiving, Vehicle & Transport

#### Production Department
- Daily Production Report
- Batch Manufacturing Report
- Production Order Status Report
- Material Consumption Report
- BOM vs Actual Consumption Report
- Production Loss Report
- FG Handover Report

---

## 4. Key Business Rules

1. **SO/WO Dual Mode**: Form switches fields based on Supply+Apply vs Supply-only selection
2. **PR→PO Flow**: PR created → Approved → Rate Comparison → PO issued
3. **Partial GRN**: Line-item checkbox enables receiving partial quantities
4. **Stock Update**: Inventory updated only after GRN posting (not on create)
5. **QC on GRN**: Each received batch requires QC testing before acceptance
6. **Auto-Numbering**: PO series differs by RM Type (Coding=RMWAD, Non-coding=RM)
7. **Execution Mode**: Project tasks differ based on Area Basis vs Day Basis
8. **Auto-Fetch**: Item Code ↔ Name, UOM, Supplier details, Stock levels auto-populated

---

## 5. System Codes

| Prefix | Product Type |
|--------|-------------|
| EP | Epoxy Flooring |
| PU | Polyurethane Flooring |
| DEM | Demarcation Line |
| NUM | Numbering |
| ARR | Arrow Marking |
| ANTI | Anti-Static Flooring |
| ESD | ESD Flooring |
| FIL | Filling |
| COV | Coving |

---

## 6. Departments

1. Purchase
2. Sales
3. Store & Logistics
4. Account & Finance
5. Admin
6. Project Coordinator
7. Project Manager 1
8. Project Manager 2

---

## 7. Assumptions & Dependencies

- Zoho Creator license covers all users across all departments
- India datacenter (`.in` domain) for all Zoho APIs
- Deluge workflows handle backend automation (auto-numbering, auto-fetch, stock updates)
- All forms accessible via Zoho Creator mobile app
- Approval workflows to be configured in Creator's native approval engine
- Reports built using Creator's Report/Page builder with Deluge for complex calculations
