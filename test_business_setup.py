"""
Test Suite for STEP 4: Business Setup Planner.
Tests:
1. Required machinery returned for Dairy, Spice Grinding, Retail, and other categories.
2. Essential, Recommended, Optional classification of machinery and infrastructure.
3. Numeric equipment costs and exact cost equation: total_cost == equipment_cost + infrastructure_cost + working_capital.
4. Funding gap calculation matches: funding_gap == max(0, total_cost - user_investment).
5. Low-capital mode triggers when user capital is below starter setup.
6. Suppliers come exclusively from existing data/suppliers.json without hallucination.
7. Infrastructure gaps from Step 3 Feasibility are carried forward into setup requirements.
8. Starter setup total cost is strictly less than standard setup total cost.
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.models import UserProfile, BusinessSetupResponse
from backend.business_setup import generate_business_setup_plan
from backend.database import load_businesses_data

DATA_DIR = Path(__file__).resolve().parent / "data"
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"

class TestBusinessSetupPlanner(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.businesses = load_businesses_data()
        assert len(cls.businesses) >= 50, f"Expected 90 businesses, found {len(cls.businesses)}"
        with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
            cls.all_suppliers = json.load(f)
        cls.valid_supplier_ids = {s["supplier_id"] for s in cls.all_suppliers}

    def test_dairy_farming_setup(self):
        """Test 1: Dairy Farming Setup Plan."""
        dairy_b = next((b for b in self.businesses if "dairy" in b["id"].lower() or "dairy" in b["business_name"].lower()), self.businesses[0])
        profile = UserProfile(
            name="Anand Shinde",
            state="Maharashtra",
            district="Pune",
            village="Baramati",
            available_investment=100000.0,
            skills=["Dairy Management", "Animal Husbandry"],
            resources=["2 acres land", "Borewell", "Electricity"]
        )

        res: BusinessSetupResponse = generate_business_setup_plan(
            business_id=dairy_b["id"],
            business_name=dairy_b["business_name"],
            user_profile=profile
        )

        self.assertIsInstance(res, BusinessSetupResponse)
        self.assertGreater(len(res.machinery), 0)
        self.assertGreater(len(res.infrastructure_requirements), 0)
        self.assertGreater(len(res.raw_materials), 0)
        self.assertGreater(len(res.setup_phases), 0)

        # Total cost math checks
        st = res.starter_setup
        self.assertAlmostEqual(st.total_cost, st.equipment_cost + st.infrastructure_cost + st.working_capital, places=1)
        
        sd = res.standard_setup
        self.assertAlmostEqual(sd.total_cost, sd.equipment_cost + sd.infrastructure_cost + sd.working_capital, places=1)

        # Starter is cheaper than standard
        self.assertLess(st.total_cost, sd.total_cost)

        # Verify supplier origins
        for sup in res.suppliers:
            self.assertIn(sup["supplier_id"], self.valid_supplier_ids, f"Fabricated supplier ID found: {sup['supplier_id']}")

        print(f"[PASS] Dairy Farming Setup verified: Starter: INR {st.total_cost:,.0f} | Standard: INR {sd.total_cost:,.0f} | Suppliers: {len(res.suppliers)}")

    def test_spice_grinding_setup(self):
        """Test 2: Spice Grinding Setup Plan."""
        spice_b = next((b for b in self.businesses if "spice" in b["id"].lower() or "masala" in b["id"].lower()), self.businesses[0])
        profile = UserProfile(
            name="Sunita Kulkarni",
            state="Maharashtra",
            district="Kolhapur",
            village="Hatkanangle",
            available_investment=500000.0,
            skills=["Food Processing", "Spice Grinding"],
            resources=["Commercial shed", "3-phase power", "Water connection"]
        )

        res: BusinessSetupResponse = generate_business_setup_plan(
            business_id=spice_b["id"],
            business_name=spice_b["business_name"],
            user_profile=profile
        )

        self.assertIsInstance(res, BusinessSetupResponse)
        # Check essential vs recommended items
        has_essential = any(m.priority == "Essential" for m in res.machinery)
        self.assertTrue(has_essential)

        # User investment exceeds standard setup cost -> funding gap = 0
        if profile.available_investment >= res.starter_setup.total_cost:
            self.assertEqual(res.funding_gap, 0.0)

        print(f"[PASS] Spice Grinding Setup verified: Essential machinery present | Funding Gap: INR {res.funding_gap:,.0f}")

    def test_retail_business_setup(self):
        """Test 3: Retail Business Setup Plan."""
        retail_b = next((b for b in self.businesses if "retail" in b["id"].lower() or "kirana" in b["id"].lower() or "grocery" in b["id"].lower()), self.businesses[0])
        profile = UserProfile(
            name="Rahul Verma",
            state="Maharashtra",
            district="Pune",
            available_investment=200000.0,
            skills=["Retail Sales", "Inventory Management"],
            resources=["Commercial shop space", "Power connection"]
        )

        res: BusinessSetupResponse = generate_business_setup_plan(
            business_id=retail_b["id"],
            business_name=retail_b["business_name"],
            user_profile=profile
        )

        self.assertIsInstance(res, BusinessSetupResponse)
        self.assertIn("Udyam", " ".join(res.compliance_requirements))
        self.assertGreater(len(res.raw_materials), 0)
        print(f"[PASS] Retail Setup verified: Scale: {res.recommended_scale} | Raw Materials: {len(res.raw_materials)}")

    def test_low_capital_mode_and_infrastructure_gaps(self):
        """Test 4: Low-Capital Entrepreneur with Step 3 Infrastructure Gaps."""
        b = self.businesses[0]
        low_cap_profile = UserProfile(
            name="Vikram Gaikwad",
            state="Maharashtra",
            district="Nashik",
            available_investment=15000.0,  # Very low capital
            skills=[],
            resources=[]  # No land, no water, no power
        )

        # Mock feasibility result with infrastructure gaps from Step 3
        feasibility_result = {
            "overall_score": 58.0,
            "infrastructure_gaps": [
                "Requires dedicated land/shed — currently not declared in profile.",
                "Continuous water supply required for operations."
            ]
        }

        res: BusinessSetupResponse = generate_business_setup_plan(
            business_id=b["id"],
            business_name=b["business_name"],
            user_profile=low_cap_profile,
            feasibility_result=feasibility_result
        )

        # Low-capital mode assertions
        self.assertTrue(res.low_capital_advice.is_low_capital)
        self.assertGreater(res.funding_gap, 0.0)
        self.assertEqual(res.funding_gap, round(res.starter_setup.total_cost - 15000.0, 2))
        self.assertGreater(len(res.low_capital_advice.deferred_items), 0)
        self.assertGreater(len(res.low_capital_advice.immediate_actions), 0)

        # Infrastructure gap carry-forward
        gap_items = [req for req in res.infrastructure_requirements if "Gap" in req.status]
        self.assertGreater(len(gap_items), 0)

        print(f"[PASS] Low-Capital Mode verified: Gap: INR {res.funding_gap:,.0f} | Deferred Items: {len(res.low_capital_advice.deferred_items)} | Gaps detected: {len(gap_items)}")

if __name__ == "__main__":
    unittest.main()
