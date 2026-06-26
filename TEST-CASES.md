# Test Cases & UAT Document — Chemsol Zoho Creator

> **Instructions**: Each test case has a unique ID. Mark status as **Pass** / **Fail** / **Not Tested**. Add comments for failures.

---

## 1. Admin Module

### 1.1 Item Master

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-ADM-001 | Create Item with all fields | Logged in as Admin | 1. Open Item Master form<br>2. Fill Category, Code, Name, UOM, HSN<br>3. Fill Min Stock, Max Stock, Standard Rate<br>4. Select Preferred Supplier<br>5. Enter Lead Time<br>6. Save | Item created successfully. All fields saved. | | |
| TC-ADM-002 | Create Item — mandatory fields only | Logged in as Admin | 1. Open Item Master<br>2. Fill Category, Code, Name, UOM, HSN, Min Stock only<br>3. Save | Item created. Optional fields empty. | | |
| TC-ADM-003 | Create Item — missing mandatory Category | Logged in as Admin | 1. Open Item Master<br>2. Leave Category empty<br>3. Fill other fields<br>4. Try to Save | Save blocked. Validation error on Category field. | | |
| TC-ADM-004 | Create Item — missing mandatory fields | Logged in as Admin | 1. Open Item Master<br>2. Leave all fields empty<br>3. Try to Save | Save blocked. All mandatory fields highlighted. | | |
| TC-ADM-005 | Edit existing Item | Item exists | 1. Search for item<br>2. Edit Name, Standard Rate<br>3. Save | Item updated. Changes reflected immediately. | | |
| TC-ADM-006 | Delete Item (no transactions) | Item exists, never used | 1. Search for item<br>2. Delete | Item deleted permanently. | | |
| TC-ADM-007 | Sales — View only access to Item Master | Logged in as Sales | 1. Open Item Master<br>2. Attempt to create/edit/delete | Create/Edit/Delete buttons hidden or disabled. View only. | | |
| TC-ADM-008 | Auto-fetch — Item Name from Code | Item exists | 1. In PR line item<br>2. Enter existing Item Code<br>3. Tab out | Item Name auto-fetches. | | |
| TC-ADM-009 | Auto-fetch — Item Code from Name | Item exists | 1. In PR line item<br>2. Enter existing Item Name<br>3. Tab out | Item Code auto-fetches. | | |
| TC-ADM-010 | Verify Item Master report | Items exist | 1. Navigate to Purchase Item Master report<br>2. Apply filters | Report shows all items with correct data. | | |
| TC-ADM-011 | Duplicate Item Code check | Item code "RM001" used | 1. Create item with code "RM001"<br>2. Try to save | Duplicate error on Item Code. | | |

### 1.2 System Master

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-ADM-012 | Create System with all fields | Logged in as Admin | 1. Open System Master<br>2. Enter System Code, Name, Thickness, Description<br>3. Select UOM<br>4. Save | System created successfully. | | |
| TC-ADM-013 | Verify System Code prefixes | Multiple systems | 1. Create systems with EP, PU, DEM, ANTI, ESD codes<br>2. Verify all save correctly | All prefixes accepted. | | |

### 1.3 Supplier Master

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-ADM-014 | Create Supplier — all fields | Logged in as Admin | 1. Open Supplier Master<br>2. Fill Supplier Name, Type, GSTIN, PAN, Contact Person<br>3. Fill Mobile (primary + alternate)<br>4. Fill Email, Address, Pincode<br>5. Fill Bank Name, Account No, IFSC<br>6. Fill Payment Terms, Credit Days<br>7. Save | Supplier created. Supplier Code auto-generated. | | |
| TC-ADM-015 | Create Supplier — mandatory only | Logged in as Admin | 1. Fill only mandatory fields<br>2. Save | Supplier created with auto-generated code. | | |
| TC-ADM-016 | GSTIN format validation | — | 1. Enter invalid GSTIN format<br>2. Try to save | Validation error on GSTIN format. | | |
| TC-ADM-017 | Supplier Code auto-generation | — | 1. Create supplier<br>2. Observe Supplier Code | Code is auto-generated (e.g. SPL-001). | | |
| TC-ADM-018 | Finance view only | Logged in as Finance | 1. Open Supplier Master<br>2. Attempt to create/edit | No create/edit access. View only. | | |

