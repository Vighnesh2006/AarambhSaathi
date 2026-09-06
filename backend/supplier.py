"""
Business Setup & Machinery Supplier Recommendation Engine (GramVantage AI).

Deterministic recommendation and search module for:
1. Identifying equipment required for any business idea
2. Estimating indicative machinery costs and ranges
3. Searching, filtering, and deterministically ranking potential equipment suppliers

IMPORTANT:
- Pure deterministic calculations (No Gemini calls for scoring/prices).
- Clearly demarcates indicative/demo data from live verified quotes.
- Incorporates location proximity prioritization without fabricating distance.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from backend.supplier_sources.local_database import LocalDatabaseSource
from backend.supplier_sources.indiamart import IndiaMARTSource
from backend.supplier_sources.tradeindia import TradeIndiaSource
from backend.supplier_sources.manufacturers import ManufacturerSource

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MACHINES_FILE = DATA_DIR / "machines.json"
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"

# Active adapter sources
ACTIVE_SOURCES = [
    LocalDatabaseSource(),
    IndiaMARTSource(),
    TradeIndiaSource(),
    ManufacturerSource()
]

# Business name alias mapping to match catalogue names with machine categories
BUSINESS_EQUIPMENT_MAP = {
    "spice": ["sp_pulverizer_01", "sp_ribbon_blender_02", "sp_pouch_packing_03", "gen_band_sealer_04", "gen_digital_weighing_05"],
    "dairy": ["dy_milking_machine_06", "dy_chaff_cutter_07", "dy_bulk_cooler_08", "gen_digital_weighing_05"],
    "poultry": ["pt_brooder_setup_09", "pt_drinker_feeder_10", "gen_digital_weighing_05"],
    "goat": ["dy_chaff_cutter_07", "gt_weighing_cage_11"],
    "mushroom": ["ms_autoclave_sterilizer_12", "ms_ultrasonic_humidifier_13", "gen_digital_weighing_05"],
    "fish": ["fs_pond_aerator_14", "gen_digital_weighing_05"],
    "aquaculture": ["fs_pond_aerator_14", "gen_digital_weighing_05"],
    "beekeeping": ["bk_extractor_honey_15", "gen_band_sealer_04"],
    "honey": ["bk_extractor_honey_15", "gen_band_sealer_04"],
    "flour": ["fl_commercial_chakki_16", "sp_pouch_packing_03", "gen_digital_weighing_05", "gen_band_sealer_04"],
    "atta": ["fl_commercial_chakki_16", "sp_pouch_packing_03", "gen_digital_weighing_05"],
    "pickle": ["pk_papad_press_17", "gen_band_sealer_04", "gen_digital_weighing_05"],
    "papad": ["pk_papad_press_17", "gen_band_sealer_04", "gen_digital_weighing_05"],
    "bakery": ["bk_deck_oven_18", "gen_band_sealer_04", "gen_digital_weighing_05"],
    "tailoring": ["tl_motorized_sewing_19"],
    "mobile": ["mb_smd_rework_20"],
    "bamboo": ["hc_bamboo_splitting_21"],
    "handicrafts": ["hc_bamboo_splitting_21", "gen_band_sealer_04"]
}


def load_all_machines() -> List[Dict[str, Any]]:
    if not MACHINES_FILE.exists():
        return []
    try:
        with open(MACHINES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def load_all_suppliers() -> List[Dict[str, Any]]:
    if not SUPPLIERS_FILE.exists():
        return []
    try:
        with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_required_machines(
    business_name: str,
    business_scale: str = "small"
) -> List[Dict[str, Any]]:
    """
    Identifies all equipment required to start the given business.
    Returns machine records with priority ("Essential", "Recommended", "Optional").
    """
    all_machines = load_all_machines()
    b_name_lower = (business_name or "").strip().lower()
    scale_lower = (business_scale or "small").strip().lower()

    # 1. First check direct alias mapping
    matched_machine_ids = []
    for kw, m_ids in BUSINESS_EQUIPMENT_MAP.items():
        if kw in b_name_lower:
            for mid in m_ids:
                if mid not in matched_machine_ids:
                    matched_machine_ids.append(mid)

    results = []
    if matched_machine_ids:
        # Strict exact alias mapping takes first priority
        machine_dict = {m["machine_id"]: m for m in all_machines}
        for mid in matched_machine_ids:
            if mid in machine_dict:
                rec = dict(machine_dict[mid])
                rec["price_type"] = "indicative"
                rec["price_note"] = "Prices are indicative and should be confirmed with the supplier before purchase."
                results.append(rec)
    else:
        # Fallback to category overlap
        for m in all_machines:
            categories = [c.lower() for c in m.get("business_categories", [])]
            if any(cat in b_name_lower or b_name_lower in cat for cat in categories):
                rec = dict(m)
                rec["price_type"] = "indicative"
                rec["price_note"] = "Prices are indicative and should be confirmed with the supplier before purchase."
                results.append(rec)

    # If no exact match found, provide common general processing baseline
    if not results:
        general_ids = ["gen_band_sealer_04", "gen_digital_weighing_05"]
        results = [dict(m) for m in all_machines if m.get("machine_id") in general_ids]

    return results


def calculate_supplier_score(
    supplier: Dict[str, Any],
    target_machine: Dict[str, Any],
    location: Optional[str] = None,
    budget: Optional[float] = None,
    capacity: Optional[str] = None
) -> Tuple[int, List[str], str]:
    """
    Deterministic Supplier Ranking Algorithm:
    - Budget Match:        30%
    - Location Match:      20%
    - Capacity Match:      20%
    - Business Fit:        15%
    - Verification:        10%
    - Service/Warranty:     5%
    Total: 100 points
    """
    score = 0.0
    highlights = []
    loc_status = "Nationwide"

    # Indicative machine price bounds
    p_min = supplier.get("estimated_price_min") or target_machine.get("estimated_price_min", 0.0)
    p_max = supplier.get("estimated_price_max") or target_machine.get("estimated_price_max", 0.0)

    # 1. Budget Match (30 points)
    if budget is not None and budget > 0:
        if p_max <= budget:
            score += 30.0
            highlights.append("✓ Fully within your specified equipment budget")
        elif p_min <= budget:
            # Overlaps budget
            ratio = (budget - p_min) / max(1.0, (p_max - p_min))
            partial_score = 15.0 + (15.0 * ratio)
            score += partial_score
            highlights.append("✓ Base models fit within your budget")
        else:
            diff = p_min - budget
            # Close overage penalty
            if diff <= budget * 0.25:
                score += 10.0
                highlights.append(f"⚠ Minimum model is ₹{diff:,.0f} above budget")
            else:
                score += 2.0
                highlights.append(f"⚠ Exceeds budget by ₹{diff:,.0f}")
    else:
        # No budget specified: neutral full base score
        score += 25.0
        highlights.append("✓ Standard competitive commercial pricing")

    # 2. Location Match (20 points)
    user_loc = (location or "").strip().lower()
    sup_city = supplier.get("location", "").strip().lower()
    sup_dist = supplier.get("district", "").strip().lower()
    sup_state = supplier.get("state", "").strip().lower()

    if user_loc:
        if user_loc in sup_city or user_loc in sup_dist or sup_city in user_loc:
            score += 20.0
            loc_status = "Same District / City"
            highlights.append(f"✓ Local supplier in {supplier.get('location')} (minimal shipping cost)")
        elif user_loc in sup_state or sup_state in user_loc:
            score += 15.0
            loc_status = "State-level match"
            highlights.append(f"✓ State-level manufacturer in {supplier.get('state')}")
        else:
            # Check western/northern/southern neighboring clusters
            score += 8.0
            loc_status = "Nationwide supplier"
            highlights.append(f"✓ Interstate supplier shipping from {supplier.get('location')}, {supplier.get('state')}")
    else:
        score += 12.0
        loc_status = "Nationwide"
        highlights.append(f"✓ Shipping available from {supplier.get('location')}, {supplier.get('state')}")

    # 3. Capacity Match (20 points)
    if capacity and capacity.strip():
        req_cap = capacity.strip().lower()
        sup_cap = supplier.get("capacity", "").lower()
        if any(part in sup_cap for part in req_cap.split()):
            score += 20.0
            highlights.append(f"✓ Meets target operating capacity ({supplier.get('capacity')})")
        else:
            score += 12.0
            highlights.append(f"✓ Standard production capacity ({supplier.get('capacity')})")
    else:
        score += 18.0
        highlights.append(f"✓ Rated capacity: {supplier.get('capacity', 'Standard micro-scale')}")

    # 4. Business Fit (15 points)
    # Checks if supplier specializes in the exact machine category
    target_id = target_machine.get("machine_id", "")
    if target_id in supplier.get("machine_ids", []):
        score += 15.0
        highlights.append(f"✓ Direct specialty manufacturer for {target_machine.get('machine_name')}")
    else:
        score += 8.0

    # 5. Verification Status (10 points)
    if supplier.get("verified", False):
        score += 10.0
        highlights.append("✓ Verified government / DIC empanelled supplier")
    else:
        score += 4.0
        highlights.append("⚠ Unverified demo listing — direct verification required")

    # 6. Service & Warranty Availability (5 points)
    service_score = 0.0
    if supplier.get("installation_available", False):
        service_score += 2.5
        highlights.append("✓ On-site installation assistance available")
    if supplier.get("warranty_available", False):
        service_score += 2.5
        highlights.append("✓ Equipment warranty provided")
    score += service_score

    final_score = int(min(100, max(1, round(score))))
    return final_score, highlights, loc_status


def search_suppliers(
    machine_id: str,
    location: Optional[str] = None,
    budget: Optional[float] = None,
    capacity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Searches and ranks suppliers for a specific machine_id across all active sources.
    Handles out-of-budget comparisons gracefully.
    """
    all_machines = load_all_machines()
    machine_map = {m["machine_id"]: m for m in all_machines}
    target_machine = machine_map.get(machine_id)

    if not target_machine:
        return {
            "machine": None,
            "suppliers": [],
            "message": f"Machine with ID '{machine_id}' was not found in catalog.",
            "budget_status": "not_found"
        }

    # Fetch suppliers from active sources
    raw_suppliers = []
    for src in ACTIVE_SOURCES:
        try:
            results = src.get_suppliers_for_machine(machine_id, location, budget)
            raw_suppliers.extend(results)
        except Exception:
            continue

    if not raw_suppliers:
        # Fallback to general local database search
        local_db = LocalDatabaseSource()
        raw_suppliers = local_db.get_suppliers_for_machine(machine_id, location, budget)

    # Deduplicate by supplier_id
    seen_ids = set()
    deduped_suppliers = []
    for s in raw_suppliers:
        if s["supplier_id"] not in seen_ids:
            seen_ids.add(s["supplier_id"])
            deduped_suppliers.append(s)

    scored_suppliers = []
    for s in deduped_suppliers:
        score, highlights, loc_status = calculate_supplier_score(
            supplier=s,
            target_machine=target_machine,
            location=location,
            budget=budget,
            capacity=capacity
        )

        p_min = s.get("estimated_price_min") or target_machine.get("estimated_price_min", 0.0)
        p_max = s.get("estimated_price_max") or target_machine.get("estimated_price_max", 0.0)

        entry = {
            "supplier_id": s.get("supplier_id"),
            "supplier_name": s.get("supplier_name"),
            "location": s.get("location"),
            "district": s.get("district"),
            "state": s.get("state"),
            "location_match_label": loc_status,
            "website": s.get("website"),
            "contact": s.get("contact"),
            "price_range": s.get("price_range") or f"₹{p_min:,.0f} - ₹{p_max:,.0f}",
            "estimated_price_min": p_min,
            "estimated_price_max": p_max,
            "price_type": s.get("source_type", "demo"),
            "capacity": s.get("capacity") or target_machine.get("capacity"),
            "installation_available": s.get("installation_available", False),
            "warranty_available": s.get("warranty_available", False),
            "verified": s.get("verified", False),
            "source": s.get("source", "Demo Database"),
            "last_verified": s.get("last_verified", "2026-08-01"),
            "match_score": score,
            "match_highlights": highlights,
            "budget_difference": max(0.0, p_min - budget) if budget else 0.0,
            "within_budget": (p_min <= budget) if budget else True
        }
        scored_suppliers.append(entry)

    # Sort deterministically by match_score descending, then price_min ascending
    scored_suppliers.sort(key=lambda x: (-x["match_score"], x["estimated_price_min"]))

    budget_status = "matched"
    warning = None
    if budget is not None and budget > 0:
        within_budget_count = sum(1 for s in scored_suppliers if s["within_budget"])
        if within_budget_count == 0 and scored_suppliers:
            budget_status = "over_budget"
            closest = scored_suppliers[0]
            diff = closest["budget_difference"]
            warning = (
                f"No supplier found within your specified budget of ₹{budget:,.0f}. "
                f"Closest option is ₹{closest['estimated_price_min']:,.0f} (Difference: ₹{diff:,.0f})."
            )

    return {
        "machine": target_machine,
        "suppliers": scored_suppliers,
        "total_suppliers": len(scored_suppliers),
        "budget_status": budget_status,
        "warning": warning,
        "disclaimer": (
            "GramVantage AI does not endorse or guarantee any supplier. "
            "Prices, availability, warranty, and technical specifications must be confirmed directly with the supplier before placing orders."
        )
    }


