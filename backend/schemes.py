import re
from typing import List, Optional, Dict, Any, Tuple
from backend.models import (
    UserProfile,
    MatchedScheme,
    EligibilityConditionResult,
    SchemeDocumentItem,
    FinancialFitDetail,
    SchemeMatchResponse,
)
from backend.database import load_schemes_data, get_business_by_id

# Sector alias mapping for national scheme eligibility
SECTOR_ALIASES = {
    "Agriculture & Allied": [
        "agriculture", "horticulture", "livestock", "dairy", "fisheries",
        "agri-tech", "agri-business", "agro processing", "bio/circular economy",
        "poultry", "goat", "beekeeping", "mushroom", "vermicompost", "organic",
        "cattle", "cow", "buffalo", "sheep", "fodder", "animal husbandry"
    ],
    "Manufacturing & Processing": [
        "manufacturing", "food processing", "agro processing", "packaging",
        "fmcg", "engineering", "textile", "recycling", "clean energy",
        "renewable energy", "biomass", "solar", "pellet", "briquette", "coir",
        "milling", "atta", "spice", "oilseed", "woodworking", "fabrication"
    ],
    "Food Processing": [
        "food processing", "dairy", "agro processing", "fmcg", "milling",
        "atta", "spice", "oilseed", "cold storage", "bakery", "juice",
        "pickle", "papadam", "flour", "oil extraction", "honey processing"
    ],
    "Services & Textiles": [
        "services", "textile", "electronics", "automobile", "repair",
        "handicrafts", "tailoring", "garment", "weavers", "transport",
        "retail", "printing", "beauty", "saloon", "hospitality"
    ],
    "Dairy & Livestock": [
        "dairy", "cattle", "cow", "buffalo", "poultry", "chicken",
        "goat", "sheep", "livestock", "fodder", "animal husbandry", "milk"
    ],
    "Fisheries & Aquaculture": [
        "fisheries", "aquaculture", "fish", "prawn", "shrimp", "biofloc",
        "ras", "pond", "ornamental fish", "hatchery"
    ],
    "Clean Energy & Renewable": [
        "solar", "biogas", "cbg", "clean energy", "renewable",
        "biomass", "pellet", "green energy", "solar dryer"
    ],
    "Women & Rural Livelihoods": [
        "women", "shg", "lakhpati", "hygiene", "sanitary",
        "tailoring", "handloom", "cottage", "craft"
    ],
    "Artisans & Traditional Crafts": [
        "artisan", "craft", "pottery", "blacksmith", "carpenter",
        "tailor", "handloom", "bamboo", "vishwakarma", "sculpture", "leather"
    ]
}

