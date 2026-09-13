# STEP 5 Walkthrough: Financial & Funding Structuring Engine

## Overview
We have upgraded the financial planning system into a deterministic **Financial & Funding Structuring Engine** for Aarambh Saathi / GramVantage AI. The engine evaluates:
1. **Total Project Cost** with clear decomposition (Equipment, Infrastructure, Initial Working Capital).
2. **Entrepreneur Own Contribution vs Funding Requirement** ($\max(0, \text{Total Cost} - \text{Own Contribution})$).
3. **Starter vs Standard Setup Financing** alignment with Step 4 setup plans.
4. **Monthly Financial Model** (Revenue, Operating Expenses, Operating Surplus, Profit Margin) with safe division guards.
5. **Deterministic Break-Even Period** ($\text{Own Contribution} / \text{Operating Surplus}$).
6. **Illustrative Loan Calculator** utilizing standard reducing-balance EMI formulation.
7. **Repayment Affordability & EMI Coverage Ratio** ($\text{Surplus} / \text{Monthly EMI}$) with human-friendly risk interpretations.
8. **Three Realistic Funding Scenarios** (Scenario A: Minimal Borrowing, Scenario B: Balanced Micro-Credit, Scenario C: Growth Scale).
9. **Deterministic Financial Health Classification** (`HEALTHY`, `CAUTION`, `HIGH RISK`, `INSUFFICIENT DATA`).
10. **Low-Capital Guidance Path** for capital-constrained rural applicants.
11. **Data Quality & Transparency** demarcation (Business Knowledge Base, User Provided, Calculated, Estimated).

---

## 1. Core Mathematical Formulations

### A. Total Project Cost & Funding Requirement
$$\text{Total Project Cost} = \text{Equipment Cost} + \text{Infrastructure Cost} + \text{Initial Working Capital} + \text{Other Setup Costs}$$
$$\text{Funding Requirement} = \max(0, \text{Total Project Cost} - \text{Entrepreneur Contribution})$$

### B. Monthly Surplus & Profit Margin
$$\text{Monthly Operating Surplus} = \text{Estimated Monthly Revenue} - \text{Estimated Monthly Operating Expense}$$
$$\text{Profit Margin (\%)} = \left(\frac{\text{Monthly Operating Surplus}}{\text{Estimated Monthly Revenue}}\right) \times 100 \quad (\text{if Revenue} > 0)$$

### C. Reducing-Balance Loan EMI
$$\text{EMI} = \frac{P \times r \times (1+r)^n}{(1+r)^n - 1}$$
Where:
- $P$ = Principal Loan Amount
- $r$ = Monthly Interest Rate ($\text{Annual Rate} / 12 / 100$)
- $n$ = Active Repayment Months ($\text{Total Months} - \text{Moratorium Months}$)

### D. Repayment Buffer (EMI Coverage Ratio)
$$\text{EMI Coverage Ratio} = \frac{\text{Monthly Operating Surplus}}{\text{Monthly EMI}}$$

- $\ge 2.0\text{x}$: `Strong repayment buffer` (Low default risk)
- $1.5\text{x} - 1.99\text{x}$: `Reasonable buffer` (Comfortable operating safety margin)
- $1.0\text{x} - 1.49\text{x}$: `Tight repayment margin` (Requires disciplined overhead control)
- $< 1.0\text{x}$: `High repayment risk` (Financial stress hazard)

---

## 2. UI Upgrades ([FinancialSummary.jsx](file:///c:/Users/vighn/Desktop/Ruraltech/frontend/src/components/FinancialSummary.jsx))

1. **Header & Health Badge**: Shows Scheme Tier (Micro Finance $\le$ ₹1.40L vs Term Loan $>$ ₹1.40L) and Financial Health Status (`HEALTHY`, `CAUTION`, `HIGH RISK`, `INSUFFICIENT DATA`).
2. **Top 3 Figures**: Total Project Cost, Your Own Contribution (% Equity), and Funding Gap / Loan (% Debt).
3. **Monthly Financial Model**: 4-card grid showing Monthly Revenue, Operating Expenses, Operating Surplus, and Profit Margin with source tags.
4. **Loan Calculator & Repayment Buffer**: Illustrative loan amount, interest rate, tenure, and monthly EMI with a dynamic EMI Coverage badge.
5. **Interactive Sliders**: Real-time slider controls for adjusting Project Cost and Own Contribution.
6. **Interactive Expandable Sections**:
   - *Cost Decomposition*: Detailed split of Equipment, Infrastructure, and Working Capital.
   - *3 Funding Scenarios*: Minimal Borrowing vs Balanced vs Maximum Permissible Financing.
   - *Financial Risks*: Contextual rural cashflow and seasonal risks.
7. **Low-Capital Guidance Banner**: Suggests starter scale and micro-loans for capital-constrained users.

---

## 3. Verification Results

### Automated Test Suite Runs:
1. `python test_finance_engine.py` -> **8/8 Tests Passed (100% OK)**
2. `python test_business_setup.py` -> **4/4 Tests Passed (100% OK)**
3. `python test_feasibility_engine.py` -> **4/4 Tests Passed (100% OK)**
4. `python backend/test_backend.py` -> **5/5 Tests Passed (100% OK)**
5. `python test_complete_step1.py` -> **6/6 Tests Passed (100% OK)**
6. `python test_recommendation_engine.py` -> **9/9 Tests Passed (100% OK)**
7. `npm run build` (Frontend) -> **Built in 5.61s (0 errors)**

### Specific Test Scenarios Validated:
- **TEST 1**: Project Cost ₹1,50,000, Own Contribution ₹1,00,000 $\rightarrow$ Funding Requirement: ₹50,000.
- **TEST 2**: Project Cost ₹2,50,000, Own Contribution ₹50,000 $\rightarrow$ Funding Requirement: ₹2,00,000.
- **TEST 3**: ₹1,00,000 @ 8% for 3 years $\rightarrow$ EMI = ₹3,133.64 (exact match to reducing-balance formula).
- **TEST 4**: Strong coverage ($\ge 2.0$x) vs High Risk ($< 1.0$x) classifications validated.
- **TEST 5**: Revenue ₹80,000, Expenses ₹50,000 $\rightarrow$ Surplus ₹30,000, Margin 37.5%.
- **TEST 6**: Low-capital user receives structured phased path without automatic rejection.
- **TEST 7**: Zero revenue safely returns 0% margin and 999.0 break-even without division error.
- **TEST 8**: Insufficient data correctly produces `INSUFFICIENT DATA` status.
