from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class UserProfile(BaseModel):
    name: Optional[str] = None
    intent: Optional[str] = None       # "Start a new business", "Expand an existing business", "I don't know what business to start"
    age: Optional[int] = None
    gender: Optional[str] = None       # "Male", "Female", "Other"
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    location: Optional[str] = None      # Village/City (backward compatible)
    education: Optional[str] = None
    occupation: Optional[str] = None    # Current occupation (backward compatible)
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str] = None
    resources: List[str] = Field(default_factory=list)
    available_investment: Optional[float] = None
    capital: Optional[float] = None     # Investment amount (backward compatible)
    business_interest: Optional[str] = None
    existing_business: Optional[str] = None
    goal: Optional[str] = None
    scale: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    category: Optional[str] = None     # Social Category (General/OBC/SC/ST)
    income: Optional[float] = None       # Annual family income in INR
    annual_income: Optional[float] = None
    rural_urban: Optional[str] = None    # "Rural" | "Urban" | "Semi-Urban"
    language: str = "en"               # "en", "hi", "mr"

    def model_post_init(self, __context: Any) -> None:
        # Keep capital and available_investment strictly synced
        if self.available_investment is not None and self.capital is None:
            self.capital = float(self.available_investment)
        elif self.capital is not None and self.available_investment is None:
            self.available_investment = float(self.capital)

        # Keep location, village, and district synced
        if not self.location:
            parts = [p for p in [self.village, self.district] if p]
            if parts:
                self.location = ", ".join(parts)
        elif not self.village and not self.district:
            self.district = self.location


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    profile: Optional[UserProfile] = None
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    session_id: str
    current_step: str
    reply: str
    updated_profile: UserProfile
    is_profile_ready: bool = False
    missing_fields: List[str] = Field(default_factory=list)
    suggested_quick_replies: List[str] = Field(default_factory=list)
    language: str = "en"

class FactorScoreDetail(BaseModel):
    score: float
    reason: str
    data_source: str = "Curated Knowledge Base Indicators"
    confidence: float = 85.0

class RecommendationFactorScores(BaseModel):
    skill_match: float = Field(..., description="Weight 20%")
    location_suitability: float = Field(..., description="Weight 20%")
    resource_match: float = Field(..., description="Weight 15%")
    investment_fit: float = Field(..., description="Weight 15%")
    local_demand: float = Field(..., description="Weight 10%")
    competition: float = Field(..., description="Weight 5%")
    customer_potential: float = Field(..., description="Weight 5%")
    supplier_availability: float = Field(..., description="Weight 5%")
    market_access: float = Field(..., description="Weight 5%")

class RecommendationScoreBreakdown(BaseModel):
    skill_match_score: float = Field(..., description="Weight 20%")
    location_suitability_score: float = Field(default=80.0, description="Weight 20%")
    resource_match_score: float = Field(..., description="Weight 15%")
    capital_match_score: float = Field(..., description="Weight 15%")
    local_demand_score: float = Field(default=80.0, description="Weight 10%")
    competition_score: float = Field(default=75.0, description="Weight 5%")
    customer_potential_score: float = Field(default=80.0, description="Weight 5%")
    supplier_availability_score: float = Field(default=85.0, description="Weight 5%")
    market_access_score: float = Field(default=80.0, description="Weight 5%")
    market_potential_score: Optional[float] = None
    risk_score: Optional[float] = None
    total_score: float = Field(..., description="Calculated out of 100")

class BusinessRecommendation(BaseModel):
    business_id: str
    business_name: str
    category: str
    overall_score: float
    match_level: str = "Strong Match"
    breakdown: RecommendationScoreBreakdown
    factor_scores: Optional[RecommendationFactorScores] = None
    factor_details: Optional[Dict[str, FactorScoreDetail]] = None
    required_investment: float
    user_capital: float
    why_matches: List[str] = Field(default_factory=list)
    why_this_matches: List[str] = Field(default_factory=list)
    considerations: List[str] = Field(default_factory=list)
    main_opportunity: str
    main_risk: str
    description: str
    scalability: str
    estimated_monthly_revenue: Optional[float] = None
    estimated_monthly_profit: Optional[float] = None
    data_sources: List[str] = Field(default_factory=list)
    confidence: float = 85.0

class RecommendationResponse(BaseModel):
    recommendations: List[BusinessRecommendation]
    profile_summary: Dict[str, Any]
    calculation_method: str = "Deterministic 9-Factor Weighted Engine (Skill 20%, Location 20%, Resource 15%, Investment 15%, Demand 10%, Competition 5%, Customer 5%, Supplier 5%, Market 5%)"

