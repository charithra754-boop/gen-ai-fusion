# ==============================================================================
# UNIT TESTS FOR FINANCIAL INCLUSION AGENT (FIA) TOOLS
# Tests the deterministic logic in the tool functions (no LLM, no web search)
# ==============================================================================
import pytest
import json
# Import the actual date object from the datetime module
from datetime import date 
# Import the functions and the module for patching
import agent
from agent import credit_advisory_tool, insurance_info_tool, fraud_prevention_tool



# --- TEST FIXTURES ---
# Mock the current date to ensure tests run consistently year after year
@pytest.fixture(autouse=True) # auto-use ensures it applies to all tests that use date.today()
def current_year(monkeypatch):
    """Fixture to ensure a consistent year for dynamic query tests."""
    class MockDate:
        @staticmethod
        def today():
            class MockToday:
                year = 2025 # Fixed year for predictable search query output
            return MockToday()
    # FIX: Patch the 'date' symbol (imported from datetime) inside the 'fia' module
    monkeypatch.setattr(fia, 'date', MockDate)


# --- 1. Credit Advisory Tool Tests ---

def test_credit_kcc_query(current_year):
    """Test that the tool generates a precise KCC search query for the fixed year."""
    query = "I want to know about the KCC loan limit."
    result = credit_advisory_tool(
        query=query, 
        farmer_status="owner", 
        land_holding_hectares=5.0
    )
    # Check for core components of the dynamic query
    assert "Kisan Credit Card (KCC)" in result
    assert "2025" in result # Should use the mocked year
    assert "interest rate (after subvention)" in result
    assert "owner" in result # Check context inclusion

def test_credit_pmkisan_query():
    """Test that the tool generates a PM-KISAN-specific query."""
    query = "When do I get my PM-KISAN money?"
    result = credit_advisory_tool(
        query=query, 
        farmer_status="marginal", 
        land_holding_hectares=1.5
    )
    assert "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)" in result
    assert "annual payout amount" in result

def test_credit_state_scheme_query():
    """Test that the tool generates a state-specific query."""
    query = "Are there any new loan schemes in Bihar?"
    result = credit_advisory_tool(
        query=query, 
        farmer_status="small", 
        land_holding_hectares=2.5,
        scheme_type="State",
        state_name="Bihar"
    )
    assert "Bihar government" in result
    assert "application process, eligibility criteria" in result


# --- 2. Insurance Information Tool Tests ---

def test_insurance_pmfby_default_query():
    """Test default PMFBY query generation for a standard crop."""
    query = "What is the insurance rate for my wheat crop?"
    result = insurance_info_tool(
        crop_type="wheat", 
        season="Rabi", 
        state_name="Punjab"
    )
    assert "Pradhan Mantri Fasal Bima Yojana (PMFBY)" in result
    assert "coverage details for wheat during the Rabi season" in result

def test_insurance_wbcis_focus_query():
    """Test that weather keywords trigger the WBCIS focus."""
    query = "Is there weather insurance for my soyabean?"
    result = insurance_info_tool(
        crop_type="soyabean (weather)", 
        season="Kharif"
    )
    assert "Weather Based Crop Insurance Scheme (WBCIS)" in result
    assert "soyabean" in result

def test_insurance_specialized_crop_focus_query():
    """Test that specialized crops trigger state-specific scheme query."""
    query = "How do I insure my coconut palms in Kerala?"
    result = insurance_info_tool(
        crop_type="coconut palm", 
        season="Year-round",
        state_name="Kerala"
    )
    assert "Coconut Palm Insurance Scheme (CPIS) or similar specialized scheme in Kerala" in result


# --- 3. Fraud Prevention Tool Tests (Testing JSON Output) ---

def test_fraud_phishing_high_risk():
    """Test for high-risk phishing keywords (OTP, PIN)."""
    scenario = "Bank called me and asked for my OTP to update my account."
    result = fraud_prevention_tool(scenario)
    data = json.loads(result)
    assert data["risk_level"] == "HIGH - Phishing/Vishing"
    assert data["advice_code"] == "NEVER_SHARE_PIN"

def test_fraud_upi_critical_warning():
    """Test for critical UPI/QR code scam warning."""
    scenario = "They told me to scan a QR code to receive a payment."
    result = fraud_prevention_tool(scenario)
    data = json.loads(result)
    assert data["risk_level"] == "HIGH - UPI Scam"
    assert data["advice_code"] == "UPI_CRITICAL_WARNING"
    assert "SEND money, NOT to receive it" in data["advice_text"]

def test_fraud_advance_fee_scam():
    """Test for advance fee/prize scam keywords."""
    scenario = "I won a huge lottery prize but must send a fee first."
    result = fraud_prevention_tool(scenario)
    data = json.loads(result)
    assert data["risk_level"] == "MEDIUM - Advance Fee Scam"
    assert data["advice_code"] == "NO_PRE_PAYMENT"

def test_fraud_no_risk_general_caution():
    """Test for a benign query that should return general caution."""
    scenario = "I saw a message about a new phone."
    result = fraud_prevention_tool(scenario)
    data = json.loads(result)
    assert data["risk_level"] == "None apparent, but exercise caution."
    assert data["advice_code"] == "GENERAL_CAUTION"