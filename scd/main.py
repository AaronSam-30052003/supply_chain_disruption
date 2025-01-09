from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Configuration
DATABASE_URL = "mysql+mysqlconnector://root:mickeychoki@localhost/supply_chains"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI Setup
app = FastAPI()

# Template Configuration
templates = Jinja2Templates(directory="templates")

# Table Definitions
class Disruption(Base):
    __tablename__ = "disruptions"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    cause = Column(String)
    impact = Column(String)
    date = Column(DateTime)

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    session = SessionLocal()
    disruptions = session.query(Disruption).all()
    session.close()
    return templates.TemplateResponse("index.html", {"request": request, "disruptions": disruptions})

@app.post("/add-disruption/")
def add_disruption(location: str = Form(...), cause: str = Form(...), impact: str = Form(...), date: str = Form(...)):
    session = SessionLocal()
    new_disruption = Disruption(location=location, cause=cause, impact=impact, date=date)
    session.add(new_disruption)
    session.commit()
    session.close()
    return {"message": "Disruption added successfully"}
