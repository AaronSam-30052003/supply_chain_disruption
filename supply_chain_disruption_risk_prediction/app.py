from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import joblib
import numpy as np

app = FastAPI()

# Load the trained model
try:
    model = joblib.load("xgboost_model.pkl")
except Exception as e:
    raise RuntimeError(f"Error loading model: {e}")

# Set up templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serve the main HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict/")
async def predict(
    year: int = Form(...),
    month: int = Form(...),
    day: int = Form(...),
    region: int = Form(...),
    country: int = Form(...),
    supplier: int = Form(...),
    inventory: float = Form(...),
    lead_time: int = Form(...),
    transport_status: int = Form(...),
    news_sentiment: float = Form(...),
):
    """
    Predict the risk factor based on the input features.
    """
    try:
        # Prepare the input data
        input_data = np.array([[year, month, day, region, country, supplier, inventory, lead_time, transport_status, news_sentiment]])
        
        # Generate the prediction
        prediction = model.predict(input_data)

        # Convert to Python native type
        risk_factor = float(prediction[0])

        # Return the result
        return {"risk_factor": round(risk_factor, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