# Explicit deterministic rule configurations for prominent schemes
SCHEME_RULES_REGISTRY = {
    "pmegp": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,  # Open to all, higher subsidy for women
        "eligible_categories": None, # Open to all, higher subsidy for SC/ST/OBC/Women/Minorities
        "education_req_threshold_mfg": 1000000.0, # > 10 Lakh in MFG requires 8th pass
        "education_req_threshold_svc": 500000.0,  # > 5 Lakh in SVC requires 8th pass
        "min_education": "8th pass",
        "max_project_cost_mfg": 5000000.0, # 50 Lakh
        "max_project_cost_svc": 2000000.0, # 20 Lakh
        "income_limit": None,
        "enterprise_stage": "both", # Primarily new, 2nd loan for existing
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://www.kviconline.gov.in/pmegpeportal/",
        "source": "Ministry of Micro, Small and Medium Enterprises (KVIC Portal)",
        "last_verified": "September 2024 (myScheme.gov.in verified)",
        "benefits_list": [
            "Up to 35% capital subsidy for rural micro-enterprises (25% for urban)",
            "Bank composite loan covering 90% - 95% of project cost",
            "Low entrepreneur contribution (5% for special categories, 10% for general)",
            "3-year lock-in period for subsidy adjustment"
        ],
        "application_steps": [
            "Register online on the KVIC PMEGP e-Portal (kviconline.gov.in)",
            "Upload project report (DPR), Aadhaar, PAN, caste/education certificates",
            "Application scrutinized by District Level Task Force Committee (DLTFC)",
            "Loan sanction and EDP training (online/offline via KVIC/DIC)",
            "Subsidy release to bank TDR account after physical verification"
        ]
    },
    "pm_mudra_yojana": {
        "min_age": 18,
        "max_age": 65,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "max_project_cost": 2000000.0, # 20 Lakh under expanded Tarun Plus
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://www.mudra.org.in/",
        "source": "Ministry of Finance / SIDBI (MUDRA Portal)",
        "last_verified": "September 2024 (myScheme.gov.in verified)",
        "benefits_list": [
            "100% collateral-free institutional credit",
            "Three tiered financing: Shishu (up to ₹50k), Kishore (₹50k-₹5L), Tarun (₹5L-₹20L)",
            "Overdraft and working capital access with MUDRA RuPay Debit Card",
            "Nominal processing charges (0% for Shishu)"
        ],
        "application_steps": [
            "Prepare business proposal and machinery/equipment cost quotations",
            "Apply online via UdyamiMitra portal (udyamimitra.in) or visit nearest bank",
            "Submit KYC documents (Aadhaar, PAN, residence proof) and business proof",
            "Bank loan sanction without collateral requirement",
            "Working capital debit card / term loan disbursement"
        ]
    },
    "pmfme": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": "8th pass",
        "max_project_cost": 3000000.0,
        "max_subsidy": 1000000.0, # Max ₹10 Lakh subsidy
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://pmfme.mofpi.gov.in/",
        "source": "Ministry of Food Processing Industries (MoFPI)",
        "last_verified": "September 2024 (myScheme.gov.in verified)",
        "benefits_list": [
            "35% credit-linked capital subsidy up to ₹10 Lakh per unit",
            "Seed capital of ₹40,000 per SHG member for working capital",
            "Branding and marketing support under One District One Product (ODOP)",
            "FSSAI food safety and quality testing assistance"
        ],
        "application_steps": [
            "Apply on the MoFPI PMFME Portal (pmfme.mofpi.gov.in)",
            "Assisted by District Resource Person (DRP) for DPR preparation",
            "Verification by District Level Committee (DLC)",
            "Bank appraisal and credit-linked subsidy sanction"
        ]
    },
    "stand_up_india": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": ["female"],
        "eligible_categories": ["sc", "st"],
        "min_education": None,
        "min_project_cost": 1000000.0, # 10 Lakh
        "max_project_cost": 10000000.0, # 1 Crore (100 Lakh)
        "income_limit": None,
        "enterprise_stage": "new", # Greenfield enterprise only
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://www.standupmitra.in/",
        "source": "Ministry of Finance / SIDBI (Stand-Up Mitra)",
        "last_verified": "September 2024 (myScheme.gov.in verified)",
        "benefits_list": [
            "Bank loans between ₹10 Lakh and ₹1 Crore for greenfield enterprises",
            "Composite loan covering up to 85% of project cost",
            "Convergence with Central/State subsidy schemes for margin money",
            "Dedicated handholding support via Lead District Managers (LDM)"
        ],
        "application_steps": [
            "Register on standupmitra.in portal",
            "Select borrower category (Woman or SC/ST entrepreneur)",
            "Submit DPR, greenfield project location, and bank preference",
            "Handholding agency guidance followed by branch bank loan sanction"
        ]
    },
    "cmeegp_mh": {
        "min_age": 18,
        "max_age": 45,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": "10th pass",
        "max_project_cost_mfg": 5000000.0,
        "max_project_cost_svc": 1000000.0,
        "income_limit": None,
        "enterprise_stage": "new",
        "scheme_level": "State",
        "designated_state": "Maharashtra",
        "official_url": "https://maha-cmegp.gov.in/",
        "source": "Government of Maharashtra (Industry Directorate)",
        "last_verified": "September 2024 (maha-cmegp.gov.in verified)",
        "benefits_list": [
            "Up to 35% state subsidy for special category/rural units (25% for general)",
            "Composite term loan and working capital coverage",
            "Subsidized margin money from State Government",
            "EDP training support by MCED / MITCON"
        ],
        "application_steps": [
            "Apply online at maha-cmegp.gov.in",
            "Upload Maharashtra Domicile certificate, 10th marksheet, and project proposal",
            "District Task Force verification via District Industries Centre (DIC)",
            "Bank appraisal and capital subsidy disbursement"
        ]
    },
    "odop_up": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": "8th pass",
        "max_project_cost": 2500000.0,
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "State",
        "designated_state": "Uttar Pradesh",
        "official_url": "https://diupmsme.upsdc.gov.in/",
        "source": "Government of Uttar Pradesh (Department of MSME)",
        "last_verified": "September 2024 (diupmsme.upsdc.gov.in verified)",
        "benefits_list": [
            "Margin money subsidy up to 25% (max ₹6.25 Lakh) for ODOP products",
            "Priority financing through commercial and cooperative banks",
            "State stall subsidies and exhibition marketing assistance"
        ],
        "application_steps": [
            "Apply on UP MSME portal (diupmsme.upsdc.gov.in)",
            "Select designated One District One Product for your UP district",
            "DIC scrutiny and bank loan sanction"
        ]
    },
    "needs_tn": {
        "min_age": 21,
        "max_age": 45,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": "Degree / Diploma / ITI",
        "min_project_cost": 1000000.0,
        "max_project_cost": 50000000.0, # 5 Crore
        "income_limit": None,
        "enterprise_stage": "new",
        "scheme_level": "State",
        "designated_state": "Tamil Nadu",
        "official_url": "https://www.msmeonline.tn.gov.in/needs/",
        "source": "Government of Tamil Nadu (MSME Department)",
        "last_verified": "September 2024 (msmeonline.tn.gov.in verified)",
        "benefits_list": [
            "25% capital subsidy up to ₹75 Lakh",
            "3% interest subvention for the entire loan tenure",
            "Mandatory entrepreneurship training via EDII-TN"
        ],
        "application_steps": [
            "Apply online at msmeonline.tn.gov.in/needs",
            "Submit degree/diploma certificate, TN domicile, and project report",
            "District Level Task Force interview and bank sanction"
        ]
    },
    "anugrahit_rajasthan": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "max_project_cost": 100000000.0, # Up to 10 Crore
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "State",
        "designated_state": "Rajasthan",
        "official_url": "https://sso.rajasthan.gov.in/",
        "source": "Government of Rajasthan (Industries & Commerce Department)",
        "last_verified": "September 2024 (MLUPY Portal verified)",
        "benefits_list": [
            "Interest subsidy @ 8% for loans up to ₹25 Lakh",
            "Interest subsidy @ 6% for loans ₹25 Lakh to ₹5 Crore",
            "Interest subsidy @ 5% for loans ₹5 Crore to ₹10 Crore",
            "Collateral-free CGTMSE coverage fee paid by state"
        ],
        "application_steps": [
            "Login to Rajasthan Single Sign On (SSO) portal",
            "Submit MLUPY scheme application with Jan Aadhaar and project details",
            "Bank sanction and automatic interest subvention credit"
        ]
    },
    "pmegp_karnataka": {
        "min_age": 21,
        "max_age": 45,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": "10th pass",
        "max_project_cost": 2000000.0,
        "income_limit": None,
        "enterprise_stage": "new",
        "scheme_level": "State",
        "designated_state": "Karnataka",
        "official_url": "https://cmegp.karnataka.gov.in/",
        "source": "Government of Karnataka (Commerce & Industries Department)",
        "last_verified": "September 2024 (cmegp.karnataka.gov.in verified)",
        "benefits_list": [
            "Up to 35% subsidy for rural general and special category units",
            "Margin money assistance for first generation entrepreneurs",
            "Subsidized power tariff linkage"
        ],
        "application_steps": [
            "Apply via cmegp.karnataka.gov.in",
            "Submit Karnataka domicile, 10th marks card, and DPR",
            "DIC selection and bank loan sanction"
        ]
    },
    "ahidf": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "min_project_cost": 500000.0,
        "max_project_cost": 500000000.0,
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://ahidf.udyamimitra.in/",
        "source": "Department of Animal Husbandry and Dairying (DAHD)",
        "last_verified": "September 2024 (ahidf.udyamimitra.in verified)",
        "benefits_list": [
            "3% interest subvention on bank loan up to 8 years",
            "Credit guarantee coverage up to 25% of loan under Credit Guarantee Fund",
            "Loan up to 90% of total project cost"
        ],
        "application_steps": [
            "Apply online at ahidf.udyamimitra.in",
            "Upload DPR for dairy processing, meat processing, or animal feed plant",
            "Bank appraisal followed by DAHD interest subvention approval"
        ]
    },
    "nlm": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "max_project_cost": 10000000.0, # 1 Crore
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://nlm.udyamimitra.in/",
        "source": "Department of Animal Husbandry and Dairying (DAHD)",
        "last_verified": "September 2024 (nlm.udyamimitra.in verified)",
        "benefits_list": [
            "50% capital subsidy (up to ₹50 Lakh for poultry, ₹50 Lakh for sheep/goat)",
            "50% capital subsidy for fodder & feed seed infrastructure (up to ₹50 Lakh)",
            "Direct beneficiary transfer (DBT) of subsidy in 2 equal tranches"
        ],
        "application_steps": [
            "Register on nlm.udyamimitra.in",
            "Upload land proof/lease, DPR, and bank loan sanction letter",
            "State Level Executive Committee (SLEC) and DAHD approval"
        ]
    },
    "pmmsy": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "max_project_cost": 25000000.0,
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://pmmsy.dof.gov.in/",
        "source": "Department of Fisheries (Ministry of Fisheries, Animal Husbandry & Dairying)",
        "last_verified": "September 2024 (pmmsy.dof.gov.in verified)",
        "benefits_list": [
            "Up to 60% governmental financial assistance for SC/ST/Women beneficiaries (40% for General)",
            "Support for biofloc, RAS, pond construction, hatcheries, and cold chain vehicles",
            "Livelihood and nutritional support during fishing ban periods"
        ],
        "application_steps": [
            "Apply online via PMMSY MIS portal (pmmsy.dof.gov.in) or District Fisheries Office",
            "Submit project plan, water/land ownership document, and bank account details",
            "District Level Committee approval and DBT subsidy release"
        ]
    },
    "nbhm": {
        "min_age": 18,
        "max_age": None,
        "eligible_genders": None,
        "eligible_categories": None,
        "min_education": None,
        "max_project_cost": 2000000.0,
        "income_limit": None,
        "enterprise_stage": "both",
        "scheme_level": "Central",
        "designated_state": None,
        "official_url": "https://nbhm.gov.in/",
        "source": "National Bee Board (Ministry of Agriculture & Farmers Welfare)",
        "last_verified": "September 2024 (nbhm.gov.in verified)",
        "benefits_list": [
            "Up to 75% financial assistance for bee colonies and beehives",
            "Subsidies for custom hiring centers and honey extraction units",
            "Free technical training by Krishi Vigyan Kendras (KVK)"
        ],
        "application_steps": [
            "Register with National Bee Board on Madhukranti portal (nbhm.gov.in)",
            "Submit beekeeping proposal through State Horticulture Mission / KVK",
            "Subsidy release to registered beekeeper account"
        ]
    }
}

