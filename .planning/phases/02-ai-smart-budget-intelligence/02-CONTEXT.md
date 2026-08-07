# Phase 2 Context: AI Integration — Smart Budget Intelligence

## Phase Goal
Add AI-powered intelligence to the Zoho Creator Budget Tracking & Inventory Management system: budget forecasting, anomaly detection, smart procurement, and natural language querying.

## Project Type
Zoho Creator low-code application with Deluge automation. AI integration will likely consume Zoho Creator API data and expose intelligence through the Zoho Creator UI or a companion web layer.

## Key Functionality Desired
1. **Budget Burn Forecasting** — Predict 30/60/90-day spend per project from historical expense + budget data
2. **Anomaly Detection** — Flag unusual spending patterns vs historical baselines and budget component limits
3. **Smart Procurement** — Recommend optimal reorder quantities/timing for inventory items
4. **Natural Language Reporting** — Allow project managers to ask questions in plain English (e.g., "Which project is over budget?")
5. **Automated Weekly Summaries** — Plain-English budget health summaries emailed to project managers

## Data Sources
- Zoho Creator forms: Projects, Budget_Plans, Budget_Components, Expenses, Inventory_Items, Purchase_Orders, Purchase_Requisitions
- Deluge workflow history and audit logs
- Historical transaction patterns

## Technical Constraints
- Zoho Creator low-code platform (no direct ML model hosting)
- Data accessible via Zoho Creator REST API or Deluge scripts
- AI layer likely external: Python service + hosted model or cloud AI service
- Must integrate back into Zoho Creator UI/notifications

## User Roles Benefiting
- Project Managers (budget forecasts, anomaly alerts)
- Finance Managers (budget health, overrun prediction)
- Procurement Team (reorder recommendations)
- Inventory Manager (stock-out prediction)
