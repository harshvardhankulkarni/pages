# Supplier Master — Implementation Artifact

## 1. Form Configuration

| Property | Value |
|----------|-------|
| Form name (displayed) | Supplier Master |
| Internal name | `Supplier_Master` |
| App | Chemsol |
| Datacenter | India (`.in`) |
| Audit fields | Enabled (Created By, Created Time, Modified By, Modified Time) — inherited from app level |
| Auto-number field | Supplier Code — format `SUP-{000}`, starts at 1, read-only |

---

## 2. Field Configuration Table

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Supplier Code | Auto Number | Yes (auto) | Format: `SUP-{000}`. Read-only. Start at 1. |
| 2 | Supplier Name | Text (Single) | Yes | Max 150. **Unique** (no duplicate supplier names). |
| 3 | Supplier Type | Dropdown | No | Options: **Manufacturer**, **Distributor**, **Trader**, **Service Provider** |
| 4 | GSTIN | Text (Single) | Yes | Max 15. Custom validation regex: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` |
| 5 | PAN No | Text (Single) | Yes | Max 10. Custom validation regex: `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` |
| 6 | Contact Person | Text (Single) | Yes | Max 100 |
| 7 | Mobile No | Text (Single) | Yes | Max 15. Min length: 10. |
| 8 | Alt Contact No | Text (Single) | No | Max 15 |
| 9 | Email ID | Email | Yes | Creator "Email" field type (built-in email validation) |
| 10 | Address | Text (Multi-line) | Yes | 4–5 rows visible |
| 11 | Pincode | Text (Single) | No | Max 10. Custom validation regex: `^\d{6}$` |
| 12 | Bank Name | Text (Single) | Yes | Max 100 |
| 13 | Account No | Text (Single) | Yes | Max 20. **Text type** (not Number — preserves leading zeros). |
| 14 | IFSC Code | Text (Single) | Yes | Max 11. Custom validation regex: `^[A-Z]{4}0[A-Z0-9]{6}$` |
| 15 | Payment Terms | Dropdown | Yes | Options: **Advance**, **7 Days**, **15 Days**, **30 Days**, **45 Days**, **60 Days**, **On Delivery** |
| 16 | Credit Days | Number (Integer) | Yes | Min value: 0 |

### Field-Level Security

| Field | Restricted Access |
|-------|------------------|
| Account No | Only Admin, Purchase Manager, Finance Executive — View + Edit |
| IFSC Code | Only Admin, Purchase Manager, Finance Executive — View + Edit |

Set via: Field > Properties > Access tab > uncheck for all other profiles.

---

## 3. UI Layout — 3 Sections

```
┌─ Section: Basic Details ──────────────────────────────────────────┐
│                                                                     │
│    Supplier Code  [SUP-001]         Supplier Type  [▼]             │
│    Supplier Name  [_____________________________]                  │
│    GSTIN          [_____________________________]                  │
│    PAN No         [_____________________________]                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
┌─ Section: Contact Details ─────────────────────────────────────────┐
│                                                                     │
│    Contact Person   [________________]    Mobile No   [__________] │
│    Alt Contact No   [________________]    Email ID    [__________] │
│                                                                     │
│    Address:                                                         │
│    [Multi-line text area — 4 rows]                                  │
│                                                                     │
│    Pincode  [________]                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
┌─ Section: Bank & Payment Terms ────────────────────────────────────┐
│                                                                     │
│    Bank Name       [________________]    Account No  [___________] │
│    IFSC Code       [________________]                              │
│    Payment Terms   [▼]                     Credit Days [_________] │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Creator Implementation Steps

1. **Create form**: Form > Create Form > name = "Supplier Master", internal name = `Supplier_Master`
2. **Add Supplier Code**: Insert > Auto Number > Format: `SUP-{000}` > Check "Read Only"
3. **Add Supplier Name**: Insert > Text > Check "Required" and "Unique" > Max 150
4. **Add Supplier Type**: Insert > Dropdown > manually enter 4 options > Do NOT check Required
5. **Add GSTIN**: Insert > Text > Check Required > Max 15 > Properties > Custom Validation > enter regex
6. **Add PAN No**: Insert > Text > Check Required > Max 10 > Custom Validation > enter regex
7. **Add Contact Person**: Insert > Text > Check Required > Max 100
8. **Add Mobile No**: Insert > Text > Check Required > Max 15 > Properties > Min Length = 10
9. **Add Alt Contact No**: Insert > Text > Max 15
10. **Add Email ID**: Insert > Email > Check Required
11. **Add Address**: Insert > Multi-line > Check Required > Rows = 4
12. **Add Pincode**: Insert > Text > Max 10 > Custom Validation > regex `^\d{6}$`
13. **Add Bank Name**: Insert > Text > Check Required > Max 100
14. **Add Account No**: Insert > Text > Check Required > Max 20
15. **Add IFSC Code**: Insert > Text > Check Required > Max 11 > Custom Validation > regex
16. **Add Payment Terms**: Insert > Dropdown > manually enter 7 options > Check Required
17. **Add Credit Days**: Insert > Number > uncheck Decimal > Check Required > Min Value = 0
18. **Create sections**: Form > Sections > Add Section: "Basic Details", "Contact Details", "Bank & Payment Terms"
19. **Arrange fields**: Drag fields into correct sections per layout above
20. **Set field-level security**: For Account No and IFSC Code > Properties > Access > keep only Admin, Purchase Manager, Finance Executive checked

