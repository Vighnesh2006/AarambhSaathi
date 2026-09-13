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
    "USER_INTENT",
    "EXISTING_BUSINESS",
    "PERSONAL_AGE",
    "PERSONAL_GENDER",
    "PERSONAL_LOCATION",
    "PERSONAL_EDUCATION",
    "BUSINESS_SKILLS",
    "BUSINESS_EXPERIENCE",
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

PROFILE_COLLECTION_STATES = {
    "PERSONAL_NAME", "USER_INTENT", "EXISTING_BUSINESS", "PERSONAL_AGE",
    "PERSONAL_GENDER", "PERSONAL_LOCATION", "PERSONAL_PLACE", "PERSONAL_EDUCATION",
    "PERSONAL_OCCUPATION", "BUSINESS_SKILLS", "BUSINESS_EXPERIENCE",
    "BUSINESS_RESOURCES", "BUSINESS_CAPITAL", "BUSINESS_INTEREST"
}

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
        "एक लाख रुपये": 100000.0, "२५ हजार": 25000.0, "25 हजार": 25000.0, "पचीस हजार": 25000.0,
        "₹25,000": 25000.0, "₹50,000": 50000.0, "₹1,00,000": 100000.0, "₹2,50,000": 250000.0, "₹5,00,000": 500000.0
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
    return " ".join([w.capitalize() for w in val.split()]) if val else raw.strip()

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
    "Maharashtra": ["pune", "satara", "baramati", "kolhapur", "nashik", "nagpur", "solapur", "aurangabad", "chhatrapati sambhajinagar", "amravati", "sangli", "nanded", "ahmednagar", "jalgaon", "latur", "akola", "dhule", "chandrapur", "parbhani", "shirwal", "khed", "maharashtra"],
    "Gujarat": ["surat", "ahmedabad", "vadodara", "rajkot", "gandhinagar", "bhavnagar", "jamnagar", "junagadh", "anand", "navsari", "gujarat"],
    "Karnataka": ["bangalore", "bengaluru", "belgaum", "mysore", "hubli", "dharwad", "mangalore", "gulbarga", "karnataka"],
    "Madhya Pradesh": ["indore", "bhopal", "jabalpur", "gwalior", "ujjain", "sagar", "rewa", "madhya pradesh", "mp"],
    "Rajasthan": ["jaipur", "jodhpur", "udaipur", "kota", "bikaner", "ajmer", "bhilwara", "alwar", "rajasthan"],
    "Uttar Pradesh": ["lucknow", "kanpur", "varanasi", "agra", "meerut", "prayagraj", "allahabad", "bareilly", "aligarh", "uttar pradesh", "up"],
    "Bihar": ["patna", "gaya", "muzaffarpur", "bhagalpur", "darbhanga", "bihar"],
    "Telangana": ["hyderabad", "warangal", "nizamabad", "karimnagar", "telangana"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "tiruchirappalli", "salem", "tamil nadu"],
    "Andhra Pradesh": ["visakhapatnam", "vijayawada", "guntur", "nellore", "kurnool", "andhra pradesh"],
    "Haryana": ["gurugram", "faridabad", "panipat", "ambala", "karnal", "haryana"],
    "Punjab": ["ludhiana", "amritsar", "jalandhar", "patiala", "bathinda", "punjab"]
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
    extracted: Dict[str, Any] = {}
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

    # 1. Capital / Available Personal Investment
    cap = extract_capital_from_text(user_msg)
    if cap is not None:
        extracted["capital"] = cap
        extracted["available_investment"] = cap

    # 2. Name
    name_match = re.search(r'\b(?:my\s+name\s+is|i\s+am|i\'m|myself|मेरा\s+नाम|माझे\s+नाव|माझं\s+नाव)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+(?:\s+[A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)?)\b', user_msg, re.IGNORECASE)
    if name_match:
        cand = name_match.group(1).strip()
        cand_clean = clean_name_string(cand)
        if cand_clean.lower() not in negative_words and cand_clean.lower() not in invalid_words:
            extracted["name"] = cand_clean
    elif current_state == "PERSONAL_NAME" and len(user_msg.split()) <= 4:
        cleaned = clean_name_string(user_msg)
        if cleaned.lower() not in negative_words and cleaned.lower() not in invalid_words:
            extracted["name"] = cleaned

    # 3. Intent
    if any(k in text_lower for k in ["start a new", "new business", "start new", "नवीन व्यवसाय", "नया व्यवसाय", "नया उद्यम", "नवीन उद्योग"]):
        extracted["intent"] = "Start a new business"
    elif any(k in text_lower for k in ["expand", "existing business", "grow business", "माझा व्यवसाय वाढवणे", "आधीचा व्यवसाय", "पुराना व्यापार", "बढ़ाना", "विस्तार"]):
        extracted["intent"] = "Expand an existing business"
    elif any(k in text_lower for k in ["don't know", "dont know", "not sure", "help me choose", "help me decide", "योग्य व्यवसाय सुचवा", "मदत हवी", "मदद करें", "सुझाव"]):
        extracted["intent"] = "I don't know what business to start"
    elif current_state == "USER_INTENT":
        if "new" in text_lower or "नवीन" in text_lower or "नया" in text_lower:
            extracted["intent"] = "Start a new business"
        elif "expand" in text_lower or "वाढ" in text_lower or "बढ़ा" in text_lower:
            extracted["intent"] = "Expand an existing business"
        else:
            extracted["intent"] = "I don't know what business to start"

    # 4. Age
    age_match = re.search(r'\b(?:age|वय|उम्र|आयु)?\s*(?:is|आहे|है|:)?\s*(\b(?:1[6-9]|[2-9][0-9])\b)\s*(?:years|yrs|वर्षे|वर्ष|साल|years old)?\b', text_lower)
    if age_match:
        try:
            val = int(age_match.group(1))
            if 16 <= val <= 95:
                extracted["age"] = val
        except Exception:
            pass
    elif current_state == "PERSONAL_AGE":
        raw_num = re.search(r'\b(\d{2})\b', text_lower)
        if raw_num:
            try:
                val = int(raw_num.group(1))
                if 16 <= val <= 95:
                    extracted["age"] = val
            except Exception:
                pass
        elif "18-25" in text_lower or "18 ते 25" in text_lower:
            extracted["age"] = 22
        elif "26-35" in text_lower or "26 ते 35" in text_lower:
            extracted["age"] = 30
        elif "36-50" in text_lower or "36 ते 50" in text_lower:
            extracted["age"] = 42
        elif "50+" in text_lower:
            extracted["age"] = 52

    # 5. Gender
    if any(k in text_lower for k in ["female", "woman", "girl", "महिला", "स्त्री", "लड़की", "औरत"]):
        extracted["gender"] = "Female"
    elif any(k in text_lower for k in ["male", "man", "boy", "पुरुष", "मुलगा", "लड़का", "आदमी"]):
        extracted["gender"] = "Male"
    elif any(k in text_lower for k in ["other", "इतर", "अन्य"]):
        extracted["gender"] = "Other"

    # 6. Location (Village, District, State)
    loc_match = re.search(r'\b(?:from|living\s+in|staying\s+in|live\s+in|गाव|राहतो|राहते|रहता|रहती)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+(?:\s*,\s*[A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)?)\b', user_msg, re.IGNORECASE)
    if loc_match:
        raw_loc = loc_match.group(1).strip()
        if raw_loc.lower() not in negative_words:
            if "," in raw_loc:
                parts = [clean_location_string(p) for p in raw_loc.split(",")]
                extracted["village"] = parts[0]
                extracted["district"] = parts[1] if len(parts) > 1 else parts[0]
                extracted["state"] = parts[2] if len(parts) > 2 else resolve_state_from_location(parts[0])
                extracted["location"] = ", ".join(parts[:2])
            else:
                c_loc = clean_location_string(raw_loc)
                extracted["district"] = c_loc
                extracted["village"] = c_loc
                extracted["location"] = c_loc
                extracted["state"] = resolve_state_from_location(c_loc)
    elif current_state in ["PERSONAL_LOCATION", "PERSONAL_PLACE"]:
        loc = clean_location_string(user_msg)
        if loc.lower() not in negative_words:
            if "," in loc:
                parts = [clean_location_string(p) for p in loc.split(",")]
                extracted["village"] = parts[0]
                extracted["district"] = parts[1] if len(parts) > 1 else parts[0]
                extracted["state"] = parts[2] if len(parts) > 2 else resolve_state_from_location(parts[0])
                extracted["location"] = ", ".join(parts[:2])
            else:
                extracted["village"] = loc
                extracted["district"] = loc
                extracted["location"] = loc
                extracted["state"] = resolve_state_from_location(loc)

    # 7. Education
    if any(k in text_lower for k in ["10th", "10वी", "१०वी", "ssc", "matric", "दसवीं"]):
        extracted["education"] = "10th Pass"
    elif any(k in text_lower for k in ["12th", "12वी", "१२वी", "hsc", "inter", "बारहवीं"]):
        extracted["education"] = "12th Pass"
    elif any(k in text_lower for k in ["graduate", "degree", "ba", "bcom", "bsc", "btech", "be", "b.a", "b.com", "b.sc", "पदवीधर", "ग्रेजुएट"]):
        extracted["education"] = "Graduate"
    elif any(k in text_lower for k in ["diploma", "iti", "polytechnic", "डिप्लोमा", "आयटीआय", "आईटीआई"]):
        extracted["education"] = "Diploma / Vocational"
    elif any(k in text_lower for k in ["no formal", "uneducated", "illiterate", "शिकलो नाही", "शिक्षण नाही", "अनपढ़", "प्राथमिक"]):
        extracted["education"] = "No Formal Schooling"
    elif current_state == "PERSONAL_EDUCATION" and text_lower not in negative_words:
        extracted["education"] = user_msg.strip()

    # 8. Occupation
    if "farm" in text_lower or "शेत" in text_lower or "किसान" in text_lower or "कृषि" in text_lower:
        extracted["occupation"] = "Farmer"
    elif "tailor" in text_lower or "शिलाई" in text_lower or "सिलाई" in text_lower:
        extracted["occupation"] = "Tailor"
    elif "student" in text_lower or "विद्यार्थी" in text_lower:
        extracted["occupation"] = "Student"
    elif "housewife" in text_lower or "गृहिणी" in text_lower or "homemaker" in text_lower:
        extracted["occupation"] = "Homemaker"

    # 9. Skills & Experience
    skills_found = []
    if any(k in text_lower for k in ["cattle", "गाय", "म्हैस", "पशु", "cow", "buffalo", "dairy", "दुग्ध", "पशुपालन"]):
        skills_found.append("Cattle Rearing & Animal Husbandry")
        extracted["experience"] = "Cattle handling and dairy experience"
    if any(k in text_lower for k in ["tailor", "शिलाई", "सिलाई", "sewing", "garment", "कपडे"]):
        skills_found.append("Tailoring & Garments")
    if any(k in text_lower for k in ["machine", "मशीन", "यंत्र", "repair", "ऑपरेटर"]):
        skills_found.append("Machinery Operation")
    if any(k in text_lower for k in ["crop", "शेती", "farming", "मशरूम", "organic"]):
        skills_found.append("Farming & Crop Management")
    if any(k in text_lower for k in ["shop", "retail", "विक्री", "दुकान", "sales", "व्यापार"]):
        skills_found.append("Retail & Customer Sales")
        
    if skills_found:
        extracted["skills"] = skills_found
    elif current_state == "BUSINESS_SKILLS" and text_lower not in negative_words:
        extracted["skills"] = [user_msg.strip()]

    # Experience
    if any(k in text_lower for k in ["beginner", "fresh", "नवा", "काही अनुभव नाही", "नया"]):
        extracted["experience"] = "Beginner / Fresh Start"
    elif any(k in text_lower for k in ["1-3", "1 to 3", "१ ते ३", "1 साल", "2 साल", "1 वर्ष", "2 वर्षे"]):
        extracted["experience"] = "1-3 Years Experience"
    elif any(k in text_lower for k in ["3-5", "3 to 5", "३ ते ५", "3 साल", "4 साल", "3 वर्षे", "4 वर्षे"]):
        extracted["experience"] = "3-5 Years Experience"
    elif any(k in text_lower for k in ["5+", "5 years", "10 years", "५ वर्षांपेक्षा जास्त", "5 साल से अधिक", "दीर्घ अनुभव"]):
        extracted["experience"] = "5+ Years Experience"
    elif current_state == "BUSINESS_EXPERIENCE" and text_lower not in negative_words:
        extracted["experience"] = user_msg.strip()

    # 10. Resources
    res_list = []
    if any(k in text_lower for k in ["shed", "गोठा", "शेड", "बाड़ा"]):
        res_list.append("Cattle Shed / Storage Shed")
    if any(k in text_lower for k in ["land", "जमीन", "प्लॉट", "field", "शेती"]):
        res_list.append("Agricultural Land")
    if any(k in text_lower for k in ["water", "पाणी", "पानी", "well", "borewell", "विहीर", "बोअरवेल"]):
        res_list.append("Water Source / Borewell")
    if any(k in text_lower for k in ["electric", "वीज", "बिजली", "power", "मीटर"]):
        res_list.append("Electricity Connection")
    if any(k in text_lower for k in ["tractor", "ट्रॅक्टर", "vehicle", "गाडी", "वाहन"]):
        res_list.append("Transport / Tractor")
    if any(k in text_lower for k in ["shop", "दुकान", "counter", "जागा"]):
        res_list.append("Commercial Shop Space")
    if any(k in text_lower for k in ["none", "काहीही नाही", "कुछ नहीं", "no assets"]):
        res_list.append("No Prior Assets")
        
    if res_list:
        extracted["resources"] = res_list
    elif current_state == "BUSINESS_RESOURCES" and text_lower not in negative_words:
        extracted["resources"] = [user_msg.strip()]

    # 11. Existing Business (if in EXISTING_BUSINESS state)
    if current_state == "EXISTING_BUSINESS" and text_lower not in negative_words:
        extracted["existing_business"] = user_msg.strip()
        extracted["business_interest"] = user_msg.strip()

    # 12. Business Interest
    if any(k in text_lower for k in ["dairy", "दूध", "दुग्ध", "गौपालन"]):
        extracted["business_interest"] = "Dairy Farming"
    elif any(k in text_lower for k in ["poultry", "कुक्कुट", "मुर्गी"]):
        extracted["business_interest"] = "Poultry Farming"
    elif any(k in text_lower for k in ["mushroom", "मशरूम", "अळिंबी"]):
        extracted["business_interest"] = "Mushroom Farming"
    elif any(k in text_lower for k in ["spice", "मसाला", "मसाले"]):
        extracted["business_interest"] = "Spice Processing & Packaging"
    elif any(k in text_lower for k in ["flour", "chakki", "चक्की", "पीठ गिरणी", "आटा"]):
        extracted["business_interest"] = "Mini Flour Mill (Atta Chakki)"
    elif any(k in text_lower for k in ["beekeep", "honey", "मध", "मधुमक्खी"]):
        extracted["business_interest"] = "Beekeeping & Honey Production"
    elif any(k in text_lower for k in ["vermicompost", "गांडूळ", "केंचुआ"]):
        extracted["business_interest"] = "Vermicompost Production"
    elif any(k in text_lower for k in ["tailor", "शिलाई", "garment", "सिलाई"]):
        extracted["business_interest"] = "Rural Tailoring & Garment Unit"
    elif any(k in text_lower for k in ["goat", "शेळी", "बकरी"]):
        extracted["business_interest"] = "Goat Rearing & Breeding"
    elif current_state == "BUSINESS_INTEREST" and text_lower not in negative_words:
        extracted["business_interest"] = user_msg.strip()

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
    Determines next onboarding state progressively.
    Never re-asks fields already populated in UserProfile.
    """
    if not p.name or not str(p.name).strip():
        return "PERSONAL_NAME"

    if not p.intent or not str(p.intent).strip():
        return "USER_INTENT"

    if p.intent == "Expand an existing business" and (not p.existing_business or not str(p.existing_business).strip()):
        return "EXISTING_BUSINESS"

    if p.age is None:
        return "PERSONAL_AGE"

    if not p.gender or not str(p.gender).strip():
        return "PERSONAL_GENDER"

    if p.location and str(p.location).strip():
        if not p.district:
            p.district = str(p.location).strip()
        if not p.state:
            p.state = resolve_state_from_location(str(p.location).strip())

    if (not p.location or not str(p.location).strip()) and (not p.district or not str(p.district).strip()):
        return "PERSONAL_LOCATION"

    if not p.education or not str(p.education).strip():
        return "PERSONAL_EDUCATION"

    if not p.skills or len(p.skills) == 0:
        return "BUSINESS_SKILLS"

    if not p.experience or not str(p.experience).strip():
        return "BUSINESS_EXPERIENCE"

    if not p.resources or len(p.resources) == 0:
        return "BUSINESS_RESOURCES"

    if p.capital is None and p.available_investment is None:
        return "BUSINESS_CAPITAL"

    if not p.business_interest or not str(p.business_interest).strip():
        return "BUSINESS_INTEREST"

    # All 14 onboarding profile dimensions collected!
    if previous_state in PROFILE_COLLECTION_STATES or previous_state == "PROFILE_CONFIRMATION":
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
    inv_num = profile.available_investment if profile.available_investment is not None else profile.capital
    cap_val = f"₹{int(inv_num):,}" if inv_num is not None else "₹1,00,000"
    skills_text = ", ".join(profile.skills[:2]) if profile.skills else "general practical skills"
    res_text = ", ".join(profile.resources[:2]) if profile.resources else "standard assets"
    b_int = profile.business_interest or "Rural Micro-Enterprise"
    gender_text = profile.gender or "Not Specified"
    age_text = f"{profile.age} Years" if profile.age else "Not Specified"
    edu_text = profile.education or "General"
    intent_text = profile.intent or "Start a new business"

    quick_replies = []

    if state == "PERSONAL_NAME":
        if lang == "mr":
            reply = "नमस्कार! 👋 मी **आरंभ साथी** आहे — तुमचा हक्काचा ग्रामीण व्यवसाय सल्लागार.\n\nतुमचे नाव काय आहे?"
        elif lang == "hi":
            reply = "नमस्कार! 👋 मैं **आरंभ साथी** हूँ — आपका ग्रामीण व्यवसाय सलाहकार।\n\nआपका नाम क्या है?"
        else:
            reply = "Namaskar! 👋 I am **Aarambh Saathi** — your dedicated rural enterprise advisor.\n\nWhat is your name?"
        quick_replies = []

    elif state == "USER_INTENT":
        if lang == "mr":
            reply = f"छान वाटले भेटून, **{name}** जी! 👋\n\nमी तुम्हाला कशात मदत करू?"
            quick_replies = ["नवीन व्यवसाय सुरू करणे", "माझा व्यवसाय वाढवणे", "मला योग्य व्यवसाय सुचवा"]
        elif lang == "hi":
            reply = f"आपसे मिलकर खुशी हुई, **{name}** जी! 👋\n\nमैं आपकी किस प्रकार मदद करूँ?"
            quick_replies = ["नया व्यवसाय शुरू करना", "मौजूदा व्यवसाय बढ़ाना", "मुझे सही व्यवसाय सुझाएं"]
        else:
            reply = f"Nice to meet you, **{name}**! 👋\n\nWhat would you like help with?"
            quick_replies = ["Start a new business", "Expand an existing business", "I don't know what business to start"]

    elif state == "EXISTING_BUSINESS":
        if lang == "mr":
            reply = f"उत्तम, **{name}** जी! तुमचा सध्या कोणता **विद्यमान व्यवसाय** आहे जो तुम्हाला वाढवायचा आहे?"
            quick_replies = ["दुग्ध व्यवसाय / डेअरी", "किराणा दुकान", "शिलाई व कपडे", "पोल्ट्री फार्म"]
        elif lang == "hi":
            reply = f"बहुत अच्छा, **{name}** जी! आपका वर्तमान में कौन सा **व्यवसाय** है जिसे आप बढ़ाना चाहते हैं?"
            quick_replies = ["डेयरी व्यवसाय", "किराना दुकान", "सिलाई व गारमेंट", "पोल्ट्री फार्म"]
        else:
            reply = f"Great, **{name}**! Which **existing business** do you currently run and wish to expand?"
            quick_replies = ["Dairy Farming", "Grocery / Kirana Shop", "Tailoring & Garments", "Poultry Farming"]

    elif state == "PERSONAL_AGE":
        if lang == "mr":
            reply = f"योग्य शासकीय योजना व कर्ज योजनांची पात्रता तपासण्यासाठी: तुमचे **वय** किती आहे?"
            quick_replies = ["18 ते 25 वर्षे", "26 ते 35 वर्षे", "36 ते 50 वर्षे", "50+ वर्षे"]
        elif lang == "hi":
            reply = f"उचित सरकारी योजनाओं और ऋण पात्रता के लिए: आपकी **आयु (उम्र)** कितनी है?"
            quick_replies = ["18 से 25 वर्ष", "26 से 35 वर्ष", "36 से 50 वर्ष", "50+ वर्ष"]
        else:
            reply = f"To check eligible credit schemes and government subsidies: what is your **age**?"
            quick_replies = ["18-25 Years", "26-35 Years", "36-50 Years", "50+ Years"]

    elif state == "PERSONAL_GENDER":
        if lang == "mr":
            reply = f"महिला व विशेष प्रवर्गासाठी ३५% पर्यंत अतिरिक्त सरकारी अनुदान (Subsidy) उपलब्ध असते. तुमचे **लिंग** कोणते आहे?"
            quick_replies = ["महिला (Female)", "पुरुष (Male)", "इतर (Other)"]
        elif lang == "hi":
            reply = f"महिला व विशेष वर्गों के लिए 35% तक अतिरिक्त सरकारी सब्सिडी उपलब्ध होती है। आपका **लिंग** क्या है?"
            quick_replies = ["महिला (Female)", "पुरुष (Male)", "अन्य (Other)"]
        else:
            reply = f"Women entrepreneurs and special categories receive up to 35% higher government subsidies. What is your **gender**?"
            quick_replies = ["Female", "Male", "Other"]

    elif state == "PERSONAL_LOCATION":
        if lang == "mr":
            reply = f"स्थानिक बाजारपेठ व कच्च्या मालाचा अभ्यास करण्यासाठी: तुम्ही कोणत्या **गावात, तालुक्यात व जिल्ह्यात** राहता?"
            quick_replies = ["पुणे, महाराष्ट्र", "सातारा, महाराष्ट्र", "बारामती, पुणे", "कोल्हापूर, महाराष्ट्र"]
        elif lang == "hi":
            reply = f"स्थानीय बाजार मांग और कच्चे माल की उपलब्धता समझने के लिए: आप किस **गांव, तहसील व जिले** में रहते हैं?"
            quick_replies = ["पुणे, महाराष्ट्र", "सतारा, महाराष्ट्र", "बारामती, पुणे", "कोल्हापुर, महाराष्ट्र"]
        else:
            reply = f"To evaluate local market demand and raw material access: which **village/town, district, and state** do you live in?"
            quick_replies = ["Pune, Maharashtra", "Satara, Maharashtra", "Baramati, Pune", "Kolhapur, Maharashtra"]

    elif state == "PERSONAL_EDUCATION":
        if lang == "mr":
            reply = f"तुमचे **शिक्षण (Education)** कुठपर्यंत झाले आहे?"
            quick_replies = ["१०वी पास (10th)", "१२वी पास (12th)", "पदवीधर (Graduate)", "डिप्लोमा / ITI", "शालेय शिक्षण नाही"]
        elif lang == "hi":
            reply = f"आपकी **शिक्षा (Education)** कहाँ तक हुई है?"
            quick_replies = ["10वीं पास (10th)", "12वीं पास (12th)", "स्नातक (Graduate)", "डिप्लोमा / ITI", "अनौपचारिक"]
        else:
            reply = f"What is your highest level of **education**?"
            quick_replies = ["10th Pass", "12th Pass", "Graduate", "Diploma / ITI", "No Formal Schooling"]

    elif state == "BUSINESS_SKILLS":
        if lang == "mr":
            reply = f"तुमच्याकडे कोणती **प्रात्यक्षिक कौशल्ये किंवा कामाचा अनुभव** आहे?"
            quick_replies = ["पशुपालन व दुग्ध व्यवसाय", "सिलाई व टेलरिंग", "शेती व पीक काळजी", "दुकान / किरकोळ विक्री"]
        elif lang == "hi":
            reply = f"आपके पास कौन सा **व्यावहारिक कौशल या कार्य अनुभव** है?"
            quick_replies = ["पशुपालन व डेयरी", "सिलाई व गारमेंट", "खेती व फसल देखभाल", "दुकान / खुदरा बिक्री"]
        else:
            reply = f"What **practical hands-on skills** do you possess?"
            quick_replies = ["Cattle Rearing & Dairy", "Tailoring & Stitching", "Farming & Crop Care", "Retail & Shop Management"]

    elif state == "BUSINESS_EXPERIENCE":
        if lang == "mr":
            reply = f"या क्षेत्रात किंवा इतर कामात तुम्हाला किती **वर्षांचा अनुभव** आहे?"
            quick_replies = ["नवीन सुरुवात (Beginner)", "१ ते ३ वर्षे", "३ ते ५ वर्षे", "५ वर्षांपेक्षा जास्त"]
        elif lang == "hi":
            reply = f"इस क्षेत्र या अन्य कार्य में आपका लगभग कितना **अनुभव** है?"
            quick_replies = ["नई शुरुआत (Beginner)", "1 से 3 वर्ष", "3 से 5 वर्ष", "5 वर्ष से अधिक"]
        else:
            reply = f"How much **prior work/business experience** do you have?"
            quick_replies = ["Beginner / Fresh Start", "1-3 Years", "3-5 Years", "5+ Years Experience"]

    elif state == "BUSINESS_RESOURCES":
        if lang == "mr":
            reply = f"तुमच्याकडे आधीपासून कोणती **साधने किंवा जागा उपलब्ध** आहे? (उदा. जमीन, गोठा, दुकान जागा, विहीर पाणी)"
            quick_replies = ["जमीन व पाणी सोय", "गोठा / शेड", "दुकान / व्यावसायिक जागा", "काहीही साधने नाहीत"]
        elif lang == "hi":
            reply = f"आपके पास पहले से कौन से **संसाधन या स्थान उपलब्ध** हैं? (जैसे ज़मीन, पशु शेड, दुकान, पानी स्रोत)"
            quick_replies = ["ज़मीन व पानी स्रोत", "पशु शेड / गोठा", "दुकान / वाणिज्यिक स्थान", "कोई साधन उपलब्ध नहीं"]
        else:
            reply = f"What **physical assets or resources** do you currently have available?"
            quick_replies = ["Own Land & Water", "Cattle Shed / Storage", "Shop / Commercial Space", "No Prior Assets"]

    elif state == "BUSINESS_CAPITAL":
        if lang == "mr":
            reply = f"हा व्यवसाय सुरू करण्यासाठी तुम्ही स्वतःचे अंदाजे किती **भांडवल (बचत)** गुंतवू शकता? 💰"
            quick_replies = ["₹२५,०००", "₹५०,०००", "₹१ लाख", "₹२.५ लाख", "₹५ लाख+"]
        elif lang == "hi":
            reply = f"यह उद्यम शुरू करने के लिए आप अपनी बचत से लगभग कितनी **पूंजी** निवेश कर सकते हैं? 💰"
            quick_replies = ["₹25,000", "₹50,000", "₹1 लाख", "₹2.5 लाख", "₹5 लाख+"]
        else:
            reply = f"Approximately how much **personal investment (savings)** can you contribute to start? 💰"
            quick_replies = ["₹25,000", "₹50,000", "₹1 Lakh", "₹2.5 Lakhs", "₹5 Lakhs+"]

    elif state == "BUSINESS_INTEREST":
        if lang == "mr":
            reply = f"तुमच्या मनात आधीपासून कोणता **विशिष्ट व्यवसाय** आहे, की मी तुमच्या प्रोफाइलसाठी सर्वोत्कृष्ट पर्याय सुचवू?"
            quick_replies = ["सर्वोत्कृष्ट व्यवसाय सुचवा", "दुग्ध व्यवसाय (Dairy)", "मशरूम शेती", "पीठ गिरणी (Atta Chakki)"]
        elif lang == "hi":
            reply = f"क्या आपके मन में पहले से कोई **विशेष व्यवसाय** है, या मैं आपके प्रोफाइल अनुसार सर्वश्रेष्ठ विकल्प सुझाऊं?"
            quick_replies = ["सर्वश्रेष्ठ व्यवसाय सुझाएं", "डेयरी फार्मिंग", "मशरूम फार्मिंग", "आटा चक्की (Flour Mill)"]
        else:
            reply = f"Do you have a **specific business idea** in mind, or would you like me to recommend the best matching options for your profile?"
            quick_replies = ["Suggest Best Businesses", "Dairy Farming", "Mushroom Farming", "Mini Flour Mill"]

    elif state == "PROFILE_CONFIRMATION":
        if lang == "mr":
            reply = (
                f"🎉 **छान! मी तुमचे संपूर्ण प्रोफाइल समजून घेतले आहे.**\n\n"
                f"📋 **तुमचा प्रोफाइल सारांश:**\n"
                f"• **नाव:** {name}\n"
                f"• **उद्देश:** {intent_text}\n"
                f"• **वय व लिंग:** {age_text}, {gender_text}\n"
                f"• **ठिकाण:** {loc}, {profile.state or 'Maharashtra'}\n"
                f"• **शिक्षण:** {edu_text}\n"
                f"• **कौशल्ये व अनुभव:** {skills_text} ({profile.experience or 'Fresh'})\n"
                f"• **उपलब्ध साधने:** {res_text}\n"
                f"• **स्वतःची गुंतवणूक:** {cap_val}\n"
                f"• **इच्छित व्यवसाय:** {b_int}\n\n"
                f"आता आम्ही तुमच्यासाठी सर्वात जास्त नफा देणाऱ्या व्यवसायांचे विश्लेषण करू शकतो."
            )
            quick_replies = ["योग्य व्यवसाय शोधा", "माहिती तपासा / बदला"]
        elif lang == "hi":
            reply = (
                f"🎉 **शानदार! मैंने आपका पूरा प्रोफाइल समझ लिया है।**\n\n"
                f"📋 **आपका प्रोफाइल सारांश:**\n"
                f"• **नाम:** {name}\n"
                f"• **उद्देश्य:** {intent_text}\n"
                f"• **आयु व लिंग:** {age_text}, {gender_text}\n"
                f"• **स्थान:** {loc}, {profile.state or 'Maharashtra'}\n"
                f"• **शिक्षा:** {edu_text}\n"
                f"• **कौशल व अनुभव:** {skills_text} ({profile.experience or 'Fresh'})\n"
                f"• **उपलब्ध संसाधन:** {res_text}\n"
                f"• **व्यक्तिगत पूंजी:** {cap_val}\n"
                f"• **इच्छित व्यवसाय:** {b_int}\n\n"
                f"अब हम आपके लिए सर्वाधिक उपयुक्त एवं लाभदायक व्यवसायों का विश्लेषण शुरू कर सकते हैं।"
            )
            quick_replies = ["उपयुक्त व्यवसाय खोजें", "विवरण देखें / बदलें"]
        else:
            reply = (
                f"🎉 **Great! I have understood your profile.**\n\n"
                f"📋 **Your Structured Profile Summary:**\n"
                f"• **Name:** {name}\n"
                f"• **Intent:** {intent_text}\n"
                f"• **Age & Gender:** {age_text}, {gender_text}\n"
                f"• **Location:** {loc}, {profile.state or 'Maharashtra'}\n"
                f"• **Education:** {edu_text}\n"
                f"• **Skills & Experience:** {skills_text} ({profile.experience or 'Fresh'})\n"
                f"• **Available Assets:** {res_text}\n"
                f"• **Personal Investment:** {cap_val}\n"
                f"• **Business Interest:** {b_int}\n\n"
                f"Shall we now calculate and find the most profitable business opportunities tailored for you?"
            )
            quick_replies = ["Find Suitable Businesses", "Review / Edit My Details"]

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
            reply = f"अनुदान (Subsidy) ची अचूक टक्केवारी ठरवण्यासाठी, कृपया तुमचे **सामाजिक प्रवर्ग (General / OBC / SC / ST)** सांगा."
            quick_replies = ["General", "OBC", "SC", "ST"]
        elif lang == "hi":
            reply = f"सटीक सब्सिडी राशि और पात्रता के लिए, कृपया अपना **सामाजिक वर्ग (General / OBC / SC / ST)** बताएं।"
            quick_replies = ["General", "OBC", "SC", "ST"]
        else:
            reply = f"To calculate your exact subsidy entitlement percentage, please specify your **social category (General / OBC / SC / ST)**."
            quick_replies = ["General", "OBC", "SC", "ST"]

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
        else:
            project_cost = max(150000, int(user_cap) * 2)
            loan_amt     = max(0, project_cost - int(user_cap))
            monthly_revenue = int(project_cost * 0.25)
            monthly_profit  = int(monthly_revenue * 0.6)
            payback  = "12-18"
            machines = "Primary Processing & Production Equipment"
            scheme   = "PMEGP – 25%-35% Capital Subsidy | PM-MUDRA Loan"
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
        quick_replies = ["Find Suitable Businesses", "Review / Edit My Details"]

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
        if any(w in user_msg for w in ["आहे", "नाही", "माझं", "माझे", "करायचा", "पाहिजे", "गावात", "भांडवल", "करा"]):
            session_lang = "mr"
        elif any(w in user_msg for w in ["है", "नहीं", "मेरा", "मेरी", "करना", "चाहिए", "गांव", "पूंजी", "करें"]):
            session_lang = "hi"

    session["language"] = session_lang
    current_profile.language = session_lang

    msg_lower = user_msg.lower()

    # 1. Global Interceptor for direct business ideas & supplier queries
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

    if (matched_biz or asking_suppliers) and current_state not in PROFILE_COLLECTION_STATES:
        if matched_biz:
            current_profile.business_interest = matched_biz
        elif not current_profile.business_interest:
            current_profile.business_interest = "Dairy Farming"
        current_state = "EQUIPMENT_SUPPLIER"

    elif current_state == "PROFILE_CONFIRMATION":
        if any(k in msg_lower for k in ["find", "suitable", "recommend", "show", "yes", "continue", "confirm", "होय", "सही", "पुढे", "योग्य व्यवसाय", "व्यवसाय खोजें", "व्यवसाय शोधा"]):
            current_state = "RECOMMENDATION"
        elif any(k in msg_lower for k in ["edit", "change", "review", "बदल", "माहिती बदला", "विवरण बदलें", "संपादित"]):
            current_state = "PERSONAL_NAME"
            current_profile.name = None

    elif current_state in ["RECOMMENDATION", "BUSINESS_SELECTION"]:
        from backend.database import load_businesses_data
        from backend.recommendation import get_recommendations
        
        selected_name = None
        businesses = load_businesses_data()
        
        for b in businesses:
            if b["business_name"].lower() == msg_lower.strip():
                selected_name = b["business_name"]
                break
        
        if not selected_name:
            for b in businesses:
                if b["business_name"].lower() in msg_lower:
                    selected_name = b["business_name"]
                    break
        
        if not selected_name:
            for b in businesses:
                if msg_lower in b["business_name"].lower():
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
        current_state = "SUPPLIER_DONE"

    elif current_state == "SUPPLIER_DONE":
        if any(k in msg_lower for k in ["finance", "financial", "loan", "budget", "cost", "profit", "आर्थिक", "नफा"]):
            current_state = "FINANCIAL"
        elif any(k in msg_lower for k in ["scheme", "government", "subsidy", "pmegp", "mudra", "nabard", "योजना"]):
            current_state = "SCHEME_OPT_IN"
        elif any(k in msg_lower for k in ["dpr", "report", "download", "अहवाल", "रिपोर्ट"]):
            current_state = "DPR"
        elif any(k in msg_lower for k in ["no", "skip"]):
            current_state = "SCHEME_OPT_IN"
        else:
            current_state = "SUPPLIER_DONE"

    elif current_state == "FINANCIAL":
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

    # 4. Advance State Machine
    if current_state in PROFILE_COLLECTION_STATES:
        next_state = determine_current_state(updated_profile, current_state)
    elif matched_biz or asking_suppliers:
        next_state = current_state
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
    if not updated_profile.intent: missing_fields.append("Intent")
    if updated_profile.age is None: missing_fields.append("Age")
    if not updated_profile.gender: missing_fields.append("Gender")
    if not updated_profile.location and not updated_profile.district: missing_fields.append("Location")
    if not updated_profile.education: missing_fields.append("Education")
    if not updated_profile.skills: missing_fields.append("Skills")
    if updated_profile.capital is None and updated_profile.available_investment is None: missing_fields.append("Investment")

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
