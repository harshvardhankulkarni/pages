# Phase 1: Master Data & Admin - Research

> **Domain:** Zoho Creator platform patterns for low-code business application development
> **Researched:** 2026-06-26
> **Context:** Chemsol - industrial flooring solutions (epoxy, PU, anti-static, ESD)
> **Phase scope:** 8 master data forms (Item, System, BOM, Supplier, Customer, Store, Bin Location, User Access)

---

## Research Topics

### 1. Zoho Creator Auto-Number Patterns

#### 1.1 Native Auto-Number Field Type

Zoho Creator provides a built-in `Auto Number` field type that auto-generates sequential values.

**Format syntax:**
- `{000}` = 3-digit zero-padded sequential (001, 002, ..., 999)
- `{0000}` = 4-digit (0001, 0002, ...)
- `{YY}` = 2-digit year, `{YYYY}` = 4-digit year
- `{MM}` = 2-digit month

**Phase 1 Auto-Number Formats:**

| Form | Format | Example |
|------|--------|--------|
| Item Master (RM) | `RM-{000}` | RM-001 |
| Item Master (PM) | `PM-{000}` | PM-001 |
| Item Master (FG) | `FG-{000}` | FG-001 |
| Item Master (CON) | `CON-{000}` | CON-001 |
| Item Master (SVC) | `SVC-{000}` | SVC-001 |
| System Master | `{prefix}-{000}` | EP-001, PU-001, DEM-001 |
| Supplier Master | `SUP-{000}` | SUP-001 |
| Customer Master | `CUS-{000}` | CUS-001 |
| Store Master | `ST-{000}` | ST-001 |
| Bin Location | `BIN-{000}` | BIN-001 |
| User Access | `USR-{000}` | USR-001 |

**Category-Dependent Prefix Options:**

Option A - Multiple Auto-Number Fields (separate field per category, conditional visibility)

Option B - Deluge-Generated Code (hidden numeric auto-number + Deluge On Submit)

Option C - Formula Auto-Number (if Creator 2026 supports it natively)

**Best Practices:**
1. Always make auto-number fields Read-Only
2. Hidden auto-number fields for sequential backing
3. Reset sequences only for testing
4. Start sequences at 1 for fresh apps
5. Set Unique constraint on text-based code fields
6. Handle data imports separately (existing codes)

#### 1.2 Best Practices Summary

- Use native auto-number fields with custom format strings (per D-16 from CONTEXT.md)
- Item Master: category-dependent prefix requires a strategy choice (Options A/B/C above)
- System Master: prefix is part of the system code, not a category selection
- All auto-number fields should be read-only and hidden if used only for sequential backing
- For year-prefix patterns (future phases): use `{YY}-{0000}` format

---
### 2. Lookup & Auto-Fetch Configuration

#### 2.1 Native Lookup Field Types

Zoho Creator offers two native mechanisms for cross-form data linkage:

**A. Lookup Field (Dropdown / Autocomplete):**
- Creates a relationship between two forms (foreign key)
- Displays records from parent form in dropdown or autocomplete search
- Automatically indexes the relationship for performance
- Config: Field > Field Type = Lookup > Select target form > Select display field

**B. Subform:** See Research Topic 6 for 1:N patterns

#### 2.2 Cascading Lookup (Auto-Fetch) Patterns

**Pattern A - On-Change Fetch (Deluge on Field Update):**
- Trigger: On User Input for the lookup field
- Fetches the related record and populates dependent fields
- Example (BOM Item Code -> Item Name + UOM):
  ```deluge
  item_id = input.Item_Code;
  if(item_id != null) {
      data = zoho.creator.getRecordById("chemsol", "Item_Master", item_id);
      input.Item_Name = data.get("Item_Name");
      input.UOM = data.get("UOM");
  }
  ```

**Pattern B - Creator's Built-in "Add Lookup Fields":**
- Zero-code option when adding a Lookup field in form designer
- Auto-populates selected fields on lookup selection
- Limitation: direct 1:1 copy only, no conditional logic

**Pattern C - On-Load Fetch (Deluge on Form Load):**
- For forms opening with a pre-selected parent (editing existing record)
- Use On Load workflow to populate fields from the parent record

#### 2.3 Phase 1 Auto-Fetch Requirements

