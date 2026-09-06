from typing import List, Dict, Any, Optional
from backend.models import UserProfile, BusinessRecommendation, RecommendationScoreBreakdown, RecommendationResponse
from backend.database import load_businesses_data

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
    
    # 1. SKILL & INTEREST MATCH (Weight: 25%)
    skill_score = 10.0  # Base score
    skill_matched_items = []
    
    # Direct interest match check
    if user_interest:
        # Exact or substring match on business name
        if user_interest == b_name_lower or b_name_lower in user_interest:
            skill_score += 14.0
            why_matches.append(f"Directly matches your stated preference for {b_name}.")
        elif user_interest in b_name_lower:
            skill_score += 13.0
            why_matches.append(f"Matches your primary interest in {profile.business_interest}.")
        elif b_category and (b_category.lower() in user_interest or user_interest in b_category.lower()):
            skill_score += 10.0
            why_matches.append(f"Belongs to your preferred {b_category} industry domain.")
        else:
            # Meaningful non-generic word match
            interest_words = [w for w in user_interest.replace(",", " ").split() if len(w) > 2 and w not in GENERIC_WORDS]
            name_words = [w for w in b_name_lower.replace(",", " ").split() if len(w) > 2 and w not in GENERIC_WORDS]
            overlap = set(interest_words).intersection(set(name_words))
            if overlap:
                skill_score += 11.0
                why_matches.append(f"Strongly aligns with your interest in {', '.join(overlap)}.")

    # Skills and background overlap check
    for req in req_skills:
        for u_sk in user_skills:
            if u_sk in req or req in u_sk:
                skill_matched_items.append(req)
        if user_exp and any(w in req for w in user_exp.split() if len(w) > 2 and w not in GENERIC_WORDS):
            skill_matched_items.append(req)
        if user_occ and any(w in req for w in user_occ.split() if len(w) > 2 and w not in GENERIC_WORDS):
            skill_matched_items.append(req)

    unique_skill_matches = list(set(skill_matched_items))
    if unique_skill_matches:
        added_skill_points = min(8.0, len(unique_skill_matches) * 3.0)
        skill_score += added_skill_points
        why_matches.append(f"Your background matches key technical requirements: {', '.join(unique_skill_matches[:3])}.")
    
    skill_score = min(25.0, max(5.0, skill_score))
    
    # 2. CAPITAL MATCH (Weight: 25%)
    # Under micro-enterprise lending guidelines, up to 90% loan can be structured
    capital_score = 15.0
    if profile.capital is not None:
        if user_capital >= rec_inv:
            capital_score = 25.0
            why_matches.append(f"Your available capital of ₹{user_capital:,.0f} comfortably covers the recommended investment of ₹{rec_inv:,.0f}.")
        elif user_capital >= min_inv:
            capital_score = 22.5
            why_matches.append(f"Available capital ₹{user_capital:,.0f} exceeds the minimum barrier (₹{min_inv:,.0f}) with room for working capital.")
        elif user_capital >= (min_inv * 0.10):  # Can secure 90% loan under standard micro-enterprise credit schemes
            capital_score = 19.5
            why_matches.append(f"Your capital (₹{user_capital:,.0f}) provides the required 10% own margin money for loan eligibility.")
        else:
            capital_score = 11.0
    else:
        capital_score = 18.0
    
    capital_score = min(25.0, max(5.0, capital_score))
    
    # 3. RESOURCE MATCH (Weight: 20%)
    resource_score = 12.0
    res_matches = []
    for req_r in req_resources:
        for u_r in user_resources:
            if u_r in req_r or req_r in u_r:
                res_matches.append(req_r)
        if any(w in user_resources for w in ["land", "shed", "yard", "room", "space"]):
            if any(w in req_r for w in ["land", "shed", "yard", "room", "space"]):
                res_matches.append("space/land")
        if "water" in user_resources and "water" in req_r:
            res_matches.append("water supply")
        if "electricity" in user_resources and "electricity" in req_r:
            res_matches.append("power")

    unique_res = list(set(res_matches))
    if unique_res:
        resource_score += min(8.0, len(unique_res) * 3.0)
        why_matches.append(f"You have essential infrastructure available: {', '.join(unique_res[:3])}.")
    else:
        resource_score += 2.0
    
    resource_score = min(20.0, max(5.0, resource_score))
    
    # 4. MARKET POTENTIAL (Weight: 20%)
    market_factors = b.get("market_factors", {})
    demand = str(market_factors.get("demand_level", "High")).lower()
    if "high" in demand:
        market_score = 18.5
    elif "medium" in demand or "moderate" in demand:
        market_score = 16.0
    else:
        market_score = 13.5
        
    if profile.district or profile.location:
        market_score = min(20.0, market_score + 1.5)
        why_matches.append(f"Strong continuous local consumer demand in {profile.district or profile.location or 'rural clusters'}.")
    else:
        why_matches.append(f"High local demand reported across regional village and town clusters.")

    # 5. RISK SCORE (Weight: 10%)
    risk_level = str(b.get("risk_level", "Medium")).lower()
    if "low" in risk_level:
        risk_score = 9.2
    elif "medium" in risk_level:
        risk_score = 8.0
    else:
        risk_score = 6.8

    total_score = round(skill_score + capital_score + resource_score + market_score + risk_score, 1)
    
    if len(why_matches) < 3:
        why_matches.append(f"Suitable for scalable expansion into allied value-added products.")

    breakdown = RecommendationScoreBreakdown(
        skill_match_score=round(skill_score, 1),
        capital_match_score=round(capital_score, 1),
        resource_match_score=round(resource_score, 1),
        market_potential_score=round(market_score, 1),
        risk_score=round(risk_score, 1),
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
    
    # Sort descending by overall_score
    scored_list.sort(key=lambda x: x.overall_score, reverse=True)
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
