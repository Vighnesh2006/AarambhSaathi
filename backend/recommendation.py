from typing import List, Dict, Any, Optional
from backend.models import UserProfile, BusinessRecommendation, RecommendationScoreBreakdown, RecommendationResponse
from backend.database import load_businesses_data

# Specific keyword-to-sector mapping
SECTOR_KEYWORD_MAP = {
    "DAIRY": ["dairy", "cow", "milk", "cattle", "buffalo", "chilling", "dugdha"],
    "GOAT_SHEEP": ["goat", "sheep", "bakri", "sheli"],
    "POULTRY": ["poultry", "chicken", "hen", "egg", "broiler", "murgi", "kukut"],
    "LIVESTOCK": ["livestock", "animal", "cattle", "pashu", "goat", "sheep", "cow"],
    "FISHERIES": ["fish", "fishery", "aquaculture", "pisciculture", "machli"],
    "BEEKEEPING": ["bee", "honey", "beekeeping", "apiculture", "madh", "madhumakhi"],
    "AGRICULTURE": ["mushroom", "organic", "vermicompost", "nursery", "crop", "farm", "khet", "shet"],
    "TEXTILES": ["tailor", "garment", "sewing", "cloth", "boutique", "stitching", "shilai"],
    "FOOD_PROCESSING": ["flour", "atta", "chakki", "spice", "masala", "jaggery", "papad", "pickle"],
    "MANUFACTURING": ["brick", "block", "plastic", "moulding", "concrete", "paper plate", "fly ash", "paving"]
}

def detect_user_target_sector(profile: UserProfile) -> Optional[str]:
    """Detects primary sector preference from user interest, skills, resources, and occupation."""
    # Priority 1: Stated business interest or explicit skills
    skills_and_interest = " ".join([
        profile.business_interest or "",
        " ".join(profile.skills or [])
    ]).lower()

    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in skills_and_interest for kw in keywords):
            return sector

    # Priority 2: General occupation and resources
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
    """Categorizes a business into a standard sector based on category, name, and description."""
    cat = (b.get("category") or "").upper()
    name = (b.get("business_name") or "").lower()
    desc = (b.get("description") or "").lower()
    text = f"{cat} {name} {desc}"

    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in text for kw in keywords):
            return sector
            
    if "AGRICULTURE" in cat or "AGRI" in cat:
        return "AGRICULTURE"
    if "MANUFACTURING" in cat:
        return "MANUFACTURING"
    if "SERVICE" in cat:
        return "SERVICES"
    if "RETAIL" in cat:
        return "RETAIL"
    return "OTHER"

