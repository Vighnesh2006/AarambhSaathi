import sys
from backend.models import UserProfile, ChatRequest
from backend.chatbot import process_chat
from backend.recommendation import get_recommendations

def run_tests():
    print("==================================================")
    print("RUNNING ADVISORY WORKFLOW TEST SUITE")
    print("==================================================")

    # TEST 1: Multi-entity fast extraction
    print("\n--- TEST 1: Multi-Entity Fast Extraction ---")
    req1 = ChatRequest(
        session_id="test_sess_1",
        message="My name is Rahul, I live in Pune and I am a farmer."
    )
    res1 = process_chat(req1)
    p1 = res1.updated_profile
    print(f"Extracted Profile: Name={p1.name}, Location={p1.location}, Occupation={p1.occupation}")
    print(f"Next State: {res1.current_step}")
    print(f"Reply: {res1.reply[:120]}...")
    assert p1.name == "Rahul", "Name extraction failed"
    assert p1.location == "Pune", "Location extraction failed"
    assert p1.occupation == "Farmer", "Occupation extraction failed"
    assert res1.current_step == "BUSINESS_SKILLS", f"Expected BUSINESS_SKILLS but got {res1.current_step}"
    print("[PASS] TEST 1 PASSED: Fast-path multi-entity extraction worked cleanly!")


    # TEST 2: Sector-Aware Recommendations (Dairy/Cows -> No Manufacturing)
    print("\n--- TEST 2: Sector-Aware Recommendations ---")
    p2 = UserProfile(
        name="Rahul",
        location="Pune",
        district="Pune",
        state="Maharashtra",
        occupation="Farmer",
        skills=["Cattle Rearing", "Animal Husbandry"],
        capital=100000.0,
        resources=["2 cows", "cattle shed"],
        business_interest="Dairy Farming"
    )
    rec_res = get_recommendations(p2, top_n=3)
    recs = rec_res.recommendations
    print("Top 3 Recommendations for Dairy Farmer:")
    for i, r in enumerate(recs):
        print(f"  {i+1}. {r.business_name} (Category: {r.category}, Score: {r.overall_score})")

    top_names = [r.business_name.lower() for r in recs]
    assert any("dairy" in name or "milk" in name or "cattle" in name for name in top_names), "Dairy recommendation missing!"
    assert not any("brick" in name or "plastic" in name or "concrete" in name for name in top_names), "Manufacturing block making should be penalized!"
    print("[PASS] TEST 2 PASSED: Sector-aware engine prioritized Livestock/Dairy over Manufacturing!")


    # TEST 3: General "Don't know" interest
    print("\n--- TEST 3: Guidance From Scratch ---")
    req3 = ChatRequest(
        session_id="test_sess_3",
        message="I don't know what business to start."
    )
    res3 = process_chat(req3)
    print(f"Next State for new user: {res3.current_step}")
    assert res3.current_step == "PERSONAL_NAME", "Should start with PERSONAL_NAME"
    print("[PASS] TEST 3 PASSED: Guidance from scratch starts cleanly with PERSONAL_NAME!")


    # TEST 4: Goat Farming selection
    print("\n--- TEST 4: Goat Farming Selection ---")
    p4 = UserProfile(
        name="Suresh",
        location="Satara",
        district="Satara",
        state="Maharashtra",
        occupation="Farmer",
        skills=["Livestock Rearing"],
        capital=150000.0,
        resources=["Land", "Shed"],
        business_interest="Goat Farming"
    )
    recs4 = get_recommendations(p4, top_n=3).recommendations
    print("Top Recommendations for Goat Farming:")
    for i, r in enumerate(recs4):
        print(f"  {i+1}. {r.business_name} (Score: {r.overall_score})")
    assert any("goat" in r.business_name.lower() or "livestock" in r.business_name.lower() for r in recs4)
    print("[PASS] TEST 4 PASSED: Goat farming prioritized correctly!")

    # TEST 5 & 6: Scheme Opt-In vs Opt-Out
    print("\n--- TEST 5 & 6: Scheme Opt-In Isolation ---")
    req5_in = ChatRequest(
        session_id="test_sess_5",
        message="Yes, Check Schemes"
    )
    # Simulate session in SCHEME_OPT_IN
    from backend.chatbot import SESSIONS
    SESSIONS["test_sess_5"] = {
        "current_state": "SCHEME_OPT_IN",
        "profile": p2,
        "language": "en"
    }
    res5_in = process_chat(req5_in)
    print(f"Opt-In Next State: {res5_in.current_step}")
    assert res5_in.current_step == "SCHEME_PROFILE", f"Expected SCHEME_PROFILE but got {res5_in.current_step}"

    req6_out = ChatRequest(
        session_id="test_sess_6",
        message="No, Continue"
    )
    SESSIONS["test_sess_6"] = {
        "current_state": "SCHEME_OPT_IN",
        "profile": p2,
        "language": "en"
    }
    res6_out = process_chat(req6_out)
    print(f"Opt-Out Next State: {res6_out.current_step}")
    assert res6_out.current_step == "EQUIPMENT", f"Expected EQUIPMENT but got {res6_out.current_step}"
    print("[PASS] TEST 5 & 6 PASSED: Scheme opt-in branches correctly without asking premature demographics!")

    print("\n==================================================")
    print("ALL TEST CASES PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
