from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class UserProfile(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None  # Village/City
    district: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str] = None
    capital: Optional[float] = None
    resources: List[str] = Field(default_factory=list)
    business_interest: Optional[str] = None
    goal: Optional[str] = None
    scale: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    language: str = "en"  # "en", "hi", "mr"

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

class RecommendationScoreBreakdown(BaseModel):
    skill_match_score: float = Field(..., description="Weight 25%")
    capital_match_score: float = Field(..., description="Weight 25%")
    resource_match_score: float = Field(..., description="Weight 20%")
    market_potential_score: float = Field(..., description="Weight 20%")
    risk_score: float = Field(..., description="Weight 10%")
    total_score: float = Field(..., description="Calculated out of 100")

class BusinessRecommendation(BaseModel):
    business_id: str
    business_name: str
    category: str
    overall_score: float
    breakdown: RecommendationScoreBreakdown
    required_investment: float
    user_capital: float
    why_matches: List[str] = Field(default_factory=list)
    main_opportunity: str
    main_risk: str
    description: str
    scalability: str

class RecommendationResponse(BaseModel):
    recommendations: List[BusinessRecommendation]
    profile_summary: Dict[str, Any]
    calculation_method: str = "Deterministic 5-Factor Weighted Engine (Skill 25%, Capital 25%, Resource 20%, Market 20%, Risk 10%)"

class FeasibilityRequest(BaseModel):
    business_id: str
    profile: UserProfile

class FeasibilityResponse(BaseModel):
    business_id: str
    business_name: str
    feasibility_score: float
    market_opportunity: str
    competition_level: str
    resource_availability: str
    risk_level: str
    positive_factors: List[str]
    caution_factors: List[str]
    is_demo_data: bool = True
    disclaimer: str = "Calculated using hyper-local heuristic baseline for demonstration; connect live APMC/DIC feeds for audited statistics."

class FinancialInput(BaseModel):
    project_cost: float
    user_contribution: Optional[float] = None
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

class MatchedScheme(BaseModel):
    scheme_id: str
    scheme_name: str
    why_relevant: str
    possible_support: str
    eligibility_summary: str
    required_documents: List[str]
    official_source: str
    notes: str
    myscheme_url: Optional[str] = None
    category: Optional[str] = None
    ministry: Optional[str] = None

class SchemeMatchRequest(BaseModel):
    profile: UserProfile
    business_category: Optional[str] = None
    business_id: Optional[str] = None
    project_cost: Optional[float] = None

class ReportRequest(BaseModel):
    profile: UserProfile
    selected_business_id: Optional[str] = None
    custom_project_cost: Optional[float] = None

class BusinessReport(BaseModel):
    report_id: str
    created_at: str
    entrepreneur_profile: UserProfile
    recommended_business: BusinessRecommendation
    local_feasibility: FeasibilityResponse
    financial_plan: FinancialPlan
    relevant_schemes: List[MatchedScheme]
    explainable_reasons: List[str]
    action_plan_90_days: Dict[str, List[str]]
    disclaimer: str
