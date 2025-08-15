from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, index=True)
    language = Column(String(10), default="en")
    location = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    query_text = Column(Text)
    query_type = Column(String(50))  # irrigation, crop_selection, weather, finance, policy
    response = Column(Text)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100))
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

class CropData(Base):
    __tablename__ = "crop_data"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100))
    season = Column(String(50))
    soil_type = Column(String(50))
    water_requirement = Column(String(50))
    growth_duration = Column(Integer)  # in days
    yield_per_hectare = Column(Float)
    market_price = Column(Float)

class PolicyData(Base):
    __tablename__ = "policy_data"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(200))
    description = Column(Text)
    eligibility = Column(Text)
    benefits = Column(Text)
    application_process = Column(Text)
    contact_info = Column(Text)
    is_active = Column(Boolean, default=True)

# Database setup
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 