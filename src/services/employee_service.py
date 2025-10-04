from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from models.employee import Employee, AttendanceRecord, EmployeeStatus
from typing import List, Optional, Dict, Any

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def create_employee(self, data: Dict[str, Any]) -> Employee:
        employee = Employee(**data)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update_employee(self, employee_id: int, data: Dict[str, Any]) -> Optional[Employee]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            for key, value in data.items():
                setattr(employee, key, value)
            self.db.commit()
            self.db.refresh(employee)
        return employee

    def delete_employee(self, employee_id: int) -> bool:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            self.db.delete(employee)
            self.db.commit()
            return True
        return False

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_employee_by_no(self, employee_no: str) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.employee_no == employee_no).first()

    def get_all_employees(self, status: Optional[EmployeeStatus] = None) -> List[Employee]:
        query = self.db.query(Employee)
        if status:
            query = query.filter(Employee.status == status)
        return query.all()

    def record_attendance(self, data: Dict[str, Any]) -> AttendanceRecord:
        record = AttendanceRecord(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_attendance(self, record_id: int, data: Dict[str, Any]) -> Optional[AttendanceRecord]:
        record = self.db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if record:
            for key, value in data.items():
                setattr(record, key, value)
            self.db.commit()
            self.db.refresh(record)
        return record

    def get_attendance_record(self, record_id: int) -> Optional[AttendanceRecord]:
        return self.db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()

    def get_employee_attendance(self, 
                              employee_id: int, 
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> List[AttendanceRecord]:
        query = self.db.query(AttendanceRecord).filter(AttendanceRecord.employee_id == employee_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.date >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.date <= end_date)
            
        return query.order_by(AttendanceRecord.date.desc()).all()

    def calculate_payroll(self, 
                         employee_id: int, 
                         start_date: date,
                         end_date: date) -> Dict[str, float]:
        records = self.get_employee_attendance(employee_id, start_date, end_date)
        employee = self.get_employee(employee_id)
        
        if not employee:
            return {"regular_hours": 0, "overtime_hours": 0, "total_amount": 0}
            
        regular_hours = sum(record.regular_hours for record in records)
        overtime_hours = sum(record.overtime_hours_calculated for record in records)
        
        regular_amount = regular_hours * employee.hourly_rate
        overtime_amount = overtime_hours * (employee.hourly_rate * 1.5)  # 1.5x for overtime
        
        return {
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "regular_amount": regular_amount,
            "overtime_amount": overtime_amount,
            "total_amount": regular_amount + overtime_amount
        }