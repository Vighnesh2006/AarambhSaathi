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
# Structure: { session_id: { "current_step": str, "profile": UserProfile, "language": str, "updated_at": datetime } }
SESSIONS: Dict[str, Dict[str, Any]] = {}

ORDERED_STEPS = [
    "name",
    "location",
    "district_state",
    "occupation",
    "skills",
    "capital",
    "resources",
    "business_interest",
    "goal",
    "scale",
    "constraints",
    "analysis"
]

def extract_capital_from_text(text: str) -> Optional[float]:
    """Helper regex to parse Indian capital formats in English, Hindi, Marathi."""
    t = text.lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "").strip()
    
    # Marathi / Hindi word numbers
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

    # 1.5 lakh / 1 lakh / 2 lac
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b', t)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000.0
    
    # 50k / 50 thousand / 50 hazaar
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:k|thousand|hazaar|hazar)\b', t)
    if k_match:
        return float(k_match.group(1)) * 1000.0

    # Plain numbers >= 1000
    num_match = re.search(r'\b(\d{4,8})\b', t)
    if num_match:
        return float(num_match.group(1))
        
    return None

def clean_name_string(raw: str) -> str:
    """Cleans common prefixes like 'My name is', 'I am', 'माझं नाव', 'मेरा नाम'."""
    val = raw.strip()
    patterns = [
        r'^(?:my\s+name\s+is|i\s+am|i\'m|myself)\s+',
        r'^(?:मेरा\s+नाम|नाम|मैं)\s+(?:है\s+)?',
        r'^(?:माझे\s+नाव|माझं\s+नाव|नाव|मी)\s+(?:आहे\s+)?',
    ]
    for p in patterns:
        val = re.sub(p, '', val, flags=re.IGNORECASE).strip()
    # Remove trailing punctuation or copula words
    val = re.sub(r'[\.\,\!\?]+$', '', val).strip()
    val = re.sub(r'\s+(?:है|आहे)$', '', val).strip()
    return val.capitalize() if val else raw.strip()

def clean_location_string(raw: str) -> str:
    """Cleans location prefixes like 'I live in', 'I am from', 'मी ... राहतो'."""
    val = raw.strip()
    patterns = [
        r'^(?:i\s+live\s+in|i\s+stay\s+in|i\s+am\s+from|from|living\s+in|at)\s+',
        r'^(?:मैं\s+)?(?:रहता\s+हूँ|रहती\s+हूँ|से\s+हूँ|का\s+हूँ|में\s+रहता\s+हूँ)',
        r'^(?:मी\s+)?(?:येथील\s+आहे|येथे\s+राहतो|येथे\s+राहते|मध्ये\s+राहतो|गाव|गावाचे\s+नाव)\s*',
    ]
    for p in patterns:
        val = re.sub(p, '', val, flags=re.IGNORECASE).strip()
    # Also remove common suffixes like "in pune" -> "Pune"
    val = re.sub(r'\b(?:में\s+रहता\s+हूँ|में\s+रहती\s+हूँ|से\s+हूँ|येथे\s+राहतो|येथे\s+राहते|मध्ये\s+राहतो)$', '', val).strip()
    val = re.sub(r'[\.\,\!\?]+$', '', val).strip()
    return val.capitalize() if val else raw.strip()

MAHARASHTRA_DISTRICTS = {
    "pune", "satara", "kolhapur", "sangli", "solapur", "ahmednagar", "nashik", 
    "aurangabad", "chhatrapati sambhajinagar", "nagpur", "amravati", "jalgaon", 
    "dhule", "nanded", "latur", "beed", "osmanabad", "dharashiv", "raigad", 
    "ratnagiri", "sindhudurg", "thane", "palghar", "wardha", "yavatmal", 
    "bhandara", "gondia", "chandrapur", "gadchiroli", "buldhana", "akola", 
    "washim", "hingoli", "jalna", "nandurbar", "mumbai", "baramati", "shirdi", 
    "karad", "pandharpur", "malegaon", "ichalkaranji", "alibag"
}