### 1.4 Customer Master

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-ADM-019 | Create Customer | Logged in as Admin/Sales | 1. Open Customer Master<br>2. Fill Client Org Name, Contact Person<br>3. Fill Contact No, Alt Contact, Email<br>4. Fill GST No, PAN, Addresses<br>5. Save | Customer created. Customer Code auto-generated. | | |
| TC-ADM-020 | Customer Code auto-fetch in SO/WO | Customer exists | 1. In SO/WO, select Customer Code<br>2. Observe auto-fetch | Client Org Name, Contact, GST, Address auto-populated. | | |

### 1.5 Store Master & Bin Location

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-ADM-021 | Create Store | Logged in as Admin/Store | 1. Open Store Master<br>2. Enter Store Name<br>3. Select Store Type (RM/FG/QC/Site)<br>4. Enter Location<br>5. Save | Store created. Store Code auto-generated. | | |
| TC-ADM-022 | Create Bin Location | Store exists | 1. Open Bin Location Master<br>2. Select Store<br>3. Enter Rack, Shelf, Bin numbers<br>4. Save | Bin location created and linked to store. | | |

---

## 2. Sales Module — SO/WO Master

### 2.1 Supply+Apply Mode (Work Order)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-SAL-001 | Create SO — Supply+Apply mode (all fields) | Customer exists, System exists | 1. Open SO/WO form<br>2. Select "Supply+Apply" mode<br>3. Fill Date, Employee<br>4. Select Customer Code → verify auto-fetch<br>5. Fill Site Name, Address, Site Manager<br>6. Select Project Type (Industrial)<br>7. Add System line item: Code, Area, UOM, Rate<br>8. Verify Amount auto-calculated<br>9. Fill Payment Terms, Transport Scope + Amount<br>10. Set Lead Time, Warranty<br>11. Check "Is Proper System Required"<br>12. Set Commission (Percentage + Amount)<br>13. Attach PO/BOQ file<br>14. Save | WO created. WO Number auto-generated. Total calculated.<br>Commission calculated correctly. Attachments saved. | | |
| TC-SAL-002 | Create SO — Supply+Apply (minimal) | Customer exists | 1. Select Supply+Apply mode<br>2. Fill mandatory fields only<br>3. Add one system line item<br>4. Save | WO created with defaults. | | |
| TC-SAL-003 | Mandatory field validation — Supply+Apply | — | 1. Try saving empty form in Supply+Apply mode | All `*` fields validated. | | |
| TC-SAL-004 | System auto-fetch in line items | System exists | 1. Enter System Code in line item<br>2. Tab out | System Name, Thickness auto-fetched. UOM populated. | | |
| TC-SAL-005 | Amount calculation in line items | — | 1. Enter Area and Rate<br>2. Observe Amount | Amount = Area × Rate (auto-calculated). | | |
| TC-SAL-006 | Total Work Order Amount | Multiple line items | 1. Add 3 system line items<br>2. Verify total | Total = Sum of all line item amounts. | | |
| TC-SAL-007 | Project Type dropdown | — | 1. Click Project Type<br>2. Verify options | Options: Industrial, Commercial only. | | |
| TC-SAL-008 | Commission — Percentage mode | — | 1. Check Commission<br>2. Select "Percentage"<br>3. Enter 10%<br>4. Verify amount | Commission amount = Total × 10%. | | |
| TC-SAL-009 | Commission — Fix Amount mode | — | 1. Check Commission<br>2. Select "Fix Amount"<br>3. Enter ₹5000<br>4. Verify | Commission amount = ₹5000. | | |
| TC-SAL-010 | PO/BOQ attachment (multiple) | — | 1. Attach 3 PDF files<br>2. Save WO<br>3. Open WO again | All 3 attachments visible and downloadable. | | |

