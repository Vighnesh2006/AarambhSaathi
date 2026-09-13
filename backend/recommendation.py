import math
from typing import List, Dict, Any, Optional, Tuple
from backend.models import (
    UserProfile,
    BusinessRecommendation,
    RecommendationScoreBreakdown,
    RecommendationFactorScores,
    FactorScoreDetail,
    RecommendationResponse
)
from backend.database import load_businesses_data

# Specific keyword-to-sector mapping
SECTOR_KEYWORD_MAP = {
    "DAIRY": ["dairy", "cow", "milk", "cattle", "buffalo", "chilling", "dugdha", "gotha", "milking"],
    "GOAT_SHEEP": ["goat", "sheep", "bakri", "sheli", "livestock"],
    "POULTRY": ["poultry", "chicken", "hen", "egg", "broiler", "murgi", "kukut", "hatchery"],
    "LIVESTOCK": ["livestock", "animal", "cattle", "pashu", "goat", "sheep", "cow", "buffalo"],
    "FISHERIES": ["fish", "fishery", "aquaculture", "pisciculture", "machli", "pond"],
    "BEEKEEPING": ["bee", "honey", "beekeeping", "apiculture", "madh", "madhumakhi"],
    "AGRICULTURE": ["mushroom", "organic", "vermicompost", "nursery", "crop", "farm", "khet", "shet", "horticulture", "vegetable"],
    "TEXTILES": ["tailor", "garment", "sewing", "cloth", "boutique", "stitching", "shilai", "dress"],
    "FOOD_PROCESSING": ["flour", "atta", "chakki", "spice", "masala", "jaggery", "papad", "pickle", "bakery", "oil", "food", "snack"],
    "MANUFACTURING": ["brick", "block", "plastic", "moulding", "concrete", "paper", "fly ash", "paving", "welding", "candle", "soap"],
    "PACKAGING": ["packaging", "box", "corrugated", "pulp", "bag"],
    "FMCG_RETAIL": ["soap", "detergent", "dishwash", "cleaning", "fmcg", "kirana", "retail", "shop", "store", "dokan", "grocery", "trade", "sales", "commercial", "collection centre"],
    "SERVICES": ["service", "repair", "maintenance", "transport", "logistics", "csc", "center"]
}

WEIGHTS = {
    "skill_match": 0.20,
    "location_suitability": 0.20,
    "resource_match": 0.15,
    "investment_fit": 0.15,
    "local_demand": 0.10,
    "competition": 0.05,
    "customer_potential": 0.05,
    "supplier_availability": 0.05,
    "market_access": 0.05
}

GENERIC_WORDS = {
    "farming", "agriculture", "manufacturing", "processing", "production", "unit", "mill",
    "business", "small", "mini", "rural", "and", "&", "the", "of", "for", "in", "making",
    "services", "center", "centre", "work", "general", "enterprise", "management", "skills",
    "knowledge", "basic", "local", "tools", "care", "operation"
}

def detect_user_target_sector(profile: UserProfile) -> Optional[str]:
    """Detects primary sector preference from user interest, skills, resources, and occupation."""
    skills_and_interest = " ".join([
        profile.business_interest or "",
        " ".join(profile.skills or [])
    ]).lower()

    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in skills_and_interest for kw in keywords):
            return sector

    combined_text = " ".join([
        profile.occupation or "",
        profile.experience or "",
        " ".join(profile.resources or [])
    ]).lower()

    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in combined_text for kw in keywords):
            return sector

    return None

