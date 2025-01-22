from fastapi import FastAPI, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

app = FastAPI()

# Load environment variables
load_dotenv()

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
    background_tasks: BackgroundTasks,
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

        # Trigger email notification if the risk is high
        if risk_factor > 0.3:  # Threshold for high risk
            background_tasks.add_task(send_email_notification, risk_factor)

        # Return the result
        return {"risk_factor": round(risk_factor, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")


@app.get("/dashboard/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render the dashboard with supply chain data visualizations.
    """
    # Simulated data
    data = {
        "regions": ["North", "South", "East", "West"],
        "inventory": [120, 95, 75, 110],
        "disruptions": [5, 8, 3, 2],
    }

    # Create visualizations
    plt.figure(figsize=(10, 5))
    sns.barplot(x=data["regions"], y=data["inventory"])
    plt.title("Inventory Status by Region")
    plt.xlabel("Region")
    plt.ylabel("Inventory Levels")

    # Convert the plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return templates.TemplateResponse("dashboard.html", {"request": request, "plot_data": image_base64})


def send_email_notification(risk_factor):
    """
    Send an email notification for critical disruptions.
    """
    try:
        sender_email = "aaronvsam289@gmail.com"
        receiver_email = "sobanaramakrishnan04@gmail.com.com@gmail.com"
        password = os.getenv("EMAIL_PASSWORD") 

        # Email content
        subject = "Critical Supply Chain Disruption Alert"
        body = f"A high-risk factor of {risk_factor:.2f} was detected. Immediate attention is required."

        # Set up the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Send the email using Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        print(f"Failed to send email: {e}")
