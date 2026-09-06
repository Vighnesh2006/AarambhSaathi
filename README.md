# GramVantage AI 🌾

> **AI-Driven Hyper-Local Business Advisory and Financial Structuring Platform for Rural Micro-Entrepreneurs**  
> *Enterprise Production Edition*

GramVantage AI is a hybrid AI decision-support and financial advisory platform engineered specifically for rural micro-entrepreneurs across India. It combines conversational intelligence (multilingual in English, Hindi, and Marathi) with deterministic recommendation algorithms, hyper-local feasibility models, and standard institutional micro-enterprise credit structuring rules.

---

## 🚀 Key Highlights & Architecture

1. **Hybrid AI Decision Support:**
   - **LLM Layer (Google Gemini):** Multilingual dialogue (English, हिन्दी, मराठी), progressive profile extraction, and simple explainability without hallucinated statistics or fake loan guarantees.
   - **Deterministic Recommendation Engine:** 100-point algorithm balancing Skill Match (25%), Capital Match (25%), Resource Match (20%), Market Potential (20%), and Risk Profile (10%) to rank Top 3 businesses.
   - **Deterministic Financial Engine:**
     - **Micro Finance Scheme Tier** ($\le$ ₹1.40 Lakh): Up to 90% loan (max ₹1.25 Lakh), **6.5% p.a. interest**, 3-year tenure, **3-month moratorium**.
     - **Commercial Term Loan Tier** (> ₹1.40 Lakh to ₹50 Lakh): Up to 90% loan (max ₹45 Lakh), **8.0% p.a. interest**, 7-year tenure, **6-month moratorium**.
     - Real-time monthly EMI, operating expenses, estimated net profit, and break-even calculations.
   - **Hyper-Local Feasibility Engine:** Evaluates rural cluster demand, local competition, and raw material availability with transparent demo/estimated disclaimers.
   - **Government Schemes Matcher:** Verified schemes (PMEGP, PM Mudra, PMFME, Stand-Up India, AHIDF, PMMSY, NBHM) with eligibility, subsidy structures, and required document checklists.
   - **Business Setup & Machinery Planner:** Catalogs essential equipment, pricing, and ranks nearby vetted suppliers.
   - **90-Day Action Plan & DPR Report Generator:** Comprehensive printable/downloadable business plan divided into Phase 1 (Regulatory), Phase 2 (Procurement/Training), and Phase 3 (Commercial Launch).

---

## 📁 Project Structure

```
Ruraltech/
├── backend/
│   ├── config.py           # Settings & Gemini configuration
│   ├── database.py         # SQLite persistence & data loaders
│   ├── models.py           # Pydantic schemas
│   ├── chatbot.py          # Multilingual progressive chat & entity extraction
│   ├── recommendation.py   # Deterministic 5-factor scoring engine
│   ├── feasibility.py      # Hyper-local demand & risk scoring
│   ├── finance.py          # Micro-enterprise credit calculation engine
│   ├── schemes.py          # Government schemes rule matcher
│   ├── report.py           # 90-day action plan & summary generator
│   ├── main.py             # FastAPI server with all endpoints
│   ├── test_backend.py     # Backend test validation suite
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Backend environment configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # Navigation & language switcher
│   │   │   ├── ChatPanel.jsx           # Conversational assistant & voice input
│   │   │   ├── ProfileCard.jsx         # Live extracted profile & editor
│   │   │   ├── RecommendationCard.jsx  # Top 3 ranking & score breakdown
│   │   │   ├── FeasibilityCard.jsx     # Hyper-local feasibility indicators
│   │   │   ├── FinancialSummary.jsx    # Micro-enterprise credit EMI & profit calculator
│   │   │   ├── SchemesCard.jsx         # Matched government schemes
│   │   │   ├── BusinessSetupCard.jsx   # Equipment requirement & supplier finder
│   │   │   └── ReportModal.jsx         # Printable 90-day DPR report
│   │   ├── services/
│   │   │   └── api.js                  # Frontend API client
│   │   ├── App.jsx                     # Responsive 2-column layout & state sync
│   │   ├── main.jsx                    # React mounting
│   │   └── index.css                   # Custom styles & design tokens
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── data/
│   ├── businesses.json     # Rural micro-business catalogue records
│   ├── schemes.json        # Verified government schemes dataset
│   ├── machines.json       # Machinery catalog
│   └── suppliers.json      # Verified equipment suppliers
├── .env.example
└── README.md
```

---

## 🛠️ Step-by-Step Installation & Run Guide

### Step 1: Clone or Navigate to Project Directory
```bash
cd Ruraltech
```

### Step 2: Configure Environment Variables
Create or verify `.env` in `backend/.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
HOST=0.0.0.0
```

### Step 3: Install Backend Dependencies & Start FastAPI Server
```bash
# Install Python packages
python -m pip install -r backend/requirements.txt

# Start Backend Server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend will be available at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)*

### Step 4: Install Frontend Dependencies & Start Vite Server
Open a second terminal window and run:
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be available at: `http://localhost:5173`*

---

## 🧪 Verification & Testing Flow

You can test the entire flow in the web browser or using the backend test suite:

1. **Run Automated Test Suite:**
   ```bash
   python backend/test_backend.py
   ```
2. **Interactive UI Walkthrough:**
   - Open `http://localhost:5173` in your browser.
   - Select your language (**English**, **हिन्दी**, or **मराठी**).
   - Enter: *"I want to start a dairy business. I have around 1 lakh rupees and I already have some experience with cattle."*
   - Notice GramVantage AI automatically extracts:
     - `business_interest` = *Dairy Farming*
     - `capital` = *₹1,00,000*
     - `experience` = *Cattle*
   - AI progressively asks for your village/district.
   - The right side dashboard instantly updates with:
     - **Top 3 Recommended Businesses** (e.g. Dairy Farming: 94/100, Freshwater Aquaculture: 89.8/100, Poultry: 88.5/100) with detailed 5-factor breakdown.
     - **Hyper-Local Feasibility Card** with local demand & competition indicators.
     - **Micro-Enterprise Financial Plan** applying the Micro Finance Tier (6.5% interest, 3-yr tenure, 3-mo moratorium, EMI calculation, and monthly profit).
     - **Business Setup & Machinery Planner** showing required equipment and regional supplier quotes.
     - **Matched Government Schemes** (PMEGP, PM Mudra, AHIDF, PMFME).
   - Click **"Generate Business Plan"** in the top bar to inspect and print the structured 90-Day Execution Plan & DPR Report.

---

## 🔮 Future Architecture Extensibility
The modular structure is ready to integrate:
- AI phone calling bot (Twilio / Exotel integration via `backend/chatbot.py`)
- Speech-to-text / Text-to-speech voice pipeline
- WhatsApp Business webhook endpoints
- GIS / Google Maps API for live competitor density mapping
- RAG pipeline over state-specific DIC gazettes and guidelines
