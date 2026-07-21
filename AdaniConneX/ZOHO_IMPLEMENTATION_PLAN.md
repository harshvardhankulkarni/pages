# AdaniConneX ZohoCRM Implementation Plan

## Overview

| Item | Detail |
|---|---|
| **CRM** | ZohoCRM Enterprise |
| **Scope** | Data Center Opportunity lifecycle automation |
| **Current State** | Partial setup exists — enhancement project |
| **Key Integrations** | EdgeOS Portal (new), SAP (new), Managed Engine |
| **Teams** | Sales, Sales Operations, Pre-Sales, Commercials, IT, Service Delivery |

---

## Phase 0: Role Hierarchy & Profiles (Foundation)

### Objective
Design ZohoCRM roles, profiles, and permissions before configuring any modules.

### Role Hierarchy (Top-Down)

```
Administrator (IT)
  └── CBO / Sales Head
        └── Sales Operations
              ├── Commercials (Product)
              ├── Pre-Sales (Technical)
              └── Sales (Account Managers)
                      └── Service Delivery
```

### Profiles & Permissions

| Profile | Module Access (Data Center Opp.) | Key Permissions |
|---|---|---|
| **IT Admin** | Read-Write-Delete all | Full system access, manage users, customisation |
| **Sales Head** | Read-Write | View all opps, mass email, export |
| **Sales Ops** | Read-Write | Validate pricing, drive data accuracy, edit post-SOF-Contracted |
| **Sales (AM)** | Read-Write owned | Create/edit opps up to SOF MSA, upload docs |
| **Commercials** | Read-only + Approval | Validate commercial details, approve SOF MSA |
| **Pre-Sales** | Read-only + Approval | Validate technical feasibility, approve SOF MSA |
| **Service Delivery** | Read-only | View contracted opps, receive notifications |

**ZohoCRM Enterprise Feature Used**: Roles, Profiles, Permission Sets

### Record-Level Sharing

- Sales: Private (only owner + reporting hierarchy sees owned records)
- Sales Ops: Read-Write access to all records
- Commercials/Pre-Sales: Read-only access to records awaiting their approval

### Open

- [ ] Confirm role hierarchy with reporting structure
- [ ] Define whether Service Delivery needs read-only on all or only specific site opps

---

## Phase 1: Module Configuration & Custom Fields

### 1A. Data Center Opportunity Module (Core)

**Existing Fields to Map / Create:**

| Field | Type | Notes |
|---|---|---|
| **Opportunity Reference ID** | Auto-number | Pattern: `{SiteID}-{000000}-{V0}` — see open items below |
| **ACX Sales Stage** | Picklist | Values from Sales Pipeline (see Phase 2) |
| **Account Name** | Lookup (Accounts) | Required |
| **Contact Name** | Lookup (Contacts) | Required |
| **Site ID** | Picklist | Values to define — see open items |
| **Deal Type** | Picklist | Colocation / Reservation / ROFR |
| **Contract Term (Months)** | Number | Initial term |
| **Renewal Periods** | Number | Number of renewal options |
| **Years Per Renewal** | Number | Years per extension |
| **Contract Expiry Date** | Date (Formula) | `Deployed Date + Contract Term (Months)` |
| **Renewed Through Date** | Date | Manual entry for renewals |
| **Deployed Date** | Date | Set by Service Delivery (ownership TBD) |
| **Deal Value (Total)** | Currency | Roll-up sum from pricing subforms |
| **Probability (%)** | Number | Auto-set by stage (10/25/50/75/90/100/0) |
| **SOF/PO Received** | Checkbox | Checked when document uploaded to SOF MSA |
| **MSA Signed** | Checkbox | Checked when document uploaded to SOF Contracted |

### 1B. Colocation Pricing Module (Subform on Opportunity)

| Field | Type | Notes |
|---|---|---|
| **Pricing Type** | Picklist | Per Rack / Per KW |
| **Product Type** | Picklist | Colocation / Reservation / ROFR |
| **Deal Type** | Picklist | Metered Pricing (KW with PUE) / All-in-Bundled Pricing |
| **Quantity (Racks)** | Number | No. of racks |
| **Power Density (KW)** | Number | Power per rack or total |
| **Monthly Rate (MRC)** | Currency | Per-unit or total |
| **One-Time Charge (OTC/NRC)** | Currency | Setup/installation |
| **Line Total** | Currency (Formula) | Calculated: Qty × Rate |

### 1C. Additional DC Products & Services Module (Subform on Opportunity)

