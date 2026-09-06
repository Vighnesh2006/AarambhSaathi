import sys
import io
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models import UserProfile, FinancialInput
from backend.finance import calculate_financial_plan
from backend.recommendation import get_recommendations
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.schemes import match_government_schemes
from backend.report import generate_business_report, ReportRequest

def test_all():
    print("=== TEST 1: Micro-Enterprise Credit Financial Engine ===")
    p_micro = calculate_financial_plan(FinancialInput(project_cost=140000, user_contribution=14000))
    print(f"Micro Tier: {p_micro.scheme_tier} | Loan: INR {p_micro.required_loan} ({p_micro.loan_percentage}%) | Rate: {p_micro.interest_rate}% | Tenure: {p_micro.tenure_years} yrs | EMI: INR {p_micro.monthly_emi} | Profit: INR {p_micro.monthly_profit}/mo | Break-even: {p_micro.break_even_months} mos")
    assert p_micro.scheme_tier == "MICRO FINANCE SCHEME"
    assert p_micro.interest_rate == 6.5
    assert p_micro.moratorium_months == 3
    assert p_micro.required_loan <= 125000.0

    p_term = calculate_financial_plan(FinancialInput(project_cost=300000, user_contribution=30000))
    print(f"Term Tier: {p_term.scheme_tier} | Loan: INR {p_term.required_loan} ({p_term.loan_percentage}%) | Rate: {p_term.interest_rate}% | Tenure: {p_term.tenure_years} yrs | EMI: INR {p_term.monthly_emi} | Profit: INR {p_term.monthly_profit}/mo | Break-even: {p_term.break_even_months} mos")
    assert p_term.scheme_tier == "TERM LOAN SCHEME"
    assert p_term.interest_rate == 8.0
    assert p_term.moratorium_months == 6

    print("\n=== TEST 2: Deterministic Recommendation Engine on 90 Catalogue Items ===")
    user_profile = UserProfile(
        name="Ramesh Patil",
        location="Shirwal Village",
        district="Satara",
        state="Maharashtra",
        capital=100000.0,
        skills=["Cattle", "Milking", "Animal Husbandry"],
        experience="5 years tending cows",
        resources=["Shed", "Water supply", "Small land"],
        business_interest="Dairy Farming",
        language="mr"
    )
    recs = get_recommendations(user_profile, top_n=3)
    print(f"Top 3 Recommendations for {user_profile.name}:")
    for i, r in enumerate(recs.recommendations, 1):
        print(f"{i}. {r.business_name} ({r.category}) - Score: {r.overall_score}/100 | Skill: {r.breakdown.skill_match_score}/25 | Cap: {r.breakdown.capital_match_score}/25 | Res: {r.breakdown.resource_match_score}/20")
    
    assert len(recs.recommendations) == 3
    assert "dairy" in recs.recommendations[0].business_name.lower()

    print("\n=== TEST 3: Hyper-Local Feasibility Evaluation ===")
    feas = evaluate_hyper_local_feasibility(recs.recommendations[0].business_id, user_profile)
    print(f"Feasibility Score: {feas.feasibility_score}/100 | Demand: {feas.market_opportunity} | Comp: {feas.competition_level}")
    assert feas.feasibility_score > 70

    print("\n=== TEST 4: Government Schemes Matcher ===")
    schemes = match_government_schemes(user_profile, business_id=recs.recommendations[0].business_id, business_category=recs.recommendations[0].category)
    print(f"Matched {len(schemes)} Schemes:")
    for s in schemes:
        print(f"- {s.scheme_name}: {s.why_relevant}")
    assert len(schemes) >= 3

    print("\n=== TEST 5: 90-Day Action Plan & Report Generator ===")
    rep = generate_business_report(ReportRequest(profile=user_profile, selected_business_id=recs.recommendations[0].business_id))
    print(f"Generated Report: {rep.report_id} | Sections: {len(rep.action_plan_90_days)} phases")
    assert "Phase 1" in list(rep.action_plan_90_days.keys())[0]

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_all()
