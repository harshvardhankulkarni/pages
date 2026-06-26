# Implementation Artifact — Customer Master

**Form**: Customer Master
**Internal name**: `Customer_Master`
**Dependency**: None. Standalone master data form.

---

## 1. Form Config

| Property | Value |
|----------|-------|
| Internal Name | `Customer_Master` |
| Display Name | Customer Master |
| Datacenter | India (`.in`) |
| Audit Fields | Enabled (app-level — Created By, Created Time, Modified By, Modified Time) |
| Record Name | Customer Code (auto-number) |

---

## 2. Field Configuration Table

| # | Field Label | Field Type | Required | Properties & Validation |
|---|-------------|-----------|----------|------------------------|
| 1 | Customer Code | Auto Number | Yes (auto) | Format: `CUS-{000}`. Starts at 1. Read-only. Unique. |
| 2 | Client Org Name | Text (Single) | Yes | Max length: 150 |
| 3 | Contact Person | Text (Single) | Yes | Max length: 100 |
| 4 | Contact No | Text (Single) | Yes | Max length: 15. Min length: 10 |
| 5 | Alt Contact No | Text (Single) | No | Max length: 15 |
| 6 | Email | Email | Yes | Creator "Email" field type. Validates email format natively. |
| 7 | GST No | Text (Single) | Yes | Max length: 15. Regex validation: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` |
| 8 | PAN | Text (Single) | Yes | Max length: 10. Regex validation: `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` |
| 9 | Regd Address | Text (Multi-line) | Yes | 4 rows visible |
| 10 | Billing Address | Text (Multi-line) | No | 4 rows visible |
| 11 | Shipping Address | Text (Multi-line) | No | 4 rows visible |

### Creator Field Setup Steps

| Field | Insert > Type | Post-Insert Settings |
|-------|--------------|---------------------|
| Customer Code | Auto Number | Set format `CUS-{000}`, check "Read Only" |
| Client Org Name | Text | Check "Required", set max 150 |
| Contact Person | Text | Check "Required", set max 100 |
| Contact No | Text | Check "Required", set max 15, set min length 10 under Custom Validation |
| Alt Contact No | Text | Uncheck "Required", set max 15 |
| Email | Email | Check "Required". Creator handles regex natively via Email type. |
| GST No | Text | Check "Required", set max 15, set Custom Validation > Pattern with GST regex |
| PAN | Text | Check "Required", set max 10, set Custom Validation > Pattern with PAN regex |
| Regd Address | Text (Multi-line) | Check "Required", set rows = 4 |
| Billing Address | Text (Multi-line) | Uncheck "Required", set rows = 4 |
| Shipping Address | Text (Multi-line) | Uncheck "Required", set rows = 4 |

### Regex Validation Strings

```
GST No: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
PAN:    ^[A-Z]{5}[0-9]{4}[A-Z]{1}$
```

**Configuration**: In field properties > Custom Validation > Pattern — paste the regex string exactly. Set error message e.g. "Invalid GST format" / "Invalid PAN format".

---

## 3. UI Layout — 3 Sections

```
┌─ Section: Basic Details ──────────────────────────────────────┐
│ Customer Code [Auto]    Client Org Name [__________________]  │
│ Contact Person [_______] Contact No [____________________]    │
│ Alt Contact No [_______] Email [_________________________]    │
└───────────────────────────────────────────────────────────────┘
┌─ Section: GST/PAN ────────────────────────────────────────────┐
│ GST No [________________]    PAN [_________________________]  │
└───────────────────────────────────────────────────────────────┘
┌─ Section: Addresses ──────────────────────────────────────────┐
│ Regd Address [Multi-line text area - 4 rows]                  │
│ Billing Address [Multi-line text area - 4 rows]               │
│ Shipping Address [Multi-line text area - 4 rows]              │
└───────────────────────────────────────────────────────────────┘
```

### Section Setup in Creator Form Designer

1. **Basic Details** — Add Section, name it "Basic Details"
   - Arrange: Customer Code + Client Org Name on row 1
   - Contact Person + Contact No on row 2
   - Alt Contact No + Email on row 3
   - Use 2-column layout for all rows

2. **GST/PAN** — Add Section, name it "GST/PAN"
   - Arrange: GST No + PAN on same row (2-column)

3. **Addresses** — Add Section, name it "Addresses"
   - Arrange: Regd Address full width, Billing Address full width below, Shipping Address full width below
   - Each address field set to 4 rows height

---

## 4. Report Configuration

**Report Name**: Customer Master List
**Type**: List Report

| Property | Value |
|----------|-------|
| Columns | Customer Code, Client Org Name, Contact Person, Contact No, Email, GST No, PAN, Regd Address, Billing Address, Shipping Address |
| Default Sort | Client Org Name (ascending) |
| Filters | None (all records shown) |
| Search Fields | Client Org Name, GST No, Contact Person |
| Summary | Record count at footer |

### Report Setup Steps

1. Go to Reports tab within Customer Master form designer
2. Click "New Report" > "List Report"
3. Add columns: Customer Code, Client Org Name, Contact Person, Contact No, Email, GST No, PAN, Regd Address, Billing Address, Shipping Address
4. Set default sort: Client Org Name ascending
5. Enable search on: Client Org Name, GST No, Contact Person
6. Enable record count summary
7. Set report sharing permissions (same as form Read permission — see §5)
8. Save as "Customer Master List"

---

## 5. Permissions

Set in Form > Permissions tab. For each profile below, check the corresponding boxes:

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | — | — | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | ✓ | ✓ | ✓ | ✓ |
| Project Manager | ✓ | ✓ | ✓ | ✓ |
| Project Coordinator | ✓ | ✓ | ✓ | ✓ |
| Finance Executive | — | ✓ | — | — |
| Viewer | — | ✓ | — | — |

### Field-Level Security

No field-level restrictions needed for Customer Master (unlike Supplier Master where Account No / IFSC are restricted). All 11 fields are visible to any profile with Read access.

### Report Permissions

Customer Master List report shares the same Read permissions as the form:
- Read access: Admin, Sales Executive, Project Manager, Project Coordinator, Finance Executive, Viewer

---

## 6. Verification Checklist

### Form Creation
- [ ] App created in India datacenter (`creator.zoho.in`)
- [ ] Internal name set to `Customer_Master`
- [ ] Display name set to "Customer Master"
- [ ] Audit fields enabled (app-level)

### Fields
- [ ] Customer Code: Auto Number with format `CUS-{000}`, Read-only
- [ ] Client Org Name: Text (Single), Required, max 150
- [ ] Contact Person: Text (Single), Required, max 100
- [ ] Contact No: Text (Single), Required, max 15, min length 10
- [ ] Alt Contact No: Text (Single), Optional, max 15
- [ ] Email: Email type, Required
- [ ] GST No: Text (Single), Required, max 15, regex pattern set
- [ ] PAN: Text (Single), Required, max 10, regex pattern set
- [ ] Regd Address: Text (Multi-line), Required, 4 rows
- [ ] Billing Address: Text (Multi-line), Optional, 4 rows
- [ ] Shipping Address: Text (Multi-line), Optional, 4 rows

### Validation
- [ ] GST No regex rejects invalid formats (wrong length, wrong character classes)
- [ ] PAN regex rejects invalid formats
- [ ] Contact No rejects fewer than 10 characters
- [ ] Email field validates email format natively
- [ ] All required fields prevent form submission when empty

### UI Layout
- [ ] Section 1: Basic Details — 2-column layout with field pairs as specified
- [ ] Section 2: GST/PAN — 2-column layout with GST No + PAN
- [ ] Section 3: Addresses — 3 full-width multi-line fields

### Reports
- [ ] Report "Customer Master List" created
- [ ] All 11 fields added as columns
- [ ] Default sort: Client Org Name ascending
- [ ] Search enabled on: Client Org Name, GST No, Contact Person
- [ ] Record count summary shown

### Permissions
- [ ] Admin: CRUD
- [ ] Sales Executive: CRUD
- [ ] Project Manager: CRUD
- [ ] Project Coordinator: CRUD
- [ ] Finance Executive: Read only
- [ ] Viewer: Read only
- [ ] All other profiles: No access
- [ ] Report sharing matches form Read permissions
