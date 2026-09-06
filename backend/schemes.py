from typing import List, Optional
from backend.models import UserProfile, MatchedScheme
from backend.database import load_schemes_data, get_business_by_id

# Sector alias mapping for national scheme eligibility
SECTOR_ALIASES = {
    "Agriculture & Allied": ["agriculture", "horticulture", "livestock", "dairy", "fisheries", "agri-tech", "agri-business", "agro processing", "bio/circular economy", "poultry", "goat", "beekeeping", "mushroom", "vermicompost", "organic"],
    "Manufacturing & Processing": ["manufacturing", "food processing", "agro processing", "packaging", "fmcg", "engineering", "textile", "recycling", "clean energy", "renewable energy", "biomass", "solar", "pellet", "briquette", "coir"],
    "Food Processing": ["food processing", "dairy", "agro processing", "fmcg", "milling", "atta", "spice", "oilseed", "cold storage", "bakery"],
    "Services & Textiles": ["services", "textile", "electronics", "automobile", "repair", "handicrafts", "tailoring", "garment", "weavers", "transport"],
    "Dairy & Livestock": ["dairy", "cattle", "cow", "buffalo", "poultry", "chicken", "goat", "sheep", "livestock", "fodder", "animal husbandry"],
    "Fisheries & Aquaculture": ["fisheries", "aquaculture", "fish", "prawn", "shrimp", "biofloc", "ras", "pond", "ornamental fish"],
    "Clean Energy & Renewable": ["solar", "biogas", "cbg", "clean energy", "renewable", "biomass", "pellet", "green energy"],
    "Women & Rural Livelihoods": ["women", "shg", "lakhpati", "hygiene", "sanitary", "tailoring", "handloom", "cottage"],
    "Artisans & Traditional Crafts": ["artisan", "craft", "pottery", "blacksmith", "carpenter", "tailor", "handloom", "bamboo", "vishwakarma"]
}

def match_government_schemes(
    profile: UserProfile, 
    business_id: Optional[str] = None, 
    business_category: Optional[str] = None,
    project_cost: Optional[float] = None
) -> List[MatchedScheme]:
    all_schemes = load_schemes_data()
    scored_matches = []

    # Identify target business category and user interests
    cat = (business_category or "").strip()
    cat_lower = cat.lower()

    if not cat and business_id:
        b_info = get_business_by_id(business_id)
        if b_info:
            cat = b_info.get("category", "")
            cat_lower = cat.lower()

    raw_interests = profile.business_interest or ""
    if isinstance(raw_interests, str):
        user_interests = [i.strip().lower() for i in raw_interests.split(",") if i.strip()]
    elif isinstance(raw_interests, list):
        user_interests = [str(i).strip().lower() for i in raw_interests if str(i).strip()]
    else:
        user_interests = []

    user_resources = [r.lower() for r in (profile.resources or [])]
    user_state = (profile.state or "").strip().lower()
    cost = project_cost if project_cost is not None else (profile.capital or 100000.0)

    for s in all_schemes:
        s_id = s.get("id", "")
        eligible_cats = s.get("eligible_businesses", [])
        eligible_ids = s.get("eligible_ids", [])
        s_level = s.get("level", "Central")
        s_category = s.get("category", "")
        
        # State-level filter: Skip state-specific schemes if user is not in that state
        if s_level == "State" and user_state:
            state_in_cat = s_category.lower()
            state_in_name = s.get("scheme_name", "").lower()
            # If scheme specifies a state but user's state does not match, skip
            if "maharashtra" in state_in_cat and "maharashtra" not in user_state:
                continue
            if "uttar pradesh" in state_in_cat and "uttar pradesh" not in user_state and "up" not in user_state:
                continue
            if "tamil nadu" in state_in_cat and "tamil nadu" not in user_state and "tn" not in user_state:
                continue
            if "rajasthan" in state_in_cat and "rajasthan" not in user_state:
                continue
            if "karnataka" in state_in_cat and "karnataka" not in user_state:
                continue

        score = 0
        why_rel = []

        # 1. Exact ID or ID prefix match (Highest specificity: +40)
        if business_id and any(business_id.startswith(eid) or eid in business_id for eid in eligible_ids):
            score += 40
            why_rel.append("Dedicated national development mission for this business activity.")

        # 2. Category / Sector match with alias resolution (+25)
        cat_matched = False
        for ec in eligible_cats:
            if ec.lower() in cat_lower or (cat_lower and cat_lower in ec.lower()):
                score += 25
                why_rel.append(f"Covers micro-enterprises under the '{cat}' sector.")
                cat_matched = True
                break
            # Check sector aliases
            aliases = SECTOR_ALIASES.get(ec, [])
            if any(a in cat_lower for a in aliases):
                score += 20
                why_rel.append(f"Eligible under '{ec}' category guidelines.")
                cat_matched = True
                break

        # 3. User interest match (+15)
        for interest in user_interests:
            for ec, aliases in SECTOR_ALIASES.items():
                if any(a in interest for a in aliases):
                    if ec in eligible_cats or s_category == ec:
                        score += 15
                        why_rel.append(f"Matches your specified interest in '{interest}'.")
                        break

        # 4. State match bonus for relevant state schemes (+20)
        if s_level == "State" and user_state and any(kw in s_category.lower() or kw in s.get("scheme_name", "").lower() for kw in [user_state, user_state.replace(" ", "")]):
            score += 20
            why_rel.append(f"Direct State incentive program for {profile.state} residents.")

        # 5. Universal priority schemes
        if s_id == "pm_mudra_yojana":
            score += 30
            if cost <= 50000:
                tier_str = "Shishu Tier (up to ₹50k, 0% collateral)"
            elif cost <= 500000:
                tier_str = "Kishore Tier (₹50k to ₹5 Lakh, 0% collateral)"
            else:
                tier_str = "Tarun Tier (₹5 Lakh to ₹20 Lakh)"
            why_rel.append(f"Provides collateral-free working capital loan under {tier_str}.")
        elif s_id == "pmegp":
            score += 30
            why_rel.append("Offers up to 35% capital subsidy for rural micro-entrepreneurs.")

        if score > 0:
            scheme_obj = MatchedScheme(
                scheme_id=s_id,
                scheme_name=s.get("scheme_name", ""),
                why_relevant="; ".join(why_rel) if why_rel else "Matches rural micro-enterprise profile.",
                possible_support=s.get("financial_support", ""),
                eligibility_summary=s.get("eligibility", ""),
                required_documents=s.get("documents", []),
                official_source=s.get("official_source", ""),
                notes=s.get("notes", ""),
                myscheme_url=s.get("myscheme_url"),
                category=s.get("category"),
                ministry=s.get("ministry")
            )
            scored_matches.append((score, scheme_obj))

    # Sort by relevance score descending
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    
    # Return top matched schemes (max 8 for clean UI presentation)
    return [item[1] for item in scored_matches[:8]]
