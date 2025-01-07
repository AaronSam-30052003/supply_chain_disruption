from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import joblib
import mysql.connector

app = FastAPI()

# Initialize the Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Example model path and data path (replace these paths with your actual paths)
MODEL_PATH = "E:\\supply_chain_disruption\\catboost_model.pkl"
DATA_PATH = "E:\supply_chain_disruption\supply_chain_sample_data.csv"

# Load the trained CatBoost model
def load_model():
    model = joblib.load(MODEL_PATH)
    return model

# Preprocess the new data
def preprocess_data(data):
    data['Date'] = pd.to_datetime(data['Date'])
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    data['Day'] = data['Date'].dt.day

    categorical_columns = ['Region', 'Country', 'Supplier', 'Transport Status', 'Item']
    for col in categorical_columns:
        data[col] = data[col].astype('category').cat.codes

    return data

# Connect to the MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",  # Replace with your MySQL host
        user="root",  # Replace with your MySQL username
        password="mickeychoki",  # Replace with your MySQL password
        database="inventory_management"
    )

# Check if an Item exists in the SupplyChainDisruptions table
def check_item_exists(item_name):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM Inventory WHERE ItemName = %s"
        cursor.execute(query, (item_name,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking item existence: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

# Update inventory based on predictions
def update_inventory(item_name, adjustment_quantity):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "UPDATE Inventory SET Stock = Stock + %s WHERE ItemName = %s"
        cursor.execute(query, (adjustment_quantity, item_name))
        conn.commit()

        cursor.execute("SELECT Stock FROM Inventory WHERE ItemName = %s", (item_name,))
        updated_stock = cursor.fetchone()[0]
        print(f"Stock for {item_name} updated to {updated_stock}")
    except Exception as e:
        print(f"Error updating inventory: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Log disruptions for tracking
def log_disruptions(item_name, prediction, probability):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "INSERT INTO SupplyChainDisruptions (Date, Region, Country, Supplier, Item, InventoryLevel, LeadTime, TransportStatus, NewsSentiment, RiskFactor, Year, Month, Day, PredictedRiskFactor) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (1, 1, 1, item_name, 100, 5, 2, 0, prediction, probability, 2020, 1, 1, prediction))  # Example values for columns
        conn.commit()
        print(f"Disruption log created for {item_name} with Probability {probability}")
    except Exception as e:
        print(f"Error logging disruption: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict/", response_class=HTMLResponse)
async def predict(request: Request, items: str = Form(...)):
    try:
        model = load_model()  # Load the trained model
        data = pd.read_csv(DATA_PATH)  # Load the dataset

        # Debug: Print the dataset to check its contents
        print("Dataset Loaded:")
        print(data.head())  # Print the first few rows to ensure data is loaded correctly

        processed_data = preprocess_data(data)  # Preprocess the data

        # Debug: Print the processed data to check the preprocessing
        print("Processed Data:")
        print(processed_data.head())  # Print the first few rows of the processed data

        item_names = [item.strip() for item in items.split(",")]  # Get items to predict
        print(f"Input Items: {item_names}")  # Debugging input items

        results = []

        for item_name in item_names:
            # Check if the item exists in the database's Inventory table
            if not check_item_exists(item_name):
                results.append({"Item": item_name, "Risk Probability": "N/A", "Adjustment": "Item Not Found"})
                continue

            # Check if the item exists in the dataset
            item_data = data[data['Item'] == item_name]
            
            # Debug: Check the filtered item data
            print(f"Checking Item: {item_name}")
            print(item_data)  # Print the matching rows (should be empty if not found)

            if item_data.empty:
                results.append({"Item": item_name, "Risk Probability": "N/A", "Adjustment": "Item Not Found"})
                continue

            # If the item exists, make the prediction
            item_data_preprocessed = preprocess_data(item_data)
            predicted_risk = model.predict(item_data_preprocessed)[0]  # Get predicted risk for the item

            adjustment = "No Adjustment"
            if predicted_risk > 0.8:  # Adjust the threshold as per your requirement
                adjustment = "Stock Reduced by 10"
                update_inventory(item_name, -10)  # Update inventory based on the prediction

            # Log disruptions
            log_disruptions(item_name, predicted_risk, predicted_risk)

            results.append({"Item": item_name, "Risk Probability": predicted_risk, "Adjustment": adjustment})

        return templates.TemplateResponse("result.html", {"request": request, "results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
