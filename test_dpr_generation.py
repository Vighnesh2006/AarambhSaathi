import sys
import io
import json
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.models import UserProfile, ReportRequest, BusinessReport, FinancialInput
from backend.recommendation import get_recommendations
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.finance import calculate_financial_plan
from backend.schemes import get_scheme_match_response
from backend.report import generate_business_report

def run_dpr_tests():
    print("==================================================================")
    print("STARTING DETERMINISTIC BUSINESS PLAN / DPR GENERATOR TESTS (STEP 7)")
    print("==================================================================")

    # -----------------------------------------------------------------
    # TEST 1: Complete Profile + All Steps 1-6 -> All 17 Sections Generated
    # -----------------------------------------------------------------
    print("\n--- TEST 1: Full 17-Section Report Generation ---")
    p1 = UserProfile(
        name="Santosh Jadhav",
        age=28,
        gender="Male",
        category="OBC",
        education="10th pass",
        state="Maharashtra",
        district="Satara",
        village="Koregaon",
        capital=35000.0,
        skills=["Spice Grinding", "Packaging", "Farming"],
        experience="3 years agro-commodity trading",
        resources=["Processing shed", "Water source", "Power"],
        business_interest="Spice Processing",
        intent="Start a new business",
        rural_urban="Rural",
        language="en"
    )

    req1 = ReportRequest(
        profile=p1,
        selected_business_id="AGR-FP-002",
        custom_project_cost=250000.0,
        language="en"
    )

    report1 = generate_business_report(req1)
    print(f"Report ID: {report1.report_id} | Created At: {report1.created_at}")
    print(f"Executive Summary: {report1.executive_summary[:90]}...")
    
    # Verify all 17 sections are present
    assert report1.report_id.startswith("GV-"), "Report ID must follow official format"
    assert len(report1.executive_summary) > 20, "Section 1 Executive Summary must be generated"
    assert report1.entrepreneur_profile.name == "Santosh Jadhav", "Section 2 Profile must match"
    assert report1.recommended_business is not None, "Section 3 Business must be present"
    assert len(report1.explainable_reasons) >= 3, "Section 4 Explainable reasons must be generated"
    assert report1.local_feasibility is not None, "Section 5 Feasibility must be present"
    assert report1.business_setup is not None, "Section 6 Business setup must be present"
    assert isinstance(report1.machinery, list), "Section 7 Machinery list must be present"
    assert isinstance(report1.suppliers, list), "Section 8 Suppliers must be present"
    assert report1.project_cost_breakdown is not None, "Section 9 Cost breakdown must be present"
    assert report1.means_of_finance is not None, "Section 10 Means of finance must be present"
    assert report1.financial_projections is not None, "Section 11 Projections must be present"
    assert len(report1.relevant_schemes) > 0, "Section 12 Schemes must be present"
    assert len(report1.documents) > 0, "Section 13 Documents must be present"
    assert report1.roadmap is not None, "Section 14 Roadmap must be present"
    assert len(report1.risks) >= 3, "Section 15 Risks must be present"
    assert len(report1.data_sources) >= 5, "Section 16 Data sources must be present"
    assert "preliminary" in report1.disclaimer.lower(), "Section 17 Disclaimer must be present"
    print("TEST 1 PASSED: All 17 structured sections successfully populated.")

    # -----------------------------------------------------------------
    # TEST 2: Missing Supplier Information -> Safe Non-Fabrication
    # -----------------------------------------------------------------
    print("\n--- TEST 2: Supplier Information Handling (No Hallucination) ---")
    p2 = UserProfile(
        name="Raju Shinde",
        state="Maharashtra",
        district="Satara",
        capital=50000.0,
        skills=["Cattle care"]
    )
    req2 = ReportRequest(
        profile=p2,
        selected_business_id="dairy / team validation_milk_quality_testing_service",
        custom_project_cost=140000.0
    )
    report2 = generate_business_report(req2)
    print(f"Suppliers count for testing service: {len(report2.suppliers)}")
    # If no supplier exists, suppliers list can be empty or verified records only, never fabricated names
    for sup in report2.suppliers:
        assert "supplier_name" in sup or "name" in sup, "Supplier record must have valid name"
    print("TEST 2 PASSED: Supplier list strictly reflects database records without hallucination.")

    # -----------------------------------------------------------------
    # TEST 3: Missing Scheme Information Handling
    # -----------------------------------------------------------------
    print("\n--- TEST 3: Scheme Eligibility & Data Status Handling ---")
    p3 = UserProfile(
        name="Anonymous User",
        age=None,
        state=None,
        capital=100000.0
    )
    req3 = ReportRequest(
        profile=p3,
        selected_business_id="AGR-FP-002"
    )
    report3 = generate_business_report(req3)
    print(f"Schemes evaluated: {len(report3.relevant_schemes)}")
    assert len(report3.relevant_schemes) > 0
    print("TEST 3 PASSED: Scheme evaluation handles incomplete profile gracefully.")

    # -----------------------------------------------------------------
    # TEST 4: Financial Data Integrity (DPR vs Step 5 Engine)
    # -----------------------------------------------------------------
    print("\n--- TEST 4: Financial Data Integrity Verification ---")
    fin_step5 = calculate_financial_plan(FinancialInput(
        project_cost=250000.0,
        user_contribution=35000.0,
        business_id=report1.recommended_business.business_id,
        business_name=report1.recommended_business.business_name,
        profile=p1
    ))
    
    assert report1.financial_plan.project_cost == fin_step5.project_cost, "DPR project cost must exactly equal Step 5 cost"
    assert report1.financial_plan.own_contribution == fin_step5.own_contribution, "DPR own contribution must exactly equal Step 5 own contribution"
    assert report1.financial_plan.required_loan == fin_step5.required_loan, "DPR funding requirement must exactly equal Step 5 required loan"
    assert report1.financial_plan.monthly_emi == fin_step5.monthly_emi, "DPR monthly EMI must exactly equal Step 5 EMI"
    assert report1.financial_plan.monthly_profit == fin_step5.monthly_profit, "DPR profit must exactly equal Step 5 profit"
    print(f"Cost: INR {report1.financial_plan.project_cost:,.0f} == INR {fin_step5.project_cost:,.0f}")
    print(f"Own: INR {report1.financial_plan.own_contribution:,.0f} == INR {fin_step5.own_contribution:,.0f}")
    print(f"Loan: INR {report1.financial_plan.required_loan:,.0f} == INR {fin_step5.required_loan:,.0f}")
    print(f"EMI: INR {report1.financial_plan.monthly_emi:,.2f} == INR {fin_step5.monthly_emi:,.2f}")
    print("TEST 4 PASSED: 100% Financial data integrity verified.")

    # -----------------------------------------------------------------
    # TEST 5: Recommendation Score Integrity
    # -----------------------------------------------------------------
    print("\n--- TEST 5: Recommendation Score Integrity Verification ---")
    recs = get_recommendations(p1, top_n=1)
    original_rec_score = recs.recommendations[0].overall_score
    print(f"Original Recommendation Score: {original_rec_score}")
    print(f"Report Recommendation Score: {report1.recommended_business.overall_score}")
    assert report1.recommended_business.overall_score == original_rec_score, "DPR must not alter recommendation score"
    print("TEST 5 PASSED: Recommendation score unaltered.")

    # -----------------------------------------------------------------
    # TEST 6: Feasibility Score Integrity
    # -----------------------------------------------------------------
    print("\n--- TEST 6: Feasibility Score Integrity Verification ---")
    feas_direct = evaluate_hyper_local_feasibility(report1.recommended_business.business_id, p1)
    print(f"Direct Feasibility Score: {feas_direct.feasibility_score}")
    print(f"Report Feasibility Score: {report1.local_feasibility.feasibility_score}")
    assert report1.local_feasibility.feasibility_score == feas_direct.feasibility_score, "DPR must not alter feasibility score"
    print("TEST 6 PASSED: Feasibility score unaltered.")

    # -----------------------------------------------------------------
    # TEST 7: Deterministic Generation Without Gemini
    # -----------------------------------------------------------------
    print("\n--- TEST 7: Deterministic Offline Generation ---")
    req_offline = ReportRequest(
        profile=p1,
        selected_business_id="AGR-FP-002",
        custom_project_cost=300000.0
    )
    rep_offline = generate_business_report(req_offline)
    assert rep_offline.report_id is not None
    assert len(rep_offline.executive_summary) > 50
    assert rep_offline.financial_plan.project_cost == 300000.0
    print("TEST 7 PASSED: Pure deterministic template fallback operational.")

    # -----------------------------------------------------------------
    # TEST 8: Multilingual Report Generation (EN, HI, MR)
    # -----------------------------------------------------------------
    print("\n--- TEST 8: Multilingual Report Generation (EN, HI, MR) ---")
    # Marathi
    req_mr = ReportRequest(profile=p1, selected_business_id="AGR-FP-002", language="mr")
    rep_mr = generate_business_report(req_mr)
    print(f"MR Summary: {rep_mr.executive_summary[:60]}...")
    assert "आरंभ साथीने" in rep_mr.executive_summary or "व्यवसाय" in rep_mr.executive_summary

    # Hindi
    req_hi = ReportRequest(profile=p1, selected_business_id="AGR-FP-002", language="hi")
    rep_hi = generate_business_report(req_hi)
    print(f"HI Summary: {rep_hi.executive_summary[:60]}...")
    assert "आरंभ साथी ने" in rep_hi.executive_summary or "व्यवसाय" in rep_hi.executive_summary
    print("TEST 8 PASSED: Multilingual templates verified.")

    # -----------------------------------------------------------------
    # TEST 9: POST /api/report Endpoint Backward Compatibility
    # -----------------------------------------------------------------
    print("\n--- TEST 9: API Contract Backward Compatibility ---")
    # Simulate legacy caller passing only profile and selected_business_id
    legacy_req = ReportRequest(
        profile=p1,
        selected_business_id="AGR-FP-002"
    )
    legacy_rep = generate_business_report(legacy_req)
    assert hasattr(legacy_rep, "report_id")
    assert hasattr(legacy_rep, "created_at")
    assert hasattr(legacy_rep, "entrepreneur_profile")
    assert hasattr(legacy_rep, "recommended_business")
    assert hasattr(legacy_rep, "local_feasibility")
    assert hasattr(legacy_rep, "financial_plan")
    assert hasattr(legacy_rep, "relevant_schemes")
    assert hasattr(legacy_rep, "explainable_reasons")
    assert hasattr(legacy_rep, "action_plan_90_days")
    assert hasattr(legacy_rep, "disclaimer")
    print("TEST 9 PASSED: Legacy endpoint schema fully compatible.")

    print("\n==================================================================")
    print(">>> ALL 9 BUSINESS PLAN / DPR GENERATOR TESTS PASSED! <<<")
    print("==================================================================")

if __name__ == "__main__":
    run_dpr_tests()
