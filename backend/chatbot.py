import json
import re
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from backend.config import GEMINI_API_KEY, DATA_DIR
from backend.models import UserProfile, ChatMessage, ChatRequest, ChatResponse

# Initialize Gemini if API key is present
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[Chatbot] Gemini configure error: {e}")

# In-Memory Session Storage
# Structure: { session_id: { "current_state": str, "profile": UserProfile, "language": str, "updated_at": datetime } }
SESSIONS: Dict[str, Dict[str, Any]] = {}

WORKFLOW_STATES = [
    "PERSONAL_NAME",
    "PERSONAL_PLACE",
    "PERSONAL_OCCUPATION",
    "BUSINESS_SKILLS",
    "BUSINESS_RESOURCES",
    "BUSINESS_CAPITAL",
    "BUSINESS_INTEREST",
    "PROFILE_CONFIRMATION",
    "RECOMMENDATION",
    "BUSINESS_SELECTION",
    "FEASIBILITY",
    "FINANCIAL",
    "SCHEME_OPT_IN",
    "SCHEME_PROFILE",
    "SCHEME_MATCHING",
    "EQUIPMENT",
    "SUPPLIER",
    "DPR",
    "COMPLETE"
]

def extract_capital_from_text(text: str) -> Optional[float]:
    """Helper regex to parse Indian capital formats in English, Hindi, Marathi."""
    t = text.lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "").strip()
    
    word_map = {
        "एक लाख": 100000.0, "१ लाख": 100000.0, "1 लाख": 100000.0,
        "दोन लाख": 200000.0, "२ लाख": 200000.0, "2 लाख": 200000.0,
        "दीड लाख": 150000.0, "डेढ़ लाख": 150000.0, "1.5 लाख": 150000.0,
        "तीन लाख": 300000.0, "३ लाख": 300000.0, "3 लाख": 300000.0,
        "पाच लाख": 500000.0, "५ लाख": 500000.0, "5 लाख": 500000.0,
        "पचास हजार": 50000.0, "पन्नास हजार": 50000.0, "५० हजार": 50000.0, "50 हजार": 50000.0,
        "एक लाख रुपये": 100000.0, "२५ हजार": 25000.0, "25 हजार": 25000.0, "पचीस हजार": 25000.0
    }
    for w, val in word_map.items():
        if w in t:
            return val

    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b', t)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000.0
    
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:k|thousand|hazaar|hazar)\b', t)
    if k_match:
        return float(k_match.group(1)) * 1000.0

    num_match = re.search(r'\b(\d{4,8})\b', t)
    if num_match:
        return float(num_match.group(1))
        
    return None

def clean_name_string(raw: str) -> str:
    val = raw.strip()
    patterns = [
        r'^(?:my\s+name\s+is|i\s+am|i\'m|myself)\s+',
        r'^(?:मेरा\s+नाम|नाम|मैं)\s+(?:है\s+)?',
        r'^(?:माझे\s+नाव|माझं\s+नाव|नाव|मी)\s+(?:आहे\s+)?',
    ]
    for p in patterns:
        val = re.sub(p, '', val, flags=re.IGNORECASE).strip()
    val = re.sub(r'[\.\,\!\?]+$', '', val).strip()
    val = re.sub(r'\s+(?:है|आहे)$', '', val).strip()
    return val.capitalize() if val else raw.strip()

def clean_location_string(raw: str) -> str:
    val = raw.strip()
    patterns = [
        r'^(?:i\s+live\s+in|i\s+stay\s+in|i\s+am\s+from|from|living\s+in|at)\s+',
        r'^(?:मैं\s+)?(?:रहता\s+हूँ|रहती\s+हूँ|से\s+हूँ|का\s+हूँ|में\s+रहता\s+हूँ)',
        r'^(?:मी\s+)?(?:येथील\s+आहे|येथे\s+राहतो|येथे\s+राहते|मध्ये\s+राहतो|गाव|गावाचे\s+नाव)\s*',
    ]
    for p in patterns:
        val = re.sub(p, '', val, flags=re.IGNORECASE).strip()
    val = re.sub(r'\b(?:में\s+रहता\s+हूँ|में\s+रहती\s+हूँ|से\s+हूँ|येथे\s+राहतो|येथे\s+राहते|मध्ये\s+राहतो)$', '', val).strip()
    val = re.sub(r'[\.\,\!\?]+$', '', val).strip()
    return val.capitalize() if val else raw.strip()