def score_business(b: dict, profile: UserProfile) -> BusinessRecommendation:
    user_capital = float(profile.capital) if profile.capital is not None else 100000.0
    user_skills = [s.lower() for s in (profile.skills or [])]
    user_resources = [r.lower() for r in (profile.resources or [])]
    user_interest = (profile.business_interest or "").lower().strip()
    user_exp = (profile.experience or "").lower()
    user_occ = (profile.occupation or "").lower()

    b_id = b.get("id", "")
    b_name = b.get("business_name", "")
    b_name_lower = b_name.lower()
    b_category = b.get("category", "")
    min_inv = float(b.get("minimum_investment", 50000))
    rec_inv = float(b.get("recommended_investment", 100000))
    req_skills = [s.lower() for s in b.get("required_skills", [])]
    req_resources = [r.lower() for r in b.get("required_resources", [])]
    
    why_matches = []
    GENERIC_WORDS = {"farming", "agriculture", "manufacturing", "processing", "production", "unit", "mill", "business", "small", "mini", "rural", "and", "&", "the", "of", "for", "in", "making", "shop", "services", "center", "centre", "trade"}
    
    user_sector = detect_user_target_sector(profile)
    business_sector = detect_business_sector(b)
    
    # 1. SKILL MATCH SCORE (Weight: 70%)
    # Checks overlap between user skills/background and the business's 3 primary skills
    skill_matched_count = 0
    matched_skill_names = []
    
    LIVESTOCK_SECTORS = {"DAIRY", "LIVESTOCK", "GOAT_SHEEP", "POULTRY"}
    
    if req_skills:
        for req in req_skills:
            # Check user skills
            matched = False
            for u_sk in user_skills:
                if u_sk in req or req in u_sk or any(w in req for w in u_sk.split() if len(w) > 2 and w not in GENERIC_WORDS):
                    matched = True
                    break
                # Sector keyword cross-match (e.g. "livestock management" skill matching "animal care" requirement)
                for sec, kws in SECTOR_KEYWORD_MAP.items():
                    if any(kw in u_sk for kw in kws) and any(kw in req for kw in kws):
                        matched = True
                        break
                if matched:
                    break

            # Check user interest
            if not matched and user_interest:
                if any(w in req for w in user_interest.split() if len(w) > 2 and w not in GENERIC_WORDS):
                    matched = True
                else:
                    for sec, kws in SECTOR_KEYWORD_MAP.items():
                        if any(kw in user_interest for kw in kws) and any(kw in req for kw in kws):
                            matched = True
                            break
            # Check user occupation
            if not matched and user_occ:
                if any(w in req for w in user_occ.split() if len(w) > 2 and w not in GENERIC_WORDS):
                    matched = True
            
            if matched:
                skill_matched_count += 1
                matched_skill_names.append(req.title())

    # Direct business name match boost
    name_bonus = 0.0
    if user_interest and (user_interest == b_name_lower or user_interest in b_name_lower or b_name_lower in user_interest):
        name_bonus = 20.0
        why_matches.append(f"Directly matches your stated interest in {b_name}.")

    # Sector Group Alignment Boost
    sector_boost = 0.0
    if user_sector and business_sector:
        if user_sector == business_sector:
            sector_boost = 25.0
            why_matches.append(f"Directly matches your background in {business_sector.replace('_', ' ').title()}.")
        elif user_sector in LIVESTOCK_SECTORS and business_sector in LIVESTOCK_SECTORS:
            sector_boost = 20.0
            why_matches.append("Strongly aligns with your livestock and animal care expertise.")
        elif user_sector == "AGRICULTURE" and business_sector in {"AGRICULTURE", "BEEKEEPING"}:
            sector_boost = 15.0

    skill_score = min(70.0, (skill_matched_count / 3.0 * 35.0) + 15.0 + name_bonus + sector_boost)
    if matched_skill_names:
        why_matches.append(f"Matches your primary skills: {', '.join(matched_skill_names[:3])}.")

    # 2. EXPERIENCE MATCH SCORE (Weight: 15%)
    exp_score = 10.0
    if "5" in user_exp or "3" in user_exp or "more" in user_exp or "experienced" in user_exp:
        exp_score = 15.0
        why_matches.append("Your extensive prior experience reduces operational risk.")
    elif "1" in user_exp or "some" in user_exp or "basic" in user_exp:
        exp_score = 12.5
    else:
        exp_score = 10.0

    # 3. CAPITAL & RESOURCE MATCH SCORE (Weight: 15%)
    cap_res_score = 10.0
    if profile.capital is not None:
        if user_capital >= rec_inv:
            cap_res_score = 15.0
            why_matches.append(f"Available capital ₹{user_capital:,.0f} comfortably covers recommended investment.")
        elif user_capital >= min_inv:
            cap_res_score = 13.0
            why_matches.append(f"Capital ₹{user_capital:,.0f} meets minimum investment requirement.")
        elif user_capital >= (min_inv * 0.10):
            cap_res_score = 11.5
            why_matches.append("Capital provides required margin money for bank credit eligibility.")
    else:
        cap_res_score = 12.0

    total_score = round(skill_score + exp_score + cap_res_score, 1)

    # HARD CATEGORY FILTER AGAINST UNRELATED MANUFACTURING FOR LIVESTOCK / AGRI SKILLS
    if user_sector and user_sector in ["DAIRY", "LIVESTOCK", "GOAT_SHEEP", "POULTRY", "FISHERIES", "BEEKEEPING", "AGRICULTURE", "TEXTILES"]:
        if business_sector in ["MANUFACTURING", "FOOD_PROCESSING"] and user_sector not in ["FOOD_PROCESSING", "MANUFACTURING"]:
            if not any(kw in b_name_lower for kw in ["dairy", "milk", "goat", "poultry", "feed", "fertilizer", "crop", "grain"]):
                total_score = max(10.0, total_score - 50.0)

    if len(why_matches) < 3:
        why_matches.append("Strong local market opportunity in rural and semi-urban clusters.")

    breakdown = RecommendationScoreBreakdown(
        skill_match_score=round(skill_score, 1),
        capital_match_score=round(cap_res_score, 1),
        resource_match_score=round(cap_res_score, 1),
        market_potential_score=round(exp_score, 1),
        risk_score=8.0,
        total_score=total_score
    )


    main_opp = b.get("market_factors", {}).get("market_reach", "Steady daily local demand and town market supply.")
    risks_list = b.get("risks", ["General market price fluctuations"])
    main_r = risks_list[0] if risks_list else "General market price fluctuations"

    return BusinessRecommendation(
        business_id=b_id,
        business_name=b_name,
        category=b_category,
        overall_score=total_score,
        breakdown=breakdown,
        required_investment=rec_inv,
        user_capital=user_capital,
        why_matches=why_matches[:4],
        main_opportunity=main_opp,
        main_risk=main_r,
        description=b.get("description", ""),
        scalability=b.get("scalability", "High")
    )

def get_recommendations(profile: UserProfile, top_n: int = 3) -> RecommendationResponse:
    businesses = load_businesses_data()
    scored_list = []
    
    for b in businesses:
        rec = score_business(b, profile)
        scored_list.append(rec)
    
    scored_list.sort(key=lambda x: x.overall_score, reverse=True)
    top_recommendations = [r for r in scored_list if r.overall_score >= 50.0][:top_n]
    
    # Fallback to top scored if none >= 50
    if not top_recommendations:
        top_recommendations = scored_list[:top_n]
    
    profile_summary = {
        "name": profile.name or "Rural Entrepreneur",
        "location": profile.location or "Local Village",
        "district": profile.district or "District",
        "state": profile.state or "State",
        "capital": profile.capital or 100000.0,
        "skills_count": len(profile.skills),
        "resources_count": len(profile.resources)
    }

    return RecommendationResponse(
        recommendations=top_recommendations,
        profile_summary=profile_summary
    )

