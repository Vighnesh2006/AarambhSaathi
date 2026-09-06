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
    "EQUIPMENT_SUPPLIER",
    "SUPPLIER_DONE",       # After showing supplier list, ask if user wants finance
    "FINANCIAL",
    "SCHEME_OPT_IN",
    "SCHEME_PROFILE",
    "SCHEME_MATCHING",
    "DPR",
    "COMPLETE"
]

# Maps business sector keywords to machine category names in the local database
BIZ_SECTOR_TO_MACHINE_CATEGORIES = {
    "dairy": ["dairy", "milk", "chilling", "milking"],
    "milk": ["dairy", "milk", "pasteurization"],
    "goat": ["livestock", "goat", "animal"],
    "poultry": ["poultry", "egg", "broiler"],
    "mushroom": ["mushroom", "spawn", "cultivation"],
    "flour": ["flour", "atta", "chakki", "milling"],
    "spice": ["spice", "masala", "grinding"],
    "oil": ["oil", "expeller", "cold press"],
    "pickle": ["food processing", "packaging"],
    "jaggery": ["jaggery", "sugar", "crushing"],
    "vermicompost": ["compost", "vermi"],
    "beekeeping": ["honey", "bee", "extraction"],
    "honey": ["honey", "extraction", "bottling"],
    "tailor": ["sewing", "stitching", "garment"],
    "garment": ["sewing", "stitching", "garment"],
    "paper": ["paper", "bag", "packaging"],
    "candle": ["candle", "wax", "mould"],
    "soap": ["soap", "detergent", "fmcg"],
    "welding": ["welding", "fabrication", "engineering"],
    "fish": ["fishery", "aquaculture", "fish"],
    "bamboo": ["bamboo", "coir", "natural fibre"],
    "brick": ["brick", "block", "fly ash"],
    "biogas": ["biogas", "biomass", "renewable"],
    "solar": ["solar", "renewable energy"],
    "cold storage": ["cold storage", "refrigeration"],
    "nursery": ["nursery", "seedling", "horticulture"],
}

# Occupation → Relevant Skills (deterministic MVP – shown as quick-reply buttons)
OCCUPATION_SKILLS_MAP = {
    "farmer":              ["Crop Cultivation & Land Management", "Cattle Rearing & Dairy", "Agricultural Equipment Operation", "Irrigation & Water Management"],
    "tailor":              ["Stitching & Tailoring", "Pattern Cutting & Design", "Sewing Machine Operation", "Fabric Selection & Handling"],
    "student":             ["Computer Skills & Digital Marketing", "Sales & Customer Service", "Business Planning & Management", "Basic Accounting"],
    "homemaker":           ["Food Processing & Preservation", "Handicraft & Embroidery", "Retail & Customer Service", "Packaging & Labelling"],
    "daily wage labourer": ["Manual Labour & Construction", "Agricultural Field Work", "Machine Operation Basics", "Transport & Logistics"],
    "retail shopkeeper":   ["Retail Inventory Management", "Customer Service & Sales", "Basic Accounting & GST", "Supply Chain & Procurement"],
}

