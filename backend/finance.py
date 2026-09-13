"""
Deterministic Financial & Funding Structuring Engine for Aarambh Saathi / GramVantage AI (Step 5).

Provides 100% deterministic mathematical calculations for rural micro-entrepreneurs:
1. Total Project Cost decomposition (Equipment, Infrastructure, Working Capital, Other)
2. Entrepreneur Own Contribution vs Funding Requirement
3. Starter vs Standard Financing comparison
4. Monthly Financial Model (Revenue, Expenses, Surplus, Profit Margin)
5. Deterministic Break-Even Period calculation
6. Illustrative Loan Calculator (Reducing-balance EMI, Total Interest, Total Repayment)
7. Repayment Affordability & EMI Coverage Ratio (Strong buffer, Reasonable, Tight, High risk)
8. Three Realistic Funding Scenarios (Self-Funded / Minimal, Balanced, Growth Scale)
9. Deterministic Financial Health Classification (HEALTHY, CAUTION, HIGH RISK, INSUFFICIENT DATA)
10. Low-Capital guidance path for capital-constrained applicants
11. Explicit data-source transparency labels without fabricating numbers
"""

import math
from typing import Optional, Dict, Any, List, Union
from backend.models import FinancialInput, FinancialPlan, UserProfile
from backend.database import get_business_by_id, load_businesses_data

# Configurable defaults
DEFAULT_MARKET_INTEREST_RATE = 12.0
DEFAULT_MICRO_INTEREST_RATE = 6.5
DEFAULT_TERM_INTEREST_RATE = 8.0

SIH_MICRO_MAX_COST = 140000.0
SIH_MICRO_MAX_LOAN = 125000.0
SIH_TERM_MAX_COST = 5000000.0
SIH_TERM_MAX_LOAN = 4500000.0
FINANCING_RATIO_CAP = 0.90  # 90% maximum financing under MSME credit norms


def validate_financial_inputs(
    project_cost: Optional[float],
    own_contribution: Optional[float] = None,
    monthly_revenue: Optional[float] = None,
    monthly_expenses: Optional[float] = None,
    interest_rate: Optional[float] = None,
    tenure_years: Optional[int] = None,
    moratorium_months: Optional[int] = None
) -> List[str]:
    """Validates inputs and returns error list if any value is fundamentally invalid."""
    errors = []
    if project_cost is not None and project_cost <= 0:
        errors.append("Project cost must be greater than 0.")
    if own_contribution is not None and own_contribution < 0:
        errors.append("Own contribution cannot be negative.")
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
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    if annual_interest_rate <= 0:
        return round(principal / tenure_months, 2)

    monthly_rate = (annual_interest_rate / 12.0) / 100.0
    try:
        factor = math.pow(1.0 + monthly_rate, tenure_months)
        if factor == 1.0 or (factor - 1.0) == 0:
            return round(principal / tenure_months, 2)
        emi = principal * monthly_rate * factor / (factor - 1.0)
        return round(emi, 2)
    except OverflowError:
        return 0.0