OTHER_INDIAN_STATES = {
    "Gujarat": ["surat", "ahmedabad", "vadodara", "rajkot", "gandhinagar", "bhavnagar", "jamnagar"],
    "Karnataka": ["bangalore", "bengaluru", "belgaum", "belagavi", "mysore", "mysuru", "hubli", "dharwad", "mangalore"],
    "Madhya Pradesh": ["indore", "bhopal", "jabalpur", "gwalior", "ujjain"],
    "Rajasthan": ["jaipur", "jodhpur", "udaipur", "kota", "bikaner"],
    "Uttar Pradesh": ["lucknow", "kanpur", "varanasi", "agra", "prayagraj", "gorakhpur"],
    "Bihar": ["patna", "gaya", "muzaffarpur", "bhagalpur"],
    "Telangana": ["hyderabad", "warangal", "nizamabad"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "salem"],
    "Punjab": ["ludhiana", "amritsar", "jalandhar", "patiala"]
}

def resolve_state_from_location(loc: str) -> str:
    """Auto-resolves Indian state from village/district name without asking redundant questions."""
    if not loc:
        return "Maharashtra"
    l = loc.lower().strip()
    for state_name, city_list in OTHER_INDIAN_STATES.items():
        if any(c in l for c in city_list):
            return state_name
    return "Maharashtra"