# Occupation → Relevant Business Ideas (deterministic MVP – quick-reply options at BUSINESS_INTEREST stage)
OCCUPATION_BUSINESS_MAP = {
    "farmer":              ["Dairy Farming", "Mushroom Farming", "Poultry Farming", "Vermicompost Production"],
    "tailor":              ["Rural Tailoring & Garment Unit", "School Uniform Manufacturing", "Boutique Garments Unit"],
    "student":             ["Mushroom Farming", "Beekeeping & Honey Production", "Rural Tailoring & Garment Unit"],
    "homemaker":           ["Pickle & Papad Production", "Rural Tailoring & Garment Unit", "Beekeeping & Honey Production"],
    "daily wage labourer": ["Mini Flour Mill (Atta Chakki)", "Goat Rearing & Breeding", "Vermicompost Production"],
    "retail shopkeeper":   ["Mini Flour Mill (Atta Chakki)", "Spice Processing & Packaging", "Bakery & Snack Production Unit"],
}


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
    invalid_words = {
        "not", "sure", "planning", "looking", "here", "just", "trying", "working", "going", "ready",
        "tailoring", "tailor", "dairy", "farming", "farm", "poultry", "spice", "bakery", "flour", "mill",
        "goat", "mushroom", "fish", "beekeeping", "honey", "pickle", "papad", "vermicompost", "supplier",
        "suppliers", "machine", "machinery", "equipment", "financial", "finance", "scheme", "schemes",
        "dpr", "report", "show", "list", "give", "details", "price", "cost", "budget", "loan", "subsidy",
        "pmegp", "mudra", "nabard", "sewing", "garment", "stitching", "masala", "chakki", "atta"
    }

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
        # Determine occupation-specific quick-reply skills
        occ_key = (profile.occupation or "").lower()
        occ_skills: list = []
        for _key, _skills in OCCUPATION_SKILLS_MAP.items():
            if _key in occ_key or occ_key in _key:
                occ_skills = _skills
                break

        if lang == "mr":
            reply = f"उत्तम! **{occ}** म्हणून तुमचा अनुभव नवीन व्यवसायासाठी मोठा पाया ठरेल. 💡\n\nतुमच्याकडे कोणती **प्रात्यक्षिक कौशल्ये किंवा कामाचा अनुभव** आहे?"
            quick_replies = occ_skills[:4] if occ_skills else ["पशुपालन व दुग्ध व्यवसाय", "सिलाई व टेलरिंग", "शेती व पीक काळजी", "मशिनरी चालवणे"]
        elif lang == "hi":
            reply = f"बहुत बढ़िया! **{occ}** के रूप में आपका व्यावहारिक अनुभव बहुत काम आएगा। 💡\n\nआपके पास कौन सा **व्यावहारिक कौशल या अनुभव** है?"
            quick_replies = occ_skills[:4] if occ_skills else ["पशुपालन व डेयरी", "सिलाई व दर्जी काम", "खेती व फसल देखभाल", "मशीन संचालन"]
        else:
            reply = f"Great! Working as a **{occ}** provides a strong practical foundation. 💡\n\nWhat specific **hands-on skills or experience** do you possess?"
            quick_replies = occ_skills[:4] if occ_skills else ["Livestock & Dairy Care", "Tailoring & Stitching", "Farming & Crop Care", "Machinery Operation"]

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
        # Show occupation-specific business ideas
        occ_key = (profile.occupation or "").lower()
        biz_opts_en: list = []
        for _key, _biz_list in OCCUPATION_BUSINESS_MAP.items():
            if _key in occ_key or occ_key in _key:
                biz_opts_en = _biz_list
                break
        if not biz_opts_en:
            biz_opts_en = ["Dairy Farming", "Mushroom Farming", "Poultry Farming"]

        if lang == "mr":
            reply = f"उत्तम! **{cap_val}** चे भांडवल आणि **{skills_text}** चे कौशल्य यासह तुमच्याकडे उत्तम संधी आहे. 🎯\n\nतुमच्या मनात आधीपासून कोणता **विशिष्ट व्यवसाय** आहे, की मी तुम्हाला **{loc}** साठी सर्वोत्कृष्ट पर्याय सुचवू?"
            quick_replies = biz_opts_en[:3] + ["सर्वोत्कृष्ट पर्याय सुचवा"]
        elif lang == "hi":
            reply = f"शानदार! **{cap_val}** की पूंजी और **{skills_text}** के कौशल के साथ आपके लिए बेहतरीन अवसर हैं। 🎯\n\nक्या आपके मन में पहले से कोई **विशेष व्यवसाय** है, या मैं आपको **{loc}** के लिए सर्वश्रेष्ठ 3 विकल्प सुझाऊं?"
            quick_replies = biz_opts_en[:3] + ["सर्वश्रेष्ठ 3 विकल्प सुझाएं"]
        else:
            reply = f"Excellent! With **{cap_val}** capital and skills in **{skills_text}**, you have strong business potential. 🎯\n\nDo you already have a **specific business idea** in mind, or would you like me to recommend the top 3 best-suited options for **{loc}**?"
            quick_replies = biz_opts_en[:3] + ["Suggest Best 3 Options"]

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
        
        # ── Better machine matching using sector keyword map ──
        biz_lower = biz_name.lower()
        target_cats = []
        for key, cats in BIZ_SECTOR_TO_MACHINE_CATEGORIES.items():
            if key in biz_lower:
                target_cats.extend(cats)
        
        matched_m = []
        if target_cats:
            for m in all_machines:
                m_cats = [c.lower() for c in m.get("business_categories", [])]
                m_name = m.get("machine_name", "").lower()
                m_all = m_name + " " + " ".join(m_cats)
                if any(cat in m_all for cat in target_cats):
                    matched_m.append(m)
        
        # Fallback: match by individual meaningful biz name words against machine name only
        if not matched_m:
            SKIP = {"farm", "farming", "unit", "mini", "small", "rural", "value",
                    "processing", "manufacturing", "production", "centre", "center"}
            biz_words = [w for w in biz_lower.split() if len(w) > 4 and w not in SKIP]
            for m in all_machines:
                m_name = m.get("machine_name", "").lower()
                if biz_words and any(w in m_name for w in biz_words):
                    matched_m.append(m)
        
        if not matched_m:
            matched_m = all_machines[:3]
            
        matched_machine_ids = set(m.get("machine_id") for m in matched_m)
        matched_suppliers = [s for s in all_suppliers if any(mid in matched_machine_ids for mid in s.get("machine_ids", []))]
        if not matched_suppliers:
            matched_suppliers = all_suppliers[:2]

        # Format Machines for Chatbox
        m_items_en, m_items_hi, m_items_mr = [], [], []
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
        s_items_en, s_items_hi, s_items_mr = [], [], []
        for idx, s in enumerate(matched_suppliers[:2], 1):
            s_name = s.get('supplier_name', 'Verified Supplier')
            s_loc = f"{s.get('location', s.get('city', 'Pune'))}, {s.get('district', 'Pune')}, {s.get('state', 'Maharashtra')}"
            phone = s.get('contact', '+91 98220 12345')
            if isinstance(phone, dict):
                phone = phone.get('phone', '+91 98220 12345')
            p_range = s.get('price_range', 'Competitive MSME Rates')
            src = s.get('source', 'DIC / MSME Empanelled Directory')
            s_items_en.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **Location:** {s_loc}\n   • 📞 **Contact:** `{phone}`\n   • 🏷️ **Price Range:** {p_range}\n   • ⚙️ **Services:** Installation, Warranty & Demo (`{src}`)")
            s_items_hi.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **स्थान:** {s_loc}\n   • 📞 **संपर्क:** `{phone}`\n   • 🏷️ **मूल्य सीमा:** {p_range}\n   • ⚙️ **सेवाएं:** इंस्टॉलेशन, वारंटी एवं प्रशिक्षण (`{src}`)")
            s_items_mr.append(f"{idx}. 🏢 **{s_name}**\n   • 📍 **ठिकाण:** {s_loc}\n   • 📞 **संपर्क:** `{phone}`\n   • 🏷️ **किंमत:** {p_range}\n   • ⚙️ **सुविधा:** इन्स्टॉलेशन, वॉरंटी व प्रशिक्षण (`{src}`)")

        machines_text_en = "\n\n".join(m_items_en)
        machines_text_hi = "\n\n".join(m_items_hi)
        machines_text_mr = "\n\n".join(m_items_mr)
        suppliers_text_en = "\n\n".join(s_items_en)
        suppliers_text_hi = "\n\n".join(s_items_hi)
        suppliers_text_mr = "\n\n".join(s_items_mr)

        if lang == "mr":
            reply = (f"⚙️ **'{biz_name}' साठी आवश्यक यंत्रसामग्री आणि सप्लायरची विस्तृत यादी:**\n\n"
                     f"🛠️ **आवश्यक यंत्रसामग्री व तांत्रिक तपशील:**\n{machines_text_mr}\n\n"
                     f"🏪 **प्रमाणित स्थानिक सप्लायर्स (विक्रेते):**\n{suppliers_text_mr}")
            quick_replies = ["आर्थिक नियोजन पहा", "सरकारी योजना तपासा", "DPR अहवाल पहा"]
        elif lang == "hi":
            reply = (f"⚙️ **'{biz_name}' के लिए आवश्यक मशीनरी एवं सत्यापित सप्लायर सूची:**\n\n"
                     f"🛠️ **अनुशंसित मशीनरी व उपकरण:**\n{machines_text_hi}\n\n"
                     f"🏪 **सत्यापित स्थानीय सप्लायर:**\n{suppliers_text_hi}")
            quick_replies = ["वित्तीय योजना देखें", "सरकारी योजनाएं देखें", "DPR रिपोर्ट देखें"]
        else:
            reply = (f"⚙️ **Machinery & Verified Supplier Directory for '{biz_name}':**\n\n"
                     f"🛠️ **Required Equipment:**\n{machines_text_en}\n\n"
                     f"🏪 **Verified Local Suppliers:**\n{suppliers_text_en}")
            quick_replies = ["View Financial Plan", "Check Government Schemes", "View DPR Report"]

    elif state == "SUPPLIER_DONE":
        # Ask if user wants the financial plan after viewing suppliers
        if lang == "mr":
            reply = ("✅ **यंत्रसामग्री व सप्लायर माहिती तयार आहे!**\n\n"
                     "पुढे तुम्हाला काय पाहायचे आहे?\n\n"
                     "• **आर्थिक नियोजन** — प्रकल्प खर्च, कर्ज, मासिक नफा\n"
                     "• **सरकारी योजना** — PMEGP, MUDRA, NABARD अनुदान\n"
                     "• **DPR अहवाल** — संपूर्ण व्यवसाय आराखडा")
            quick_replies = ["आर्थिक नियोजन पहा", "सरकारी योजना तपासा", "DPR अहवाल पहा"]
        elif lang == "hi":
            reply = ("✅ **मशीनरी व सप्लायर जानकारी तैयार है!**\n\n"
                     "अगला कदम — आप क्या देखना चाहते हैं?\n\n"
                     "• **वित्तीय योजना** — परियोजना लागत, ऋण, मासिक लाभ\n"
                     "• **सरकारी योजनाएं** — PMEGP, MUDRA, NABARD सब्सिडी\n"
                     "• **DPR रिपोर्ट** — पूरा बिजनेस प्लान")
            quick_replies = ["वित्तीय योजना देखें", "सरकारी योजनाएं देखें", "DPR रिपोर्ट देखें"]
        else:
            reply = ("✅ **Machinery & Supplier list is ready!**\n\n"
                     "What would you like to explore next?\n\n"
                     "• **Financial Plan** — Project cost, loan needed, monthly profit\n"
                     "• **Government Schemes** — PMEGP, MUDRA, NABARD subsidies\n"
                     "• **DPR Report** — Complete 90-day Business Plan")
            quick_replies = ["View Financial Plan", "Check Government Schemes", "View DPR Report"]

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

    elif state in ["DPR", "COMPLETE"]:
        biz_name = profile.business_interest or "Rural Business"
        user_cap  = profile.capital or 100000.0
        occ_lower = (profile.occupation or "").lower()
        biz_lower = biz_name.lower()

        # ── Choose archetype DPR template ──
        if "dairy" in biz_lower or "milk" in biz_lower:
            project_cost, loan_amt = 300000, max(0, 300000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 35000, 22000, "12-15"
            machines = "Milking Machine (₹35,000) | Milk Chiller / Bulk Cooler (₹85,000) | Pasteurization Unit (₹60,000)"
            scheme   = "NABARD DEDS – 25%-33% Subsidy | PM-MUDRA Kishore Loan (₹50K–₹5L)"
            month1   = "Register FSSAI licence, identify 5-6 high-yield cattle (HF/Jersey), join local milk co-op (AMUL / KMF)"
            month2   = "Purchase cattle & milking equipment, apply for NABARD/MUDRA loan, start local supply (50 L/day)"
            month3   = "Scale to 100 L/day, sign bulk contract with dairy co-op, achieve ₹35,000/month revenue"
        elif "tailor" in biz_lower or "garment" in biz_lower or "tailor" in occ_lower:
            project_cost, loan_amt = 120000, max(0, 120000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 25000, 16000, "8-12"
            machines = "Industrial Sewing Machine ×2 (₹40,000) | Overlock Machine (₹15,000) | Cutting Table & Tools (₹8,000)"
            scheme   = "PMEGP – 25%-35% Subsidy | PM-MUDRA Shishu/Kishore (₹50K–₹5L collateral-free)"
            month1   = "Register Udyam (MSME), purchase 2 sewing machines, attend garment stitching training at ITI"
            month2   = "Accept school uniform orders & alteration work, market via WhatsApp with price list"
            month3   = "Hire 1 helper, launch readymade blouse/kurta collection, target ₹25,000/month revenue"
        elif "mushroom" in biz_lower:
            project_cost, loan_amt = 80000, max(0, 80000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 18000, 12000, "6-9"
            machines = "Spawn Culture Bags (₹15,000) | Sterilization Drum (₹8,000) | Polythene Shelving & Polyhouse (₹25,000)"
            scheme   = "PMEGP – 25%-35% Subsidy | NABARD Horticulture Promotion Scheme"
            month1   = "Source paddy straw substrate, buy spawn from KVK, set up polyhouse (14°C–28°C range)"
            month2   = "First harvest in 30-40 days, supply fresh mushrooms to vegetable vendors & restaurants"
            month3   = "Scale to 200 kg/month, explore dried mushroom value-added products for higher margins"
        elif "poultry" in biz_lower:
            project_cost, loan_amt = 200000, max(0, 200000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 30000, 18000, "10-14"
            machines = "Brooder & Heating System (₹15,000) | Automatic Feeder & Drinkers (₹10,000) | Egg Trays & Crates (₹5,000)"
            scheme   = "NABARD Poultry Development Scheme | PMEGP | State Animal Husbandry Dept Subsidy"
            month1   = "Register with State Animal Husbandry Dept, construct shed for 500 birds, procure day-old chicks (DOC)"
            month2   = "Manage 6-8 week feed & vaccination cycle, tie-up with local poultry market/aggregator"
            month3   = "Complete first batch (500 birds), target ₹30,000/month, plan second batch cycle"
        elif "flour" in biz_lower or "chakki" in biz_lower or "atta" in biz_lower:
            project_cost, loan_amt = 150000, max(0, 150000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 20000, 13000, "10-14"
            machines = "Atta Chakki / Flour Mill (₹75,000) | Weighing Scale (₹5,000) | Packing Machine (₹20,000)"
            scheme   = "PMEGP – 25%-35% Subsidy | PM-MUDRA Kishore Loan"
            month1   = "Register Udyam, secure location, procure flour mill, obtain FSSAI licence"
            month2   = "Begin wheat/jowar/bajra milling, supply to local kirana stores & households"
            month3   = "Add home delivery, target 500 kg/day milling, achieve ₹20,000/month profit"
        elif "goat" in biz_lower:
            project_cost, loan_amt = 100000, max(0, 100000 - int(user_cap))
            monthly_revenue, monthly_profit, payback = 15000, 9000, "12-18"
            machines = "Feeder Troughs (₹5,000) | Goat Shed / Housing (₹30,000) | Weighing Balance (₹3,000)"
            scheme   = "NABARD Animal Husbandry Scheme | PMEGP | State Goat Development Corporation Subsidy"
            month1   = "Register with Animal Husbandry Dept, build shed for 20 goats, procure Osmanabadi/Sirohi goats"
            month2   = "Set up feed & health management, establish tie-up with local meat market"
            month3   = "First kidding cycle, expand to 40 goats, target ₹15,000/month revenue"
        else:
            project_cost = max(150000, int(user_cap) * 2)
            loan_amt     = max(0, project_cost - int(user_cap))
            monthly_revenue = int(project_cost * 0.25)
            monthly_profit  = int(monthly_revenue * 0.6)
            payback  = "12-18"
            machines = "Primary Processing & Production Equipment (as listed in supplier section above)"
            scheme   = "PMEGP – 25%-35% Capital Subsidy | PM-MUDRA Loan (up to ₹10 Lakhs collateral-free)"
            month1   = "Business registration (Udyam/GST/FSSAI), equipment procurement, raw material sourcing"
            month2   = "Trial production, local market entry, bank loan disbursement, hire 1-2 helpers"
            month3   = "Full production scale-up, achieve monthly revenue target, open business bank account"

        if lang == "mr":
            reply = (
                f"📄 **{name} जी — '{biz_name}' साठी संपूर्ण DPR (Detailed Project Report):**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏭 **प्रकल्प सारांश**\n"
                f"• **व्यवसाय:** {biz_name}\n"
                f"• **उद्योजक:** {name}, {loc}\n"
                f"• **एकूण प्रकल्प खर्च:** ₹{project_cost:,.0f}\n"
                f"• **स्वतःचे भांडवल:** ₹{int(user_cap):,.0f}\n"
                f"• **बँक कर्ज / अनुदान आवश्यक:** ₹{loan_amt:,.0f}\n"
                f"• **अंदाजे मासिक उत्पन्न:** ₹{monthly_revenue:,}\n"
                f"• **अंदाजे मासिक निव्वळ नफा:** ₹{monthly_profit:,}\n"
                f"• **गुंतवणूक परतावा कालावधी:** {payback} महिने\n\n"
                f"🛠️ **आवश्यक यंत्रसामग्री व उपकरणे**\n{machines}\n\n"
                f"📅 **९०-दिवसीय कृती योजना**\n"
                f"• **महिना १:** {month1}\n"
                f"• **महिना २:** {month2}\n"
                f"• **महिना ३:** {month3}\n\n"
                f"🏛️ **पात्र शासकीय योजना व अनुदान**\n{scheme}\n\n"
                f"🎉 **अभिनंदन {name} जी! तुमचा व्यवसाय प्रवास आता सुरू होत आहे. आरंभ साथी सदैव तुमच्यासोबत! 🌟**"
            )
            quick_replies = ["पुन्हा नवीन सुरुवात करा", "सप्लायर पुन्हा पहा"]
        elif lang == "hi":
            reply = (
                f"📄 **{name} जी — '{biz_name}' के लिए पूर्ण DPR (विस्तृत परियोजना रिपोर्ट):**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏭 **परियोजना सारांश**\n"
                f"• **व्यवसाय:** {biz_name}\n"
                f"• **उद्यमी:** {name}, {loc}\n"
                f"• **कुल परियोजना लागत:** ₹{project_cost:,.0f}\n"
                f"• **स्वयं की पूंजी:** ₹{int(user_cap):,.0f}\n"
                f"• **बैंक ऋण / सब्सिडी आवश्यक:** ₹{loan_amt:,.0f}\n"
                f"• **अनुमानित मासिक आय:** ₹{monthly_revenue:,}\n"
                f"• **अनुमानित मासिक शुद्ध लाभ:** ₹{monthly_profit:,}\n"
                f"• **निवेश वापसी अवधि:** {payback} महीने\n\n"
                f"🛠️ **आवश्यक मशीनरी व उपकरण**\n{machines}\n\n"
                f"📅 **90-दिवसीय कार्य योजना**\n"
                f"• **महीना 1:** {month1}\n"
                f"• **महीना 2:** {month2}\n"
                f"• **महीना 3:** {month3}\n\n"
                f"🏛️ **पात्र सरकारी योजनाएं व सब्सिडी**\n{scheme}\n\n"
                f"🎉 **बधाई हो {name} जी! आपकी व्यावसायिक यात्रा शुरू हो रही है। आरंभ साथी हमेशा आपके साथ! 🌟**"
            )
            quick_replies = ["पुनः नई शुरुआत करें", "सप्लायर पुनः देखें"]
        else:
            reply = (
                f"📄 **Detailed Project Report (DPR) — '{biz_name}' for {name}:**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏭 **Project Overview**\n"
                f"• **Business:** {biz_name}\n"
                f"• **Entrepreneur:** {name}, {loc}\n"
                f"• **Total Project Cost:** ₹{project_cost:,.0f}\n"
                f"• **Own Capital Contribution:** ₹{int(user_cap):,.0f}\n"
                f"• **Bank Loan / Subsidy Required:** ₹{loan_amt:,.0f}\n"
                f"• **Estimated Monthly Revenue:** ₹{monthly_revenue:,}\n"
                f"• **Estimated Monthly Net Profit:** ₹{monthly_profit:,}\n"
                f"• **Investment Payback Period:** {payback} months\n\n"
                f"🛠️ **Required Machinery & Equipment**\n{machines}\n\n"
                f"📅 **90-Day Action Plan**\n"
                f"• **Month 1:** {month1}\n"
                f"• **Month 2:** {month2}\n"
                f"• **Month 3:** {month3}\n\n"
                f"🏛️ **Eligible Government Schemes & Subsidies**\n{scheme}\n\n"
                f"🎉 **Congratulations {name}! Your entrepreneurial journey begins now. Aarambh Saathi is always with you! 🌟**"
            )
            quick_replies = ["Start a New Consultation", "View Suppliers Again"]

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

    # 1. Global Interceptor for Business Ideas & Supplier Queries Across All States
    msg_lower = user_msg.lower()
    
    # Check for direct business selection or supplier/machinery query across ALL states
    KEYWORD_MAP = {
        "tailor": "Rural Tailoring & Garment Unit",
        "tailoring": "Rural Tailoring & Garment Unit",
        "sewing": "Rural Tailoring & Garment Unit",
        "garment": "Rural Tailoring & Garment Unit",
        "stitching": "Rural Tailoring & Garment Unit",
        "dairy": "Dairy Farming",
        "milking": "Dairy Farming",
        "milk": "Dairy Farming",
        "gotha": "Dairy Farming",
        "spice": "Spice Processing & Packaging",
        "masala": "Spice Processing & Packaging",
        "flour": "Mini Flour Mill (Atta Chakki)",
        "chakki": "Mini Flour Mill (Atta Chakki)",
        "atta": "Mini Flour Mill (Atta Chakki)",
        "bakery": "Bakery & Snack Production Unit",
        "bread": "Bakery & Snack Production Unit",
        "poultry": "Poultry Farming",
        "hatchery": "Poultry Farming",
        "egg": "Poultry Farming",
        "goat": "Goat Rearing & Breeding",
        "bakri": "Goat Rearing & Breeding",
        "mushroom": "Mushroom Farming",
        "fish": "Fish Farming / Aquaculture",
        "honey": "Beekeeping & Honey Production",
        "beekeep": "Beekeeping & Honey Production",
        "pickle": "Pickle & Papad Production",
        "papad": "Pickle & Papad Production"
    }

    matched_biz = None
    for kw, b_name in KEYWORD_MAP.items():
        if kw in msg_lower:
            matched_biz = b_name
            break

    asking_suppliers = any(k in msg_lower for k in ["supplier", "suppliers", "machinery", "machine", "equipment", "vendor", "vendors"])

    # Don't intercept during early profile-collection states — occupation/skill answers
    # contain business keywords but should not skip the funnel.
    PROFILE_COLLECTION_STATES = {
        "PERSONAL_NAME", "PERSONAL_PLACE", "PERSONAL_OCCUPATION",
        "BUSINESS_SKILLS", "BUSINESS_RESOURCES", "BUSINESS_CAPITAL", "BUSINESS_INTEREST"
    }

    if (matched_biz or asking_suppliers) and current_state not in PROFILE_COLLECTION_STATES:
        if matched_biz:
            current_profile.business_interest = matched_biz
        elif not current_profile.business_interest:
            current_profile.business_interest = "Dairy Farming"
        current_state = "EQUIPMENT_SUPPLIER"

    elif current_state == "PROFILE_CONFIRMATION":
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
        
        # PRIORITY 1: Exact full name match
        for b in businesses:
            if b["business_name"].lower() == msg_lower.strip():
                selected_name = b["business_name"]
                break
        
        # PRIORITY 2: Full business name is contained in the user message
        if not selected_name:
            for b in businesses:
                if b["business_name"].lower() in msg_lower:
                    selected_name = b["business_name"]
                    break
        
        # PRIORITY 3: User message contains the business name
        if not selected_name:
            for b in businesses:
                if msg_lower in b["business_name"].lower():
                    selected_name = b["business_name"]
                    break
        
        # PRIORITY 4: Match ONLY meaningful unique words (4+ chars, not generic terms)
        GENERIC = {"farm", "farming", "unit", "mini", "small", "rural", "production",
                   "manufacturing", "processing", "making", "centre", "center",
                   "services", "service", "business", "value", "added", "local"}
        if not selected_name:
            msg_words = {w for w in msg_lower.split() if len(w) > 4 and w not in GENERIC}
            if msg_words:
                best_match = None
                best_overlap = 0
                for b in businesses:
                    b_words = {w for w in b["business_name"].lower().split() if len(w) > 4 and w not in GENERIC}
                    overlap = len(msg_words & b_words)
                    if overlap > 0 and overlap >= len(b_words) * 0.6 and overlap > best_overlap:
                        best_overlap = overlap
                        best_match = b["business_name"]
                selected_name = best_match
        
        # PRIORITY 5: fallback only if none matched — use top recommendation
        if not selected_name:
            rec_res = get_recommendations(current_profile, top_n=3)
            if rec_res.recommendations:
                selected_name = rec_res.recommendations[0].business_name

        if selected_name:
            current_profile.business_interest = selected_name
            current_state = "EQUIPMENT_SUPPLIER"

    elif current_state == "EQUIPMENT_SUPPLIER":
        current_state = "SUPPLIER_DONE"

    elif current_state == "SUPPLIER_DONE":
        # Route to FINANCIAL ONLY if user asks about finance/budget/loan/profit/plan
        if any(k in msg_lower for k in ["finance", "financial", "loan", "budget", "cost", "profit", "आर्थिक", "नफा"]):
            current_state = "FINANCIAL"
        # Route to SCHEME_OPT_IN if asking about government schemes
        elif any(k in msg_lower for k in ["scheme", "government", "subsidy", "pmegp", "mudra", "nabard", "योजना"]):
            current_state = "SCHEME_OPT_IN"
        # Route to COMPLETE if asking for DPR report
        elif any(k in msg_lower for k in ["dpr", "report", "download", "अहवाल", "रिपोर्ट"]):
            current_state = "DPR"
        elif any(k in msg_lower for k in ["no", "skip"]):
            current_state = "SCHEME_OPT_IN"
        else:
            current_state = "SUPPLIER_DONE"

    elif current_state == "FINANCIAL":
        # After financial plan shown, ask about schemes
        if any(k in msg_lower for k in ["no", "skip", "नाही", "नहीं", "छोड़", "सोडा"]):
            current_state = "COMPLETE"
        else:
            current_state = "SCHEME_OPT_IN"

    elif current_state == "SCHEME_OPT_IN":
        if any(k in msg_lower for k in ["dpr", "report", "plan", "अहवाल", "रिपोर्ट"]):
            current_state = "DPR"
        elif any(k in msg_lower for k in ["yes", "check", "scheme", "होय", "हाँ", "हां", "योजना", "सरकारी", "government", "subsidy", "pmegp", "mudra", "nabard"]):
            current_state = "SCHEME_PROFILE"
        elif any(k in msg_lower for k in ["no", "skip", "continue", "नाही", "नहीं"]):
            current_state = "COMPLETE"
        else:
            current_state = "SCHEME_PROFILE"

    elif current_state == "SCHEME_PROFILE":
        current_state = "SCHEME_MATCHING"

    elif current_state == "SCHEME_MATCHING":
        current_state = "DPR"

    elif current_state == "DPR":
        current_state = "COMPLETE"

    # 2. Extract Entities from user message
    extracted_data = extract_entities_locally(user_msg, current_state)

    # 3. Update Profile with extracted entities
    updated_profile = merge_profile_entities(current_profile, extracted_data)
    session["profile"] = updated_profile

    # 4. Advance State Machine: If a business idea or supplier request was intercepted, stay in EQUIPMENT_SUPPLIER/SUPPLIER_DONE
    if matched_biz or asking_suppliers:
        next_state = current_state
    elif current_state in ["PERSONAL_NAME", "PERSONAL_PLACE", "PERSONAL_OCCUPATION", "BUSINESS_SKILLS", "BUSINESS_RESOURCES", "BUSINESS_CAPITAL", "BUSINESS_INTEREST"]:
        next_state = determine_current_state(updated_profile, current_state)
    else:
        next_state = current_state

    if next_state == "EQUIPMENT_SUPPLIER":
        session["current_state"] = "SUPPLIER_DONE"
    else:
        session["current_state"] = next_state

    # 5. Build Response
    reply_text, quick_replies = build_state_response(
        state=next_state,
        profile=updated_profile,
        extracted=extracted_data,
        lang=session_lang,
        user_msg=user_msg
    )

    is_ready = next_state in ["PROFILE_CONFIRMATION", "RECOMMENDATION", "FINANCIAL", "DPR", "COMPLETE"]
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

