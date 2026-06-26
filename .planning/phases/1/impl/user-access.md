# User Access & Approval Matrix — Implementation Artifact

## 1. Form Config

| Property | Value |
|----------|-------|
| Internal name | `User_Access` |
| Form name displayed | User Access & Approval Matrix |
| Dependency | None |
| Audit fields | Enabled at app level (Created By, Created Time, Modified By, Modified Time) |

---

## 2. Field Configuration Table

| # | Field Label | Field Type | Required | Default | Properties |
|---|-------------|-----------|----------|---------|------------|
| 1 | User Code | Auto Number | Yes (auto) | — | Format: `USR-{000}`. Read-only. Starts at 1. |
| 2 | User Name | User | Yes | — | Insert > User. Dropdown of all Zoho Creator org users. Single-select only. |
| 3 | Department | Dropdown | Yes | — | Options: **Admin**, **Purchase**, **Store & Logistics**, **Production**, **QC**, **Sales**, **Project Management**, **Account & Finance** |
| 4 | Role | Dropdown | Yes | — | Options: **Admin**, **Purchase Manager**, **Purchase Executive**, **Store Manager**, **Store Keeper**, **Production Manager**, **Production Executive**, **QC Inspector**, **Sales Executive**, **Project Manager**, **Project Coordinator**, **Finance Executive**, **Viewer** |
| 5 | PR Approval Limit | Currency | No | 0 | INR (₹). 2 decimal places. Default value = 0 (user cannot approve PR). |
| 6 | PO Approval Limit | Currency | No | 0 | INR (₹). 2 decimal places. Default value = 0 (user cannot approve PO). |

### Field-Level Notes

**User Code** — Native Creator auto-number field. Set via Insert > Auto Number with custom format `USR-{000}`. Check "Read Only". No Deluge needed.

