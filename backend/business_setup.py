"""
Business Setup Planner Module for Aarambh Saathi / GramVantage AI (Step 4).

Generates a practical, deterministic Business Setup Plan:
1. Setup Requirements (Infrastructure, Machinery, Raw Materials, Labour, Compliance)
2. Machinery Classification (Essential, Recommended, Optional)
3. Deterministic Cost Modeling (Starter Setup vs Standard Setup)
4. User Investment Comparison & Funding Gap calculation
5. Supplier Recommendations & Local Ranking (via backend/supplier.py)
6. 3-Phase Setup Roadmap (Phase 1 Must-Have, Phase 2 Post-Launch, Phase 3 Scale-Up)
7. Low-Capital Mode with practical deferral advice for micro-entrepreneurs
8. Integration with Step 3 Feasibility Infrastructure Gaps
"""

from typing import List, Dict, Any, Optional
from backend.models import (
    UserProfile,
    BusinessSetupRequest,
    BusinessSetupResponse,
    BusinessSetupCostBreakdown,
    InfrastructureRequirement,
    MachineryRequirement,
    RawMaterialRequirement,
    LabourRequirement,
    SetupPhase,
    LowCapitalAdvice,
    DataQualityReport
)
from backend.database import get_business_by_id, load_businesses_data
from backend.supplier import get_required_machines, search_suppliers