| Field | Type | Notes |
|---|---|---|
| **Product Category** | Picklist | Cross-Connect, Rack Cabinet, PDU, CCTV, etc. |
| **Product Name** | Picklist (EDC Products) | Populated from EDC Products catalog |
| **Quantity** | Number |  |
| **Monthly Rate (MRC)** | Currency |  |
| **One-Time Charge (OTC/NRC)** | Currency |  |
| **Line Total** | Currency (Formula) | Calculated: Qty × Rate |

### 1D. EDC Products Module (Product Catalog — Maintained by Sales Ops)

| Field | Type | Notes |
|---|---|---|
| **Product Category** | Picklist | Product family grouping |
| **Product Name** | Text/Unique | Unique product name |
| **Description** | Text |  |
| **Default MRC** | Currency | Optional — may vary by customer |
| **Default OTC** | Currency | Optional — may vary by customer |
| **Active** | Checkbox | Enable/disable products without deleting |

**Products to seed** (from process document — ~50 products):

- Cross-Connect (Fiber), Cross-Connect (Copper)
- Rack Cabinets: 42U/48U/52U in various widths (600×800/1000/1200 mm) + Setup Charges
- PDUs: Basic & Intelligent, 1Ph/3Ph, 16A/32A/63A + Floor Mount
- CCTV, Biometric with Access Controller
- Caging: Mesh (Stainless Steel), Opaque (Stainless Steel)
- Remote Hands, Smart Hand, Staff Augmentation, Migration, Lift & Shift
- Structured Cabling, ATS, STS, Blanking Panels
- Supplementary Cooling, Cold Aisle Containment, Duct Charges
- Seating Space, Dedicated Staging Space, Dedicated Storage Unit
- Tape Movement, Secured Duct/Conduit, Dedicated Copper Basket

### 1E. Supporting Modules (Accounts, Contacts, Calls, Meetings, Documents)

These likely already exist. Verify:

- **Accounts**: Industry, Account Manager (User lookup), NDA upload field
- **Contacts**: Email, Phone, Title, Primary Contact checkbox
- **Documents**: Association fields to Account, Opportunity, Contact; Document Type picklist (MSA, SOF, PO, NDA, LOA)
- **Calls/Meetings**: Attendees lookup, Related To (Account/Opportunity), Call Purpose/Agenda

### Open

- [ ] Define SiteID picklist values (e.g., EDCPOR01, BLR01, MUM01, etc.)
- [ ] Decide: 6-digit counter — global or per SiteID?
- [ ] Confirm auto-number formula feasibility in ZohoCRM (custom function may be needed for per-SiteID counters)
- [ ] Confirm Deployed Date ownership (Service Delivery? Sales Ops?)
- [ ] Validate existing modules/fields — what already exists vs needs creation

---

## Phase 2: Sales Pipeline Blueprint

### Objective
Enforce correct stage progression with mandatory fields, documents, and approvals using ZohoCRM Blueprint (Enterprise feature).

### Blueprint States & Transitions

```
Suspect ──→ Prospect ──→ Funnel ──→ Negotiation ──→ SOF MSA ──→ SOF Contracted
                  │            │           │               │
                  └──── Did Not Participate ──── Lost / Dropped / Material Change
```

### Stage Details with Blueprint Checks

| Transition | Triggers | Required Fields | Required Doc | Approval |
|---|---|---|---|---|
| **Suspect → Prospect** | Sales action | Customer requirement summary, site preference | — | — |
| **Prospect → Funnel** | Sales action | RFP received? checkbox, proposal submitted date | — | — |
| **Funnel → Negotiation** | Sales action | Final proposal submitted date, commercial offer total | — | — |
| **Negotiation → SOF MSA** | Sales action | All pricing fields filled | PO or SOF uploaded | Pre-Sales approval → then Commercial approval |
| **SOF MSA → SOF Contracted** | Sales Ops action | MSA signed date | MSA uploaded | — |
| **Any active → Lost** | Sales action | Lost reason (Competitor/Insourced/Cancelled) | — | — |
| **Any active → Dropped** | Sales action | Dropped reason | — | — |
| **Negotiation+ → Material Change** | Sales action | Change description, new opp reference ID | — | — |
| **Prospect → Did Not Participate** | Sales action | Reason code | — | — |

### Terminal States

- **Lost** (0%): Competitor awarded, customer insourced
- **Dropped** (0%): Customer cancelled requirement
- **Did Not Participate** (0%): ACX chose not to bid (space sold, budget not approved, etc.)
- **Material Change** (0%): Requirements changed drastically → new opportunity created

### End-of-Life States (post-contract)