### 2.2 Supply-Only Mode (Sales Order)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-SAL-011 | Create SO — Supply mode | Customer exists, FG exists | 1. Select "Supply" mode<br>2. Fill Customer details → auto-fetch<br>3. Add FG line items: Name, Qty, UOM, Rate<br>4. Fill Billing and Shipping Address<br>5. Set Transport Scope + Amount<br>6. Save | SO created. SO Number auto-generated. Total calculated. | | |
| TC-SAL-012 | Mode switching — field visibility | — | 1. Select "Supply+Apply" → observe fields<br>2. Switch to "Supply" → observe fields | System-related fields hide in Supply mode. FG fields show.<br>Field labels change (Work Order ↔ Sales Order). | | |
| TC-SAL-013 | Edit SO/WO after save | SO/WO exists | 1. Open existing SO/WO<br>2. Modify line items<br>3. Save | Changes saved. Totals recalculated. | | |

### 2.3 Search & Reports

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-SAL-014 | Search SO by Customer Name | SOs exist | 1. Open SO listing<br>2. Filter by Customer Name | Matching SOs displayed. | | |
| TC-SAL-015 | SO register report | SOs exist | 1. Navigate to SO reports<br>2. View SO Register | All SOs listed with status, dates, amounts. | | |
| TC-SAL-016 | Mode filter in reports | Both SO and WO exist | 1. Open report<br>2. Filter by Supply+Apply vs Supply | Correct mode records shown. | | |

---

## 3. Purchase Module

### 3.1 Purchase Requisition (PR)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PUR-001 | Create PR with line items | Items exist | 1. Open PR form<br>2. PR Number auto-generated, Date = Today<br>3. Department auto-filled from login<br>4. Add line item: enter Item Code → verify auto-fetch<br>5. Enter Qty, Description<br>6. Verify UOM and Lead Time auto-fetched<br>7. Save | PR created. Line items saved with auto-fetched data. | | |
| TC-PUR-002 | PR — auto-fetch Item Name from Code | Item exists | 1. Enter Item Code in line item<br>2. Tab out | Item Name auto-fetched. | | |
| TC-PUR-003 | PR — auto-fetch Item Code from Name | Item exists | 1. Enter Item Name in line item<br>2. Tab out | Item Code auto-fetched. | | |
| TC-PUR-004 | PR — UOM auto-fetch | Item exists | 1. Enter Item Code/Name<br>2. Verify UOM field | UOM auto-populates from Item Master. | | |
| TC-PUR-005 | PR — Lead Time auto-fetch | Item has Lead Time | 1. Enter Item with configured Lead Time<br>2. Verify | Lead Time (Days) auto-populated. | | |
| TC-PUR-006 | PR — department auto-filled | Logged in as Production | 1. Open PR form<br>2. Observe Department field | Department = "Production" (from login). | | |
| TC-PUR-007 | PR — mandatory fields validation | — | 1. Try saving PR without any line items | Validation error: at least one line item required. | | |
| TC-PUR-008 | PR Approval workflow | PR created as Executive | 1. Submit PR for approval<br>2. Login as Purchase Manager<br>3. Approve PR | PR status = "Approved". | | |
| TC-PUR-009 | PR Rejection workflow | PR submitted | 1. As approver, reject PR with reason<br>2. Notify requester | PR status = "Rejected". Requester notified. | | |
| TC-PUR-010 | PR — limit-based escalation | PR amount > ₹50,000 | 1. Create PR with high-value items<br>2. Submit | PR routed to Director (beyond Purchase Manager limit). | | |

### 3.2 Rate Comparison

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PUR-011 | Create Rate Comparison from approved PR | Approved PR exists | 1. Open Rate Comparison<br>2. Date = Today's Date<br>3. Select PR Reference → items auto-fetched<br>4. Enter Product No, Name from PR<br>5. Add Supplier 1: select, Price, Credit<br>6. Add Supplier 2-5 | All suppliers listed with prices. | | |
| TC-PUR-012 | Finalise supplier and rate | Suppliers quoted | 1. Enter Finalised Supplier<br>2. Enter Final Rate<br>3. Save | Rate Comparison saved. Ready for PO creation. | | |
| TC-PUR-013 | Rate Comparison — edit after save | Saved | 1. Open existing Rate Comparison<br>2. Modify supplier prices<br>3. Save | Changes saved. Approval may be needed. | | |

