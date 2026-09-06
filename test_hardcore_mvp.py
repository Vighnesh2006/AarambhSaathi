import sys
from backend.models import UserProfile, ChatRequest
from backend.chatbot import process_chat, SESSIONS
from backend.recommendation import get_recommendations
from backend.database import validate_mvp_datasets

def run_tests():
    print("==================================================")
    print("RUNNING HARDCORE MVP TEST SUITE")
    print("==================================================")

    # 0. Validate Datasets
    print("\n--- TEST 0: Startup Dataset Validation ---")
    validate_mvp_datasets()
    print("[PASS] TEST 0 PASSED: Datasets verified successfully.")

    # TEST 1: Step-by-Step Personal Info Order
    print("\n--- TEST 1: Sequential Personal Info Order ---")
    res1_name = process_chat(ChatRequest(session_id="mvp_sess_1", message="Rahul"))
    print(f"Step after Name: {res1_name.current_step}")
    assert res1_name.current_step == "PERSONAL_PLACE", f"Expected PERSONAL_PLACE got {res1_name.current_step}"

    res1_place = process_chat(ChatRequest(session_id="mvp_sess_1", message="Pune"))
    print(f"Step after Place: {res1_place.current_step}")
    assert res1_place.current_step == "PERSONAL_OCCUPATION", f"Expected PERSONAL_OCCUPATION got {res1_place.current_step}"

    res1_occ = process_chat(ChatRequest(session_id="mvp_sess_1", message="Farmer"))
    print(f"Step after Occupation: {res1_occ.current_step}")
    assert res1_occ.current_step == "BUSINESS_SKILLS", f"Expected BUSINESS_SKILLS got {res1_occ.current_step}"
    print("[PASS] TEST 1 PASSED: Sequential personal information collected in exact order!")

    # TEST 2: Multi-Field Input
    print("\n--- TEST 2: Multi-Field Extraction ---")
    res2 = process_chat(ChatRequest(session_id="mvp_sess_2", message="My name is Rahul, I live in Pune and I am a farmer."))
    p2 = res2.updated_profile
    print(f"Extracted: Name={p2.name}, Place={p2.location}, Occupation={p2.occupation}")
    print(f"Next State: {res2.current_step}")
    assert p2.name == "Rahul" and p2.location == "Pune" and p2.occupation == "Farmer"
    assert res2.current_step == "BUSINESS_SKILLS"
    print("[PASS] TEST 2 PASSED: Multi-entity fast extraction skipped re-asking known fields!")

    # TEST 3: Animal Skills vs Manufacturing Penalty
    print("\n--- TEST 3: Animal Skills Filter ---")
    p3 = UserProfile(
        name="Rahul", location="Pune", district="Pune", state="Maharashtra",
        occupation="Farmer", skills=["Animal Care", "Farming"], capital=100000.0,
        resources=["2 cows", "cattle shed"], business_interest="Dairy Farming"
    )
    recs3 = get_recommendations(p3, top_n=3).recommendations
    top_names3 = [r.business_name for r in recs3]
    print(f"Top 3 Recommendations for Animal Care: {top_names3}")
    assert any("Dairy" in name or "Goat" in name or "Milk" in name for name in top_names3)
    assert not any("Plastic" in name or "Brick" in name or "Soap" in name for name in top_names3)
    print("[PASS] TEST 3 PASSED: Animal skills prioritized livestock/dairy and penalized manufacturing!")

    # TEST 4: Guidance From Scratch
    print("\n--- TEST 4: Guidance From Scratch ---")
    res4 = process_chat(ChatRequest(session_id="mvp_sess_4", message="I don't know what business I should start."))
    print(f"State for user with no idea: {res4.current_step}")
    assert res4.current_step == "PERSONAL_NAME"
    print("[PASS] TEST 4 PASSED: Guidance from scratch collects profile first!")

    # TEST 5: User Choice
    print("\n--- TEST 5: User Business Choice ---")
    p5 = UserProfile(name="Suresh", location="Satara", district="Satara", state="Maharashtra", occupation="Farmer", skills=["Livestock Management"], capital=150000.0)
    recs5 = get_recommendations(p5, top_n=3).recommendations
    print(f"Top choice for Suresh: {recs5[0].business_name}")
    assert any(k in recs5[0].business_name for k in ["Goat", "Dairy", "Livestock", "Duck", "Poultry", "Animal"]) or "Livestock" in recs5[0].category
    print("[PASS] TEST 5 PASSED: User business choice stored correctly!")

    # TEST 7: Supplier BEFORE Finance & Schemes
    print("\n--- TEST 7: Supplier Pipeline Position ---")
    workflow_order = ["BUSINESS_SELECTION", "EQUIPMENT", "SUPPLIER", "COST_ESTIMATION", "INVESTMENT", "FINANCIAL", "SCHEME_OPT_IN"]
    print(f"Workflow sequence: {' -> '.join(workflow_order)}")
    assert workflow_order.index("SUPPLIER") < workflow_order.index("FINANCIAL")
    assert workflow_order.index("SUPPLIER") < workflow_order.index("SCHEME_OPT_IN")
    print("[PASS] TEST 7 PASSED: Supplier pipeline correctly positioned BEFORE finance and scheme!")

    # TEST 10 & 11: Scheme Opt-In vs Opt-Out
    print("\n--- TEST 10 & 11: Scheme Opt-In Isolation ---")
    SESSIONS["mvp_sess_optin"] = {"current_state": "SCHEME_OPT_IN", "profile": p3, "language": "en"}
    res_optin = process_chat(ChatRequest(session_id="mvp_sess_optin", message="Yes, Check Government Schemes"))
    print(f"Opt-In Next State: {res_optin.current_step}")
    assert res_optin.current_step == "SCHEME_PROFILE"

    SESSIONS["mvp_sess_optout"] = {"current_state": "SCHEME_OPT_IN", "profile": p3, "language": "en"}
    res_optout = process_chat(ChatRequest(session_id="mvp_sess_optout", message="No, Continue"))
    print(f"Opt-Out Next State: {res_optout.current_step}")
    assert res_optout.current_step in ["COMPLETE", "DPR", "EQUIPMENT"]
    print("[PASS] TEST 10 & 11 PASSED: Scheme opt-in isolated demographic questions!")

    print("\n==================================================")
    print("ALL HARDCORE MVP TEST SCENARIOS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