def calculate_financial_plan_raw(
    project_cost: Optional[float] = None,
    own_contribution: Optional[float] = None,
    monthly_revenue: Optional[float] = None,
    monthly_expenses: Optional[float] = None,
    interest_rate: Optional[float] = None,
    tenure_years: Optional[int] = None,
    moratorium_months: Optional[int] = None,
    business_id: Optional[str] = None,
    business_name: Optional[str] = None,
    setup_plan: Optional[Dict[str, Any]] = None,
    user_profile: Optional[UserProfile] = None,
    setup_mode: Optional[str] = "starter"
) -> Dict[str, Any]:
    """
    Complete deterministic Financial & Funding Structuring calculation engine.
    """
    # 1. Validation
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

    # 2. Resolve Business Knowledge Base Data
    business = None
    if business_id:
        business = get_business_by_id(business_id)
    if not business and business_name:
        all_b = load_businesses_data()
        business = next((b for b in all_b if b.get("business_name", "").lower() == business_name.lower()), None)

    b_name = business.get("business_name") if business else (business_name or "Rural Micro Enterprise")

    # 3. Resolve Project Cost & Setup Decomposition
    equip_cost = 0.0
    infra_cost = 0.0
    working_cap = 0.0
    other_cost = 0.0
    total_cost = 0.0

    if setup_plan:
        mode_data = setup_plan.get("starter_setup" if setup_mode == "starter" else "standard_setup", {})
        equip_cost = float(mode_data.get("equipment_cost", 0.0))
        infra_cost = float(mode_data.get("infrastructure_cost", 0.0))
        working_cap = float(mode_data.get("working_capital", 0.0))
        total_cost = float(mode_data.get("total_cost", equip_cost + infra_cost + working_cap))
    elif business:
        min_inv = float(business.get("minimum_investment", 80000.0))
        rec_inv = float(business.get("recommended_investment", 140000.0))
        base_inv = min_inv if setup_mode == "starter" else rec_inv
        
        # Deterministic standard MSME proportions
        equip_cost = round(base_inv * 0.50, 2)
        infra_cost = round(base_inv * 0.25, 2)
        working_cap = round(base_inv * 0.25, 2)
        total_cost = base_inv
    elif project_cost is not None and project_cost > 0:
        total_cost = float(project_cost)
        equip_cost = round(total_cost * 0.50, 2)
        infra_cost = round(total_cost * 0.25, 2)
        working_cap = round(total_cost * 0.25, 2)
    else:
        total_cost = 100000.0
        equip_cost = 50000.0
        infra_cost = 25000.0
        working_cap = 25000.0

    # Ensure total_cost override if explicitly provided
    if project_cost is not None and project_cost > 0:
        total_cost = float(project_cost)
        if equip_cost + infra_cost + working_cap != total_cost:
            equip_cost = round(total_cost * 0.50, 2)
            infra_cost = round(total_cost * 0.25, 2)
            working_cap = round(total_cost - (equip_cost + infra_cost), 2)

    # 4. Entrepreneur Own Contribution & Funding Requirement
    user_inv = 0.0
    if own_contribution is not None:
        user_inv = float(own_contribution)
    elif user_profile:
        user_inv = float(user_profile.available_investment or user_profile.capital or 0.0)

    # Own contribution actually allocated to project
    effective_own_contribution = round(min(user_inv, total_cost), 2) if user_inv > 0 else 0.0
    funding_requirement = round(max(0.0, total_cost - user_inv), 2)

    # 5. Financial Scheme Tier Determination
    warnings = []
    is_sih_scheme = True
    rate_disclaimer = None

    if total_cost <= SIH_MICRO_MAX_COST:
        scheme_tier = "MICRO FINANCE SCHEME"
        applicable_max_loan = SIH_MICRO_MAX_LOAN
        default_rate = DEFAULT_MICRO_INTEREST_RATE
        default_tenure_years = 3
        default_moratorium_months = 3
        tier_desc = f"National Micro Finance Tier (Cost up to ₹1.40L; max 90% up to ₹1.25L @ {DEFAULT_MICRO_INTEREST_RATE}% p.a.)"
    elif total_cost <= SIH_TERM_MAX_COST:
        scheme_tier = "TERM LOAN SCHEME"
        applicable_max_loan = SIH_TERM_MAX_LOAN
        default_rate = DEFAULT_TERM_INTEREST_RATE
        default_tenure_years = 7
        default_moratorium_months = 6
        tier_desc = f"Commercial Term Loan Tier (Cost > ₹1.40L to ₹50L; max 90% up to ₹45L @ {DEFAULT_TERM_INTEREST_RATE}% p.a.)"
    else:
        scheme_tier = "NON-SCHEME MARKET RATE"
        applicable_max_loan = total_cost * FINANCING_RATIO_CAP
        default_rate = DEFAULT_MARKET_INTEREST_RATE
        default_tenure_years = 5
        default_moratorium_months = 3
        is_sih_scheme = False
        rate_disclaimer = "Indicative market rate — not a bank offer."
        tier_desc = f"Project cost exceeds ₹50 Lakh. Indicative commercial rate ({DEFAULT_MARKET_INTEREST_RATE}% p.a.) applied."
        warnings.append("Project cost exceeds ₹50 Lakh maximum limit under standard micro-enterprise scheme rules.")

    applied_rate = float(interest_rate) if interest_rate is not None else default_rate
    applied_tenure_years = int(tenure_years) if tenure_years is not None else default_tenure_years
    applied_moratorium_months = int(moratorium_months) if moratorium_months is not None else default_moratorium_months

    # Max eligible financing = min(90% of cost, applicable max loan cap)
    eligible_loan = round(min(total_cost * FINANCING_RATIO_CAP, applicable_max_loan), 2)
    required_min_margin = round(total_cost - eligible_loan, 2)

    # Loan required to bridge user gap
    if user_inv > 0:
        actual_loan = round(min(funding_requirement, eligible_loan), 2)
        if user_inv < required_min_margin:
            deficit = round(required_min_margin - user_inv, 2)
            warnings.append(f"Additional own contribution required: minimum 10% margin required is ₹{required_min_margin:,.0f} (deficit: ₹{deficit:,.0f}).")
    else:
        actual_loan = eligible_loan
        effective_own_contribution = required_min_margin

    # 6. Loan Calculator (Reducing Balance EMI)
    total_tenure_months = applied_tenure_years * 12
    active_repayment_months = max(1, total_tenure_months - applied_moratorium_months)

    monthly_emi = calculate_reducing_balance_emi(
        principal=actual_loan,
        annual_interest_rate=applied_rate,
        tenure_months=active_repayment_months
    )
    total_repayment = round(monthly_emi * active_repayment_months, 2)
    total_interest = round(max(0.0, total_repayment - actual_loan), 2)

    # 7. Monthly Financial Model
    rev_source = "Estimated from sector baseline"
    if monthly_revenue is not None:
        est_rev = float(monthly_revenue)
        rev_source = "User Provided"
    elif business and "revenue_factors" in business:
        est_rev = float(business["revenue_factors"].get("estimated_monthly_revenue_per_unit", total_cost * 0.28))
        rev_source = "Business Knowledge Base"
    else:
        est_rev = round(total_cost * 0.28, 2)

    exp_source = "Estimated from sector baseline"
    if monthly_expenses is not None:
        est_exp = float(monthly_expenses)
        exp_source = "User Provided"
    elif business and "revenue_factors" in business:
        margin_pct = float(business["revenue_factors"].get("margin_percentage", 35.0))
        est_exp = round(est_rev * (1.0 - (margin_pct / 100.0)), 2)
        exp_source = "Business Knowledge Base (Margin Benchmark)"
    else:
        est_exp = round(est_rev * 0.58, 2)

    monthly_surplus = round(est_rev - est_exp, 2)
    annual_profit = round(monthly_surplus * 12.0, 2)

    # Profit Margin calculation with safe division guard
    if est_rev > 0:
        profit_margin = round((monthly_surplus / est_rev) * 100.0, 1)
    else:
        profit_margin = 0.0

    # Expense breakdown
    expense_breakdown = {
        "raw_materials": round(est_exp * 0.52, 2),
        "electricity_and_utilities": round(est_exp * 0.14, 2),
        "packaging_and_transport": round(est_exp * 0.14, 2),
        "contingency_and_maintenance": round(est_exp * 0.20, 2)
    }

    # Cash flow after EMI
    monthly_cash_flow_after_emi = round(monthly_surplus - monthly_emi, 2)

    # 8. Deterministic Break-Even Period
    if monthly_surplus > 0 and effective_own_contribution > 0:
        break_even_months_val = round(effective_own_contribution / monthly_surplus, 1)
        break_even_label = f"~ {break_even_months_val} Months"
        break_even_source = "Initial Own Contribution / Monthly Operating Surplus"
    elif monthly_surplus > 0:
        break_even_months_val = 0.0
        break_even_label = "Immediate (0 Months)"
        break_even_source = "Self-Funded / Immediate Operational Break-Even"
    else:
        break_even_months_val = 999.0
        break_even_label = "Break-even estimate unavailable (non-positive surplus)"
        break_even_source = "Operating Cash Flow Model"
        warnings.append("Break-even cannot be estimated because monthly operating cash flow is non-positive.")

    # 9. Repayment Affordability & EMI Coverage Ratio
    if monthly_emi > 0 and monthly_surplus > 0:
        emi_coverage_ratio = round(monthly_surplus / monthly_emi, 2)
        if emi_coverage_ratio >= 2.0:
            coverage_status = "Strong repayment buffer"
            coverage_interpretation = f"Monthly operating surplus (₹{monthly_surplus:,.0f}) covers EMI (₹{monthly_emi:,.0f}) by {emi_coverage_ratio}x. Low default risk."
        elif emi_coverage_ratio >= 1.5:
            coverage_status = "Reasonable buffer"
            coverage_interpretation = f"Operating surplus covers EMI by {emi_coverage_ratio}x with comfortable working capital buffer."
        elif emi_coverage_ratio >= 1.0:
            coverage_status = "Tight repayment margin"
            coverage_interpretation = f"Operating surplus covers EMI by {emi_coverage_ratio}x. Keep tight control on monthly overheads."
        else:
            coverage_status = "High repayment risk"
            coverage_interpretation = f"Monthly EMI exceeds or nearly equals surplus. High financial stress risk."
    elif monthly_emi == 0:
        emi_coverage_ratio = 99.0
        coverage_status = "Fully Self-Funded / No EMI"
        coverage_interpretation = "No loan required. 100% of operating surplus retained as net profit."
    else:
        emi_coverage_ratio = 0.0
        coverage_status = "Unable to assess repayment capacity"
        coverage_interpretation = "Operating surplus is non-positive."

    # 10. Financial Health Classification
    if total_cost <= 0 or est_rev <= 0:
        financial_health = "INSUFFICIENT DATA"
    elif monthly_surplus <= 0 or emi_coverage_ratio < 1.0:
        financial_health = "HIGH RISK"
    elif emi_coverage_ratio < 1.5 or profit_margin < 15.0 or (funding_requirement > 0 and user_inv < total_cost * 0.10):
        financial_health = "CAUTION"
    else:
        financial_health = "HEALTHY"

    # 11. Three Funding Scenarios
    # Scenario A: Self-Funded / Minimal Borrowing
    scen_a_loan = round(min(actual_loan, total_cost * 0.40), 2) if funding_requirement > 0 else 0.0
    scen_a_emi = calculate_reducing_balance_emi(scen_a_loan, applied_rate, active_repayment_months)
    scen_a = {
        "scenario_name": "Scenario A: Minimal Borrowing / Lean Setup",
        "own_contribution": round(total_cost - scen_a_loan, 2),
        "loan_amount": scen_a_loan,
        "monthly_emi": scen_a_emi,
        "emi_coverage": round(monthly_surplus / scen_a_emi, 2) if scen_a_emi > 0 else 99.0,
        "description": "Maximizes own capital to keep monthly loan payment as low as possible."
    }

    # Scenario B: Balanced Funding
    scen_b_loan = round(min(actual_loan, total_cost * 0.75), 2)
    scen_b_emi = calculate_reducing_balance_emi(scen_b_loan, applied_rate, active_repayment_months)
    scen_b = {
        "scenario_name": "Scenario B: Balanced Micro-Credit",
        "own_contribution": round(total_cost - scen_b_loan, 2),
        "loan_amount": scen_b_loan,
        "monthly_emi": scen_b_emi,
        "emi_coverage": round(monthly_surplus / scen_b_emi, 2) if scen_b_emi > 0 else 99.0,
        "description": "Standard 75% loan structuring preserving a healthy cash liquidity cushion."
    }

    # Scenario C: Standard / Growth Scale
    scen_c_loan = eligible_loan
    scen_c_emi = calculate_reducing_balance_emi(scen_c_loan, applied_rate, active_repayment_months)
    scen_c_cov = round(monthly_surplus / scen_c_emi, 2) if scen_c_emi > 0 else 99.0
    scen_c = {
        "scenario_name": "Scenario C: Maximum Permissible Financing",
        "own_contribution": round(total_cost - scen_c_loan, 2),
        "loan_amount": scen_c_loan,
        "monthly_emi": scen_c_emi,
        "emi_coverage": scen_c_cov,
        "description": f"90% loan financing tier. {'High repayment risk — requires disciplined collections.' if scen_c_cov < 1.3 else 'Supports complete equipment procurement.'}"
    }

    scenarios = [scen_a, scen_b, scen_c]

    # 12. Low-Capital Path
    is_low_capital = user_inv > 0 and user_inv < (total_cost * 0.50)
    low_cap_path = None
    if is_low_capital:
        starter_target = round(total_cost * 0.65, 2)
        low_cap_path = {
            "is_low_capital": True,
            "message": f"Your current capital of ₹{user_inv:,.0f} is below standard setup (₹{total_cost:,.0f}).",
            "starter_recommendation": f"Start with a micro-scale setup (₹{starter_target:,.0f}) to reduce initial funding gap to ₹{max(0, starter_target - user_inv):,.0f}.",
            "recommended_next_steps": [
                "Procure only Phase-1 core essential machinery",
                "Utilize home / existing family land to avoid initial lease expenses",
                "Apply for PMMY Shishu micro-credit (up to ₹50,000, 0% collateral)"
            ]
        }

    # 13. Financial Risks
    risks_list = [
        f"Working capital variance: Keep ₹{working_cap:,.0f} buffer for initial 60-day customer credit cycles.",
        "Equipment maintenance: Account for routine quarterly servicing costs.",
        "Revenue seasonality: Rural cashflow may fluctuate during monsoon or post-harvest cycles."
    ]
    if emi_coverage_ratio < 1.5 and actual_loan > 0:
        risks_list.insert(0, f"Tight EMI buffer ({emi_coverage_ratio}x): Prioritize prompt monthly loan repayments to maintain credit score.")

    # 14. Data Quality & Transparency
    data_quality = {
        "verified": [
            "Deterministic reducing-balance EMI mathematical formula",
            "National Micro-Enterprise Credit Lending Tier rules"
        ],
        "estimated": [
            f"Monthly revenue (Source: {rev_source})",
            f"Monthly operating expenses (Source: {exp_source})",
            "Equipment & setup cost decomposition (MSME benchmark model)"
        ],
        "missing": [] if user_inv > 0 else ["User available capital (assumed minimum margin)"]
    }

    loan_pct = round((actual_loan / total_cost) * 100, 1) if total_cost > 0 else 0.0
    own_pct = round((effective_own_contribution / total_cost) * 100, 1) if total_cost > 0 else 0.0

    return {
        "business_name": b_name,
        "project_cost": round(total_cost, 2),
        "own_contribution": round(effective_own_contribution, 2),
        "own_contribution_percentage": own_pct,
        "required_loan": actual_loan,
        "loan_required": actual_loan,
        "funding_requirement": funding_requirement,
        "eligible_loan": eligible_loan,
        "actual_loan": actual_loan,
        "loan_percentage": loan_pct,
        "scheme": scheme_tier,
        "scheme_tier": scheme_tier,
        "tier_description": tier_desc,
        "interest_rate": round(applied_rate, 2),
        "tenure_years": applied_tenure_years,
        "tenure_months": total_tenure_months,
        "active_repayment_months": active_repayment_months,
        "moratorium_months": applied_moratorium_months,
        "monthly_emi": monthly_emi,
        "total_interest": total_interest,
        "total_interest_payable": total_interest,
        "total_repayment": total_repayment,
        "monthly_revenue": est_rev,
        "monthly_expenses": est_exp,
        "monthly_operating_expenses": est_exp,
        "monthly_profit": monthly_cash_flow_after_emi,
        "annual_profit": round(monthly_cash_flow_after_emi * 12.0, 2),
        "break_even_months": break_even_months_val,
        "is_sih_scheme": is_sih_scheme,
        "rate_disclaimer": rate_disclaimer,
        "warnings": warnings,
        "cost_breakdown": {
            "equipment": equip_cost,
            "infrastructure": infra_cost,
            "working_capital": working_cap,
            "other": other_cost,
            "total": total_cost
        },
        "monthly_financials": {
            "revenue": est_rev,
            "operating_expense": est_exp,
            "surplus": monthly_surplus,
            "net_surplus_after_emi": monthly_cash_flow_after_emi,
            "profit_margin": profit_margin,
            "expense_breakdown": expense_breakdown,
            "revenue_source": rev_source,
            "expense_source": exp_source
        },
        "break_even": {
            "months": break_even_months_val,
            "label": break_even_label,
            "source": break_even_source
        },
        "financing": {
            "loan_amount": actual_loan,
            "interest_rate": applied_rate,
            "tenure_months": active_repayment_months,
            "tenure_years": applied_tenure_years,
            "moratorium_months": applied_moratorium_months,
            "monthly_emi": monthly_emi,
            "total_repayment": total_repayment,
            "total_interest": total_interest
        },
        "repayment_capacity": {
            "emi_coverage_ratio": emi_coverage_ratio,
            "status": coverage_status,
            "interpretation": coverage_interpretation
        },
        "financial_health": financial_health,
        "scenarios": scenarios,
        "risks": risks_list,
        "low_capital_path": low_cap_path,
        "data_quality": data_quality,
        "disclaimer": (
            "Illustrative financing estimate adhering to micro-enterprise lending guidelines. "
            "Indicative structuring only — not a formal credit sanction or guaranteed income offer. "
            "Final credit appraisal subject to bank verification."
        )
    }