| Form | Trigger | Fetch Fields | Mechanism |
|------|---------|--------------|-----------|
| BOM Master | Item Code (Lookup) | Item Name, UOM | On-Change + On-Load |
| BOM Master | System Code (Lookup) | System Name | On-Change + On-Load |
| Item Master | Preferred Supplier | Supplier Name | On-Change (or built-in) |
| Bin Location | Store Name | Store Type, Location | On-Change |

#### 2.4 Best Practices

1. Use Creator's built-in Add Lookup Fields first (zero code)
2. Bind both directions: Item Code -> Item Name AND Item Name -> Item Code
3. Handle null values: check `if(item_id != null)` before fetching
4. Avoid circular lookups (Form A -> Form B -> Form A)
5. Use Autocomplete mode for 500+ records instead of dropdown

---
### 3. Form Permissions

#### 3.1 Zoho Creator Profile System

Creator provides a built-in Profiles system for access control:

- **Profiles:** Named permission sets (e.g., Admin, Purchase Manager)
- **Form Actions:** Create, Read, Update, Delete per profile per form
- **Report Actions:** View, Export, Print per profile per report
- **Field Actions:** View, Edit per profile per field (field-level security)
- **Record-Level Access:** Criteria-based sharing rules

#### 3.2 Phase 1 Permission Setup

**13 Creator profiles to create (one per role from USER-ROLES.md):**
Admin, Purchase Manager, Purchase Executive, Store Manager, Store Keeper,
Production Manager, Production Executive, QC Inspector, Sales Executive,
Project Manager, Project Coordinator, Finance Executive, Viewer

**Form Permissions Matrix (abbreviated from USER-ROLES.md Section 2.1):**

| Form | Admin | Pur.Mgr | Sto.Mgr | Prod.Mgr | QC | Sales | Proj.Mgr | Fin. | Viewer |
|------|-------|---------|---------|----------|-----|-------|----------|------|--------|
| Item Master | CRUD | CRUD | CRUD | CRUD | CRUD | V | -- | -- | V |
| System Master | CRUD | -- | -- | CRUD | -- | CRUD | CRUD | -- | V |
| BOM Master | CRUD | -- | -- | CRUD | CRUD | -- | -- | V | V |
| Supplier Master | CRUD | CRUD | -- | -- | -- | -- | -- | R | V |
| Customer Master | CRUD | -- | -- | -- | -- | CRUD | CRUD | R | V |
| Store Master | CRUD | -- | CRUD | R | -- | -- | -- | -- | V |
| Bin Location | CRUD | -- | CRUD | -- | -- | -- | -- | -- | V |
| User Access | CRUD | -- | -- | -- | -- | -- | -- | -- | -- |

**Legend:** C=Create, R=Read, U=Update, D=Delete, V=View-only

#### 3.3 Built-in vs Custom Deluge

| Layer | Built-in Creator | Custom Deluge |
|-------|-----------------|---------------|
| Form-level C/R/U/D | Native profiles | Not needed for Phase 1 |
| Field-level visibility | Native (per profile per field) | Not needed for Phase 1 |
| Record-level access | Criteria-based sharing | User Access (restrict to Admin) |

**Recommendation:** Use 100% native Creator profiles for Phase 1. No Deluge permission checks needed.

#### 3.4 Configuring Permissions in Creator

- Profiles: Settings > Users & Permissions > Profiles (create 13 profiles)
- Users: Settings > Users & Permissions > Users (assign to profiles)
- Form permissions: Form > Permissions tab (set C/R/U/D per profile)
- Field permissions: Field > Properties > Access tab (set View/Edit per profile)
- Report permissions: Report > Share (set View/Export/Print per profile)
- Record sharing: Form > Permissions > Advanced > Criteria-based rules

---
### 4. Creator Report Builder

#### 4.1 Report Types in Creator

| Report Type | Creator Feature | Phase 1 Use |
|-------------|----------------|-------------|
| List Report | Report Builder > List | All master data listings |
| Summary Report | Report Builder > Summary | Count of items by category |
| Pivot Report | Report Builder > Pivot | Cross-tabulation (future) |
| Printable Doc | Page Builder | PO/GRN print (future phases) |

Every form automatically gets a default List View. Enhanced reports are created via Report Designer.

#### 4.2 Configuring Phase 1 Reports