- **SOF Expired**: Initial term ended, no renewal
- **SOF Cancelled**: Customer terminated before expiry

### Blueprint Enforcement Rules

- Each transition shows the correct Blueprint state
- Fields marked Required before transition are enforced
- File upload (PO/SOF, MSA) validated against ZohoCRM Documents module
- Probability % auto-populated from stage
- Pre-Sales approval triggered first on SOF MSA transition → then forwarded to Commercials

### Open

- [ ] Define terminal transitions from each stage — can any active stage go to Lost/Dropped, or only from Negotiation+?
- [ ] Confirm Material Change is only from Negotiation+ (document says Funnel+?)
- [ ] Do we show the "Did Not Participate" option from Suspect/Prospect only?
- [ ] Expiry/Cancelled stages — who triggers these transitions? Sales Ops?

---

## Phase 3: Approval Workflow (SOF MSA)

### Objective
Sequential approval process when an opportunity moves to SOF MSA stage.

### Flow

```
Sales moves to SOF MSA
      │
      ▼
Pre-Sales Approval Request (Technical Feasibility)
      │
      ├── Approved ──→ Commercials Approval Request (Commercial Validation)
      │                      │
      │                      ├── Approved ──→ Stage moved to SOF MSA
      │                      │                   → Notification sent
      │                      │
      │                      └── Rejected ──→ Returned to Negotiation with comments
      │
      └── Rejected ──→ Returned to Negotiation with comments
```

### ZohoCRM Implementation

- **Blueprints** handle the stage transition + field requirements
- **Approval Process** (separate ZohoCRM module) handles the sequential approvals
- Two approval processes:
  1. `APPROVAL_SOFMSA_PRESALES` — Pre-Sales approvers
  2. `APPROVAL_SOFMSA_COMMERCIAL` — Commercial approvers (triggered only if Pre-Sales approved)
- Each approval sends email notification to the approver with record link
- Rejection reason captured and displayed on record
- Escalation: If no response in 48 hours, notify the approver's reporting manager

### Open

- [ ] Confirm 48-hour escalation SLA — is this correct?
- [ ] Who are fallback approvers if primary approvers are unavailable?
- [ ] Should all Pre-Sales and Commercial team members get the approval request, or a specific person per site/region?

---

## Phase 4: Pricing Automation

### Objective
Ensure pricing data is captured correctly and validated.

### Workflow: Pricing Validation (Before SOF MSA)

1. Sales enters pricing in:
   - **Colocation Pricing** subform (space + power)
   - **Additional DC Products & Services** subform (ancillary items)
2. **Validation rule**: At least one pricing line must exist before moving to SOF MSA
3. **Sales Ops validation**: When Sales moves to SOF MSA, Sales Ops receives a notification to review pricing
4. If pricing is incorrect → Sales Ops returns to Sales with corrections needed
5. If pricing is correct → Sales Ops approves → continues to Pre-Sales approval

### Validation Rules

- Colocation Pricing: If Deal Type = Colocation, at least one row required with Quantity > 0
- MRC + OTC: Must be positive numbers
- Pricing Type (Per Rack / Per KW): Must match the deal type configuration

### Open

- [ ] Is there a standard price list (rate card) that Sales Ops validates against, or is pricing entirely negotiated per deal?
- [ ] Should pricing validation be part of the SOF MSA approval flow, or a separate step?

---

## Phase 5: Document Management

### Module: Documents

Each document record is associated to its parent module.

| Document Type | Mandatory For | Uploaded On |
|---|---|---|
| NDA | Optional (Account/Opportunity) | Any time |
| Purchase Order (PO) | SOF MSA transition | At SOF MSA |
| Sales Order Form (SOF) | SOF MSA transition | At SOF MSA |
| MSA | SOF Contracted transition | At SOF Contracted |
| LOA | Optional (Account/Opportunity) | Any time |

### Document Upload Rules (via Blueprint + Workflow)

- Stage transition to **SOF MSA**: Requires at least one document of type `PO` or `SOF` linked to the opportunity (file upload enforced)
- Stage transition to **SOF Contracted**: Requires at least one document of type `MSA` linked to the opportunity
- **File size limits**: Configure per ZohoCRM limits (default 20 MB, can be increased per edition)

### Open

- [ ] Can a single document serve both as PO and MSA check? (e.g., combined contract document)
- [ ] Should document expiry alerts be configured? (e.g., NDA expiry)
- [ ] Is LOA ever mandatory for any specific process?

---

## Phase 6: Notifications & Automation

### Triggered Notifications (Workflow Automations)