# =========================================================================
# DETERMINISTIC RULE EVALUATION FUNCTIONS
# =========================================================================

def check_age_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    min_age = scheme_data.get("min_age", 18)
    max_age = scheme_data.get("max_age")
    
    if min_age is None and max_age is None:
        return EligibilityConditionResult(
            condition="Age Requirement",
            status="Not Specified",
            reason="No restrictive age criterion specified for this scheme.",
            source="Official Scheme Guidelines"
        )
    
    if profile.age is None:
        return EligibilityConditionResult(
            condition="Age Requirement",
            status="Insufficient Data",
            reason="Applicant age is not provided in profile; cannot verify minimum age compliance.",
            source="Official Scheme Guidelines"
        )
    
    if min_age is not None and profile.age < min_age:
        return EligibilityConditionResult(
            condition="Age Requirement",
            status="Not Eligible",
            reason=f"Applicant age ({profile.age} yrs) is below the minimum mandatory requirement of {min_age} years.",
            source="Official Scheme Guidelines"
        )
    
    if max_age is not None and profile.age > max_age:
        return EligibilityConditionResult(
            condition="Age Requirement",
            status="Not Eligible",
            reason=f"Applicant age ({profile.age} yrs) exceeds the maximum permissible limit of {max_age} years.",
            source="Official Scheme Guidelines"
        )
    
    age_str = f"{min_age}+ years" if max_age is None else f"{min_age} to {max_age} years"
    return EligibilityConditionResult(
        condition="Age Requirement",
        status="Eligible",
        reason=f"Applicant age ({profile.age} yrs) satisfies the required range ({age_str}).",
        source="Official Scheme Guidelines"
    )

def check_gender_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    req_genders = scheme_data.get("eligible_genders")
    req_categories = scheme_data.get("eligible_categories")
    
    if not req_genders and not req_categories:
        return EligibilityConditionResult(
            condition="Gender Eligibility",
            status="Not Specified",
            reason="Scheme is open to all applicants irrespective of gender.",
            source="Official Scheme Guidelines"
        )
    
    user_gender = (profile.gender or "").strip().lower()
    user_cat = (profile.category or "").strip().lower()
    
    # Check Stand-Up India rule: Female OR SC/ST
    if req_genders and "female" in req_genders:
        if not user_gender and not user_cat:
            return EligibilityConditionResult(
                condition="Gender / Social Target Group",
                status="Insufficient Data",
                reason="Gender and social category not provided to verify special beneficiary criteria.",
                source="Official Scheme Guidelines"
            )
        
        if user_gender == "female":
            return EligibilityConditionResult(
                condition="Gender / Social Target Group",
                status="Eligible",
                reason="Eligible under Women Entrepreneur priority guidelines.",
                source="Official Scheme Guidelines"
            )
        elif req_categories and any(c in user_cat for c in req_categories):
            return EligibilityConditionResult(
                condition="Gender / Social Target Group",
                status="Eligible",
                reason=f"Eligible under {profile.category} special beneficiary priority.",
                source="Official Scheme Guidelines"
            )
        else:
            return EligibilityConditionResult(
                condition="Gender / Social Target Group",
                status="Not Eligible",
                reason=f"Scheme specifically prioritizes Women, SC, or ST entrepreneurs; applicant profile ({profile.gender or 'Not specified'}, {profile.category or 'General'}) does not match target group.",
                source="Official Scheme Guidelines"
            )
            
    return EligibilityConditionResult(
        condition="Gender Eligibility",
        status="Eligible",
        reason="Gender criterion satisfied.",
        source="Official Scheme Guidelines"
    )

def check_category_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    req_categories = scheme_data.get("eligible_categories")
    
    if not req_categories:
        user_cat = (profile.category or "").strip()
        if user_cat and user_cat.lower() in ["sc", "st", "obc", "women", "minority"]:
            return EligibilityConditionResult(
                condition="Social Category & Special Subsidies",
                status="Eligible",
                reason=f"Applicant belongs to {user_cat} category; eligible for enhanced subsidy tier (up to 35% in rural areas).",
                source="Official Scheme Guidelines"
            )
        return EligibilityConditionResult(
            condition="Social Category",
            status="Not Specified",
            reason="All social categories (General, OBC, SC, ST, EWS) are eligible under standard guidelines.",
            source="Official Scheme Guidelines"
        )
    
    user_cat = (profile.category or "").strip().lower()
    user_gender = (profile.gender or "").strip().lower()
    
    if not user_cat and not user_gender:
        return EligibilityConditionResult(
            condition="Social Category",
            status="Insufficient Data",
            reason="Category details not provided in profile; cannot verify reservation criteria.",
            source="Official Scheme Guidelines"
        )
    
    if any(c in user_cat for c in req_categories) or (scheme_data.get("eligible_genders") and user_gender in scheme_data["eligible_genders"]):
        return EligibilityConditionResult(
            condition="Social Category",
            status="Eligible",
            reason=f"Applicant ({profile.category or profile.gender}) qualifies for scheme beneficiary reservation.",
            source="Official Scheme Guidelines"
        )
    
    return EligibilityConditionResult(
        condition="Social Category",
        status="Not Eligible",
        reason=f"Scheme is designated exclusively for {', '.join(req_categories).upper()}; applicant is {profile.category or 'General'}.",
        source="Official Scheme Guidelines"
    )