def extract_entities_locally(user_msg: str, current_step: str) -> Dict[str, Any]:
    """Fallback / rule-based entity extractor for multi-language inputs."""
    extracted = {}
    text_lower = user_msg.lower().strip()
    
    # Negative words guard (not a name or valid answer)
    negative_words = [
        "i don't know", "dont know", "not sure", "pata nahi", "mahit nahi", "nahi", "no", "yes", "none", 
        "hello", "hi", "namaskar", "namaste", "hey", "नमस्कार", "नमस्ते", "not", "scratch", "guidance",
        "guide", "help", "start", "starting", "beginning", "advice", "option", "options"
    ]
    invalid_name_words = {
        "not", "sure", "interested", "planning", "looking", "here", "just", "trying", "working", 
        "going", "ready", "willing", "able", "farmer", "daily", "labour", "skilled", "student", 
        "housewife", "homemaker", "businessman", "shopkeeper", "shuru", "ahe", "nahi", "ka", "ki", 
        "from", "scratch", "now", "today", "tomorrow", "want", "seeking", "asking", "someone"
    }
    invalid_loc_words = {
        "scratch", "today", "now", "beginning", "here", "there", "home", "farm", "village", 
        "city", "town", "start", "starting", "scratch.", "market", "field", "area", "region"
    }

    # If message is a general query asking for guidance from scratch, do not extract false entities
    if "not sure" in text_lower or "from scratch" in text_lower or "guide me" in text_lower or "मार्गदर्शन" in text_lower or "मार्गदर्शन हवे" in text_lower:
        return extracted

    # 1. Capital extraction
    cap = extract_capital_from_text(user_msg)
    if cap is not None:
        extracted["capital"] = cap

    # 2. Name extraction (pattern-based or step-based)
    name_match = re.search(r'\b(?:my\s+name\s+is|i\s+am|i\'m|myself|मेरा\s+नाम|माझे\s+नाव|माझं\s+नाव)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)\b', user_msg, re.IGNORECASE)
    if name_match:
        cand = name_match.group(1).strip()
        if cand.lower() not in negative_words and cand.lower() not in invalid_name_words:
            extracted["name"] = cand.capitalize()
    elif current_step == "name" and len(user_msg.split()) <= 4:
        cleaned = clean_name_string(user_msg)
        if cleaned.lower() not in negative_words and cleaned.lower() not in invalid_name_words:
            extracted["name"] = cleaned

    # 3. Location extraction with automatic District and State resolution
    loc_match = re.search(r'\b(?:from|living\s+in|staying\s+in|live\s+in|गाव|राहतो|राहते)\s+([A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+(?:\s*,\s*[A-Z\u0900-\u097F][a-zA-Z\u0900-\u097F]+)?)\b', user_msg, re.IGNORECASE)
    if loc_match:
        raw_loc = loc_match.group(1).strip()
        if raw_loc.lower() not in invalid_loc_words and raw_loc.lower() not in negative_words:
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
    elif current_step == "location":
        loc = clean_location_string(user_msg)
        if loc.lower() not in negative_words and loc.lower() not in invalid_loc_words:
            if "," in loc:
                parts = [clean_location_string(p) for p in loc.split(",")]
                extracted["location"] = parts[0]
                extracted["district"] = parts[0]
                extracted["state"] = parts[1] if len(parts) > 1 and parts[1] else resolve_state_from_location(parts[0])
            else:
                extracted["location"] = loc
                extracted["district"] = loc
                extracted["state"] = resolve_state_from_location(loc)

    elif current_step == "district_state":
        parts = [clean_location_string(p) for p in user_msg.split(",")]
        if len(parts) >= 2:
            extracted["district"] = clean_location_string(parts[0])
            extracted["state"] = clean_location_string(parts[1])
        else:
            d = clean_location_string(user_msg)
            extracted["district"] = d
            extracted["state"] = resolve_state_from_location(d)

    # 4. Occupation extraction
    if "farm" in text_lower or "शेत" in text_lower or "किसान" in text_lower or "कृषि" in text_lower:
        extracted["occupation"] = "Farmer"
    elif "tailor" in text_lower or "शिलाई" in text_lower or "सिलाई" in text_lower:
        extracted["occupation"] = "Tailor"
    elif current_step == "occupation":
        occ = user_msg.strip()
        patterns = [r'^(?:i\s+am\s+a|i\s+am\s+an|i\s+am|i\s+work\s+as|working\s+as)\s+', r'^(?:मैं\s+एक|मैं|हम)\s+']
        for p in patterns:
            occ = re.sub(p, '', occ, flags=re.IGNORECASE).strip()
        occ = re.sub(r'[\.\,\!\?]+$', '', occ).strip()
        if occ.lower() not in negative_words:
            extracted["occupation"] = occ.capitalize()

    # 5. Skills & Experience
    skills_found = []
    if "cattle" in text_lower or "गाय" in text_lower or "म्हैस" in text_lower or "पशु" in text_lower or "animal" in text_lower:
        skills_found.append("Cattle Rearing & Animal Husbandry")
        extracted["experience"] = "Cattle handling and dairy experience"
    if "tailor" in text_lower or "शिलाई" in text_lower or "सिलाई" in text_lower or "sewing" in text_lower:
        skills_found.append("Tailoring & Garments")
    if "machine" in text_lower or "मशीन" in text_lower or "यंत्र" in text_lower:
        skills_found.append("Machinery Operation")
    if skills_found:
        extracted["skills"] = skills_found
    elif current_step == "skills" and text_lower not in negative_words:
        extracted["skills"] = [user_msg.strip()]
        extracted["experience"] = user_msg.strip()

    # 6. Resources
    res_list = []
    if "shed" in text_lower or "गोठा" in text_lower or "शेड" in text_lower or "बाड़ा" in text_lower:
        res_list.append("Cattle Shed / Storage Shed")
    if "land" in text_lower or "जमीन" in text_lower or "प्लॉट" in text_lower or "field" in text_lower:
        res_list.append("Agricultural Land")
    if "water" in text_lower or "पाणी" in text_lower or "पानी" in text_lower or "well" in text_lower or "borewell" in text_lower or "विहीर" in text_lower:
        res_list.append("Water Source / Borewell")
    if "electric" in text_lower or "वीज" in text_lower or "बिजली" in text_lower or "power" in text_lower:
        res_list.append("Electricity Connection")
    if "tractor" in text_lower or "ट्रॅक्टर" in text_lower or "ट्रैक्टर" in text_lower or "vehicle" in text_lower:
        res_list.append("Transport / Tractor")
    if res_list:
        extracted["resources"] = res_list
    elif current_step == "resources" and text_lower not in negative_words:
        extracted["resources"] = [user_msg.strip()]

    # 7. Keyword business extraction (independent of step)
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
        if not extracted.get("skills"):
            extracted["skills"] = ["Cultivation", "Hygiene Management", "Climate Control"]
    elif "spice" in text_lower or "मसाला" in text_lower or "मसाले" in text_lower or "pulverizer" in text_lower:
        extracted["business_interest"] = "Spice Processing & Packaging"
        if not extracted.get("skills"):
            extracted["skills"] = ["Spice Grinding", "Packaging", "Quality Check"]
    elif "flour" in text_lower or "chakki" in text_lower or "चक्की" in text_lower or "पीठ गिरणी" in text_lower or "आटा" in text_lower:
        extracted["business_interest"] = "Mini Flour Mill (Atta Chakki)"
    elif "beekeep" in text_lower or "honey" in text_lower or "मध" in text_lower or "मधुमक्खी" in text_lower:
        extracted["business_interest"] = "Beekeeping & Honey Production"
    elif "vermicompost" in text_lower or "गांडूळ" in text_lower or "केंचुआ" in text_lower or "खत" in text_lower:
        extracted["business_interest"] = "Vermicompost Production"
    elif "tailor" in text_lower or "शिलाई" in text_lower or "garment" in text_lower:
        extracted["business_interest"] = "Rural Tailoring & Garment Unit"
    elif "goat" in text_lower or "शेळी" in text_lower or "बकरी" in text_lower:
        extracted["business_interest"] = "Goat Rearing & Breeding"
    elif "solar" in text_lower or "सौर" in text_lower:
        extracted["business_interest"] = "Solar Food Dryer"
    elif current_step == "business_interest" and text_lower not in negative_words:
        extracted["business_interest"] = user_msg.strip()

    return extracted

