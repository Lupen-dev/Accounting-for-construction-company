from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class CustomerType(enum.Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    BOTH = "both"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tax_number = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    type = Column(Enum(CustomerType))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    balance = relationship("CustomerBalance", back_populates="customer", uselist=False)

class TransactionType(enum.Enum):
    DEBIT = "debit"  # Borç
    CREDIT = "credit"  # Alacak

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(Enum(TransactionType))
    description = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")

class CustomerBalance(Base):
    __tablename__ = "customer_balances"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True)
    total_debit = Column(Float, default=0)  # Toplam borç
    total_credit = Column(Float, default=0)  # Toplam alacak
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="balance")