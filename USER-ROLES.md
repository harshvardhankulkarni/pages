# User Roles & Permissions Matrix — Chemsol Zoho Creator

---

## 1. Role Definitions

| Role | Department | Description |
|------|-----------|-------------|
| Admin | Admin | System configuration, master data, user access |
| Purchase Manager | Purchase | PR approval, PO creation, supplier management |
| Purchase Executive | Purchase | PR initiation, rate comparison, GRN entry |
| Store Manager | Store & Logistics | Inventory oversight, material issues, FG receiving |
| Store Keeper | Store & Logistics | Daily store operations, material movement |
| Production Manager | Production | Production planning, batch management |
| Production Executive | Production | MR creation, RM consumption, packing |
| QC Inspector | QC | Quality inspection, test results entry |
| Sales Executive | Sales | SO/WO creation, customer management |
| Project Manager | Project Management | Project creation, tracking, task management |
| Project Coordinator | Project Management | Daily project updates, coordination |
| Finance Executive | Account & Finance | Payment tracking, financial reports |
| Viewer | All | Read-only access to assigned forms/reports |

---

## 2. Form-Level Permissions

> **Legend**: C=Create, R=Read, U=Update, D=Delete, V=View (read-only)

### 2.1 Admin

| Form | Admin | Purchase Manager | Store Manager | Production Manager | QC Inspector | Sales Executive | Project Manager | Finance | Viewer |
|------|-------|-----------------|---------------|-------------------|--------------|-----------------|-----------------|---------|--------|
| Item Master | CRUD | CRUD | CRUD | CRUD | CRUD | V | — | — | V |
| System Master | CRUD | — | — | CRUD | — | CRUD | CRUD | — | V |
| BOM Master | CRUD | — | — | CRUD | CRUD | — | — | V | V |
| Supplier Master | CRUD | CRUD | — | — | — | — | — | R | V |
| Customer Master | CRUD | — | — | — | — | CRUD | CRUD | R | V |
| Store Master | CRUD | — | CRUD | R | — | — | — | — | V |
| Bin Location Master | CRUD | — | CRUD | — | — | — | — | — | V |
| User Access | CRUD | — | — | — | — | — | — | — | — |
| Approval Matrix | CRUD | — | — | — | — | — | — | — | — |

### 2.2 Sales

| Form | Sales Executive | Project Manager | Finance | Admin | Viewer |
|------|----------------|-----------------|---------|-------|--------|
| Sales/Work Order (SO) | CRUD | CRUD | R | CRUD | V |
| Sales/Work Order (WO) | CRUD | CRUD | R | CRUD | V |

### 2.3 Purchase

| Form | Purchase Manager | Purchase Executive | Admin | Store Manager | Finance | Viewer |
|------|-----------------|-------------------|-------|---------------|---------|--------|
| Purchase Requisition (PR) | CRUD | CRUD | CRUD | R | R | V |
| Rate Comparison | CRUD | CRUD | CRUD | R | R | V |
| Purchase Order (PO) | CRUD | CRU (no D) | CRUD | R | R | V |
| PO Amendment | CRUD | CRUD | CRUD | R | R | V |
| GRN | CRUD | CRUD | CRUD | R | R | V |

### 2.4 Store

| Form | Store Manager | Store Keeper | Production Manager | Admin | Viewer |
|------|---------------|--------------|-------------------|-------|--------|
| Material Requisition (MR) | CRUD | CRUD | CRUD | CRUD | V |
| Material Issue Slip (MIS) | CRUD | CRUD | R | CRUD | V |
| Material Return | CRUD | CRUD | R | CRUD | V |
| Material Handover | CRUD | CRUD | R | CRUD | V |
| FG Receiving | CRUD | CRUD | R | CRUD | V |
| Vehicle & Transport | CRUD | CRUD | — | CRUD | V |

### 2.5 Production

| Form | Production Manager | Production Executive | Admin | Store Manager | Viewer |
|------|-------------------|---------------------|-------|---------------|--------|
| Production Planning | CRUD | CRUD | CRUD | R | V |
| Production Order | CRUD | CRUD | CRUD | R | V |
| Batch Manufacturing Record | CRUD | CRUD | CRUD | R | V |
| RM Consumption Entry | CRUD | CRUD | CRUD | R | V |
| Packing Entry | CRUD | CRUD | CRUD | R | V |

### 2.6 Quality Control

