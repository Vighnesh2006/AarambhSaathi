import urllib.request
import json
import time
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/chat"

test_messages = [
    ("Turn 1", "Hello"),
    ("Turn 2", "My name is Rahul"),
    ("Turn 3", "I live in Pune"),
    ("Turn 4", "Pune, Maharashtra"),
    ("Turn 5", "I am a farmer"),
    ("Turn 6", "I have experience with cattle"),
    ("Turn 7", "I have ₹1 lakh"),
    ("Turn 8", "I have a cattle shed"),
    ("Turn 9", "I want to start dairy farming")
]

session_id = f"sess_{int(time.time())}"
print(f"============================================================")
print(f"STATEFUL MULTI-TURN CHATBOT TEST (Session: {session_id})")
print(f"============================================================\n")

history = []
current_profile = {}

for label, msg in test_messages:
    payload = {
        "session_id": session_id,
        "message": msg,
        "conversation_history": history,
        "profile": current_profile,
        "language": "en"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f">>> {label} | USER: \"{msg}\"")
            print(f"    AI REPLY: {res_data.get('reply')}")
            print(f"    CURRENT STEP: {res_data.get('current_step')}")
            print(f"    IS PROFILE READY: {res_data.get('is_profile_ready')}")
            prof = res_data.get('updated_profile', {})
            print(f"    PROFILE: name={prof.get('name')}, loc={prof.get('location')}, dist={prof.get('district')}, occ={prof.get('occupation')}, skills={prof.get('skills')}, cap={prof.get('capital')}, res={prof.get('resources')}, biz={prof.get('business_interest')}")
            print("-" * 60)
            
            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": res_data.get("reply")})
            current_profile = res_data.get("updated_profile")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")
        break

print("\nFinished Multi-Turn Test successfully.")
