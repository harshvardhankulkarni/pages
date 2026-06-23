# Testing Guide — Project Budget Tracking & Inventory Management

After completing each build phase in the Zoho Creator console, run the corresponding tests below before proceeding to the next phase.

---

## How to Use This Guide

1. Build Phase 1A in the Zoho Creator console
2. Return here, run all **Phase 1A** test scenarios
3. Fix any failures before moving on
4. Build Phase 1B, test Phase 1B, and so on
5. After Phase 1F, run the **Integration Test** to verify end-to-end flow

Each test section lists:
- **Modules to test** — which forms are involved
- **Prerequisites** — data that must exist before testing
- **Test scenarios** — numbered steps with sample data
- **Expected results** — what should happen after each step
- **Edge cases** — failure conditions to verify

---

## Phase 1A — Vendors, Accounts, Projects, Warehouses, Inventory Items

### Modules to Test
| Module | API Name | Subforms |
|--------|----------|----------|
| Vendors | `Vendors` | `Vendor_Contacts`, `Vendor_Documents` |
| Accounts | `Accounts` | `Account_Contacts`, `Account_Documents` |
| Projects | `Projects` | — |
| Warehouses | `Warehouses` | — |
| Inventory Items | `Inventory_Items` | `Item_Warehouse_Stock` |

### Prerequisites
None — these are the foundation forms.

### Test Data Preparation

Create these records before running test scenarios:

| Record | Data |
|--------|------|
| Warehouse 1 | Name: `Main Warehouse`, Status: `Active` |
| Warehouse 2 | Name: `Secondary Store`, Status: `Active` |
| Warehouse 3 | Name: `Returns Bay`, Status: `Active` |

### Test Scenarios

---

#### TC-1A-01: Create Vendor with Contacts and Documents

**Steps:**
1. Open `Vendors` form
2. Enter: Vendor Name = `TechSupply Co.`, Email = `orders@techsupply.com`, Phone = `+1-555-0100`
3. Payment Terms = `Net 30`, Currency = `USD`, Tax ID = `GST12345`, Status = `Active`
4. In `Vendor_Contacts` subform, add row:
   - Salutation = `Mr`, First Name = `Raj`, Last Name = `Patel`, Email = `raj@techsupply.com`
   - Check `Is Primary`
5. Add another contact:
   - Salutation = `Ms`, First Name = `Priya`, Last Name = `Sharma`, Email = `priya@techsupply.com`
6. In `Vendor_Documents` subform, upload a sample file (any PDF/image), set Document Name = `GST Certificate`
7. Submit

**Expected:**
- Record saved with auto-generated Vendor ID
- Both contacts visible when you open the record
- Uploaded document accessible from the record

**Edge Cases:**
- Submit with blank Vendor Name → alert `Vendor Name is required.`
- Add 5+ contacts — all should save
- Upload file >5MB — should still upload (Zoho Creator handles file storage)

---

#### TC-1A-02: Create Second Vendor

**Steps:**
1. Create Vendor: Vendor Name = `Logistics Pro`, Email = `info@logisticspro.com`
2. Add one contact: First Name = `Amit`, Last Name = `Verma`, Is Primary = Yes
3. Submit

**Expected:**
- Record saved. Both vendors (TechSupply Co., Logistics Pro) visible in reports.

---

#### TC-1A-03: Create Account with Contacts and Documents

**Steps:**
1. Open `Accounts` form
2. Enter: Account Name = `ABC Manufacturing`, Email = `billing@abcmfg.com`
3. Payment Terms = `Net 45`, Currency = `USD`, Status = `Active`
4. In `Account_Contacts` subform, add:
   - Salutation = `Mr`, First Name = `Vikram`, Last Name = `Singh`, Email = `vikram@abcmfg.com`, Is Primary = Yes
5. In `Account_Documents` subform, upload a file, Document Name = `Signed MSA`
6. Submit

**Expected:**
- Record saved with contacts and document

**Edge Cases:**
- Submit with blank Account Name → alert `Account Name is required.`

---

#### TC-1A-04: Create Second Account

**Steps:**
1. Create Account: Account Name = `XYZ Constructions`, Email = `info@xyzconstruct.com`
2. Add one contact: First Name = `Neha`, Last Name = `Gupta`, Is Primary = Yes
3. Submit

**Expected:**
- Record saved. Both accounts visible in lookup lists.

---

#### TC-1A-05: Create Project

**Steps:**
1. Open `Projects` form
2. Enter: Project Name = `Office Renovation 2026`, Account = `ABC Manufacturing`
3. Start Date = `01-Jun-2026`, End Date = `31-Dec-2026`
4. Project Manager = select yourself (any user), Total Approved Budget = `50000`
5. Status = `Active`
6. Submit

**Expected:**
- Project Code auto-generated as `PROJ-0001`
- Account lookup shows `ABC Manufacturing`
- Record saved

**Edge Cases:**
- Set End Date before Start Date → alert `End Date must be after Start Date.`
- Leave Project Name blank → alert from required field validation
- Create Project without Account — should be allowed (Account is optional)

---

#### TC-1A-06: Create Second Project

**Steps:**
1. Create: Project Name = `Warehouse Automation`, Account = `XYZ Constructions`
2. Start = `01-Jul-2026`, End = `30-Jun-2027`, Budget = `75000`
3. Status = `Active`
4. Submit

**Expected:**
- `PROJ-0002` generated