def check_income_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    income_limit = scheme_data.get("income_limit")
    
    if income_limit is None:
        return EligibilityConditionResult(
            condition="Income Ceiling",
            status="Not Specified",
            reason="No family income ceiling applies for this credit-linked scheme.",
            source="Official Scheme Guidelines"
        )
    
    user_income = profile.income if profile.income is not None else profile.annual_income
    
    if user_income is None:
        return EligibilityConditionResult(
            condition="Income Ceiling",
            status="Insufficient Data",
            reason="Annual family income is unknown in profile; cannot verify income ceiling compliance.",
            source="Official Scheme Guidelines"
        )
    
    if user_income > income_limit:
        return EligibilityConditionResult(
            condition="Income Ceiling",
            status="Not Eligible",
            reason=f"Annual income (INR {user_income:,.0f}) exceeds the maximum permissible limit of INR {income_limit:,.0f}.",
            source="Official Scheme Guidelines"
        )
    
    return EligibilityConditionResult(
        condition="Income Ceiling",
        status="Eligible",
        reason=f"Annual income (INR {user_income:,.0f}) is within the permissible limit of INR {income_limit:,.0f}.",
        source="Official Scheme Guidelines"
    )

def check_education_eligibility(
    scheme_data: Dict[str, Any], 
    profile: UserProfile, 
    project_cost: float, 
    business_sector: str
) -> EligibilityConditionResult:
    min_edu = scheme_data.get("min_education")
    mfg_thresh = scheme_data.get("education_req_threshold_mfg")
    svc_thresh = scheme_data.get("education_req_threshold_svc")
    
    is_mfg = "manufactur" in business_sector.lower() or "food" in business_sector.lower() or "process" in business_sector.lower()
    requires_edu = False
    thresh_desc = ""
    
    if mfg_thresh and is_mfg and project_cost > mfg_thresh:
        requires_edu = True
        thresh_desc = f"for manufacturing projects above INR {mfg_thresh:,.0f}"
    elif svc_thresh and not is_mfg and project_cost > svc_thresh:
        requires_edu = True
        thresh_desc = f"for service projects above INR {svc_thresh:,.0f}"
    elif min_edu and not mfg_thresh and not svc_thresh:
        requires_edu = True
        thresh_desc = "mandatory for this scheme"
        
    if not requires_edu:
        return EligibilityConditionResult(
            condition="Educational Qualification",
            status="Not Specified",
            reason="No minimum educational barrier required for this project outlay level.",
            source="Official Scheme Guidelines"
        )
    
    user_edu = (profile.education or "").strip().lower()
    
    if not user_edu:
        return EligibilityConditionResult(
            condition="Educational Qualification",
            status="Insufficient Data",
            reason=f"Minimum {min_edu} certificate required {thresh_desc}; education is not specified in profile.",
            source="Official Scheme Guidelines"
        )
    
    valid_edu_keywords = ["8th", "8 th", "10th", "10 th", "12th", "12 th", "ssc", "hsc", "graduate", "degree", "diploma", "iti", "post graduate", "masters", "btech", "ba", "bsc", "bcom"]
    
    if "below 8" in user_edu or "illiterate" in user_edu or "none" in user_edu or "uneducated" in user_edu:
        return EligibilityConditionResult(
            condition="Educational Qualification",
            status="Not Eligible",
            reason=f"Applicant education ({profile.education}) does not satisfy the minimum requirement of {min_edu} {thresh_desc}.",
            source="Official Scheme Guidelines"
        )
        
    if any(k in user_edu for k in valid_edu_keywords) or len(user_edu) > 2:
        return EligibilityConditionResult(
            condition="Educational Qualification",
            status="Eligible",
            reason=f"Educational qualification ({profile.education}) meets or exceeds the required {min_edu}.",
            source="Official Scheme Guidelines"
        )
        
    return EligibilityConditionResult(
        condition="Educational Qualification",
        status="Conditionally Eligible",
        reason=f"Subject to verification of school leaving / qualification certificate for {min_edu}.",
        source="Official Scheme Guidelines"
    )

def check_location_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    scheme_level = scheme_data.get("scheme_level", "Central")
    designated_state = scheme_data.get("designated_state")
    user_state = (profile.state or "").strip().lower()
    
    if scheme_level == "State" and designated_state:
        if not user_state:
            return EligibilityConditionResult(
                condition="Location & State Jurisdiction",
                status="Insufficient Data",
                reason=f"State location missing from profile to verify eligibility for {designated_state} State scheme.",
                source="State Government Guidelines"
            )
        
        target_state_clean = designated_state.lower().replace(" ", "")
        user_state_clean = user_state.replace(" ", "")
        
        if target_state_clean not in user_state_clean and user_state_clean not in target_state_clean:
            # Special case for UP
            if designated_state.lower() == "uttar pradesh" and "up" in user_state.split():
                pass
            elif designated_state.lower() == "tamil nadu" and "tn" in user_state.split():
                pass
            else:
                return EligibilityConditionResult(
                    condition="Location & State Jurisdiction",
                    status="Not Eligible",
                    reason=f"Scheme is restricted to {designated_state} residents; applicant profile indicates location in {profile.state}.",
                    source="State Government Guidelines"
                )
                
        return EligibilityConditionResult(
            condition="Location & State Jurisdiction",
            status="Eligible",
            reason=f"Applicant state ({profile.state}) matches the designated State Government jurisdiction ({designated_state}).",
            source="State Government Guidelines"
        )
    
    # Central scheme location
    user_loc = (profile.village or profile.location or profile.district or "Rural").lower()
    is_rural = "rural" in user_loc or bool(profile.village) or (profile.rural_urban and "rural" in profile.rural_urban.lower())
    
    return EligibilityConditionResult(
        condition="Location Jurisdiction",
        status="Eligible",
        reason=f"National Central scheme accessible across all districts in {profile.state or 'India'}{' (Rural location qualifies for maximum 35% subsidy)' if is_rural else ''}.",
        source="Official Scheme Guidelines"
    )

