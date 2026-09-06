"""
Deterministic Financial Calculation Engine for GramVantage AI.

IMPORTANT:
This module contains 100% deterministic mathematical calculations.
No LLM/Gemini calls are used for financial structuring.

Rules & Parameters (National Micro-Enterprise Lending Framework):
1. Micro Finance Scheme:
   - Project Cost <= ₹1,40,000
   - Max Financing = 90%
   - Max Loan = ₹1,25,000
   - Interest Rate = 6.5% p.a.
   - Repayment Period = 3 years
   - Moratorium = 3 months
2. Term Loan Scheme:
   - Project Cost > ₹1,40,000 and <= ₹50,00,000
   - Max Financing = 90%
   - Max Loan = ₹45,00,000
   - Interest Rate = 8.0% p.a.
   - Repayment Period = 7 years
   - Moratorium = 6 months
3. Beyond Standard Scheme Coverage (> ₹50,00,000):
   - Scheme = "Commercial Lending / Non-Subsidized"
   - Fallback to configurable DEFAULT_MARKET_INTEREST_RATE (12.0%)
   - Clearly labeled: "Indicative market rate — not a bank offer."
"""

import math
from typing import Optional, Dict, Any, List, Union
from backend.models import FinancialInput, FinancialPlan

# Configurable default market interest rate for fallback/out-of-scheme scenarios
# Allows seamless integration of future live RBI / ULI (Unified Lending Interface) APIs
DEFAULT_MARKET_INTEREST_RATE = 12.0
DEFAULT_MARKET_TENURE_YEARS = 5
DEFAULT_MARKET_MORATORIUM_MONTHS = 3

# SIH26091 Scheme Constants
SIH_MICRO_MAX_COST = 140000.0
SIH_MICRO_MAX_LOAN = 125000.0
SIH_MICRO_RATE = 6.5
SIH_MICRO_TENURE_YEARS = 3
SIH_MICRO_MORATORIUM_MONTHS = 3

SIH_TERM_MAX_COST = 5000000.0
SIH_TERM_MAX_LOAN = 4500000.0
SIH_TERM_RATE = 8.0
SIH_TERM_TENURE_YEARS = 7
SIH_TERM_MORATORIUM_MONTHS = 6

FINANCING_RATIO_CAP = 0.90  # 90% maximum financing


def validate_financial_inputs(
    project_cost: float,
    own_contribution: Optional[float] = None,
    monthly_revenue: Optional[float] = None,
    monthly_expenses: Optional[float] = None,
    interest_rate: Optional[float] = None,
    tenure_years: Optional[int] = None,
    moratorium_months: Optional[int] = None
) -> List[str]:
    """
    Validates all inputs and returns a list of error strings if invalid.
    """
    errors = []

    if project_cost is None or project_cost <= 0:
        errors.append("Project cost must be greater than 0.")

    if own_contribution is not None:
        if own_contribution < 0:
            errors.append("Own contribution cannot be negative.")
        elif project_cost is not None and own_contribution > project_cost:
            errors.append("Own contribution cannot exceed total project cost.")

    if monthly_revenue is not None and monthly_revenue < 0:
        errors.append("Monthly revenue cannot be negative.")

    if monthly_expenses is not None and monthly_expenses < 0:
        errors.append("Monthly expenses cannot be negative.")

    if interest_rate is not None and interest_rate < 0:
        errors.append("Interest rate cannot be negative.")

    if tenure_years is not None and tenure_years <= 0:
        errors.append("Tenure years must be greater than 0.")

    if moratorium_months is not None and moratorium_months < 0:
        errors.append("Moratorium months cannot be negative.")

    if tenure_years is not None and moratorium_months is not None:
        if moratorium_months >= tenure_years * 12:
            errors.append("Moratorium period cannot be greater than or equal to total loan tenure.")

    return errors


