# Chemsol Zoho Creator ERP Implementation

## Specification Summary
**Original Requirements**: Project-centric ERP system for flooring materials company with 18 forms across Master Data, Sales, Project Management, Procurement, Inventory, Production, and P&L modules. Complete digitization of 18+ paper forms with 75+ automations documented. Project is the root entity for Stream B; SO <code>Sales Type</code> (Supply+Apply vs Supply Only) controls a dual subform and whether a Project is created. Stream A (pre-project procurement) carries NO Project ID. See Two-Stream Architecture.

**Technical Stack**: Zoho Creator (India .in instance), GenAI Builder, HTML5/CSS3, JavaScript, Forms, custom scripts. Mobile responsive design with 768px + 480px breakpoints.

**Target Timeline**: 24-28 weeks total implementation (8-week phase cycles with overlapping deliverables)

## Development Tasks

### [ ] Task 1: Master Data Setup - Purchase Item Muster
**Description**: Create central item catalog master form in Zoho Creator with all Purchase Item Muster fields from specification (Category, Item Code, Name, UOM, HSN, GST%, Min/Max stock, Preferred Supplier, Lead Time, Status). Include field validations and auto-generation logic.
**Acceptance Criteria**: 
- Form loads and displays all 12 fields from specification
- Item Code auto-generates per category
- Min/Max stock alerts configured
- Dropdown options match specification (1.RM, 2.Packaging Material, etc.)

**Files to Create/Edit**: Master form configuration
**Reference**: Section 3.1.1, Lines 112-133

### [ ] Task 2: Master Data Setup - Supplier Master
**Description**: Implement Supplier Master form with all 17 fields (Supplier Code, Name, Type, GSTIN, PAN, Contact info, Bank details, Payment Terms, Credit Days, Status). Configure auto-generation and duplicate prevention.
**Acceptance Criteria**: 
- Form validates GSTIN (15-digit) and PAN format
- Auto-generated Supplier Code on new registration
- All 5 payment terms options configurable
- Status field allows Active/Inactive toggle

**Files to Create/Edit**: Master form configuration
**Reference**: Section 3.1.2, Lines 136-162

### [ ] Task 3: Master Data Setup - System Master
**Description**: Create System Master form for flooring system definitions with 7 fields (System Code, Name, Category, Thickness, UOM, Description, Status). Configure prefix+number auto-generation for System Code.
**Acceptance Criteria**: 
- System Code auto-generates as EP01, PU02, etc.
- All 8 flooring system categories functional (EP/PU/DEM/NUM/ARR/ANTI/ESD/FIL/COV)
- UOM dropdown includes 4 options (SqM/Mtr/Nos)
- Description auto-fetch from Sales/Work Order

**Files to Create/Edit**: Master form configuration
**Reference**: Section 3.1.3, Lines 163-178

### [ ] Task 4: Master Data Setup - BOM Master
**Description**: Implement BOM Master form with parent header fields (BOM ID, System Code, System Name, Revision No) and Subform BOM Line Items (6 fields). Configure auto-fetch relationships from System and Item Masters.
**Acceptance Criteria**: 
- System Code lookup from System Master
- System Name autofetch from System Code
- Item Code lookup from Purchase Item Muster  
- Item Name autofetch from Item Code
- UOM autofetch from Item Muster
- BOM ID auto-generated

**Files to Create/Edit**: BOM form structure with subform
**Reference**: Section 3.1.4, Lines 179-201

### [ ] Task 5: Master Data Setup - Customer/Site Master
**Description**: Create Customer/Site Master form with all 13 fields (Customer Code, Client Name, Contacts, GST/PAN, Addresses, Site details). Configure code auto-generation and duplicate prevention.
**Acceptance Criteria**: 
- Customer Code auto-generates
- GSTIN and PAN validation
- Site information split from org details
- All address fields in main and site sections

**Files to Create/Edit**: Master form configuration
**Reference**: Section 3.1.5, Lines 203-224

