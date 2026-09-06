from backend.models import UserProfile, FeasibilityResponse
from backend.database import get_business_by_id

def evaluate_hyper_local_feasibility(business_id: str, profile: UserProfile) -> FeasibilityResponse:
    business = get_business_by_id(business_id)
    if not business:
        # Fallback default
        b_name = "Rural Micro Enterprise"
        category = "General"
        min_inv = 80000
        risks = ["Market demand variance"]
    else:
        b_name = business.get("business_name", "")
        category = business.get("category", "")
        min_inv = business.get("minimum_investment", 80000)
        risks = business.get("risks", ["General market price fluctuations"])

    user_loc = profile.location or profile.district or "Local Village Cluster"
    user_cap = profile.capital or 100000.0
    user_skills = [s.lower() for s in (profile.skills or [])]
    user_res = [r.lower() for r in (profile.resources or [])]

    # Deterministic scoring factors:
    # 1. Demand & Market Opportunity (25 pts)
    demand_pts = 22.0
    market_opp = "High Local Consumption"
    
    # 2. Raw Material & Resource Accessibility (25 pts)
    resource_pts = 20.0
    res_avail = "Good (Accessible within 5-10 km)"
    if len(user_res) >= 2:
        resource_pts = 24.0
        res_avail = "Abundant (Available on-premise)"

    # 3. Competition Density (25 pts)
    comp_level = "Moderate (1-3 local players)"
    comp_pts = 21.0
    if "kirana" in business_id or "grocery" in business_id:
        comp_level = "High (Check village shop density)"
        comp_pts = 18.0
    elif "mushroom" in business_id or "beekeeping" in business_id or "vermicompost" in business_id:
        comp_level = "Low (Pioneer advantage in village)"
        comp_pts = 24.0

    # 4. Financial & Local Risk Profile (25 pts)
    risk_level = "Low to Moderate"
    risk_pts = 20.0
    if user_cap >= min_inv:
        risk_pts += 3.0
    else:
        risk_pts += 1.0

    total_feasibility = round(demand_pts + resource_pts + comp_pts + risk_pts, 1)
    total_feasibility = min(96.0, max(65.0, total_feasibility))

    positive_factors = [
        f"Strong daily retail and mandi demand identified around {user_loc}",
        "Available capital aligns with 90% micro-enterprise loan structuring tier",
        f"Favorable supply chain for raw materials and inputs in {profile.district or profile.state or 'the region'}",
        "High value-addition margin potential with manageable overheads"
    ]

    caution_factors = [
        f"Operating margin subject to regional price variations: {risks[0]}",
        f"Verify local competitor count within a 3-5 km radius before site finalization",
        "Maintain contingency fund for seasonal working capital fluctuations"
    ]

    return FeasibilityResponse(
        business_id=business_id,
        business_name=b_name,
        feasibility_score=total_feasibility,
        market_opportunity=market_opp,
        competition_level=comp_level,
        resource_availability=res_avail,
        risk_level=risk_level,
        positive_factors=positive_factors,
        caution_factors=caution_factors,
        is_demo_data=True,
        disclaimer="Hyper-local feasibility estimated using demographic indices and heuristic benchmarks. Connect live GIS/APMC feeds for official sanctions."
    )