OTHER_INDIAN_STATES = {
    "Gujarat": ["surat", "ahmedabad", "vadodara", "rajkot", "gandhinagar"],
    "Karnataka": ["bangalore", "bengaluru", "belgaum", "mysore", "hubli"],
    "Madhya Pradesh": ["indore", "bhopal", "jabalpur", "gwalior", "ujjain"],
    "Rajasthan": ["jaipur", "jodhpur", "udaipur", "kota"],
    "Uttar Pradesh": ["lucknow", "kanpur", "varanasi", "agra"],
    "Bihar": ["patna", "gaya", "muzaffarpur"],
    "Telangana": ["hyderabad", "warangal"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai"]
}

def resolve_state_from_location(loc: str) -> str:
    if not loc:
        return "Maharashtra"
    l = loc.lower().strip()
    for state_name, city_list in OTHER_INDIAN_STATES.items():
        if any(c in l for c in city_list):
            return state_name
    return "Maharashtra"

def extract_entities_locally(user_msg: str, current_state: str) -> Dict[str, Any]:
    """Rule-based multi-entity extractor that extracts all available fields in parallel."""
    extracted = {}
    text_lower = user_msg.lower().strip()
    
    negative_words = ["i don't know", "dont know", "not sure", "pata nahi", "mahit nahi", "nahi", "no", "yes", "none", "hello", "hi", "namaskar", "namaste"]
    invalid_words = {"not", "sure", "planning", "looking", "here", "just", "trying", "working", "going", "ready"}

    # 1. Capital
    cap = extract_capital_from_text(user_msg)
    if cap is not None:
        extracted["capital"] = cap

    # 2. Name
    name_match = re.search(r'\b(?:my\s+name\s+is|i\s+am|i\'m|myself|मेरा\s+नाम|माझे\s+नाव|माझं\s+नाव)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)\b', user_msg, re.IGNORECASE)
    if name_match:
        cand = name_match.group(1).strip()
        if cand.lower() not in negative_words and cand.lower() not in invalid_words:
            extracted["name"] = cand.capitalize()
    elif current_state == "PERSONAL_NAME" and len(user_msg.split()) <= 4:
        cleaned = clean_name_string(user_msg)
        if cleaned.lower() not in negative_words and cleaned.lower() not in invalid_words:
            extracted["name"] = cleaned

    # 3. Location / Place
    loc_match = re.search(r'\b(?:from|living\s+in|staying\s+in|live\s+in|गाव|राहतो|राहते)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+(?:\s*,\s*[A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)?)\b', user_msg, re.IGNORECASE)
    if loc_match:
        raw_loc = loc_match.group(1).strip()
        if raw_loc.lower() not in negative_words:
            if "," in raw_loc:
                parts = [clean_location_string(p) for p in raw_loc.split(",")]
                extracted["location"] = parts[0]
                extracted["district"] = parts[0]
                extracted["state"] = parts[1] if len(parts) > 1 and parts[1] else resolve_state_from_location(parts[0])
            else:
                c_loc = clean_location_string(raw_loc)
                extracted["location"] = c_loc
                extracted["district"] = c_loc
                extracted["state"] = resolve_state_from_location(c_loc)
    elif current_state == "PERSONAL_PLACE":
        loc = clean_location_string(user_msg)
        if loc.lower() not in negative_words:
            if "," in loc:
                parts = [clean_location_string(p) for p in loc.split(",")]
                extracted["location"] = parts[0]
                extracted["district"] = parts[0]
                extracted["state"] = parts[1] if len(parts) > 1 and parts[1] else resolve_state_from_location(parts[0])
            else:
                extracted["location"] = loc
                extracted["district"] = loc
                extracted["state"] = resolve_state_from_location(loc)

    # 4. Occupation
    if "farm" in text_lower or "शेत" in text_lower or "किसान" in text_lower or "कृषि" in text_lower:
        extracted["occupation"] = "Farmer"
    elif "tailor" in text_lower or "शिलाई" in text_lower or "सिलाई" in text_lower:
        extracted["occupation"] = "Tailor"
    elif "student" in text_lower or "विद्यार्थी" in text_lower:
        extracted["occupation"] = "Student"
    elif "housewife" in text_lower or "गृहिणी" in text_lower or "homemaker" in text_lower:
        extracted["occupation"] = "Homemaker"
    elif current_state == "PERSONAL_OCCUPATION":
        occ = user_msg.strip()
        patterns = [r'^(?:i\s+am\s+a|i\s+am\s+an|i\s+am|i\s+work\s+as|working\s+as)\s+', r'^(?:मैं\s+एक|मैं|हम)\s+']
        for p in patterns:
            occ = re.sub(p, '', occ, flags=re.IGNORECASE).strip()
        occ = re.sub(r'[\.\,\!\?]+$', '', occ).strip()
        if occ.lower() not in negative_words:
            extracted["occupation"] = occ.capitalize()

    # 5. Skills & Experience
    skills_found = []
    if "cattle" in text_lower or "गाय" in text_lower or "म्हैस" in text_lower or "पशु" in text_lower or "cow" in text_lower or "animal" in text_lower:
        skills_found.append("Cattle Rearing & Animal Husbandry")
        extracted["experience"] = "Cattle handling and dairy experience"
    if "tailor" in text_lower or "शिलाई" in text_lower or "सिलाई" in text_lower or "sewing" in text_lower:
        skills_found.append("Tailoring & Garments")
    if "machine" in text_lower or "मशीन" in text_lower or "यंत्र" in text_lower:
        skills_found.append("Machinery Operation")
    if skills_found:
        extracted["skills"] = skills_found
    elif current_state == "BUSINESS_SKILLS" and text_lower not in negative_words:
        extracted["skills"] = [user_msg.strip()]
        extracted["experience"] = user_msg.strip()

    # 6. Resources
    res_list = []
    if "shed" in text_lower or "गोठा" in text_lower or "शेड" in text_lower or "बाड़ा" in text_lower:
        res_list.append("Cattle Shed / Storage Shed")
    if "land" in text_lower or "जमीन" in text_lower or "प्लॉट" in text_lower or "field" in text_lower:
        res_list.append("Agricultural Land")
    if "water" in text_lower or "पाणी" in text_lower or "पानी" in text_lower or "well" in text_lower or "borewell" in text_lower:
        res_list.append("Water Source / Borewell")
    if "electric" in text_lower or "वीज" in text_lower or "बिजली" in text_lower or "power" in text_lower:
        res_list.append("Electricity Connection")
    if "tractor" in text_lower or "ट्रॅक्टर" in text_lower or "vehicle" in text_lower:
        res_list.append("Transport / Tractor")
    if res_list:
        extracted["resources"] = res_list
    elif current_state == "BUSINESS_RESOURCES" and text_lower not in negative_words:
        extracted["resources"] = [user_msg.strip()]

    # 7. Business Interest
    if "dairy" in text_lower or "दूध" in text_lower or "दुग्ध" in text_lower or "गौपालन" in text_lower:
        extracted["business_interest"] = "Dairy Farming"
        if not extracted.get("skills"):
            extracted["skills"] = ["Cattle Rearing", "Milking", "Animal Husbandry"]
    elif "poultry" in text_lower or "कुक्कुट" in text_lower or "मुर्गी" in text_lower:
        extracted["business_interest"] = "Poultry Farming"
        if not extracted.get("skills"):
            extracted["skills"] = ["Poultry Management", "Bird Care"]
    elif "mushroom" in text_lower or "मशरूम" in text_lower or "अळिंबी" in text_lower:
        extracted["business_interest"] = "Mushroom Farming"
    elif "spice" in text_lower or "मसाला" in text_lower or "मसाले" in text_lower:
        extracted["business_interest"] = "Spice Processing & Packaging"
    elif "flour" in text_lower or "chakki" in text_lower or "चक्की" in text_lower or "पीठ गिरणी" in text_lower or "आटा" in text_lower:
        extracted["business_interest"] = "Mini Flour Mill (Atta Chakki)"
    elif "beekeep" in text_lower or "honey" in text_lower or "मध" in text_lower:
        extracted["business_interest"] = "Beekeeping & Honey Production"
    elif "vermicompost" in text_lower or "गांडूळ" in text_lower or "केंचुआ" in text_lower:
        extracted["business_interest"] = "Vermicompost Production"
    elif "tailor" in text_lower or "शिलाई" in text_lower or "garment" in text_lower:
        extracted["business_interest"] = "Rural Tailoring & Garment Unit"
    elif "goat" in text_lower or "शेळी" in text_lower or "बकरी" in text_lower:
        extracted["business_interest"] = "Goat Rearing & Breeding"
    elif current_state == "BUSINESS_INTEREST" and text_lower not in negative_words:
        extracted["business_interest"] = user_msg.strip()

    # 8. Scheme Demographics (if in SCHEME_PROFILE state)
    if current_state == "SCHEME_PROFILE":
        if "female" in text_lower or "woman" in text_lower or "महिला" in text_lower or "स्त्री" in text_lower:
            extracted["gender"] = "Female"
        elif "male" in text_lower or "man" in text_lower or "पुरुष" in text_lower:
            extracted["gender"] = "Male"
            
        if "obc" in text_lower:
            extracted["category"] = "OBC"
        elif "sc" in text_lower or " अनुसूचित जाती" in text_lower:
            extracted["category"] = "SC"
        elif "st" in text_lower or "अनुसूचित जमाती" in text_lower:
            extracted["category"] = "ST"
        elif "general" in text_lower or "ओपन" in text_lower or "open" in text_lower:
            extracted["category"] = "General"

    return extracted

def merge_profile_entities(existing: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
    d = existing.model_dump()
    for k, v in new_data.items():
        if v is not None and v != "" and v != []:
            if k in ["skills", "resources", "constraints"]:
                curr = d.get(k, []) or []
                if isinstance(v, list):
                    combined = list(dict.fromkeys(curr + [str(item).strip() for item in v if str(item).strip()]))
                    d[k] = combined
                elif isinstance(v, str) and v.strip() and v.strip() not in curr:
                    d[k] = curr + [v.strip()]
            else:
                d[k] = v
    return UserProfile(**d)

def determine_current_state(p: UserProfile, previous_state: str = "PERSONAL_NAME") -> str:
    """
    Determines next state strictly based on profile completion rules.
    Never re-asks fields already populated in UserProfile.
    """
    if not p.name or not str(p.name).strip():
        return "PERSONAL_NAME"

    if p.location and str(p.location).strip():
        if not p.district:
            p.district = str(p.location).strip()
        if not p.state:
            p.state = resolve_state_from_location(str(p.location).strip())

    if not p.location or not str(p.location).strip():
        return "PERSONAL_PLACE"

    if not p.occupation or not str(p.occupation).strip():
        return "PERSONAL_OCCUPATION"

    if (not p.skills or len(p.skills) == 0) and (not p.experience or not str(p.experience).strip()):
        return "BUSINESS_SKILLS"

    if not p.resources or len(p.resources) == 0:
        return "BUSINESS_RESOURCES"

    if p.capital is None:
        return "BUSINESS_CAPITAL"

    if not p.business_interest or not str(p.business_interest).strip():
        return "BUSINESS_INTEREST"

    # All onboarding profile attributes collected!
    if previous_state in ["PERSONAL_NAME", "PERSONAL_PLACE", "PERSONAL_OCCUPATION", "BUSINESS_SKILLS", "BUSINESS_RESOURCES", "BUSINESS_CAPITAL", "BUSINESS_INTEREST"]:
        return "PROFILE_CONFIRMATION"

    return previous_state or "PROFILE_CONFIRMATION"

def build_state_response(
    state: str,
    profile: UserProfile,
    extracted: Dict[str, Any],
    lang: str,
    user_msg: str
) -> (str, List[str]):
    name = profile.name or "Friend"
    loc = profile.location or profile.district or "your village"
    occ = profile.occupation or "entrepreneur"
    cap_val = f"₹{int(profile.capital):,}" if profile.capital is not None else "₹1,00,000"
    skills_text = ", ".join(profile.skills[:2]) if profile.skills else "general experience"
    res_text = ", ".join(profile.resources[:2]) if profile.resources else "standard setup"
    b_int = profile.business_interest or "Rural Business"

    quick_replies = []

    if state == "PERSONAL_NAME":
        if lang == "mr":
            reply = "नमस्कार! 👋 मी 'आरंभ साथी' आहे — तुमचा हक्काचा ग्रामीण उद्योग व स्वयंरोजगार सल्लागार.\n\nतुमच्या गावात कमी भांडवलात यशस्वी व फायदेशीर व्यवसाय सुरू करण्यासाठी मी तुम्हाला मार्गदर्शन करेन. चला सुरुवात करूया, कृपया तुमचे **पूर्ण नाव** काय आहे?"
        elif lang == "hi":
            reply = "नमस्कार! 👋 मैं 'आरंभ साथी' हूँ — आपका ग्रामीण व्यवसाय एवं स्वरोजगार सलाहकार।\n\nकम लागत में अपने गांव में सफल व्यवसाय स्थापित करने के लिए मैं आपका मार्गदर्शन करूंगा। आइए शुरुआत करें, कृपया अपना **पूरा नाम** बताएं?"
        else:
            reply = "Namaste! 👋 I am 'Aarambh Saathi' — your dedicated Rural Business & Micro-Enterprise Advisor.\n\nI am here to guide you step-by-step to choose, setup, and launch a profitable business in your village. Let's begin, may I know your **full name**?"
        quick_replies = []  # No sample name suggestions on first message!

    elif state == "PERSONAL_PLACE":
        if lang == "mr":
            reply = f"छान वाटले भेटून, **{name}** जी! 📍 स्थानिक बाजारपेठ आणि ग्राहक मागणीचा अभ्यास करण्यासाठी मला तुमचे स्थान आवश्यक आहे.\n\nतुम्ही कोणत्या **गावात, तालुक्यात किंवा जिल्ह्यात** राहता?"
            quick_replies = ["पुणे", "सातारा", "बारामती", "कोल्हापूर"]
        elif lang == "hi":
            reply = f"आपसे मिलकर खुशी हुई, **{name}** जी! 📍 स्थानीय बाजार की मांग और आपूर्ति को समझने के लिए आपका क्षेत्र जानना जरूरी है।\n\nआप किस **गांव, तहसील या जिले** में रहते हैं?"
            quick_replies = ["पुणे", "सतारा", "बारामती", "कोल्हापुर"]
        else:
            reply = f"Pleased to connect with you, **{name}**! 📍 Knowing your local area helps me analyze raw material availability and village market demand.\n\nWhich **village, town, or district** do you live in?"
            quick_replies = ["Pune", "Satara", "Baramati", "Kolhapur"]

    elif state == "PERSONAL_OCCUPATION":
        if lang == "mr":
            reply = f"धन्यवाद, **{name}** जी! **{loc}** परिसर हा व्यवसायासाठी अतिशय उत्तम भाग आहे. 🌾\n\nसध्या तुम्ही काय काम किंवा व्यवसाय करता? (उदा. शेती, रोजंदारी कामगार, छोटे व्यापारी, गृहिणी, किंवा कुशल कारागीर)"
            quick_replies = ["शेतकरी", "मजूर / कामगार", "दुकानदार / छोटे व्यापारी", "गृहिणी"]
        elif lang == "hi":
            reply = f"धन्यवाद, **{name}** जी! **{loc}** में नए छोटे उद्यमों के लिए बेहतरीन संभावनाएं हैं। 🌾\n\nवर्तमान में आप क्या काम या व्यवसाय करते हैं? (जैसे खेती, मजदूरी, छोटी दुकान, गृहिणी, या कारीगर)"
            quick_replies = ["किसान", "मजदूर / कामगार", "दुकानदार / छोटा व्यापारी", "गृहिणी"]
        else:
            reply = f"Thank you, **{name}**! **{loc}** is a promising cluster for rural enterprise. 🌾\n\nWhat work or occupation do you currently do? (e.g., Farmer, Daily wage worker, Retail shopkeeper, Skilled craftsman, Homemaker)"
            quick_replies = ["Farmer", "Daily Wage Labourer", "Retail Shopkeeper", "Homemaker"]

    elif state == "BUSINESS_SKILLS":
        if lang == "mr":
            reply = f"उत्तम! **{occ}** म्हणून तुमचा अनुभव नवीन व्यवसायासाठी मोठा पाया ठरेल. 💡\n\nतुमच्याकडे कोणती **प्रात्यक्षिक कौशल्ये किंवा कामाचा अनुभव** आहे? (उदा. पशुपालन, सिलाई/टेलरिंग, पीक व्यवस्थापन, यंत्रसामग्री चालवणे, वेल्डिंग)"
            quick_replies = ["पशुपालन व दुग्ध व्यवसाय", "सिलाई व टेलरिंग", "शेती व पीक काळजी", "मशिनरी चालवणे"]
        elif lang == "hi":
            reply = f"बहुत बढ़िया! **{occ}** के रूप में आपका व्यावहारिक अनुभव बहुत काम आएगा। 💡\n\nआपके पास कौन सा **व्यावहारिक कौशल या अनुभव** है? (जैसे पशुपालन, सिलाई, फसल प्रबंधन, मशीन संचालन, वेल्डिंग)"
            quick_replies = ["पशुपालन व डेयरी", "सिलाई व दर्जी काम", "खेती व फसल देखभाल", "मशीन संचालन"]
        else:
            reply = f"Great! Working as a **{occ}** provides a strong practical foundation. 💡\n\nWhat specific **hands-on skills or experience** do you possess? (e.g., Cattle/livestock care, Tailoring, Crop cultivation, Machinery operation, Electrician/welding)"
            quick_replies = ["Livestock & Dairy Care", "Tailoring & Stitching", "Farming & Crop Care", "Machinery Operation"]

    elif state == "BUSINESS_RESOURCES":
        if lang == "mr":
            reply = f"छान! **{skills_text}** या कौशल्याचा व्यवसाय निवडीत मोठा फायदा होईल. 🚜\n\nतुमच्याकडे आधीपासून कोणती **साधने किंवा जागा उपलब्ध** आहे? (उदा. १ एकर शेती, गोठा, मोकळी दुकान जागा, बोअरवेल पाणी, ट्रॅक्टर, वाहन)"
            quick_replies = ["जमीन व पाण्याची सोय", "गोठा / पशू शेड", "मोकळी दुकान जागा", "काहीही साधने नाहीत"]
        elif lang == "hi":
            reply = f"बहुत अच्छा! **{skills_text}** का कौशल व्यवसाय में आपकी सफलता की संभावना बढ़ाएगा। 🚜\n\nआपके पास पहले से क्या **साधन या स्थान उपलब्ध** है? (जैसे जमीन, पशु शेड, दुकान, बोरवेल पानी, वाहन, या कुछ नहीं)"
            quick_replies = ["ज़मीन व पानी का स्रोत", "पशु शेड / गोठा", "छोटी दुकान की जगह", "कोई साधन उपलब्ध नहीं"]
        else:
            reply = f"Understood! Your background in **{skills_text}** will be a key competitive advantage. 🚜\n\nWhat **physical resources or assets** do you currently have available? (e.g., Own land, Cattle shed, Shop counter, Water source, Vehicle, or None)"
            quick_replies = ["Land & Water Source", "Cattle Shed / Gotha", "Small Shop Space", "No Prior Assets"]

    elif state == "BUSINESS_CAPITAL":
        if lang == "mr":
            reply = f"व्यवसायाचे योग्य बजेट आखण्यासाठी: नवीन उद्योगात तुम्ही स्वतःचे किती **भांडवल (पैसे)** गुंतवू शकता? 💰\n\n(उदा. ₹५० हजार, ₹१ लाख, ₹२.५ लाख, ₹५ लाख)"
            quick_replies = ["₹५०,०००", "₹१ लाख (₹१,००,०००)", "₹२.५ लाख (₹२,५०,०००)", "₹५ लाख"]
        elif lang == "hi":
            reply = f"व्यवसाय का सही बजट तैयार करने के लिए: नए उद्यम में आप अपनी बचत से लगभग कितनी **पूंजी** निवेश कर सकते हैं? 💰\n\n(जैसे ₹50 हजार, ₹1 लाख, ₹2.5 लाख, ₹5 लाख)"
            quick_replies = ["₹50,000", "₹1 लाख (₹1,00,000)", "₹2.5 लाख (₹2,50,000)", "₹5 लाख"]
        else:
            reply = f"To structure a realistic project budget: approximately how much **own capital/savings** can you invest to start? 💰\n\n(e.g., ₹50,000, ₹1 Lakh, ₹2.5 Lakhs, ₹5 Lakhs)"
            quick_replies = ["₹50,000", "₹1 Lakh (₹1,00,000)", "₹2.5 Lakhs (₹2,50,000)", "₹5 Lakhs"]

    elif state == "BUSINESS_INTEREST":
        if lang == "mr":
            reply = f"उत्तम! **{cap_val}** चे भांडवल आणि **{skills_text}** चे कौशल्य यासह तुमच्याकडे उत्तम संधी आहे. 🎯\n\nतुमच्या मनात आधीपासून कोणता **विशिष्ट व्यवसाय** आहे, की मी तुम्हाला **{loc}** साठी सर्वोत्कृष्ट ३ पर्याय सुचवू?"
            quick_replies = ["दुग्ध व्यवसाय", "मशरूम शेती", "कुक्कुटपालन (पोल्ट्री)", "सर्वोत्कृष्ट ३ पर्याय सुचवा"]
        elif lang == "hi":
            reply = f"शानदार! **{cap_val}** की पूंजी और **{skills_text}** के कौशल के साथ आपके लिए बेहतरीन अवसर हैं। 🎯\n\nक्या आपके मन में पहले से कोई **विशेष व्यवसाय** है, या मैं आपको **{loc}** के लिए सर्वश्रेष्ठ 3 विकल्प सुझाऊं?"
            quick_replies = ["डेयरी फार्मिंग", "मशरूम खेती", "पोल्ट्री फार्मिंग", "सर्वश्रेष्ठ 3 विकल्प सुझाएं"]
        else:
            reply = f"Excellent! With **{cap_val}** capital and skills in **{skills_text}**, you have strong business potential. 🎯\n\nDo you already have a **specific business idea** in mind, or would you like me to recommend the top 3 best-suited options for **{loc}**?"
            quick_replies = ["Dairy Farming", "Mushroom Farming", "Poultry Farming", "Suggest Best 3 Options"]

    elif state == "PROFILE_CONFIRMATION":
        if lang == "mr":
            reply = f"📋 **तुमचा व्यावसायिक प्रोफाइल सारांश:**\n\n• **नाव:** {name}\n• **ठिकाण:** {loc}, {profile.state or 'Maharashtra'}\n• **सध्याचा व्यवसाय:** {occ}\n• **प्रमुख कौशल्ये:** {skills_text}\n• **उपलब्ध साधने:** {res_text}\n• **स्वतःचे भांडवल:** {cap_val}\n• **इच्छित क्षेत्र:** {b_int}\n\nमी या माहितीच्या आधारे तुमचे व्यवसाय विश्लेषण सुरू करू का?"
            quick_replies = ["होय, शिफारसी दाखवा", "माहिती बदला"]
        elif lang == "hi":
            reply = f"📋 **आपका व्यावसायिक प्रोफाइल सारांश:**\n\n• **नाम:** {name}\n• **स्थान:** {loc}, {profile.state or 'Maharashtra'}\n• **वर्तमान व्यवसाय:** {occ}\n• **प्रमुख कौशल:** {skills_text}\n• **उपलब्ध संसाधन:** {res_text}\n• **निवेश पूंजी:** {cap_val}\n• **इच्छित क्षेत्र:** {b_int}\n\nक्या मैं इस जानकारी के आधार पर आपका व्यवसाय विश्लेषण शुरू करूं?"
            quick_replies = ["हां, सिफारिशें दिखाएं", "प्रोफ़ाइल बदलें"]
        else:
            reply = f"📋 **Your Verified Business Profile Summary:**\n\n• **Name:** {name}\n• **Location:** {loc}, {profile.state or 'Maharashtra'}\n• **Current Occupation:** {occ}\n• **Primary Skills:** {skills_text}\n• **Available Assets:** {res_text}\n• **Investment Capital:** {cap_val}\n• **Target Business Interest:** {b_int}\n\nShall I proceed with calculating your top business recommendations?"
            quick_replies = ["Yes, Show Recommendations", "Edit Profile"]

    elif state == "RECOMMENDATION":
        from backend.recommendation import get_recommendations
        rec_res = get_recommendations(profile, top_n=3)
        recs = rec_res.recommendations
        
        items_en = [f"**{i+1}. {r.business_name}** (Match Score: {r.overall_score:.0f}/100)\n   • **Required Investment:** ₹{r.required_investment:,.0f}\n   • **Why Recommended:** {r.why_matches[0] if r.why_matches else 'Strong local demand match'}" for i, r in enumerate(recs)]
        items_hi = [f"**{i+1}. {r.business_name}** (मैच स्कोर: {r.overall_score:.0f}/100)\n   • **आवश्यक निवेश:** ₹{r.required_investment:,.0f}\n   • **मुख्य कारण:** {r.why_matches[0] if r.why_matches else 'स्थानीय बाजार मांग'}" for i, r in enumerate(recs)]
        items_mr = [f"**{i+1}. {r.business_name}** (सुसंगतता गुण: {r.overall_score:.0f}/100)\n   • **अंदाजे भांडवल:** ₹{r.required_investment:,.0f}\n   • **शिफारशीचे कारण:** {r.why_matches[0] if r.why_matches else 'स्थानिक बाजारपेठ संधी'}" for i, r in enumerate(recs)]

        if lang == "mr":
            reply = f"🏆 **{name} जी, तुमच्या प्रोफाइलनुसार सर्वोत्कृष्ट ३ शिफारस केलेले व्यवसाय:**\n\n" + "\n\n".join(items_mr) + "\n\nतुम्ही कोणत्या व्यवसायाचे सविस्तर मशिनरी, सप्लायर आणि बँक कर्ज नियोजन पाहू इच्छिता?"
        elif lang == "hi":
            reply = f"🏆 **{name} जी, आपके प्रोफाइल के अनुसार सर्वश्रेष्ठ 3 अनुशंसित व्यवसाय:**\n\n" + "\n\n".join(items_hi) + "\n\nआप किस व्यवसाय का मशीनरी, सप्लायर और बैंक ऋण विवरण देखना चाहते हैं?"
        else:
            reply = f"🏆 **{name}, here are your Top 3 Data-Backed Business Recommendations:**\n\n" + "\n\n".join(items_en) + "\n\nWhich business would you like to select to view equipment, suppliers, and financial viability?"

        quick_replies = [r.business_name for r in recs]

    elif state == "EQUIPMENT_SUPPLIER":
        biz_name = profile.business_interest or "Selected Business"
        from backend.supplier_sources.local_database import LocalDatabaseSource
        source = LocalDatabaseSource()
        all_machines = source.load_all_machines()
        all_suppliers = source.load_all_suppliers()
        
        # Match machines by business interest keywords or category
        matched_m = []
        biz_words = [w.lower() for w in biz_name.split() if len(w) > 3]
        for m in all_machines:
            m_cats = [c.lower() for c in m.get("business_categories", [])]
            m_name = m.get("machine_name", "").lower()
            if any(w in m_name for w in biz_words) or any(any(w in cat for w in biz_words) for cat in m_cats):
                matched_m.append(m)
        
        if not matched_m:
            matched_m = all_machines[:3]
            
        matched_machine_ids = set(m.get("machine_id") for m in matched_m)
        matched_suppliers = [s for s in all_suppliers if any(mid in matched_machine_ids for mid in s.get("machine_ids", []))]
        if not matched_suppliers:
            matched_suppliers = all_suppliers[:2]

        # Format Machines for Chatbox
        m_items_en = []
        m_items_hi = []
        m_items_mr = []
        for idx, m in enumerate(matched_m[:3], 1):
            m_name = m.get('machine_name', 'Machinery')
            p_min = m.get('estimated_price_min', 25000)
            p_max = m.get('estimated_price_max', 75000)
            price_en = f"₹{p_min:,.0f} - ₹{p_max:,.0f}"
            price_mr = f"₹{p_min:,.0f} ते ₹{p_max:,.0f}"
            cap = m.get('capacity', 'Standard')
            purp = m.get('purpose', 'Production & Processing')
            
            m_items_en.append(f"{idx}. **{m_name}**\n   • **Function:** {purp}\n   • **Capacity:** {cap} | **Est. Price:** {price_en}")
            m_items_hi.append(f"{idx}. **{m_name}**\n   • **उद्देश्य:** {purp}\n   • **क्षमता:** {cap} | **अनुमानित मूल्य:** {price_en}")
            m_items_mr.append(f"{idx}. **{m_name}**\n   • **उद्दिष्ट:** {purp}\n   • **क्षमता:** {cap} | **अंदाजे किंमत:** {price_mr}")

        # Format Suppliers for Chatbox
        s_items_en = []
        s_items_hi = []
        s_items_mr = []
        for idx, s in enumerate(matched_suppliers[:2], 1):
            s_name = s.get('supplier_name', 'Verified Supplier')
            loc = f"{s.get('location', s.get('city', 'Pune'))}, {s.get('district', 'Pune')}, {s.get('state', 'Maharashtra')}"
            phone = s.get('contact', '+91 98220 12345')
            if isinstance(phone, dict):
                phone = phone.get('phone', '+91 98220 12345')
            p_range = s.get('price_range', 'Competitive MSME Rates')
            src = s.get('source', 'DIC / MSME Empanelled Directory')

            s_items_en.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **Location:** {loc}\n   • 📞 **Contact Phone:** `{phone}`\n   • 🏷️ **Price Range:** {p_range}\n   • ⚙️ **Services:** Free Installation, Warranty & Demo Support (`{src}`)")
            s_items_hi.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **स्थान:** {loc}\n   • 📞 **संपर्क नंबर:** `{phone}`\n   • 🏷️ **मूल्य सीमा:** {p_range}\n   • ⚙️ **सेवाएं:** निःशुल्क इंस्टॉलेशन, वारंटी एवं प्रशिक्षण (`{src}`)")
            s_items_mr.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **ठिकाण:** {loc}\n   • 📞 **संपर्क क्रमांक:** `{phone}`\n   • 🏷️ **किंमत श्रेणी:** {p_range}\n   • ⚙️ **सुविधा:** मोफत इन्स्टॉलेशन, वॉरंटी व प्रशिक्षण (`{src}`)")

        machines_text_en = "\n\n".join(m_items_en)
        machines_text_hi = "\n\n".join(m_items_hi)
        machines_text_mr = "\n\n".join(m_items_mr)

        suppliers_text_en = "\n\n".join(s_items_en)
        suppliers_text_hi = "\n\n".join(s_items_hi)
        suppliers_text_mr = "\n\n".join(s_items_mr)

        if lang == "mr":
            reply = f"⚙️ **'{biz_name}' साठी आवश्यक यंत्रसामग्री आणि सप्लायरची विस्तृत यादी:**\n\n🛠️ **आवश्यक यंत्रसामग्री व तांत्रिक तपशील:**\n{machines_text_mr}\n\n🏪 **प्रमाणित स्थानिक सप्लायर्स (विक्रेते):**\n{suppliers_text_mr}\n\n💰 **भांडवल गुंतवणूक विचारणा:**\nया यंत्रसामग्री व सेटअपसाठी तुम्ही स्वतःचे किती **भांडवल (पैसे)** गुंतवू शकता? (उदा. ₹५० हजार, ₹१ लाख, ₹२ लाख)"
            quick_replies = ["₹५०,०००", "₹१ लाख (₹१,००,०००)", "₹२ लाख (₹२,००,०००)", "₹५ लाख"]
        elif lang == "hi":
            reply = f"⚙️ **'{biz_name}' के लिए आवश्यक मशीनरी एवं सत्यापित सप्लायर सूची:**\n\n🛠️ **अनुशंसित मशीनरी व उपकरण विवरण:**\n{machines_text_hi}\n\n🏪 **सत्यापित स्थानीय सप्लायर (विक्रेता):**\n{suppliers_text_hi}\n\n💰 **निवेश पूंजी पूछताछ:**\nइस मशीनरी सेटअप के लिए आप अपनी बचत से कितना **निवेश** कर सकते हैं? (जैसे ₹50 हजार, ₹1 लाख, ₹2 लाख)"
            quick_replies = ["₹50,000", "₹1 लाख (₹1,00,000)", "₹2 लाख (₹2,00,000)", "₹5 लाख"]
        else:
            reply = f"⚙️ **Machinery & Verified Local Supplier Directory for '{biz_name}':**\n\n🛠️ **Required Equipment & Specifications:**\n{machines_text_en}\n\n🏪 **Verified District & Regional Suppliers:**\n{suppliers_text_en}\n\n💰 **Investment Capital Inquiry:**\nBased on this equipment list, how much money can you invest as your **own capital contribution**? (e.g., ₹50,000, ₹1 Lakh, ₹2 Lakhs)"
            quick_replies = ["₹50,000", "₹1 Lakh (₹1,00,000)", "₹2 Lakhs (₹2,00,000)", "₹5 Lakhs"]

    elif state == "FINANCIAL":
        biz_name = profile.business_interest or "Selected Business"
        user_cap = profile.capital or 100000.0
        project_cost = max(150000.0, user_cap * 1.5)
        loan_needed = max(0.0, project_cost - user_cap)
        monthly_profit = round(project_cost * 0.18, -2)
        
        if lang == "mr":
            reply = f"📊 **'{biz_name}' चे आर्थिक नियोजन व नफा विश्लेषण:**\n\n• **अंदाजे एकूण प्रकल्प खर्च:** ₹{project_cost:,.0f}\n• **तुमचे स्वतःचे भांडवल:** ₹{user_cap:,.0f}\n• **बँक कर्ज / अनुदान सहाय्य:** ₹{loan_needed:,.0f}\n• **अंदाजे मासिक निव्वळ नफा:** ₹{monthly_profit:,.0f}\n• **भांडवल परतफेड कालावधी:** १२ ते १८ महिने\n\n💡 **शासकीय योजना विचारणा:**\nतुम्हाला या व्यवसायासाठी केंद्र व राज्य सरकारच्या **PMEGP, मुद्रा कर्ज, NABARD** अनुदानाची पात्रता तपासायची आहे का?"
            quick_replies = ["होय, योजना पहा", "नाही, पुढे जा"]
        elif lang == "hi":
            reply = f"📊 **'{biz_name}' का वित्तीय नियोजन एवं लाभ विश्लेषण:**\n\n• **अनुमानित कुल परियोजना लागत:** ₹{project_cost:,.0f}\n• **आपकी स्वयं की पूंजी:** ₹{user_cap:,.0f}\n• **बैंक ऋण / सब्सिडी सहायता:** ₹{loan_needed:,.0f}\n• **अनुमानित मासिक शुद्ध लाभ:** ₹{monthly_profit:,.0f}\n• **पूंजी वापसी समय:** 12 से 18 महीने\n\n💡 **सरकारी योजना पूछताछ:**\nक्या आप इस व्यवसाय के लिए **PMEGP, मुद्रा, NABARD** योजनाओं के तहत सब्सिडी की पात्रता जांचना चाहते हैं?"
            quick_replies = ["हां, योजनाएं देखें", "नहीं, आगे बढ़ें"]
        else:
            reply = f"📊 **Financial Structuring & Profit Viability for '{biz_name}':**\n\n• **Estimated Total Project Cost:** ₹{project_cost:,.0f}\n• **Your Own Capital Contribution:** ₹{user_cap:,.0f}\n• **Required Bank Loan / Subsidy:** ₹{loan_needed:,.0f}\n• **Estimated Monthly Net Profit:** ₹{monthly_profit:,.0f}/month\n• **Payback Period:** 12 to 18 months\n\n💡 **Government Scheme Inquiry:**\nWould you like to check matching government schemes & subsidies (PMEGP, MUDRA, NABARD) for your business?"
            quick_replies = ["Yes, Check Schemes", "No, Skip Schemes"]

    elif state == "SCHEME_OPT_IN":
        if lang == "mr":
            reply = f"💡 **विशेष शासकीय योजना व अनुदान (Subsidy):**\n\nतुम्हाला या व्यवसायासाठी केंद्र व राज्य सरकारच्या **PMEGP, मुद्रा कर्ज, NABARD किंवा Standup India** योजनेअंतर्गत २५% ते ३५% अनुदानाची पात्रता तपासायची आहे का?"
            quick_replies = ["होय, योजना तपासा", "नाही, पुढे जा"]
        elif lang == "hi":
            reply = f"💡 **विशेष सरकारी योजना और सब्सिडी:**\n\nक्या आप इस व्यवसाय के लिए केंद्र एवं राज्य सरकार की **PMEGP, मुद्रा, NABARD या स्टैंडअप इंडिया** योजनाओं के तहत 25% से 35% सब्सिडी की पात्रता जांचना चाहते हैं?"
            quick_replies = ["हां, योजनाएं देखें", "नहीं, आगे बढ़ें"]
        else:
            reply = f"💡 **Government Subsidy & Support Schemes:**\n\nWould you like to check your eligibility for government subsidy schemes like **PMEGP (25%-35% Subsidy), MUDRA Loan, or NABARD** for this business?"
            quick_replies = ["Yes, Check Schemes", "No, Skip Schemes"]

    elif state == "SCHEME_PROFILE":
        if lang == "mr":
            reply = f"अनुदान (Subsidy) ची अचूक टक्केवारी ठरवण्यासाठी, कृपया तुमचे **लिंग (महिला/पुरुष)** आणि **सामाजिक प्रवर्ग (General / OBC / SC / ST)** सांगा."
            quick_replies = ["महिला, General", "महिला, OBC", "पुरुष, General", "पुरुष, OBC", "पुरुष, SC/ST"]
        elif lang == "hi":
            reply = f"सटीक सब्सिडी राशि और पात्रता के लिए, कृपया अपना **लिंग (महिला/पुरुष)** और **सामाजिक वर्ग (General / OBC / SC / ST)** बताएं।"
            quick_replies = ["महिला, General", "महिला, OBC", "पुरुष, General", "पुरुष, OBC", "पुरुष, SC/ST"]
        else:
            reply = f"To calculate your exact subsidy entitlement percentage, please specify your **gender (Female/Male)** and **social category (General / OBC / SC / ST)**."
            quick_replies = ["Female, General", "Female, OBC", "Male, General", "Male, OBC", "Male, SC/ST"]

    elif state == "SCHEME_MATCHING":
        cat = profile.category or "General"
        gen = profile.gender or "Male"
        sub_pct = "35%" if (gen == "Female" or cat in ["OBC", "SC", "ST"]) else "25%"
        
        if lang == "mr":
            reply = f"🏛️ **तुमच्यासाठी पात्र शासकीय योजना व अनुदान:**\n\n1. **PMEGP (Prime Minister Employment Generation Programme)**\n   • **पात्र अनुदान:** {sub_pct} पर्यंत केंद्र सरकार कडून कर्जमाफी/सबसिडी\n   • **कर्ज मर्यादा:** ₹२५ लाखांपर्यंत प्रकल्प खर्च\n\n2. **PM-MUDRA Yojana (Kishore / Tarun Loan)**\n   • **कर्ज सहाय्य:** ₹५०,००० ते ₹१० लाख (विनातारण कर्ज)\n\n🎉 **अभिनंदन! तुमचे ९०-दिवसांचे सविस्तर व्यवसाय नियोजन तयार आहे.**"
            quick_replies = ["DPR अहवाल पहा", "सारांश डाउनलोड करा"]
        elif lang == "hi":
            reply = f"🏛️ **आपके लिए पात्र सरकारी योजनाएं और सब्सिडी:**\n\n1. **PMEGP (प्रधानमंत्री रोजगार सृजन कार्यक्रम)**\n   • **पात्र सब्सिडी:** {sub_pct} तक केंद्र सरकार द्वारा अनुदान\n   • **ऋण सीमा:** ₹25 लाख तक की परियोजना\n\n2. **PM-MUDRA योजना (किशोर / तरुण ऋण)**\n   • **ऋण सहायता:** ₹50,000 से ₹10 लाख (बिना गारंटी ऋण)\n\n🎉 **बधाई हो! आपका 90-दिवसीय विस्तृत बिजनेस प्लान तैयार है।**"
            quick_replies = ["DPR रिपोर्ट देखें", "सारांश डाउनलोड करें"]
        else:
            reply = f"🏛️ **Matched Government Subsidy Schemes for You:**\n\n1. **PMEGP (Prime Minister's Employment Generation Programme)**\n   • **Eligible Subsidy:** Up to {sub_pct} Capital Subsidy\n   • **Max Loan Limit:** Up to ₹25 Lakhs project cost\n\n2. **PM-MUDRA Loan Scheme**\n   • **Credit Support:** ₹50,000 to ₹10 Lakhs collateral-free credit\n\n🎉 **Congratulations! Your 90-Day Comprehensive DPR Business Plan is fully generated!**"
            quick_replies = ["View DPR Report", "Download Summary"]

    else:
        reply = f"Thank you {name}! Your advisory workflow is fully active."
        quick_replies = ["View DPR Report", "Check Suppliers", "Edit Profile"]

    return reply, quick_replies

def process_chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())[:12]
    user_msg = (request.message or "").strip()
    req_lang = request.language or "en"

    if session_id not in SESSIONS:
        initial_profile = request.profile or UserProfile(language=req_lang)
        initial_state = determine_current_state(initial_profile, "PERSONAL_NAME")
        SESSIONS[session_id] = {
            "current_state": initial_state,
            "profile": initial_profile,
            "language": req_lang,
            "created_at": datetime.now()
        }
    
    session = SESSIONS[session_id]
    current_profile = session.get("profile", UserProfile())
    current_state = session.get("current_state", "PERSONAL_NAME")
    session_lang = req_lang or session.get("language", "en")

    if request.profile:
        current_profile = merge_profile_entities(current_profile, request.profile.model_dump())
        session["profile"] = current_profile

    # Language detection
    if re.search(r'[\u0900-\u097F]', user_msg):
        if any(w in user_msg for w in ["आहे", "नाही", "माझं", "माझे", "करायचा", "पाहिजे", "गावात", "भांडवल"]):
            session_lang = "mr"
        elif any(w in user_msg for w in ["है", "नहीं", "मेरा", "मेरी", "करना", "चाहिए", "गांव", "पूंजी"]):
            session_lang = "hi"

    session["language"] = session_lang
    current_profile.language = session_lang

    # 1. Handle State Transitions Triggered by Buttons/Commands
    msg_lower = user_msg.lower()
    if current_state == "PROFILE_CONFIRMATION":
        if any(k in msg_lower for k in ["yes", "continue", "confirm", "होय", "सही", "पुढे"]):
            current_state = "RECOMMENDATION"
        elif any(k in msg_lower for k in ["edit", "change", "बदल"]):
            current_state = "PERSONAL_NAME"
            current_profile.name = None

    elif current_state in ["RECOMMENDATION", "BUSINESS_SELECTION"]:
        from backend.database import load_businesses_data
        from backend.recommendation import get_recommendations
        
        selected_name = None
        businesses = load_businesses_data()
        for b in businesses:
            b_name = b["business_name"].lower()
            if b_name in msg_lower or any(w in msg_lower for w in b_name.split() if len(w) > 3):
                selected_name = b["business_name"]
                break
        
        if not selected_name:
            rec_res = get_recommendations(current_profile, top_n=3)
            if rec_res.recommendations:
                selected_name = rec_res.recommendations[0].business_name

        if selected_name:
            current_profile.business_interest = selected_name
            current_state = "EQUIPMENT_SUPPLIER"

    elif current_state == "EQUIPMENT_SUPPLIER":
        cap = extract_capital_from_text(user_msg)
        if cap is not None:
            current_profile.capital = cap
        current_state = "FINANCIAL"

    elif current_state == "FINANCIAL":
        if any(k in msg_lower for k in ["no", "skip", "नाही", "नहीं"]):
            current_state = "COMPLETE"
        else:
            current_state = "SCHEME_OPT_IN"

    elif current_state == "SCHEME_OPT_IN":
        if any(k in msg_lower for k in ["yes", "check", "scheme", "होय", "हाँ"]):
            current_state = "SCHEME_PROFILE"
        elif any(k in msg_lower for k in ["no", "skip", "continue", "नाही", "नहीं"]):
            current_state = "COMPLETE"
        else:
            current_state = "SCHEME_PROFILE"

    elif current_state == "SCHEME_PROFILE":
        current_state = "SCHEME_MATCHING"

    elif current_state == "SCHEME_MATCHING":
        current_state = "COMPLETE"

    # 2. Extract Entities from user message
    extracted_data = extract_entities_locally(user_msg, current_state)

    # 3. Update Profile with extracted entities
    updated_profile = merge_profile_entities(current_profile, extracted_data)
    session["profile"] = updated_profile

    # 4. Advance State Machine if in profile collection phase
    if current_state in ["PERSONAL_NAME", "PERSONAL_PLACE", "PERSONAL_OCCUPATION", "BUSINESS_SKILLS", "BUSINESS_RESOURCES", "BUSINESS_CAPITAL", "BUSINESS_INTEREST"]:
        next_state = determine_current_state(updated_profile, current_state)
    else:
        next_state = current_state

    session["current_state"] = next_state

    # 5. Build Response
    reply_text, quick_replies = build_state_response(
        state=next_state,
        profile=updated_profile,
        extracted=extracted_data,
        lang=session_lang,
        user_msg=user_msg
    )

    is_ready = next_state in ["PROFILE_CONFIRMATION", "RECOMMENDATION", "FINANCIAL", "COMPLETE"]
    missing_fields = []
    if not updated_profile.name: missing_fields.append("Name")
    if not updated_profile.location: missing_fields.append("Location")
    if not updated_profile.occupation: missing_fields.append("Occupation")

    return ChatResponse(
        session_id=session_id,
        current_step=next_state,
        reply=reply_text,
        updated_profile=updated_profile,
        is_profile_ready=is_ready,
        missing_fields=missing_fields,
        suggested_quick_replies=quick_replies[:4],
        language=session_lang
    )

