from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ddr(inspection_text, thermal_text):
    prompt = f"""
You are a professional building inspection expert.

Generate a clean, professional Detailed Diagnostic Report (DDR).

Structure:

1. Property Issue Summary
2. Area-wise Observations
3. Root Cause Analysis
4. Severity Assessment
5. Recommended Actions
6. Additional Notes
7. Limitations / Disclaimer

Keep it detailed, structured, and readable like a professional report.

Inspection Report:
{inspection_text}

Thermal Report:
{thermal_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