def calculate_financial_plan(inputs: FinancialInput) -> FinancialPlan:
    """
    FastAPI / Pydantic compatible endpoint wrapper.
    """
    user_prof = inputs.user_profile or inputs.profile
    res = calculate_financial_plan_raw(
        project_cost=inputs.project_cost,
        own_contribution=inputs.user_contribution,
        monthly_revenue=inputs.estimated_monthly_revenue,
        monthly_expenses=inputs.estimated_monthly_operating_expenses,
        interest_rate=inputs.custom_interest_rate,
        tenure_years=inputs.custom_tenure_years,
        moratorium_months=inputs.custom_moratorium_months,
        business_id=inputs.business_id,
        business_name=inputs.business_name,
        setup_plan=inputs.setup_plan,
        user_profile=user_prof,
        setup_mode=inputs.setup_mode or "starter"
    )

    b_even_val = float(res["break_even_months"])

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
        monthly_profit=res["monthly_profit"],
        annual_profit=res["annual_profit"],
        break_even_months=b_even_val,
        disclaimer=res["disclaimer"],
        business_name=res["business_name"],
        cost_breakdown=res["cost_breakdown"],
        funding_requirement=res["funding_requirement"],
        monthly_financials=res["monthly_financials"],
        break_even=res["break_even"],
        financing=res["financing"],
        repayment_capacity=res["repayment_capacity"],
        financial_health=res["financial_health"],
        scenarios=res["scenarios"],
        risks=res["risks"],
        low_capital_path=res["low_capital_path"],
        data_quality=res["data_quality"]
    )


def format_currency_inr(amount: Union[float, int]) -> str:
    """Format numeric value into Indian Rupee currency string."""
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