**Item Master Report (Purchase Item Master per BRD):**
- Columns: Category, Item Code, Item Name, UOM, HSN Code, Min Stock, Max Stock, Standard Rate, Preferred Supplier, Lead Time
- Default filter: By Category (e.g., show only RM)
- Grouping: By Category
- Search: Full-text on Item Name and Item Code
- Sorting: Item Code ascending

**Other Phase 1 Reports (one per form):**
- System Master List: Code, Name, Thickness, UOM, Description
- BOM Master List: System Code, Item Code, Quantity, UOM (grouped by System)
- Supplier Master List: All 13 fields, searchable by Name/GSTIN/PAN
- Customer Master List: All 11 fields
- Store Master List: Code, Name, Type, Location
- Bin Location List: Store, Rack, Shelf, Bin
- User Access List: User Name, Department, Role, PR/PO Limits

#### 4.3 Report Features

1. Filters: Predefined + ad-hoc at runtime
2. Grouping: By any field
3. Summaries: Sum, Count, Average, Min, Max on numeric fields
4. Chart Integration: Bar/pie/line charts
5. Export: CSV, XLS, PDF
6. Conditional Formatting: Highlight rows (e.g., stock < Min Stock in red)

#### 4.4 Report Permissions

- Config: Report > Share > Select Profile > View / Export / Print / No Access
- Per USER-ROLES.md Section 2.8: Viewer gets View-only; Admin gets full access

#### 4.5 Best Practices

1. Limit columns to essential fields
2. Use meaningful default filters
3. Name reports consistently: [Form Name] - [Type]
4. Enable full-text search on name and code fields
5. Set default sort by Code or Name ascending
6. Use Summary footers (record count)

---
### 5. Deluge Validation Patterns

#### 5.1 Three Validation Layers

**Layer 1 - Field Properties (No Deluge):**
- Required, Unique, Min/Max length, Min/Max value, Pattern/Regex
- Phase 1 usage: GSTIN length (15), PAN (10), IFSC (11), Email regex

**Layer 2 - Form Validation Rules (No Deluge):**
- Settings > Form > Validation: simple cross-field conditions
- Phase 1 usage: Min Stock <= Max Stock, at least one BOM item

**Layer 3 - Deluge On Submit (Complex Logic):**
- Used when built-in rules cannot handle the validation
- Standard pattern: throw an error message to block submission

#### 5.2 Standard Deluge Validation Pattern

```deluge
// Trigger: On Submit - Item Master
if (input.Min_Stock > input.Max_Stock && input.Max_Stock != null)
{
    throw "Min Stock cannot be greater than Max Stock.";
}

// Duplicate check
existing = zoho.creator.getRecords("chemsol", "Item_Master",
    "Item_Name == " + q(input.Item_Name), 1, 0);
if (existing.size() > 0 && existing.get(0).get("ID") != input.ID)
{
    throw "An item with this name already exists.";
}
```

#### 5.3 Phase 1 Validations

| Form | Validation | Layer |
|------|-----------|-------|
| Item Master | GST% between 0-100 | Layer 3 (Deluge) |
| Item Master | Min Stock <= Max Stock | Layer 2 or 3 |
| Item Master | Unique Item Name (soft check) | Layer 3 (Deluge) |
| Supplier Master | GSTIN length = 15 | Layer 1 (Field regex) |
| Supplier Master | PAN length = 10 | Layer 1 (Field regex) |
| Supplier Master | IFSC length = 11 | Layer 1 (Field regex) |
| Supplier Master | Email format | Layer 1 (Field regex) |
| BOM Master | Quantity > 0 | Layer 3 (Deluge on submit) |
| BOM Master | No duplicate items in BOM | Layer 3 (Deluge) |
| Customer Master | GSTIN length = 15 | Layer 1 (Field regex) |
| Customer Master | Contact No >= 10 digits | Layer 1 (Min length) |

#### 5.4 Validation Priority (per D-18)

1. Field Properties (required, unique, min/max, regex) - first choice
2. Form Validation Rules (cross-field simple conditions) - second choice
3. Deluge On Submit (complex multi-field logic) - last resort

---
### 6. Subform / Linked Form Patterns

#### 6.1 One-to-Many in Creator

**A. Subform (Embedded Form):**
- Child table embedded within parent form
- Stored as separate data table, displayed as grid
- Best for small child sets (< 20 rows)