class FeasibilityFactorDetail(BaseModel):
    score: float
    confidence: float
    source: str
    reason: str

class FeasibilityFactorScores(BaseModel):
    location: FeasibilityFactorDetail
    infrastructure: FeasibilityFactorDetail
    market_access: FeasibilityFactorDetail
    local_demand: FeasibilityFactorDetail
    competition: FeasibilityFactorDetail
    supplier_availability: FeasibilityFactorDetail
    raw_material_access: FeasibilityFactorDetail
    transport: FeasibilityFactorDetail

class CompetitorSignal(BaseModel):
    business_name: str
    category: str
    distance_km: float
    rating: float = 4.0
    source: str = "Google Places / Knowledge Base"
    relevance: str = "Sector competitor"
    is_live_api: bool = False

class MarketSignal(BaseModel):
    market_name: str
    market_type: str
    distance_km: float
    relevance: str
    operating_days: str = "Regular"
    source: str = "APMC / Rural Haat Registry"
    is_live_api: bool = False

class DataQualityReport(BaseModel):
    verified_factors: List[str] = Field(default_factory=list)
    estimated_factors: List[str] = Field(default_factory=list)
    missing_data: List[str] = Field(default_factory=list)

class FeasibilityRequest(BaseModel):
    business_id: str
    business_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    profile: Optional[UserProfile] = None
    user_profile: Optional[UserProfile] = None

class FeasibilityResponse(BaseModel):
    business_id: str
    business_name: str
    overall_score: float
    feasibility_score: float  # Legacy compatibility alias
    feasibility_level: str = "Feasible"  # Highly Feasible, Feasible, Moderately Feasible, Needs Validation, Low Feasibility
    factors: FeasibilityFactorScores
    nearby_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    nearby_markets: List[Dict[str, Any]] = Field(default_factory=list)
    suppliers: List[Dict[str, Any]] = Field(default_factory=list)
    infrastructure_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    data_quality: DataQualityReport = Field(default_factory=DataQualityReport)
    
    # Legacy fields for backward compatibility
    market_opportunity: str
    competition_level: str
    resource_availability: str
    risk_level: str
    positive_factors: List[str] = Field(default_factory=list)
    caution_factors: List[str] = Field(default_factory=list)
    is_demo_data: bool = False
    disclaimer: str = "Calculated using hyper-local deterministic indicators and verified supplier directory."

class FinancialInput(BaseModel):
    project_cost: Optional[float] = None
    user_contribution: Optional[float] = None
    business_id: Optional[str] = None
    business_name: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    profile: Optional[UserProfile] = None
    setup_plan: Optional[Dict[str, Any]] = None
    feasibility_result: Optional[Dict[str, Any]] = None
    setup_mode: Optional[str] = "starter"  # "starter" | "standard" | "custom"
    custom_interest_rate: Optional[float] = None
    custom_tenure_years: Optional[int] = None
    custom_moratorium_months: Optional[int] = None
    estimated_monthly_revenue: Optional[float] = None
    estimated_monthly_operating_expenses: Optional[float] = None

class FinancialPlan(BaseModel):
    project_cost: float
    scheme_tier: str
    tier_description: str
    own_contribution: float
    own_contribution_percentage: float
    required_loan: float
    loan_percentage: float
    interest_rate: float
    tenure_years: int
    tenure_months: int
    moratorium_months: int
    monthly_emi: float
    total_repayment: float
    total_interest_payable: float
    monthly_revenue: float
    monthly_operating_expenses: float
    monthly_profit: float
    annual_profit: float
    break_even_months: float
    disclaimer: str = "Preliminary eligibility estimate under micro-enterprise credit guidelines. Final credit sanction subject to bank & channelizing agency verification."

    # Extended Step 5 structured attributes
    business_name: Optional[str] = None
    cost_breakdown: Optional[Dict[str, float]] = None
    funding_requirement: float = 0.0
    monthly_financials: Optional[Dict[str, Any]] = None
    break_even: Optional[Dict[str, Any]] = None
    financing: Optional[Dict[str, Any]] = None
    repayment_capacity: Optional[Dict[str, Any]] = None
    financial_health: str = "HEALTHY"  # "HEALTHY" | "CAUTION" | "HIGH RISK" | "INSUFFICIENT DATA"
    scenarios: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    low_capital_path: Optional[Dict[str, Any]] = None
    data_quality: Optional[Dict[str, Any]] = None

class EligibilityConditionResult(BaseModel):
    condition: str
    status: str  # "Eligible", "Not Eligible", "Conditionally Eligible", "Not Specified", "Insufficient Data"
    reason: str
    source: str = "Official Scheme Guidelines"

