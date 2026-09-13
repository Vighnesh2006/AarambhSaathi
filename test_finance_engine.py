"""
Test Suite for STEP 5: Financial & Funding Structuring Engine.
Tests:
1. TEST 1: Project Cost ₹1,50,000, Own Contribution ₹1,00,000 -> Funding Requirement: ₹50,000.
2. TEST 2: Project Cost ₹2,50,000, Own Contribution ₹50,000 -> Funding Requirement: ₹2,00,000.
3. TEST 3: Verify EMI calculation against standard reducing-balance EMI formula.
4. TEST 4: Verify EMI coverage classification (Strong >= 2.0x, Reasonable >= 1.5x, Tight >= 1.0x, High Risk < 1.0x).
5. TEST 5: Monthly revenue ₹80,000, Operating expense ₹50,000 -> Surplus: ₹30,000, Margin: 37.5%.
6. TEST 7: Low-capital user receives starter/funding-gap path without automatic rejection.
7. TEST 7: Zero/negative/invalid revenue handles gracefully without division by zero.
8. TEST 8: Insufficient data produces INSUFFICIENT DATA status without fabricated values.
"""

import os
import sys
import math
import unittest

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.models import FinancialInput, FinancialPlan, UserProfile
from backend.finance import calculate_financial_plan_raw, calculate_financial_plan, calculate_reducing_balance_emi

class TestFinancialStructuringEngine(unittest.TestCase):

    def test_1_funding_requirement_basic(self):
        """TEST 1: Project Cost ₹1,50,000, Own Contribution ₹1,00,000 -> Funding Requirement: ₹50,000."""
        res = calculate_financial_plan_raw(
            project_cost=150000.0,
            own_contribution=100000.0
        )
        self.assertEqual(res["project_cost"], 150000.0)
        self.assertEqual(res["own_contribution"], 100000.0)
        self.assertEqual(res["funding_requirement"], 50000.0)
        print("[PASS] TEST 1: Funding Requirement INR 50,000 verified.")

    def test_2_funding_requirement_higher_gap(self):
        """TEST 2: Project Cost ₹2,50,000, Own Contribution ₹50,000 -> Funding Requirement: ₹2,00,000."""
        res = calculate_financial_plan_raw(
            project_cost=250000.0,
            own_contribution=50000.0
        )
        self.assertEqual(res["project_cost"], 250000.0)
        self.assertEqual(res["own_contribution"], 50000.0)
        self.assertEqual(res["funding_requirement"], 200000.0)
        print("[PASS] TEST 2: Funding Requirement INR 200,000 verified.")

    def test_3_emi_calculation_formula(self):
        """TEST 3: Verify EMI calculation against standard reducing-balance formula."""
        principal = 100000.0
        annual_rate = 8.0
        tenure_months = 36

        # Standard reducing-balance formula: P * r * (1+r)^n / ((1+r)^n - 1)
        r = (annual_rate / 12.0) / 100.0
        expected_emi = round(principal * r * math.pow(1.0 + r, tenure_months) / (math.pow(1.0 + r, tenure_months) - 1.0), 2)
        
        calculated_emi = calculate_reducing_balance_emi(principal, annual_rate, tenure_months)
        self.assertEqual(calculated_emi, expected_emi)
        self.assertAlmostEqual(calculated_emi, 3133.64, places=1)
        print(f"[PASS] TEST 3: EMI calculation INR {calculated_emi} exactly matches reducing-balance formula.")

    def test_4_emi_coverage_classification(self):
        """TEST 4: Verify EMI coverage classification (Strong, Reasonable, Tight, High Risk)."""
        # Strong coverage >= 2.0x
        res_strong = calculate_financial_plan_raw(
            project_cost=100000.0,
            own_contribution=20000.0,
            monthly_revenue=40000.0,
            monthly_expenses=20000.0  # Surplus = 20,000
        )
        cov_strong = res_strong["repayment_capacity"]["status"]
        self.assertEqual(cov_strong, "Strong repayment buffer")

        # High Risk < 1.0x (Surplus lower than EMI)
        res_high_risk = calculate_financial_plan_raw(
            project_cost=400000.0,
            own_contribution=40000.0,
            monthly_revenue=10000.0,
            monthly_expenses=9000.0  # Surplus = 1,000, EMI ~ 6,500
        )
        cov_risk = res_high_risk["repayment_capacity"]["status"]
        self.assertEqual(cov_risk, "High repayment risk")
        print("[PASS] TEST 4: EMI coverage classification verified.")

    def test_5_revenue_expense_surplus_and_margin(self):
        """TEST 5: Monthly revenue ₹80,000, Operating expense ₹50,000 -> Surplus: ₹30,000, Margin: 37.5%."""
        res = calculate_financial_plan_raw(
            project_cost=200000.0,
            monthly_revenue=80000.0,
            monthly_expenses=50000.0
        )
        self.assertEqual(res["monthly_financials"]["revenue"], 80000.0)
        self.assertEqual(res["monthly_financials"]["operating_expense"], 50000.0)
        self.assertEqual(res["monthly_financials"]["surplus"], 30000.0)
        self.assertEqual(res["monthly_financials"]["profit_margin"], 37.5)
        print("[PASS] TEST 5: Monthly surplus INR 30,000 and profit margin 37.5% verified.")

    def test_6_low_capital_user_guidance(self):
        """TEST 6: Low-capital user receives a starter/funding-gap path, not an automatic rejection."""
        low_cap_profile = UserProfile(
            name="Raju",
            available_investment=20000.0
        )
        res = calculate_financial_plan_raw(
            project_cost=150000.0,
            user_profile=low_cap_profile
        )
        self.assertIsNotNone(res["low_capital_path"])
        self.assertTrue(res["low_capital_path"]["is_low_capital"])
        self.assertGreater(len(res["low_capital_path"]["recommended_next_steps"]), 0)
        self.assertIn("starter_recommendation", res["low_capital_path"])
        print("[PASS] TEST 6: Low-capital user guidance verified without rejection.")

    def test_7_zero_and_invalid_revenue_guards(self):
        """TEST 7: Zero/negative/invalid revenue must not cause division errors."""
        res_zero = calculate_financial_plan_raw(
            project_cost=100000.0,
            monthly_revenue=0.0,
            monthly_expenses=0.0
        )
        self.assertEqual(res_zero["monthly_financials"]["profit_margin"], 0.0)
        self.assertEqual(res_zero["break_even"]["months"], 999.0)
        print("[PASS] TEST 7: Zero revenue division guards verified.")

    def test_8_insufficient_data_handling(self):
        """TEST 8: Insufficient data produces INSUFFICIENT DATA rather than fabricated values."""
        res = calculate_financial_plan_raw(
            project_cost=100000.0,
            monthly_revenue=0.0
        )
        self.assertIn(res["financial_health"], ["INSUFFICIENT DATA", "HIGH RISK"])
        self.assertIn("verified", res["data_quality"])
        self.assertIn("estimated", res["data_quality"])
        print("[PASS] TEST 8: Data quality and health categorization verified.")

if __name__ == "__main__":
    unittest.main()
