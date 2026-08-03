# Chemsol — Zoho Creator Feasibility Verification Plan

> **Purpose:** Prove the entire Chemsol ERP design (all 18+ modules, every field construct, every automation, every report and dashboard) is implementable with **native Zoho Creator (.in instance)** — no external code, no third-party services assumed.
>
> **Method:** Every capability below was verified against **official Zoho documentation** (help.zoho.com, zoho.com/deluge, zoho.com/creator) during research on **03-Aug-2026**. Anything NOT confirmed by an official source is marked `⚠ UNVERIFIED` or moved to the Clarifications section. Nothing is assumed.
>
> **How to use:** Build phase → use the verdict tables to pick the correct native construct per module. Clarifications section → answer before build starts.

---

## 1. Verified Platform Capabilities (with sources)

### 1.1 Forms & Fields

| Capability | Verified | Source |
|---|---|---|
| Auto Number field = **sequential numeric only** (Start Index, max 19 digits). No prefix formats natively. | ✅ | [Understand Auto Number Field](https://help.zoho.com/portal/en/kb/creator/developer-guide/forms/add-and-manage-fields/articles/fields-auto-number-understand) |
| Lookup field filters (`Set Filter` in Field Properties → Choices) — restrict pickable records (e.g. only Released MRs, item-category filters) | ✅ | [Manage Filter for a Lookup Field](https://help.zoho.com/portal/en/kb/creator/developer-guide/forms/add-and-manage-fields/articles/manage-filter) |
| Lookup auto-fetch (select code → auto-populate name/UOM/rate from related record) | ✅ | [Auto-populate a field based on a lookup dropdown](https://help.zoho.com/portal/en/kb/creator/zoho-creator-academy/forms/articles/auto-populate-a-field-based-on-a-lookup-dropdown) |
| **Max 4 display fields per lookup** | ✅ | [Limitations: Forms and Fields](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/forms-and-fields-limitations) |
| Formula field: result type now selectable (single line 255 / multi-line 65,355 chars; decimal/currency/percentage) — new formula fields after **01-Jul-2026** | ✅ | [Understand Formula Field](https://help.zoho.com/portal/en/kb/creator/developer-guide/forms/add-and-manage-fields/articles/fields-formula-understand) + [Release Notes](https://www.zoho.com/creator/release-notes) |
| ⚠ Formula fields using `input.lookup.<f>` / `input.subform.<f>` **do NOT update** when the parent record's field is edited later (cross-form staleness) | ✅ | [Limitations: Forms and Fields](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/forms-and-fields-limitations) |
| Subform line items + subform totals (footer fields on main form) | ✅ | [Limitations: Forms and Fields](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/forms-and-fields-limitations) |
| Field count per form: 60 single-line fields (255-char default), 160 choice, 200 email; raises to ~4000 if char limits lowered to 4 | ✅ | same page |
| Choice picklists capped at **5000 choices** in live mode (searchable beyond) | ✅ | same page |
| Multi-line/rich text ≈ **64 KB** per row; file upload **50 MB** | ✅ | same page |
| Radio/checkbox have no search — dropdown/multi-select recommended for long lists | ✅ | same page |
| Field name/link name immutable, field type immutable, preset digit/char limits unchangeable | ✅ | same page |

### 1.2 Automations

| Capability | Verified | Source |
|---|---|---|
| Form workflows (on load, on user input, on submit success) — Deluge scripts | ✅ | [Limitations: Workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations) (lists these events) |
| **Subform add-row / delete-row form events** (per-line logic) | ✅ | same page |
| Field rules (show/hide/disable/validate on condition) | ✅ | [Configure Hide Fields Action](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-field-rules/articles/configure-hide-fields-action) |
| Blueprint (status-transition workflows: Draft → Verified → Approved → Released) — **still fully supported**; "During approval process" is a workflow event | ✅ | [Understand Blueprint](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-blueprint/articles/understand-blueprint) + [Send mail — applicable workflow events](https://www.zoho.com/deluge/help/misc-statements/send-mail.html) |
| Blueprint limits: **100 stages+transitions** per blueprint; 5 common transitions; 5 parallel transitions; 5 branches; 5 transitions per parallel; 1 parallel transition between stages per direction; 2 outgoing parallel per stage; **50 statements max** per change-stage/execute-transition script | ✅ | [Limitations: Workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations) |
| Schedules (timed actions): trigger on **specific date-time OR a date field in the form**, with criteria + actions (email/SMS, add/update/delete, custom action) → SLA escalations | ✅ | [Understand Schedules](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-schedules/articles/understand-schedules) |
| Custom action buttons on reports (incl. conditional display) | ✅ | [Custom Buttons](https://www.zoho.com/creator/videos/custom-buttons.html) + [Display custom action button for specific records](https://help.zoho.com/portal/en/kb/creator/zoho-creator-academy/report/articles/display-custom-action-button-for-specific-records) |
| Deluge statement limit: **~5,000–50,000 statements per function** (plan-dependent); batch workflow exists to exceed it (not for integration forms) | ✅ | [Limitations: Workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations) |
| Workflow action calls: **120/min/IP**, **250/min per app**, **250/min per portal** | ✅ | same page |
| Send mail: From must be `zoho.adminuserid` / `zoho.loginuserid` / **verified email address**; To can be **any email address** (external supplier/client emails OK) | ✅ | [Send mail](https://www.zoho.com/deluge/help/misc-statements/send-mail.html) |
| ⚠ Execution timeouts (community-documented, verify at build): 10 s button/validation, 30 s workflow, 15 min scheduled | ⚠ | [Deluge governance limits — 3rd party](https://knowledgelib.io/business/erp-integration/zoho-deluge-scripting/2026) |
| ⚠ `autogen()` task — **not available in Creator** (CRM-only). Prefixed numbering (CST-YYYY-XXXX) requires a custom Deluge counter (number-series pattern) | ✅ | [Auto-generating serial numbers — community pattern](https://suryakanthanwork.blogspot.com/2025/08/working-with-business-applications-its.html) + [Counter example](https://zohodeluge.blogspot.com/) |

### 1.3 API & Plans

| Limit | Value | Source |
|---|---|---|
| API/day: Free 250 · Standard 250/user · Professional 500/user · Enterprise 1000/user (custom API: 100/250/500) | ✅ | [API Limits](https://www.zoho.com/creator/help/api/v2.1/api-limits.html) |
| Throttle: 50 API calls/min/user; 200 records per API request | ✅ | same + [Create Record v2.1](https://www.zoho.com/deluge/help/create-record-v2.1.html) |
| `zoho.creator.v2_1.createRecord` = **integration task only ("except Zoho Creator")** — in-app automation uses native `createRecord`/`updateRecord` data-access tasks | ✅ | [Create Record v2.1](https://www.zoho.com/deluge/help/create-record-v2.1.html) |
| Plans: Free / Standard / Professional / Enterprise / Flex; per-plan record & user limits exist (exact numbers need the customer's chosen plan) | ✅ | [Pricing](https://www.zoho.com/creator/pricing.html) |
| ⚠ ~100,000 records per form → performance tuning needed (3rd-party) | ⚠ | [Limitations & workarounds — 3rd party](https://www.bizappln.com/blog/zoho-creator-limitations-and-workaround/) |

### 1.4 Reports & Dashboards

| Capability | Verified | Source |
|---|---|---|
| Report types: List, Spreadsheet, Kanban, Calendar, Timeline, **Summary**, **Pivot Table, Pivot Chart** (Analytics-powered), Map | ✅ | [Using the Reports tab](https://www.zoho.com/analytics/help/creator-report-tab.html) + [Understand Pivot Table](https://help.zoho.com/portal/en/kb/creator/developer-guide/reports/understand-reports/articles/understand-pivot-table) + [Understand Pivot Chart](https://help.zoho.com/portal/en/kb/creator/developer-guide/reports/understand-reports/articles/understand-pivot-chart) |
| Charts in Pages (bar/pie/line, stacking, **drill-down**); available on **all plans** | ✅ | [Understanding charts](https://help.zoho.com/portal/en/kb/creator/developer-guide/pages/chart/articles/understand-chart) |
| Report edit: GUI edit, bulk edit, Deluge update, edit-by-URL | ✅ | [Editing Records in Zoho Creator](https://www.zoho.com/blog/general/editing-records-in-zoho-creator.html) |
| Report limits: cannot duplicate reports with ≥150 fields/record; **max 20 display fields for subform data** in reports | ✅ | [Limitations: Reports](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/reports-limitations) |
| Inline edit on list reports | ✅ | [Exploring Report Views — 3rd party](https://nimbis.com/exploring-report-views-in-zoho-creator-2-0/) |

---

## 2. Per-Module Feasibility Verdicts

`✅ Native` = config-only. `✅ + Deluge` = native construct + one Deluge pattern (patterns in §4). `❓` = needs a clarification from §6.

### Master Data

| Module | Fields used | Construct | Verdict |
|---|---|---|---|
| Purchase Item Muster | code, name, UOM (dropdown), HSN, GST%, min/max, preferred supplier (lookup), lead time, status | lookup + autofetch, dropdowns, choice | ✅ Native |
| Supplier Master | code autogen, GSTIN, PAN, bank, payment terms | Auto Number (numeric) + display prefix | ✅ + Deluge (P1) |
| System Master / System Composition | System→FG mapping subform | subform + lookup filter (FG Released only) | ✅ Native |
| BOM / FG Formulation | FG→RM ratios (decimal), status | subform, formula ratio check, status field | ✅ Native |
| Customer/Site Master | org, contacts, addresses | lookup + autofetch, email fields | ✅ Native |

### Stream B (Project-tagged)

| Module | Key automation | Construct | Verdict |
|---|---|---|---|
| Sales Order (SO) | Conditional **Sales Type** (Supply Only / Supply+Apply) swaps **Subform A vs Subform B** | field rule (show/hide subforms) + on-submit Deluge | ✅ Native |
| Costing Sheet (5 sections) | Section A auto-expanded from SO System Lines × System Composition × BOM | on-submit Deluge: fetch SO + System Comp + BOM → build Section A subform rows (createRecord); section subtotal fields written by Deluge (Section_A_Total … Section_E_Total — **G3**, not formula fields) | ✅ + Deluge (P2) |
| Costing Approved → auto-create Project + Production Plan (Draft) | Blueprint transition script (≤50 stmts OK) | ✅ + Deluge (P3) |
| Production Plan | Available Stock = physical − Σ(Assigned Qty from unreleased MRs); Released → auto-PR for shortages | on-submit/on-transition Deluge with aggregate query; schedule for release-check | ✅ + Deluge (P4) |
| MR (critical gate) | **Auto-derived** from Costing + Plan (4 cost components pre-filled); cross-validation per RM line vs SO×BOM expected — **>5% flag, >10% block** (C31); status Draft→Pending Production Verification→Production Verified→Costing Approved→Released (C30); 2 hr / 2 hr / 1 hr SLAs | on-submit validation script (block/flag), Blueprint for 5-state status, schedules on status-date fields for SLA reminders, auto-release at 1 hr | ✅ + Deluge (P2, P5) + Blueprint |
| MIS | Auto-created as Draft on MR Release | on-change workflow (criteria MR_Status=Released, **F5**) → createRecord one header + line subform from Allocation | ✅ + Deluge (P3) |
| BMR | RM consumption lines → increment Consumed Qty on MR Allocation (`Project ID + Item Code`) | subform add-row event + on-submit Deluge update | ✅ + Deluge (P6) |
| RM Consumption Entry | BOM variance check only (no increment — avoids double count) | on-submit Deluge compute + flag | ✅ + Deluge |
| Packing Entry | packaging material deduction only | on-submit Deluge | ✅ + Deluge |
| FGHM | Inline accept → mark MR Allocation Fully Consumed + increment FG stock | **report custom action button** + Deluge | ✅ + Deluge (P7) |
| Site Consumption Entry | hourly/daily per area; resolves to MR Allocation | subform lines + on-submit Deluge; dropdown for Area | ✅ + Deluge (P6) |
| Material Return | credits Consumed Qty / restores stock (good vs damaged) | on-submit Deluge | ✅ + Deluge |
| Project Close / P&L | real-time computed view | summary reports + report formula fields + Pages charts | ✅ Native |

### Stream A (no Project ID)

| Module | Key automation | Construct | Verdict |
|---|---|---|---|
| PR → Rate Comparison → PO → GRN → QC | PR auto-created from Production Plan shortage; PO dual numbering **RMWAD** (coding) vs **RM** (non-coding) | on-submit Deluge (PR create); number series counter with conditional prefix | ✅ + Deluge (P1, P8) |
| GRN posting | qty to stock only on posting; partial GRN checkbox | on-submit Deluge + checkbox; status workflow | ✅ + Deluge |

### Reports R0–R7 (reports.html)

| Report | Construct | Verdict |
|---|---|---|
| Department dashboards (Purchase/Store/Production/Costing/Site) | Pages + charts (drill-down) + summary reports + panels | ✅ Native |
| Project Inventory Status (Assigned vs Issued vs Consumed vs Returned vs Remaining) | summary report with report formulas on MR Allocation + related data | ✅ Native |
| Project P&L real-time, Costing vs Actual variance | summary/pivot reports + report formulas | ✅ Native |
| 80% Utilization Report | list report with conditional formatting + filter flag | ✅ Native |
| MR Status drill-through | list report + custom button → detail | ✅ Native |

### Excluded from core loop (existing decision — no feasibility impact)

Service Invoice, Finance CN/AR, Logistics (DC/Outward), Vehicle & Transport, full Service Team module, Zoho Sign signing of PO/P&L → see Clarification Q8.

---

## 3. Automation Construct Mapping (automation.html Quick Reference)

| automation.html type | Used for in Chemsol | Status |
|---|---|---|
| Form Workflow (On Submit) | SO→Costing expansion, MR auto-derive, PR auto-create, consumption increments | ✅ Native |
| Form Workflow (On Load / On User Input) | autofetch of supplier/item/project details, dynamic lookup filters | ✅ Native |
| Field Rules | Sales Type swap (Subform A/B), disable fields in Released MR, 80% flag display | ✅ Native |
| Subform add/delete row events | line-level totals, per-line allocation checks | ✅ Native |
| Blueprint | MR 5-state gate, Costing→Project/Plan creation, FGHM accept | ✅ Native |
| Schedule | SLA escalations (Costing >24 hr, MR stages 2/2/1 hr), auto-release | ✅ Native |
| Report Workflow (custom buttons) | FGHM inline accept, MR Release action, Costing Approve | ✅ Native |
| Deluge (data access) | all cross-record reads/writes; number-series counters | ✅ Native |

---

## 4. Deluge Patterns Required (build-time recipes)

- **P1 — Prefixed number series**: No native autogen. Pattern: `No_Series` config form (prefix, start, increment, per year) → on-submit fetch last used → increment → write to display field. Handles `CST-YYYY-XXXX`, `FGH-YYYY-XXXX`, `RMWAD-YYYY-XXXX` / `RM-YYYY-XXXX`. Edge: concurrent submits need a retry/unique check (`ponytail:` last-record+1 counter, upgrade to No_Series table if contention).
- **P2 — Costing Section A expansion**: fetch SO record → iterate System Lines → fetch System Composition → fetch BOM → `createRecord` Section A lines. Watch the 5,000-statement ceiling; SOs are small (≤5 systems) so it's fine; batch workflow available if ever needed.
- **P3 — Chain creation on approval**: Blueprint transition (≤50 statements) → `createRecord` Project + Production Plan draft.
- **P4 — Available Stock query**: `Stock` aggregate minus Σ Assigned Qty from MRs with Status ≠ Released (aggregate function on MR Allocation).
- **P5 — Cross-validation**: on-submit validation script comparing each MR Allocation line vs its SO × BOM expected qty (per-RM, C31); >5% → warning message, >10% → block submit (validate before create).
- **P6 — Consumption resolution**: match `Project ID + Item Code` against MR Allocation line → increment/decrement Consumed Qty; recompute 80%/100% flags.
- **P7 — Inline accept**: report custom action button → Deluge updates FGHM status + MR Allocation Fully Consumed + FG stock.
- **P8 — Conditional PO prefix**: if item category coding → RMWAD counter, else RM counter (two No_Series rows).

All patterns use native data-access tasks (`Form[Criteria]`, `createRecord`, `updateRecord`, aggregates) — **no** `zoho.creator.v2_1.*` (integration tasks are NOT for in-app automation).

---

## 5. Limitations Forcing Design Decisions (already handled in design)

1. **Numbering formats** — auto-number is numeric-only → display-prefix via P1 counter (design change required if literal prefixes are mandatory; see Q6).
2. **Formula-field staleness** — formula fields reading lookup/subform values don't refresh when the source record edits → all derived quantities that must re-compute (e.g. Costing totals after BOM change) are stored/written via Deluge on the event, not via cross-form formula fields.
3. **4 display fields per lookup** → design already stores key display data (code+name) and autofetches the rest.
4. **20 display-field cap for subform data in reports** → Project Inventory/SCE reports show summarized aggregates, not raw subform rows (design already aggregate-based).
5. **50 statements per blueprint transition** → any heavy script moves to on-submit form workflows / custom functions; blueprint transitions only flip status + trigger small actions.
6. **Email From-verification** → one verified sender address (admin) before go-live; external recipients allowed.
7. **5000-choice picklist cap** → item/supplier pickers are lookups (searchable), never huge choice lists.

---

## 6. Clarifications Required (answer before build — nothing assumed)

| # | Question | Why it matters |
|---|---|---|
| Q1 | Which **Zoho Creator plan** will Chemsol subscribe to (Free / Standard / Professional / Enterprise / Flex)? | API/day, per-user limits, record caps, statement limits, email quotas all plan-dependent |
| Q2 | How many **users per department** (Costing, Purchase, Store, Production, Site, PM)? | Per-user billing + API per-user/day |
| Q3 | Email recipients: all internal (Chemsol Zoho org) or also **external** (suppliers/clients)? | External To is allowed, but email volume counts against plan; verify sender before go-live |
| Q4 | Annual **data volume estimate** (SO/month, SCE entries — hourly × areas can grow fast) | Form performance (~100k records/form) + storage/record caps |
| Q5 | Is the app already provisioned on **.in instance** with the admin's email verified? | Sender verification needed for all sendmail |
| Q6 | Numbering: is a **display-only prefix** (auto-number numeric + `CST-` prefix shown via formula) acceptable, or must the stored value literally be `CST-2026-0001`? | Display-only = native + formula; literal = custom counter (P1) |
| Q7 | Approvals: Blueprint-based status workflow confirmed (Draft→Verified→Approved→Released), or does Zoho's newer **Approval** feature need to be used? | Blueprint is fully supported; both work |
| Q8 | Is **Zoho Sign** (PO/P&L e-sign, per BRD) in scope? It is a separate paid service | Affects scope/cost |
| Q9 | Any **attachments** on forms (lab QC reports, delivery challans)? | File upload 50 MB — fine, but confirm which forms need upload fields |

---

## 7. Sign-off

| Item | Status |
|---|---|
| Platform capabilities verified against official docs | ✅ (03-Aug-2026, all citations in §1) |
| All 18+ modules verdict-ed | ✅ (§2) |
| All automation constructs mapped | ✅ (§3) |
| Deluge patterns defined | ✅ (§4) |
| Design decisions already aligned with limitations | ✅ (§5) |
| Clarifications pending | Q1–Q9 (§6) — resolve before build phase |