| Form | QC Inspector | Production Manager | Admin | Store Manager | Viewer |
|------|--------------|-------------------|-------|---------------|--------|
| QC/QA Master | CRUD | R | CRUD | R | V |

### 2.7 Project Management

| Form | Project Manager | Project Coordinator | Admin | Sales Executive | Finance | Viewer |
|------|----------------|---------------------|-------|-----------------|---------|--------|
| Create Project | CRUD | CRU | CRUD | R | R | V |
| Edit Project | CRUD | CRU | CRUD | R | R | V |
| Task Management | CRUD | CRUD | CRUD | — | — | V |
| Machinery & Equipment | CRUD | CRUD | CRUD | — | — | V |
| Labour Management | CRUD | CRUD | CRUD | — | R | V |

### 2.8 Reports

| Report | Department Owners | Admin | Finance | Viewer |
|--------|------------------|-------|---------|--------|
| Open PO Register | Purchase | CRUD | R | V |
| PO vs GRN Pending | Purchase, Store | CRUD | R | V |
| Vendor Performance | Purchase | CRUD | R | V |
| Purchase by Item Group | Purchase | CRUD | R | V |
| Price Comparison | Purchase | CRUD | R | V |
| Transportation Reports | Purchase, Store | CRUD | — | V |
| Daily Production Report | Production | CRUD | — | V |
| Batch Manufacturing Report | Production | CRUD | — | V |
| Production Order Status | Production | CRUD | — | V |
| Material Consumption Report | Production | CRUD | — | V |
| BOM vs Actual Consumption | Production | CRUD | — | V |
| Production Loss Report | Production | CRUD | — | V |
| FG Handover Report | Production, Store | CRUD | — | V |
| Project Margins | Project | CRUD | R | V |
| Execution Target vs Achieve | Project | CRUD | — | V |

---

## 3. Field-Level Permissions

### 3.1 Approval Workflow

| Step | Form | Initiator | Approver | Admin Override |
|------|------|-----------|----------|----------------|
| 1 | PR Approval | Purchase Executive | Purchase Manager / Department Head | Yes |
| 2 | Rate Comparison Finalisation | Purchase Executive | Purchase Manager | Yes |
| 3 | PO Approval | Purchase Executive | Purchase Manager (as per Approval Matrix limit) | Yes |
| 4 | QC Status Update | QC Inspector | QC Head / Production Manager | Yes |

### 3.2 Approval Limits

| Role | PR Approval Limit | PO Approval Limit |
|------|-------------------|-------------------|
| Purchase Executive | ₹0 (cannot approve) | ₹0 (cannot approve) |
| Purchase Manager | ₹50,000 | ₹2,00,000 |
| Director / Admin | No limit | No limit |

---

## 4. Dashboard Permissions

| Dashboard | Purchase | Store | Production | QC | Sales | Project | Finance | Admin |
|-----------|----------|-------|------------|----|-------|---------|---------|-------|
| Purchase Dashboard | Full | V | — | — | — | — | V | Full |
| Store Dashboard | — | Full | R | — | — | — | — | Full |
| Production Dashboard | — | — | Full | R | — | — | — | Full |
| Project Dashboard | — | — | — | — | — | Full | R | Full |
| Sales Dashboard | — | — | — | — | Full | R | R | Full |

---

## 5. Security Rules

### 5.1 Record-Level Access

| Module | Rule |
|--------|------|
| PR | Users see only their department's PRs; Purchase Manager sees all |
| PO | Purchase sees all; others see only linked to their department |
| MR | Production sees own; Store sees all for issue processing |
| Project | Project Manager sees own; Admin sees all |
| GRN | Purchase sees all; Store sees warehouse-specific records |

### 5.2 Restricted Fields

| Form | Field | Restricted To |
|------|-------|--------------|
| PO | Rate, Basic Amount, GST | Purchase Manager, Admin, Finance |
| Supplier Master | Bank Account, IFSC | Purchase Manager, Admin, Finance |
| SO/WO | Rate, Amount, Commission | Sales Manager, Admin |
| Project | Project Cost | Project Manager, Admin |

### 5.3 Action Restrictions

| Action | Rule |
|--------|------|
| Delete PO | Only Admin; never after GRN created |
| Delete Project | Only Admin; soft delete preferred |
| Amend PO Rate | Purchase Manager + Admin, only before GRN |
| Override QC Status | QC Head or Admin only |
| Modify Item Master Rate | Purchase Manager + Admin only |