---

#### TC-1A-07: Inventory Item — Goods Type

**Steps:**
1. Open `Inventory_Items` form
2. Enter: Item Name = `Cement Bag (50kg)`, Item Type = `Goods`
3. Category = `Raw Material`, Unit = `Kg`, Purchase Price = `8.50`
4. Preferred Vendor = `TechSupply Co.`, Reorder Level = `100`
5. Status = `Active`
6. In `Item_Warehouse_Stock` subform, add:
   - Warehouse = `Main Warehouse`, Current Stock = `500`, Reorder Level = `100`
7. Add another row:
   - Warehouse = `Secondary Store`, Current Stock = `200`, Reorder Level = `50`
8. Submit

**Expected:**
- SKU auto-generated as `SKU-0001`
- Available Stock formula shows `500` for Main Warehouse (Current - Reserved)
- Stock Value = `500 * 8.50 = 4250`
- Record saved

**Edge Cases:**
- Set Purchase Price = `-5` → alert `Purchase Price cannot be negative.`
- Select Item Type = `Goods` but leave Unit blank → alert `Unit is required for Goods items.`
- Leave Item Name blank → alert `Item Name is required.`

---

#### TC-1A-08: Inventory Item — Service Type

**Steps:**
1. Create: Item Name = `Consulting Fee`, Item Type = `Services`
2. Category = `Service`, Unit = `Hour`, Purchase Price = `150.00`
3. Status = `Active`
4. No stock entry needed (Services don't track stock)
5. Submit

**Expected:**
- `SKU-0002` generated. No Item_Warehouse_Stock rows needed.

---

#### TC-1A-09: Inventory Item with Preferred Vendor

**Steps:**
1. Create: Item Name = `Steel Rods (12mm)`, Item Type = `Goods`
2. Category = `Raw Material`, Unit = `Kg`, Purchase Price = `12.00`
3. Preferred Vendor = `Logistics Pro`, Reorder Level = `200`
4. Status = `Active`
5. Stock: Warehouse = `Main Warehouse`, Current Stock = `1000`, Reorder Level = `200`
6. Submit

**Expected:**
- `SKU-0003` generated. Item linked to Logistics Pro vendor.

---

### Build Verification Checklist for Phase 1A

- [ ] Vendors form creates records with all fields saving
- [ ] Vendor_Contacts subform adds and saves multiple contacts
- [ ] Vendor_Documents subform uploads and stores files
- [ ] Accounts form creates records with all fields
- [ ] Account_Contacts subform works
- [ ] Account_Documents subform works
- [ ] Projects generates `PROJ-0001`, `PROJ-0002` correctly
- [ ] Account lookup in Projects shows Accounts list
- [ ] Warehouses form generates `WH-0001` etc.
- [ ] Inventory Items generates `SKU-0001`, `SKU-0002`, `SKU-0003`
- [ ] Item_Warehouse_Stock subform accepts and saves multiple warehouse rows
- [ ] All validation rules fire correctly on bad data

---

## Phase 1B — Budget Plans, Inventory Transactions

### Modules to Test
| Module | API Name | Subforms |
|--------|----------|----------|
| Budget Plans | `Budget_Plans` | `Budget_Components` |
| Inventory Transactions | `Inventory_Transactions` | — |

### Prerequisites
Phase 1A data must exist:
- Projects: `Office Renovation 2026` (PROJ-0001), `Warehouse Automation` (PROJ-0002)
- Warehouses: `Main Warehouse`, `Secondary Store`, `Returns Bay`
- Inventory Items: `Cement Bag`, `Steel Rods`, `Consulting Fee`
- Item_Warehouse_Stock: Cement=500/Steel=1000 at Main Warehouse

### Test Data Preparation

None needed — test scenarios create everything.

### Test Scenarios

---

#### TC-1B-01: Create Budget Plan with Components

**Steps:**
1. Open `Budget_Plans` form
2. Select Project = `Office Renovation 2026`, Currency = `USD`
3. Total Budget = `50000`
4. Start Date = `01-Jun-2026`, End Date = `31-Dec-2026`
5. Status = `Draft` (not yet Active)
6. In `Budget_Components` subform, add rows:
   | Component Name | Category | Allocated Amount |
   |----------------|----------|-----------------|
   | Construction Material | Raw Material | 25000 |
   | Labor Cost | Service | 15000 |
   | Equipment Rental | Equipment | 5000 |
7. Submit

**Expected:**
- Budget Code = `BUD-0001`
- Remaining Amount (formula) = Allocated - Spent (initially = Allocated)
- Utilization Percent = 0%

---

#### TC-1B-02: Validation — Component Sum Exceeds Budget

**Steps:**
1. Create new Budget Plan, Project = `Warehouse Automation`
2. Total Budget = `75000`
3. Add components:
   | Component | Amount |
   |-----------|--------|
   | Racking System | 50000 |
   | Installation | 20000 |
   | Software | 10000 |
4. Try to submit with Status = `Draft` first — note whether validation fires (it may only fire on Active)

**Expected:**
- If sum (80000) > Total Budget (75000) → alert "Component totals exceed Total Budget"

**Edge Cases:**
- Delete one component so total ≤ budget and submit → should pass

---

#### TC-1B-03: Activate Budget Plan (Status = Active)

**Steps:**
1. Open `BUD-0001` (Office Renovation)
2. Change Status to `Active`
3. Submit

**Expected:**
- The project `Office Renovation 2026` now shows `Total Approved Budget = 50000` (synced from Budget Plan)
- Duplicate active plan check passes (no other active plan for same project)

**Edge Cases:**
- Try to create another Budget Plan for `Office Renovation 2026` with Status = `Active` → alert "An active Budget Plan already exists for this project."
- Creating a Draft or Closed plan for the same project → should succeed

---

#### TC-1B-04: Inventory Transaction — Stock In

**Steps:**
1. Open `Inventory_Transactions` form
2. Transaction Type = `Stock In`, Item = `Cement Bag (50kg)`
3. Warehouse = `Main Warehouse`, Quantity = `100`
4. Reference Type = `Manual`, Reference No = `INITIAL-STOCK`
5. Submit

**Expected:**
- Transaction No = `TXN-0001`
- After submission, open Inventory Items → Cement Bag →
  - Item_Warehouse_Stock → Main Warehouse → Current Stock = `600` (was 500 + 100)

---

#### TC-1B-05: Inventory Transaction — Stock In (Second Warehouse)

**Steps:**
1. Create: Type = `Stock In`, Item = `Steel Rods (12mm)`
2. Warehouse = `Secondary Store`, Quantity = `300`
3. Reference Type = `Manual`
4. Submit

**Expected:**
- Item_Warehouse_Stock for Steel Rods at Secondary Store → Current Stock = `300`

---

#### TC-1B-06: Inventory Transaction — Stock Out

**Steps:**
1. Create: Type = `Stock Out`, Item = `Cement Bag (50kg)`
2. Warehouse = `Main Warehouse`, Quantity = `50`
3. Submit

**Expected:**
- Current Stock at Main Warehouse for Cement = `550` (was 600 - 50)

**Edge Cases:**
- Try Stock Out Quantity = `10000` (exceeds available) → alert "Insufficient stock. Available: 550, Requested: 10000"

---

#### TC-1B-07: Inventory Transaction — Reservation

**Steps:**
1. Create: Type = `Reservation`, Item = `Cement Bag (50kg)`
2. Warehouse = `Main Warehouse`, Quantity = `30`
3. Submit

**Expected:**
- Reserved Qty at Main Warehouse for Cement = `30` (Current Stock stays 550)
- Available Stock (formula) = 550 - 30 = `520`

---

#### TC-1B-08: Inventory Transaction — Release

**Steps:**
1. Create: Type = `Release`, Item = `Cement Bag (50kg)`
2. Warehouse = `Main Warehouse`, Quantity = `10`
3. Submit

**Expected:**
- Reserved Qty at Main Warehouse for Cement = `20` (was 30 - 10)

---

#### TC-1B-09: Inventory Transaction — Transfer

**Steps:**
1. Create: Type = `Transfer`, Item = `Cement Bag (50kg)`
2. From Warehouse = `Main Warehouse`, To Warehouse = `Secondary Store`, Quantity = `40`
3. Submit

**Expected:**
- Main Warehouse: Current Stock = `510` (was 550 - 40)
- Secondary Store: Current Stock = `40` (new entry with 40, or incremented by 40 if row existed)

---

#### TC-1B-10: Inventory Transaction — Adjustment

**Steps:**
1. Create: Type = `Adjustment`, Item = `Steel Rods (12mm)`
2. Warehouse = `Main Warehouse`, Quantity = `950` (set to actual physical count)
3. Submit

**Expected:**
- Current Stock at Main Warehouse for Steel Rods = `950` (set to absolute value, not delta)

---

#### TC-1B-11: Validation — Warehouse Requirements

**Edge Cases:**
- Try Stock Out without selecting a Warehouse → alert "Warehouse is required."
- Try Transfer without To_Warehouse → alert "To Warehouse is required for Transfer."
- Set Quantity = 0 or negative → alert

---

### Build Verification Checklist for Phase 1B

- [ ] Budget Plans create with auto-number BUD-0001
- [ ] Budget_Components subform validates total ≤ parent budget
- [ ] Activating Budget Plan syncs Total_Budget → Project.Total_Approved_Budget
- [ ] Unique active plan per project enforced (duplicate blocked)
- [ ] Inventory Transactions auto-number TXN-0001, TXN-0002...
- [ ] Stock In increases Item_Warehouse_Stock.Current_Stock
- [ ] Stock Out decreases Current_Stock with availability check
- [ ] Transfer creates paired movements (source -qty, destination +qty)
- [ ] Reservation increments Reserved_Qty
- [ ] Release decrements Reserved_Qty (floor at 0)
- [ ] Adjustment sets Current_Stock to absolute value

---

## Phase 1C — Expenses, Purchase Requisitions

### Modules to Test
| Module | API Name | Subforms |
|--------|----------|----------|
| Expenses | `Expenses` | — |
| Purchase Requisitions | `Purchase_Requisitions` | `PR_Line_Items` |

### Prerequisites
- Budget Plan `BUD-0001` for `Office Renovation 2026` must be Active
- Budget Components: Construction Material (25000), Labor Cost (15000), Equipment Rental (5000)
- Inventory Items from Phase 1A must exist

### Test Scenarios

---

#### TC-1C-01: Expense — Within Budget (Auto-Approved)

**Steps:**
1. Open `Expenses` form
2. Project = `Office Renovation 2026`, Expense Type = `Material Purchase`
3. Budget Component = `Construction Material` (allocated 25000)
4. Amount = `5000`, Expense Date = `15-Jun-2026`
5. Description = `Purchased cement for foundation work`
6. Vendor = `TechSupply Co.`
7. Submit

**Expected:**
- Expense No = `EXP-0001`
- Status = `Approved` (auto-approved because 5000 ≤ 25000 allocated)
- Budget_Component `Construction Material`: Spent Amount = `5000`

**Edge Cases:**
- Submit without selecting Project → validation should block
- Submit with Amount = 0 or negative → alert

---

#### TC-1C-02: Expense — Triggers Overrun Approval

**Steps:**
1. Create Expense: Project = `Office Renovation 2026`
2. Budget Component = `Construction Material` (already spent 5000, allocated 25000)
3. Amount = `22000` → total would be 27000 which exceeds 25000
4. Description = `Additional steel and fittings`
5. Submit

**Expected:**
- Expense No = `EXP-0002`
- Status = `Overrun-Pending Approval`
- A `Budget_Approvals` record is auto-created (we'll approve in Phase 1D)
- Budget_Component Spent Amount = `5000` (not yet updated — pending approval)

---

#### TC-1C-03: Expense — Within Remaining Budget

**Steps:**
1. Create Expense: Project = `Office Renovation 2026`
2. Budget Component = `Labor Cost` (allocated 15000, spent 0)
3. Amount = `8000`, Description = `Electrician labor charges`
4. Submit

**Expected:**
- Status = `Approved` (8000 ≤ 15000)
- Budget_Component `Labor Cost`: Spent Amount = `8000`

---

#### TC-1C-04: Purchase Requisition with Line Items

**Steps:**
1. Open `Purchase_Requisitions` form
2. Subject = `Cement and Steel for Foundation`
3. Project = `Office Renovation 2026`, Request Type = `Standard`
4. Urgency = `Normal`
5. In `PR_Line_Items` subform, add rows:
   | Item | Description | Qty | Unit | Est. Unit Rate | Total |
   |------|-------------|-----|------|---------------|-------|
   | Cement Bag (50kg) | — | 100 | Kg (auto) | 8.50 | 850 (auto) |
   | Steel Rods (12mm) | — | 50 | Kg (auto) | 12.00 | 600 (auto) |
6. Status = `Open` (initiates approval)
7. Note: Line Item `Unit` and `Item Type` should auto-fill from the selected Item
8. Submit

**Expected:**
- Requisition No = `REQ-0001`
- Status = `Open`
- Approval Stage = `0` (pending Dept Manager)
- Auto-number works

**Edge Cases:**
- Submit with Status = Open but no line items → alert "At least one line item is required"
- Submit with Status = Open but no Project → alert
- Select Item = Steel Rods → Unit should auto-fill as `Kg`, Item Type as `Goods`

---

#### TC-1C-05: Blueprint — Approve PR Stage 1 (Dept Manager)

**Steps:**
1. In Zoho Creator, open the `Purchase_Requisitions` form as a user with `Project Manager` role
2. Find `REQ-0001`
3. Advance the Blueprint stage from `Pending Dept Manager` to next stage
4. Set Approval Note = `Approved — proceed`
5. Save

**Expected:**
- Stage advances to `1` (Finance Manager pending)
- Email notification should be triggered (WF)

---

#### TC-1C-06: Blueprint — Reject PR at Stage 2

**Steps:**
1. Create another PR: Subject = `Emergency Server Parts`
2. Project = `Office Renovation 2026`, Request Type = `Emergency`
3. Urgency = `Critical`, Justification = `Server cooling fan failed — needs immediate replacement`
4. Add one line item: Item = `Consulting Fee`, Qty = `5`, Rate = `150`
5. Status = `Open`, Submit

**Expected:**
- `REQ-0002` created, Status = Open

**Edge Cases:**
- Set Urgency = `Critical` but leave Justification blank → alert "Justification is required for Critical urgency"

---

#### TC-1C-07: PR — Final Approval (Auto-Creates PO)

**Steps:**
1. Advance `REQ-0001` through all 3 stages:
   - Dept Manager → Approve
   - Finance Manager → Approve  
   - Procurement → Approve
2. After final approval, the Deluge script should auto-create a Purchase Order

**Expected:**
- `REQ-0001` Status = `Approved`
- A new `Purchase_Orders` record appears with Status = `Draft`
- PO has line items matching PR line items (PO_Line_Items subform populated)

---

### Build Verification Checklist for Phase 1C

- [ ] Expenses auto-number EXP-0001, EXP-0002
- [ ] Within-budget expenses auto-approve (Status = Approved)
- [ ] Over-budget expenses → Status = Overrun-Pending Approval
- [ ] Overrun creates Budget_Approval record automatically
- [ ] Approved expenses update Budget_Component.Spent_Amount
- [ ] Expense Budget Component validation works (must belong to selected Project)
- [ ] Expense duplicate check (same Project+Component+Date+Amount)
- [ ] Purchase Requisitions auto-number REQ-0001, REQ-0002
- [ ] PR_Line_Items subform saves multiple items
- [ ] Unit and Item Type auto-fill from Item lookup
- [ ] 3-stage Blueprint approval chain works
- [ ] Urgency=Critical requires Justification
- [ ] Final PR approval auto-creates PO (Draft) with line items

---

## Phase 1D — Budget Approvals, Purchase Orders, Goods Receipts, Transfer Orders

### Modules to Test
| Module | API Name | Subforms |
|--------|----------|----------|
| Budget Approvals | `Budget_Approvals` | — |
| Purchase Orders | `Purchase_Orders` | `PO_Line_Items` |
| Goods Receipts | `Goods_Receipts` | `GRN_Line_Items` |
| Transfer Orders | `Transfer_Orders` | `TO_Line_Items` |

### Prerequisites
- Expense `EXP-0002` (Overrun-Pending Approval for Construction Material) must exist
- PR `REQ-0001` must have been approved and auto-created a PO
- Budget Plan `BUD-0001` must be Active

### Test Scenarios

---

#### TC-1D-01: Approve Budget Overrun

**Steps:**
1. Open `Budget_Approvals` form
2. Find the auto-created record for expense `EXP-0002` (Construction Material overrun)
3. Status = `Approved`, Reviewer Notes = `Approved for Phase 1 foundation work`
4. Submit

**Expected:**
- Expense `EXP-0002` Status changes to `Approved`
- Budget_Component `Construction Material`: Spent Amount updates to `27000` (5000 + 22000)
- Budget_Approvals App No = `APPR-0001`

**Edge Cases:**
- Try to approve without selecting an Expense → alert

---

#### TC-1D-02: Purchase Order — Edit and Open

**Steps:**
1. Open the auto-created PO (Draft) from Phase 1C PR approval
2. Verify `PO_Line_Items` contains the items from PR:
   - Cement Bag — Qty 100, Unit Rate 8.50
   - Steel Rods — Qty 50, Unit Rate 12.00
3. Verify Item Total formula = Qty × Unit Rate (850.00, 600.00)
4. Verify Discount Amount and Tax Amount formulas
5. Set Vendor = `TechSupply Co.`, Payment Terms = `Net 30`
6. Change Status to `Open`
7. Submit

**Expected:**
- PO No = `PO-0001`
- On Status = Open → vendor email notification (WF)
- PO lifecycle: Draft → Open

**Edge Cases:**
- Try to Open without selecting Vendor → alert
- Try to add a line item with 0 Quantity → should this be blocked by validation?

---

#### TC-1D-03: Purchase Order — Manual Creation

**Steps:**
1. Create new Purchase Order: Vendor = `Logistics Pro`
2. Project = `Warehouse Automation`
3. In `PO_Line_Items`, add:
   | Item | Description | Qty | Unit Rate | Disc% | Tax% |
   |------|-------------|-----|-----------|-------|------|
   | Steel Rods (12mm) | For racking | 200 | 12.00 | 5 | 18 |
4. Status = `Open`
5. Submit

**Expected:**
- PO-0002 created
- Item Total = 200 × 12 = `2400`
- Discount Amount = 2400 × 5% = `120`
- Tax Amount = (2400 - 120) × 18% = `410.40`
- Total = 2400 - 120 + 410.40 = `2690.40`

---

#### TC-1D-04: Purchase Order — Cancel (with Guard)

**Steps:**
1. Try to cancel `PO-0001` (which has no GRN yet)
2. Set Status = `Cancelled`, Submit

**Expected:**
- PO-0001 status = Cancelled (no linked GRN, so allowed)

**Edge Cases:**
- Create a GRN against a PO, then try to cancel the PO → alert "Cannot cancel PO with linked GRN records"
- (Test this after TC-1D-05)

---

#### TC-1D-05: Goods Receipt — Full Receipt

**Steps:**
1. Open `Goods_Receipts` form (create a new PO first if needed, or use PO-0002)
2. PO = `PO-0002` (Steel Rods), GRN Date = today
3. In `GRN_Line_Items`, add:
   | Item | PO Qty | Accepted Qty | Rejected Qty | Reason | Actual Unit Cost | Warehouse |
   |------|--------|-------------|-------------|--------|-----------------|-----------|
   | Steel Rods | 200 | 195 | 5 | Surface rust on 5 rods | 12.00 | Main Warehouse |
4. Status = `Open`
5. Submit

**Expected:**
- GRN No = `GRN-0001`
- A Stock In transaction is auto-created:
  - Item = Steel Rods, Warehouse = Main Warehouse, Qty = `195`
  - Reference Type = `GRN`, Reference No = GRN No
- Current Stock for Steel Rods at Main Warehouse = `950 + 195 = 1145` (was adjusted to 950)
- Inventory_Transactions record created with Transaction_Type = `Stock In`

**Edge Cases:**
- Accepted + Rejected > PO_Quantity → alert
- Rejected Qty > 0 but Reason_for_Rejection blank → alert
- PO is `Open` status — verify GRN blocks for non-Open POs
- Accepted Qty > 0 but Warehouse blank → alert

---

#### TC-1D-06: Transfer Order — Create and Complete

**Steps:**
1. Open `Transfer_Orders` form
2. From Warehouse = `Main Warehouse`, To Warehouse = `Returns Bay`
3. In `TO_Line_Items`, add:
   | Item | Qty | Rate | Total |
   |------|-----|------|-------|
   | Cement Bag (50kg) | 20 | 8.50 | 170 (auto) |
4. Status = `Completed`
5. Submit

**Expected:**
- TO No = `TO-0001`
- Two Inventory_Transactions auto-created:
  1. Stock Out: Cement → Main Warehouse → Qty = `20`
  2. Stock In: Cement → Returns Bay → Qty = `20`
- Main Warehouse Cement: Current Stock = `510 - 20 = 490`
- Returns Bay Cement: Current Stock = `0 + 20 = 20`

**Edge Cases:**
- From_Warehouse = To_Warehouse → alert "From and To warehouse must be different"
- Insufficient stock at From_Warehouse → alert

---

#### TC-1D-07: Budget Approval — Reject Overrun

**Steps:**
1. Create a new Expense: Project = `Office Renovation 2026`
2. Budget Component = `Equipment Rental` (allocated 5000), Amount = `6000`
3. Submit → Status = Overrun-Pending Approval
4. Open the auto-created Budget_Approval
5. Status = `Rejected`, Notes = `Equipment rental budget exhausted. Request reallocation.`
6. Submit

**Expected:**
- Expense status changes to `Rejected`
- Construction Material Spent Amount remains unchanged (no update on rejection)

---

### Build Verification Checklist for Phase 1D

- [ ] Budget_Approvals auto-create on expense overrun with correct defaults
- [ ] Approval cascades: Exp_Approved → Expense.Approved + Spent_Amount updated
- [ ] Rejection cascade: Exp_Rejected → Expense.Rejected, Spent_Amount unchanged
- [ ] PO-0001 auto-created from PR with matching line items
- [ ] PO-0002 manually created with all formula calculations correct
- [ ] PO Open triggers vendor email (verify in activity log)
- [ ] PO Cancel blocked if GRNs exist
- [ ] GRN-0001 with partial rejection creates Stock In for accepted qty only
- [ ] GRN line item total formula works (Accepted × Actual Cost)
- [ ] TO-0001 with paired Stock Out + Stock In
- [ ] All validation rules fire correctly

---

## Phase 1E — BOM, Delivery Challans, Invoicing

### Modules to Test
| Module | API Name | Subforms |
|--------|----------|----------|
| Bill of Materials | `BOM` | `BOM_Line_Items` |
| Delivery Challans | `Delivery_Challans` | `DC_Line_Items` |
| Invoices | `Invoices` | `Invoice_Line_Items` |

### Prerequisites
- All prior phase data must exist (items with stock, projects, accounts)
- Stock levels verified (Cement = 490 Main, 20 Returns Bay; Steel = 1145 Main)
- Account `ABC Manufacturing` exists

### Test Scenarios

---

#### TC-1E-01: Create BOM

**Steps:**
1. Open `BOM` form
2. Product Item = `Consulting Fee` (the service item for the BOM output)
3. BOM Name = `Foundation Work Kit`, Version = `1.0`
4. In `BOM_Line_Items`, add:
   | Component Item | Qty | Unit Cost | Total Cost |
   |----------------|-----|-----------|------------|
   | Cement Bag (50kg) | 10 | 8.50 | 85.00 (auto) |
   | Steel Rods (12mm) | 5 | 12.00 | 60.00 (auto) |
5. Status = `Active`
6. Submit

**Expected:**
- BOM No = `BOM-0001`
- Total Manufacturing Cost = `85 + 60 = 145`
- No duplicate component items allowed

**Edge Cases:**
- Add same Component_Item twice → validation alert for duplicate
- Submit with zero quantity → alert
- Submit with no line items → alert

---

#### TC-1E-02: Delivery Challan — Create and Ship

**Steps:**
1. Open `Delivery_Challans` form
2. Project = `Office Renovation 2026`, Account = `ABC Manufacturing`
3. Warehouse = `Main Warehouse`
4. In `DC_Line_Items`, add:
   | Item | Description | Qty | Unit | Warehouse |
   |------|-------------|-----|------|-----------|
   | Cement Bag (50kg) | For site delivery | 30 | Kg (auto) | Main Warehouse |
5. Status = `Shipped`
6. Submit

**Expected:**
- DC No = `DC-0001`
- A Stock Out transaction is auto-created:
  - Item = Cement Bag, Warehouse = Main Warehouse, Qty = `30`
  - Reference Type = `DC`, Reference No = DC No
- Main Warehouse Cement: Current Stock = `490 - 30 = 460`

**Edge Cases:**
- Ship with insufficient stock → alert
- Ship with no line items → alert
- Ship with no Warehouse → alert

---

#### TC-1E-03: Delivery Challan — Multi-Item

**Steps:**
1. Create DC: Project = `Office Renovation 2026`, Account = `ABC Manufacturing`
2. Warehouse = `Main Warehouse`
3. Line items:
   | Item | Qty |
   |------|-----|
   | Cement Bag (50kg) | 20 |
   | Steel Rods (12mm) | 100 |
4. Status = `Shipped`
5. Submit

**Expected:**
- DC-0002 created
- Two Stock Out transactions: Cement -20, Steel -100
- Steel Main Warehouse: `1145 - 100 = 1045`

---

#### TC-1E-04: Invoice — Create and Send (Manual)

**Steps:**
1. Open `Invoices` form
2. Project = `Office Renovation 2026`, Account = `ABC Manufacturing`
3. Invoice Date = today, Due Date = 30 days from now
4. In `Invoice_Line_Items`:
   | Item | Description | Qty | Rate | Disc% | Tax% |
   |------|-------------|-----|------|-------|------|
   | Consulting Fee | Project management fee | 40 | 150.00 | 0 | 18 |
5. Status = `Sent`
6. Submit

**Expected:**
- Invoice No = `INV-0001`
- Line Total = 40 × 150 = `6000`
- Discount Amount = `0` (0%)
- Tax Amount = 6000 × 18% = `1080`
- Total = 6000 + 1080 = `7080`
- Project `Office Renovation 2026`: Total Invoiced = `7080`

**Edge Cases:**
- Submit without line items with Status=Sent → alert
- Set Due Date before Invoice Date → alert

---

#### TC-1E-05: Invoice — Custom Button (Create DC from Invoice)

**Steps:**
1. Open Invoice `INV-0001`
2. Click the custom button `Create DC`
3. (This opens/creates a Delivery Challan with line items copied from invoice)

**Expected:**
- A new DC record (DC-0003) is created or opened with matching line items
- DC populated with Project/Account from Invoice

---

#### TC-1E-06: Invoice — Mark as Paid

**Steps:**
1. Open Invoice `INV-0001`
2. Create a Receipt/Payment record linking to this invoice
3. Or if using a Status field approach, change Status to `Paid`
4. Submit

**Expected:**
- If Status → Paid: Balance Due = `0`, Total Paid updated
- Project `Office Renovation 2026`: Total Paid updated (Phase 2 financial)

---

#### TC-1E-07: Project Completed → Auto-Create Final Invoice

**Steps:**
1. Open Project `Warehouse Automation` (PROJ-0002)
2. Set Status = `Completed`
3. Submit

**Expected:**
- Check whether any Deliveries exist for this project
- If yes → auto-create Invoice with uninvoiced items
- Project Completion validation runs (checks open Expenses/POs/PRs)

---

#### TC-1E-08: Overdue Invoice Detection

**Steps:**
1. Create an Invoice: Status = `Sent`, Due Date = 7 days ago
2. Run the scheduled workflow (or wait for midnight trigger)

**Expected:**
- Invoice Status auto-updates to `Overdue` if Due_Date passed and Status = Sent

---

### Build Verification Checklist for Phase 1E

- [ ] BOM-0001 creates with cost calculation (Total_Mfg_Cost)
- [ ] BOM validates no duplicate components, positive quantities
- [ ] DC-0001 Shipped → auto-Stock Out with correct reference
- [ ] DC multi-line creates separate Stock Out per item
- [ ] Unit auto-fills from Item lookup in DC line items
- [ ] INV-0001 with correct Subtotal, Discount, Tax, Total calculations
- [ ] Invoice Sent updates Project Total Invoiced
- [ ] Invoice Paid updates Project Total Paid / Balance Due
- [ ] Create DC custom button works from Invoice
- [ ] Project Completed → auto-Invoice from uninvoiced DCs
- [ ] Scheduled overdue detection works (Sent→Overdue if past Due Date)

---

## Phase 1F — Reports & Dashboards

### Modules to Test
| Module | Description |
|--------|-------------|
| Project P&L | Project revenue − expense report |
| Budget vs Actual | Budget consumption per component |
| Stock Availability | Current stock across warehouses |
| Low Stock Alert | Items below reorder level |
| Invoice Aging | Invoices grouped by overdue duration |
| Executive Dashboard | KPI cards + charts |
| DC Register | Delivery challans by status/project |
| BOM Cost Summary | All BOMs with manufacturing costs |
| PO Register | Purchase orders by status |
| Expense Analysis | Expenses by type and project |
| Vendor Performance | Vendors list with metadata |

### Prerequisites
All prior phase data must exist with multiple records across all modules.

### Test Scenarios

---

#### TC-1F-01: Verify Report Data Accuracy

**Steps:**
1. Open the **Project P&L** report
2. Verify values:
   | Project | Budget | Invoiced | Expenses | P&L |
   |---------|--------|----------|----------|-----|
   | Office Renovation 2026 | 50000 | 7080 (INV-0001) | 40000 (5000+27000+8000) | -32920 |
   | Warehouse Automation | 75000 | 0 | 0 | 0 |
3. Compare against manually calculated values

**Expected:**
- Report numbers match manual calculation
- Zero-expense projects show 0 or blank

---

#### TC-1F-02: Stock Availability Report

**Steps:**
1. Open **Stock Availability** report (grouped by Item)
2. Expand `Cement Bag (50kg)`

**Expected:**
| Warehouse | Current Stock | Reserved Qty | Available |
|-----------|--------------|-------------|-----------|
| Main Warehouse | 460 | 20 | 440 |
| Secondary Store | 40 | 0 | 40 |
| Returns Bay | 20 | 0 | 20 |

---

#### TC-1F-03: Low Stock Alert

**Steps:**
1. Open **Low Stock Alert** report

**Expected:**
- Any item where Current_Stock ≤ Reorder_Level appears
- Example: If Cement Main Warehouse current (460) > reorder (100) → not in report
- Set Cement Main Warehouse Current Stock to 50, verify it appears in alert

---

#### TC-1F-04: Invoice Aging

**Steps:**
1. Open **Invoice Aging** report

**Expected:**
- INV-0001 (Overdue) appears in appropriate bucket (31-60 or 61-90 days depending on test date)
- Correct count per aging bucket

---

#### TC-1F-05: Executive Dashboard

**Steps:**
1. Open the Executive Dashboard

**Expected:**
| KPI Card | Expected Value |
|----------|---------------|
| Total Active Projects | 1 (Office Renovation) |
| Total Budget | 50000 |
| Total Spent | 40000 (or sum of approved expenses) |
| Budget Utilization % | ~80% |
| Open PO Value | Sum of Open POs |
| Pending GRNs | PO-0002 (if delivered but GRN pending) |
| Inventory Value | Sum of `Stock_Value` across all items |

---

#### TC-1F-06: Scheduled KPI Refresh

**Steps:**
1. Add a new expense or change project data
2. Manually trigger the scheduled workflow (or wait for midnight run)
3. Verify KPI values update

**Expected:**
- After scheduled workflow runs, dashboard KPIs reflect latest data

---

### Build Verification Checklist for Phase 1F

- [ ] All 10 report views render with correct data
- [ ] Project P&L shows revenue − expense accurately
- [ ] Stock Availability groups by item, shows per-warehouse breakdown
- [ ] Low Stock Alert correctly filters items ≤ reorder level
- [ ] Invoice Aging shows overdue invoices in correct buckets
- [ ] Executive Dashboard displays 7 KPI cards with correct values
- [ ] Budget vs Actual chart matches component data
- [ ] PO Register groups by status correctly
- [ ] DC Register lists challans by project
- [ ] Scheduled KPI refresh runs without errors
- [ ] POs all listed as Completed/Cancelled (none auto-closed)

---

## Integration Test — End-to-End Flow

Run this after ALL phases are built and all phase-level tests pass.

### Full Business Flow: Procure → Receive → Use → Bill

This test exercises the complete system across all modules.

---

#### INT-01: Create Project and Budget

1. Create: Project = `Factory Expansion`, Budget = `200000`, Status = `Active`
2. Create: Budget Plan = `Factory Expansion Plan`, Total = `200000`, Status = `Active`
3. Components:
   | Name | Amount |
   |------|--------|
   | Construction Material | 100000 |
   | Equipment | 60000 |
   | Labor | 40000 |

**Expected:** Budget synced to Project.Total_Approved_Budget = 200000

---

#### INT-02: Raise Purchase Requisition

1. Create PR for `Factory Expansion`: Subject = `Steel Beams`
2. Items: `Steel Rods (12mm)` Qty 500, Est Rate 12.00
3. Status = Open

**Expected:** REQ generated, approval starts

---

#### INT-03: Approve PR → Auto-Create PO

1. Approve through all 3 stages
2. **Expected:** PO created with Steel Rods × 500 @ 12.00

---

#### INT-04: Open PO → Vendor Email

1. Open PO, Set Vendor = `TechSupply Co.`, Status = `Open`
2. **Expected:** PO-0003, Item Total = 6000

---

#### INT-05: Receive Goods (GRN)

1. Create GRN for PO-0003: Accept 490 of 500, Reject 10 (damaged)
2. **Expected:** GRN-0002, Stock In for 490 units

---

#### INT-06: Create Expense

1. Expense: `Construction Material`, Amount = `50000`
2. **Expected:** Auto-approved (50000 ≤ 100000 allocated)

---

#### INT-07: Transfer Stock

1. Transfer 100 Steel Rods: Main → Secondary Store
2. **Expected:** Paired Stock Out/In

---

#### INT-08: Create BOM

1. BOM Name = `Steel Frame Unit`, Product Item = any item
2. Components: Steel Rods Qty 10 @ 12.00, Labor Qty 5 @ 150
3. Status = Active
4. **Expected:** BOM cost = 120 + 750 = 870

---

#### INT-09: Deliver to Customer (DC)

1. DC: Project = `Factory Expansion`, Account = `ABC Manufacturing`
2. 50 Steel Rods to site
3. Status = Shipped
4. **Expected:** DC created, Stock Out for 50 units

---

#### INT-10: Invoice Customer

1. Invoice: Project = `Factory Expansion`, Account = `ABC Manufacturing`
2. Item = any service, Qty 10, Rate 1000, Tax 18%
3. Status = Sent
4. **Expected:** Total = 10000 + 1800 = 11800, Project Total Invoiced updated

---

#### INT-11: Verify Dashboard

1. Open Executive Dashboard
2. **Expected:** Factory Expansion appears in KPI, Budget vs Actual, P&L

---

### Integration Test Sign-off

- [ ] Full procure-to-bill cycle works end-to-end
- [ ] Stock quantities are consistent across all transactions
- [ ] Budget amounts are correctly tracked
- [ ] Reports reflect real-time data
- [ ] All auto-created records have correct references

---

## Test Recording Template

Use this template to record each test run:

```
Phase: _______ | Tester: _______ | Date: _______

| TC ID | Status (Pass/Fail) | Actual Result | Notes |
|-------|-------------------|---------------|-------|
|       |                   |               |       |

Issues Found:
1. ...
```

---

## Common Issues and Resolutions

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Subform data not saving | Embedded subform not configured correctly | Re-check form builder — subform must be embedded, not linked |
| Deluge script not firing | Workflow not activated or trigger wrong | Check workflow status → must be "Active", trigger must match (On Submit, On Post Submit) |
| Formula not calculating | Field type wrong or formula syntax error | Verify field type is `Formula`, check field API names in expression |
| Lookup shows no records | Lookup relationship config wrong | Verify target form and display field |
| `alert` not showing | Using `throw` instead of `alert` | Change `throw` to `alert` in Deluge |
| Stock not updating | getRecordById not finding correct record | Verify item_id field exists and is populated |
| PR not auto-creating PO | Approval stage not triggering final stage | Check Blueprint stage configuration and final stage Deluge script |
