# Prerequisites — Implementation Artifact

## 1. App Creation Checklist

### Step-by-step: Create Chemsol App in Zoho Creator (India Datacenter)

| Step | Action | Screenshot / Field | Value / Instruction |
|------|--------|--------------------|--------------------|
| 1 | Open browser | URL | `https://creator.zoho.in` — **must be `.in`**, not `.com` |
| 2 | Sign in | Email/Password | Use ITOTCloud's Zoho Creator account (Creator license required) |
| 3 | Dashboard | Click **Create App** (top-right blue button) | |
| 4 | App Name | Field | **Chemsol** |
| 5 | App type | Select | **Application** (not Blueprint, not Extension) |
| 6 | Datacenter | Dropdown | **India** — once saved, this is **permanent and irreversible** |
| 7 | Verify region | Browser URL bar | Must show `creator.zoho.in/app/chemsol...` |
| 8 | App slug | Auto-generated | `chemsol` (Creator derives from name — verify it's lowercase, no spaces) |

### Post-creation app-level settings

Once the app is created and the (empty) form canvas loads:

| Setting | Navigation Path | Value |
|---------|----------------|-------|
| Timezone | Settings (gear icon) > App Settings > General > Time Zone | **Asia/Kolkata (IST)** |
| Date format | Settings > App Settings > General > Date Format | **DD/MM/YYYY** |
| Currency | Settings > App Settings > General > Currency | **INR (₹)** |
| Audit fields | Settings > App Settings > Forms > Show Audit Fields | **Toggle ON** |

### Audit fields details

When "Show Audit Fields" is enabled, every form in the app automatically gets these 4 hidden fields:

| Field Name | Type | Purpose |
|-----------|------|---------|
| Created By | Lookup (User) | Who created the record |
| Created Time | Date/Time | When the record was created |
| Modified By | Lookup (User) | Who last modified |
| Modified Time | Date/Time | When last modified |

> **Important**: Enable audit fields **before** creating any forms. If enabled later, existing forms won't retroactively get audit fields — you'd need to add them manually per form.

---

## 2. 13 Profiles Creation

### Creator UI Path

**Settings (gear icon, top-right) > Users & Permissions > Profiles > Create Profile**

Repeat the following for each of the 13 profiles:

1. Click **Create Profile**
2. Enter **Profile Name** (exactly as listed below)
3. Leave all permissions at their defaults (no forms exist yet)
4. Click **Save**
5. Repeat

### Profile Table

| # | Profile Name | Description | Notes |
|---|-------------|-------------|-------|
| 1 | Admin | System configuration, master data, user access | Full access to everything |
| 2 | Purchase Manager | PR approval, PO creation, supplier management | Approver-level procurement |
| 3 | Purchase Executive | PR initiation, rate comparison, GRN entry | Transactional procurement |
| 4 | Store Manager | Inventory oversight, material issues, FG receiving | Store decision-maker |
| 5 | Store Keeper | Daily store ops, material movement | Hands-on store execution |
| 6 | Production Manager | Production planning, batch management | Production decision-maker |
| 7 | Production Executive | MR creation, RM consumption, packing | Shop-floor execution |
| 8 | QC Inspector | Quality inspection, test results entry | Lab/testing role |
| 9 | Sales Executive | SO/WO creation, customer management | Front-end sales |
| 10 | Project Manager | Project creation, tracking, task management | Project ownership |
| 11 | Project Coordinator | Daily project updates, coordination | Project support |
| 12 | Finance Executive | Payment tracking, financial reports | Financial oversight |
| 13 | Viewer | Read-only access to assigned forms/reports | Audit/review only |

### After all profiles exist

Confirm by returning to **Settings > Users & Permissions > Profiles** — all 13 should be listed. Permissions will be configured per-form later in Phase 1.

---

## 3. App-Level Settings Summary

| Setting | Value | Location |
|---------|-------|----------|
| App name | Chemsol | App creation screen |
| App URL slug | `chemsol` | Auto-generated, verify |
| Datacenter | India (`.in`) | App creation — **cannot be changed** |
| Timezone | Asia/Kolkata (IST) | Settings > App Settings > General |
| Date format | DD/MM/YYYY | Settings > App Settings > General |
| Currency | INR (₹) | Settings > App Settings > General |
| Audit fields | Enabled (all 4) | Settings > App Settings > Forms |
| Number format | 1,234,567.89 (Indian) | Settings > App Settings > General |

---

## 4. Verification Checklist

Run through this checklist before moving to Phase 1 form creation.

| # | Check | Expected Result | Done |
|---|-------|----------------|------|
| 1 | Open `https://creator.zoho.in` | India datacenter login page | |
| 2 | Open Chemsol app from dashboard | App opens to empty form list | |
| 3 | Verify URL contains `creator.zoho.in/app/chemsol` | `.in` domain confirmed | |
| 4 | Check timezone | Asia/Kolkata (IST) | |
| 5 | Check date format | DD/MM/YYYY | |
| 6 | Check currency | INR (₹) | |
| 7 | Check audit fields toggle | Enabled | |
| 8 | Verify audit fields on any scratch form (optional) | Created By, Created Time, etc. visible in form designer | |
| 9 | Navigate to Settings > Users & Permissions > Profiles | All 13 profiles listed | |
| 10 | Spot-check profile names | No typos, exact names as spec | |
| 11 | Log out, log back in as a test user assigned to Viewer profile | Read-only experience confirmed (later) | |

---

## 5. India Datacenter Gotchas & Creator UI Quirks

### Critical (blocking if wrong)

| # | Quirk | Impact | Mitigation |
|---|-------|--------|------------|
| 1 | Datacenter selection is **one-time, irreversible** | If `.com` is selected, all APIs use `zoho.com`, URLs differ, and `.in` users can't access | Double-check the domain before clicking Create |
| 2 | Zoho Creator licenses are **per-datacenter** | A `.com` license won't work on `.in` | Ensure the account has an India-datacenter license or trial |
| 3 | Audit fields must be enabled **before** forms exist | Forms created before toggle get no audit fields | Enable it immediately after app creation |
| 4 | Profile names cannot be changed after creation | Must delete + recreate to rename | Type carefully when creating |

### Annoying but not blocking

| # | Quirk | Workaround |
|---|-------|------------|
| 5 | Creator UI sometimes defaults to `.com` even when you type `.in` | Explicitly use `creator.zoho.in` bookmark; never navigate from a `.com` page |
| 6 | App slug may auto-generate with uppercase or spaces if app name has them | Creator usually lowercases and hyphenates — verify in URL |
| 7 | Profile list doesn't refresh immediately after creation | Use browser refresh (F5) before checking the list |
| 8 | "Show Audit Fields" setting is a single toggle, but it's easy to miss because it's under Forms sub-tab, not General | Navigate to Settings > App Settings > Forms > scroll to bottom |
| 9 | Indian number format (lakh/crore) vs Western (million/billion) | Set explicitly in App Settings > General: Number Format = **Indian** |
| 10 | Creator auto-saves form edits — no explicit Save button on many dialogs | Changes are applied immediately; there's no undo for field deletion |
