# ==============================================================================
# FINANCIAL INCLUSION AGENT (FIA) using Google ADK
# This is the Orchestrator Agent for the fia/ directory.
# It uses Google Search Grounding for live facts on credit and insurance schemes.
# ==============================================================================

import json
from typing import List, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import types
from datetime import date # ADDED: For dynamic year generation

# --- 1. Specialized Tool Definitions (Logic copied from fia_functions.py) ---
# NOTE: In a production environment, you would typically import these functions:
# from .fia_functions import credit_advisory_tool, insurance_info_tool, fraud_prevention_tool

# Tool 1: Credit Advisory Tool (Dynamic - Returns Search Prompt)
def credit_advisory_tool(
    query: str,
    farmer_status: str,
    land_holding_hectares: float,
    scheme_type: str = "National",
    state_name: str = ""
) -> str:
    """
    Handles queries related to loans, subsidies, credit card schemes (like KCC), 
    and direct benefit schemes (like PM-KISAN). This tool returns a precise 
    search query for the LLM to execute via Google Search, ensuring live, up-to-date facts.
    """
    current_year = date.today().year # FIX: Use current year dynamically
    
    context = f"Farmer Status: {farmer_status}, Land: {land_holding_hectares} hectares. "
    
    if scheme_type.lower() == "state" and state_name:
        # State-level scheme query (dynamic)
        search_prompt = f"Find the official, current application process, eligibility criteria, and interest rates for the latest major agriculture credit or subsidy scheme run by the {state_name} government for small and marginal farmers. Ensure the source is a government or regulated financial website."
    
    elif "kcc" in query.lower() or "kisan credit card" in query.lower() or "loan" in query.lower():
        # National KCC query (dynamic)
        search_prompt = f"Find the official {current_year} interest rate (after subvention), maximum loan limit (short term), and the full list of required documents for the Kisan Credit Card (KCC) scheme for Indian farmers. Ensure the source is a government or regulated financial website."
        
    elif "pm-kisan" in query.lower() or "income support" in query.lower():
        # PM-KISAN query (dynamic)
        search_prompt = "What is the official annual payout amount, installment frequency, and eligibility criteria for the Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme?"
        
    else:
        # Default fallback for an unspecified credit query
        search_prompt = f"Provide a concise summary of the latest and most relevant government agricultural loan schemes available to Indian farmers today, focusing on subsidized interest rates and application methods."

    return context + search_prompt

# Tool 2: Insurance Information Tool (Dynamic - Returns Search Prompt, Expanded)
def insurance_info_tool(
    crop_type: str,
    season: str,
    state_name: str = ""
) -> str:
    """
    Handles queries about crop insurance, premium rates, claim procedures, and 
    scheme eligibility for PMFBY, WBCIS, and state-specific schemes. This tool 
    returns a precise search query for the LLM to execute against live web data.
    """
    
    base_query = (
        f"Find the official farmer premium rates and coverage details for {crop_type} "
        f"during the {season} season. Confirm the required loss reporting window and "
        f"the official claim helpline number."
    )
    
    if "weather" in crop_type.lower():
        # Focus on WBCIS for weather-related queries
        scheme_focus = "Weather Based Crop Insurance Scheme (WBCIS)"
    elif "coconut" in crop_type.lower() or "palm" in crop_type.lower() and state_name:
        # Focus on state-specific or specialized crop insurance like CPIS
        scheme_focus = f"Coconut Palm Insurance Scheme (CPIS) or similar specialized scheme in {state_name}"
    else:
        # Default to the most common, PMFBY, but keep the query broad enough to find alternatives
        scheme_focus = "Pradhan Mantri Fasal Bima Yojana (PMFBY)"

    # Final Combined Search Prompt
    search_prompt = (
        f"Focus on the latest official information for the **{scheme_focus}**. "
        f"{base_query} Prioritize sources from government or national insurance entities."
    )

    return search_prompt

# Tool 3: Fraud Prevention Tool (Static/Universal - Returns JSON String)
def fraud_prevention_tool(
    scenario: str
) -> str:
    """
    Analyzes user scenarios for common rural financial fraud risks (Phishing, UPI scams, 
    Advance Fee scams) and provides immediate, non-negotiable safety advice. 
    This tool uses static, reliable security rules. **Returns structured JSON.**
    """
    scenario_lower = scenario.lower()
    
    # Initialize structured output
    output = {
        "risk_level": "None apparent, but exercise caution.",
        "advice_code": "GENERAL_CAUTION",
        "advice_text": "Always remember to keep your personal financial details private. If something sounds too good to be true, it usually is."
    }
    
    # --- STATIC ANALYSIS LOGIC ---
    if "otp" in scenario_lower or "pin" in scenario_lower or "cvv" in scenario_lower or "bank manager" in scenario_lower or "aadhar update" in scenario_lower:
        output.update({
            "risk_level": "HIGH - Phishing/Vishing",
            "advice_code": "NEVER_SHARE_PIN",
            "advice_text": "NEVER SHARE YOUR OTP, PIN, CVV, or AADHAR details. Official bank staff will never ask for this over the phone or SMS. This is a SCAM. Immediately block the sender/caller."
        })
    elif "prize" in scenario_lower or "lottery" in scenario_lower or ("fees" in scenario_lower and "loan" in scenario_lower):
        output.update({
            "risk_level": "MEDIUM - Advance Fee Scam",
            "advice_code": "NO_PRE_PAYMENT",
            "advice_text": "Be highly skeptical. Legitimate loans or prizes never require you to pay a fee or deposit money first to receive your funds. Do not send any money."
        })
    elif "qr code" in scenario_lower or "request money" in scenario_lower or "upi" in scenario_lower:
        output.update({
            "risk_level": "HIGH - UPI Scam",
            "advice_code": "UPI_CRITICAL_WARNING",
            "advice_text": "CRITICAL: Scanning a QR code or approving a 'Request Money' link is used to SEND money, NOT to receive it. If you are expecting money, you should never be asked to scan or enter your UPI PIN. Do not proceed."
        })
    elif "guaranteed return" in scenario_lower or "chit fund" in scenario_lower or "investment" in scenario_lower:
        output.update({
            "risk_level": "MEDIUM - Ponzi/Investment Scam",
            "advice_code": "VERIFY_INVESTMENT",
            "advice_text": "Investment schemes promising 'guaranteed' or 'unrealistic' high returns are often fraudulent (Ponzi Schemes). Only trust schemes registered with RBI or SEBI. Verify before you invest."
        })

    # FIX: Return JSON string instead of a formatted string
    return json.dumps(output)


