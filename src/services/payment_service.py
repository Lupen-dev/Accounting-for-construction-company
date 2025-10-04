from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.payment import PaymentPlan, Installment, PaymentNotification
from models.payment import PaymentStatus, PaymentType
from typing import List, Optional, Dict, Any

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment_plan(self, data: Dict[str, Any]) -> PaymentPlan:
        """Create a new payment plan with installments"""
        # Create payment plan
        payment_plan = PaymentPlan(**{
            k: v for k, v in data.items() 
            if k not in ['installments']
        })
        self.db.add(payment_plan)
        self.db.flush()  # Get ID without committing
        
        # Calculate and create installments
        amount_per_installment = (payment_plan.total_amount - payment_plan.down_payment) / payment_plan.number_of_installments
        
        # If there's interest, calculate the amount with interest
        if payment_plan.interest_rate > 0:
            monthly_rate = payment_plan.interest_rate / 12 / 100
            # Calculate monthly payment with interest (PMT formula)
            amount_per_installment = (payment_plan.total_amount - payment_plan.down_payment) * \
                (monthly_rate * (1 + monthly_rate) ** payment_plan.number_of_installments) / \
                ((1 + monthly_rate) ** payment_plan.number_of_installments - 1)
        
        # Create installments
        start_date = payment_plan.start_date
        for i in range(payment_plan.number_of_installments):
            # Calculate due date (same day each month)
            if start_date.day != payment_plan.payment_day:
                # Adjust to specified payment day
                due_date = start_date.replace(day=payment_plan.payment_day)
                if payment_plan.payment_day < start_date.day:
                    # If payment day is earlier in month, move to next month
                    due_date = self._add_months(due_date, 1)
            else:
                due_date = start_date
            
            installment = Installment(
                payment_plan_id=payment_plan.id,
                installment_no=i + 1,
                due_date=self._add_months(due_date, i),
                amount=round(amount_per_installment, 2),
                status=PaymentStatus.PENDING
            )
            self.db.add(installment)
        
        self.db.commit()
        self.db.refresh(payment_plan)
        return payment_plan
    
    def update_payment_plan(self, plan_id: int, data: Dict[str, Any]) -> Optional[PaymentPlan]:
        """Update payment plan details"""
        plan = self.db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
        if plan:
            # Only allow updating certain fields if no payments have been made
            if not any(i.status == PaymentStatus.PAID for i in plan.installments):
                for key, value in data.items():
                    setattr(plan, key, value)
                self.db.commit()
                self.db.refresh(plan)
            else:
                # If payments exist, only allow updating title and description
                plan.title = data.get('title', plan.title)
                plan.description = data.get('description', plan.description)
                self.db.commit()
                self.db.refresh(plan)
        return plan
    
    def get_payment_plan(self, plan_id: int) -> Optional[PaymentPlan]:
        """Get payment plan by ID"""
        return self.db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
    
    def get_customer_payment_plans(self, customer_id: int) -> List[PaymentPlan]:
        """Get all payment plans for a customer"""
        return self.db.query(PaymentPlan)\
                     .filter(PaymentPlan.customer_id == customer_id)\
                     .all()
    
    def record_payment(self, installment_id: int, data: Dict[str, Any]) -> Optional[Installment]:
        """Record a payment for an installment"""
        installment = self.db.query(Installment).filter(Installment.id == installment_id).first()
        if installment:
            installment.status = PaymentStatus.PAID
            installment.payment_date = datetime.now()
            installment.payment_type = data['payment_type']
            installment.payment_reference = data.get('payment_reference')
            installment.notes = data.get('notes')
            
            self.db.commit()
            self.db.refresh(installment)
        return installment
    
    def cancel_payment(self, installment_id: int, notes: Optional[str] = None) -> Optional[Installment]:
        """Cancel a payment for an installment"""
        installment = self.db.query(Installment).filter(Installment.id == installment_id).first()
        if installment:
            installment.status = PaymentStatus.CANCELLED
            if notes:
                installment.notes = notes
            self.db.commit()
            self.db.refresh(installment)
        return installment
    
    def get_late_payments(self) -> List[Installment]:
        """Get all late payments"""
        today = datetime.now().date()
        return self.db.query(Installment)\
                     .filter(and_(
                         Installment.status == PaymentStatus.PENDING,
                         Installment.due_date < today
                     ))\
                     .all()
    
    def get_upcoming_payments(self, days: int = 7) -> List[Installment]:
        """Get payments due in the next X days"""
        today = datetime.now().date()
        future = today + timedelta(days=days)
        return self.db.query(Installment)\
                     .filter(and_(
                         Installment.status == PaymentStatus.PENDING,
                         Installment.due_date.between(today, future)
                     ))\
                     .all()
    
    def create_notification(self, installment_id: int, type: str, message: str) -> PaymentNotification:
        """Create a payment notification"""
        notification = PaymentNotification(
            installment_id=installment_id,
            type=type,
            message=message
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_unread_notifications(self) -> List[PaymentNotification]:
        """Get all unread notifications"""
        return self.db.query(PaymentNotification)\
                     .filter(PaymentNotification.is_read == False)\
                     .all()
    
    def mark_notification_read(self, notification_id: int) -> Optional[PaymentNotification]:
        """Mark a notification as read"""
        notification = self.db.query(PaymentNotification)\
                            .filter(PaymentNotification.id == notification_id)\
                            .first()
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def _add_months(self, source_date: date, months: int) -> date:
        """Add months to a date, handling month end dates correctly"""
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, [31,
                                  29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
                                  else 28,
                                  31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    
    def calculate_payment_summary(self, plan_id: int) -> Dict[str, Any]:
        """Calculate payment summary for a plan"""
        plan = self.get_payment_plan(plan_id)
        if not plan:
            return {}
            
        total_paid = sum(i.amount for i in plan.installments if i.status == PaymentStatus.PAID)
        total_pending = sum(i.amount for i in plan.installments if i.status == PaymentStatus.PENDING)
        late_payments = [i for i in plan.installments if i.is_late]
        
        return {
            'total_amount': plan.total_amount,
            'down_payment': plan.down_payment,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'number_of_installments': plan.number_of_installments,
            'completed_installments': len([i for i in plan.installments if i.status == PaymentStatus.PAID]),
            'pending_installments': len([i for i in plan.installments if i.status == PaymentStatus.PENDING]),
            'late_payments': len(late_payments),
            'total_late_amount': sum(i.amount for i in late_payments),
            'is_completed': plan.is_completed
        }