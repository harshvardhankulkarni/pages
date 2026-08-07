# AdaniConneX — ZohoCRM Sales Automation for Data Center Opportunities

## Business Domain

AdaniConneX uses ZohoCRM to automate sales workflows across lead management, sales cycle, contracting, and capacity management. This repo focuses on **Data Center Opportunities** lifecycle, from creation through `SOF Contracted` (100%).

## Core ZohoCRM Modules

| Module | Purpose |
|---|---|
| Accounts | Companies with a business relationship |
| Data Center Opportunity | Tracks DC product sales lifecycle |
| Contacts | People at each Account |
| Calls / Meetings | Logged interactions with Contacts |
| Documents | MSA, SOF, PO, NDA, LOA (linked to modules) |
| EDC Products | Ancillary product catalog (maintained by Sales Ops) |
| Colocation Pricing | Colo space+power pricing (Per Rack or Per KW) |
| Additional DC Products & Services | Supplementary products with recurring/one-time costs |

## Sales Pipeline Stages

| Stage | Probability | Trigger |
|---|---|---|
| Suspect | 10% | Potential DC need identified |
| Prospect | 25% | Budgetary proposal shared |
| Funnel | 50% | RFP received, firm proposal submitted |
| Negotiation | 75% | Commercial/SLA negotiations underway |
| SOF MSA | 90% | PO/SOF executed (mandatory attachment) |
| SOF Contracted | 100% | MSA signed (mandatory attachment) |
| Lost / Dropped / Did Not Participate / Material Change | 0% | Terminal/closed-lost |

## Key Teams & Handoffs

- **Sales** — Creates/maintains Opportunities, Accounts, Contacts, Calls, Meetings
- **Sales Operations** — Validates pricing, drives data accuracy; approves on `SOF MSA` stage
- **Product / Commercials** — Validates commercial details; approval required on `SOF MSA`
- **Pre-Sales** — Validates technical feasibility; approval required on `SOF MSA`
- **IT** — Administers the system
- **Service Delivery** — Receives order notification; initiates billing in SAP

## Data Integrity Rules

- Pre-`SOF Contracted`: Sales + Sales Ops can edit
- Post-`SOF Contracted`: Only Sales Ops + Admins can edit
- Post-Deployment: Only Admins can edit

## Critical Field: Opportunity Reference ID

Auto-generated pattern: `{SiteID}-{6DigitNumber}-{Version}` (e.g., `EDCPOR01-219350-5`). Used by all downstream systems.

## Document Requirements

| Stage | Required Document |
|---|---|
| Move to `SOF MSA` | Purchase Order or Sales Order Form |
| Move to `SOF Contracted` | MSA (Master Service Agreement) |
| Optional | NDA (on Account/Opportunity), LOA |

## Pricing Architecture

- **Colocation Pricing** module: captures rack count, power density (KW), pricing type (Per Rack or Per KW), deal type (Metered Pricing with PUE or All-in-Bundled), monthly rate + OTC
- **Additional DC Products & Services** module: captures ancillary products from the catalog
- **EDC Products** module: product catalog maintained by Sales Ops

## Dependent Systems

- **EdgeOS Portal** — Syncs every 15 min with `SOF Contracted` opportunities; controls data center visibility and contracted power limits
- **SAP** — Billing; initiated by Service Delivery after deployment
- **Managed Engine** — IT asset management (Praise/Krishna)

## Third-Party Integrations — Technical Detail

### EdgeOS Portal (ZohoCRM → EdgeOS, every 15 min)

**Trigger**: Stage change to `SOF Contracted` + scheduler every 15 min for batch sync.

**Deluge Pseudocode (Custom Function `pushToEdgeOS`)**:
```
1. Query ZohoCRM: Get all opps where ACX Sales Stage = "SOF Contracted"
2. Join Colocation Pricing subform, sum Contracted Power (KW)
3. Build JSON payload per opportunity:
   {
     "opportunityRefId": "EDCPOR01-219350-5",
     "customerName": "Acme Corp",
     "siteId": "EDCPOR01",
     "contractedPowerKW": 250,
     "contractStatus": "Active",
     "contractExpiryDate": "2029-06-15"
   }
4. POST payload to EdgeOS REST API endpoint:
   POST https://edgeos.adaniconnex.com/api/v1/sync-opportunity
   Headers: Authorization: Bearer {api_key}, Content-Type: application/json
5. EdgeOS validates → upserts customer + site + power limit
6. Update sync status on opportunity: "Synced" (200 OK) or "Sync Failed" (retry next run)
```

**What EdgeOS must provide**: REST API endpoint, auth mechanism (API key/OAuth), network accessibility from Zoho servers, upsert logic for customer+site+power limits.

**Fallback (no API)**: Zoho generates JSON file → SFTP to EdgeOS-polled folder. Less real-time, works without API.

### SAP Billing Integration (ZohoCRM → SAP, trigger on Deployed Date)

**Option A — File-based (recommended initially)**:
```
1. On Deployed Date update, Custom Function "generateSAPExport":
   - Query opportunity + all pricing subforms (Colo + Additional)
   - Map to SAP structure: customer master, material codes, quantities, prices
   - Generate CSV with fixed-width columns per SAP spec
   - Write file to SFTP server that SAP polls

2. SAP team schedules import job:
   - Picks up file from SFTP, validates, creates billing documents
   - Writes confirmation file back to SFTP

3. Zoho scheduler polls for confirmation:
   - Updates opportunity status to "Billing Confirmed"
```