class SchemeDocumentItem(BaseModel):
    document_name: str
    mandatory: bool = True
    applicable_condition: Optional[str] = None
    description: Optional[str] = None
    where_to_get: Optional[str] = None
    format: Optional[str] = "Original / Self-attested copy"
    validity: Optional[str] = None
    status: str = "Required"  # "Required", "Conditionally Required", "Not Required"

class FinancialFitDetail(BaseModel):
    status: str = "Appears financially compatible"  # "Appears financially compatible", "Exceeds Scheme Limit", "Below Scheme Minimum", "Financially Incompatible", "Not Specified"
    project_cost: float = 0.0
    max_limit: Optional[float] = None
    min_limit: Optional[float] = None
    own_contribution: Optional[float] = None
    funding_requirement: Optional[float] = None
    indicative_subsidy: Optional[str] = None
    notes: Optional[str] = None

class MatchedScheme(BaseModel):
    scheme_id: str
    scheme_name: str
    scheme_level: str = "Central"  # "Central", "State", "District"
    status: str = "MATCHED"        # "MATCHED", "CONDITIONALLY MATCHED", "INSUFFICIENT DATA", "NOT ELIGIBLE"
    match_score: float = 85.0
    confidence: float = 90.0

    why_matched: List[str] = Field(default_factory=list)
    eligibility: List[EligibilityConditionResult] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    financial_fit: Optional[FinancialFitDetail] = None
    documents: List[SchemeDocumentItem] = Field(default_factory=list)
    application_process: List[str] = Field(default_factory=list)

    official_url: str = ""
    source: str = "myScheme / Official Ministry Portal"
    last_verified: str = "September 2024 (Verified via myScheme.gov.in)"

    # Legacy backward compatibility fields
    why_relevant: str = ""
    possible_support: str = ""
    eligibility_summary: str = ""
    required_documents: List[str] = Field(default_factory=list)
    official_source: str = ""
    notes: str = ""
    myscheme_url: Optional[str] = None
    category: Optional[str] = None
    ministry: Optional[str] = None

class SchemeMatchRequest(BaseModel):
    profile: Optional[UserProfile] = None
    user_profile: Optional[UserProfile] = None
    business_category: Optional[str] = None
    business_id: Optional[str] = None
    business_name: Optional[str] = None
    project_cost: Optional[float] = None
    own_contribution: Optional[float] = None
    funding_requirement: Optional[float] = None

    def get_effective_profile(self) -> UserProfile:
        return self.profile or self.user_profile or UserProfile()

class SchemeMatchResponse(BaseModel):
    user_profile_summary: Dict[str, Any] = Field(default_factory=dict)
    project_summary: Dict[str, Any] = Field(default_factory=dict)
    matched_schemes: List[MatchedScheme] = Field(default_factory=list)
    conditional_schemes: List[MatchedScheme] = Field(default_factory=list)
    insufficient_data_schemes: List[MatchedScheme] = Field(default_factory=list)
    not_eligible_schemes: List[MatchedScheme] = Field(default_factory=list)
    data_quality: Dict[str, Any] = Field(default_factory=dict)

class ReportRequest(BaseModel):
    profile: Optional[UserProfile] = None
    user_profile: Optional[UserProfile] = None
    selected_business_id: Optional[str] = None
    business_id: Optional[str] = None
    custom_project_cost: Optional[float] = None
    project_cost: Optional[float] = None
    setup_mode: Optional[str] = "starter"  # "starter" | "standard"
    recommendation: Optional[Any] = None
    feasibility: Optional[Any] = None
    business_setup: Optional[Any] = None
    financial_plan: Optional[Any] = None
    scheme_matches: Optional[Any] = None
    language: Optional[str] = "en"


    def get_effective_profile(self) -> UserProfile:
        return self.profile or self.user_profile or UserProfile()

    def get_effective_business_id(self) -> Optional[str]:
        return self.selected_business_id or self.business_id

    def get_effective_cost(self) -> Optional[float]:
        return self.custom_project_cost if self.custom_project_cost is not None else self.project_cost

