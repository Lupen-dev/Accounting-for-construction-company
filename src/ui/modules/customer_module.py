from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QPushButton, QLabel, QLineEdit, QGridLayout,
                             QMessageBox, QTableWidgetItem, QComboBox)
from PySide6.QtCore import Qt
from core.localization import get_text
from core.database import get_db
from services.customer_service import CustomerService
from models.customer import CustomerType, TransactionType
from datetime import datetime

class CustomerModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("customer_module.title"))
        self.setMinimumSize(1000, 700)
        
        # Initialize database service
        db = next(get_db())
        self.customer_service = CustomerService(db)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create form layout for customer details
        form_layout = QGridLayout()
        
        # Add form fields
        labels = [
            ("customer_module.customer_name", "name"),
            ("customer_module.tax_number", "tax_number"),
            ("customer_module.phone", "phone"),
            ("customer_module.address", "address")
        ]
        self.inputs = {}
        
        for i, (label_key, input_key) in enumerate(labels):
            form_layout.addWidget(QLabel(get_text(label_key)), i, 0)
            self.inputs[input_key] = QLineEdit()
            form_layout.addWidget(self.inputs[input_key], i, 1)
        
        # Add customer type combo box
        form_layout.addWidget(QLabel(get_text("customer_module.type")), len(labels), 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            get_text("customer_module.type_customer"),
            get_text("customer_module.type_supplier"),
            get_text("customer_module.type_both")
        ])
        form_layout.addWidget(self.type_combo, len(labels), 1)
        
        # Add transaction fields
        transaction_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(get_text("customer_module.amount"))
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(get_text("customer_module.description"))
        
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems([
            get_text("customer_module.debit"),
            get_text("customer_module.credit")
        ])
        
        transaction_layout.addWidget(self.amount_input)
        transaction_layout.addWidget(self.description_input)
        transaction_layout.addWidget(self.transaction_type_combo)
        
        # Add customer buttons
        customer_button_layout = QHBoxLayout()
        customer_buttons = [
            ("common.add", self.add_customer),
            ("common.update", self.update_customer),
            ("common.delete", self.delete_customer),
            ("common.clear", self.clear_form)
        ]
        
        for text_key, slot in customer_buttons:
            button = QPushButton(get_text(text_key))
            button.clicked.connect(slot)
            customer_button_layout.addWidget(button)
            
        # Add transaction button
        transaction_button = QPushButton(get_text("customer_module.add_transaction"))
        transaction_button.clicked.connect(self.add_transaction)
        transaction_layout.addWidget(transaction_button)
        
        # Add table widget for transactions
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            get_text("common.date"),
            get_text("customer_module.transaction_type"),
            get_text("common.description"),
            get_text("customer_module.debit"),
            get_text("customer_module.credit")
        ])
        
        # Add customer info summary
        self.balance_label = QLabel()
        self.update_balance_display(0, 0)
        
        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(customer_button_layout)
        main_layout.addWidget(self.balance_label)
        main_layout.addLayout(transaction_layout)
        main_layout.addWidget(self.table)
        
        # Initialize state
        self.current_customer_id = None
        self.load_customers()
        
        # Set modern style
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
            QLineEdit {
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
        """)
    
    def add_customer(self):
        # TODO: Implement customer addition
        pass
    
    def update_customer(self):
        # TODO: Implement customer update
        pass
    
    def delete_customer(self):
        # TODO: Implement customer deletion
        pass
    
    def clear_form(self):
        # Clear all input fields
        for input_field in self.inputs.values():
            input_field.clear()