| Event | Recipients | Trigger | Channel |
|---|---|---|---|
| Account created | Sales Head, Sales Ops | On create | Email |
| Opportunity created | Sales Head, Sales Ops, CBO | On create | Email |
| New order book (daily per scheduler) | Sales Head per team | Scheduled daily | Email |
| Stage moved to SOF MSA | Sales Leads, Sales Heads, CBO, Pre-Sales, Service Delivery | On approval complete | Email |
| Order delivery notification | Service Delivery Team | On SOF MSA approval complete | Email |
| Contract expiry approaching | Sales Ops, Sales | Scheduled (interval TBD) | Email |
| Opportunity modified post-SOF-Contracted | Sales Ops, IT Admin | On edit by non-allowed user | Email alert |

### ZohoCRM Enterprise Features Used

- **Workflow Automation**: Create/Update records, send email, trigger webhooks, call custom functions
- **Scheduler**: Daily/weekly/monthly scheduled tasks for order book and contract expiry reports
- **Custom Functions (Deluge)**: For complex logic (e.g., Opportunity Reference ID generation, EdgeOS sync preparation, SAP data export)

### Notification Sender

All automated emails sent from ZohoCRM Admin account (Lance Devin) — configure sender email in ZohoCRM.

### Open

- [ ] Confirm contract expiry notification lead time (single or staged reminders)
- [ ] Confirm order book scheduler frequency and distribution list
- [ ] Should notification emails include an HTML dashboard/summary or be plain text?

---

## Phase 7: Dependent System Integrations

### 7A. EdgeOS Portal Integration

**Direction**: ZohoCRM → EdgeOS (push every 15 minutes)

**Trigger**: Stage change to `SOF Contracted` + scheduler every 15 min for batch sync.

#### Data to Sync (for each SOF Contracted opportunity)

| Field | Description |
|---|---|
| Opportunity Reference ID | Unique deal identifier |
| Account Name | Customer company name |
| Site ID | Data center site |
| Contracted Power (KW) | Sum from Colocation Pricing lines |
| Contract Status | Active / Expired / Cancelled |
| Contract Expiry Date | When access should end |

#### Deluge Pseudocode (Custom Function `pushToEdgeOS`)

```
// Step 1: Query all SOF Contracted opportunities
criteria = "ACX_Sales_Stage == 'SOF Contracted'"
oppRecords = zoho.crm.getRecords("Data_Center_Opportunity", criteria);

// Step 2: Iterate and build payload
for each opp in oppRecords:
    // Join Colocation Pricing subform
    pricingLines = opp.get("Colocation_Pricing");
    totalPowerKW = 0;
    for each line in pricingLines:
        totalPowerKW += line.get("Power_Density_KW");
    end

    // Build JSON payload
    payload = Map();
    payload.put("opportunityRefId", opp.get("Opportunity_Reference_ID"));
    payload.put("customerName", opp.get("Account_Name").get("Account_Name"));
    payload.put("siteId", opp.get("Site_ID"));
    payload.put("contractedPowerKW", totalPowerKW);
    payload.put("contractStatus", "Active");
    payload.put("contractExpiryDate", opp.get("Contract_Expiry_Date").toString("yyyy-MM-dd"));

    // POST to EdgeOS API
    headerParams = Map();
    headerParams.put("Authorization", "Bearer " + edgeosApiKey);
    headerParams.put("Content-Type", "application/json");

    response = invokeUrl(
        url: "https://edgeos.adaniconnex.com/api/v1/sync-opportunity",
        type: POST,
        headers: headerParams,
        body: payload.toString()
    );

    // Update sync status on opportunity
    updateRecord = Map();
    if response.getResponseCode() == 200:
        updateRecord.put("EdgeOS_Sync_Status", "Synced");
    else:
        updateRecord.put("EdgeOS_Sync_Status", "Sync Failed");
        // Log error for retry
    end

    zoho.crm.updateRecord("Data_Center_Opportunity", opp.get("id"), updateRecord);
end
```

#### What EdgeOS Must Provide
- REST API endpoint (e.g., `POST /api/v1/sync-opportunity`)
- Auth mechanism (API key in header, or OAuth2 client credentials)
- Network accessibility: EdgeOS endpoint must be reachable from Zoho servers
- Upsert logic for customer + site + power limits (create if not exists, update if exists)
- Documentation: expected payload schema, response codes, error messages

#### Architecture Options

| Option | Pros | Cons |
|---|---|---|
| **A. Zoho Custom Function → Webhook → EdgeOS API** | Real-time push, no middleware | EdgeOS needs public API endpoint |
| **B. Zoho Scheduler + Deluge → JSON export → FTP/SFTP** | No EdgeOS API needed, simpler | 15-min delay, file management overhead |
| **C. Zoho → Middleware (Zapier/Workato) → EdgeOS** | No coding, visual connector | Monthly cost, external dependency |