---

## 4. Report Configuration

| Property | Value |
|----------|-------|
| Report name | Supplier Master List |
| Report type | List Report |
| Columns | Supplier Code, Supplier Name, Supplier Type, GSTIN, PAN No, Contact Person, Mobile No, Alt Contact No, Email ID, Address, Pincode, Bank Name, Account No, IFSC Code, Payment Terms, Credit Days |
| Default sort | Supplier Name ascending (A→Z) |
| Filters | Optional: by Supplier Type |
| Search fields | Supplier Name, GSTIN, PAN No, Contact Person |
| Summary | Record count at footer |

### Steps

1. Reports tab > New Report > List Report
2. Add all 16 fields from available column list
3. Set default sort: Supplier Name → Ascending
4. Add optional filter: Supplier Type (user can select to filter)
5. Enable search: check Supplier Name, GSTIN, PAN No, Contact Person
6. Report permissions: same as form Read permissions (see §5)

---

## 5. Permissions

### Form-Level CRUD

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | ✓ | ✓ | ✓ | ✓ |
| Purchase Executive | ✓ | ✓ | ✓ | ✓ |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | — | — | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | ✓ | — | — |
| Viewer | — | ✓ | — | — |

Set via: Form > Permissions tab > select each profile, check CRUD boxes

### Report Permissions

Same as form Read permission (Admin ✓, Purchase Manager ✓, Purchase Executive ✓, Finance Executive ✓, Viewer ✓ — all others No Access)

---

## 6. Deluge Validation

No Deluge workflows required for Supplier Master. All validations are handled at the field level:

| Validation | Mechanism |
|-----------|-----------|
| GSTIN format | Field regex pattern |
| PAN format | Field regex pattern |
| IFSC format | Field regex pattern |
| Pincode format (optional) | Field regex pattern |
| Email format | Creator Email field type (built-in) |
| Mobile No min length | Field property: Min Length = 10 |
| Credit Days min 0 | Field property: Min Value = 0 |
| Supplier Name uniqueness | Field property: Unique checkbox |
| Supplier Code auto-number | Native Auto Number field type |

No cross-field validation logic is needed — there is no conditional dependency between any two fields in this form. The BRD and PLAN do not specify any Deluge-level rules for Supplier Master.

---

## 7. Verification Checklist

- [ ] Form created with internal name `Supplier_Master`
- [ ] Supplier Code: auto-number `SUP-{000}`, read-only, starts at 1
- [ ] All 16 fields created with correct types (Auto Number, Text, Dropdown, Email, Multi-line, Number)
- [ ] Required fields set: Supplier Name, GSTIN, PAN No, Contact Person, Mobile No, Email ID, Address, Bank Name, Account No, IFSC Code, Payment Terms, Credit Days
- [ ] Non-required fields: Supplier Type, Alt Contact No, Pincode
- [ ] Supplier Name marked **Unique**
- [ ] GSTIN regex validation configured: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`
- [ ] PAN No regex validation configured: `^[A-Z]{5}[0-9]{4}[A-Z]{1}$`
- [ ] IFSC Code regex validation configured: `^[A-Z]{4}0[A-Z0-9]{6}$`
- [ ] Pincode regex validation configured: `^\d{6}$`
- [ ] Mobile No min length = 10
- [ ] Credit Days min value = 0
- [ ] Email ID uses Creator Email field type
- [ ] Account No is Text type (not Number) — preserves leading zeros
- [ ] 3 sections created and named correctly: Basic Details, Contact Details, Bank & Payment Terms
- [ ] Fields arranged in correct section per layout
- [ ] Field-level security: Account No and IFSC Code restricted to Admin, Purchase Manager, Finance Executive only
- [ ] Supplier Type dropdown has 4 options: Manufacturer, Distributor, Trader, Service Provider
- [ ] Payment Terms dropdown has 7 options: Advance, 7 Days, 15 Days, 30 Days, 45 Days, 60 Days, On Delivery
- [ ] Report "Supplier Master List" created with all 16 columns
- [ ] Report default sort: Supplier Name ascending
- [ ] Report search enabled on: Supplier Name, GSTIN, PAN No, Contact Person
- [ ] Report optional filter: by Supplier Type
- [ ] Report permissions match form Read permissions
- [ ] Form permissions set per matrix (14 profiles × CRUD)
- [ ] Audit fields visible (inherited from app level)
- [ ] No Deluge workflows needed — all validation is field-level