**B. Linked Form (Lookup-based):**
- Child records in separate form with Lookup to parent
- Lazy-loads related records; better for mobile
- Best for large child sets or independent child entry

#### 6.2 BOM Master Design

**Option A - BOM as Subform of System Master:**
- One form: System + BOM items together
- Pros: All-in-one management
- Cons: System Master becomes large; less modular

**Option B - Separate BOM Master Form (Recommended):**
- BOM Master has header: System Code (Lookup), System Name (Auto-fetch)
- BOM Master has subform: Item Code, Item Name, Quantity, UOM
- Pros: Clean separation, modular, aligns with BRD Section 3.1.3

**Recommendation: Option B** - separate BOM Master form with subform for line items.

#### 6.3 BOM Subform Field Spec

| Field | Type | Behavior |
|-------|------|----------|
| Item Code | Lookup (Item Master) | Autocomplete |
| Item Name | Text (Read-only) | Auto-fetched from Item Code |
| Quantity | Decimal (Required) | User entry |
| UOM | Text (Read-only) | Auto-fetched from Item Master |

#### 6.4 BOM Layout Diagram

```
+--------------------------------------------------+
|  BOM MASTER                                       |
|  System Code: [Lookup]  System Name: [Auto]     |
|  Description: [Multi-line]                      |
|                                                  |
|  BOM Items (Subform):                            |
|  Item Code | Item Name | UOM  | Qty  | Delete |
|  [Lookup]  | [Auto]    |[Auto]| [__] |   X    |
|  [+ Add Item]                                    |
|                                                  |
|  [Save]  [Cancel]                                |
+--------------------------------------------------+
```

#### 6.5 Subform Best Practices

1. Limit subform rows to < 50 (BOM: 3-15 rows, fine)
2. Use Add Row button (not pre-populated empty rows)
3. Enable Delete Row for each row
4. Auto-fetch within each subform row on Item Code selection
5. Validate parent form On Submit: check duplicates, zero qty

---
### 7. India Datacenter (.in) Best Practices

#### 7.1 Domain Configuration

Zoho Creator operates from multiple global datacenters. Chemsol uses the **India (.in)** datacenter.

**Key URLs:**
- Creator App: `https://creator.zoho.in` (not `.com`)
- API base: `https://creator.zoho.in/api/v2/`
- OAuth authorize: `https://accounts.zoho.in/oauth/v2/auth`
- OAuth token: `https://accounts.zoho.in/oauth/v2/token`

#### 7.2 API Call Patterns

**Internal Creator API (no OAuth needed):**
```deluge
// Creator automatically uses the correct datacenter
records = zoho.creator.getRecords("chemsol", "Item_Master",
    "Category == 'RM'", 200, 0);
```

**External API calls (invokeurl for future integrations):**
```deluge
response = invokeurl [
    url: "https://books.zoho.in/api/v3/contacts"  // .in domain
    type: GET
    connection: "zohobooks_connection"
];
```

**Important:** All API URLs must use `.in` domain. Never use `.com`, `.eu`, `.jp`.

#### 7.3 Deployment Checklist

- [ ] Creator app region set to India during initial setup (not changeable after)
- [ ] All invokeurl calls use `.in` domain
- [ ] External integrations use India-region OAuth endpoints
- [ ] App shared URL uses creator.zoho.in format
- [ ] Mobile users connect via Zoho Creator app (India datacenter)

#### 7.4 Performance Notes

- India datacenter has same SLA as global datacenters
- For India-based users, `.in` is optimal (lowest latency)
- Zoho maintains geo-redundant backups within India region

---
### 8. UI Layout Conventions

#### 8.1 Section Grouping Strategy

General rule (per D-18): single section for <10 fields, grouped sections for 10+ fields.

**Phase 1 Section Plan:**

| Form | Fields | Sections |
|------|--------|----------|
| Item Master | 11 | 2: Basic Details, Inventory & Purchase |
| System Master | 5 | 1: System Details |
| BOM Master | 2 + subform | 1: BOM Details + subform |
| Supplier Master | 15 | 3: Basic, Contact, Bank & Terms |
| Customer Master | 11 | 3: Basic, GST/PAN, Addresses |
| Store Master | 4 | 1: Store Details |
| Bin Location | 4 | 1: Bin Location Details |
| User Access | 5 | 1: User Access & Approval Limits |

