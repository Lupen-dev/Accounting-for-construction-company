from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import enum

class EmployeeStatus(enum.Enum):
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    TERMINATED = "Terminated"

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    employee_no = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    hire_date = Column(Date, nullable=False)
    position = Column(String(100))
    department = Column(String(100))
    hourly_rate = Column(Float, nullable=False)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="employee")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    overtime_hours = Column(Float, default=0.0)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

    @property
    def total_hours(self):
        if self.time_in and self.time_out:
            duration = self.time_out - self.time_in
            return duration.total_seconds() / 3600  # Convert to hours
        return 0.0

    @property
    def regular_hours(self):
        return min(self.total_hours, 8.0) if self.total_hours > 0 else 0.0

    @property
    def overtime_hours_calculated(self):
        return max(self.total_hours - 8.0, 0.0) if self.total_hours > 0 else 0.0