**User Name** — This is a special Creator field type (Insert > User), not a standard Lookup or Text field. It links to the Zoho Creator user table (the org's user list under Settings > Users & Permissions > Users). See §6 for detailed setup instructions.

**Department** — Insert > Dropdown. Manually type all 8 options in the dropdown editor. Check "Required".

**Role** — Insert > Dropdown. Manually type all 13 options. Check "Required".

**PR Approval Limit / PO Approval Limit** — Insert > Currency. Set Currency = INR. In field properties, set "Default Value" = 0. Uncheck "Required" (a user with zero limit simply cannot approve — that's valid business logic, not an incomplete record).

---

## 3. UI Layout — 1 Section

```
┌─ Section: User Access & Approval Limits ─────────────────────┐
│ User Code [Auto]          User Name [User ▼]                │
│ Department [▼]            Role [▼]                          │
│ PR Approval Limit [₹___]  PO Approval Limit [₹_________]   │
└──────────────────────────────────────────────────────────────┘
```

**Section setup in Creator:**
1. Insert > Section. Label: "User Access & Approval Limits"
2. Place fields in a 2-column layout by dragging them side by side
3. User Code on left, User Name on right (row 1)
4. Department on left, Role on right (row 2)
5. PR Approval Limit on left, PO Approval Limit on right (row 3)
6. All widths should be "Equal" or lefts at 50% / rights at 50%

---

## 4. Report Configuration

| Property | Value |
|----------|-------|
| Report name | User Access List |
| Type | List Report |
| Columns | User Code, User Name (display name), Department, Role, PR Approval Limit, PO Approval Limit |
| Default sort | Department ascending, then User Name ascending |
| Search | Enable on User Name, Department, Role |
| Summary | Record count at footer; Sum of PR Approval Limit; Sum of PO Approval Limit |

**Creator steps:**
1. Reports tab > New Report > List Report
2. Add field columns: User Code, User Name, Department, Role, PR Approval Limit, PO Approval Limit
3. Sort: Department ASC, then User Name ASC
4. Enable search bar; select User Name, Department, Role as searchable fields
5. Add summary fields: Count (Records), Sum (PR Approval Limit), Sum (PO Approval Limit)
6. Report permissions: same as form Read — Admin only
7. Save as "User Access List"

---

## 5. Permissions

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
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | — | — | — |
| Viewer | — | — | — | — |

**This form is Admin-only.** No other profile gets any access (not even Read). All 12 non-Admin profiles must have all 4 checkboxes (Create, Read, Update, Delete) left unchecked.

**Report permissions**: Set report "User Access List" to the same — Admin only.

---

## 6. Important: Handling the "User Name" Field in Zoho Creator

The **User Name** field in this form uses Creator's native **User** field type — **not** a standard Lookup or a Text field. This is a critical distinction:

### What the User field does
- Insert > **User** (not Lookup, not Text, not Dropdown)
- Automatically lists all users from Zoho Creator's **Settings > Users & Permissions > Users** (the org's active user roster)
- Displays as a dropdown showing user display names (e.g., "Rajesh Kumar")
- Stores the internal user ID (a GUID) behind the scenes
- Is single-select only — one user per record
- The Creator User field is different from a Lookup to another form

### Steps to Add in Form Designer
1. Open the User Access form in edit mode
2. Click **Insert** > **User**
3. A field appears titled "User Name" — rename the label in Field Properties if needed
4. Check **"Required"** in field properties
5. Set **"Choose Users From"** → "All Users" (default; this lists all org users)
6. Optionally set **"Limit by Profile"** if you want to restrict which profiles appear in the dropdown (for this form, keep "All Users" so Admin can assign any user)

### Important Caveats
- The User field cannot be used as the "Display Field" in a report that needs to show as plain text in subforms or integrations — but for a List Report it displays the user's display name correctly
- If a user is **deactivated** in Zoho Creator org settings, they will still appear in existing records but will not appear in the dropdown for new records
- There is **no multi-select** option — one record per user assignment
- You cannot use the User field in Deluge criteria like `input.User_Name == "Rajesh"` — it stores a user ID, not a string. To compare, use `input.User_Name.getId()` or `input.User_Name.getDisplayValue()`
- If you need to reference the logged-in user in a Deluge workflow, use `zoho.loginuser` — not the User field

### Recommended Pattern for This Form
- **One record per user**: Admin creates one record per employee. Department + Role define what the user can do in the app
- **Unique constraint**: Since User Name cannot be set as "Unique" in Creator for the User field type, use a Deluge **On Submit (Before)** workflow to check for duplicate user assignments:

```deluge
if(input.User_Name != null)
{
    user_id = input.User_Name.getId();
    existing = zoho.creator.getRecords("chemsol", "User_Access",
        "User_Name == '" + user_id + "'", 1, 0);
    if(existing.size() > 0)
    {
        throw "This user already has an access record. Please edit the existing record instead of creating a duplicate.";
    }
}
```

---

## 7. Verification Checklist

- [ ] Form created with internal name `User_Access` and display name "User Access & Approval Matrix"
- [ ] User Code: Auto-number field with format `USR-{000}`, read-only
- [ ] User Name: Insert > User field type (not Lookup, not Text), required
- [ ] Department: Dropdown with exactly 8 options listed (Admin, Purchase, Store & Logistics, Production, QC, Sales, Project Management, Account & Finance), required
- [ ] Role: Dropdown with exactly 13 options listed, required
- [ ] PR Approval Limit: Currency (INR), default value 0, not required
- [ ] PO Approval Limit: Currency (INR), default value 0, not required
- [ ] UI layout matches the 1-section / 2-column wireframe above
- [ ] Report "User Access List" created with all 6 columns, sorted by Department ASC then User Name ASC
- [ ] Search enabled on User Name, Department, Role
- [ ] Summary: Record count + Sum of PR Limit + Sum of PO Limit
- [ ] Permissions: Admin = CRUD, all 12 other profiles = No Access (all 4 checkboxes unchecked)
- [ ] Report permissions: Admin only
- [ ] Deluge duplicate check added (On Submit — Before) for User Name uniqueness
- [ ] Audit fields enabled (app-level — verified)