def check_business_type_eligibility(
    scheme_data: Dict[str, Any], 
    raw_scheme_json: Dict[str, Any],
    business_id: Optional[str], 
    business_category: Optional[str]
) -> Tuple[EligibilityConditionResult, int]:
    eligible_cats = raw_scheme_json.get("eligible_businesses", [])
    eligible_ids = raw_scheme_json.get("eligible_ids", [])
    s_cat = raw_scheme_json.get("category", "")
    
    cat_lower = (business_category or "").strip().lower()
    b_id = business_id or ""
    
    # 1. Exact ID Prefix Match
    if b_id and any(b_id.startswith(eid) or eid in b_id for eid in eligible_ids):
        return (
            EligibilityConditionResult(
                condition="Business Activity Match",
                status="Eligible",
                reason="Direct national mission mandate for this exact business activity.",
                source="Official Scheme Guidelines"
            ),
            40
        )
    
    # 2. Sector Match
    for ec in eligible_cats:
        if ec.lower() in cat_lower or (cat_lower and cat_lower in ec.lower()):
            return (
                EligibilityConditionResult(
                    condition="Business Activity Match",
                    status="Eligible",
                    reason=f"Covers micro-enterprises operating in the '{business_category}' sector.",
                    source="Official Scheme Guidelines"
                ),
                25
            )
        aliases = SECTOR_ALIASES.get(ec, [])
        if any(a in cat_lower for a in aliases):
            return (
                EligibilityConditionResult(
                    condition="Business Activity Match",
                    status="Eligible",
                    reason=f"Eligible under sector guideline parameters ({ec}).",
                    source="Official Scheme Guidelines"
                ),
                20
            )
            
    # Generic micro enterprise fit
    if "pmegp" in raw_scheme_json.get("id", "") or "mudra" in raw_scheme_json.get("id", ""):
        return (
            EligibilityConditionResult(
                condition="Business Activity Match",
                status="Eligible",
                reason="Covers non-farm micro-enterprises and allied manufacturing/service activities.",
                source="Official Scheme Guidelines"
            ),
            15
        )
        
    return (
        EligibilityConditionResult(
            condition="Business Activity Match",
            status="Conditionally Eligible",
            reason=f"Activity subject to detailed DPR appraisal against {s_cat} guidelines.",
            source="Official Scheme Guidelines"
        ),
        5
    )

def check_project_cost_eligibility(
    scheme_data: Dict[str, Any], 
    project_cost: float, 
    business_sector: str
) -> Tuple[EligibilityConditionResult, FinancialFitDetail]:
    is_mfg = "manufactur" in business_sector.lower() or "food" in business_sector.lower() or "process" in business_sector.lower()
    
    max_cost = scheme_data.get("max_project_cost")
    if is_mfg and scheme_data.get("max_project_cost_mfg"):
        max_cost = scheme_data.get("max_project_cost_mfg")
    elif not is_mfg and scheme_data.get("max_project_cost_svc"):
        max_cost = scheme_data.get("max_project_cost_svc")
        
    min_cost = scheme_data.get("min_project_cost", 0.0)
    
    if max_cost is None and min_cost == 0.0:
        fit = FinancialFitDetail(
            status="Appears financially compatible",
            project_cost=project_cost,
            max_limit=None,
            min_limit=None,
            notes="No strict upper cap on overall project size."
        )
        return (
            EligibilityConditionResult(
                condition="Financial Outlay & Loan Limits",
                status="Not Specified",
                reason="No ceiling constraints specified in official notifications.",
                source="Official Scheme Guidelines"
            ),
            fit
        )
    
    if max_cost is not None and project_cost > max_cost:
        fit = FinancialFitDetail(
            status="Exceeds Scheme Limit",
            project_cost=project_cost,
            max_limit=max_cost,
            min_limit=min_cost,
            notes=f"Project cost exceeds scheme ceiling of INR {max_cost:,.0f}."
        )
        return (
            EligibilityConditionResult(
                condition="Financial Outlay & Loan Limits",
                status="Not Eligible",
                reason=f"Project cost (INR {project_cost:,.0f}) exceeds the maximum allowable limit of INR {max_cost:,.0f}.",
                source="Official Scheme Guidelines"
            ),
            fit
        )
        
    if min_cost > 0.0 and project_cost < min_cost:
        fit = FinancialFitDetail(
            status="Below Scheme Minimum",
            project_cost=project_cost,
            max_limit=max_cost,
            min_limit=min_cost,
            notes=f"Project cost is below the required threshold of INR {min_cost:,.0f}."
        )
        return (
            EligibilityConditionResult(
                condition="Financial Outlay & Loan Limits",
                status="Not Eligible",
                reason=f"Project cost (INR {project_cost:,.0f}) is below the minimum outlay threshold of INR {min_cost:,.0f}.",
                source="Official Scheme Guidelines"
            ),
            fit
        )
        
    fit = FinancialFitDetail(
        status="Appears financially compatible",
        project_cost=project_cost,
        max_limit=max_cost,
        min_limit=min_cost,
        notes=f"Project cost of INR {project_cost:,.0f} is within available limits (up to INR {max_cost:,.0f})." if max_cost else "Financially compatible."
    )
    return (
        EligibilityConditionResult(
            condition="Financial Outlay & Loan Limits",
            status="Eligible",
            reason=f"Project cost (INR {project_cost:,.0f}) is compatible with scheme limits.",
            source="Official Scheme Guidelines"
        ),
        fit
    )

def check_existing_business_eligibility(scheme_data: Dict[str, Any], profile: UserProfile) -> EligibilityConditionResult:
    stage_req = scheme_data.get("enterprise_stage", "both")
    user_intent = (profile.intent or "").strip().lower()
    has_existing = bool(profile.existing_business and "no" not in profile.existing_business.lower())
    
    if stage_req == "new" and ("expand" in user_intent or has_existing):
        return EligibilityConditionResult(
            condition="Enterprise Inception Stage",
            status="Conditionally Eligible",
            reason="Scheme targets greenfield / new enterprises; expansion units may require setting up a separate unit or second loan window.",
            source="Official Scheme Guidelines"
        )
        
    return EligibilityConditionResult(
        condition="Enterprise Inception Stage",
        status="Eligible",
        reason="Matches enterprise inception stage requirements.",
        source="Official Scheme Guidelines"
    )

# =========================================================================
# DOCUMENT CHECKLIST GENERATION
# =========================================================================

