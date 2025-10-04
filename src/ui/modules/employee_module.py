from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QDateEdit, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
    QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDate, QDateTime
from core.localization import get_text
from core.database import get_db
from services.employee_service import EmployeeService
from models.employee import Employee, EmployeeStatus, AttendanceRecord
from datetime import datetime, date

class EmployeeModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("employee_module.title"))
        self.setMinimumSize(1200, 800)
        
        # Initialize database service
        db = next(get_db())
        self.employee_service = EmployeeService(db)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Create tabs
        employee_tab = QWidget()
        attendance_tab = QWidget()
        payroll_tab = QWidget()
        
        tabs.addTab(employee_tab, get_text("employee_module.tab_employees"))
        tabs.addTab(attendance_tab, get_text("employee_module.tab_attendance"))
        tabs.addTab(payroll_tab, get_text("employee_module.tab_payroll"))
        
        # Setup each tab
        self._setup_employee_tab(employee_tab)
        self._setup_attendance_tab(attendance_tab)
        self._setup_payroll_tab(payroll_tab)
        
        # Set style
        self._set_style()
        
        # Load initial data
        self.load_employees()

    def _set_style(self):
        """Set the modern style for the window"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                min-width: 100px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit, QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: none;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
        """)

    def _setup_employee_tab(self, tab):
        """Setup the employees management tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for employee details
        form = QGridLayout()
        
        # Employee number
        form.addWidget(QLabel(get_text("employee_module.employee_no")), 0, 0)
        self.emp_no_input = QLineEdit()
        form.addWidget(self.emp_no_input, 0, 1)
        
        # First name
        form.addWidget(QLabel(get_text("employee_module.first_name")), 0, 2)
        self.first_name_input = QLineEdit()
        form.addWidget(self.first_name_input, 0, 3)
        
        # Last name
        form.addWidget(QLabel(get_text("employee_module.last_name")), 0, 4)
        self.last_name_input = QLineEdit()
        form.addWidget(self.last_name_input, 0, 5)
        
        # Phone
        form.addWidget(QLabel(get_text("employee_module.phone")), 1, 0)
        self.phone_input = QLineEdit()
        form.addWidget(self.phone_input, 1, 1)
        
        # Email
        form.addWidget(QLabel(get_text("employee_module.email")), 1, 2)
        self.email_input = QLineEdit()
        form.addWidget(self.email_input, 1, 3)
        
        # Hire date
        form.addWidget(QLabel(get_text("employee_module.hire_date")), 1, 4)
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        form.addWidget(self.hire_date_input, 1, 5)
        
        # Position
        form.addWidget(QLabel(get_text("employee_module.position")), 2, 0)
        self.position_input = QLineEdit()
        form.addWidget(self.position_input, 2, 1)
        
        # Department
        form.addWidget(QLabel(get_text("employee_module.department")), 2, 2)
        self.department_input = QLineEdit()
        form.addWidget(self.department_input, 2, 3)
        
        # Hourly rate
        form.addWidget(QLabel(get_text("employee_module.hourly_rate")), 2, 4)
        self.hourly_rate_input = QDoubleSpinBox()
        self.hourly_rate_input.setRange(0, 999999.99)
        self.hourly_rate_input.setDecimals(2)
        form.addWidget(self.hourly_rate_input, 2, 5)
        
        # Status
        form.addWidget(QLabel(get_text("employee_module.status")), 3, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems([status.value for status in EmployeeStatus])
        form.addWidget(self.status_combo, 3, 1)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(get_text("common.save"))
        self.save_btn.clicked.connect(self.save_employee)
        button_layout.addWidget(self.save_btn)
        
        clear_btn = QPushButton(get_text("common.clear"))
        clear_btn.clicked.connect(self.clear_employee_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(9)
        self.employee_table.setHorizontalHeaderLabels([
            get_text("employee_module.employee_no"),
            get_text("employee_module.first_name"),
            get_text("employee_module.last_name"),
            get_text("employee_module.phone"),
            get_text("employee_module.email"),
            get_text("employee_module.hire_date"),
            get_text("employee_module.position"),
            get_text("employee_module.hourly_rate"),
            get_text("employee_module.status")
        ])
        layout.addWidget(self.employee_table)

    def _setup_attendance_tab(self, tab):
        """Setup the attendance tracking tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for attendance
        form = QGridLayout()
        
        # Employee selector
        form.addWidget(QLabel(get_text("employee_module.select_employee")), 0, 0)
        self.attendance_emp_combo = QComboBox()
        form.addWidget(self.attendance_emp_combo, 0, 1)
        
        # Date
        form.addWidget(QLabel(get_text("employee_module.date")), 0, 2)
        self.attendance_date = QDateEdit()
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDate(QDate.currentDate())
        form.addWidget(self.attendance_date, 0, 3)
        
        # Time in
        form.addWidget(QLabel(get_text("employee_module.time_in")), 1, 0)
        self.time_in = QDateEdit()
        self.time_in.setCalendarPopup(True)
        self.time_in.setDateTime(QDateTime.currentDateTime())
        form.addWidget(self.time_in, 1, 1)
        
        # Time out
        form.addWidget(QLabel(get_text("employee_module.time_out")), 1, 2)
        self.time_out = QDateEdit()
        self.time_out.setCalendarPopup(True)
        self.time_out.setDateTime(QDateTime.currentDateTime())
        form.addWidget(self.time_out, 1, 3)
        
        # Notes
        form.addWidget(QLabel(get_text("employee_module.notes")), 2, 0)
        self.attendance_notes = QLineEdit()
        form.addWidget(self.attendance_notes, 2, 1, 1, 3)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_attendance_btn = QPushButton(get_text("employee_module.record_attendance"))
        save_attendance_btn.clicked.connect(self.save_attendance)
        button_layout.addWidget(save_attendance_btn)
        
        clear_attendance_btn = QPushButton(get_text("common.clear"))
        clear_attendance_btn.clicked.connect(self.clear_attendance_form)
        button_layout.addWidget(clear_attendance_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels([
            get_text("employee_module.employee_name"),
            get_text("employee_module.date"),
            get_text("employee_module.time_in"),
            get_text("employee_module.time_out"),
            get_text("employee_module.total_hours"),
            get_text("employee_module.notes")
        ])
        layout.addWidget(self.attendance_table)

    def _setup_payroll_tab(self, tab):
        """Setup the payroll calculation tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for payroll
        form = QGridLayout()
        
        # Employee selector
        form.addWidget(QLabel(get_text("employee_module.select_employee")), 0, 0)
        self.payroll_emp_combo = QComboBox()
        form.addWidget(self.payroll_emp_combo, 0, 1)
        
        # Date range
        form.addWidget(QLabel(get_text("employee_module.start_date")), 1, 0)
        self.payroll_start_date = QDateEdit()
        self.payroll_start_date.setCalendarPopup(True)
        form.addWidget(self.payroll_start_date, 1, 1)
        
        form.addWidget(QLabel(get_text("employee_module.end_date")), 1, 2)
        self.payroll_end_date = QDateEdit()
        self.payroll_end_date.setCalendarPopup(True)
        form.addWidget(self.payroll_end_date, 1, 3)
        
        layout.addLayout(form)
        
        # Calculate button
        calc_btn = QPushButton(get_text("employee_module.calculate_payroll"))
        calc_btn.clicked.connect(self.calculate_payroll)
        layout.addWidget(calc_btn)
        
        # Results table
        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(6)
        self.payroll_table.setHorizontalHeaderLabels([
            get_text("employee_module.employee_name"),
            get_text("employee_module.regular_hours"),
            get_text("employee_module.overtime_hours"),
            get_text("employee_module.regular_amount"),
            get_text("employee_module.overtime_amount"),
            get_text("employee_module.total_amount")
        ])
        layout.addWidget(self.payroll_table)

    def load_employees(self):
        """Load employees into the table and combo boxes"""
        self.employee_table.setRowCount(0)
        employees = self.employee_service.get_all_employees()
        
        # Clear and reload combo boxes
        self.attendance_emp_combo.clear()
        self.payroll_emp_combo.clear()
        
        for row, employee in enumerate(employees):
            self.employee_table.insertRow(row)
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee.employee_no))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee.first_name))
            self.employee_table.setItem(row, 2, QTableWidgetItem(employee.last_name))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee.phone))
            self.employee_table.setItem(row, 4, QTableWidgetItem(employee.email))
            self.employee_table.setItem(row, 5, QTableWidgetItem(str(employee.hire_date)))
            self.employee_table.setItem(row, 6, QTableWidgetItem(employee.position))
            self.employee_table.setItem(row, 7, QTableWidgetItem(f"{employee.hourly_rate:.2f}"))
            self.employee_table.setItem(row, 8, QTableWidgetItem(employee.status.value))
            
            # Add to combo boxes
            self.attendance_emp_combo.addItem(employee.full_name, employee.id)
            self.payroll_emp_combo.addItem(employee.full_name, employee.id)
        
        self.employee_table.resizeColumnsToContents()

    def clear_employee_form(self):
        """Clear all employee form fields"""
        self.emp_no_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.hire_date_input.setDate(QDate.currentDate())
        self.position_input.clear()
        self.department_input.clear()
        self.hourly_rate_input.setValue(0)
        self.status_combo.setCurrentIndex(0)

    def clear_attendance_form(self):
        """Clear all attendance form fields"""
        self.attendance_date.setDate(QDate.currentDate())
        self.time_in.setDateTime(QDateTime.currentDateTime())
        self.time_out.setDateTime(QDateTime.currentDateTime())
        self.attendance_notes.clear()
        if self.attendance_emp_combo.count() > 0:
            self.attendance_emp_combo.setCurrentIndex(0)

    def save_employee(self):
        """Save or update employee information"""
        try:
            employee_data = {
                'employee_no': self.emp_no_input.text(),
                'first_name': self.first_name_input.text(),
                'last_name': self.last_name_input.text(),
                'phone': self.phone_input.text(),
                'email': self.email_input.text(),
                'hire_date': self.hire_date_input.date().toPython(),
                'position': self.position_input.text(),
                'department': self.department_input.text(),
                'hourly_rate': self.hourly_rate_input.value(),
                'status': EmployeeStatus(self.status_combo.currentText())
            }

            if not all([employee_data['employee_no'], employee_data['first_name'],
                       employee_data['last_name'], employee_data['hourly_rate']]):
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("common.fill_required_fields"))
                return

            self.employee_service.create_employee(employee_data)
            self.clear_employee_form()
            self.load_employees()
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("common.save_success"))

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))

    def save_attendance(self):
        """Save attendance record"""
        try:
            employee_id = self.attendance_emp_combo.currentData()
            if not employee_id:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("employee_module.select_employee_warning"))
                return

            attendance_data = {
                'employee_id': employee_id,
                'date': self.attendance_date.date().toPython(),
                'time_in': self.time_in.dateTime().toPython(),
                'time_out': self.time_out.dateTime().toPython(),
                'notes': self.attendance_notes.text()
            }

            if attendance_data['time_out'] <= attendance_data['time_in']:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("employee_module.invalid_time_range"))
                return

            self.employee_service.record_attendance(attendance_data)
            self.clear_attendance_form()
            self.load_attendance_records()
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("common.save_success"))

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))

    def load_attendance_records(self):
        """Load attendance records for the selected employee"""
        employee_id = self.attendance_emp_combo.currentData()
        if not employee_id:
            return

        self.attendance_table.setRowCount(0)
        records = self.employee_service.get_employee_attendance(employee_id)
        
        for row, record in enumerate(records):
            self.attendance_table.insertRow(row)
            self.attendance_table.setItem(row, 0, QTableWidgetItem(record.employee.full_name))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(str(record.date)))
            self.attendance_table.setItem(row, 2, QTableWidgetItem(record.time_in.strftime("%H:%M")))
            self.attendance_table.setItem(row, 3, QTableWidgetItem(record.time_out.strftime("%H:%M")))
            self.attendance_table.setItem(row, 4, QTableWidgetItem(f"{record.total_hours:.2f}"))
            self.attendance_table.setItem(row, 5, QTableWidgetItem(record.notes))
        
        self.attendance_table.resizeColumnsToContents()

    def calculate_payroll(self):
        """Calculate and display payroll for selected employee and date range"""
        try:
            employee_id = self.payroll_emp_combo.currentData()
            if not employee_id:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("employee_module.select_employee_warning"))
                return

            start_date = self.payroll_start_date.date().toPython()
            end_date = self.payroll_end_date.date().toPython()
            
            if end_date < start_date:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("employee_module.invalid_date_range"))
                return

            result = self.employee_service.calculate_payroll(employee_id, start_date, end_date)
            employee = self.employee_service.get_employee(employee_id)
            
            self.payroll_table.setRowCount(1)
            self.payroll_table.setItem(0, 0, QTableWidgetItem(employee.full_name))
            self.payroll_table.setItem(0, 1, QTableWidgetItem(f"{result['regular_hours']:.2f}"))
            self.payroll_table.setItem(0, 2, QTableWidgetItem(f"{result['overtime_hours']:.2f}"))
            self.payroll_table.setItem(0, 3, QTableWidgetItem(f"{result['regular_amount']:.2f}"))
            self.payroll_table.setItem(0, 4, QTableWidgetItem(f"{result['overtime_amount']:.2f}"))
            self.payroll_table.setItem(0, 5, QTableWidgetItem(f"{result['total_amount']:.2f}"))
            
            self.payroll_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))
        self.setCentralWidget(central_widget)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)