### [ ] Task 6: Sales Setup - Sales Work Order Master (SO) — Dual Subform (Supply+Apply / Supply Only)
**Description**: Implement SO form with header + a <code>Sales Type</code> controlling dropdown (Supply+Apply / Supply Only) that toggles between two subforms. **Supply+Apply** → Subform A "System Lines" (System Code lookup from System Master, System Name, Thickness, Area, UOM, Rate, Amount=Area×Rate, Commission%, Warranty, Transport Scope) and auto-creates a Project (Stream B root). **Supply Only** → Subform B "FG Lines" (FG Code lookup from FG Handover/Item Muster, FG Name, Qty, UOM, Rate, Amount=Qty×Rate) with NO Project (direct FG sale, Stream A-adjacent). Client PO is a reference field only.
**Acceptance Criteria**: 
- SO Number auto-generated; Customer lookup from Customer Master
- <code>Sales Type</code> is the controlling field; show/hide rule swaps Subform A / Subform B
- Supply+Apply: ≥1 System line; on accept auto-creates Project; Subform A copied to Project Systems
- Supply Only: ≥1 FG line; NO Project; routes to FG dispatch / customer invoice only
- Area × Rate (or Qty × Rate) formula calculates line Amount; Total Work Order Amount = sum of active subform
- Commission (per-line % in Subform A + header arrangement) applies ONLY to Supply+Apply
- MR Material Allocation + 80% alert fire ONLY for Supply+Apply projects (not Supply Only)

**Files to Create/Edit**: Sales form with dual subforms + controlling field rule
**Reference**: forms.html §2A (Lines 455-571), BRD §3.2 (Lines 256-321), flow.html SO node (Lines 582-690)

### [ ] Task 7: Project Management Setup - Create Project
**Description**: Implement central Project form as root entity with Project ID auto-generation. Include 15 header fields and Systems subform (5 fields) and Task Budget subform (11 fields). Configure autofetch from SO line items.
**Acceptance Criteria**: 
- Project ID auto-generates
- SO lookup fields auto-populates based on user input
- Systems subform filtered from SO System Code
- Task Budget with Category dropdown (4 options)
- Actual Amounts fields feed to P&L
- Execution Base highlights Manpower tasks

**Files to Create/Edit**: Project form with two subforms
**Reference**: Section 3.3, Lines 286-321

### [ ] Task 8: Procurement Setup - Purchase Requisition (PR)
**Description**: Implement PR form with sequential numbering and complete Line Items subform (10 fields). Configure Project ID lookup and auto-fetch cascades from Item Code through Name, Category, UOM.
**Acceptance Criteria**: 
- PR Number auto-generates (PR-YYYY-XXXX format)
- Project ID lookup from Project Master
- Department auto-fetch from user login
- Status workflow: Draft → Pending Approval → Approved → Rejected
- Item Code ↔ Item Name bidirectional autofill
- All line item fields functional with validation

**Files to Create/Edit**: PR form with subform
**Reference**: Section 3.4.1, Lines 327-351

### [ ] Task 9: Procurement Setup - Rate Comparison
**Description**: Create 5-line Supplier Comparison subform (15 fields) with Rate Comparison header (10 fields). Configure lookup from Supplier Master and automatic notifications for missing data.
**Acceptance Criteria**: 
- Supplier 1-5 dropdowns from Supplier Master
- Finalised Supplier and Final Rate in footer
- Auto-notify Purchase dept if data incomplete
- All 5 suppliers comparison grid functional
- Supplier details auto-populate on selection

**Files to Create/Edit**: Rate Comparison form with fixed subform
**Reference**: Section 3.4.2, Lines 354-378

### [ ] Task 10: Procurement Setup - Purchase Order (PO)
**Description**: Implement PO form with dual numbering (RMWAD for Coding, RM for Non-Coding based on RM Type). Header fields: RM Type, PO Number (auto-generated), PO Date, Supplier Code (lookup), Supplier Name (auto-fetch), PR Reference, Bill To, Ship To. Line Items subform with 7 fields: Sr No, Item Code (lookup), Item Name (auto-fetch), HSN (auto-fetch), Quantity, UOM (auto-fetch), Rate (from Rate Comparison), Basic Amount (formula), GST % (auto-fetch), GST Amount (formula), Total Amount (formula). Footer fields: Basic Total (formula), CGST (formula), SGST (formula), IGST (formula), Total Amount (Words), Delivery Date, Payment Terms, Scope of Transport, Mode of Transport.
**Acceptance Criteria**: 
- PO Number auto-generates in RMWAD-YYYY-XXXX format (Coding) or RM-YYYY-XXXX format (Non-Coding)
- Supplier autofetch from Supplier Master with GSTIN validation
- GST split at line level: Basic Amount × GST% = GST Amount, Total = Basic + GST
- CGST/SGST for intra-state (GST/2 each), IGST for inter-state (full GST)
- Printable PO includes e-way bill, COA, batch numbers, quality clause, T&C
- Transport terms and delivery date configurable per PO

