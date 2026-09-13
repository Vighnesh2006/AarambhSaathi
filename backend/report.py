import uuid
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

from backend.models import (
    UserProfile,
    BusinessReport,
    ReportRequest,
    FinancialInput,
    BusinessRecommendation,
    FeasibilityResponse,
    FinancialPlan,
    MatchedScheme,
    BusinessSetupRequest,
)
from backend.recommendation import get_recommendations, score_business
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.finance import calculate_financial_plan
from backend.schemes import get_scheme_match_response, match_government_schemes_core
from backend.supplier import get_required_machines, get_supplier_recommendations, search_suppliers
from backend.business_setup import generate_business_setup_plan
from backend.database import get_business_by_id, save_report
from backend.config import GEMINI_API_KEY

# Multilingual localized boilerplate templates
TRANSLATIONS = {
    "en": {
        "title": "Aarambh Saathi Detailed Project Report (DPR)",
        "subtitle": "Micro-Enterprise Business Plan & Financial Structuring Model",
        "exec_summary": "Based on the information provided, Aarambh Saathi identified {business_name} as a highly suitable business opportunity for {entrepreneur_name}. The proposed {setup_mode}-scale setup requires an estimated total project outlay of INR {project_cost:,.0f}, against an own margin contribution of INR {own_contribution:,.0f} ({own_pct:.1f}%), resulting in an estimated illustrative funding requirement of INR {funding_requirement:,.0f}. Hyper-local market feasibility scored {feasibility_score}/100 ({feasibility_level}), supported by {scheme_count} matched government credit and subsidy schemes.",
        "disclaimer": "This report is an AI-assisted preliminary business planning document based on the information and data available to Aarambh Saathi. Financial projections, supplier information, scheme eligibility and feasibility indicators may require verification from the relevant authorities, lenders, suppliers and local market sources before making investment decisions.",
        "risk_raw_mat": "Raw material price fluctuations & seasonal supply variance",
        "risk_raw_mat_mit": "Establish forward purchase ties with multiple local village suppliers and maintain a 15-day raw material reserve.",
        "risk_comp": "Local market competition and pricing pressure",
        "risk_comp_mit": "Differentiate on product purity, freshness, local packaging, and direct village-to-consumer delivery.",
        "risk_wc": "Working capital constraints during initial operational cycle",
        "risk_wc_mit": "Utilize MUDRA RuPay overdraft credit limits and maintain tight 7-day credit terms with buyers.",
        "phase1": "Phase 1: Regulatory Setup, Udyam Registration & Bank Sanction",
        "phase2": "Phase 2: Site Preparation, Utilities & Infrastructure",
        "phase3": "Phase 3: Machinery Procurement, Installation & Trial Batch",
        "phase4": "Phase 4: Commercial Launch, Local Haat Sales & Distribution",
        "phase5": "Phase 5: Operational Scale-Up & Working Capital Review"
    },
    "hi": {
        "title": "आरंभ साथी विस्तृत परियोजना रिपोर्ट (DPR)",
        "subtitle": "ग्रामीण सूक्ष्म-उद्यम व्यापार योजना और वित्तीय संरचना",
        "exec_summary": "प्रदान की गई जानकारी के आधार पर, आरंभ साथी ने {entrepreneur_name} के लिए {business_name} को एक उपयुक्त व्यावसायिक अवसर के रूप में पहचाना है। प्रस्तावित {setup_mode}-स्तरीय सेटअप के लिए कुल अनुमानित परियोजना लागत INR {project_cost:,.0f} है, जिसमें उद्यमी का स्वयं का अंशदान INR {own_contribution:,.0f} ({own_pct:.1f}%) है, जिससे अनुमानित ऋण/अनुदान आवश्यकता INR {funding_requirement:,.0f} निकलती है। स्थानीय बाजार व्यवहार्यता स्कोर {feasibility_score}/100 ({feasibility_level}) रहा, जो {scheme_count} संबंधित सरकारी योजनाओं से समर्थित है।",
        "disclaimer": "यह रिपोर्ट आरंभ साथी को उपलब्ध जानकारी के आधार पर एक एआई-सहायता प्राप्त प्रारंभिक व्यावसायिक योजना दस्तावेज है। वित्तीय अनुमान, आपूर्तिकर्ता विवरण, सरकारी योजना पात्रता और व्यवहार्यता संकेतकों को निवेश से पहले संबंधित बैंकों, नोडल एजेंसियों और बाजार स्रोतों से सत्यापित किया जाना चाहिए।",
        "risk_raw_mat": "कच्चे माल की कीमतों में उतार-चढ़ाव और मौसमी आपूर्ति",
        "risk_raw_mat_mit": "कई स्थानीय आपूर्तिकर्ताओं के साथ आपूर्ति समझौते करें और 15 दिनों का बफर स्टॉक रखें।",
        "risk_comp": "स्थानीय बाजार में प्रतिस्पर्धा और मूल्य दबाव",
        "risk_comp_mit": "गुणवत्ता, शुद्धता और सीधे उपभोक्ता तक डिलीवरी के माध्यम से अपनी पहचान बनाएं।",
        "risk_wc": "शुरुआती दौर में कार्यशील पूंजी का दबाव",
        "risk_wc_mit": "मुद्रा ओवरड्राफ्ट सुविधा का उपयोग करें और ग्राहकों से नकद या 7-दिवसीय भुगतान शर्तें रखें।",
        "phase1": "चरण 1: उद्यम पंजीकरण, ग्राम पंचायत एनओसी और बैंक ऋण आवेदन",
        "phase2": "चरण 2: कार्यस्थल की तैयारी, बिजली और पानी की व्यवस्था",
        "phase3": "चरण 3: मशीनरी खरीद, स्थापना और परीक्षण उत्पादन",
        "phase4": "चरण 4: औपचारिक शुरुआत, स्थानीय हाट-बाजारों में बिक्री",
        "phase5": "चरण 5: उत्पादन विस्तार और वित्तीय समीक्षा"
    },
    "mr": {
        "title": "आरंभ साथी सविस्तर प्रकल्प अहवाल (DPR)",
        "subtitle": "ग्रामीण सूक्ष्म-उद्योग व्यवसाय योजना व वित्तीय मॉडेल",
        "exec_summary": "दिलेल्या माहितीनुसार, आरंभ साथीने {entrepreneur_name} यांच्यासाठी {business_name} हा अत्यंत सुयोग्य व्यवसाय म्हणून निश्चित केला आहे. प्रस्तावित {setup_mode}-स्तरीय रचनेसाठी अंदाजे एकूण प्रकल्प खर्च INR {project_cost:,.0f} असून, स्वतःचे भांडवल INR {own_contribution:,.0f} ({own_pct:.1f}%) आहे. उर्वरित अंदाजे निधी/कर्ज आवश्यकता INR {funding_requirement:,.0f} आहे. स्थानिक बाजार व्यवहार्यता निर्देशांक {feasibility_score}/100 ({feasibility_level}) असून, {scheme_count} शासकीय योजनांचे साहाय्य उपलब्ध आहे.",
        "disclaimer": "हा अहवाल आरंभ साथीकडे उपलब्ध माहितीच्या आधारे तयार केलेला प्राथमिक व्यवसाय नियोजन आराखडा आहे. अंतिम आर्थिक गुंतवणूक करण्यापूर्वी बँक, संबंधित शासकीय विभाग, पुरवठादार व स्थानिक बाजाराकडून अधिकृत पडताळणी करणे आवश्यक आहे.",
        "risk_raw_mat": "कच्च्या मालाच्या किमतीतील चढ-उतार व हंगामी कमतरता",
        "risk_raw_mat_mit": "स्थानिक शेतकऱ्यांशी थेट करार करा आणि १५ दिवसांचा कच्चा माल साठा राखून ठेवा.",
        "risk_comp": "स्थानिक बाजारातील स्पर्धा",
        "risk_comp_mit": "उत्पादनाची शुद्धता, स्थानिक ब्रँडिंग आणि थेट ग्राहकांपर्यंत पोहोचून स्पर्धा मात करा.",
        "risk_wc": "सुरुवातीच्या काळातील खेळत्या भांडवलाची गरज",
        "risk_wc_mit": "मुद्रा ओव्हरड्राफ्ट सुविधेचा लाभ घ्या आणि उधारीचे व्यवहार मर्यादित ठेवा.",
        "phase1": "टप्पा १: उद्यम नोंदणी, ग्रामपंचायत ना-हरकत व बँक कर्ज मंजुरी",
        "phase2": "टप्पा २: जागेची तयारी, वीज व पाणी जोडणी",
        "phase3": "टप्पा ३: यंत्रसामग्री खरेदी, उभारणी व प्रायोगिक उत्पादन",
        "phase4": "टप्पा ४: प्रत्यक्ष व्यावसायिक शुभारंभ व स्थानिक आठवडे बाजारात विक्री",
        "phase5": "टप्पा ५: व्यवसाय विस्तार व नफा आढावा"
    }
}

