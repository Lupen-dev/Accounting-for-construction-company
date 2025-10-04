from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class ChequeType(enum.Enum):
    CHEQUE = "cheque"  # Çek
    BILL = "bill"      # Senet

class ChequeStatus(enum.Enum):
    PENDING = "pending"       # Beklemede
    CASHED = "cashed"        # Tahsil edildi
    BOUNCED = "bounced"      # Karşılıksız
    CANCELLED = "cancelled"  # İptal edildi
    
class ChequeDirection(enum.Enum):
    RECEIVED = "received"  # Alınan
    GIVEN = "given"       # Verilen

class Cheque(Base):
    __tablename__ = "cheques"

    id = Column(Integer, primary_key=True, index=True)
    cheque_no = Column(String, unique=True, index=True)
    type = Column(Enum(ChequeType))
    direction = Column(Enum(ChequeDirection))
    amount = Column(Float)
    due_date = Column(DateTime)
    issue_date = Column(DateTime, default=datetime.utcnow)
    bank_name = Column(String)
    bank_branch = Column(String)
    drawer_name = Column(String)  # Keşideci
    status = Column(Enum(ChequeStatus), default=ChequeStatus.PENDING)
    
    # Optional fields
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    notes = Column(String, nullable=True)
    
    # Tracking fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", backref="cheques")
    transactions = relationship("ChequeTransaction", back_populates="cheque")

class ChequeTransactionType(enum.Enum):
    STATUS_CHANGE = "status_change"
    NOTE_ADDED = "note_added"
    DETAIL_UPDATED = "detail_updated"

class ChequeTransaction(Base):
    __tablename__ = "cheque_transactions"

    id = Column(Integer, primary_key=True, index=True)
    cheque_id = Column(Integer, ForeignKey("cheques.id"))
    transaction_type = Column(Enum(ChequeTransactionType))
    old_status = Column(Enum(ChequeStatus), nullable=True)
    new_status = Column(Enum(ChequeStatus), nullable=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cheque = relationship("Cheque", back_populates="transactions")