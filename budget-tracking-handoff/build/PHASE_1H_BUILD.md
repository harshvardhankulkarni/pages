# Phase 1H Build Guide — FX Rates → Accounting Periods → Tax/GST Enhancements

## Dependencies
Requires Phase 1G complete (Vendor_Bills, Payments forms exist). Enhances existing forms — no new primary forms needed except Currency_Rates and Accounting_Periods.

---

## 1. Currency Exchange Rates Form (`Currency_Rates`)

Tracks daily FX rates for multi-currency support. Referenced by Bills, Invoices, and Payments for automatic rate lookups.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Rate ID | Auto Number | `Rate_ID` | Yes | Format: `FX-{0000}` |
| Base Currency | Dropdown | `Base_Currency` | Yes | Fixed at setup: `USD`, `EUR`, `GBP`, `INR` |
| Target Currency | Dropdown | `Target_Currency` | Yes | e.g., `EUR`, `GBP`, `INR`, `AED`, `SGD` |
| Rate | Decimal | `Rate` | Yes | 1 Base Currency = X Target Currency |
| Effective Date | Date | `Effective_Date` | Yes | Date this rate is valid from |
| Source | Dropdown | `Source` | No | `Manual`, `Bank Rate`, `API Feed` |

### Validation Rules
1. Base Currency ≠ Target Currency — cannot set rate for same currency
2. No duplicate rates — same Base + Target + Effective_Date combination must be unique
3. Rate must be > 0

---

## 2. Accounting Periods Form (`Accounting_Periods`)

Defines accounting periods (months/quarters) for period-end close and transaction period-locking.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Period ID | Auto Number | `Period_ID` | Yes | Format: `PER-{0000}` |
| Period Name | Text | `Period_Name` | Yes | e.g., "April 2026" |
| Period Type | Dropdown | `Period_Type` | Yes | `Monthly`, `Quarterly`, `Yearly` |
| Start Date | Date | `Start_Date` | Yes | First day of period |
| End Date | Date | `End_Date` | Yes | Last day of period |
| Status | Dropdown | `Status` | Yes | `Open`, `Closing`, `Closed` |
| Closed By | User Picker | `Closed_By` | No | Who closed this period |
| Closed Date | Date/Time | `Closed_Date` | No | When it was closed |

### Deluge — Period Close Validation
Add this validation script to the On Submit workflow of ALL financial forms (Expenses, POs, Vendor_Bills, Invoices, Payments, Inventory_Transactions, GRNs):

```deluge
/* JUSTIFICATION: Period-lock prevents financial transactions from being posted to closed accounting periods — a standard accounting control that cannot be enforced by form-level validation alone */

/* ===== PSEUDOCODE =====
   Trigger: On Submit — every financial form

   1. Get the transaction date from the current form
   2. Query Accounting_Periods where:
        Start_Date <= Transaction_Date <= End_Date
        AND Status == "Closed"
   3. If any matching closed period found:
        Alert: "Cannot post to closed period [Period_Name]. Please change the transaction date or contact Finance."
        Return (stop submission)
   4. If Status == "Closing":
        Show warning but allow with Finance override flag
   5. If no closed period matched: continue submission normally
   ===== END PSEUDOCODE ===== */

/* Implementation note: This script must be added to the On Submit workflow of:
   - Expenses, Budget_Approvals, Purchase_Orders, Goods_Receipts
   - Supplier_Credit_Notes, Vendor_Bills, Invoices, Payments
   - Inventory_Transactions (for financial impact)
*/
```

---

## 3. Tax/GST Enhancements

### 3.1 Vendor Bills — Enhanced Bill_Line_Items Subform

Add these fields to the existing `Bill_Line_Items` subform:

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Tax Classification | Dropdown | `Tax_Classification` | No | `Input GST`, `Input IGST`, `CESS`, `Non-Taxable`, `Zero-Rated`, `Exempt` |
| ITC Eligibility | Dropdown | `ITC_Eligibility` | No | `Full ITC`, `50% ITC` (personal use), `No ITC` (blocked credit) — Default: Full ITC |

