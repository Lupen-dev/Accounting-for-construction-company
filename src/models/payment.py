from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    LATE = "Late"
    CANCELLED = "Cancelled"

class PaymentType(enum.Enum):
    CASH = "Cash"
    BANK_TRANSFER = "Bank Transfer"
    CREDIT_CARD = "Credit Card"
    CHEQUE = "Cheque"

class PaymentPlan(Base):
    __tablename__ = 'payment_plans'

    id = Column(Integer, primary_key=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Financial details
    total_amount = Column(Float, nullable=False)
    down_payment = Column(Float, default=0.0)
    interest_rate = Column(Float, default=0.0)  # Annual interest rate
    number_of_installments = Column(Integer, nullable=False)
    
    start_date = Column(Date, nullable=False)
    payment_day = Column(Integer, nullable=False)  # Day of month for payments
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    customer = relationship("Customer", back_populates="payment_plans")
    installments = relationship("Installment", back_populates="payment_plan")
    
    @property
    def remaining_balance(self):
        """Calculate remaining balance"""
        paid_amount = sum(inst.amount for inst in self.installments if inst.status == PaymentStatus.PAID)
        return self.total_amount - self.down_payment - paid_amount
    
    @property
    def is_completed(self):
        """Check if all installments are paid"""
        return all(inst.status == PaymentStatus.PAID for inst in self.installments)

class Installment(Base):
    __tablename__ = 'installments'

    id = Column(Integer, primary_key=True)
    payment_plan_id = Column(Integer, ForeignKey('payment_plans.id'), nullable=False)
    installment_no = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    due_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment details (when paid)
    payment_date = Column(DateTime)
    payment_type = Column(SQLEnum(PaymentType))
    payment_reference = Column(String(100))  # Reference number, cheque number, etc.
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    payment_plan = relationship("PaymentPlan", back_populates="installments")
    
    @property
    def is_late(self):
        """Check if payment is late"""
        return (self.status == PaymentStatus.PENDING and 
                self.due_date < datetime.now().date())
    
    @property
    def days_late(self):
        """Calculate days late if payment is late"""
        if self.is_late:
            return (datetime.now().date() - self.due_date).days
        return 0

class PaymentNotification(Base):
    __tablename__ = 'payment_notifications'

    id = Column(Integer, primary_key=True)
    installment_id = Column(Integer, ForeignKey('installments.id'), nullable=False)
    type = Column(String(50), nullable=False)  # 'upcoming', 'late', etc.
    message = Column(Text, nullable=False)
    sent_date = Column(DateTime, default=datetime.now)
    is_read = Column(bool, default=False)
    
    # Relationships
    installment = relationship("Installment")