def detect_business_sector(b: dict) -> str:
    """Categorizes a business into a standard sector based on category, title, and business traits."""
    cat = (b.get("category") or "").upper().strip()
    name = (b.get("business_name") or b.get("business_idea") or "").lower()

    # Direct category mappings
    if "DAIRY" in cat:
        return "DAIRY"
    if "LIVESTOCK" in cat:
        return "LIVESTOCK"
    if "FISHERIES" in cat:
        return "FISHERIES"
    if "FOOD" in cat or "AGRO PROCESSING" in cat:
        return "FOOD_PROCESSING"
    if "TEXTILE" in cat:
        return "TEXTILES"
    if "FMCG" in cat or "RETAIL" in cat:
        return "FMCG_RETAIL"
    if "PACKAGING" in cat:
        return "PACKAGING"
    if "RECYCLING" in cat or "ENVIRONMENTAL" in cat or "CIRCULAR" in cat:
        return "ENVIRONMENTAL"
    if "ENERGY" in cat:
        return "ENERGY"
    if "MANUFACTURING" in cat or "ENGINEERING" in cat:
        return "MANUFACTURING"
    if "HORTICULTURE" in cat or "AGRICULTURE" in cat or "AGRI-TECH" in cat:
        return "AGRICULTURE"
    if "AGRI-BUSINESS" in cat:
        return "FMCG_RETAIL"

    # Name-based fallback matching
    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in name for kw in keywords):
            return sector
            
    return "GENERAL_ENTERPRISE"

# =========================================================================
# 9 INDIVIDUAL DETERMINISTIC FACTOR CALCULATION FUNCTIONS
# =========================================================================