**Recommended**: Option A if EdgeOS has a REST API. Option B if EdgeOS does not.

#### ZohoCRM Implementation

Custom Function `pushToEdgeOS`:
- Triggered on stage change to SOF Contracted (real-time)
- Also runs on scheduler every 15 min for batch sync / retry of failed records
- Updates `EdgeOS_Sync_Status` field on each opportunity:
  - `Synced` — last push succeeded (HTTP 200)
  - `Sync Failed` — last push failed (will retry on next scheduler run)
  - `Pending` — awaiting first sync attempt

### 7B. SAP Billing Integration

**Direction**: ZohoCRM → SAP (trigger when Service Delivery marks deployment complete)

**When**: Service Delivery updates Deployed Date on the opportunity

#### Data to Send

| Field | Description |
|---|---|
| Opportunity Reference ID | Billing reference |
| Account Name + Billing Address | Customer details |
| Product Lines (Colo + Additional) | Services to bill |
| MRC (Monthly) | Recurring billing amount |
| OTC (One-time) | Setup/installation charges |
| Contract Start Date | Billing start |
| Contract Term | Billing duration |

#### Option A — File-based (Recommended Initially)

```
Custom Function "generateSAPExport":
1. Trigger: Service Delivery updates Deployed Date on opportunity
2. Query: Get opportunity + all pricing subforms
   - Colocation Pricing (space + power lines)
   - Additional DC Products & Services (ancillary lines)
3. Map to SAP structure:
   - Customer master from Account (billing address, GST, PAN)
   - Material codes from product-to-SAP mapping (requires mapping table)
   - Quantities from pricing subforms
   - Prices from MRC/OTC fields
4. Generate CSV with fixed-width columns per SAP spec:
   - Header row: Customer, Material, Qty, UoM, Price, Currency, Tax, ...
   - Detail rows: one per product line
   - Trailer row: total amounts, record count
5. Write file to SFTP server that SAP team polls
6. Update opportunity status: "Billing Exported"

SAP Team's Import Job:
1. Polls SFTP folder periodically
2. Validates file (checksum, record count)
3. Creates billing documents via BAPI_BILLINGDOCUMENT_CREATEMULTIPLE
4. Writes confirmation file back to SFTP:
   - File: ACK_{filename}.csv
   - Content: opportunityRefId, status (Confirmed/Failed), SAP doc number, error details

Zoho Polling:
1. Scheduler runs every 30 min
2. Checks SFTP for ACK files matching pending exports
3. On Confirmed → updates opportunity to "Billing Confirmed"
4. On Failed → updates to "Billing Failed" with error reason
```

#### Option B — Direct API (Future State)

```
1. Custom Function calls SAP RFC or REST API directly:
   - BAPI: BAPI_BILLINGDOCUMENT_CREATEMULTIPLE
   - Or: Custom SAP OData/REST service
2. SAP creates billing document synchronously
3. Immediate confirmation or error returned to Zoho
4. Faster turnaround, no file management

Prerequisites:
   - SAP connector enabled in Zoho (via Integration or middleware)
   - Network connectivity between Zoho and SAP
   - RFC/API user with billing creation authorization
```

#### Architecture Options Summary

| Option | Description | Risk | Effort |
|---|---|---|---|
| **A. Zoho → Flat file (CSV) → FTP/SFTP → SAP** | Batch processing, SAP polls | Low — file-based, decoupled | Zoho: 3 days, SAP: 3 days |
| **B. Zoho → SAP API (RFC/REST)** | Direct, real-time | Medium — needs API, network, auth | Zoho: 5 days, SAP: 7 days |
| **C. Zoho → Middleware → SAP** | Boomi, MuleSoft, SAP CPI | Low-Medium — uses existing connectors | Depends on middleware |

**Recommended**: Option A for initial go-live (lowest risk, can be built independently). Migrate to Option B or C post go-live when SAP team confirms API availability.

#### ZohoCRM Implementation

Custom Function `generateSAPExport`:
- Triggered on Deployed Date update (Workflow rule: When Deployed Date is set, call function)
- Queries all pricing subforms on the opportunity
- Builds CSV rows per SAP spec
- Writes file to SFTP using Zoho's SFTP connector

Status fields on Opportunity:
- `SAP_Billing_Status`: `Billing Pending` → `Billing Exported` → `Billing Confirmed` / `Billing Failed`
- `SAP_Document_Number`: SAP billing doc number (from ACK file)

