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
        try:
            # Get input values
            customer_data = {
                key: input.text().strip()
                for key, input in self.inputs.items()
            }
            
            # Validate inputs
            if not all(customer_data.values()):
                QMessageBox.warning(
                    self,
                    get_text("common.warning"),
                    get_text("customer_module.fill_all_fields")
                )
                return
            
            # Get customer type
            type_index = self.type_combo.currentIndex()
            customer_type = [CustomerType.CUSTOMER, CustomerType.SUPPLIER, CustomerType.BOTH][type_index]
            
            # Create customer
            customer = self.customer_service.create_customer(
                name=customer_data["name"],
                tax_number=customer_data["tax_number"],
                phone=customer_data["phone"],
                address=customer_data["address"],
                type=customer_type
            )
            
            QMessageBox.information(
                self,
                get_text("common.success"),
                get_text("customer_module.customer_added")
            )
            
            self.clear_form()
            self.load_customers()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text("common.error"),
                str(e)
            )
    
    def update_customer(self):
        if not self.current_customer_id:
            QMessageBox.warning(
                self,
                get_text("common.warning"),
                get_text("customer_module.select_customer")
            )
            return
        
        try:
            # Get input values
            customer_data = {
                key: input.text().strip()
                for key, input in self.inputs.items()
            }
            
            # Validate inputs
            if not all(customer_data.values()):
                QMessageBox.warning(
                    self,
                    get_text("common.warning"),
                    get_text("customer_module.fill_all_fields")
                )
                return
            
            # Get customer type
            type_index = self.type_combo.currentIndex()
            customer_type = [CustomerType.CUSTOMER, CustomerType.SUPPLIER, CustomerType.BOTH][type_index]
            
            # Update customer
            customer = self.customer_service.update_customer(
                customer_id=self.current_customer_id,
                name=customer_data["name"],
                tax_number=customer_data["tax_number"],
                phone=customer_data["phone"],
                address=customer_data["address"],
                type=customer_type
            )
            
            if customer:
                QMessageBox.information(
                    self,
                    get_text("common.success"),
                    get_text("customer_module.customer_updated")
                )
                self.load_customers()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text("common.error"),
                str(e)
            )
    
    def delete_customer(self):
        if not self.current_customer_id:
            QMessageBox.warning(
                self,
                get_text("common.warning"),
                get_text("customer_module.select_customer")
            )
            return
        
        reply = QMessageBox.question(
            self,
            get_text("common.confirm"),
            get_text("customer_module.confirm_delete"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.customer_service.delete_customer(self.current_customer_id):
                    QMessageBox.information(
                        self,
                        get_text("common.success"),
                        get_text("customer_module.customer_deleted")
                    )
                    self.clear_form()
                    self.load_customers()
                    self.current_customer_id = None
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    get_text("common.error"),
                    str(e)
                )
    
    def clear_form(self):
        # Clear all input fields
        for input_field in self.inputs.values():
            input_field.clear()
        self.type_combo.setCurrentIndex(0)
        self.current_customer_id = None
        self.update_balance_display(0, 0)
        self.table.setRowCount(0)
    
    def load_customers(self):
        try:
            customers = self.customer_service.get_customers()
            self.table.setRowCount(0)
            
            for customer in customers:
                balance = self.customer_service.get_customer_balance(customer.id)
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(customer.name))
                self.table.setItem(row, 1, QTableWidgetItem(customer.tax_number))
                self.table.setItem(row, 2, QTableWidgetItem(f"{balance.total_debit:.2f}" if balance else "0.00"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{balance.total_credit:.2f}" if balance else "0.00"))
                self.table.setItem(row, 4, QTableWidgetItem(
                    f"{balance.total_credit - balance.total_debit:.2f}" if balance else "0.00"
                ))
        
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text("common.error"),
                str(e)
            )
    
    def add_transaction(self):
        if not self.current_customer_id:
            QMessageBox.warning(
                self,
                get_text("common.warning"),
                get_text("customer_module.select_customer")
            )
            return
        
        try:
            amount_text = self.amount_input.text().strip()
            description = self.description_input.text().strip()
            
            if not amount_text or not description:
                QMessageBox.warning(
                    self,
                    get_text("common.warning"),
                    get_text("customer_module.fill_transaction_fields")
                )
                return
            
            try:
                amount = float(amount_text)
            except ValueError:
                QMessageBox.warning(
                    self,
                    get_text("common.warning"),
                    get_text("customer_module.invalid_amount")
                )
                return
            
            transaction_type = TransactionType.DEBIT if self.transaction_type_combo.currentIndex() == 0 else TransactionType.CREDIT
            
            transaction = self.customer_service.add_transaction(
                customer_id=self.current_customer_id,
                type=transaction_type,
                amount=amount,
                description=description
            )
            
            if transaction:
                self.amount_input.clear()
                self.description_input.clear()
                self.load_transactions()
                self.load_customers()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text("common.error"),
                str(e)
            )
    
    def load_transactions(self):
        if not self.current_customer_id:
            return
        
        try:
            transactions = self.customer_service.get_customer_transactions(self.current_customer_id)
            balance = self.customer_service.get_customer_balance(self.current_customer_id)
            
            self.table.setRowCount(0)
            for transaction in transactions:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(transaction.date.strftime("%Y-%m-%d %H:%M")))
                self.table.setItem(row, 1, QTableWidgetItem(get_text(f"customer_module.{transaction.type.value}")))
                self.table.setItem(row, 2, QTableWidgetItem(transaction.description))
                
                if transaction.type == TransactionType.DEBIT:
                    self.table.setItem(row, 3, QTableWidgetItem(f"{transaction.amount:.2f}"))
                    self.table.setItem(row, 4, QTableWidgetItem(""))
                else:
                    self.table.setItem(row, 3, QTableWidgetItem(""))
                    self.table.setItem(row, 4, QTableWidgetItem(f"{transaction.amount:.2f}"))
            
            if balance:
                self.update_balance_display(balance.total_debit, balance.total_credit)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text("common.error"),
                str(e)
            )
    
    def update_balance_display(self, total_debit: float, total_credit: float):
        net_balance = total_credit - total_debit
        balance_text = f"Toplam Borç: {total_debit:.2f} | Toplam Alacak: {total_credit:.2f} | Net Bakiye: {net_balance:.2f}"
        self.balance_label.setText(balance_text)
        
        # Set color based on balance
        if net_balance < 0:
            self.balance_label.setStyleSheet("color: red;")
        elif net_balance > 0:
            self.balance_label.setStyleSheet("color: green;")
        else:
            self.balance_label.setStyleSheet("")