EXTRACTION_SYSTEM_PROMPT = """You are an accurate, structured entity extraction engine for a rural business advisory chatbot in India.
Your SOLE job is to extract user profile attributes from the user's message into a strict JSON object.

Extract only values explicitly stated or clearly implied:
- name: string or null
- location: village or city name, or null
- district: district name or null
- state: state name or null
- occupation: current job/profession or null
- skills: array of skill strings or empty array []
- experience: experience summary string or null
- capital: numeric amount in INR (e.g., '1 lakh' -> 100000, '50 thousand' -> 50000, '25000' -> 25000) or null
- resources: array of physical resource strings (e.g. land, shed, water, electricity, tractor, shop) or empty array []
- business_interest: string name of business they want to start or null
- goal: business goal or null
- scale: business scale ("small", "medium", "large") or null
- constraints: array of constraint strings or empty array []
- is_unclear_or_unknown: boolean (true if user says "I don't know", "not sure", "pata nahi", "माहित नाही")

OUTPUT STRICT JSON ONLY:
```json
{
  "name": null,
  "location": null,
  "district": null,
  "state": null,
  "occupation": null,
  "skills": [],
  "experience": null,
  "capital": null,
  "resources": [],
  "business_interest": null,
  "goal": null,
  "scale": null,
  "constraints": [],
  "is_unclear_or_unknown": false
}
```
"""

def extract_entities_with_llm(user_msg: str, current_step: str, known_profile: UserProfile, lang: str) -> Dict[str, Any]:
    """Uses Gemini LLM strictly for entity extraction, combined with local fallbacks."""
    extracted = extract_entities_locally(user_msg, current_step)

    if not GEMINI_API_KEY:
        return extracted

    prompt = f"""Current Step in Dialog: {current_step}
User Message: "{user_msg}"
Existing Known Profile: {json.dumps(known_profile.model_dump(), ensure_ascii=False)}
Language: {lang}

Extract all profile attributes present in the message:"""

    raw_json = None
    for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=EXTRACTION_SYSTEM_PROMPT
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                raw_json = resp.text.strip()
                break
        except Exception as e:
            continue

    if raw_json:
        try:
            clean = raw_json
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean)
            for k, v in data.items():
                if v is not None and v != "" and v != []:
                    if k in ["skills", "resources", "constraints"]:
                        existing_list = extracted.get(k, [])
                        if isinstance(v, list):
                            extracted[k] = list(set(existing_list + [str(i).strip() for i in v if str(i).strip()]))
                    else:
                        extracted[k] = v
        except Exception as e:
            pass

    return extracted