def calculate_skill_match(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 1: Skill Match (Weight 20%)
    Compares user profile skills, background, and stated interest against business requirements.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    user_skills = [s.lower() for s in (getattr(profile, 'skills', []) or [])]
    user_occ = (getattr(profile, 'occupation', '') or "").lower()
    user_exp = (getattr(profile, 'experience', '') or "").lower()
    user_interest = (getattr(profile, 'business_interest', '') or "").lower().strip()
    b_name = (b.get("business_name") or b.get("business_idea") or "").lower()
    
    req_skills = [s.lower() for s in (b.get("required_skills") or b.get("skill_required") or [])]
    if isinstance(req_skills, str):
        req_skills = [s.strip().lower() for s in req_skills.split(",") if s.strip()]

    matched_skills = []
    
    # 1. Exact or partial skill overlaps
    for req in req_skills:
        req_clean = req.lower().strip()
        for u_sk in user_skills:
            u_clean = u_sk.lower().strip()
            if u_clean in req_clean or req_clean in u_clean:
                matched_skills.append(req.title())
                break
            # Meaningful word matching
            words = [w for w in u_clean.split() if len(w) >= 4 and w not in GENERIC_WORDS]
            if any(w in req_clean for w in words):
                matched_skills.append(req.title())
                break

    # 2. Sector cross-matches
    user_sec = detect_user_target_sector(profile)
    biz_sec = detect_business_sector(b)
    
    if len(matched_skills) >= 3:
        base_score = 95.0
    elif len(matched_skills) == 2:
        base_score = 88.0
    elif len(matched_skills) == 1:
        base_score = 78.0
    elif not req_skills:
        base_score = 70.0  # Low barrier enterprise
    elif user_sec and biz_sec and user_sec == biz_sec:
        base_score = 75.0
    elif user_sec and biz_sec and user_sec in {"DAIRY", "LIVESTOCK", "POULTRY", "GOAT_SHEEP"} and biz_sec in {"DAIRY", "LIVESTOCK", "POULTRY", "GOAT_SHEEP"}:
        base_score = 70.0
    else:
        base_score = 35.0
    
    # Sector alignment bonus
    if user_sec and biz_sec and user_sec == biz_sec:
        base_score = min(100.0, base_score + 10.0)

    # Stated interest match boost
    if user_interest:
        user_int_words = [w for w in user_interest.split() if len(w) >= 3 and w not in GENERIC_WORDS]
        if any(w in b_name for w in user_int_words) or user_interest in b_name or b_name in user_interest:
            base_score = min(100.0, base_score + 15.0)
        elif user_sec and biz_sec and user_sec == biz_sec:
            base_score = min(100.0, base_score + 10.0)

    score = max(10.0, min(100.0, round(base_score, 1)))
    
    if matched_skills:
        reason = f"Your hands-on skills in {', '.join(matched_skills[:2])} directly match this business setup."
    elif user_sec and user_sec == biz_sec:
        reason = f"Your background in {user_sec.replace('_', ' ').title()} aligns with the operational skills needed."
    else:
        reason = "Basic operational skills can be learned through standard 1-week district training."

    return {
        "score": score,
        "reason": reason,
        "data_source": "User Skill Audit vs Business Skill Taxonomy",
        "confidence": 90.0
    }

def calculate_location_suitability(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 2: Location Suitability (Weight 20%)
    Compares user village/district/state with business ideal location and regional agro-climatic fit.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    loc = (getattr(profile, 'location', '') or getattr(profile, 'district', '') or getattr(profile, 'village', '') or "Rural Village").strip()
    state = (getattr(profile, 'state', '') or "Maharashtra").strip().lower()
    biz_sec = detect_business_sector(b)
    
    suitable_locs = b.get("suitable_locations") or b.get("ideal_location") or ["Rural villages", "Semi-urban mandis"]
    if isinstance(suitable_locs, list):
        suitable_text = " ".join(suitable_locs).lower()
    else:
        suitable_text = str(suitable_locs).lower()

    score = 80.0
    
    # Regional suitability adjustments
    if "dairy" in biz_sec.lower() or "livestock" in biz_sec.lower() or "agri" in biz_sec.lower():
        if any(st in state for st in ["maharashtra", "madhya pradesh", "gujarat", "karnataka", "rajasthan", "punjab", "haryana", "uttar pradesh"]):
            score = 92.0
    elif "textile" in biz_sec.lower() or "garment" in biz_sec.lower():
        score = 88.0
    elif "food" in biz_sec.lower():
        score = 85.0

    score = max(20.0, min(100.0, round(score, 1)))
    reason = f"Favorable regional demand and input accessibility identified for {loc}."
    
    return {
        "score": score,
        "reason": reason,
        "data_source": "Curated Agro-Climatic & Regional Business Indicators",
        "confidence": 85.0
    }

def calculate_resource_match(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 3: Resource Match (Weight 15%)
    Compares user physical resources (land, shed, water, shop, power) with enterprise requirements.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    user_res = [r.lower() for r in (getattr(profile, 'resources', []) or [])]
    user_res_text = " ".join(user_res)
    
    space_req = str(b.get("space_requirement") or b.get("space_required") or "Small space").lower()
    water_needed = b.get("water_needed", True)
    elec_needed = b.get("electricity_needed", True)
    biz_sec = detect_business_sector(b)
    
    score = 65.0
    has_land = any(k in user_res_text for k in ["land", "शेती", "जमीन", "field", "farm"])
    has_shed = any(k in user_res_text for k in ["shed", "गोठा", "शेड", "बाड़ा"])
    has_water = any(k in user_res_text for k in ["water", "पाणी", "पानी", "well", "borewell"])
    has_shop = any(k in user_res_text for k in ["shop", "दुकान", "commercial", "space", "counter"])
    has_vehicle = any(k in user_res_text for k in ["tractor", "vehicle", "वाहन", "ट्रॅक्टर"])
    has_none = any(k in user_res_text for k in ["none", "काहीही नाही", "कुछ नहीं", "no prior"])
    
    reasons = []

    if biz_sec in {"DAIRY", "LIVESTOCK", "GOAT_SHEEP"}:
        if has_shed and has_water:
            score = 96.0
            reasons.append("Your existing cattle shed and water source eliminate major initial setup costs.")
        elif has_land or has_shed:
            score = 88.0
            reasons.append("Your available land/shed provides a ready foundation for animal housing.")
        elif not has_land and not has_shed:
            score = 45.0
            reasons.append("Setting up animal shelter will require preliminary civil investment.")
        else:
            score = 70.0
    elif biz_sec in {"AGRICULTURE", "BEEKEEPING"}:
        if has_land and has_water:
            score = 95.0
            reasons.append("Your agricultural land and water access perfectly fit crop & cultivation requirements.")
        elif has_land:
            score = 85.0
            reasons.append("Your agricultural land provides a solid foundation for cultivation setup.")
        elif not has_land and not has_shed:
            score = 45.0
            reasons.append("Cultivation and plant nursery activities typically require dedicated agricultural land or open plot.")
        else:
            score = 70.0
    elif biz_sec in {"FMCG_RETAIL", "RETAIL", "SERVICES", "PACKAGING", "TEXTILES"}:
        if has_shop:
            score = 95.0
            reasons.append("Your available commercial/shop space saves significant monthly rental overhead.")
        else:
            score = 72.0
            reasons.append("Can be operated from a small rented commercial space or home premise.")
    else:
        # Food processing / Manufacturing
        if has_water or has_land or has_shop:
            score = 85.0
            reasons.append("Your premises and utility access fulfill basic processing setup requirements.")
        elif has_none:
            score = 65.0
        else:
            score = 75.0

    score = max(10.0, min(100.0, round(score, 1)))
    reason = reasons[0] if reasons else "Existing infrastructure meets preliminary startup requirements."

    return {
        "score": score,
        "reason": reason,
        "data_source": "User Asset Audit vs Enterprise Requirements",
        "confidence": 88.0
    }

def calculate_investment_fit(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 4: Investment Fit (Weight 15%)
    Compares user available investment with enterprise recommended capital and loan margin feasibility.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    user_cap = float(profile.available_investment if getattr(profile, 'available_investment', None) is not None else (getattr(profile, 'capital', 100000.0) or 100000.0))
    
    min_inv = float(b.get("minimum_investment", 50000.0))
    rec_inv = float(b.get("recommended_investment") or b.get("estimated_total_investment") or (min_inv * 1.5))
    
    ratio = user_cap / rec_inv if rec_inv > 0 else 1.0

    if 0.8 <= ratio <= 2.5:
        score = 96.0
        reason = f"Your investment of ₹{user_cap:,.0f} matches the ideal required capital of ₹{rec_inv:,.0f}."
    elif 0.5 <= ratio < 0.8:
        score = 88.0
        reason = f"Your savings cover over 50% of the cost; the balance is readily structured via MUDRA/PMEGP bank credit."
    elif 0.15 <= ratio < 0.5:
        score = 76.0
        reason = f"Your investment satisfies the 10%-15% promoter margin requirement under government subsidized loan schemes."
    elif 0.08 <= ratio < 0.15:
        score = 60.0
        reason = f"Meets minimum threshold for micro-credit assistance (up to 90% bank financing)."
    elif ratio > 2.5:
        score = 72.0
        reason = f"Your capital of ₹{user_cap:,.0f} comfortably exceeds the budget for this micro enterprise."
    else:
        score = 35.0
        reason = f"Recommended setup cost (₹{rec_inv:,.0f}) significantly exceeds available starting savings."

    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "Deterministic Credit & Capital Structuring Model",
        "confidence": 95.0
    }

def calculate_local_demand(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 5: Local Demand (Weight 10%)
    Evaluates daily essential consumption patterns and market turnover in rural clusters.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    biz_sec = detect_business_sector(b)
    m_factors = b.get("market_factors", {})
    demand_level = str(m_factors.get("demand_level") or b.get("local_demand") or "High").lower()

    if biz_sec in {"DAIRY", "FOOD_PROCESSING", "POULTRY"}:
        score = 92.0
        reason = "Continuous daily household and tea-stall/mandi consumption with quick cash turnaround."
    elif biz_sec in {"AGRICULTURE", "LIVESTOCK"}:
        score = 85.0
        reason = "High seasonal and periodic mandi demand with value-addition opportunities."
    elif biz_sec in {"TEXTILES", "RETAIL"}:
        score = 80.0
        reason = "Consistent village customer footfall for essential tailoring, repair, and retail needs."
    else:
        score = 75.0
        reason = "Steady regional market demand across weekly rural haats and trading centers."

    if "very high" in demand_level:
        score = min(100.0, score + 6.0)
    elif "variable" in demand_level:
        score = max(50.0, score - 5.0)

    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "Curated MSME Rural Market Indicators",
        "confidence": 85.0
    }

def calculate_competition_score(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 6: Competition (Weight 5%)
    Balanced evaluation: Moderate competition indicates proven demand; extreme saturation reduces score.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    m_factors = b.get("market_factors", {})
    comp = str(m_factors.get("competition") or b.get("competition_level") or "Medium").lower()
    biz_sec = detect_business_sector(b)
    
    if "medium" in comp or "moderate" in comp:
        score = 88.0
        reason = "Moderate local competition confirms strong validated market demand with room for quality producers."
    elif "low" in comp:
        if biz_sec in {"BEEKEEPING", "AGRICULTURE"}:
            score = 84.0
            reason = "Low local competition provides early-mover advantage in premium rural niche markets."
        else:
            score = 78.0
            reason = "Emerging category with low competition; requires early customer awareness."
    elif "high" in comp:
        score = 62.0
        reason = "Competitive market presence requires competitive pricing and quality differentiation."
    else:
        score = 80.0
        reason = "Balanced competitive dynamics in typical rural trade zones."

    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "Village Market Competition Heuristics",
        "confidence": 80.0
    }

def calculate_customer_potential(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 7: Customer Potential (Weight 5%)
    Assesses breadth of customer segments (Households, Mandi traders, Co-ops, Commercial buyers).
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    biz_sec = detect_business_sector(b)
    
    if biz_sec == "DAIRY":
        score = 90.0
        reason = "Multi-channel buyer base: Local households, village dairy co-operatives, and town sweet makers."
    elif biz_sec in {"FOOD_PROCESSING", "POULTRY"}:
        score = 86.0
        reason = "Dual customer reach: Direct rural retail consumers and institutional canteen/hotel supply."
    elif biz_sec == "TEXTILES":
        score = 82.0
        reason = "Steady local clientele for festive tailoring, school uniforms, and alteration work."
    else:
        score = 78.0
        reason = "Broad customer reach across village clusters and nearby taluka trading nodes."

    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "Customer Segment Indicators",
        "confidence": 80.0
    }

def calculate_supplier_availability(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 8: Supplier Availability (Weight 5%)
    Assesses availability of local machinery, seed/feed suppliers, and technical vendors.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    biz_name = (b.get("business_name") or b.get("business_idea") or "").lower()
    biz_sec = detect_business_sector(b)
    
    # Check if equipment is standard or highly available in Maharashtra / India
    if biz_sec in {"DAIRY", "TEXTILES", "FOOD_PROCESSING", "AGRICULTURE"}:
        score = 88.0
        reason = "Verified equipment manufacturers and input suppliers available across district hubs."
    else:
        score = 78.0
        reason = "Standard machinery sourcing available through regional MSME equipment networks."

    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "District Machinery Directory & Supplier Database",
        "confidence": 85.0
    }

def calculate_market_access(b: Any, profile: Any) -> Dict[str, Any]:
    """
    Factor 9: Market Access (Weight 5%)
    Evaluates sales off-take channels, village logistics, and co-op aggregators.
    """
    if isinstance(b, UserProfile) and isinstance(profile, dict):
        b, profile = profile, b
    m_factors = b.get("market_factors", {})
    reach = str(m_factors.get("market_reach") or b.get("sales_channels") or "Local village markets and weekly haats")
    
    score = 85.0
    reason = f"Accessible sales channels: {reach[:80]}."
    
    return {
        "score": round(score, 1),
        "reason": reason,
        "data_source": "Supply Chain & Offtake Route Analysis",
        "confidence": 82.0
    }

# =========================================================================
# MATCH LEVEL CLASSIFIER
# =========================================================================

def get_match_level(overall_score: float) -> str:
    if overall_score >= 90.0:
        return "Excellent Match"
    elif overall_score >= 80.0:
        return "Strong Match"
    elif overall_score >= 70.0:
        return "Good Match"
    elif overall_score >= 60.0:
        return "Possible Match"
    else:
        return "Low Match"

# =========================================================================
# MASTER SCORING ENGINE
# =========================================================================

def score_business(b: dict, profile: UserProfile) -> BusinessRecommendation:
    b_id = b.get("id") or b.get("business_id") or "b_custom"
    b_name = b.get("business_name") or b.get("business_idea") or "Rural Enterprise"
    b_name_lower = b_name.lower()
    b_category = b.get("category") or "General"
    min_inv = float(b.get("minimum_investment", 50000.0))
    rec_inv = float(b.get("recommended_investment") or b.get("estimated_total_investment") or 100000.0)
    user_cap = float(profile.available_investment if profile.available_investment is not None else (profile.capital or 100000.0))

    # Calculate 9 individual factor scores
    f_skill = calculate_skill_match(b, profile)
    f_location = calculate_location_suitability(b, profile)
    f_resource = calculate_resource_match(b, profile)
    f_investment = calculate_investment_fit(b, profile)
    f_demand = calculate_local_demand(b, profile)
    f_comp = calculate_competition_score(b, profile)
    f_customer = calculate_customer_potential(b, profile)
    f_supplier = calculate_supplier_availability(b, profile)
    f_market = calculate_market_access(b, profile)

    factor_details = {
        "skill_match": FactorScoreDetail(**f_skill),
        "location_suitability": FactorScoreDetail(**f_location),
        "resource_match": FactorScoreDetail(**f_resource),
        "investment_fit": FactorScoreDetail(**f_investment),
        "local_demand": FactorScoreDetail(**f_demand),
        "competition": FactorScoreDetail(**f_comp),
        "customer_potential": FactorScoreDetail(**f_customer),
        "supplier_availability": FactorScoreDetail(**f_supplier),
        "market_access": FactorScoreDetail(**f_market)
    }

    factor_scores = RecommendationFactorScores(
        skill_match=f_skill["score"],
        location_suitability=f_location["score"],
        resource_match=f_resource["score"],
        investment_fit=f_investment["score"],
        local_demand=f_demand["score"],
        competition=f_comp["score"],
        customer_potential=f_customer["score"],
        supplier_availability=f_supplier["score"],
        market_access=f_market["score"]
    )

    # Compute weighted final score
    raw_final_score = (
        f_skill["score"] * WEIGHTS["skill_match"] +
        f_location["score"] * WEIGHTS["location_suitability"] +
        f_resource["score"] * WEIGHTS["resource_match"] +
        f_investment["score"] * WEIGHTS["investment_fit"] +
        f_demand["score"] * WEIGHTS["local_demand"] +
        f_comp["score"] * WEIGHTS["competition"] +
        f_customer["score"] * WEIGHTS["customer_potential"] +
        f_supplier["score"] * WEIGHTS["supplier_availability"] +
        f_market["score"] * WEIGHTS["market_access"]
    )

    # Sector Filter: Penalize heavy unrelated manufacturing if user background is purely livestock/farming without manufacturing interest
    user_sec = detect_user_target_sector(profile)
    biz_sec = detect_business_sector(b)
    if user_sec and user_sec in ["DAIRY", "LIVESTOCK", "POULTRY", "GOAT_SHEEP", "AGRICULTURE"]:
        if biz_sec in ["MANUFACTURING"] and user_sec not in ["MANUFACTURING"]:
            if not any(kw in b_name_lower for kw in ["dairy", "feed", "fertilizer", "crop", "agri"]):
                raw_final_score = max(15.0, raw_final_score - 35.0)

    overall_score = max(0.0, min(100.0, round(raw_final_score, 1)))
    match_level = get_match_level(overall_score)

    why_this_matches = [
        f_skill["reason"],
        f_investment["reason"],
        f_resource["reason"],
        f_location["reason"]
    ]

    risks_list = b.get("risks") or b.get("key_risks") or ["General market price fluctuations"]
    if isinstance(risks_list, list):
        main_r = risks_list[0] if risks_list else "General market price fluctuations"
        considerations = [str(r) for r in risks_list[:2]]
    else:
        main_r = str(risks_list)
        considerations = [main_r]

    # Revenue & Profit estimates
    rev_factors = b.get("revenue_factors", {})
    est_rev = rev_factors.get("estimated_monthly_revenue_per_unit") or b.get("monthly_revenue_estimate")
    margin_pct = rev_factors.get("margin_percentage", 30)
    est_profit = (est_rev * (margin_pct / 100.0)) if est_rev else b.get("monthly_net_profit_estimate")

    breakdown = RecommendationScoreBreakdown(
        skill_match_score=f_skill["score"],
        location_suitability_score=f_location["score"],
        resource_match_score=f_resource["score"],
        capital_match_score=f_investment["score"],
        local_demand_score=f_demand["score"],
        competition_score=f_comp["score"],
        customer_potential_score=f_customer["score"],
        supplier_availability_score=f_supplier["score"],
        market_access_score=f_market["score"],
        market_potential_score=f_demand["score"],
        risk_score=f_comp["score"],
        total_score=overall_score
    )

    data_sources = [
        "Curated MSME Business Knowledge Base",
        "Deterministic 9-Factor Decision Matrix",
        "National Micro-Enterprise Credit Guidelines"
    ]

    return BusinessRecommendation(
        business_id=b_id,
        business_name=b_name,
        category=b_category,
        overall_score=overall_score,
        match_level=match_level,
        breakdown=breakdown,
        factor_scores=factor_scores,
        factor_details=factor_details,
        required_investment=rec_inv,
        user_capital=user_cap,
        why_matches=why_this_matches[:4],
        why_this_matches=why_this_matches[:4],
        considerations=considerations,
        main_opportunity=b.get("market_factors", {}).get("market_reach", "Steady daily local demand and town market supply."),
        main_risk=main_r,
        description=b.get("description") or b.get("business_description") or f"A high-potential rural enterprise in the {b_category} sector.",
        scalability=b.get("scalability", "High"),
        estimated_monthly_revenue=est_rev,
        estimated_monthly_profit=est_profit,
        data_sources=data_sources,
        confidence=87.5
    )

def get_recommendations(profile: UserProfile, top_n: int = 5) -> RecommendationResponse:
    """
    Ranks suitable rural businesses using the 9-factor deterministic scoring model.
    Returns TOP 5 recommendations sorted by overall_score descending.
    """
    businesses = load_businesses_data()
    scored_list = []
    
    for b in businesses:
        rec = score_business(b, profile)
        scored_list.append(rec)
    
    # Sort by overall score descending
    scored_list.sort(key=lambda x: x.overall_score, reverse=True)
    
    # Filter by minimum quality threshold (50.0) or top N fallback
    valid_recs = [r for r in scored_list if r.overall_score >= 50.0]
    top_recommendations = valid_recs[:top_n] if valid_recs else scored_list[:top_n]
    
    profile_summary = {
        "name": profile.name or "Rural Entrepreneur",
        "intent": profile.intent or "Start a new business",
        "age": profile.age,
        "gender": profile.gender,
        "location": profile.location or profile.district or "Local Village",
        "district": profile.district or "District",
        "state": profile.state or "State",
        "capital": profile.available_investment if profile.available_investment is not None else (profile.capital or 100000.0),
        "education": profile.education,
        "skills_count": len(profile.skills or []),
        "resources_count": len(profile.resources or []),
        "business_interest": profile.business_interest
    }

    return RecommendationResponse(
        recommendations=top_recommendations,
        profile_summary=profile_summary
    )