**Option B — Direct API (future state)**: Custom Function calls SAP RFC/REST API directly; billing created synchronously; immediate confirmation.

**What SAP must provide**: BAPI/RFC or REST API for billing (`BAPI_BILLINGDOCUMENT_CREATEMULTIPLE`), SFTP drop folder (Option A) or web service endpoint (Option B), product-to-material-code mapping, SAP team availability.

**Integration effort**: ~30–40% of total project. Can proceed independently of internal CRM work (Phases 0–6, 8–9).

## CRM Flow Changes — Before vs After

### Current State (As-Is)

| Capability | Status | Gap |
|---|---|---|
| Accounts & Contacts creation | ✅ Exists | May need field additions |
| Opportunity creation | ✅ Exists | New fields needed (Contract Term, Renewal Periods, etc.) |
| Manual stage updates | ✅ Exists | No enforcement, free-form |
| Calls & Meetings logging | ✅ Exists | Minor if any changes |
| Basic document upload | ⚠️ Probably exists | No stage-gate enforcement |
| Pricing entry | ⚠️ Partial | May not use structured subforms |
| EDC Products catalog | ❌ Needs creation | ~50 products to seed |
| Stage gate enforcement | ❌ None | No validation on transitions |
| Document-stage linkage | ❌ None | PO/SOF, MSA not enforced |
| Approval workflows | ❌ None | Pre-Sales + Commercials not configured |
| Automated notifications | ❌ None | All need creation |
| EdgeOS sync | ❌ New build | Does not exist |
| SAP billing trigger | ❌ New build | Does not exist |
| Contract expiry tracking | ❌ None | Auto-calculation + renewal fields needed |
| Reports & dashboards | ⚠️ Partial | Standard Zoho reports exist; custom ACX needed |

### Daily Workflow — Before vs After

**Before (Current)**:
```
Sales creates opportunity → manually types stage → uploads docs when remembered
→ emails someone for approval → tracks contract dates in Excel
→ no one knows when pricing is complete → no automatic handoff to Service Delivery
```

**After (Target)**:
```
Sales creates opportunity → picks correct stage from controlled picklist
→ enters pricing in structured subforms (Colocation Pricing + Additional Products)
→ uploads PO/SOF → clicks "Move to SOF MSA"
→ Blueprint enforces: all pricing filled? PO uploaded?  ✓
→ Pre-Sales auto-notified → approves → Commercials auto-notified → approves
→ Stage moves to SOF MSA → Email notification fires to Service Delivery + Sales Heads
→ Service Delivery deploys, sets Deployed Date
→ Sales Ops uploads MSA, moves to SOF Contracted
→ EdgeOS synced automatically → SAP billing scheduled
→ Auto-reminder for contract renewal sent to Sales Ops before expiry
```

### Behavioral Changes by Team

| Team | What Changes |
|---|---|
| **Sales** | Must fill pricing subforms (not free-text). Must upload PO/SOF before stage moves. Cannot skip stages. Gets auto-notified on approvals/rejections. |
| **Sales Ops** | Must validate pricing before SOF MSA. Receives daily order book report. Manages contract renewals. Can edit post-SOF-Contracted. |
| **Pre-Sales** | Gets approval request when Sales clicks "Move to SOF MSA". Must approve/reject with comments. |
| **Commercials** | Gets approval request only after Pre-Sales approves. Must validate commercial terms. |
| **Service Delivery** | Gets auto-notified on new orders. Sets Deployed Date to trigger billing. |
| **IT** | Manages integrations (EdgeOS, SAP). Administers roles and permissions. |

## Contract Management Fields (on Data Center Opportunity)

- `Contract Term (Months)` — Initial term
- `Renewal Periods` — Number of renewal options
- `Years Per Renewal` — Years per extension
- `Contract Expiry Date` — Auto-calculated: `Deployed Date + Contract Term`
- `Renewed Through Date` — Manual entry for renewals
- Stage `SOF Expired` or `SOF Cancelled` for end-of-life

## Notifications (Auto-Triggered)

- Account creation → immediate
- Opportunity creation → immediate
- New order book → immediate
- Stage movement to `SOF MSA` → immediate + order delivery notification
- Order book (scheduled) → per scheduler
- Contract expiry approaching → per scheduler
- Sent from ZohoCRM Admin (Lance Devin)

## CSAT Dashboard Project (separate initiative)

Customer feedback collection via QR codes at DC sites + email scheduler. Integrates ratings from Sales, Service Delivery, Service Assurance, Security, Billing, Customer Experience, and Overall Organization departments. Dashboard with real-time aggregation, historical views, and departmental breakdowns.

## Product Families Catalogs

- Cross-Connects (Fiber, Copper)
- Rack Cabinets (42U–52U, various widths)
- PDUs (Basic/Intelligent, 1Ph/3Ph, 16A–63A)
- CCTV, Biometrics, Caging (Mesh/Opaque)
- Structured Cabling, ATS, STS, Blanking Panels, Duct
- Services: Remote Hands, Smart Hand, Migration, Staff Augmentation, Lift & Shift
- Supplementary Cooling, Cold Aisle Containment