def calculate_reducing_balance_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int
) -> float:
    """
    Standard reducing-balance EMI formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

    Where:
    P = Principal loan amount
    r = Monthly interest rate (annual_rate / 12 / 100)
    n = Number of monthly installments
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    if annual_interest_rate <= 0:
        return round(principal / tenure_months, 2)

    monthly_rate = (annual_interest_rate / 12.0) / 100.0
    factor = math.pow(1.0 + monthly_rate, tenure_months)
    emi = principal * monthly_rate * factor / (factor - 1.0)
    return round(emi, 2)


def calculate_financial_plan_raw(
    project_cost: float,
    own_contribution: Optional[float] = None,
    monthly_revenue: Optional[float] = None,
    monthly_expenses: Optional[float] = None,
    interest_rate: Optional[float] = None,
    tenure_years: Optional[int] = None,
    moratorium_months: Optional[int] = None
) -> Dict[str, Any]:
    """
    Core deterministic calculation engine returning a complete dictionary structure.
    Independent of any framework, LLM, or database.
    """
    # Validation
    errors = validate_financial_inputs(
        project_cost=project_cost,
        own_contribution=own_contribution,
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
        interest_rate=interest_rate,
        tenure_years=tenure_years,
        moratorium_months=moratorium_months
    )
    if errors:
        raise ValueError("; ".join(errors))

    warnings: List[str] = []
    is_sih_scheme = True
    rate_disclaimer = None

    # Determine Financial Tier
    if project_cost <= SIH_MICRO_MAX_COST:
        scheme = "Micro Finance Scheme"
        scheme_tier = "MICRO FINANCE SCHEME"
        applicable_max_loan = SIH_MICRO_MAX_LOAN
        default_rate = SIH_MICRO_RATE
        default_tenure_years = SIH_MICRO_TENURE_YEARS
        default_moratorium_months = SIH_MICRO_MORATORIUM_MONTHS
        tier_desc = (
            f"National Micro Finance Tier (Project cost up to ₹1,40,000; "
            f"max 90% up to ₹1,25,000 @ {SIH_MICRO_RATE}% p.a., "
            f"{SIH_MICRO_TENURE_YEARS}y tenure, {SIH_MICRO_MORATORIUM_MONTHS}m moratorium)"
        )
    elif project_cost <= SIH_TERM_MAX_COST:
        scheme = "Term Loan Scheme"
        scheme_tier = "TERM LOAN SCHEME"
        applicable_max_loan = SIH_TERM_MAX_LOAN
        default_rate = SIH_TERM_RATE
        default_tenure_years = SIH_TERM_TENURE_YEARS
        default_moratorium_months = SIH_TERM_MORATORIUM_MONTHS
        tier_desc = (
            f"Commercial Term Loan Tier (Project cost > ₹1,40,000 up to ₹50,00,000; "
            f"max 90% up to ₹45,00,000 @ {SIH_TERM_RATE}% p.a., "
            f"{SIH_TERM_TENURE_YEARS}y tenure, {SIH_TERM_MORATORIUM_MONTHS}m moratorium)"
        )
    else:
        # Project costs > ₹50,00,000
        scheme = "Commercial Lending / Non-Subsidized"
        scheme_tier = "NON-SCHEME MARKET RATE"
        applicable_max_loan = project_cost * FINANCING_RATIO_CAP
        default_rate = DEFAULT_MARKET_INTEREST_RATE
        default_tenure_years = DEFAULT_MARKET_TENURE_YEARS
        default_moratorium_months = DEFAULT_MARKET_MORATORIUM_MONTHS
        is_sih_scheme = False
        rate_disclaimer = "Indicative market rate — not a bank offer."
        tier_desc = (
            "Project cost exceeds ₹50 Lakh (Not covered by subsidized micro-enterprise financial tiers). "
            f"Calculations provided at indicative market rate ({DEFAULT_MARKET_INTEREST_RATE}% p.a.)."
        )
        warnings.append(
            "Project cost exceeds ₹50 Lakh maximum limit under standard micro-enterprise scheme rules. "
            f"Applied indicative market rate of {DEFAULT_MARKET_INTEREST_RATE}% p.a. "
            "(Indicative market rate — not a bank offer)."
        )

    # Applied rates, tenure and moratorium (custom overrides take precedence)
    applied_rate = float(interest_rate) if interest_rate is not None else default_rate
    applied_tenure_years = int(tenure_years) if tenure_years is not None else default_tenure_years
    applied_moratorium_months = int(moratorium_months) if moratorium_months is not None else default_moratorium_months

    # Rule 3: Eligible Loan and Own Contribution
    # eligible_loan = min(90% of project_cost, applicable maximum loan)
    eligible_loan = min(project_cost * FINANCING_RATIO_CAP, applicable_max_loan)
    required_own_contribution = project_cost - eligible_loan

    if own_contribution is not None:
        user_contrib = float(own_contribution)
        actual_loan_required = project_cost - user_contrib

        # Check if user contribution is below minimum required margin
        if user_contrib < required_own_contribution:
            deficit = round(required_own_contribution - user_contrib, 2)
            warnings.append(
                f"Additional own contribution required: minimum margin required is "
                f"{round(required_own_contribution, 2)} (deficit: {deficit})."
            )

        # actual_loan = min(actual_loan_required, eligible_loan)
        actual_loan = max(0.0, min(actual_loan_required, eligible_loan))
        effective_own_contribution = project_cost - actual_loan
    else:
        # User contribution not provided: assume eligible financing
        actual_loan = eligible_loan
        effective_own_contribution = required_own_contribution

    # Total tenure & active repayment months after moratorium
    total_tenure_months = applied_tenure_years * 12
    active_repayment_months = max(1, total_tenure_months - applied_moratorium_months)

    # Rule 4: EMI Calculation (standard reducing-balance after moratorium)
    # Estimated EMI after moratorium
    monthly_emi = calculate_reducing_balance_emi(
        principal=actual_loan,
        annual_interest_rate=applied_rate,
        tenure_months=active_repayment_months
    )
    total_repayment = round(monthly_emi * active_repayment_months, 2)
    total_interest = round(max(0.0, total_repayment - actual_loan), 2)

    # Rule 6: Business Profitability & Cash Flow
    # Revenue defaults (~28% of project cost monthly if unprovided)
    if monthly_revenue is not None:
        est_rev = float(monthly_revenue)
    else:
        est_rev = round(project_cost * 0.28, 2)

    # Operating expense defaults (~58% of revenue monthly if unprovided)
    if monthly_expenses is not None:
        est_exp = float(monthly_expenses)
    else:
        est_exp = round(est_rev * 0.58, 2)

    monthly_profit = round(est_rev - est_exp, 2)
    annual_profit = round(monthly_profit * 12.0, 2)

    # Cash flow after EMI
    monthly_cash_flow_after_emi = round(monthly_profit - monthly_emi, 2)

    # Break-even calculation
    # break_even_months = initial_own_contribution / monthly_cash_flow_after_emi
    if monthly_cash_flow_after_emi > 0 and effective_own_contribution > 0:
        break_even_months: Union[float, str] = round(effective_own_contribution / monthly_cash_flow_after_emi, 1)
    elif monthly_cash_flow_after_emi > 0:
        break_even_months = 0.0
    else:
        break_even_months = "Break-even cannot be estimated because monthly cash flow is non-positive."
        warnings.append("Break-even cannot be estimated because monthly cash flow is non-positive.")

    # Percentages
    loan_percentage = round((actual_loan / project_cost) * 100, 1) if project_cost > 0 else 0.0
    own_contrib_percentage = round((effective_own_contribution / project_cost) * 100, 1) if project_cost > 0 else 0.0

    return {
        "project_cost": round(project_cost, 2),
        "own_contribution": round(effective_own_contribution, 2),
        "own_contribution_percentage": own_contrib_percentage,
        "loan_required": round(project_cost - (own_contribution if own_contribution is not None else effective_own_contribution), 2),
        "eligible_loan": round(eligible_loan, 2),
        "actual_loan": round(actual_loan, 2),
        "loan_percentage": loan_percentage,
        "scheme": scheme,
        "scheme_tier": scheme_tier,
        "tier_description": tier_desc,
        "interest_rate": round(applied_rate, 2),
        "tenure_years": applied_tenure_years,
        "tenure_months": total_tenure_months,
        "active_repayment_months": active_repayment_months,
        "moratorium_months": applied_moratorium_months,
        "emi_label": "Estimated EMI after moratorium",
        "monthly_emi": monthly_emi,
        "total_interest": total_interest,
        "total_repayment": total_repayment,
        "monthly_revenue": round(est_rev, 2),
        "monthly_expenses": round(est_exp, 2),
        "monthly_operating_expenses": round(est_exp, 2),
        "monthly_profit": monthly_profit,
        "annual_profit": annual_profit,
        "monthly_cash_flow_after_emi": monthly_cash_flow_after_emi,
        "break_even_months": break_even_months,
        "is_sih_scheme": is_sih_scheme,
        "rate_disclaimer": rate_disclaimer,
        "warnings": warnings,
        "disclaimer": (
            "Preliminary eligibility estimate adhering to micro-enterprise credit guidelines. "
            "Indicative structuring only — not a formal credit sanction. "
            "Final credit sanction and interest concessions subject to bank and channelizing agency appraisal."
        )
    }


def calculate_financial_plan(inputs: FinancialInput) -> FinancialPlan:
    """
    FastAPI / Pydantic compatible wrapper for calculate_financial_plan_raw.
    Accepts FinancialInput and returns FinancialPlan.
    """
    res = calculate_financial_plan_raw(
        project_cost=inputs.project_cost,
        own_contribution=inputs.user_contribution,
        monthly_revenue=inputs.estimated_monthly_revenue,
        monthly_expenses=inputs.estimated_monthly_operating_expenses,
        interest_rate=inputs.custom_interest_rate,
        tenure_years=inputs.custom_tenure_years,
        moratorium_months=inputs.custom_moratorium_months
    )

    # In FinancialPlan model, break_even_months is typed as float.
    # Convert string message to 999.0 if non-positive cash flow for backward compatibility.
    b_even = res["break_even_months"]
    if isinstance(b_even, str):
        b_even_val = 999.0
    else:
        b_even_val = float(b_even)

    # Map monthly_profit in FinancialPlan to cash flow after EMI (net monthly profit)
    return FinancialPlan(
        project_cost=res["project_cost"],
        scheme_tier=res["scheme_tier"],
        tier_description=res["tier_description"],
        own_contribution=res["own_contribution"],
        own_contribution_percentage=res["own_contribution_percentage"],
        required_loan=res["actual_loan"],
        loan_percentage=res["loan_percentage"],
        interest_rate=res["interest_rate"],
        tenure_years=res["tenure_years"],
        tenure_months=res["tenure_months"],
        moratorium_months=res["moratorium_months"],
        monthly_emi=res["monthly_emi"],
        total_repayment=res["total_repayment"],
        total_interest_payable=res["total_interest"],
        monthly_revenue=res["monthly_revenue"],
        monthly_operating_expenses=res["monthly_operating_expenses"],
        monthly_profit=res["monthly_cash_flow_after_emi"],
        annual_profit=round(res["monthly_cash_flow_after_emi"] * 12.0, 2),
        break_even_months=b_even_val,
        disclaimer=res["disclaimer"]
    )


# Helper function for currency formatting (separate from numeric calculation layer)
def format_currency_inr(amount: Union[float, int]) -> str:
    """
    Format numeric value into Indian Rupee currency string.
    Example: 123456.78 -> '₹1,23,456.78'
    """
    if amount is None:
        return "₹0.00"
    is_neg = amount < 0
    amount = abs(amount)
    parts = f"{amount:.2f}".split(".")
    int_part = parts[0]
    dec_part = parts[1]

    if len(int_part) > 3:
        last3 = int_part[-3:]
        rest = int_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_int = ",".join(groups) + "," + last3
    else:
        formatted_int = int_part

    sign = "-" if is_neg else ""
    return f"{sign}₹{formatted_int}.{dec_part}"