#### What SAP Must Provide
- BAPI/RFC or REST API for billing document creation (`BAPI_BILLINGDOCUMENT_CREATEMULTIPLE` or equivalent)
- SFTP drop folder details (host, port, credentials, path) — for Option A
- Web service endpoint details — for Option B
- Product-to-material-code mapping (AdaniConneX product name → SAP material number)
- SAP team point of contact for import job development

### 7C. Managed Engine Integration

Out of scope for this implementation — noted for reference. Managed Engine is used for IT asset management by Praise/Krishna.

### Open

- [ ] Does EdgeOS have a REST API available? Need endpoint details + auth mechanism
- [ ] Does SAP have an import file format (CSV/IDoc) or API? Need SAP team input
- [ ] Is there existing middleware (Boomi/MuleSoft/etc.) that could be reused?
- [ ] Confirm EdgeOS sync scope — only SOF Contracted, or also SOF MSA with future-dated start?

---

## Phase 8: Contract Management & Renewals

### Fields (on Data Center Opportunity)

| Field | Type | Behavior |
|---|---|---|
| Contract Term (Months) | Number | Input by Sales Ops at SOF MSA |
| Renewal Periods | Number | Number of renewal options |
| Years Per Renewal | Number | Years per option |
| Contract Expiry Date | Date (Formula) | Auto: `Deployed Date + Contract Term` |
| Renewed Through Date | Date | Manual entry on renewal |
| ACX Sales Stage | Picklist | Set to `SOF Expired` or `SOF Cancelled` at end of life |

### Renewal Workflow

1. Contract expiry notification sent to Sales Ops + Sales (per scheduler, interval TBD)
2. If customer renews:
   - Sales Ops enters the `Renewed Through Date`
   - Opportunity remains in SOF Contracted
3. If customer does not renew:
   - Sales Ops sets stage to `SOF Expired`
4. If customer terminates early:
   - Sales Ops sets stage to `SOF Cancelled`

### Open

- [ ] Confirm expiry notification lead time (single vs staged — see earlier question)
- [ ] Does renewal trigger a new Opportunity or update the existing one? The doc implies updating `Renewed Through Date` on same record.
- [ ] What happens to EdgeOS sync when contract expires? Should the portal access be revoked?

---

## Phase 9: Reports & Dashboards

### Suggested Reports

| Report | Audience | Purpose |
|---|---|---|
| Pipeline by Stage (Weighted) | Sales Heads, CBO | Forecast revenue by probability |
| Opportunities by Site ID | Sales Ops | Capacity planning per data center |
| Stuck Opportunities (30+ days in stage) | Sales Ops, Sales Heads | Pipeline hygiene |
| Aging — Contract Expiry Next 90 Days | Sales Ops | Renewal pipeline |
| Deal Closure Summary (Month/Quarter) | CBO, Leadership | Win rate, average deal size |
| Order Book (SOF MSA and above) | Service Delivery | Deployment queue |
| Sales Team Performance | Sales Heads | Per-salesperson metrics |

### Dashboards (ZohoCRM Home Dashboard or Zoho Analytics)

- **Executive Dashboard**: Pipeline value, weighted forecast, close rate, new opps this month
- **Sales Ops Dashboard**: Data integrity checks, pending validations, contract expirations
- **Service Delivery Dashboard**: New orders (SOF MSA), upcoming deployments

### Open

- [ ] Any specific KPI targets to embed? (e.g., "Win rate > 40%")
- [ ] Use Zoho CRM dashboards or Zoho Analytics for deeper drill-down?

---

## Phase 10: CSAT Dashboard (Decision Pending)

### Scope Decision Required

There are two possible approaches:

**Option A: Part of this Zoho Implementation**
- Custom module in Zoho CRM or Zoho Creator for survey data
- Dashboard in Zoho Analytics
- QR code → web form → Zoho
- Email scheduler via Zoho CRM workflows

**Option B: Separate External System**
- Standalone application with its own database
- Webhook or periodic import to bridge data to Zoho if needed
- Noted in architecture as a cross-reference only

### Decision needed from stakeholders.

---

## Phase 11: Data Migration & Go-Live

### Pre-Migration Checklist

- [ ] All modules, fields, picklists configured and tested
- [ ] EDC Products catalog populated
- [ ] User roles, profiles, and permissions created and assigned
- [ ] Blueprints and approval processes tested end-to-end
- [ ] Document upload flows verified
- [ ] Notifications sending to correct recipients
- [ ] EdgeOS integration tested (if available during cutover)
- [ ] SAP export format validated with SAP team
- [ ] Reports and dashboards created