**Files to Create/Edit**: PO form with subform and GST calculations
**Reference**: Section 3.4.3, Lines 381-419

### [ ] Task 11: Procurement Setup - Goods Receipt Note (GRN)
**Description**: Implement GRN form with header fields: GRN Number (auto-generated after posting, not on create), GRN Date, PO Number (lookup), Supplier Code (auto-fetch), Supplier Name (auto-fetch), Vehicle Number, Warehouse (dropdown: 1.Wadki, 2.Main, 3.Neelo, 4.Gurgaon, 5.Bangalore, 6.Client Site), Client/Site Name (conditional if Warehouse = Client Site), Invoice Number, Invoice Date. Line Items subform with 9 fields: Checkbox, Item Code (auto-fetch), Item Name (auto-fetch), Ordered Qty (auto-fetch), Received Qty, QC Status (dropdown: Pending/Pass/Fail), Packing Quality (dropdown: Good/Damaged/Partial). Transport subform (1 row, conditional if PO Scope = Own) with 5 fields: Transporter Name, Transportation Charges, Local Transport, Loading/Unloading Charges.
**Acceptance Criteria**: 
- GRN Number auto-generated **after posting** (not create)
- PO lookup auto-fetches Supplier and Project ID
- Warehouse dropdown with 6 options including conditional Client Site
- Item checkbox selects items for partial GRN processing
- QC Status and Packing Quality tracking per item
- Stock added to inventory only after posting with timestamp logged
- Transport charges calculated and allocated per line item

**Files to Create/Edit**: GRN form with line item checkboxes and conditional transport subform
**Reference**: Section 3.4.4, Lines 422-454

### [ ] Task 12: Procurement Setup - QC/QA
**Description**: Implement QC form with GRN lookup and Inspection Line Items subform (12 fields). Configure auto-fetch from GRN and complete inspection tracking.
**Acceptance Criteria**: 
- QC Number auto-generated (QC-YYYY-XXXX)
- GRN lookup triggers inspection item fetch
- Viscosity, Density, Color, Moisture results
- Accepted/Rejected Qty tracking
- Packaging Quality and QC Status options
- Auto-fetch all items from GRN reference

**Files to Create/Edit**: QC form with inspection subform
**Reference**: Section 3.4.5, Lines 457-483

### [ ] Task 13: Inventory Setup - Material Requisition (MR)
**Description**: Implement MR form with Project ID lookup and Line Items subform (8 fields). Configure auto-fetch cascades from Item Code to Name, Category, UOM, and Available Stock.
**Acceptance Criteria**: 
- MR Number auto-generates (MR-YYYY-XXXX)
- Project ID lookup from Project Master
- Required vs Available Stock comparison
- Department and Requested By auto-fetch
- Batch Number and Priority fields
- Stock validation on creation

**Files to Create/Edit**: MR form with auto-fetch subform
**Reference**: Section 3.5.1, Lines 488-513

### [ ] Task 14: Inventory Setup - Material Issue Slip (MIS)
**Description**: Implement MIS form with MR lookup and Line Items subform (6 fields). Configure auto-fetch from MR and balance calculation (Required − Issued).
**Acceptance Criteria**: 
- MIS Number auto against MR reference
- Items auto-fetched from MR
- Balance Qty calculated formula
- Issued By and Handover To supervisor tracking
- Stock deducted on posting
- All MR data accurately copied

**Files to Create/Edit**: MIS form with balance tracking
**Reference**: Section 3.5.2, Lines 516-539

### [ ] Task 15: Production Setup - Production Planning
**Description**: Implement Production Planning form with 10 fields (Planning, Dates, Quantities). Configure SO/WO qty and FG Stock autofetch for net requirement calculation.
**Acceptance Criteria**: 
- Planning Number reference to MR Sheet
- Planning Period dropdown (Week/Month)
- SO/WO Qty auto-fetch from MR Sheet
- FG Stock auto-fetch from inventory
- Net Production Requirement formula
- Status workflow (Planned/In Progress/Completed)

**Files to Create/Edit**: Production Planning form
**Reference**: Section 3.6.1, Lines 594-613