### 3.3 Purchase Order (PO)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PUR-014 | Create PO — Non-coding RM Type | Approved Rate Comparison exists, Supplier exists | 1. Open PO form<br>2. Select RM Type = "Non Coding"<br>3. PO Number auto-generated as RM-xxx<br>4. PO Date = Today<br>5. Select Supplier Code → details auto-fetch<br>6. Select PR Reference<br>7. Select Bill To, Ship To<br>8. Add line items from Rate Comparison<br>9. Enter Qty, Rate<br>10. Verify Basic Amount, GST%, GST, Total auto-calc<br>11. Set Delivery Date, Payment Terms<br>12. Select Transport Scope, Mode<br>13. Save | PO created with correct numbering. All calculations correct. | | |
| TC-PUR-015 | Create PO — Coding RM Type | Same as above | 1. Select RM Type = "Coding"<br>2. Observe PO Number | PO Number = RMWAD-xxx. | | |
| TC-PUR-016 | PO — auto-fetch supplier details | Supplier exists | 1. Select Supplier Code<br>2. Verify | Supplier Name, GST, Address, Bank details auto-fetched. | | |
| TC-PUR-017 | PO line item — auto-fetch | Item exists | 1. Enter Item Code in line item<br>2. Verify | Item Name, HSN, UOM, GST% auto-fetched. | | |
| TC-PUR-018 | PO — item description textbox | — | 1. Add item to PO<br>2. Check Item Name field | Sub-textbox for additional description available below Item Name. | | |
| TC-PUR-019 | PO — GST calculation | GST% = 18%, Qty=10, Rate=100 | 1. Enter qty=10, rate=100<br>2. Verify | Basic=1000, GST%=18, GST=180, Total=1180. | | |
| TC-PUR-020 | PO — CGST/SGST/IGST breakdown | Intra-state supplier | 1. Verify tax calculation<br>2. Check CGST, SGST fields | CGST = 9%, SGST = 9% (split of 18% GST). | | |
| TC-PUR-021 | PO — Total in words | Total = ₹1,18,000 | 1. Observe Total Amount field<br>2. Check "In word" display | "Rupees One Lakh Eighteen Thousand Only". | | |
| TC-PUR-022 | PO — T&C display | — | 1. View printable PO<br>2. Check footer | Standard T&C shown as specified. | | |
| TC-PUR-023 | PO — printable format | PO exists | 1. Navigate to PO report<br>2. Click Print/PDF | Formatted PO with all details, T&C, calculations. | | |
| TC-PUR-024 | PO Approval — within limit | Amount < ₹2,00,000 | 1. Submit PO<br>2. Approve as Purchase Manager | PO approved. Status = "Issued". | | |
| TC-PUR-025 | PO Approval — escalation | Amount > ₹2,00,000 | 1. Submit high-value PO<br>2. Check approval chain | Routed to Director for approval. | | |
| TC-PUR-026 | PO — block delete after GRN | PO has GRN | 1. Try to delete PO with GRN | Delete blocked. Error: "Cannot delete PO with existing GRN". | | |
| TC-PUR-027 | PO Amendment — before GRN | Issued PO, no GRN | 1. Open PO Amendment<br>2. Change item quantity/rate<br>3. Save | PO amended. Version history maintained. | | |
| TC-PUR-028 | PO Amendment — rate change after GRN | PO has partial GRN | 1. Try to amend rate after GRN | Rate change blocked. Only quantity changes allowed. | | |

