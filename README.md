# Supply Chain Risk Prediction System

This project is a web-based application built with FastAPI for predicting supply chain risk factors using a trained XGBoost model. The app provides an intuitive interface for inputting supply chain parameters and visualizing data insights.

## Features

Risk Factor Prediction: Predicts supply chain disruption risk using user-provided parameters.
Dashboard Visualization: Displays visual insights like inventory status by region.
Email Alerts: Sends notifications for high-risk predictions.
Interactive Form: User-friendly form for submitting input data.
Data Visualizations: Built with Matplotlib and Seaborn for better decision-making.

## Tech Stack

Backend: FastAPI
Frontend: HTML, CSS, JavaScript
Machine Learning: XGBoost
Database: Environment-based setup (optional)
Email Integration: SMTP
Environment Variables: Managed using dotenv

## Usage

Home Page: Input features like year, region, inventory, and more to predict the risk factor.
Dashboard: View graphical insights on inventory and disruptions by region.
Email Alerts: Receive notifications for high-risk factors above the threshold.

## Dependencies

FastAPI
Jinja2
Numpy
Matplotlib
Seaborn
Joblib
Python-Dotenv
SMTP for email alerts


