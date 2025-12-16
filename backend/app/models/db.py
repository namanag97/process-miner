import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """
    User model for no-auth session management.
    Users are identified by a UUID stored in the frontend.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")


class Upload(Base):
    """
    Upload model to track files uploaded by users.
    """
    __tablename__ = "uploads"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, error
    row_count = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploads")
    mappings = relationship("Mapping", back_populates="upload", cascade="all, delete-orphan")


class Mapping(Base):
    """
    Mapping model for process mining configurations.
    """
    __tablename__ = "mappings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String, ForeignKey("uploads.id"), nullable=False)
    
    case_id_column = Column(String, nullable=False)
    activity_column = Column(String, nullable=False)
    timestamp_column = Column(String, nullable=False)
    timestamp_format = Column(String, nullable=True)
    resource_column = Column(String, nullable=True)
    cost_column = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    upload = relationship("Upload", back_populates="mappings")
    jobs = relationship("Job", back_populates="mapping", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="mapping", cascade="all, delete-orphan")


class Job(Base):
    """
    Job model for background processing status.
    """
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    mapping_id = Column(String, ForeignKey("mappings.id"), nullable=False)
    
    status = Column(String, default="queued")  # queued, processing, completed, failed
    progress = Column(Integer, default=0)
    progress_message = Column(String, nullable=True)
    error = Column(String, nullable=True)
    
    dataset_id = Column(String, nullable=True)  # Set when completed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    mapping = relationship("Mapping", back_populates="jobs")


class Dataset(Base):
    """
    Dataset model for storing analysis results.
    Stores large JSON blobs as Text for MVP.
    """
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    mapping_id = Column(String, ForeignKey("mappings.id"), nullable=False)
    
    # Analysis results stored as JSON strings
    dfg_json = Column(String, nullable=True)  # Using String/Text for SQLite
    variants_json = Column(String, nullable=True)
    stats_json = Column(String, nullable=True)
    activity_stats_json = Column(String, nullable=True)
    deviations_json = Column(String, nullable=False, default="[]")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mapping = relationship("Mapping", back_populates="datasets")