def merge_profile_entities(existing: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
    """Safely updates existing profile with newly extracted entities without overwriting known values with None."""
    d = existing.model_dump()
    for k, v in new_data.items():
        if k in ["is_unclear_or_unknown"]:
            continue
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

def determine_current_step(p: UserProfile) -> str:
    """
    Checks missing fields with smart auto-resolution and fast path:
    1. name
    2. location (auto-resolves district & state)
    3. occupation
    4. skills / experience
    5. capital
    6. business_interest
    -> analysis (when minimum profile is ready)
    """
    if not p.name or not str(p.name).strip():
        return "name"

    # Auto-resolve district and state if location is present
    if p.location and str(p.location).strip():
        if not p.district:
            p.district = str(p.location).strip()
        if not p.state:
            p.state = resolve_state_from_location(str(p.location).strip())

    if not p.location or not str(p.location).strip():
        return "location"

    # Fast track: If user already provided capital AND (interest OR skills OR occupation), ready for recommendations!
    if p.capital is not None and (p.business_interest or (p.skills and len(p.skills) > 0) or p.occupation):
        return "analysis"

    if not p.occupation or not str(p.occupation).strip():
        return "occupation"
    if (not p.skills or len(p.skills) == 0) and (not p.experience or not str(p.experience).strip()):
        return "skills"
    if p.capital is None:
        return "capital"
    if not p.business_interest or not str(p.business_interest).strip():
        return "business_interest"
    
    return "analysis"

def build_acknowledgment_and_question(
    next_step: str,
    profile: UserProfile,
    extracted: Dict[str, Any],
    lang: str,
    user_msg: str
) -> (str, List[str]):
    """
    Builds a natural language acknowledgment of user's input + next question
    in English, Hindi, or Marathi.
    """
    name = profile.name or ""
    
    # 1. Generate Acknowledgment based on what was just extracted
    ack_en = ""
    ack_hi = ""
    ack_mr = ""

    if "business_interest" in extracted and extracted["business_interest"]:
        b_int = extracted["business_interest"]
        ack_en = f"Great interest in {b_int}!"
        ack_hi = f"{b_int} में आपकी रुचि बहुत अच्छी है!"
        ack_mr = f"{b_int} सुरू करण्याची तुमची निवड उत्तम आहे!"
    elif "resources" in extracted and extracted["resources"]:
        res_text = ", ".join(extracted["resources"][:2])
        ack_en = f"Having {res_text} is a valuable head start!"
        ack_hi = f"{res_text} का होना बहुत बड़ा फायदा है!"
        ack_mr = f"{res_text} असणे ही मोठी जमेची बाजू आहे!"
    elif "capital" in extracted and extracted["capital"] is not None:
        cap_val = f"₹{int(extracted['capital']):,}"
        ack_en = f"Noted {cap_val} investment capital."
        ack_hi = f"नोट कर लिया, {cap_val} की निवेश क्षमता।"
        ack_mr = f"नोंद केली, {cap_val} गुंतवणुकीची क्षमता."
    elif "skills" in extracted and extracted["skills"]:
        sk = ", ".join(extracted["skills"][:2])
        ack_en = f"Great experience with {sk}!"
        ack_hi = f"{sk} का अनुभव बहुत मूल्यवान है!"
        ack_mr = f"{sk} चा अनुभव खूप फायदेशीर आहे!"
    elif "occupation" in extracted and extracted["occupation"]:
        occ = extracted["occupation"]
        ack_en = f"Understood, working as {occ} provides a great foundation!"
        ack_hi = f"समझ गया, {occ} के रूप में आपका अनुभव बहुत उपयोगी है!"
        ack_mr = f"उत्तम, {occ} म्हणून तुमचा अनुभव खूप उपयुक्त ठरेल!"
    elif "district" in extracted and extracted["district"]:
        dist = extracted["district"]
        ack_en = f"Got it, {dist} district!"
        ack_hi = f"समझ गया, {dist} जिला!"
        ack_mr = f"समजले, {dist} जिल्हा!"
    elif "location" in extracted and extracted["location"]:
        loc = extracted["location"]
        ack_en = f"Great, {loc} is a promising region!"
        ack_hi = f"बहुत बढ़िया, {loc} एक अच्छा क्षेत्र है!"
        ack_mr = f"छान, {loc} हे एक उत्तम ठिकाण आहे!"
    elif "name" in extracted and extracted["name"]:
        ack_en = f"Nice to meet you, {extracted['name']}!"
        ack_hi = f"आपसे मिलकर खुशी हुई, {extracted['name']} जी!"
        ack_mr = f"छान वाटलं भेटून, {extracted['name']}!"

    # 2. Generate Next Question & Suggested Quick Replies
    q_en = ""
    q_hi = ""
    q_mr = ""
    quick_replies = []

    if next_step == "name":
        q_en = "Namaskar! 👋 What is your name?"
        q_hi = "नमस्कार! 👋 आपका नाम क्या है?"
        q_mr = "नमस्कार! 👋 आपले नाव काय आहे?"
        quick_replies = ["Rahul", "Pooja", "Suresh", "Ramesh"]

    elif next_step == "location":
        q_en = f"Which village or city are you from?"
        q_hi = f"आप किस गांव या शहर से हैं?"
        q_mr = f"तुम्ही कोणत्या गावात किंवा शहरात राहता?"
        quick_replies = ["Pune", "Satara", "Kolhapur", "Nashik", "Nagpur", "Baramati"]

    elif next_step == "district_state":
        q_en = f"Which district and state is your village located in?"
        q_hi = f"आपका गांव किस जिले और राज्य में स्थित है?"
        q_mr = f"तुमचे गाव कोणत्या जिल्ह्यात आणि राज्यात आहे?"
        quick_replies = ["Pune, Maharashtra", "Satara, Maharashtra", "Ahmednagar, Maharashtra", "Solapur, Maharashtra"]

    elif next_step == "occupation":
        q_en = f"What work do you currently do?"
        q_hi = f"वर्तमान में आप क्या काम या खेती करते हैं?"
        q_mr = f"सध्या तुम्ही काय काम किंवा व्यवसाय करता?"
        quick_replies = ["Farmer / शेतकरी", "Daily Wage / कामगार", "Self Employed / छोटे व्यापारी", "Homemaker / गृहिणी"]

    elif next_step == "skills":
        q_en = f"What skills or experience do you have?"
        q_hi = f"आपके पास क्या कौशल या पिछला अनुभव है?"
        q_mr = f"तुमच्याकडे कोणती कौशल्ये किंवा कामाचा अनुभव आहे?"
        quick_replies = ["Cattle handling / पशुपालन", "Tailoring / सिलाई", "Farming & Agriculture", "Machinery operation"]

    elif next_step == "capital":
        q_en = f"How much money can you invest?"
        q_hi = f"आप अपना व्यवसाय शुरू करने के लिए कितने पैसे लगा सकते हैं?"
        q_mr = f"नवीन व्यवसाय सुरू करण्यासाठी तुम्ही किती भांडवल गुंतवू शकता?"
        quick_replies = ["₹50,000", "₹1 Lakh (₹1,00,000)", "₹2 Lakhs (₹2,00,000)", "₹5 Lakhs"]

    elif next_step == "resources":
        q_en = f"Do you already have resources such as land, cattle shed, equipment, or livestock?"
        q_hi = f"क्या आपके पास पहले से जमीन, पशु शेड, उपकरण या पशुधन जैसी सुविधाएं हैं?"
        q_mr = f"तुमच्याकडे आधीपासून जमीन, गोठा, यंत्रे किंवा पशुधन अशी काही साधने आहेत का?"
        quick_replies = ["I have land and water", "I have a cattle shed", "I have a small shop space", "No resources yet"]

    elif next_step == "business_interest":
        q_en = f"What business are you interested in?"
        q_hi = f"आप किस व्यवसाय में रुचि रखते हैं?"
        q_mr = f"तुम्हाला कोणता व्यवसाय सुरू करण्यात स्वारस्य आहे?"
        quick_replies = ["Dairy farming", "Mushroom farming", "Spice processing", "Poultry farming", "Mini Flour mill"]

    elif next_step == "analysis":
        # Minimum profile complete! Generate top 3 recommendations summary
        from backend.recommendation import get_recommendations
        rec_summary_en = ""
        rec_summary_hi = ""
        rec_summary_mr = ""
        
        try:
            rec_res = get_recommendations(profile, top_n=3)
            recs = rec_res.recommendations
            if recs:
                items_en = [f"{i+1}. {r.business_name} (Match: {r.overall_score:.0f}%) — Est. Cost: ₹{r.required_investment:,.0f}" for i, r in enumerate(recs)]
                items_hi = [f"{i+1}. {r.business_name} (मैच स्कोर: {r.overall_score:.0f}%) — अनुमानित लागत: ₹{r.required_investment:,.0f}" for i, r in enumerate(recs)]
                items_mr = [f"{i+1}. {r.business_name} (साम्य: {r.overall_score:.0f}%) — अंदाजे गुंतवणूक: ₹{r.required_investment:,.0f}" for i, r in enumerate(recs)]
                
                rec_summary_en = "\n\n🏆 Top 3 Recommended Businesses for You:\n" + "\n".join(items_en) + "\n\n📊 Feasibility: High Local Opportunity\n💰 Financial Structuring: Up to 90% Loan Eligibility under PMEGP / MUDRA\n🏛️ Matched Schemes: PMEGP, PMFME, MUDRA Yojana\n⚙️ Machinery & Suppliers: Required equipment catalog matched"
                rec_summary_hi = "\n\n🏆 आपके लिए टॉप 3 व्यावसायिक सिफारिशें:\n" + "\n".join(items_hi) + "\n\n📊 स्थानीय व्यवहार्यता: उच्च अवसर\n💰 वित्तीय योजना: 90% तक ऋण सुविधा (PMEGP / मुद्रा)\n🏛️ सरकारी योजनाएं: PMEGP, PMFME, मुद्रा योजना\n⚙️ आवश्यक मशीनें व सप्लायर: तैयार हैं"
                rec_summary_mr = "\n\n🏆 तुमच्यासाठी टॉप ३ व्यवसाय शिफारसी:\n" + "\n".join(items_mr) + "\n\n📊 स्थानिक संभाव्यता: उत्तम संधी\n💰 वित्तीय आराखडा: ९०% पर्यंत कर्ज पात्रता (PMEGP / MUDRA)\n🏛️ शासकीय योजना: PMEGP, PMFME, मुद्रा योजना\n⚙️ आवश्यक यंत्रसामग्री: पुरवठादार यादी तयार आहे"
        except Exception as e:
            print(f"[Chatbot Analysis Recommendation Exception]: {e}")

        q_en = f"Thank you {name}! I have gathered all required details. I have analyzed your profile across our 90-business rural catalogue.{rec_summary_en}\n\nYou can inspect the live decision cards and financial plan below!"
        q_hi = f"धन्यवाद {name} जी! मुझे आपका प्रोफ़ाइल तैयार करने के लिए सभी आवश्यक जानकारी मिल गई है।{rec_summary_hi}\n\nनीचे दिए गए कार्ड्स में विस्तृत रिपोर्ट देखें!"
        q_mr = f"धन्यवाद {name}! तुमच्या व्यवसायाची रूपरेषा ठरवण्यासाठी आवश्यक सर्व माहिती मिळाली आहे.{rec_summary_mr}\n\nखालील कार्ड्समध्ये सविस्तर विश्लेषण आणि योजना पहा!"
        quick_replies = ["View Top 3 Recommendations", "Check Financial & EMI Plan", "View Government Schemes", "See Setup Machinery"]

    # Combine Acknowledgment + Question smoothly
    if lang == "mr":
        reply = f"{ack_mr} {q_mr}".strip() if ack_mr else q_mr
    elif lang == "hi":
        reply = f"{ack_hi} {q_hi}".strip() if ack_hi else q_hi
    else:
        reply = f"{ack_en} {q_en}".strip() if ack_en else q_en

    return reply, quick_replies

def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Main state machine orchestrator for GramVantage / Aarambh Saathi Chatbot.
    Enforces persistent session state, entity extraction, deterministic state transition,
    and acknowledgment + next question generation.
    """
    # 1. Retrieve or Create Session
    session_id = request.session_id or str(uuid.uuid4())[:12]
    user_msg = (request.message or "").strip()
    req_lang = request.language or "en"

    if session_id not in SESSIONS:
        # Initialize session state
        initial_profile = request.profile or UserProfile(language=req_lang)
        initial_step = determine_current_step(initial_profile)
        SESSIONS[session_id] = {
            "current_step": initial_step,
            "profile": initial_profile,
            "language": req_lang,
            "created_at": datetime.now()
        }
    
    session = SESSIONS[session_id]
    current_profile = session.get("profile", UserProfile())
    session_lang = req_lang or session.get("language", "en")

    # If frontend supplied profile data that is more updated, sync it
    if request.profile:
        current_profile = merge_profile_entities(current_profile, request.profile.model_dump())
        session["profile"] = current_profile

    current_step = determine_current_step(current_profile)
    session["current_step"] = current_step

    # Detect language from input if Hindi/Marathi characters exist
    if re.search(r'[\u0900-\u097F]', user_msg):
        # Contains Devanagari script (Hindi or Marathi)
        if any(w in user_msg for w in ["आहे", "नाही", "माझं", "माझे", "करायचा", "पाहिजे", "गावात", "शहरात", "भांडवल"]):
            session_lang = "mr"
        elif any(w in user_msg for w in ["है", "नहीं", "मेरा", "मेरी", "करना", "चाहिए", "गांव", "पूंजी"]):
            session_lang = "hi"

    session["language"] = session_lang
    current_profile.language = session_lang

    # 2. Extract Entities from User Message
    extracted_data = extract_entities_with_llm(
        user_msg=user_msg,
        current_step=current_step,
        known_profile=current_profile,
        lang=session_lang
    )

    # 3. Check for Unclear/Invalid Answers at critical steps (Validation)
    is_unclear = extracted_data.get("is_unclear_or_unknown", False) or user_msg.lower() in [
        "i don't know", "dont know", "not sure", "pata nahi", "mahit nahi", "माहित नाही", "पता नहीं", "no idea"
    ]

    if is_unclear and current_step == "capital" and current_profile.capital is None:
        # User is unsure about capital
        if session_lang == "mr":
            clarification = "काही हरकत नाही! तुम्ही अंदाजे रक्कम सांगू शकता, जसे की ₹५०,०००, ₹१ लाख किंवा ₹२ लाख."
            quick_replies = ["₹50,000", "₹1,00,000", "₹2,00,000", "₹5,00,000"]
        elif session_lang == "hi":
            clarification = "कोई बात नहीं! आप एक अनुमानित बजट बता सकते हैं, जैसे ₹50,000, ₹1 लाख या ₹2 लाख।"
            quick_replies = ["₹50,000", "₹1,00,000", "₹2,00,000", "₹5,00,000"]
        else:
            clarification = "No problem! You can give me an approximate amount, such as ₹50,000, ₹1 lakh, or ₹2 lakh."
            quick_replies = ["₹50,000", "₹1,00,000", "₹2,00,000", "₹5,00,000"]

        return ChatResponse(
            session_id=session_id,
            current_step="capital",
            reply=clarification,
            updated_profile=current_profile,
            is_profile_ready=False,
            missing_fields=["Available Capital"],
            suggested_quick_replies=quick_replies,
            language=session_lang
        )

    # 4. Update Profile with Extracted Entities
    updated_profile = merge_profile_entities(current_profile, extracted_data)
    session["profile"] = updated_profile

    # 5. Determine Next Step
    next_step = determine_current_step(updated_profile)
    session["current_step"] = next_step

    # 6. Generate Acknowledgment + Next Question
    reply_text, quick_replies = build_acknowledgment_and_question(
        next_step=next_step,
        profile=updated_profile,
        extracted=extracted_data,
        lang=session_lang,
        user_msg=user_msg
    )

    # 7. Calculate Missing Fields & Profile Readiness
    is_ready = (next_step == "analysis")
    missing_fields = []
    if not updated_profile.name: missing_fields.append("Name")
    if not updated_profile.location or not updated_profile.district: missing_fields.append("Location/District")
    if not updated_profile.occupation: missing_fields.append("Occupation")
    if not updated_profile.skills and not updated_profile.experience: missing_fields.append("Skills / Experience")
    if updated_profile.capital is None: missing_fields.append("Capital")
    if not updated_profile.resources: missing_fields.append("Resources")
    if not updated_profile.business_interest: missing_fields.append("Business Interest")

    # Debug Logging (Safe for Windows console)
    try:
        debug_output = f"""
==================================================
--- CHAT SESSION DEBUG ---
SESSION: {session_id}
CURRENT STEP (Incoming): {current_step}
USER MESSAGE: {user_msg}
EXTRACTED DATA: {json.dumps(extracted_data, ensure_ascii=True)}
UPDATED PROFILE: {json.dumps(updated_profile.model_dump(), ensure_ascii=True)}
NEXT STEP: {next_step}
IS PROFILE READY: {is_ready}
REPLY: {reply_text}
==================================================
"""
        print(debug_output.encode('ascii', errors='backslashreplace').decode('ascii'))
    except Exception:
        pass

    return ChatResponse(
        session_id=session_id,
        current_step=next_step,
        reply=reply_text,
        updated_profile=updated_profile,
        is_profile_ready=is_ready,
        missing_fields=missing_fields,
        suggested_quick_replies=quick_replies[:4],
        language=session_lang
    )