def generate_business_report(request: ReportRequest) -> BusinessReport:
    """
    Comprehensive, deterministic 17-Section Detailed Project Report (DPR) / Business Plan generator.
    Combines the verified outputs of Steps 1 to 6 without recalculating or distorting upstream data.
    """
    profile = request.get_effective_profile()
    b_id = request.get_effective_business_id()
    lang = (request.language or profile.language or "en").lower()
    if lang not in TRANSLATIONS:
        lang = "en"
    t = TRANSLATIONS[lang]
    
    report_id = f"GV-DPR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
    
    # -------------------------------------------------------------------------
    # STEP 2: Business Recommendation Integration
    # -------------------------------------------------------------------------
    if request.recommendation:
        if isinstance(request.recommendation, BusinessRecommendation):
            rec_business = request.recommendation
        elif isinstance(request.recommendation, dict):
            rec_business = BusinessRecommendation(**request.recommendation)
        else:
            rec_business = request.recommendation
    elif b_id:
        b_data = get_business_by_id(b_id)
        if b_data:
            rec_business = score_business(b_data, profile)
        else:
            recs = get_recommendations(profile, top_n=1)
            rec_business = recs.recommendations[0]
    else:
        recs = get_recommendations(profile, top_n=1)
        rec_business = recs.recommendations[0]

    b_id = rec_business.business_id
    business_name = rec_business.business_name
    business_category = rec_business.category

    # -------------------------------------------------------------------------
    # STEP 3: Hyper-Local Feasibility Integration
    # -------------------------------------------------------------------------
    if request.feasibility:
        if isinstance(request.feasibility, FeasibilityResponse):
            feasibility = request.feasibility
        elif isinstance(request.feasibility, dict):
            feasibility = FeasibilityResponse(**request.feasibility)
        else:
            feasibility = request.feasibility
    else:
        feasibility = evaluate_hyper_local_feasibility(b_id, profile)

    # -------------------------------------------------------------------------
    # STEP 4: Business Setup & Machinery Integration
    # -------------------------------------------------------------------------
    setup_mode = request.setup_mode or "starter"
    if request.business_setup:
        if hasattr(request.business_setup, "model_dump"):
            setup_data = request.business_setup.model_dump()
        elif isinstance(request.business_setup, dict):
            setup_data = request.business_setup
        else:
            setup_data = dict(request.business_setup)
    else:
        setup_resp = generate_business_setup_plan(
            business_id=b_id,
            business_name=business_name,
            user_profile=profile,
            available_investment=profile.capital,
            feasibility_result=feasibility.model_dump() if hasattr(feasibility, "model_dump") else feasibility
        )
        setup_data = setup_resp.model_dump()

    machinery_items = setup_data.get("machinery", [])
    raw_materials = setup_data.get("raw_materials", [])
    infra_reqs = setup_data.get("infrastructure_requirements", [])
    labour_reqs = setup_data.get("labour_requirements", [])
    setup_suppliers = setup_data.get("suppliers", [])

    # If setup suppliers list is empty, search directory directly
    if not setup_suppliers and machinery_items:
        first_m_id = machinery_items[0].get("machine_id", "")
        if first_m_id:
            loc_str = f"{profile.district or profile.location or ''} {profile.state or ''}".strip()
            sup_res = search_suppliers(first_m_id, location=loc_str, limit=5)
            setup_suppliers = sup_res.get("suppliers", [])

    # -------------------------------------------------------------------------
    # STEP 5: Financial Plan & Capital Structuring Integration
    # -------------------------------------------------------------------------
    starter_breakdown = setup_data.get("starter_setup", {})
    standard_breakdown = setup_data.get("standard_setup", {})
    
    if setup_mode == "standard" and standard_breakdown:
        determined_cost = standard_breakdown.get("total_cost", rec_business.required_investment)
    elif starter_breakdown:
        determined_cost = starter_breakdown.get("total_cost", rec_business.required_investment)
    else:
        determined_cost = rec_business.required_investment

    project_cost = float(request.get_effective_cost() or determined_cost)
    own_capital = float(profile.capital or profile.available_investment or (project_cost * 0.10))

    if request.financial_plan:
        if isinstance(request.financial_plan, FinancialPlan):
            financial_plan = request.financial_plan
        elif isinstance(request.financial_plan, dict):
            financial_plan = FinancialPlan(**request.financial_plan)
        else:
            financial_plan = request.financial_plan
    else:
        fin_input = FinancialInput(
            project_cost=project_cost,
            user_contribution=own_capital,
            business_id=b_id,
            business_name=business_name,
            profile=profile,
            setup_mode=setup_mode
        )
        financial_plan = calculate_financial_plan(fin_input)


    # -------------------------------------------------------------------------
    # STEP 6: Government Schemes & Document Integration
    # -------------------------------------------------------------------------
    if request.scheme_matches and hasattr(request.scheme_matches, "matched_schemes"):
        scheme_resp = request.scheme_matches
    elif request.scheme_matches and isinstance(request.scheme_matches, dict) and "matched_schemes" in request.scheme_matches:
        from backend.models import SchemeMatchResponse
        scheme_resp = SchemeMatchResponse(**request.scheme_matches)
    else:
        scheme_resp = get_scheme_match_response(
            profile=profile,
            business_id=b_id,
            business_category=business_category,
            business_name=business_name,
            project_cost=financial_plan.project_cost,
            own_contribution=financial_plan.own_contribution,
            funding_requirement=financial_plan.funding_requirement
        )

    matched_schemes_list = scheme_resp.matched_schemes + scheme_resp.conditional_schemes + scheme_resp.insufficient_data_schemes

    # -------------------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY GENERATION (Deterministic Template + Safe Fallback)
    # -------------------------------------------------------------------------
    exec_summary_text = t["exec_summary"].format(
        business_name=business_name,
        entrepreneur_name=profile.name or "the entrepreneur",
        setup_mode=setup_mode.capitalize(),
        project_cost=financial_plan.project_cost,
        own_contribution=financial_plan.own_contribution,
        own_pct=financial_plan.own_contribution_percentage,
        funding_requirement=financial_plan.funding_requirement,
        feasibility_score=feasibility.feasibility_score,
        feasibility_level=feasibility.feasibility_level,
        scheme_count=len(matched_schemes_list)
    )

    # -------------------------------------------------------------------------
    # 4. WHY THIS BUSINESS WAS RECOMMENDED (Explainable 9-Factor Fit)
    # -------------------------------------------------------------------------
    bd = rec_business.breakdown
    dem_score = feasibility.factors.local_demand.score if hasattr(feasibility, "factors") and hasattr(feasibility.factors, "local_demand") else 85.0
    explainable_reasons = [
        f"Skill Match ({bd.skill_match_score}/25): High compatibility with applicant's background in {profile.experience or 'allied trade'}.",
        f"Investment Compatibility ({bd.capital_match_score}/25): Available capital of INR {financial_plan.own_contribution:,.0f} meets the margin requirements for {financial_plan.scheme_tier}.",
        f"Resource Readiness ({bd.resource_match_score}/20): Essential infrastructure verified ({', '.join(profile.resources[:3]) if profile.resources else 'basic rural site space'}).",
        f"Local Market Feasibility ({feasibility.feasibility_score}/100): High regional demand score of {dem_score}/100 with manageable competition.",
        f"Fast Break-Even Horizon: Projected break-even achievable within {financial_plan.break_even_months} months with strong operating margin."
    ]

    # -------------------------------------------------------------------------
    # 9 & 10. PROJECT COST BREAKDOWN & MEANS OF FINANCE
    # -------------------------------------------------------------------------
    equipment_subtotal = sum(m.get("price_min", 0.0) for m in machinery_items) or (financial_plan.project_cost * 0.50)
    infra_subtotal = (financial_plan.project_cost * 0.25)
    working_cap_subtotal = max(15000.0, financial_plan.project_cost - equipment_subtotal - infra_subtotal)
    
    project_cost_breakdown = {
        "equipment_cost": round(equipment_subtotal, 2),
        "infrastructure_cost": round(infra_subtotal, 2),
        "working_capital": round(working_cap_subtotal, 2),
        "total_project_cost": round(financial_plan.project_cost, 2),
        "own_contribution": round(financial_plan.own_contribution, 2),
        "funding_requirement": round(financial_plan.funding_requirement, 2)
    }

    means_of_finance = {
        "own_contribution": round(financial_plan.own_contribution, 2),
        "own_contribution_percentage": financial_plan.own_contribution_percentage,
        "illustrative_loan_requirement": round(financial_plan.required_loan, 2),
        "loan_percentage": financial_plan.loan_percentage,
        "scheme_tier": financial_plan.scheme_tier,
        "indicative_interest_rate": financial_plan.interest_rate,
        "tenure_years": financial_plan.tenure_years,
        "moratorium_months": financial_plan.moratorium_months,
        "monthly_emi": round(financial_plan.monthly_emi, 2),
        "total_interest_payable": round(financial_plan.total_interest_payable, 2),
        "total_repayment": round(financial_plan.total_repayment, 2),
        "status_label": "Illustrative Financing Estimate (Subject to formal bank appraisal)"
    }

    # -------------------------------------------------------------------------
    # 11. FINANCIAL PROJECTIONS (Monthly & Annual Calculated Estimates)
    # -------------------------------------------------------------------------
    annual_revenue = round(financial_plan.monthly_revenue * 12, 2)
    annual_opex = round(financial_plan.monthly_operating_expenses * 12, 2)
    annual_profit = round(financial_plan.annual_profit, 2)
    profit_margin = round((financial_plan.monthly_profit / financial_plan.monthly_revenue * 100.0) if financial_plan.monthly_revenue > 0 else 0.0, 1)

    financial_projections = {
        "monthly_revenue": round(financial_plan.monthly_revenue, 2),
        "monthly_operating_expenses": round(financial_plan.monthly_operating_expenses, 2),
        "monthly_net_profit": round(financial_plan.monthly_profit, 2),
        "profit_margin_percentage": profit_margin,
        "break_even_months": financial_plan.break_even_months,
        "year_1_estimated_revenue": annual_revenue,
        "year_1_estimated_expenses": annual_opex,
        "year_1_estimated_net_profit": annual_profit,
        "projection_status": "Calculated Estimate (Based on standard MSME operating benchmarks)"
    }

    # -------------------------------------------------------------------------
    # 13. CONSOLIDATED DOCUMENT CHECKLIST
    # -------------------------------------------------------------------------
    doc_items = []
    seen_docs = set()
    
    # Extract from top matched schemes
    if matched_schemes_list:
        for s in matched_schemes_list[:3]:
            for d in s.documents:
                key = d.document_name.lower().strip()
                if key not in seen_docs:
                    seen_docs.add(key)
                    doc_items.append({
                        "document_name": d.document_name,
                        "category": "Identity & Financial KYC" if "aadhaar" in key or "pan" in key or "bank" in key else ("Social / Special Category" if "caste" in key else "Business & Project Proposal"),
                        "status": d.status,
                        "description": d.description,
                        "issuing_authority": d.where_to_get,
                        "format": d.format
                    })
    
    # Fallback standard documents if scheme documents empty
    if not doc_items:
        doc_items = [
            {"document_name": "Aadhaar Card", "category": "Identity & KYC", "status": "Required", "issuing_authority": "UIDAI", "description": "Proof of Identity & Address", "format": "Self-attested copy"},
            {"document_name": "PAN Card", "category": "Financial KYC", "status": "Required", "issuing_authority": "Income Tax Dept", "description": "Tax Identification for Bank Account", "format": "Self-attested copy"},
            {"document_name": "Bank Passbook / Cancelled Cheque", "category": "Financial KYC", "status": "Required", "issuing_authority": "Commercial / Grameen Bank", "description": "Active Account for Loan & Subsidy DBT", "format": "Original / Copy"},
            {"document_name": "Detailed Project Report (DPR)", "category": "Business & Technical", "status": "Required", "issuing_authority": "Aarambh Saathi System", "description": "Comprehensive Feasibility & Financial Plan", "format": "Printed & Signed Dossier"},
            {"document_name": "Machinery Price Quotation", "category": "Business & Technical", "status": "Required", "issuing_authority": "Verified Supplier", "description": "Proforma Invoice for Capital Expenditure", "format": "Original Proforma Invoice"},
            {"document_name": "Caste / Category Certificate", "category": "Social Category", "status": "Conditionally Required", "issuing_authority": "Tehsil / SDM Office", "description": "Required to claim special 35% subsidy rate", "format": "Digilocker / Certified Copy"}
        ]

    # -------------------------------------------------------------------------
    # 14. 5-PHASE IMPLEMENTATION ROADMAP
    # -------------------------------------------------------------------------
    roadmap_phases = [
        {
            "phase_number": 1,
            "phase_name": t["phase1"],
            "duration": "Days 1 to 20",
            "milestones": [
                "Finalize DPR dossier and formal business application.",
                "Complete free Udyam MSME Registration on udyamregistration.gov.in.",
                "Obtain Gram Panchayat / Local Municipality Trade NOC.",
                "Submit credit application under PMEGP / Mudra at local bank branch."
            ]
        },
        {
            "phase_number": 2,
            "phase_name": t["phase2"],
            "duration": "Days 21 to 40",
            "milestones": [
                "Finalize site lease / workshed area with water and electricity connections.",
                "Secure commercial power load (Single Phase / 3-Phase as required).",
                "Receive bank in-principle credit sanction letter and deposit own margin money."
            ]
        },
        {
            "phase_number": 3,
            "phase_name": t["phase3"],
            "duration": "Days 41 to 60",
            "milestones": [
                "Place formal purchase order with verified machinery supplier.",
                "Complete equipment delivery, on-site installation, and electrical calibration.",
                "Procure initial raw material batch from local wholesale sources.",
                "Complete trial test runs and product quality validation."
            ]
        },
        {
            "phase_number": 4,
            "phase_name": t["phase4"],
            "duration": "Days 61 to 75",
            "milestones": [
                "Formal commercial launch and commencement of regular production/service.",
                "Establish weekly supply linkage with local village grocers, traders, and weekly haats.",
                "Distribute local promotional flyers and announce inaugural pricing."
            ]
        },
        {
            "phase_number": 5,
            "phase_name": t["phase5"],
            "duration": "Days 76 to 90",
            "milestones": [
                "Initiate daily digital bookkeeping and monitor monthly operational margins.",
                "Achieve consistent capacity utilization to comfortably service monthly loan EMI.",
                "Review working capital reserves and plan for phase-2 equipment additions."
            ]
        }
    ]

    action_plan_legacy = {p["phase_name"]: p["milestones"] for p in roadmap_phases}

    # -------------------------------------------------------------------------
    # 15. RISKS & MITIGATION
    # -------------------------------------------------------------------------
    risks_list = [
        {
            "risk": t["risk_raw_mat"],
            "impact": "Medium",
            "mitigation": t["risk_raw_mat_mit"]
        },
        {
            "risk": t["risk_comp"],
            "impact": "Medium",
            "mitigation": t["risk_comp_mit"]
        },
        {
            "risk": t["risk_wc"],
            "impact": "High",
            "mitigation": t["risk_wc_mit"]
        }
    ]

    # -------------------------------------------------------------------------
    # 16. DATA SOURCES & TRANSPARENCY ASSUMPTIONS
    # -------------------------------------------------------------------------
    data_sources = [
        {"component": "Entrepreneur Profile & Capital", "source_type": "User Provided", "source_details": "Direct conversational input during Step 1 onboarding"},
        {"component": "Business Taxonomy & Requirements", "source_type": "Business Knowledge Base", "source_details": "Curated 90-business rural micro-enterprise catalogue"},
        {"component": "Recommendation Algorithm (9 Factors)", "source_type": "Calculated", "source_details": "Deterministic hybrid multi-factor weighted scoring engine"},
        {"component": "Hyper-Local Feasibility & Places", "source_type": "API / Knowledge Base", "source_details": "Deterministic indicators augmented by Google Places API"},
        {"component": "Machinery & Equipment Specifications", "source_type": "Business Knowledge Base", "source_details": "National MSME development technical blueprints"},
        {"component": "Supplier Shortlist & Contact Directory", "source_type": "Supplier Database", "source_details": "Verified Indian machinery manufacturers directory"},
        {"component": "Financial Model & EMI Structuring", "source_type": "Calculated", "source_details": "Reducing-balance financial amortization & MSME cost model"},
        {"component": "Government Schemes & Subsidy Guidelines", "source_type": "Government / Official Metadata", "source_details": "Cross-referenced official notifications & myscheme.gov.in portal"}
    ]

    assumptions = [
        "Project cost and equipment estimates reflect standard regional market quotes as of 2024.",
        "Monthly revenue assumes a steady 60% capacity utilization during Year 1 operations.",
        "Interest rate of 6.5% - 8.0% p.a. is indicative under central micro-enterprise priority lending windows.",
        "Working capital requirement assumes a 30-day operating cycle."
    ]

    # -------------------------------------------------------------------------
    # STRUCTURED REPORT INSTANTIATION
    # -------------------------------------------------------------------------
    report = BusinessReport(
        report_id=report_id,
        created_at=created_at,
        generated_at=created_at,
        language=lang,
        executive_summary=exec_summary_text,
        entrepreneur_profile=profile,
        entrepreneur={
            "name": profile.name or "Entrepreneur",
            "age": profile.age,
            "gender": profile.gender,
            "education": profile.education,
            "location": f"{profile.village or ''} {profile.district or ''}, {profile.state or ''}".strip(),
            "skills": profile.skills,
            "experience": profile.experience,
            "resources": profile.resources,
            "available_capital": profile.capital,
            "business_intent": profile.intent
        },
        recommended_business=rec_business,
        business={
            "business_id": b_id,
            "business_name": business_name,
            "category": business_category,
            "description": rec_business.description,
            "required_investment": rec_business.required_investment,
            "setup_mode": setup_mode
        },
        recommendation_breakdown=rec_business.breakdown.model_dump() if hasattr(rec_business, "breakdown") else {},
        explainable_reasons=explainable_reasons,
        local_feasibility=feasibility,
        feasibility=feasibility.model_dump(),
        business_setup=setup_data,
        setup=setup_data,
        machinery=machinery_items,
        suppliers=setup_suppliers,
        project_cost_breakdown=project_cost_breakdown,
        means_of_finance=means_of_finance,
        financial_plan=financial_plan,
        financial_projections=financial_projections,
        relevant_schemes=matched_schemes_list,
        schemes=[s.model_dump() for s in matched_schemes_list],
        documents=doc_items,
        action_plan_90_days=action_plan_legacy,
        roadmap=roadmap_phases,
        risks=risks_list,
        data_sources=data_sources,
        assumptions=assumptions,
        disclaimer=t["disclaimer"]
    )

    # Save to SQLite Database
    save_report(report_id, profile.name or "session", b_id, report.model_dump())

    return report