def generate_business_setup_plan(
    business_id: str,
    business_name: Optional[str] = None,
    user_profile: Optional[UserProfile] = None,
    available_investment: Optional[float] = None,
    feasibility_result: Optional[Dict[str, Any]] = None
) -> BusinessSetupResponse:
    """
    Main deterministic engine for generating practical Business Setup Plans.
    """
    # 1. Resolve business data
    business = get_business_by_id(business_id)
    if not business:
        all_b = load_businesses_data()
        business = next((b for b in all_b if b.get("business_name", "").lower() == (business_name or "").lower()), None)
        if not business:
            business = all_b[0] if all_b else {
                "id": business_id,
                "business_name": business_name or "Rural Micro Enterprise",
                "category": "General",
                "minimum_investment": 80000.0,
                "recommended_investment": 140000.0,
                "space_requirement": "Small space (200-500 sqft)",
                "water_needed": True,
                "electricity_needed": True,
                "common_expenses": ["Raw materials", "Utilities", "Packaging"]
            }

    b_name = business.get("business_name", business_name or "Rural Micro Enterprise")
    category = business.get("category", "General")
    b_id = business.get("id", business_id)

    # 2. Resolve Profile & Location
    if user_profile is None:
        user_profile = UserProfile()

    user_loc = user_profile.village or user_profile.location or user_profile.district or ""
    user_dist = user_profile.district or ""
    user_state = user_profile.state or "Maharashtra"
    
    # Resolve investment
    if available_investment is not None and available_investment > 0:
        user_inv = float(available_investment)
    elif user_profile.available_investment is not None and user_profile.available_investment > 0:
        user_inv = float(user_profile.available_investment)
    elif user_profile.capital is not None and user_profile.capital > 0:
        user_inv = float(user_profile.capital)
    else:
        user_inv = 50000.0

    user_res_str = " ".join((user_profile.resources or [])).lower()

    # 3. Extract infrastructure gaps from Feasibility (Step 3) if present
    infra_gaps = []
    if feasibility_result:
        infra_gaps = feasibility_result.get("infrastructure_gaps", [])

    # 4. Infrastructure Requirements Breakdown
    space_req = business.get("space_requirement", "Small space (200-500 sqft)")
    water_needed = business.get("water_needed", False)
    elec_needed = business.get("electricity_needed", False)

    infra_reqs: List[InfrastructureRequirement] = []

    # Land / Operating Space
    has_space = any(w in user_res_str for w in ["land", "acre", "shed", "space", "shop", "plot", "building", "sqft"])
    is_space_gap = not has_space and (user_profile.resources or any("land" in g.lower() or "space" in g.lower() for g in infra_gaps))
    infra_reqs.append(InfrastructureRequirement(
        item="Operating Space / Land",
        detail=f"Required: {space_req}",
        status="Gap — Required Before Launch" if is_space_gap else "Available / Sourced",
        priority="Essential"
    ))

    # Building / Shed
    has_shed = any(w in user_res_str for w in ["shed", "building", "shop", "hall", "workshop"])
    infra_reqs.append(InfrastructureRequirement(
        item="Covered Shed / Work Area",
        detail="Weather-protected, ventilated covered area for machinery setup and raw material storage",
        status="Available / Sourced" if has_shed else "Gap — Required Before Launch",
        priority="Essential" if "manufacturing" in category.lower() or "processing" in category.lower() else "Recommended"
    ))

    # Electricity
    has_elec = any(w in user_res_str for w in ["electricity", "power", "3 phase", "three phase", "connection", "generator"])
    elec_detail = "Commercial 3-Phase Power (440V) for industrial motors" if elec_needed else "Single Phase Domestic / Commercial Connection (220V)"
    infra_reqs.append(InfrastructureRequirement(
        item="Electricity & Power",
        detail=elec_detail,
        status="Available / Sourced" if has_elec else "Gap — Required Before Launch",
        priority="Essential" if elec_needed else "Recommended"
    ))

    # Water
    has_water = any(w in user_res_str for w in ["water", "borewell", "well", "pipeline", "supply", "tap"])
    infra_reqs.append(InfrastructureRequirement(
        item="Water Supply",
        detail="Continuous clean water connection for cleaning, processing, and hygiene" if water_needed else "Standard utility water connection",
        status="Available / Sourced" if has_water else "Gap — Required Before Launch",
        priority="Essential" if water_needed else "Recommended"
    ))

    # Storage Space
    has_storage = any(w in user_res_str for w in ["storage", "room", "godown", "warehouse", "shop"])
    infra_reqs.append(InfrastructureRequirement(
        item="Raw Material & Finished Goods Storage",
        detail="Damp-proof storage room with pallets/racks for finished goods preservation",
        status="Available / Sourced" if has_storage else "Gap — Required Before Launch",
        priority="Recommended"
    ))

    # 5. Fetch Required Machinery from Knowledge Base (data/machines.json)
    raw_machines = get_required_machines(b_name, business_scale="small")
    machinery_reqs: List[MachineryRequirement] = []
    all_suppliers_for_business: List[Dict[str, Any]] = []
    seen_supplier_ids = set()

    # Per-machine budget allocation
    per_machine_budget = (user_inv / max(1, len(raw_machines))) if user_inv > 0 else None

    for m in raw_machines:
        m_id = m.get("machine_id", "")
        m_name = m.get("machine_name", "Processing Unit")
        p_min = float(m.get("estimated_price_min", 20000.0))
        p_max = float(m.get("estimated_price_max", 45000.0))
        p_priority = m.get("priority", "Essential")
        
        # Search suppliers for this machine
        search_res = search_suppliers(
            machine_id=m_id,
            location=user_loc or user_dist,
            budget=per_machine_budget,
            capacity=m.get("capacity")
        )
        sup_list = search_res.get("suppliers", [])
        
        # Power requirement heuristic
        power_req = "Single Phase 220V" if p_min < 30000 else "3-Phase 440V / 3 HP"

        machinery_reqs.append(MachineryRequirement(
            machine_id=m_id,
            machine_name=m_name,
            purpose=m.get("purpose", "Primary processing equipment"),
            capacity=m.get("capacity", "Standard micro-scale"),
            power_requirement=power_req,
            price_min=p_min,
            price_max=p_max,
            price_range=f"₹{p_min:,.0f} - ₹{p_max:,.0f}",
            priority=p_priority,
            installation_available=True,
            maintenance_requirement="Quarterly lubrication and blade/motor inspection",
            supplier_count=len(sup_list)
        ))

        # Collect top suppliers
        for s in sup_list[:3]:
            if s["supplier_id"] not in seen_supplier_ids:
                seen_supplier_ids.add(s["supplier_id"])
                all_suppliers_for_business.append({
                    "supplier_id": s.get("supplier_id"),
                    "supplier_name": s.get("supplier_name"),
                    "machine_name": m_name,
                    "location": s.get("location"),
                    "district": s.get("district"),
                    "state": s.get("state"),
                    "location_match_label": s.get("location_match_label", "State-level"),
                    "price_range": s.get("price_range"),
                    "contact": s.get("contact"),
                    "installation_available": s.get("installation_available", True),
                    "warranty_available": s.get("warranty_available", True),
                    "verified": s.get("verified", False),
                    "source": s.get("source", "GramVantage Verified Directory"),
                    "match_score": s.get("match_score", 85),
                    "match_highlights": s.get("match_highlights", [])
                })

    # Sort suppliers deterministically by match score
    all_suppliers_for_business.sort(key=lambda x: -x.get("match_score", 0))

    # 6. Cost Calculation: Starter Setup vs Standard Setup
    min_inv_b = float(business.get("minimum_investment", 80000.0))
    rec_inv_b = float(business.get("recommended_investment", 140000.0))
    if rec_inv_b <= min_inv_b:
        rec_inv_b = min_inv_b * 1.5

    # Essential equipment sum
    essential_eq_min = sum(m.price_min for m in machinery_reqs if m.priority == "Essential")
    if essential_eq_min == 0:
        essential_eq_min = min_inv_b * 0.45

    # All equipment sum for Standard
    all_eq_max = sum(m.price_max for m in machinery_reqs)
    if all_eq_max == 0:
        all_eq_max = rec_inv_b * 0.55

    # Ensure Starter Equipment is proportionate to minimum_investment
    starter_equip_cost = round(min(essential_eq_min, min_inv_b * 0.55), 2)
    starter_infra_cost = round(min_inv_b * 0.25, 2)
    starter_working_cap = round(max(10000.0, min_inv_b - (starter_equip_cost + starter_infra_cost)), 2)
    starter_total = round(starter_equip_cost + starter_infra_cost + starter_working_cap, 2)

    # Ensure Standard Equipment is proportionate to recommended_investment
    standard_equip_cost = round(max(starter_equip_cost * 1.3, min(all_eq_max, rec_inv_b * 0.50)), 2)
    standard_infra_cost = round(rec_inv_b * 0.25, 2)
    standard_working_cap = round(max(20000.0, rec_inv_b - (standard_equip_cost + standard_infra_cost)), 2)
    standard_total = round(standard_equip_cost + standard_infra_cost + standard_working_cap, 2)

    # Strict Guarantee: Starter is cheaper than standard
    if starter_total >= standard_total:
        standard_total = round(starter_total * 1.4, 2)
        standard_equip_cost = round(starter_equip_cost * 1.35, 2)
        standard_infra_cost = round(starter_infra_cost * 1.3, 2)
        standard_working_cap = round(standard_total - (standard_equip_cost + standard_infra_cost), 2)

    starter_breakdown = BusinessSetupCostBreakdown(
        equipment_cost=starter_equip_cost,
        infrastructure_cost=starter_infra_cost,
        working_capital=starter_working_cap,
        total_cost=starter_total
    )

    standard_breakdown = BusinessSetupCostBreakdown(
        equipment_cost=standard_equip_cost,
        infrastructure_cost=standard_infra_cost,
        working_capital=standard_working_cap,
        total_cost=standard_total
    )

    # 7. Funding Gap & User Investment Comparison
    funding_gap_starter = round(max(0.0, starter_total - user_inv), 2)
    funding_gap_standard = round(max(0.0, standard_total - user_inv), 2)

    # 8. Recommended Scale & Low-Capital Mode
    is_low_capital = user_inv < starter_total
    if user_inv >= standard_total:
        rec_scale = "Standard / Commercial Scale"
        scale_reason = f"Your available capital of ₹{user_inv:,.0f} fully supports a standard setup with enhanced capacity and equipment."
    elif user_inv >= starter_total:
        rec_scale = "Starter / Micro Scale"
        scale_reason = f"Your available capital of ₹{user_inv:,.0f} matches the starter setup requirements perfectly."
    else:
        rec_scale = "Micro Starter (Phased Setup)"
        scale_reason = (
            f"Your current investment (₹{user_inv:,.0f}) is below the complete starter setup (₹{starter_total:,.0f}). "
            f"A phased startup configuration is recommended with a funding gap of ₹{funding_gap_starter:,.0f} to be financed via micro-credit (PMMY / PMEGP)."
        )

    # Low-Capital Advice & Deferrals
    essential_machines = [m.machine_name for m in machinery_reqs if m.priority == "Essential"]
    non_essential_machines = [m.machine_name for m in machinery_reqs if m.priority != "Essential"]
    
    deferred_list = list(non_essential_machines)
    deferred_list.extend(["Automatic digital packaging & batch printing", "Dedicated commercial warehouse expansion", "Hired helper labour (initially self-operated)"])

    immediate_actions_list = [
        f"Procure only core essential machinery: {', '.join(essential_machines[:2]) if essential_machines else 'Primary processing machine'}",
        "Leverage existing family space / home shed to minimize initial infrastructure expense",
        f"Apply for PMMY Shishu/Kishore loan to cover the ₹{funding_gap_starter:,.0f} funding requirement for working capital"
    ]

    low_cap_advice = LowCapitalAdvice(
        is_low_capital=is_low_capital,
        advice=(
            "Start lean by procuring Phase 1 essential machinery only. Defer secondary packaging automation "
            "and additional storage until initial cash flow and local sales volume are proven."
            if is_low_capital else
            "Your investment provides healthy operational runway. Maintain a 3-month working capital reserve."
        ),
        deferred_items=deferred_list,
        immediate_actions=immediate_actions_list
    )

    # 9. Categorize Essential, Recommended, Optional items
    essential_items = [
        f"Core Machinery: {', '.join(essential_machines) if essential_machines else 'Primary processing unit'}",
        "Operating Space & Work Shed",
        "Commercial Utility Connections (Power & Water)",
        "First Production Batch Raw Material Stock",
        "Basic Safety & Hygiene Setup"
    ]

    recommended_items = [
        f"Auxiliary Equipment: {', '.join(non_essential_machines) if non_essential_machines else 'Semi-automatic heat sealer'}",
        "Precision Digital Weighing Scale",
        "Moisture-proof Finished Goods Racks",
        "Basic Accounting & Receipt Ledger"
    ]

    optional_items = [
        "Automatic Pouch Filling & Nitrogen Flushing Unit",
        "Commercial Solar Power Backup System",
        "Branded Custom-Printed Box Packaging",
        "Dedicated Delivery Transit Vehicle"
    ]

    # 10. Raw Materials Breakdown
    raw_mat_items: List[RawMaterialRequirement] = []
    cat_lower = category.lower()
    b_name_lower = b_name.lower()

    if "dairy" in cat_lower or "milk" in b_name_lower:
        raw_mat_items = [
            RawMaterialRequirement(item="Dry Cattle Feed & Green Fodder", source="Local farmers & Agri-cooperatives", estimated_monthly_cost=18000.0, priority="Essential"),
            RawMaterialRequirement(item="Veterinary Supplements & Mineral Mix", source="District veterinary pharmacy", estimated_monthly_cost=3500.0, priority="Essential"),
            RawMaterialRequirement(item="Testing Chemicals & Sanitizing Wash", source="Dairy equipment dealer", estimated_monthly_cost=2000.0, priority="Recommended")
        ]
    elif "spice" in cat_lower or "flour" in b_name_lower or "food" in cat_lower:
        raw_mat_items = [
            RawMaterialRequirement(item="Whole Grains / Raw Spices (Whole Chili, Turmeric, Cumin)", source="Nearest APMC Mandi / Farm-gate", estimated_monthly_cost=25000.0, priority="Essential"),
            RawMaterialRequirement(item="Food-Grade Printed / Plain Laminated Pouches", source="Regional packaging distributor", estimated_monthly_cost=4500.0, priority="Essential"),
            RawMaterialRequirement(item="Corrugated Outer Cartons & Sealing Tape", source="Taluka packaging wholesaler", estimated_monthly_cost=2500.0, priority="Recommended")
        ]
    elif "retail" in cat_lower or "grocery" in b_name_lower:
        raw_mat_items = [
            RawMaterialRequirement(item="FMCG & Daily Essential Packaged Inventory", source="Taluka wholesale distributors", estimated_monthly_cost=30000.0, priority="Essential"),
            RawMaterialRequirement(item="Carry Bags & Billing Rolls", source="Local wholesale market", estimated_monthly_cost=1500.0, priority="Essential")
        ]
    else:
        raw_mat_items = [
            RawMaterialRequirement(item="Primary Processing Raw Inputs", source="District wholesale market / APMC Mandi", estimated_monthly_cost=20000.0, priority="Essential"),
            RawMaterialRequirement(item="Packaging & Consumables", source="Local trade suppliers", estimated_monthly_cost=4000.0, priority="Recommended")
        ]

    # 11. Labour Requirements
    labour_reqs = [
        LabourRequirement(role="Entrepreneur / Machine Operator", count=1, skill_level="Semi-skilled (Owner-Operated)", priority="Essential"),
        LabourRequirement(role="General Helper / Packing Assistant", count=1, skill_level="Unskilled (Optional during launch)", priority="Recommended")
    ]

    # 12. Compliance Requirements
    compliance = [
        "Udyam MSME Registration (Free on udyamregistration.gov.in)",
        "Local Gram Panchayat / Municipal Trade NOC"
    ]
    if "food" in cat_lower or "dairy" in cat_lower or "spice" in cat_lower:
        compliance.insert(0, "FSSAI Basic Food Business Registration (₹100/year)")
    elif "retail" in cat_lower:
        compliance.insert(0, "Shop & Establishment Act Registration")

    # 13. Setup Phases (Purchase & Implementation Priority)
    setup_phases = [
        SetupPhase(
            phase_number=1,
            phase_name="PHASE 1 — MUST HAVE (Launch Operations)",
            items=[
                "Secure operating shed and complete water/power hookups",
                f"Procure Essential machinery ({', '.join(essential_machines[:2]) if essential_machines else 'Primary equipment'})",
                "Procure initial raw material stock (15 days inventory)",
                "Complete Udyam & basic regulatory registrations"
            ],
            focus="Get production operational with minimum upfront capital."
        ),
        SetupPhase(
            phase_number=2,
            phase_name="PHASE 2 — ADD AFTER STARTING (Quality & Market Reach)",
            items=[
                "Procure secondary equipment (Heat sealer / Digital weighing scale)",
                "Upgrade to branded customized pouch packaging",
                "Establish weekly supply tie-ups with 5-10 local village retail outlets"
            ],
            focus="Improve packaging quality, brand recognition, and recurring customer base."
        ),
        SetupPhase(
            phase_number=3,
            phase_name="PHASE 3 — SCALE UP (Capacity Expansion)",
            items=[
                "Add semi-automatic filling or automated secondary machinery",
                "Expand storage space with damp-proof racking",
                "Explore institutional supply contracts (schools, canteens, district traders)"
            ],
            focus="Scale production volume and expand regional distribution channels."
        )
    ]

    # 14. Data Quality Report
    verified_items = []
    if all_suppliers_for_business:
        verified_items.append(f"{len(all_suppliers_for_business)} Registered Equipment Suppliers (Curated & Verified Directory)")
    estimated_items = [
        "Indicative equipment price brackets (confirm with supplier before purchase)",
        "Working capital baseline based on MSME industry averages"
    ]
    missing_info = []
    if not user_profile.village:
        missing_info.append("Exact village location for doorstep delivery freight quotes")

    data_qual = DataQualityReport(
        verified_factors=verified_items,
        estimated_factors=estimated_items,
        missing_data=missing_info
    )

    return BusinessSetupResponse(
        business_id=b_id,
        business_name=b_name,
        recommended_scale=rec_scale,
        scale_reason=scale_reason,
        starter_setup=starter_breakdown,
        standard_setup=standard_breakdown,
        user_investment=user_inv,
        funding_gap=funding_gap_starter,
        funding_gap_standard=funding_gap_standard,
        infrastructure_requirements=infra_reqs,
        machinery=machinery_reqs,
        raw_materials=raw_mat_items,
        labour_requirements=labour_reqs,
        compliance_requirements=compliance,
        suppliers=all_suppliers_for_business,
        setup_phases=setup_phases,
        essential_items=essential_items,
        recommended_items=recommended_items,
        optional_items=optional_items,
        low_capital_advice=low_cap_advice,
        data_quality=data_qual,
        disclaimer="Business setup plan estimates equipment, infrastructure, and working capital deterministically from regional MSME standards. Prices are indicative and must be confirmed directly with suppliers."
    )
