from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import shutil
import json

from backend.config import PORT, HOST, DATA_DIR, BUSINESSES_FILE
from backend.models import (
    UserProfile,
    ChatRequest,
    ChatResponse,
    RecommendationResponse,
    FeasibilityRequest,
    FeasibilityResponse,
    FinancialInput,
    FinancialPlan,
    SchemeMatchRequest,
    MatchedScheme,
    ReportRequest,
    BusinessReport
)
from backend.database import init_db, load_businesses_data, load_schemes_data
from backend.chatbot import process_chat
from backend.recommendation import get_recommendations
from backend.feasibility import evaluate_hyper_local_feasibility
from backend.finance import calculate_financial_plan
from backend.schemes import match_government_schemes
from backend.report import generate_business_report
from backend.importer import import_business_catalogue

app = FastAPI(
    title="GramVantage AI API",
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs",
    version="1.2.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {
        "app": "GramVantage AI",
        "tagline": "AI-Driven Hyper-Local Business Advisory & Financial Structuring for Rural Micro-Entrepreneurs",
        "edition": "Enterprise Production",
        "status": "Online",
        "docs": "/docs"
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "GramVantage AI"}


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest):
    try:
        response = process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.post("/api/profile")
def api_update_profile(profile: UserProfile):
    return {
        "status": "success",
        "profile": profile
    }