# --- 2. ADK FunctionTool Wrappers ---

# This function is what your team will run to create the agent for deployment.
def create_fia_agent() -> LlmAgent:
    """
    Creates the Financial Inclusion Agent, equipped with its specialized tools.
    This is the core definition of the Orchestrator Agent.
    """
    
    # 1. Wrap the Credit Function
    # FIX: Removed 'name' and 'description' arguments. Description is taken from the docstring.
    credit_tool = FunctionTool(
        credit_advisory_tool, 
    )
    
    # 2. Wrap the Insurance Function
    # FIX: Removed 'name' and 'description' arguments. Description is taken from the docstring.
    insurance_tool = FunctionTool(
        insurance_info_tool, 
    )
    
    # 3. Wrap the Fraud Function
    # FIX: Removed 'name' and 'description' arguments. Description is taken from the docstring.
    fraud_tool = FunctionTool(
        fraud_prevention_tool, 
    )

    # Define the Orchestrator Agent (The Brain)
    fia_agent = LlmAgent(
        model='gemini-2.5-flash-preview-09-2025',  # Recommended fast model for agentic planning
        name='FinancialInclusionAgent',
        description='Expert agent specializing in Indian farmer financial inclusion: Credit, Insurance, and Anti-fraud guidance.',
        instruction="""
        You are the 'Financial Inclusion Agent (FIA)', a friendly, precise, and highly trusted financial tutor for Indian farmers.
        Your primary role is to simplify complex financial topics and government schemes.
        
        1. When the user asks about loans, credit, or financial support, use the **credit_advisory_tool** (the tool name is inferred from the function name).
        2. When the user asks about crop protection or insurance, use the **insurance_info_tool**.
        3. When the user asks if a message/call/scheme is safe, or asks for general safety advice, use the **fraud_prevention_tool**.
        
        CRITICAL RULE: For Credit and Insurance, the tool output is a search query. You MUST execute this search query using your internal tools and then construct the final, cited, conversational answer from the search results.
        
        4. If you use the fraud_prevention_tool, you will receive a JSON string. Extract the 'advice_text' from the JSON and present it to the user in a strong, non-negotiable warning format.
        """,
        tools=[credit_tool, insurance_tool, fraud_tool],
        # REMOVED: The problematic 'google_search={}' parameter. Rely on environment/instruction for grounding.
        # Optional: Configure the model generation for deterministic, factual outputs
        generate_content_config=types.GenerateContentConfig(temperature=0.0)
    )
    
    return fia_agent

# --- 3. ADK Entry Point and Local Runner ---

# 1. ADK ENTRY POINT: Create the required global variable 'root_agent' 
# This is the fix to resolve the ValueError: No root_agent found
root_agent = create_fia_agent()

if __name__ == '__main__':
    print("--- Initializing Financial Inclusion Agent (FIA) ---")
    
    # Use the globally defined root_agent for local testing
    print(f"Agent '{root_agent.name}' initialized successfully with {len(root_agent.tools)} tools in agent.py.")
    
    # Example 1: Credit Query (KCC) - Simulates LLM calling the tool
    print("\n--- TEST 1: Credit Query (KCC) ---")
    credit_query = "How can I apply for a Kisan Credit Card? I am a sharecropper."
    
    print("Simulated Tool Call Output (This is the query the LLM will search for):")
    # Manually calling the tool function to see the LLM's next step (the search query)
    result = credit_advisory_tool(
        query="apply for KCC",
        farmer_status="sharecropper",
        land_holding_hectares=0.0, # Assuming no owned land
        scheme_type="National"
    )
    print(f"**Query for Gemini:** {result}")

    # Example 2: Insurance Query (WBCIS) - Simulates LLM calling the expanded tool
    print("\n--- TEST 2: Insurance Query (WBCIS Focus) ---")
    insurance_query = "I need insurance for my cotton crop, I'm worried about the weather this Kharif season in Maharashtra."
    
    print("Simulated Tool Call Output (This is the query the LLM will search for):")
    # Manually calling the tool function to see the LLM's next step (the search query)
    result = insurance_info_tool(
        crop_type="cotton", 
        season="Kharif",
        state_name="Maharashtra" # ADDED: Demonstrates the state parameter
    )
    print(f"**Query for Gemini:** {result}")


    # Example 3: Fraud Query (Static - Now returns JSON)
    print("\n--- TEST 3: Fraud Query (Static Security) ---")
    fraud_query = "A message said I won a big prize but I must give my CVV to confirm my bank details."
    
    print("Tool Output (JSON string - The HGA should parse this):")
    # Manually calling the tool function (Fraud is static, so this is the final answer)
    result = fraud_prevention_tool(scenario=fraud_query)
    print(result)