### Data Migration

If existing opportunities need to be imported:

| Source | Target | Key Mapping |
|---|---|---|
| Legacy pipeline (Excel/other CRM) | Data Center Opportunity | Map stage, site, pricing, contacts, docs |
| Existing product lists | EDC Products | Seed all ~50 products |

**Cleanup before import**:
- Standardise SiteID values
- Ensure no duplicate Accounts or Contacts
- Validate stage definitions match current pipeline

### Go-Live Sequence

```
1. Cutover: Freeze legacy system input
2. Import Accounts & Contacts
3. Import Opportunities (open pipeline)
4. Configure EdgeOS initial sync (full load)
5. User training sessions (Sales, Sales Ops, Commercials, Pre-Sales)
6. Go-Live: ZohoCRM becomes system of record
7. Hyper-care (2 weeks): IT + Sales Ops monitor for issues
8. Post-go-live: Configure scheduler for order book + expiry reports
```

---

---

## CRM Flow Changes — Current vs Target

### Capability Gap Analysis

| Capability | Current Status | Target | Change Needed |
|---|---|---|---|
| Accounts & Contacts creation | ✅ Exists | ✅ Enhanced | Minor field additions (Site ID, Account Manager) |
| Opportunity creation | ✅ Exists | ✅ Structured | Add Contract Term, Renewal Periods, Deal Type fields |
| Stage updates | ✅ Free-form | ✅ Blueprint-controlled | Replace free-text with controlled picklist + transitions |
| Calls & Meetings | ✅ Exists | ✅ Unchanged | Minor if any changes |
| Document upload | ⚠️ Basic | ✅ Stage-gated | Enforce PO/SOF before SOF MSA, MSA before SOF Contracted |
| Pricing entry | ⚠️ Free-text | ✅ Structured subforms | Colocation Pricing + Additional DC Products subforms |
| EDC Products catalog | ❌ Missing | ✅ Populated | Seed ~50 products |
| Stage gate enforcement | ❌ None | ✅ Blueprint | Field validation, doc requirements, approval triggers |
| Approval workflows | ❌ None | ✅ Sequential | Pre-Sales → Commercials on SOF MSA |
| Notifications | ❌ None | ✅ 7 triggers | Account, Opp, Order book, SOF MSA, Delivery, Expiry, Edit alerts |
| EdgeOS sync | ❌ None | ✅ 15-min push | Deluge Custom Function → EdgeOS API |
| SAP billing trigger | ❌ None | ✅ File-based | CSV → SFTP → SAP import |
| Contract expiry tracking | ❌ Manual | ✅ Auto-calculated | Formula: Deployed Date + Contract Term |
| Reports & dashboards | ⚠️ Standard Zoho | ✅ Custom ACX | 7 reports + 3 role-specific dashboards |

### Daily Workflow Comparison

**Before (Current State)**:
```
Sales creates an opportunity
  → manually types the stage from memory
  → uploads documents when they remember (no enforcement)
  → emails Pre-Sales or Commercials asking for approval
  → tracks contract dates and renewals in a personal Excel sheet
  → no one knows whether pricing is complete
  → no automatic handoff to Service Delivery
  → EdgeOS and SAP teams wait for manual email notification
```

**After (Target State)**:
```
Sales creates an opportunity
  → enters all required fields (Contract Term, Site, Deal Type)
  → enters pricing in structured subforms (Colocation Pricing + Additional Products)
  → uploads PO/SOF document to the opportunity
  → clicks "Move to SOF MSA" in the Blueprint
  → Blueprint validates: all pricing filled? PO uploaded? Fields complete?
  → Pre-Sales receives auto-approval request → approves with comments
  → Commercials receives auto-approval request → approves with comments
  → Stage automatically moves to SOF MSA
  → Email notification fires to: Sales Leads, Sales Heads, CBO, Service Delivery
  → Service Delivery receives order → deploys → sets Deployed Date
  → Sales Ops uploads MSA → moves to SOF Contracted
  → EdgeOS synced automatically via pushToEdgeOS function
  → SAP billing export generated via generateSAPExport function
  → 90/60/30 days before expiry: auto-reminder sent to Sales Ops
  → On renewal: Renewed Through Date updated → cycle continues
  → On expiry or cancellation: stage set to SOF Expired or SOF Cancelled
```

### Behavioral Changes by Team