### 3.4 Goods Receipt Note (GRN)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PUR-029 | Create GRN — full receipt | Issued PO exists | 1. Open GRN form<br>2. GRN Date = Today<br>3. Select PO Number → supplier, items auto-fetched<br>4. Enter Vehicle Number<br>5. Select Warehouse<br>6. Enter Invoice Number, Date<br>7. For each item: check checkbox, enter Received Qty = Ordered Qty<br>8. Post GRN | GRN posted. GRN Number generated. Stock updated.<br>QC status = "Pending". | | |
| TC-PUR-030 | Create GRN — partial receipt | PO with 5 items | 1. Select PO<br>2. Check only 3 of 5 items<br>3. Enter Received Qty < Ordered for those 3<br>4. Post GRN | Partial GRN created. Remaining 2 items available for future GRN.<br>Stock updated only for received items. | | |
| TC-PUR-031 | GRN — Warehouse dropdown options | — | 1. Click Warehouse field<br>2. Verify options | Options: Wadki w/h, Main w/h 1, Neelo w/h 2, Gurgaon, Bangalore, Client Site. | | |
| TC-PUR-032 | GRN — Client Site conditional field | — | 1. Select "Client Site" as Warehouse<br>2. Observe | Textbox for Client/Site Name appears. | | |
| TC-PUR-033 | GRN — Transport subform visibility | PO with SCOPE = Own | 1. Create GRN against PO with Own transport<br>2. Check form | Transport subform visible: Transporter, Charges, Loading/Unloading. | | |
| TC-PUR-034 | GRN — Transport subform hidden | PO with SCOPE = Supplier | 1. Create GRN against PO with Supplier transport<br>2. Check form | Transport subform hidden. | | |
| TC-PUR-035 | GRN — stock update verification | GRN posted | 1. Note stock before GRN<br>2. Post GRN with Qty=100<br>3. Check stock after GRN | Stock increased by 100. | | |
| TC-PUR-036 | GRN — QC status init | GRN posted | 1. Post GRN<br>2. Check QC status on line items | QC status = "Pending" for all items. | | |
| TC-PUR-037 | GRN — posting timestamp | GRN posted | 1. Post GRN<br>2. Check backend timestamp field | Timestamp recorded. | | |
| TC-PUR-038 | GRN — multiple GRN against same PO | PO with remaining items | 1. Create first partial GRN<br>2. Create second GRN for remaining items | Both GRNs valid. PO fully received after second. | | |

### 3.5 Purchase Reports

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PUR-039 | Open PO Register | Multiple POs exist | 1. Open report<br>2. Filter by status | Shows all POs with outstanding quantities. | | |
| TC-PUR-040 | PO vs GRN Pending report | POs with partial GRN | 1. Open report<br>2. View | Shows ordered vs received quantities and pending balance. | | |
| TC-PUR-041 | Vendor Performance report | Multiple POs, GRNs, QCs | 1. Open report<br>2. View vendor-wise data | Shows delivery timeliness and QC pass % per vendor. | | |
| TC-PUR-042 | Purchase by Item Group | Items in different categories | 1. Open report<br>2. Group by Category | Purchase spend grouped by item category. | | |
| TC-PUR-043 | Price Comparison Report | Rate Comparisons exist | 1. Open report<br>2. Filter by item/supplier | Historical price comparison data. | | |

---

## 4. Quality Control Module

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-QC-001 | Create QC record against GRN | GRN exists with items | 1. Open QC form<br>2. QC Number auto-generated, Date = Today<br>3. Select GRN Number → Supplier auto-fetched<br>4. For each item: enter Inspection Date<br>5. Enter Viscosity, Density, Color, Moisture results<br>6. Enter Accepted Qty, Rejected Qty<br>7. Enter Packaging Quality<br>8. Set QC Status = "Pass"<br>9. Save | QC record created. GRN item QC status updated. | | |
| TC-QC-002 | QC — all items pass | All test results OK | 1. Set QC Status = Pass for all items<br>2. Save | All items accepted. Stock fully available. | | |
| TC-QC-003 | QC — all items fail | Test results out of spec | 1. Set QC Status = Fail for an item<br>2. Accepted Qty = 0, Rejected Qty = Received Qty<br>3. Save | Item rejected. Stock quarantined. | | |
| TC-QC-004 | QC — partial pass | Only some items OK | 1. Accepted Qty < Received Qty for an item<br>2. Set Rejected Qty > 0<br>3. Save | Partial acceptance. Rejected quantity segregated. | | |
| TC-QC-005 | QC — mandatory fields | — | 1. Try saving QC without Inspection Date<br>2. Without entering any results | Validation on mandatory fields works. | | |
| TC-QC-006 | QC — auto-fetch from GRN | GRN with 3 items | 1. Select GRN Number<br>2. Verify line items | All 3 GRN items auto-fetched with Item No. and Name. | | |

