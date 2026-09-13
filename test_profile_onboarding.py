import sys
import json
from backend.chatbot import process_chat
from backend.models import ChatRequest, UserProfile

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("\n--- Test 3: Marathi Flow ---")
sess_mr = "test_sess_mr"
turns_mr = [
    "तुकाराम शिंदे",
    "नवीन व्यवसाय सुरू करणे",
    "३२",
    "पुरुष (Male)",
    "बारामती, पुणे, महाराष्ट्र",
    "१०वी पास (10th)",
    "पशुपालन व दुग्ध व्यवसाय",
    "३ वर्षे अनुभव",
    "गोठा / शेड आणि विहीर पाणी",
    "५० हजार"
]

history_mr = []
prof_mr = UserProfile(language="mr")

for i, t in enumerate(turns_mr, 1):
    req = ChatRequest(
        session_id=sess_mr,
        message=t,
        conversation_history=history_mr,
        profile=prof_mr,
        language="mr"
    )
    res = process_chat(req)
    print(f"Turn {i} (MR): '{t}' -> Step: {res.current_step} | Ready: {res.is_profile_ready}")
    print(f"   AI: {res.reply.splitlines()[0]}")
    print(f"   Suggestions: {res.suggested_quick_replies}")
    prof_mr = res.updated_profile

print("\nFinal Marathi Profile:")
print(json.dumps(prof_mr.model_dump(), indent=2, ensure_ascii=False))


print("\n--- Test 4: Hindi Flow ---")
sess_hi = "test_sess_hi"
turns_hi = [
    "सुरेश कुमार",
    "नया व्यवसाय शुरू करना",
    "26",
    "पुरुष (Male)",
    "कोल्हापुर, महाराष्ट्र",
    "12वीं पास (12th)",
    "सिलाई व गारमेंट",
    "2 साल का अनुभव",
    "दुकान / वाणिज्यिक स्थान",
    "1 लाख"
]

history_hi = []
prof_hi = UserProfile(language="hi")

for i, t in enumerate(turns_hi, 1):
    req = ChatRequest(
        session_id=sess_hi,
        message=t,
        conversation_history=history_hi,
        profile=prof_hi,
        language="hi"
    )
    res = process_chat(req)
    print(f"Turn {i} (HI): '{t}' -> Step: {res.current_step} | Ready: {res.is_profile_ready}")
    print(f"   AI: {res.reply.splitlines()[0]}")
    print(f"   Suggestions: {res.suggested_quick_replies}")
    prof_hi = res.updated_profile

print("\nFinal Hindi Profile:")
print(json.dumps(prof_hi.model_dump(), indent=2, ensure_ascii=False))