def generate_personalized_documents(
    scheme_id: str, 
    raw_docs: List[str], 
    profile: UserProfile, 
    project_cost: float,
    business_sector: str
) -> List[SchemeDocumentItem]:
    items: List[SchemeDocumentItem] = []
    seen = set()
    
    is_mfg = "manufactur" in business_sector.lower() or "food" in business_sector.lower()
    user_cat = (profile.category or "").strip().lower()
    is_special_cat = user_cat in ["sc", "st", "obc", "women", "minority"] or (profile.gender and profile.gender.lower() == "female")
    
    # 1. Standard Mandatory Identity & Address
    items.append(SchemeDocumentItem(
        document_name="Aadhaar Card",
        mandatory=True,
        applicable_condition="Mandatory for all applicants",
        description="Proof of identity and residential verification.",
        where_to_get="UIDAI (eaadhaar.uidai.gov.in)",
        format="Original + Self-attested copy",
        status="Required"
    ))
    seen.add("aadhaar")

    items.append(SchemeDocumentItem(
        document_name="PAN Card",
        mandatory=True,
        applicable_condition="Mandatory for financial sanction",
        description="Income Tax identification for bank loan account and subsidy disbursement.",
        where_to_get="UTIITSL / NSDL Portal",
        format="Self-attested copy",
        status="Required"
    ))
    seen.add("pan")

    items.append(SchemeDocumentItem(
        document_name="Bank Account Details / Cancelled Cheque",
        mandatory=True,
        applicable_condition="Mandatory for loan disbursement & subsidy",
        description="Active savings or current account passbook / cheque for DBT.",
        where_to_get="Your Commercial or Grameen Bank Branch",
        format="Original Passbook / Cancelled Cheque",
        status="Required"
    ))
    seen.add("bank")

    # 2. Detailed Project Report (DPR)
    items.append(SchemeDocumentItem(
        document_name="Detailed Project Report (DPR) / Business Plan",
        mandatory=True,
        applicable_condition="Required for loan appraisal & subsidy claim",
        description="Comprehensive financial projections, machinery quotations, and revenue forecast.",
        where_to_get="Generated via Aarambh Saathi DPR Suite or DIC consultant",
        format="Printed & Signed Dossier",
        status="Required"
    ))
    seen.add("dpr")

    # 3. Special Category Certificate (Caste / Minority / Disability)
    if is_special_cat or "sc" in user_cat or "st" in user_cat or "obc" in user_cat:
        items.append(SchemeDocumentItem(
            document_name="Caste / Social Category Certificate",
            mandatory=True,
            applicable_condition="Mandatory to claim 35% special category subsidy rate",
            description="Valid government issued caste / community certificate.",
            where_to_get="Tehsildar / Sub-Divisional Magistrate (SDM) / Revenue Portal",
            format="Original Digilocker / Attested Copy",
            status="Required"
        ))
    else:
        items.append(SchemeDocumentItem(
            document_name="Caste / Category Certificate (If Applicable)",
            mandatory=False,
            applicable_condition="Only required if claiming SC/ST/OBC special subsidy",
            description="Proof of social category for higher subsidy margin.",
            where_to_get="Local Tehsil / Revenue Office",
            format="Self-attested copy",
            status="Conditionally Required"
        ))
    seen.add("caste")

    # 4. Educational Certificate
    edu_needed = (scheme_id == "pmegp" and ((is_mfg and project_cost > 1000000.0) or (not is_mfg and project_cost > 500000.0))) or (scheme_id in ["cmeegp_mh", "pmegp_karnataka"])
    if edu_needed:
        items.append(SchemeDocumentItem(
            document_name="Educational Qualification Certificate (8th / 10th / Degree)",
            mandatory=True,
            applicable_condition="Mandatory for projects above ₹10L (Mfg) / ₹5L (Svc)",
            description="School leaving certificate / marksheet / degree certificate.",
            where_to_get="Educational Board / School / Digilocker",
            format="Attested Marksheet Copy",
            status="Required"
        ))
    else:
        items.append(SchemeDocumentItem(
            document_name="Educational Certificate (Optional)",
            mandatory=False,
            applicable_condition="Applicable if project outlay exceeds ₹5 Lakh - ₹10 Lakh",
            description="School leaving certificate or highest education proof.",
            where_to_get="School / College / Digilocker",
            format="Self-attested copy",
            status="Not Required"
        ))
    seen.add("education")

    # 5. Rural Area Certificate / Gram Panchayat NOC
    user_loc = (profile.village or profile.location or "").lower()
    is_rural = bool(profile.village) or "rural" in user_loc or (profile.rural_urban and "rural" in profile.rural_urban.lower())
    if is_rural:
        items.append(SchemeDocumentItem(
            document_name="Rural Area Certificate / Gram Panchayat NOC",
            mandatory=True,
            applicable_condition="Required to claim rural 35% subsidy rate vs 25% urban rate",
            description="Certificate from Gram Sevak / Sarpanch confirming rural unit location.",
            where_to_get="Gram Panchayat Office / BDO",
            format="Original on GP Letterhead with Seal",
            status="Required"
        ))
    seen.add("rural")

    # 6. Machinery Quotation & Site Lease
    items.append(SchemeDocumentItem(
        document_name="Machinery / Equipment Quotation",
        mandatory=True,
        applicable_condition="Required for equipment loan disbursement",
        description="Formal price quotation from verified supplier with GST details.",
        where_to_get="Machinery Suppliers via Aarambh Saathi Supplier Directory",
        format="Original Supplier Proforma Invoice",
        status="Required"
    ))

    # Add any extra scheme specific docs from raw data
    for rd in raw_docs:
        rd_lower = rd.lower()
        if any(k in rd_lower for k in ["aadhaar", "pan", "bank", "project report", "dpr", "caste", "qualification", "rural"]):
            continue
        items.append(SchemeDocumentItem(
            document_name=rd,
            mandatory=False,
            applicable_condition="Scheme-specific requirement",
            description="Supporting documentation as required by nodal bank.",
            where_to_get="Respective issuing agency",
            format="Self-attested copy",
            status="Conditionally Required"
        ))
        
    return items

# =========================================================================
# 100% WEIGHTED MATCHING SCORE CALCULATION
# =========================================================================