class BusinessReport(BaseModel):
    report_id: str
    created_at: str
    generated_at: Optional[str] = None
    language: str = "en"

    # 1. Executive Summary
    executive_summary: str = ""

    # 2. Entrepreneur Profile
    entrepreneur_profile: UserProfile
    entrepreneur: Optional[Dict[str, Any]] = None

    # 3. Proposed Business
    recommended_business: BusinessRecommendation
    business: Optional[Dict[str, Any]] = None

    # 4. Recommendation Fit & Explainability
    recommendation_breakdown: Optional[Dict[str, Any]] = None
    explainable_reasons: List[str] = Field(default_factory=list)

    # 5. Hyper-Local Feasibility
    local_feasibility: FeasibilityResponse
    feasibility: Optional[Dict[str, Any]] = None

    # 6. Business Setup Configuration
    business_setup: Optional[Dict[str, Any]] = None
    setup: Optional[Dict[str, Any]] = None

    # 7. Machinery & Equipment
    machinery: List[Dict[str, Any]] = Field(default_factory=list)

    # 8. Suppliers
    suppliers: List[Dict[str, Any]] = Field(default_factory=list)

    # 9. Project Cost
    project_cost_breakdown: Optional[Dict[str, Any]] = None

    # 10. Means of Finance
    means_of_finance: Optional[Dict[str, Any]] = None

    # 11. Financial Projections
    financial_plan: FinancialPlan
    financial_projections: Optional[Dict[str, Any]] = None

    # 12. Government Schemes
    relevant_schemes: List[MatchedScheme] = Field(default_factory=list)
    schemes: Optional[List[Dict[str, Any]]] = None

    # 13. Consolidated Document Checklist
    documents: List[Dict[str, Any]] = Field(default_factory=list)

    # 14. Implementation Roadmap
    action_plan_90_days: Dict[str, List[str]] = Field(default_factory=dict)
    roadmap: Optional[List[Dict[str, Any]]] = None

    # 15. Risks & Mitigation
    risks: List[Dict[str, Any]] = Field(default_factory=list)

    # 16. Data Transparency & Assumptions
    data_sources: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)

    # 17. Disclaimer
    disclaimer: str = "This report is an AI-assisted preliminary business planning document based on the information and data available to Aarambh Saathi. Financial projections, supplier information, scheme eligibility and feasibility indicators may require verification from the relevant authorities, lenders, suppliers and local market sources before making investment decisions."

class BusinessSetupCostBreakdown(BaseModel):
    equipment_cost: float
    infrastructure_cost: float
    working_capital: float
    total_cost: float

class InfrastructureRequirement(BaseModel):
    item: str
    detail: str
    status: str = "Available"  # "Available" or "Gap — Required Before Launch"
    priority: str = "Essential"  # "Essential", "Recommended", "Optional"

class MachineryRequirement(BaseModel):
    machine_id: str
    machine_name: str
    purpose: str
    capacity: str
    power_requirement: Optional[str] = "Single Phase / 220V"
    price_min: float
    price_max: float
    price_range: str
    priority: str = "Essential"
    installation_available: bool = True
    maintenance_requirement: Optional[str] = "Routine monthly lubrication"
    supplier_count: int = 0

class RawMaterialRequirement(BaseModel):
    item: str
    source: str
    estimated_monthly_cost: float
    priority: str = "Essential"

class LabourRequirement(BaseModel):
    role: str
    count: int = 1
    skill_level: str = "Unskilled / Semi-skilled"
    priority: str = "Essential"

class SetupPhase(BaseModel):
    phase_number: int
    phase_name: str
    items: List[str]
    focus: str

class LowCapitalAdvice(BaseModel):
    is_low_capital: bool = False
    advice: str
    deferred_items: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)

class BusinessSetupRequest(BaseModel):
    business_id: str
    business_name: Optional[str] = None
    available_investment: Optional[float] = None
    user_profile: Optional[UserProfile] = None
    profile: Optional[UserProfile] = None
    feasibility_result: Optional[Dict[str, Any]] = None

class BusinessSetupResponse(BaseModel):
    business_id: str
    business_name: str
    recommended_scale: str
    scale_reason: str
    
    starter_setup: BusinessSetupCostBreakdown
    standard_setup: BusinessSetupCostBreakdown
    
    user_investment: float
    funding_gap: float
    funding_gap_standard: float
    
    infrastructure_requirements: List[InfrastructureRequirement] = Field(default_factory=list)
    machinery: List[MachineryRequirement] = Field(default_factory=list)
    raw_materials: List[RawMaterialRequirement] = Field(default_factory=list)
    labour_requirements: List[LabourRequirement] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    suppliers: List[Dict[str, Any]] = Field(default_factory=list)
    setup_phases: List[SetupPhase] = Field(default_factory=list)
    
    essential_items: List[str] = Field(default_factory=list)
    recommended_items: List[str] = Field(default_factory=list)
    optional_items: List[str] = Field(default_factory=list)
    
    low_capital_advice: LowCapitalAdvice
    data_quality: DataQualityReport = Field(default_factory=DataQualityReport)
    disclaimer: str = "Business setup plan estimates equipment, infrastructure, and working capital deterministically from regional MSME standards. Prices are indicative and must be confirmed with suppliers."