### 3.2 Invoices — Enhanced Invoice_Line_Items Subform

Add these fields to the existing `Invoice_Line_Items` subform:

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Tax Classification | Dropdown | `Tax_Classification` | No | `Output GST`, `Output IGST`, `CESS`, `Non-Taxable`, `Zero-Rated`, `Exempt` — Default: Output GST |

### 3.3 Multi-Currency Fields on Existing Forms

#### Vendor_Bills header
Add:
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| FX Rate | Decimal | `FX_Rate` | No | Auto-populated from Currency_Rates on Bill Date |
| Base Currency Amount | Currency (Formula) | `Base_Amount` | No | `Total_Amount / FX_Rate` |

#### Invoices header
Add:
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Currency | Dropdown | `Currency` | No | Copied from Account — default to Base Currency |
| FX Rate | Decimal | `FX_Rate` | No | Auto-populated from Currency_Rates on Invoice Date |
| Base Currency Amount | Currency (Formula) | `Base_Amount` | No | `Total / FX_Rate` |

#### Payments form
Add:
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| FX Rate | Decimal | `FX_Rate` | No | Auto-populated from Currency_Rates on Payment Date |
| Base Currency Amount | Currency (Formula) | `Base_Amount` | No | `Amount / FX_Rate` |
| FX Gain/Loss | Currency (Formula) | `FX_Gain_Loss` | No | `(Linked Bill/Invoice FX Rate − Payment FX Rate) × Base Amount` |

### Deluge — FX Rate Auto-Population

Add this to the On Load or On Create workflow of Bills, Invoices, and Payments:

```deluge
/* JUSTIFICATION: FX rate must be looked up from the Currency_Rates table based on the transaction date — cannot be a static formula or form-level default */

/* ===== PSEUDOCODE =====
   Trigger: On Load / On User Input when date or currency changes

   1. Get the transaction date and currency from the current form
   2. If currency != Base Currency:
        Query Currency_Rates: find the most recent rate
          WHERE Target_Currency == form's currency
          AND Effective_Date <= Transaction_Date
          ORDER BY Effective_Date DESC
          LIMIT 1
   3. If rate found: populate FX_Rate field
   4. If no rate found: leave blank; show user note "FX rate not found — enter manually or create rate in Currency_Rates"
   ===== END PSEUDOCODE ===== */
```

---

## 4. Reports

| Report | Type | Source | Audience |
|--------|------|--------|----------|
| GSTR-1 Summary (Sales) | Summary by HSN/SAC | Invoices | Finance |
| GSTR-2 Summary (Purchases) | Summary by HSN/SAC | Vendor_Bills | Finance |
| GST Reconciliation | Tabular (compare) | Vendor_Bills vs GSTR-2A | Finance |
| ITC Register | Tabular (filter: ITC_Eligibility) | Vendor_Bills | Finance |
| FX Gain/Loss Register | Tabular (filter: FX_Gain_Loss != 0) | Payments | Finance |
| Currency Exposure | Summary by Currency | Vendor_Bills + Invoices | Finance |
| Trial Balance by Period | Pivot by Period | Bills + Expenses + Invoices | Finance |
| GRNI Accrual | Tabular (unbilled GRN lines) | Goods_Receipts | Finance |
| Period Close Checklist | Status dashboard | Accounting_Periods | Finance |

---

## Verification Checklist

- [ ] Currency_Rates form created, rates can be entered and looked up
- [ ] Accounting_Periods form created, periods can be opened/closed
- [ ] Period-lock validation works: transaction in closed period is rejected with alert
- [ ] Tax Classification fields added to Bill_Line_Items and Invoice_Line_Items
- [ ] ITC Eligibility field added to Bill_Line_Items
- [ ] FX Rate auto-populates on Bills, Invoices, Payments when currency != Base
- [ ] Base Currency Amount calculates correctly
- [ ] FX Gain/Loss calculated correctly when Bill rate differs from Payment rate
- [ ] GST reports show correct grouping by HSN/SAC
- [ ] GRNI Accrual report shows unmatched GRN lines