---

## 5. Store Module

### 5.1 Material Requisition (MR)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-STO-001 | Create MR for production | Items in stock | 1. Open MR form<br>2. MR Number auto, Date = Today<br>3. Select Requisition Type<br>4. Enter Batch Number (optional)<br>5. Department auto from login<br>6. Requested By = Employee Name<br>7. Select Priority<br>8. Add item: enter Item Code<br>9. Verify auto-fetch of Name, Category, UOM, Available Stock<br>10. Enter Required Qty<br>11. Save | MR created. Available stock shown for each item. | | |
| TC-STO-002 | MR — auto-fetch available stock | Item has stock | 1. Enter Item Code<br>2. Verify Available Stock field | Current stock level displayed. | | |
| TC-STO-003 | MR — stock shortage flag | Required Qty > Available | 1. Enter Required Qty > Available Stock<br>2. Observe | Shortage flag/indicator shown. | | |

### 5.2 Material Issue Slip (MIS)

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-STO-004 | Issue material against MR | Approved MR exists | 1. Open MIS form<br>2. Select MR Number<br>3. MIS Number auto-generated<br>4. Verify Date<br>5. Enter/verify issued quantities<br>6. Post MIS | MIS posted. Stock reduced for issued items. | | |
| TC-STO-005 | MIS — stock deduction verification | Stock before = 100 | 1. Issue Qty = 20 via MIS<br>2. Check stock after | Stock = 80. | | |
| TC-STO-006 | Partial issue from MR | MR requests 50 units | 1. Issue only 30 units via MIS<br>2. Process second MIS for remaining 20 | Both MIS entries valid against same MR. | | |

### 5.3 Material Return & FG Receiving

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-STO-007 | Return unused material | Previously issued material | 1. Open Material Return form<br>2. Select MIS/Item<br>3. Enter Return Qty<br>4. Save | Stock increased by return quantity. | | |
| TC-STO-008 | FG Receiving from production | Completed batch | 1. Open FG Receiving form<br>2. Enter FG details from production<br>3. Enter Qty<br>4. Save | FG stock updated. | | |

---

## 6. Production Module

### 6.1 Production Planning

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PROD-001 | Create Production Plan | SO/WO exists | 1. Open Production Planning form<br>2. Enter Planning No (auto)<br>3. Date, Period, Plant<br>4. Planner Name<br>5. Status<br>6. Total SO/WO Qty vs FG Stock (auto)<br>7. Save | Plan created. Stock vs demand visible. | | |

### 6.2 Production Order & BMR

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PROD-002 | Create Production Order | Plan exists | 1. Open Production Order<br>2. Select System/Product<br>3. Enter Planned Qty<br>4. Save | Order created. | | |
| TC-PROD-003 | Create BMR from Production Order | Order + BOM exist | 1. Open BMR form<br>2. Select Production Order<br>3. RM/PM items auto-fetched from BOM<br>4. Record actual consumption<br>5. Save | BMR created. Actual vs planned variance visible. | | |
| TC-PROD-004 | RM Consumption Entry — actual vs planned | BMR exists | 1. Open RM Consumption Entry<br>2. Record actual RM consumed<br>3. Save | Consumption recorded. Variance calculated. | | |
| TC-PROD-005 | Packing Entry | Batch completed | 1. Open Packing Entry<br>2. Enter FG packed quantity<br>3. Save | FG receipt trigger sent to store. | | |

### 6.3 Production Reports

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PROD-006 | Daily Production Report | BMR entries exist | 1. Open report<br>2. Filter by date | All batches for the date shown. | | |
| TC-PROD-007 | BOM vs Actual Consumption | BMR with actuals | 1. Open report<br>2. View variance per batch | Planned vs actual consumption compared. | | |
| TC-PROD-008 | Production Loss Report | Completed batches | 1. Open report<br>2. View yield data | Yield variance and loss percentage shown. | | |