def get_supplier_recommendations(
    business_name: str,
    business_scale: str = "small",
    location: Optional[str] = None,
    budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    Complete end-to-end setup recommendation pipeline:
    1. Returns required machines with priority and price brackets
    2. Searches top potential suppliers for each required machine
    3. Calculates aggregate setup equipment investment
    """
    machines = get_required_machines(business_name, business_scale)

    total_min_equipment_cost = sum(m.get("estimated_price_min", 0.0) for m in machines if m.get("priority") == "Essential")
    total_max_equipment_cost = sum(m.get("estimated_price_max", 0.0) for m in machines if m.get("priority") == "Essential")

    # Allocate per-machine budget if overall budget given
    machine_budget = (budget / max(1, len(machines))) if budget else None

    machine_supplier_pairs = []
    warnings = []

    for m in machines:
        search_res = search_suppliers(
            machine_id=m["machine_id"],
            location=location,
            budget=machine_budget
        )
        if search_res.get("warning"):
            warnings.append(search_res["warning"])

        machine_supplier_pairs.append({
            "machine": m,
            "top_suppliers": search_res.get("suppliers", [])[:3],
            "total_found": search_res.get("total_suppliers", 0)
        })

    return {
        "business_name": business_name,
        "business_scale": business_scale,
        "location": location,
        "equipment_budget": budget,
        "estimated_essential_machinery_cost_min": total_min_equipment_cost,
        "estimated_essential_machinery_cost_max": total_max_equipment_cost,
        "machines": machines,
        "machine_supplier_pairs": machine_supplier_pairs,
        "warnings": list(set(warnings)),
        "disclaimer": (
            "GramVantage AI does not endorse or guarantee any supplier. "
            "Prices are indicative and should be confirmed directly with suppliers before purchase."
        )
    }
