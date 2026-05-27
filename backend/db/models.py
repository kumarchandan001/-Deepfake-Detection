from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.db.config import Base
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relational mappings
    investigations = relationship("Investigation", back_populates="analyst")
    audit_logs = relationship("AuditLog", back_populates="user")

class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    analyst_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="open") # open, completed, closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    analyst = relationship("User", back_populates="investigations")
    media = relationship("UploadedMedia", back_populates="investigation")
    reports = relationship("ForensicReport", back_populates="investigation")

class UploadedMedia(Base):
    __tablename__ = "uploaded_media"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(50), ForeignKey("investigations.id"), nullable=False)
    filename = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    cloud_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="media")
    predictions = relationship("AIPrediction", back_populates="media")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    media_id = Column(String(50), ForeignKey("uploaded_media.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    prediction = Column(String(30), nullable=False) # REAL, FAKE
    confidence = Column(Float, nullable=False)
    raw_score = Column(Float, nullable=False)
    processing_time = Column(Float, nullable=False)
    xai_heatmap_path = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    media = relationship("UploadedMedia", back_populates="predictions")

class ForensicReport(Base):
    __tablename__ = "reports"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(50), ForeignKey("investigations.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    verdict = Column(String(30), nullable=False) # AUTHENTIC, MANIPULATED, UNDETERMINED
    confidence_aggregate = Column(Float, nullable=False)
    pdf_path = Column(String(500), nullable=True)
    csv_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="reports")

class RealtimeSession(Base):
    __tablename__ = "realtime_sessions"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    session_token = Column(String(100), unique=True, nullable=False)
    client_ip = Column(String(50), nullable=True)
    frames_processed = Column(Integer, default=0)
    anomalies_detected = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(50), primary_key=True, default=generate_uuid)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # e.g. login_attempt, file_upload
    ip_address = Column(String(50), nullable=True)
    resource_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audit_logs")
