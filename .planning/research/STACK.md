# Technology Stack

**Project:** Chemsol — Zoho Creator Application
**Researched:** 2026-06-24

## Recommended Stack

### Core Platform
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Zoho Creator | Latest (2026) | Application platform | Low-code, built-in mobile, India datacenter |
| Deluge | Latest | Automation, workflows, integrations | Zoho's native scripting — only option in Creator |
| Zoho Creator Forms | Latest | UI forms, subforms, lookups | Native form builder, conditional fields, auto-fetch |
| Zoho Creator Pages | Latest | Dashboards, printable reports | Built-in report builder with charts |
| Zoho Creator Approval | Latest | PR/PO/MR approval chains | Native approval engine with escalation |

### Data & Storage
| Technology | Purpose | Why |
|------------|---------|-----|
| Zoho Creator DB (Postgres-based) | All form data | No separate DB needed — Creator handles persistence |
| Zoho Creator File Attachment | PO/BOQ uploads | Native file storage, max 20MB per file |
| Zoho Creator Audit Log | Change tracking | Built-in audit trail for all CRUD operations |

### Integration
| Technology | Purpose | Why |
|------------|---------|-----|
| Deluge `invokeurl` | Future Zoho Books/CRM sync | Built-in HTTP client with OAuth connection support |
| Zoho OAuth (Self Client) | Future external API access | Standard Zoho auth pattern |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Platform | Zoho Creator | Custom web app (React + Node) | 10x slower delivery, no mobile, higher TCO |
| Automation | Deluge | Python scripts + API | No server to run them, Creator integration requires invokeurl |
| Database | Creator DB | External PostgreSQL | Latency, auth complexity, no native Creator binding |

## Key Constraints

- **No local development** — all forms built in Zoho Creator UI
- **No package manager** — Deluge has no npm/pip equivalent
- **No test framework** — Deluge has no unit testing; test via Creator UI
- **India datacenter** — all API base URLs use `.in` domain
- **Deluge timeout** — workflows must complete within 5 minutes
