import sys
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from backend.models import UserProfile, ChatRequest, FeasibilityRequest, FinancialInput, SchemeMatchRequest, ReportRequest
from backend.chatbot import process_chat
from backend.recommendation import get_recommendations
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.finance import calculate_financial_plan
from backend.schemes import match_government_schemes
from backend.report import generate_business_report

print("================================================================")
print("AARAMBH SAATHI MVP UPGRADE - STEP 1 COMPREHENSIVE TEST SUITE")
print("================================================================\n")

# 1. TEST COMPOUND MULTI-ENTITY EXTRACTION
print("--- TEST 1: Compound Multi-Entity Extraction ---")
compound_msg = "My name is Suresh Patil, I am 28, I live in Pune and I have experience in dairy farming."
res_compound = process_chat(ChatRequest(message=compound_msg, language="en"))
p_c = res_compound.updated_profile
print(f"Extracted Name: {p_c.name}")
print(f"Extracted Age: {p_c.age}")
print(f"Extracted Location: {p_c.location} | District: {p_c.district} | State: {p_c.state}")
print(f"Extracted Skills: {p_c.skills}")
print(f"Extracted Interest: {p_c.business_interest}")
print(f"Next Logical Step: {res_compound.current_step} (Should be USER_INTENT)")
assert p_c.name == "Suresh Patil", f"Expected Suresh Patil, got {p_c.name}"
assert p_c.age == 28, f"Expected 28, got {p_c.age}"
assert p_c.district == "Pune", f"Expected Pune, got {p_c.district}"
assert res_compound.current_step == "USER_INTENT", f"Expected USER_INTENT, got {res_compound.current_step}"
print(">>> TEST 1 PASSED!\n")

# 2. TEST PROGRESSIVE TURN-BY-TURN ONBOARDING (ENGLISH)
print("--- TEST 2: Progressive Turn-by-Turn Profile Flow (EN) ---")
session_en = "sess_step1_en"
turns = [
    ("Name", "Ramesh Patil", "USER_INTENT"),
    ("Intent", "Start a new business", "PERSONAL_AGE"),
    ("Age", "29", "PERSONAL_GENDER"),
    ("Gender", "Male", "PERSONAL_LOCATION"),
    ("Location", "Shirwal, Satara, Maharashtra", "PERSONAL_EDUCATION"),
    ("Education", "12th Pass", "BUSINESS_SKILLS"),
    ("Skills", "Cattle Rearing & Milking", "BUSINESS_RESOURCES"),
    ("Resources", "Own Land & Water Source", "BUSINESS_CAPITAL"),
    ("Investment", "1 lakh", "BUSINESS_INTEREST"),
    ("Business Interest", "Dairy Farming", "PROFILE_CONFIRMATION")
]

history = []
curr_p = UserProfile(language="en")

for step_name, msg, expected_step in turns:
    res = process_chat(ChatRequest(
        session_id=session_en,
        message=msg,
        conversation_history=history,
        profile=curr_p,
        language="en"
    ))
    curr_p = res.updated_profile
    print(f"  [{step_name}] User: '{msg}' -> State: {res.current_step}")
    assert res.current_step == expected_step, f"Expected {expected_step}, got {res.current_step}"

assert res.is_profile_ready == True, "Expected is_profile_ready = True at confirmation"
print(">>> TEST 2 PASSED!\n")

# 3. TEST EDIT / FIELD CORRECTION IN PROFILE
print("--- TEST 3: Edit Profile Field ---")
updated_p = curr_p.model_copy(update={"capital": 150000.0, "available_investment": 150000.0, "education": "Graduate"})
assert updated_p.capital == 150000.0
assert updated_p.available_investment == 150000.0
assert updated_p.education == "Graduate"
print(">>> TEST 3 PASSED!\n")

# 4. TEST MARATHI CONVERSATIONAL ONBOARDING
print("--- TEST 4: Marathi Progressive Onboarding ---")
session_mr = "sess_step1_mr"
res_mr = process_chat(ChatRequest(session_id=session_mr, message="तुकाराम शिंदे", language="mr"))
print(f"  Turn 1 (MR): State={res_mr.current_step} | Reply: {res_mr.reply.splitlines()[0]}")
assert res_mr.current_step == "USER_INTENT"
assert "तुकाराम" in res_mr.reply

res_mr_2 = process_chat(ChatRequest(session_id=session_mr, message="नवीन व्यवसाय सुरू करणे", language="mr", profile=res_mr.updated_profile))
print(f"  Turn 2 (MR): State={res_mr_2.current_step} | Reply: {res_mr_2.reply.splitlines()[0]}")
assert res_mr_2.current_step == "PERSONAL_AGE"
print(">>> TEST 4 PASSED!\n")

# 5. TEST HINDI CONVERSATIONAL ONBOARDING
print("--- TEST 5: Hindi Progressive Onboarding ---")
session_hi = "sess_step1_hi"
res_hi = process_chat(ChatRequest(session_id=session_hi, message="सुरेश कुमार", language="hi"))
print(f"  Turn 1 (HI): State={res_hi.current_step} | Reply: {res_hi.reply.splitlines()[0]}")
assert res_hi.current_step == "USER_INTENT"
assert "सुरेश" in res_hi.reply

res_hi_2 = process_chat(ChatRequest(session_id=session_hi, message="नया व्यवसाय शुरू करना", language="hi", profile=res_hi.updated_profile))
print(f"  Turn 2 (HI): State={res_hi_2.current_step} | Reply: {res_hi_2.reply.splitlines()[0]}")
assert res_hi_2.current_step == "PERSONAL_AGE"
print(">>> TEST 5 PASSED!\n")

# 6. TEST COMPATIBILITY WITH DOWNSTREAM ENGINES (Recommendations, Feasibility, Finance, Schemes, DPR)
print("--- TEST 6: Backward Compatibility with Advisory Engines ---")
# Recommendation engine
recs = get_recommendations(curr_p, top_n=3)
print(f"  Top Recommendation: {recs.recommendations[0].business_name} (Score: {recs.recommendations[0].overall_score})")
assert len(recs.recommendations) == 3

# Feasibility engine
feas = evaluate_hyper_local_feasibility(recs.recommendations[0].business_id, curr_p)
print(f"  Feasibility: Score={feas.feasibility_score} | Demand={feas.market_opportunity}")
assert feas.feasibility_score > 0

# Financial calculation engine
fin = calculate_financial_plan(FinancialInput(project_cost=200000.0, user_contribution=curr_p.capital))
print(f"  Financial Plan: Loan=₹{fin.required_loan:,.0f} | EMI=₹{fin.monthly_emi:,.0f} | Profit=₹{fin.monthly_profit:,.0f}")
assert fin.required_loan > 0

# Schemes matcher
schemes = match_government_schemes(curr_p, recs.recommendations[0].business_id, recs.recommendations[0].category, 200000.0)
print(f"  Matched Schemes: Found {len(schemes)} schemes (Top: {schemes[0].scheme_name})")
assert len(schemes) > 0

# DPR Report Generator
dpr = generate_business_report(ReportRequest(profile=curr_p, selected_business_id=recs.recommendations[0].business_id, custom_project_cost=200000.0))
print(f"  DPR Report ID: {dpr.report_id}")
assert dpr.report_id.startswith("GV-")
print(">>> TEST 6 PASSED!\n")

print("================================================================")
print(">>> ALL STEP 1 VERIFICATIONS COMPLETED SUCCESSFULLY! <<<")
print("================================================================")