---

## 7. Project Management Module

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PRJ-001 | Create Project — Area Basis | Systems exist | 1. Open Create Project form<br>2. Enter Project Name, Address<br>3. Select Project Manager<br>4. Execution Base = "Area Basis"<br>5. Start Date, End Date, Project Cost<br>6. Add Systems subform: System, Area, UOM<br>7. Save | Project created. Execution mode = Area Basis. | | |
| TC-PRJ-002 | Create Project — Day Basis | — | 1. Execution Base = "Day Basis"<br>2. Fill other fields<br>3. Save | Project created. Execution mode = Day Basis. | | |
| TC-PRJ-003 | Project — add Transport task | Project exists | 1. Open Project<br>2. Go to Tasks → Transportation<br>3. Enter Budget<br>4. Add Dispatch 1: From, To, Transport Charges<br>5. Add Dispatch 2<br>6. Save | Transport tasks saved with budget and dispatches. | | |
| TC-PRJ-004 | Project — add Application/Execution (Area Basis) | Area Basis project | 1. Open Tasks → Application/Execution<br>2. Add Sub-task A: Subtask Name, Area, Cost, MP<br>3. Add Sub-task B<br>4. Save | Application tasks recorded with area-based costing. | | |
| TC-PRJ-005 | Project — add Manpower (Day Basis) | Day Basis project | 1. Open Tasks → Manpower<br>2. Enter Manpower Budget<br>3. Enter Manpower Count<br>4. Save | Manpower tasks recorded with day-based costing. | | |
| TC-PRJ-006 | Project — add Tools budget | Project exists | 1. Open Tasks → Tools<br>2. Enter Budget for Tools<br>3. Save | Tools budget set. | | |
| TC-PRJ-007 | Project — add Additional Expenses | Project exists | 1. Open Tasks → Additional Expenses<br>2. Enter amounts<br>3. Save | Additional expenses recorded. | | |
| TC-PRJ-008 | Project Dashboard — metrics | Multiple projects exist | 1. Open Project Dashboard<br>2. View metrics | Open Projects, Active PO's, Margins, Issues visible. | | |
| TC-PRJ-009 | Project Dashboard — charts | Data exists | 1. View Execution Target vs Achieve<br>2. View Manpower Cost Monthly<br>3. View Transportation Monthly | Charts render with correct data. | | |
| TC-PRJ-010 | Project — Machinery & Equipment | Project exists | 1. Open Machinery sub-module<br>2. Add new equipment<br>3. Search records | Equipment tracked per project. | | |
| TC-PRJ-011 | Project — Labour management | Project exists | 1. Open Labour sub-module<br>2. Enter Manpower Cost, Count | Labour data recorded. | | |
| TC-PRJ-012 | Edit Project after creation | Project exists | 1. Open existing project<br>2. Modify tasks<br>3. Save | Changes saved. Version history (if applicable). | | |
| TC-PRJ-013 | Project Margins report | Projects with tasks | 1. Open report<br>2. View margin data | Budget vs Actual comparison shown. | | |

---

## 8. Integration & Workflow Tests

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-INT-001 | SO/WO → Project link (Supply+Apply) | WO created in Supply+Apply mode | 1. Create WO in Supply+Apply mode<br>2. Check Project module | Project automatically created/linked from WO data. | | |
| TC-INT-002 | PR → Rate Comparison → PO flow | PR approved | 1. Create and approve PR<br>2. Create Rate Comparison from PR<br>3. Finalise supplier<br>4. Create PO from Rate Comparison | Full chain works. Data flows correctly between forms. | | |
| TC-INT-003 | PO → GRN → Stock | PO issued, GRN posted | 1. Create PO, issue it<br>2. Receive goods via GRN<br>3. Post GRN<br>4. Check stock | Stock updated after GRN posting. | | |
| TC-INT-004 | GRN → QC → Stock available | GRN posted | 1. Post GRN (status = Pending QC)<br>2. Create QC record, pass all items<br>3. Check stock status | Stock becomes fully available after QC pass. | | |
| TC-INT-005 | MR → MIS → Stock deduction | MR approved | 1. Create and approve MR<br>2. Issue material via MIS<br>3. Check stock | Stock reduced by issued quantity. | | |
| TC-INT-006 | BOM → BMR → Production | BOM exists | 1. Create Production Order<br>2. Create BMR → BOM items auto-fetched<br>3. Record actual consumption | BOM data correctly feeds into BMR. | | |
| TC-INT-007 | Production → FG Receiving | Packing entry done | 1. Complete packing<br>2. Receive FG in store | FG stock updated in store module. | | |

