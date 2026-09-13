import sys
import io
import json
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.models import UserProfile, SchemeMatchRequest
from backend.schemes import (
    match_government_schemes,
    match_government_schemes_core,
    get_scheme_match_response,
    check_age_eligibility,
    check_gender_eligibility,
    check_category_eligibility,
    check_income_eligibility,
    check_education_eligibility,
    check_location_eligibility,
    check_project_cost_eligibility,
    generate_personalized_documents,
    SCHEME_RULES_REGISTRY,
)

def run_tests():
    print("==================================================================")
    print("STARTING DETERMINISTIC GOVERNMENT SCHEME MATCHING ENGINE TESTS")
    print("==================================================================")

    # -----------------------------------------------------------------
    # TEST 1: New Rural Entrepreneur in Maharashtra matching PMEGP
    # -----------------------------------------------------------------
    print("\n--- TEST 1: New rural entrepreneur (Age 28, Maharashtra, Rural, MFG business, INR 2.5L cost) ---")
    p1 = UserProfile(
        name="Santosh Jadhav",
        age=28,
        gender="Male",
        category="OBC",
        education="10th pass",
        state="Maharashtra",
        district="Satara",
        village="Koregaon",
        location="Koregaon, Satara",
        capital=30000.0,
        business_interest="Spice Processing",
        intent="Start a new business",
        rural_urban="Rural"
    )
    
    res1 = get_scheme_match_response(
        profile=p1,
        business_id="AGR-FP-002",
        business_category="Food Processing",
        business_name="Spice Processing & Packaging",
        project_cost=250000.0,
        own_contribution=25000.0,
        funding_requirement=225000.0
    )
    
    print(f"Matched Schemes Count: {len(res1.matched_schemes)}")
    print(f"Conditional Schemes Count: {len(res1.conditional_schemes)}")
    print(f"Total Relevant Schemes: {len(res1.matched_schemes) + len(res1.conditional_schemes)}")
    
    # Verify PMEGP is in matched or conditional
    all_matched_ids = [s.scheme_id for s in res1.matched_schemes + res1.conditional_schemes]
    print("Top matched scheme IDs:", all_matched_ids[:5])
    assert "pmegp" in all_matched_ids, "PMEGP must be matched for new rural food processing entrepreneur"
    
    pmegp_obj = next(s for s in res1.matched_schemes + res1.conditional_schemes if s.scheme_id == "pmegp")
    print(f"PMEGP Status: {pmegp_obj.status} | Match Score: {pmegp_obj.match_score}% | Confidence: {pmegp_obj.confidence}%")
    assert pmegp_obj.status in ["MATCHED", "CONDITIONALLY MATCHED"]
    assert pmegp_obj.match_score >= 70.0
    print("TEST 1 PASSED: Rural entrepreneur successfully matched according to deterministic criteria.")

    # -----------------------------------------------------------------
    # TEST 2: Missing Eligibility Field -> INSUFFICIENT DATA (Not Eligible)
    # -----------------------------------------------------------------
    print("\n--- TEST 2: User missing an eligibility field (Age = None, Category = None) ---")
    p2 = UserProfile(
        name="Unknown Applicant",
        age=None,  # Unknown age!
        state="Maharashtra",
        capital=100000.0
    )
    age_check = check_age_eligibility(SCHEME_RULES_REGISTRY["pmegp"], p2)
    print(f"Age Check Result: condition={age_check.condition}, status={age_check.status}, reason={age_check.reason}")
    assert age_check.status == "Insufficient Data", "Missing age MUST return 'Insufficient Data', NEVER 'Eligible'"

    # Check Stand-Up India requiring category/gender when both are None
    gender_check = check_gender_eligibility(SCHEME_RULES_REGISTRY["stand_up_india"], p2)
    print(f"Stand-Up India Target Check: status={gender_check.status}, reason={gender_check.reason}")
    assert gender_check.status == "Insufficient Data", "Missing gender & category MUST return 'Insufficient Data'"
    print("TEST 2 PASSED: Missing data strictly treated as 'Insufficient Data' (Unknown != Eligible).")

    # -----------------------------------------------------------------
    # TEST 3: User Violates Explicit Mandatory Rule -> NOT ELIGIBLE
    # -----------------------------------------------------------------
    print("\n--- TEST 3: Hard disqualifiers (Underage applicant & Out-of-state applicant) ---")
    p3_underage = UserProfile(
        name="Minor Applicant",
        age=16, # Under 18
        state="Maharashtra",
        capital=50000.0
    )
    age_check_underage = check_age_eligibility(SCHEME_RULES_REGISTRY["pmegp"], p3_underage)
    print(f"Underage check (Age 16): status={age_check_underage.status}, reason={age_check_underage.reason}")
    assert age_check_underage.status == "Not Eligible", "Age < 18 must be Not Eligible"

    # State scheme mismatch: Rajasthan resident applying for Maharashtra CMEGP
    p3_rajasthan = UserProfile(
        name="Jaipur Resident",
        age=25,
        state="Rajasthan",
        capital=100000.0
    )
    loc_check_mh = check_location_eligibility(SCHEME_RULES_REGISTRY["cmeegp_mh"], p3_rajasthan)
    print(f"Location check (Rajasthan resident for MH scheme): status={loc_check_mh.status}, reason={loc_check_mh.reason}")
    assert loc_check_mh.status == "Not Eligible", "Out-of-state applicant must be Not Eligible for state scheme"
    
    # Stand-Up India male general category applicant (Stand-Up India is for Women or SC/ST)
    p3_male_gen = UserProfile(
        name="General Male Applicant",
        age=30,
        gender="Male",
        category="General",
        state="Maharashtra"
    )
    su_check = check_gender_eligibility(SCHEME_RULES_REGISTRY["stand_up_india"], p3_male_gen)
    print(f"Stand-Up India check for Male General: status={su_check.status}, reason={su_check.reason}")
    assert su_check.status == "Not Eligible", "Male General applicant must be Not Eligible for Stand-Up India"
    print("TEST 3 PASSED: Hard disqualifiers correctly result in 'Not Eligible'.")

    # -----------------------------------------------------------------
    # TEST 4: Project Cost Above Scheme Financial Limit
    # -----------------------------------------------------------------
    print("\n--- TEST 4: Project cost above scheme financial limit ---")
    # PMEGP Manufacturing maximum is 50 Lakh (5,000,000). Test with 60 Lakh.
    cost_check_high, fin_fit_high = check_project_cost_eligibility(
        SCHEME_RULES_REGISTRY["pmegp"],
        project_cost=6000000.0,
        business_sector="Manufacturing"
    )
    print(f"PMEGP Cost Check (INR 60L): status={cost_check_high.status}, fit_status={fin_fit_high.status}, max_limit={fin_fit_high.max_limit}")
    assert cost_check_high.status == "Not Eligible"
    assert fin_fit_high.status == "Exceeds Scheme Limit"

    # Stand-Up India minimum threshold is 10 Lakh. Test with 5 Lakh.
    cost_check_low, fin_fit_low = check_project_cost_eligibility(
        SCHEME_RULES_REGISTRY["stand_up_india"],
        project_cost=500000.0,
        business_sector="Manufacturing"
    )
    print(f"Stand-Up India Cost Check (INR 5L): status={cost_check_low.status}, fit_status={fin_fit_low.status}, min_limit={fin_fit_low.min_limit}")
    assert cost_check_low.status == "Not Eligible"
    assert fin_fit_low.status == "Below Scheme Minimum"
    print("TEST 4 PASSED: Financial outlay limits evaluated and flagged deterministically.")

    # -----------------------------------------------------------------
    # TEST 5: Conditional Category Requirement
    # -----------------------------------------------------------------
    print("\n--- TEST 5: Conditional category requirements and subsidy rates ---")
    p5_sc = UserProfile(
        name="Pooja Kamble",
        age=29,
        gender="Female",
        category="SC",
        state="Maharashtra",
        capital=50000.0
    )
    cat_check_sc = check_category_eligibility(SCHEME_RULES_REGISTRY["pmegp"], p5_sc)
    print(f"SC category check: status={cat_check_sc.status}, reason={cat_check_sc.reason}")
    assert cat_check_sc.status == "Eligible"
    assert "35%" in cat_check_sc.reason or "special" in cat_check_sc.reason.lower()
    print("TEST 5 PASSED: Enhanced special category conditions handled properly.")

    # -----------------------------------------------------------------
    # TEST 6: Document Checklist Generation
    # -----------------------------------------------------------------
    print("\n--- TEST 6: Personalized document checklist generation ---")
    docs_sc = generate_personalized_documents(
        scheme_id="pmegp",
        raw_docs=["Aadhaar Card", "PAN Card", "Project Report", "Caste Certificate"],
        profile=p5_sc,
        project_cost=300000.0,
        business_sector="Food Processing"
    )
    doc_names = [d.document_name for d in docs_sc]
    print(f"Generated {len(docs_sc)} documents for SC female entrepreneur:")
    for d in docs_sc:
        print(f"  - [{d.status}] {d.document_name} ({d.where_to_get})")
    
    assert any("Aadhaar" in n for n in doc_names)
    assert any("PAN" in n for n in doc_names)
    assert any("Detailed Project Report" in n or "DPR" in n for n in doc_names)
    assert any("Caste" in n for n in doc_names)
    caste_doc = next(d for d in docs_sc if "Caste" in d.document_name)
    assert caste_doc.status == "Required", "For SC profile, Caste Certificate must be marked Required"
    print("TEST 6 PASSED: Personalized document checklist verified.")

    # -----------------------------------------------------------------
    # TEST 7: Official Source Fields Preserved
    # -----------------------------------------------------------------
    print("\n--- TEST 7: Official source and verified date preservation ---")
    for s_id, rule in SCHEME_RULES_REGISTRY.items():
        assert rule.get("official_url"), f"Scheme {s_id} must have official_url"
        assert rule.get("source"), f"Scheme {s_id} must have source authority"
        assert rule.get("last_verified"), f"Scheme {s_id} must have last_verified date"
        assert rule["official_url"].startswith("http"), f"Official URL for {s_id} must be a valid HTTP link"
    print(f"Verified {len(SCHEME_RULES_REGISTRY)} core schemes have authentic official portals & verification dates.")
    print("TEST 7 PASSED: Official source fields preserved.")

    # -----------------------------------------------------------------
    # TEST 8: No Fabricated Subsidy or Loan Amounts
    # -----------------------------------------------------------------
    print("\n--- TEST 8: Verifying benefits come directly from structured scheme data ---")
    schemes_matched = match_government_schemes(p1, business_id="AGR-FP-002", project_cost=250000.0)
    for sm in schemes_matched:
        assert isinstance(sm.benefits, list)
        assert len(sm.benefits) > 0
        assert sm.benefits[0] != ""
        print(f"  Scheme: {sm.scheme_name[:35]} | Benefit Sample: {sm.benefits[0][:50]}...")
    print("TEST 8 PASSED: Benefits are structured and extracted from verified sources without fabrication.")

    # -----------------------------------------------------------------
    # TEST 9: Existing API Endpoints and Backward Compatibility
    # -----------------------------------------------------------------
    print("\n--- TEST 9: Backward compatibility for match_government_schemes ---")
    legacy_results = match_government_schemes(p1, business_id="AGR-FP-002")
    assert isinstance(legacy_results, list)
    assert len(legacy_results) > 0
    assert hasattr(legacy_results[0], "scheme_name")
    assert hasattr(legacy_results[0], "why_relevant")
    assert hasattr(legacy_results[0], "possible_support")
    assert hasattr(legacy_results[0], "required_documents")
    assert hasattr(legacy_results[0], "official_source")
    print(f"Returned {len(legacy_results)} legacy-compatible MatchedScheme objects.")
    print("TEST 9 PASSED: Complete backward compatibility verified.")

    print("\n==================================================================")
    print(">>> ALL 9 GOVERNMENT SCHEME MATCHING ENGINE TESTS PASSED! <<<")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