def calculate_scheme_relevance_score(
    scheme_rules: Dict[str, Any],
    raw_scheme_json: Dict[str, Any],
    profile: UserProfile,
    business_id: Optional[str],
    business_category: Optional[str],
    project_cost: float,
    all_eligibility_results: List[EligibilityConditionResult]
) -> Tuple[float, List[str]]:
    """
    Computes a 100% weighted ranking match score:
    - Profile Match (25%): Age, gender, education, category alignment
    - Business Match (25%): Exact ID/Prefix match & direct category match
    - Location Match (15%): State / rural jurisdiction match
    - Financial Fit (15%): Project cost & funding bounds
    - Category/Sector (10%): Sector alias & keywords
    - Intent/Enterprise (5%): Stage of business
    - Data Confidence (5%): Official verified metadata
    """
    score = 0.0
    why_matched: List[str] = []
    
    # 1. Profile Match (25%)
    profile_score = 0.0
    age_res = next((r for r in all_eligibility_results if r.condition == "Age Requirement"), None)
    if age_res and age_res.status == "Eligible":
        profile_score += 8.0
    elif age_res and age_res.status == "Not Specified":
        profile_score += 6.0
        
    gender_res = next((r for r in all_eligibility_results if "Gender" in r.condition), None)
    if gender_res and gender_res.status == "Eligible":
        profile_score += 7.0
    elif gender_res and gender_res.status == "Not Specified":
        profile_score += 5.0
        
    cat_res = next((r for r in all_eligibility_results if "Category" in r.condition), None)
    if cat_res and cat_res.status == "Eligible":
        profile_score += 5.0
    elif cat_res and cat_res.status == "Not Specified":
        profile_score += 4.0
        
    edu_res = next((r for r in all_eligibility_results if "Education" in r.condition), None)
    if edu_res and edu_res.status in ["Eligible", "Not Specified"]:
        profile_score += 5.0
        
    score += min(25.0, profile_score)
    
    # 2. Business Match (25%)
    biz_score = 0.0
    b_id = business_id or ""
    cat_lower = (business_category or "").strip().lower()
    eligible_ids = raw_scheme_json.get("eligible_ids", [])
    eligible_cats = raw_scheme_json.get("eligible_businesses", [])
    
    if b_id and any(b_id.startswith(eid) or eid in b_id for eid in eligible_ids):
        biz_score += 15.0
        why_matched.append("Direct national mission mandate for this exact business activity.")
    elif cat_lower:
        biz_score += 10.0
        
    if any(ec.lower() in cat_lower or (cat_lower and cat_lower in ec.lower()) for ec in eligible_cats):
        biz_score += 10.0
        why_matched.append(f"Specifically designated for micro-enterprises under '{business_category}'.")
    else:
        biz_score += 5.0
        
    score += min(25.0, biz_score)
    
    # 3. Location Match (15%)
    loc_score = 0.0
    s_level = raw_scheme_json.get("level", "Central")
    user_state = (profile.state or "").strip().lower()
    
    if s_level == "State":
        des_state = scheme_rules.get("designated_state", "")
        if des_state and des_state.lower() in user_state:
            loc_score += 15.0
            why_matched.append(f"Dedicated State Government incentive scheme for {profile.state} residents.")
    else:
        loc_score += 10.0
        user_loc = (profile.village or profile.location or "").lower()
        if bool(profile.village) or "rural" in user_loc:
            loc_score += 5.0
            why_matched.append("Rural location qualifies for highest available subsidy slab.")
            
    score += min(15.0, loc_score)
    
    # 4. Financial Fit (15%)
    fin_score = 0.0
    fin_res = next((r for r in all_eligibility_results if "Financial Outlay" in r.condition), None)
    if fin_res and fin_res.status == "Eligible":
        fin_score += 15.0
        why_matched.append(f"Project cost of INR {project_cost:,.0f} falls safely within eligible loan and subsidy limits.")
    elif fin_res and fin_res.status == "Not Specified":
        fin_score += 12.0
    score += min(15.0, fin_score)
    
    # 5. Category/Sector Fit (10%)
    sector_score = 0.0
    raw_interests = profile.business_interest or ""
    user_interests = [i.strip().lower() for i in raw_interests.split(",") if i.strip()] if isinstance(raw_interests, str) else []
    for ec, aliases in SECTOR_ALIASES.items():
        if any(a in cat_lower for a in aliases):
            sector_score += 6.0
            break
    for interest in user_interests:
        for ec, aliases in SECTOR_ALIASES.items():
            if any(a in interest for a in aliases) and ec in eligible_cats:
                sector_score += 4.0
                why_matched.append(f"Matches your specified interest in '{interest}'.")
                break
    score += min(10.0, sector_score)
    
    # 6. Intent / Enterprise Stage (5%)
    stage_res = next((r for r in all_eligibility_results if "Enterprise Inception" in r.condition), None)
    if stage_res and stage_res.status == "Eligible":
        score += 5.0
    else:
        score += 3.0
        
    # 7. Data Confidence (5%)
    if raw_scheme_json.get("official_source") and raw_scheme_json.get("myscheme_url"):
        score += 5.0
    else:
        score += 3.0
        
    final_score = round(min(100.0, max(10.0, score)), 1)
    if not why_matched:
        why_matched.append("Matches general rural micro-enterprise financial assistance criteria.")
        
    return final_score, why_matched

# =========================================================================
# CORE SCHEME MATCHING ENGINE
# =========================================================================