#### 8.2 Field Ordering Principles

1. Code fields first (record identifier)
2. Name/Description next (what is this?)
3. Classification fields (Category, Type, Department)
4. Detail fields (Numbers, amounts)
5. Reference/lookup fields (links to other forms)
6. Addresses at the bottom (multi-line)

#### 8.3 Item Master Layout

```
Section: Basic Details
  1. Category of Purchase Item [Dropdown]
  2. Purchase Item Code [Auto-number/Text]
  3. Purchase Item Name [Text]
  4. UOM [Dropdown]
  5. HSN Code [Text]
  6. GST % [Decimal]
Section: Inventory & Purchase
  7. Min Stock [Number]    8. Max Stock [Number]
  9. Standard Rate [Currency]  10. Preferred Supplier [Lookup]
  11. Lead Time (Days) [Number]
```

#### 8.4 Supplier Master Layout

```
Section: Basic Details
  1. Supplier Code [Auto-number]  2. Supplier Name [Text]
  3. Supplier Type [Dropdown]
  4. GSTIN [Text]   5. PAN No [Text]
Section: Contact
  6. Contact Person [Text]  7. Mobile No [Text]
  8. Alternate Mobile [Text]  9. Email ID [Text]
  10. Address [Multi-line]
  11. Pincode [Text]
Section: Bank & Terms
  12. Bank Name [Text]  13. Account No [Text]
  14. IFSC Code [Text]
  15. Payment Terms [Dropdown]  16. Credit Days [Number]
```

#### 8.5 Customer Master Layout

```
Section: Basic Details
  1. Customer Code [Auto-number]
  2. Client Org Name [Text]  3. Contact Person [Text]
  4. Contact No [Text]  5. Alt Contact No [Text]
  6. Email [Text]
Section: GST/PAN
  7. GST No [Text]  8. PAN [Text]
Section: Addresses
  9. Regd Address [Multi-line]
  10. Billing Address [Multi-line]
  11. Shipping Address [Multi-line]
```

#### 8.6 Layout Best Practices

1. Use 2-column layout for paired fields (Min/Max Stock, GSTIN/PAN)
2. Auto-number fields at top-right (standard UX convention)
3. Addresses in their own section (multi-line needs vertical space)
4. Use field descriptions for guidance (e.g., "Enter 15-character GSTIN")
5. Set field widths: Code 30%, Text full, Numeric 20-30%
6. Give subforms their own section with clear header
7. Mobile: sections stack vertically; keep headers short

#### 8.7 UI Controls Reference

| Control | Phase 1 Usage |
|---------|---------------|
| Text (Single) | Names, codes, HSN, PAN, GSTIN, IFSC, Contact |
| Text (Multi-line) | Addresses, Description |
| Number | Min/Max Stock, Lead Time, Credit Days, Quantity |
| Decimal (Currency) | Standard Rate, PR/PO Limit |
| Dropdown | Category, UOM, Store Type, Dept, Role, Payment Terms |
| Lookup | Preferred Supplier, Store Name |
| Lookup (Autocomplete) | Item Code, System Code (large lists) |
| Auto Number | All system-generated codes |
| Subform | BOM line items |
| Checkbox | Is Active |
| Audit fields | Created By, Created Time, Modified By, Modified Time |

---
## Recommendations for Phase 1

### 1. Auto-Numbering Strategy

**Recommendation:** Use **Option B (Deluge-Generated Code)** for Item Master (category-dependent prefix).
- Hidden numeric auto-number field + Deluge On Submit constructs the code
- Item Code text field marked as **Unique** for uniqueness enforcement
- Other forms: use native auto-number with `{prefix}-{000}` format strings

### 2. Lookup & Auto-Fetch

**Recommendation:** Use Creator built-in "Add Lookup Fields" where possible (zero code).
- Deluge On-User-Input only for: subform rows, bi-directional fetch, conditional logic
- BOM: On-Change Deluge on Item Code for Item Name + UOM auto-fetch

### 3. Permissions

**Recommendation:** Use 100% native Creator profiles (13 profiles, one per USER-ROLES.md role).
- No Deluge permission checks needed for Phase 1
- Form-level C/R/U/D per form Permissions tab
- Field-level: hide Rate from non-Purchase profiles
- Record-level: restrict User Access to Admin only

### 4. Reports