| Team | What Changes Today | What Stays the Same |
|---|---|---|
| **Sales** | Must fill pricing subforms (not free-text notes). Must upload PO/SOF before moving to SOF MSA. Cannot skip stages or back-date. Gets auto-notified on approval/rejection/resubmit requests. | Still creates opportunities, accounts, contacts, logs calls and meetings. Still drives the customer relationship. |
| **Sales Ops** | Must actively validate pricing before SOF MSA. Receives daily order book report. Manages contract renewals (expiry tracking). Has edit access post-SOF-Contracted (Sales loses it). | Still responsible for data accuracy. Still point of contact for pricing validation. |
| **Pre-Sales** | Must log into ZohoCRM and approve/reject SOF MSA requests with technical comments. Gets auto-email notification when action is needed. | Still validates technical feasibility. Still the technical point of contact. |
| **Commercials** | Must log into ZohoCRM and approve/reject SOF MSA requests with commercial comments. Gets auto-email only after Pre-Sales approves. | Still validates commercial terms. Still the commercial point of contact. |
| **Service Delivery** | Gets auto-notified on new orders (no more waiting for email). Must set Deployed Date in ZohoCRM when deployment completes (triggers SAP billing). | Still responsible for physical deployment. |
| **IT** | Manages EdgeOS and SAP integration code (Custom Functions, schedulers, sync status monitoring). Administers ZohoCRM roles, profiles, permissions. | Still the system administrator. |

### Effort Breakdown

| Workstream | Est. Days | % of Total |
|---|---|---|
| ZohoCRM internal configuration (Phases 0–6, 8–9) | 25–35 | 45–50% |
| EdgeOS integration (Custom Function, API, scheduler) | 5–8 | 10–12% |
| SAP integration (Custom Function, CSV, SFTP, polling) | 5–7 | 10–12% |
| Testing + UAT | 5–7 | 10% |
| Training + Data Migration | 3–5 | 6–8% |
| Go-Live + Hyper-care | 10 | 14–16% |
| **Total** | **55–75** | **100%** |

> **Note**: Integration work (~30–40%) can proceed independently of internal CRM work. Phases 0–6, 8–9 do not depend on EdgeOS or SAP teams.

---
|---|---|---|---|
| 1 | SiteID values list | Sales Ops / IT | Blocks auto-number setup |
| 2 | 6-digit counter: global or per SiteID | Sales Ops / IT | Blocks auto-number setup |
| 3 | Deployed Date ownership | Service Delivery / Sales Ops | Blocks contract expiry auto-calculation |
| 4 | Expiry notification interval (single/staged) | Sales Ops | Blocks scheduler config |
| 5 | CSAT Dashboard — in-scope or separate? | Stakeholder decision | Resourcing and timeline |
| 6 | EdgeOS API availability & auth method | EdgeOS Team | Blocks integration design |
| 7 | SAP integration file format (CSV/API) | SAP Team | Blocks integration design |
| 8 | Approval escalation SLA (48 hrs? different?) | Sales Ops / Pre-Sales / Commercials | Blocks approval config |
| 9 | Standard price list for validation or all negotiated? | Sales Ops / Commercials | May affect pricing workflow |
| 10 | Can a combined PO+MSA document serve both requirements? | Sales / Legal | Affects document validation rules |
| 11 | Terminal transitions — which stages can go to Lost/Dropped/Material Change? | Sales / Sales Ops | Affects Blueprint design |
| 12 | Renewal — new opportunity or update existing? | Sales Ops | Affects contract management design |

---

## Estimated Implementation Phasing

| Phase | Effort Estimate | Dependencies |
|---|---|---|
| P0: Roles & Security | 2–3 days | Org chart confirmation |
| P1: Module Config & Fields | 5–7 days | SiteID + auto-number decisions |
| P2: Blueprint (Pipeline) | 3–5 days | P1 complete, stage definitions signed off |
| P3: Approval Workflows | 3–4 days | P2 complete, approval sequence confirmed |
| P4: Pricing Validation | 2–3 days | P1 complete, price list decision made |
| P5: Document Management | 1–2 days | P1 complete |
| P6: Notifications | 3–5 days | P2/P3 complete, interval decisions made |
| P7: Integrations (EdgeOS + SAP) | 10–15 days | API specs from EdgeOS/SAP teams |
| P8: Contract Management | 2–3 days | P1 complete, Deployed Date ownership decided |
| P9: Reports & Dashboards | 3–5 days | P1–P6 complete, data flowing |
| Testing + UAT | 5–7 days | All phases complete |
| Training + Data Migration | 3–5 days | Before go-live |
| Go-Live + Hyper-care | 10 days | All above |
| **Total** | **~55–75 days** | Depends on open decisions and team availability |
