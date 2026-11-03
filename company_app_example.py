"""
Example: your EXISTING company FastAPI app with the resistor game mounted at /resistor.

Put the resistor_app folder next to (or inside) your company project, then in your
existing main file add the 3 marked lines. Students open  https://yourcompany.com/resistor/
"""
import sys
from pathlib import Path

from fastapi import FastAPI

# --- 1) make the resistor code importable (adjust the path to where you put the folder) ---
sys.path.append(str(Path(__file__).resolve().parent))
from main import app as resistor_app          # --- 2) import the resistor sub-app ---

company_app = FastAPI(title="Company App")     # <- this is YOUR existing app object


@company_app.get("/")
def home():
    return {"message": "Company app home"}


company_app.mount("/resistor", resistor_app)   # --- 3) mount it ---

# Run for testing:  python -m uvicorn company_app_example:company_app --reload
# Then open:        http://127.0.0.1:8000/resistor/
