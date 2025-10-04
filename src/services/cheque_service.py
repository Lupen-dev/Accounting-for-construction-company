from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from models.cheque import (
    Cheque, ChequeTransaction, ChequeType, ChequeStatus, 
    ChequeDirection, ChequeTransactionType
)

class ChequeService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_cheque(self,
                     cheque_no: str,
                     type: ChequeType,
                     direction: ChequeDirection,
                     amount: float,
                     due_date: datetime,
                     bank_name: str,
                     bank_branch: str,
                     drawer_name: str,
                     customer_id: Optional[int] = None,
                     notes: Optional[str] = None) -> Cheque:
        """Create a new cheque record"""
        cheque = Cheque(
            cheque_no=cheque_no,
            type=type,
            direction=direction,
            amount=amount,
            due_date=due_date,
            bank_name=bank_name,
            bank_branch=bank_branch,
            drawer_name=drawer_name,
            customer_id=customer_id,
            notes=notes,
            status=ChequeStatus.PENDING
        )
        
        self.db.add(cheque)
        self.db.commit()
        self.db.refresh(cheque)
        
        # Create initial transaction record
        self._add_transaction(
            cheque.id,
            ChequeTransactionType.STATUS_CHANGE,
            None,
            ChequeStatus.PENDING,
            "Çek/Senet kaydedildi"
        )
        
        return cheque
    
    def update_cheque(self,
                     cheque_id: int,
                     cheque_no: Optional[str] = None,
                     bank_name: Optional[str] = None,
                     bank_branch: Optional[str] = None,
                     drawer_name: Optional[str] = None,
                     amount: Optional[float] = None,
                     due_date: Optional[datetime] = None,
                     notes: Optional[str] = None) -> Optional[Cheque]:
        """Update an existing cheque record"""
        cheque = self.get_cheque(cheque_id)
        if not cheque:
            return None
            
        if cheque_no:
            cheque.cheque_no = cheque_no
        if bank_name:
            cheque.bank_name = bank_name
        if bank_branch:
            cheque.bank_branch = bank_branch
        if drawer_name:
            cheque.drawer_name = drawer_name
        if amount:
            cheque.amount = amount
        if due_date:
            cheque.due_date = due_date
        if notes:
            cheque.notes = notes
        
        cheque.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(cheque)
        
        # Log the update
        self._add_transaction(
            cheque.id,
            ChequeTransactionType.DETAIL_UPDATED,
            None,
            None,
            "Çek/Senet bilgileri güncellendi"
        )
        
        return cheque
    
    def update_status(self,
                     cheque_id: int,
                     new_status: ChequeStatus,
                     description: Optional[str] = None) -> Optional[Cheque]:
        """Update the status of a cheque"""
        cheque = self.get_cheque(cheque_id)
        if not cheque:
            return None
        
        old_status = cheque.status
        cheque.status = new_status
        cheque.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(cheque)
        
        # Log the status change
        self._add_transaction(
            cheque.id,
            ChequeTransactionType.STATUS_CHANGE,
            old_status,
            new_status,
            description or f"Durum değiştirildi: {old_status.value} -> {new_status.value}"
        )
        
        return cheque
    
    def get_cheque(self, cheque_id: int) -> Optional[Cheque]:
        """Get a cheque by ID"""
        return self.db.query(Cheque).filter(Cheque.id == cheque_id).first()
    
    def get_cheques(self,
                   skip: int = 0,
                   limit: int = 100,
                   status: Optional[ChequeStatus] = None,
                   direction: Optional[ChequeDirection] = None) -> List[Cheque]:
        """Get all cheques with optional filtering"""
        query = self.db.query(Cheque)
        
        if status:
            query = query.filter(Cheque.status == status)
        if direction:
            query = query.filter(Cheque.direction == direction)
            
        return query.order_by(Cheque.due_date).offset(skip).limit(limit).all()
    
    def get_due_cheques(self, days: int = 7) -> List[Cheque]:
        """Get cheques due within specified days"""
        due_date = datetime.utcnow() + datetime.timedelta(days=days)
        return (self.db.query(Cheque)
                .filter(Cheque.status == ChequeStatus.PENDING)
                .filter(Cheque.due_date <= due_date)
                .order_by(Cheque.due_date)
                .all())
    
    def get_cheque_transactions(self,
                              cheque_id: int,
                              skip: int = 0,
                              limit: int = 100) -> List[ChequeTransaction]:
        """Get transaction history for a cheque"""
        return (self.db.query(ChequeTransaction)
                .filter(ChequeTransaction.cheque_id == cheque_id)
                .order_by(ChequeTransaction.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all())
    
    def _add_transaction(self,
                        cheque_id: int,
                        transaction_type: ChequeTransactionType,
                        old_status: Optional[ChequeStatus],
                        new_status: Optional[ChequeStatus],
                        description: str) -> ChequeTransaction:
        """Add a transaction record for a cheque"""
        transaction = ChequeTransaction(
            cheque_id=cheque_id,
            transaction_type=transaction_type,
            old_status=old_status,
            new_status=new_status,
            description=description
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction