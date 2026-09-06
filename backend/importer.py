import os
import json
import re
from pathlib import Path
import openpyxl
from backend.config import DATA_DIR, BUSINESSES_FILE

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def import_business_catalogue(excel_path: str) -> dict:
    """
    Imports, cleans, and standardizes business catalogue from Excel into GramVantage AI format.
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at: {excel_path}")

    wb = openpyxl.load_workbook(excel_path, data_only=True)
    
    # Try finding the business sheet
    sheet_name = 'Business Master' if 'Business Master' in wb.sheetnames else wb.sheetnames[0]
    sheet = wb[sheet_name]
    
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError("The provided sheet is empty.")

    header_row = [str(c).strip() if c is not None else '' for c in rows[0]]
    
    # Map column indexes
    col_map = {}
    for idx, h in enumerate(header_row):
        h_lower = h.lower()
        if 'id' in h_lower:
            col_map['id'] = idx
        elif 'name' in h_lower:
            col_map['name'] = idx
        elif 'main domain' in h_lower or 'domain' in h_lower or 'category' in h_lower:
            col_map['domain'] = idx
        elif 'type' in h_lower:
            col_map['type'] = idx
        elif 'fund' in h_lower or 'investment' in h_lower or 'capital' in h_lower:
            col_map['fund'] = idx
        elif 'skill 1' in h_lower or 'skill1' in h_lower:
            col_map['skill1'] = idx
        elif 'skill 2' in h_lower or 'skill2' in h_lower:
            col_map['skill2'] = idx
        elif 'skill 3' in h_lower or 'skill3' in h_lower:
            col_map['skill3'] = idx
        elif 'space' in h_lower or 'land' in h_lower:
            col_map['space'] = idx
        elif 'water' in h_lower:
            col_map['water'] = idx
        elif 'electr' in h_lower:
            col_map['elec'] = idx
        elif 'training' in h_lower:
            col_map['training'] = idx
        elif 'risk' in h_lower:
            col_map['risk'] = idx
        elif 'demand' in h_lower:
            col_map['demand'] = idx
        elif 'competition' in h_lower:
            col_map['comp'] = idx
        elif 'scalability' in h_lower:
            col_map['scalability'] = idx
        elif 'source' in h_lower or 'validation' in h_lower:
            col_map['source'] = idx

    imported_businesses = []
    domains_summary = {}

    for row_idx, r in enumerate(rows[1:], start=2):
        if not r or not any(r):
            continue
        
        b_id_raw = r[col_map.get('id', 0)] if 'id' in col_map else f"B{row_idx-1:03d}"
        if not b_id_raw:
            continue
        b_id_str = str(b_id_raw).strip()

        b_name = str(r[col_map.get('name', 1)] or f"Business {b_id_str}").strip()
        domain = str(r[col_map.get('domain', 2)] or "Agriculture & Allied").strip()
        b_type = str(r[col_map.get('type', 3)] or "Micro-enterprise").strip()

        # Parse minimum fund
        fund_val = r[col_map.get('fund', 4)]
        try:
            if isinstance(fund_val, (int, float)):
                min_fund = float(fund_val)
            else:
                # remove currency symbols, commas
                cleaned_num = re.sub(r'[^\d.]', '', str(fund_val))
                min_fund = float(cleaned_num) if cleaned_num else 80000.0
        except Exception:
            min_fund = 80000.0

        # Calculate recommended investment with standard buffer for working capital
        if min_fund <= 100000:
            rec_fund = round(min_fund * 1.5, -3)
        elif min_fund <= 500000:
            rec_fund = round(min_fund * 1.35, -3)
        else:
            rec_fund = round(min_fund * 1.25, -3)

        # Extract skills
        skills = []
        for sk_key in ['skill1', 'skill2', 'skill3']:
            if sk_key in col_map and col_map[sk_key] < len(r):
                val = r[col_map[sk_key]]
                if val and str(val).strip() and str(val).strip().lower() != 'none':
                    skills.append(str(val).strip())
        if not skills:
            skills = [domain.lower(), "micro-business management", "local trade"]

        # Resources
        space_req = str(r[col_map.get('space', 8)] or 'Small space').strip()
        water_req = str(r[col_map.get('water', 9)] or 'No').strip().lower() in ['yes', 'y', 'true', '1']
        elec_req = str(r[col_map.get('elec', 10)] or 'Yes').strip().lower() in ['yes', 'y', 'true', '1']

        resources = [space_req]
        if water_req:
            resources.append("Water supply")
        if elec_req:
            resources.append("Electricity connection")
        resources.append("Basic tools/setup")

        training = str(r[col_map.get('training', 11)] or 'Recommended').strip()
        risk_lvl = str(r[col_map.get('risk', 12)] or 'Medium').strip()
        demand_lvl = str(r[col_map.get('demand', 13)] or 'High').strip()
        comp_lvl = str(r[col_map.get('comp', 14)] or 'Medium').strip()
        scalability = str(r[col_map.get('scalability', 15)] or 'High').strip()
        source_val = str(r[col_map.get('source', 16)] or 'GramVantage Rural Catalogue').strip() if 'source' in col_map and col_map['source'] < len(r) else 'GramVantage Rural Catalogue'

        # Revenue and margin model
        margin_pct = 40 if risk_lvl.lower() == 'low' else 35 if risk_lvl.lower() == 'medium' else 45
        monthly_rev = round(min_fund * 0.32, 2)

        unique_slug = f"{b_id_str.lower()}_{slugify(b_name)}"

        business_record = {
            "id": unique_slug,
            "catalogue_id": b_id_str,
            "business_name": b_name,
            "category": domain,
            "business_type": b_type,
            "minimum_investment": min_fund,
            "recommended_investment": rec_fund,
            "required_skills": skills,
            "required_resources": resources,
            "space_requirement": space_req,
            "water_needed": water_req,
            "electricity_needed": elec_req,
            "training_required": training,
            "risk_level": risk_lvl,
            "market_factors": {
                "demand_level": demand_lvl,
                "competition": comp_lvl,
                "market_reach": f"Local village markets, district mandis, and retail consumers across {domain} trade networks",
                "seasonal_variance": "Moderate"
            },
            "revenue_factors": {
                "estimated_monthly_revenue_per_unit": monthly_rev,
                "margin_percentage": margin_pct
            },
            "common_expenses": [
                "Raw materials & consumables",
                "Electricity & utilities" if elec_req else "Operating tools maintenance",
                "Packaging & local transit",
                "Contingency working capital"
            ],
            "risks": [
                f"{risk_lvl} Risk: Price fluctuations of inputs and seasonal variations.",
                "Quality consistency and storage requirements."
            ],
            "suitable_locations": [
                "Rural agrarian villages",
                "Peri-urban clusters and weekly haats",
                "District trading centers"
            ],
            "scalability": scalability,
            "source_validation": source_val,
            "description": f"A scalable rural {b_type.lower()} in the {domain} sector. Requires {space_req} with an estimated minimum capital of ₹{min_fund:,.0f} and {training.lower()} skill development."
        }

        imported_businesses.append(business_record)
        domains_summary[domain] = domains_summary.get(domain, 0) + 1

    # Save to data/businesses.json
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(BUSINESSES_FILE, "w", encoding="utf-8") as f:
        json.dump(imported_businesses, f, indent=2, ensure_ascii=False)

    # Save summary metadata
    meta = {
        "source_file": excel_path,
        "total_businesses": len(imported_businesses),
        "domains_count": len(domains_summary),
        "domains_breakdown": domains_summary,
        "min_investment_overall": min(b["minimum_investment"] for b in imported_businesses),
        "max_investment_overall": max(b["minimum_investment"] for b in imported_businesses),
        "status": "Trained & Ingested into Knowledge Base"
    }

    meta_file = DATA_DIR / "catalogue_meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return meta