**Recommendation:** One standard list report per form (8 total). Built-in List Report builder.
- Default filters, full-text search, meaningful columns, summary footer

### 5. Validation

**Recommendation:** Priority order: Field Properties > Form Validation Rules > Deluge On Submit.
- Deluge only for: cross-field comparisons, duplicate checks, format validation beyond regex

### 6. BOM Subform Design

**Recommendation:** Separate BOM Master form (not subform of System Master) with subform for line items.
- Clean separation, aligns with BRD Section 3.1.3, keeps System Master lean

### 7. India Datacenter

**Recommendation:** Ensure app is created in India datacenter. All API URLs use .in domain.
- Already documented in ARCHITECTURE.md Section 1

### 8. UI Layout

**Recommendation:** Follow section plans from Section 8.
- 2 sections for Item Master (11 fields)
- 3 sections for Supplier Master (15 fields)
- 3 sections for Customer Master (11 fields)
- 2-column layout for paired fields

### Summary: Form Build Order

1. Item Master (no dependencies)
2. Supplier Master (no dependencies, referenced by Item Master)
3. Customer Master (no dependencies)
4. Store Master (no dependencies)
5. System Master (no dependencies, foundation for BOM)
6. Bin Location Master (depends on Store Master lookup)
7. BOM Master (depends on System Master + Item Master)
8. User Access & Approval Matrix (no form dependencies)

---
## Appendices

### A. Auto-Number Format Reference

| Pattern | Output |
|---------|--------|
| `{000}` | 001, 002, ..., 999 |
| `{0000}` | 0001, 0002, ..., 9999 |
| `{yy}` | 26 (for year 2026) |
| `{yyyy}` | 2026 |
| `{mm}` | 06 |
| `{dd}` | 26 |
| `RM-{000}` | RM-005 |
| `PO-{yy}-{0000}` | PO-26-0042 |

### B. Dropdown Values Reference

| Field | Values | Source |
|-------|--------|--------|
| Item Category | RM, PM, FG, CON, SVC | CONTEXT.md D-02 |
| UOM (Items) | Sq.Ft, Sq.Mtr, Kg, Litre, Nos, Meter, Roll, Packet, Bag, Drum, Set, Hour, Day | CONTEXT.md D-12 |
| UOM (Systems) | Sq.Ft, Sq.Mtr | BRD Section 3.1.2 |
| Store Type | RM, FG, QC, Site | CONTEXT.md D-10 |
| Payment Terms | Advance, 7 Days, 15 Days, 30 Days, 45 Days, 60 Days, On Delivery | CONTEXT.md Specific Ideas |
| System Prefix | EP, PU, DEM, NUM, ARR, ANTI, ESD, FIL, COV | BRD Section 3.1.2 |
| Department | Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1, Project Manager 2 | BRD Section 6 |
| Role | Admin, Purchase Manager, Purchase Executive, Store Manager, Store Keeper, Production Manager, Production Executive, QC Inspector, Sales Executive, Project Manager, Project Coordinator, Finance Executive, Viewer | USER-ROLES.md Section 1 |

### C. Field Counts & Build Effort

| Form | Fields | Sections | Build Effort |
|------|--------|----------|-------------|
| Item Master | 11 | 2 | Medium |
| System Master | 5 | 1 | Low |
| BOM Master | 2 + subform (4) | 1 + subform | Medium |
| Supplier Master | 15 | 3 | High |
| Customer Master | 11 | 3 | Medium |
| Store Master | 4 | 1 | Low |
| Bin Location | 4 | 1 | Low |
| User Access | 5 | 1 | Low |

### D. Creator Platform Limits

| Limit | Value | Phase 1 Impact |
|-------|-------|----------------|
| Max fields per form | 200 | 4-15 fields per form. No issue. |
| Max subform rows | 1000/record | BOM: 3-15 rows. No issue. |
| Max records per form | Unlimited | No concern. |
| Auto-number max | 999,999,999 | No concern. |
| Deluge timeout | 5 minutes | Phase 1 validations are instant. |
| File attachment | 20 MB max | Not applicable to Phase 1. |
| Lookup performance | ~500 records | Use Autocomplete for large lists. |

---

*Research compiled: 2026-06-26*
*For: Phase 1 - Master Data & Admin*
*Applies to: Chemsol Zoho Creator Application - India Datacenter (.in)*