### [ ] Task 16: Production Setup - Batch Manufacturing Record (BMR)
**Description**: Implement comprehensive BMR form with three subforms (Raw Materials 5 fields, Process Parameters 5 fields, QC Results 5 fields). Configure lookups from Master Data.
**Acceptance Criteria**: 
- BMR Number auto-generated
- Raw Materials lookup from Purchase Item Muster
- Process parameters tracking
- QC test results with Pass/Fail
- Production Order reference
- Status tracking across production

**Files to Create/Edit**: BMR form with three subforms
**Reference**: Section 3.6.2, Lines 633-664

### [ ] Task 17: Production Setup - Production Order
**Description**: Implement Production Order form with 7 fields (Order Details, Scheduling, Status). Configure lookup from Production Planning and System Master.
**Acceptance Criteria**: 
- Production Order Number auto-generated
- MR/Planning Reference lookup
- System Code lookup from System Master
- Start/End date scheduling
- Status workflow (Planned/In Progress/Completed)

**Files to Edit**: Production Order form
**Reference**: Section 3.6.3, Lines 616-631

### [ ] Task 18: P&L Statement (Computed View)
**Description**: Configure Project P&L Statement with all 17 line items (14 cost categories + 3 summaries). Implement formulas across all transactional forms.
**Acceptance Criteria**: 
- Auto-calculated on Project Close
- Revenue from SO System subtable
- All 14 cost components from transactional forms
- Gross Margin = Total Revenue - Total Cost
- Margin % = (Gross Margin / Total Revenue) × 100
- 15% margin threshold alert

**Files to Edit**: P&L computed view configuration
**Reference**: Section 3.7, Lines 717-742

### [ ] Task 19: Authentication & User Management
**Description**: Implement Zoho Creator user access control and authentication with 7 role-based access groups (Purchase Entry, Approve, Review, Store Entry, Production Entry, Sales Entry, Project Manager, Coordinator, QC Entry, Finance, Admin). Configure approval matrix and department-specific permissions.
**Acceptance Criteria**: 
- Role-based access control functional
- User lookup fields for employee assignments
- Department filters for dashboards
- Approval matrix for PR/PO limits
- 4 approval levels for financial controls

**Files to Edit**: User management and authentication setup
**Reference**: BRD Section 2.4, PRD Project Management section

### [ ] Task 20: Project Dashboard
**Description**: Create comprehensive Project dashboard with real-time data views for all seven departments. Filterable by Project ID with key metrics and KPIs.
**Acceptance Criteria**: 
- Department dashboards (7 total)
- Project-level filters for all reports
- Real-time auto-refresh functionality
- Key metrics: Open POs, Stock levels, Net requirements, Task status
- Each department configurable independently

**Files to Edit**: Dashboard configuration for all departments
**Reference**: BRD Section 2.4

## Quality Requirements
- [ ] All forms follow Zoho Creator GenAI convention (HEADER/SUBFORM/FOOTER structure)
- [ ] No background processes in any commands
- [ ] No server startup commands (assume development server running)
- [ ] Mobile responsive design with 768px + 480px breakpoints
- [ ] All 18 forms from specification implemented
- [ ] Auto-fetch relationships functional across all forms
- [ ] Project ID flows through Stream B transactions only (SO Supply+Apply → Project → PR → PO → GRN → QC → MR → MIS → Production → FGHM [inline acceptance, FGAN eliminated]). Stream A (Supply Only FG sales / pre-project procurement) carries NO Project ID.
- [ ] Budget tracking: Execution / Manpower / Tools / Overhead categories
- [ ] GST compliance: All GST calculations and validations
- [ ] Supplier Credit Limit monitoring (80% alert)
- [ ] Period Close with 6-item checklist
- [ ] All 75+ automations from specification implemented

## Technical Notes
**Development Stack**: Zoho Creator (India .in instance), GenAI Builder, HTML5/CSS3, JavaScript, Forms
**Special Instructions**: All forms follow Zoho Creator Subform convention. Feed each form section directly into Zoho Creator GenAI. **Two-Stream Architecture**: Stream A = pre-project stock procurement (no Project ID); Stream B = project-centric (Project ID root). The SO <code>Sales Type</code> toggle decides which stream an order enters — Supply+Apply → Stream B (Project created), Supply Only → Stream A-adjacent direct FG sale (no Project).
**Timeline Expectations**: 8-week phase cycles with overlapping deliverables, 24-28 weeks total for complete implementation