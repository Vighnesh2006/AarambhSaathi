import urllib.request
import json
import time
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/chat"

def send_chat(session_id, msg, lang="en", history=[], profile={}):
    payload = {
        "session_id": session_id,
        "message": msg,
        "conversation_history": history,
        "profile": profile,
        "language": lang
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

print("\n--- TEST 1: MARATHI CONVERSATION FLOW ---")
sess_mr = f"sess_mr_{int(time.time())}"
prof_mr = {}
hist_mr = []
mr_messages = [
    "नमस्कार",
    "माझं नाव राहुल आहे",
    "मी बारामती येथे राहतो",
    "पुणे, महाराष्ट्र",
    "मी शेतकरी आहे",
    "मला जनावरांचा आणि दुग्ध व्यवसायाचा अनुभव आहे",
    "माझ्याकडे १ लाख रुपये आहेत",
    "माझ्याकडे गोठा आणि शेतजमीन आहे",
    "मला दुग्ध व्यवसाय सुरू करायचा आहे"
]

for msg in mr_messages:
    res = send_chat(sess_mr, msg, lang="mr", history=hist_mr, profile=prof_mr)
    print(f"USER (MR): {msg}")
    print(f"AI (MR):   {res.get('reply')}")
    print(f"STEP: {res.get('current_step')}, READY: {res.get('is_profile_ready')}")
    print("-" * 50)
    hist_mr.append({"role": "user", "content": msg})
    hist_mr.append({"role": "assistant", "content": res.get("reply")})
    prof_mr = res.get("updated_profile")

print("\n--- TEST 2: CAPITAL VALIDATION (User says 'I don't know') ---")
sess_val = f"sess_val_{int(time.time())}"
# Jump to capital step
init_prof = {
    "name": "Rahul",
    "location": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "occupation": "Farmer",
    "skills": ["Farming"],
    "experience": "Farming",
    "capital": None
}
res_val = send_chat(sess_val, "I don't know", lang="en", profile=init_prof)
print(f"USER: \"I don't know\"")
print(f"AI:   \"{res_val.get('reply')}\"")
print(f"CURRENT STEP: {res_val.get('current_step')} (Should remain 'capital')")
print(f"SUGGESTED REPLIES: {res_val.get('suggested_quick_replies')}")

print("\n--- TEST 3: MULTI-ATTRIBUTE EXTRACTION IN ONE MESSAGE ---")
sess_multi = f"sess_multi_{int(time.time())}"
multi_msg = "I am Rahul from Pune, Maharashtra. I am a farmer with cattle experience and I want to start dairy farming with 1 lakh capital and a cattle shed."
res_multi = send_chat(sess_multi, multi_msg, lang="en")
print(f"USER: \"{multi_msg}\"")
print(f"AI:   \"{res_multi.get('reply')}\"")
print(f"CURRENT STEP: {res_multi.get('current_step')}")
print(f"IS PROFILE READY: {res_multi.get('is_profile_ready')}")
print(f"EXTRACTED PROFILE: {json.dumps(res_multi.get('updated_profile'), indent=2)}")