@app.post("/api/recommend", response_model=RecommendationResponse)
def api_recommend(profile: UserProfile):
    try:
        return get_recommendations(profile, top_n=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation scoring error: {str(e)}")

@app.post("/api/feasibility", response_model=FeasibilityResponse)
def api_feasibility(request: FeasibilityRequest):
    try:
        return evaluate_hyper_local_feasibility(request.business_id, request.profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feasibility calculation error: {str(e)}")

@app.post("/api/financial", response_model=FinancialPlan)
def api_financial(inputs: FinancialInput):
    try:
        return calculate_financial_plan(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial calculation error: {str(e)}")

@app.get("/api/businesses")
def api_list_businesses(domain: Optional[str] = None, search: Optional[str] = None):
    all_b = load_businesses_data()
    if domain and domain != "All":
        all_b = [b for b in all_b if b.get("category", "").lower() == domain.lower()]
    if search:
        s_lower = search.lower()
        all_b = [
            b for b in all_b
            if s_lower in b.get("business_name", "").lower()
            or s_lower in b.get("category", "").lower()
            or any(s_lower in sk.lower() for sk in b.get("required_skills", []))
        ]
    return all_b

@app.get("/api/schemes")
def api_list_schemes():
    return load_schemes_data()

@app.get("/api/schemes/stats")
def api_schemes_stats():
    """
    Returns scheme database statistics including total schemes, categories, and sync metadata.
    """
    meta_file = DATA_DIR / "schemes_meta.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    schemes = load_schemes_data()
    return {
        "total_schemes": len(schemes),
        "source": "Curated database cross-referenced with myscheme.gov.in",
        "last_synced": None
    }

@app.post("/api/schemes/sync")
def api_sync_schemes():
    """
    Triggers a sync of the government schemes master catalogue cross-referenced with myscheme.gov.in.
    """
    try:
        from backend.scheme_scraper import sync_schemes_from_myscheme
        meta = sync_schemes_from_myscheme()
        return {
            "status": "success",
            "message": f"Successfully synced {meta['total_schemes']} verified government schemes cross-referenced with myscheme.gov.in.",
            "meta": meta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheme sync error: {str(e)}")

@app.post("/api/schemes/match", response_model=List[MatchedScheme])
def api_match_schemes(request: SchemeMatchRequest):
    try:
        return match_government_schemes(
            profile=request.profile,
            business_id=request.business_id,
            business_category=request.business_category,
            project_cost=request.project_cost
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheme matching error: {str(e)}")

# =========================================================================
# BUSINESS SETUP & MACHINERY SUPPLIER ENDPOINTS
# =========================================================================

class SupplierSearchRequest(BaseModel):
    machine_id: str
    location: Optional[str] = None
    budget: Optional[float] = None
    capacity: Optional[str] = None

class SupplierRecommendRequest(BaseModel):
    business_name: str
    business_scale: Optional[str] = "small"
    location: Optional[str] = None
    budget: Optional[float] = None

@app.get("/api/equipment/{business_name}")
def api_get_equipment(business_name: str, scale: Optional[str] = "small"):
    """
    Returns required equipment and machines to start the specified business.
    """
    from backend.supplier import get_required_machines
    try:
        return get_required_machines(business_name=business_name, business_scale=scale or "small")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Equipment retrieval error: {str(e)}")

@app.post("/api/suppliers/search")
def api_search_suppliers(request: SupplierSearchRequest):
    """
    Filters and deterministically ranks suppliers for a specific machine.
    """
    from backend.supplier import search_suppliers
    try:
        return search_suppliers(
            machine_id=request.machine_id,
            location=request.location,
            budget=request.budget,
            capacity=request.capacity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supplier search error: {str(e)}")

@app.post("/api/suppliers/recommend")
def api_recommend_suppliers(request: SupplierRecommendRequest):
    """
    Full pipeline: returns required machinery and matched/ranked supplier shortlists.
    """
    from backend.supplier import get_supplier_recommendations
    try:
        return get_supplier_recommendations(
            business_name=request.business_name,
            business_scale=request.business_scale or "small",
            location=request.location,
            budget=request.budget
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supplier recommendation error: {str(e)}")

@app.post("/api/report", response_model=BusinessReport)
def api_generate_report(request: ReportRequest):
    try:
        return generate_business_report(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

# =========================================================================
# MODEL TRAINING & CATALOGUE INGESTION ENDPOINTS
# =========================================================================

class ImportPathRequest(BaseModel):
    file_path: Optional[str] = None

@app.get("/api/train/status")
def api_train_status():
    meta_file = DATA_DIR / "catalogue_meta.json"
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    businesses = load_businesses_data()
    return {
        "total_businesses": len(businesses),
        "status": "Initialized with baseline dataset"
    }

@app.post("/api/train")
def api_train_model(request: Optional[ImportPathRequest] = None):
    """
    Ingests and trains the decision models on the catalogue.
    """
    default_excel = r"C:\Users\vighn\Downloads\GramVantage_Business_Catalogue.xlsx"
    target_path = request.file_path if (request and request.file_path) else default_excel

    if os.path.exists(target_path):
        try:
            result = import_business_catalogue(target_path)
            return {
                "status": "success",
                "message": f"Successfully trained model and ingested {result['total_businesses']} businesses across {result['domains_count']} domains into knowledge base.",
                "meta": result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Training / Ingestion error: {str(e)}")

    # Check in data dir fallback
    fallback = DATA_DIR / "GramVantage_Business_Catalogue.xlsx"
    if fallback.exists():
        try:
            result = import_business_catalogue(str(fallback))
            return {
                "status": "success",
                "message": f"Successfully trained model and ingested {result['total_businesses']} businesses across {result['domains_count']} domains into knowledge base.",
                "meta": result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Training / Ingestion error: {str(e)}")

    # Fallback from existing businesses.json
    businesses = load_businesses_data()
    domains_summary = {}
    for b in businesses:
        cat = b.get("category", "General")
        domains_summary[cat] = domains_summary.get(cat, 0) + 1

    meta = {
        "source_file": "businesses.json",
        "total_businesses": len(businesses),
        "domains_count": len(domains_summary),
        "domains_breakdown": domains_summary,
        "min_investment_overall": min((b.get("minimum_investment", 50000) for b in businesses), default=50000),
        "max_investment_overall": max((b.get("minimum_investment", 500000) for b in businesses), default=500000),
        "status": "Trained & Ingested into Knowledge Base"
    }
    meta_file = DATA_DIR / "catalogue_meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "message": f"Successfully validated and retrained model on {len(businesses)} businesses across {len(domains_summary)} domains.",
        "meta": meta
    }

@app.post("/api/businesses/import")
async def api_upload_and_train(file: UploadFile = File(...)):
    """
    Upload an Excel (.xlsx) or CSV file directly from the browser to train the model.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = DATA_DIR / file.filename

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = import_business_catalogue(str(saved_path))
        return {
            "status": "success",
            "message": f"Successfully uploaded and trained on {result['total_businesses']} business ideas from {file.filename}.",
            "meta": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse and train on uploaded file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
