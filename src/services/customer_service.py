from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from models.customer import Customer, Transaction, CustomerBalance, CustomerType, TransactionType

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, 
                       name: str, 
                       tax_number: str, 
                       phone: str, 
                       address: str, 
                       type: CustomerType) -> Customer:
        """Create a new customer record"""
        customer = Customer(
            name=name,
            tax_number=tax_number,
            phone=phone,
            address=address,
            type=type
        )
        
        # Create initial balance record
        balance = CustomerBalance(customer=customer)
        
        self.db.add(customer)
        self.db.add(balance)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def update_customer(self,
                       customer_id: int,
                       name: Optional[str] = None,
                       tax_number: Optional[str] = None,
                       phone: Optional[str] = None,
                       address: Optional[str] = None,
                       type: Optional[CustomerType] = None) -> Optional[Customer]:
        """Update an existing customer record"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            if name:
                customer.name = name
            if tax_number:
                customer.tax_number = tax_number
            if phone:
                customer.phone = phone
            if address:
                customer.address = address
            if type:
                customer.type = type
            
            customer.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer record"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            # Delete related records
            self.db.query(CustomerBalance).filter(CustomerBalance.customer_id == customer_id).delete()
            self.db.query(Transaction).filter(Transaction.customer_id == customer_id).delete()
            
            self.db.delete(customer)
            self.db.commit()
            return True
        return False
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID"""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers with pagination"""
        return self.db.query(Customer).offset(skip).limit(limit).all()
    
    def add_transaction(self,
                       customer_id: int,
                       type: TransactionType,
                       amount: float,
                       description: str) -> Optional[Transaction]:
        """Add a new transaction for a customer"""
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        
        transaction = Transaction(
            customer_id=customer_id,
            type=type,
            amount=amount,
            description=description,
            date=datetime.utcnow()
        )
        
        # Update customer balance
        balance = customer.balance
        if type == TransactionType.DEBIT:
            balance.total_debit += amount
        else:
            balance.total_credit += amount
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_customer_transactions(self,
                                customer_id: int,
                                skip: int = 0,
                                limit: int = 100) -> List[Transaction]:
        """Get all transactions for a customer with pagination"""
        return (self.db.query(Transaction)
                .filter(Transaction.customer_id == customer_id)
                .order_by(Transaction.date.desc())
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_customer_balance(self, customer_id: int) -> Optional[CustomerBalance]:
        """Get current balance for a customer"""
        return (self.db.query(CustomerBalance)
                .filter(CustomerBalance.customer_id == customer_id)
                .first())