---

## 9. Access Control & Security Tests

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-SEC-001 | Role-based form access | Multiple user roles | 1. Login as Store user<br>2. Attempt to access Sales forms | Access denied or hidden. | | |
| TC-SEC-002 | Purchase view-only for Sales | Login as Sales | 1. Open Purchase item forms<br>2. Attempt edit/delete | Edit/Delete disabled. View only. | | |
| TC-SEC-003 | Sales view-only for QC | Login as QC | 1. Open SO/WO form<br>2. Attempt modifications | Read-only access. | | |
| TC-SEC-004 | Admin — full access | Login as Admin | 1. Access all modules<br>2. Create/edit/delete across forms | Full CRUD access everywhere. | | |
| TC-SEC-005 | PO Rate hidden from non-Purchase | Login as Production | 1. Open PO report<br>2. Check Rate column | Rate/Basic Amount/GST columns hidden. | | |
| TC-SEC-006 | Project Cost hidden from non-Admin/PM | Login as Store | 1. Open Project form<br>2. Check Project Cost field | Project Cost field hidden or read-only. | | |
| TC-SEC-007 | Approver limit enforcement | Purchase Executive submits | 1. Executive creates PO > ₹2,00,000<br>2. Purchase Manager tries to approve | Escalated to Director. Manager cannot approve. | | |

---

## 10. Performance & Usability

| ID | Test Case | Prerequisites | Steps | Expected Result | Status | Comments |
|----|-----------|---------------|-------|----------------|--------|----------|
| TC-PERF-001 | Form load time — Item Master | 500+ items | 1. Open Item Master form<br>2. Measure load time | Loads within 3 seconds. | | |
| TC-PERF-002 | Report load — Open PO Register | 200+ POs | 1. Open PO Register report<br>2. Measure load time | Loads within 5 seconds. | | |
| TC-PERF-003 | Mobile form access | Mobile device | 1. Open any form on mobile<br>2. Check layout and usability | Form renders correctly. Fields are usable on touch. | | |
| TC-PERF-004 | Search — Supplier by GSTIN | 100+ suppliers | 1. Search supplier by GSTIN<br>2. Check result time | Search completes within 2 seconds. | | |

---

## 11. UAT Sign-Off

| Department | Module | Tester Name | Date | Overall Status | Comments | Sign-off |
|------------|--------|-------------|------|----------------|----------|---------|
| Admin | Master Data | | | ☐ Pass ☐ Fail | | |
| Sales | SO/WO | | | ☐ Pass ☐ Fail | | |
| Purchase | PR, Rate Comparison, PO, GRN | | | ☐ Pass ☐ Fail | | |
| Store | MR, MIS, Stock | | | ☐ Pass ☐ Fail | | |
| Production | Planning, Order, BMR | | | ☐ Pass ☐ Fail | | |
| QC | QC/QA | | | ☐ Pass ☐ Fail | | |
| Project | Project Management | | | ☐ Pass ☐ Fail | | |
| Finance | Reports, Financial data | | | ☐ Pass ☐ Fail | | |

---

## 12. Test Environment

| Parameter | Value |
|-----------|-------|
| Application URL | Zoho Creator app URL |
| Zoho Domain | India (creator.zoho.in) |
| Browser(s) | Chrome 120+, Firefox 120+, Edge 120+ |
| Mobile | Zoho Creator mobile app (iOS 15+, Android 12+) |
| Test Data | Dummy items, suppliers, customers, projects |
| Users | Test accounts for each role |
