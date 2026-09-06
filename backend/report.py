import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from backend.models import UserProfile, BusinessReport, ReportRequest, FinancialInput
from backend.recommendation import get_recommendations, score_business
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.finance import calculate_financial_plan
from backend.schemes import match_government_schemes
from backend.supplier import get_required_machines
from backend.database import get_business_by_id, save_report

def generate_business_report(request: ReportRequest) -> BusinessReport:
    profile = request.profile
    report_id = f"GV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # 1. Select Business
    if request.selected_business_id:
        b_data = get_business_by_id(request.selected_business_id)
        if b_data:
            rec_business = score_business(b_data, profile)
        else:
            recs = get_recommendations(profile, top_n=1)
            rec_business = recs.recommendations[0]
    else:
        recs = get_recommendations(profile, top_n=1)
        rec_business = recs.recommendations[0]

    b_id = rec_business.business_id
    project_cost = request.custom_project_cost or rec_business.required_investment

    # 2. Local Feasibility
    feasibility = evaluate_hyper_local_feasibility(b_id, profile)

    # 3. Financial Plan
    fin_input = FinancialInput(
        project_cost=project_cost,
        user_contribution=profile.capital
    )
    financial_plan = calculate_financial_plan(fin_input)

    # 4. Relevant Schemes
    schemes = match_government_schemes(
        profile=profile,
        business_id=b_id,
        business_category=rec_business.category,
        project_cost=project_cost
    )

    # 5. Explainable Reasons
    explainable_reasons = [
        f"Skill Alignment: Score of {rec_business.breakdown.skill_match_score}/25 based on your experience with {profile.experience or 'allied trade'}.",
        f"Capital Viability: Available capital ₹{profile.capital or 0:,.0f} qualifies for 90% loan under {financial_plan.scheme_tier}.",
        f"Resource Readiness: Essential infrastructure verified ({', '.join(profile.resources[:3]) if profile.resources else 'basic rural amenities'}).",
        f"Local Market: Assessed feasibility score of {feasibility.feasibility_score}/100 with {feasibility.market_opportunity}.",
        f"Risk Control: Manageable risk profile with break-even projected within {financial_plan.break_even_months} months."
    ]

    # 6. 90-Day Action Plan
    action_plan = {
        "Phase 1 (Days 1 to 30) — Regulatory Setup & Financial Sanction": [
            "Finalize detailed project report (DPR) using GramVantage AI financial model.",
            "Apply for Udyam Registration (free MSME portal) and obtain local Gram Panchayat NOC.",
            "Submit loan application under PMEGP / Mudra / Micro-Enterprise credit window at nearest commercial or Grameen bank branch.",
            "Identify site lease or space preparation with water and power utilities."
        ],
        "Phase 2 (Days 31 to 60) — Procurement, Infrastructure & Training": [
            "Disbursement of bank loan and release of margin money.",
            f"Procurement and installation of essential machinery ({', '.join([m['machine_name'] for m in get_required_machines(rec_business.business_name)[:2]]) if get_required_machines(rec_business.business_name) else 'production tooling & equipment'}).",
            "Obtain quotations from regional machinery suppliers identified via GramVantage Setup Planner.",
            "Undergo short EDP (Entrepreneurship Development Program) or KVK skill training.",
            "Complete electrical load setup, trial test batches, and mandatory quality/safety licensing."
        ],
        "Phase 3 (Days 61 to 90) — Commercial Launch & Market Linkage": [
            "Formal commercial launch and opening of local retail / distribution counters.",
            "Establish forward sales contracts with local village traders, weekly haats, and town buyers.",
            "Implement daily cashflow bookkeeping and monitor monthly operating margins.",
            "Achieve break-even operating capacity to ensure seamless loan EMI servicing."
        ]
    }

    report = BusinessReport(
        report_id=report_id,
        created_at=created_at,
        entrepreneur_profile=profile,
        recommended_business=rec_business,
        local_feasibility=feasibility,
        financial_plan=financial_plan,
        relevant_schemes=schemes,
        explainable_reasons=explainable_reasons,
        action_plan_90_days=action_plan,
        disclaimer="GramVantage AI is an AI-assisted advisory system for rural micro-entrepreneurs. Financial structuring adheres to institutional micro-enterprise lending guidelines. Actual bank sanctions and scheme subsidies require formal application via authorized agencies."
    )

    # Save to SQLite
    save_report(report_id, profile.name or "session", b_id, report.model_dump())

    return report
