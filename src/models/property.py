from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

class PropertyType(enum.Enum):
    LAND = "Land"
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    MIXED_USE = "Mixed Use"

class PropertyStatus(enum.Enum):
    AVAILABLE = "Available"
    SOLD = "Sold"
    RENTED = "Rented"
    UNDER_CONSTRUCTION = "Under Construction"
    UNDER_MAINTENANCE = "Under Maintenance"

class OwnershipType(enum.Enum):
    FULL = "Full Ownership"
    SHARED = "Shared Ownership"
    LEASEHOLD = "Leasehold"
    CONDOMINIUM = "Condominium"

class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    property_no = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    type = Column(SQLEnum(PropertyType), nullable=False)
    status = Column(SQLEnum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    
    # Location details
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100))
    postal_code = Column(String(20))
    
    # Property details
    area = Column(Float)  # in square meters
    construction_year = Column(Integer)
    features = Column(Text)  # JSON string of property features
    
    # Financial details
    purchase_price = Column(Float)
    current_value = Column(Float)
    monthly_rent = Column(Float)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    deeds = relationship("Deed", back_populates="property")
    documents = relationship("PropertyDocument", back_populates="property")

class Deed(Base):
    __tablename__ = 'deeds'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    deed_no = Column(String(50), unique=True, nullable=False)
    registration_date = Column(Date, nullable=False)
    ownership_type = Column(SQLEnum(OwnershipType), nullable=False)
    
    # Owner details
    owner_name = Column(String(200), nullable=False)
    owner_id_number = Column(String(20))  # National ID or tax number
    share_ratio = Column(Float, default=1.0)  # For shared ownership
    
    purchase_price = Column(Float)
    notes = Column(Text)
    
    is_active = Column(bool, default=True)  # To track current vs historical deeds
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    property = relationship("Property", back_populates="deeds")

class DocumentType(enum.Enum):
    DEED = "Deed"
    BLUEPRINT = "Blueprint"
    PERMIT = "Building Permit"
    TAX = "Tax Document"
    INSURANCE = "Insurance"
    CONTRACT = "Contract"
    OTHER = "Other"

class PropertyDocument(Base):
    __tablename__ = 'property_documents'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    type = Column(SQLEnum(DocumentType), nullable=False)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to stored document
    description = Column(Text)
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    property = relationship("Property", back_populates="documents")