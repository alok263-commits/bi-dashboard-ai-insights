import os
from google import genai
from dotenv import load_dotenv

# 1. Unlock the vault and get the API key
# Try .env first (local dev). On Streamlit Cloud there is no .env file,
# so we fall back to st.secrets, which is where Cloud "Secrets" actually live.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    raise ValueError(
        "API Key not found. Set GEMINI_API_KEY in your .env file locally, "
        "or in Streamlit Cloud → Settings → Secrets when deployed."
    )

# 2. Connect to Google Gemini using the new unified SDK
client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"

def generate_kpi_summary(kpi_data_string):
    """Feeds KPI data to Gemini to generate an executive summary."""
    prompt = f"""
    You are an expert Business Intelligence Analyst. 
    Review the following retail KPI data and provide a concise, 3-bullet-point executive summary highlighting the most critical insights.
    
    Data:
    {kpi_data_string}
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text

# --- Quick Connection Test ---
if __name__ == "__main__":
    print("Testing Gemini API Connection...")
    
    # Fake data to test the connection
    sample_kpi_data = "Total Revenue: $2.30M, Total Profit: $286K, Profit Margin: 12.4%, Outlier Sales: $1.74M"
    
    try:
        summary = generate_kpi_summary(sample_kpi_data)
        print("\n✅ API Connection Successful! Here is the AI output:\n")
        print(summary)
    except Exception as e:
        print(f"\n❌ API Error: {e}")