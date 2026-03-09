from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    website = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    employees = Column(String(100), nullable=True)
    size_category = Column(String(50), nullable=True)  # Startup, Small, Medium, Large
    hourly_rate = Column(String(100), nullable=True)
    founded = Column(String(50), nullable=True)
    services = Column(Text, nullable=True)  # JSON string
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    source = Column(String(100), default="Clutch.co")
    lead_score = Column(Integer, default=0)
    ai_analysis = Column(Text, nullable=True)
    ai_insights = Column(Text, nullable=True)
    email_status = Column(String(50), default="pending")
    crm_status = Column(String(50), default="not_synced")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Lead {self.company_name}>"