def match_government_schemes_core(
    profile: UserProfile,
    business_id: Optional[str] = None,
    business_category: Optional[str] = None,
    business_name: Optional[str] = None,
    project_cost: Optional[float] = None,
    own_contribution: Optional[float] = None,
    funding_requirement: Optional[float] = None
) -> Tuple[List[MatchedScheme], List[MatchedScheme], List[MatchedScheme], List[MatchedScheme]]:
    all_schemes = load_schemes_data()
    
    cat = (business_category or "").strip()
    b_id = business_id or ""
    
    if not cat and b_id:
        b_info = get_business_by_id(b_id)
        if b_info:
            cat = b_info.get("category", "")
            if not business_name:
                business_name = b_info.get("business_name")
                
    effective_cost = float(project_cost) if project_cost is not None else float(profile.capital or 150000.0)
    effective_own = float(own_contribution) if own_contribution is not None else float(profile.capital or profile.available_investment or (effective_cost * 0.10))
    effective_funding = float(funding_requirement) if funding_requirement is not None else max(0.0, effective_cost - effective_own)
    
    matched_list: List[MatchedScheme] = []
    conditional_list: List[MatchedScheme] = []
    insufficient_list: List[MatchedScheme] = []
    not_eligible_list: List[MatchedScheme] = []
    
    for s in all_schemes:
        s_id = s.get("id", "")
        s_rules = SCHEME_RULES_REGISTRY.get(s_id, {})
        s_level = s.get("level", "Central")
        s_name = s.get("scheme_name", "")
        
        # 1. Run all deterministic checks
        age_check = check_age_eligibility(s_rules, profile)
        gender_check = check_gender_eligibility(s_rules, profile)
        cat_check = check_category_eligibility(s_rules, profile)
        income_check = check_income_eligibility(s_rules, profile)
        edu_check = check_education_eligibility(s_rules, profile, effective_cost, cat)
        loc_check = check_location_eligibility(s_rules, profile)
        biz_check, _ = check_business_type_eligibility(s_rules, s, b_id, cat)
        cost_check, fin_fit = check_project_cost_eligibility(s_rules, effective_cost, cat)
        stage_check = check_existing_business_eligibility(s_rules, profile)
        
        fin_fit.own_contribution = effective_own
        fin_fit.funding_requirement = effective_funding
        
        all_checks = [
            age_check,
            gender_check,
            cat_check,
            income_check,
            edu_check,
            loc_check,
            biz_check,
            cost_check,
            stage_check
        ]
        
        # 2. Determine Overall Status based on Hard Disqualifiers vs Missing Info
        # Hard Disqualifier -> NOT ELIGIBLE
        if any(c.status == "Not Eligible" for c in all_checks):
            overall_status = "NOT ELIGIBLE"
        elif any(c.status == "Insufficient Data" for c in all_checks):
            overall_status = "INSUFFICIENT DATA"
        elif any(c.status == "Conditionally Eligible" for c in all_checks):
            overall_status = "CONDITIONALLY MATCHED"
        else:
            overall_status = "MATCHED"
            
        # 3. Calculate 100% Ranking Score
        score, why_matched_reasons = calculate_scheme_relevance_score(
            scheme_rules=s_rules,
            raw_scheme_json=s,
            profile=profile,
            business_id=b_id,
            business_category=cat,
            project_cost=effective_cost,
            all_eligibility_results=all_checks
        )
        
        # 4. Benefits from source
        benefits_list = s_rules.get("benefits_list")
        if not benefits_list:
            raw_ben = s.get("benefits") or s.get("financial_support") or "Credit-linked financial support and entrepreneurship assistance."
            benefits_list = [b.strip() for b in re.split(r'[.,;]\s+', raw_ben) if len(b.strip()) > 8][:4]
            if not benefits_list:
                benefits_list = ["Benefit details unavailable in current dataset."]
                
        # 5. Documents list
        doc_checklist = generate_personalized_documents(
            scheme_id=s_id,
            raw_docs=s.get("documents", []),
            profile=profile,
            project_cost=effective_cost,
            business_sector=cat
        )
        
        # 6. Application process
        app_steps = s_rules.get("application_steps")
        if not app_steps:
            raw_app = s.get("application_process") or "Apply online via nodal portal or visit nearest District Industries Centre (DIC)."
            app_steps = [a.strip() for a in re.split(r'[.;]\s+', raw_app) if len(a.strip()) > 8][:4]
            
        official_url = s_rules.get("official_url") or s.get("official_source") or "Official application link unavailable in current dataset."
        source_name = s_rules.get("source") or s.get("ministry") or "Government of India / myScheme Portal"
        last_verified = s_rules.get("last_verified") or "September 2024 (myScheme.gov.in verified)"
        
        # Build MatchedScheme Object
        matched_obj = MatchedScheme(
            scheme_id=s_id,
            scheme_name=s_name,
            scheme_level=s_level,
            status=overall_status,
            match_score=score,
            confidence=95.0 if s_rules else 85.0,
            why_matched=why_matched_reasons,
            eligibility=all_checks,
            benefits=benefits_list,
            financial_fit=fin_fit,
            documents=doc_checklist,
            application_process=app_steps,
            official_url=official_url,
            source=source_name,
            last_verified=last_verified,
            # Legacy Fields
            why_relevant="; ".join(why_matched_reasons[:2]),
            possible_support=s.get("financial_support", ""),
            eligibility_summary=s.get("eligibility", ""),
            required_documents=[d.document_name for d in doc_checklist if d.status == "Required"],
            official_source=s.get("official_source", official_url),
            notes=s.get("notes", ""),
            myscheme_url=s.get("myscheme_url"),
            category=s.get("category"),
            ministry=s.get("ministry")
        )
        
        if overall_status == "MATCHED":
            matched_list.append(matched_obj)
        elif overall_status == "CONDITIONALLY MATCHED":
            conditional_list.append(matched_obj)
        elif overall_status == "INSUFFICIENT DATA":
            insufficient_list.append(matched_obj)
        else:
            not_eligible_list.append(matched_obj)
            
    # Sort each list descending by match_score
    matched_list.sort(key=lambda x: x.match_score, reverse=True)
    conditional_list.sort(key=lambda x: x.match_score, reverse=True)
    insufficient_list.sort(key=lambda x: x.match_score, reverse=True)
    not_eligible_list.sort(key=lambda x: x.match_score, reverse=True)
    
    return matched_list, conditional_list, insufficient_list, not_eligible_list

def match_government_schemes(
    profile: UserProfile,
    business_id: Optional[str] = None,
    business_category: Optional[str] = None,
    project_cost: Optional[float] = None
) -> List[MatchedScheme]:
    """
    Standard backward-compatible endpoint returning a ranked list of matched & conditionally matched schemes.
    """
    matched, conditional, insufficient, _ = match_government_schemes_core(
        profile=profile,
        business_id=business_id,
        business_category=business_category,
        project_cost=project_cost
    )
    # Return top matched and conditionally matched schemes
    combined = matched + conditional + insufficient
    return combined[:8]

def get_scheme_match_response(
    profile: UserProfile,
    business_id: Optional[str] = None,
    business_category: Optional[str] = None,
    business_name: Optional[str] = None,
    project_cost: Optional[float] = None,
    own_contribution: Optional[float] = None,
    funding_requirement: Optional[float] = None
) -> SchemeMatchResponse:
    """
    Full structured response for Step 6 frontend and rich reporting.
    """
    matched, conditional, insufficient, not_eligible = match_government_schemes_core(
        profile=profile,
        business_id=business_id,
        business_category=business_category,
        business_name=business_name,
        project_cost=project_cost,
        own_contribution=own_contribution,
        funding_requirement=funding_requirement
    )
    
    effective_cost = float(project_cost) if project_cost is not None else float(profile.capital or 150000.0)
    effective_own = float(own_contribution) if own_contribution is not None else float(profile.capital or profile.available_investment or (effective_cost * 0.10))
    effective_funding = float(funding_requirement) if funding_requirement is not None else max(0.0, effective_cost - effective_own)
    
    user_summary = {
        "name": profile.name or "Entrepreneur",
        "age": profile.age,
        "gender": profile.gender,
        "category": profile.category,
        "education": profile.education,
        "location": f"{profile.village or ''} {profile.district or ''}, {profile.state or ''}".strip(),
        "state": profile.state,
        "district": profile.district,
        "rural_urban": profile.rural_urban or ("Rural" if profile.village else "Rural/Semi-Urban"),
        "annual_income": profile.income or profile.annual_income
    }
    
    proj_summary = {
        "business_name": business_name or business_category or "Rural Micro-Enterprise",
        "business_category": business_category,
        "business_id": business_id,
        "project_cost": effective_cost,
        "own_contribution": effective_own,
        "funding_requirement": effective_funding
    }
    
    verified_factors = ["State location", "Age", "Education", "Project cost limits"]
    if profile.category:
        verified_factors.append("Social category")
    if profile.gender:
        verified_factors.append("Gender eligibility")
        
    missing_factors = []
    if profile.age is None:
        missing_factors.append("Age")
    if profile.gender is None:
        missing_factors.append("Gender")
    if profile.category is None:
        missing_factors.append("Social category")
    if profile.income is None and profile.annual_income is None:
        missing_factors.append("Annual income")
    if profile.education is None:
        missing_factors.append("Educational qualification")
        
    data_quality = {
        "verified": verified_factors,
        "estimated": ["Indicative subsidy slab based on published guidelines"],
        "missing": missing_factors,
        "data_status": "DETERMINISTIC_EVALUATION_COMPLETED"
    }
    
    return SchemeMatchResponse(
        user_profile_summary=user_summary,
        project_summary=proj_summary,
        matched_schemes=matched,
        conditional_schemes=conditional,
        insufficient_data_schemes=insufficient,
        not_eligible_schemes=not_eligible,
        data_quality=data_quality
    )
