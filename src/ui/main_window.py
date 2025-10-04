from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from core.localization import get_text
from ui.modules.customer_module import CustomerModule
from ui.modules.cheque_module import ChequeModule
from ui.modules.employee_module import EmployeeModule
from ui.modules.property_module import PropertyModule
from ui.modules.payment_module import PaymentModule
from ui.modules.trade_module import TradeModule
from ui.modules.reports_module import ReportsModule
from ui.modules.settings_module import SettingsModule

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("app_name"))
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu layout
        menu_layout = QHBoxLayout()
        
        # Create module buttons with modern style
        self.create_module_buttons(menu_layout)
        
        # Add layouts to main layout
        main_layout.addLayout(menu_layout)
        main_layout.addStretch()
        
        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                min-width: 120px;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

    def create_module_buttons(self, layout):
        modules = [
            ("menu.customers", self.open_customer_module),
            ("menu.cheques", self.open_cheque_module),
            ("menu.employees", self.open_employee_module),
            ("menu.properties", self.open_property_module),
            ("menu.payments", self.open_payment_module),
            ("menu.trade", self.open_trade_module),
            ("menu.reports", self.open_reports_module),
            ("menu.settings", self.open_settings_module)
        ]
        
        for text_key, slot in modules:
            button = QPushButton(get_text(text_key))
            button.clicked.connect(slot)
            layout.addWidget(button)
        
        layout.addStretch()

    def open_customer_module(self):
        self.customer_module = CustomerModule()
        self.customer_module.show()

    def open_cheque_module(self):
        self.cheque_module = ChequeModule()
        self.cheque_module.show()

    def open_employee_module(self):
        self.employee_module = EmployeeModule()
        self.employee_module.show()

    def open_property_module(self):
        self.property_module = PropertyModule()
        self.property_module.show()

    def open_payment_module(self):
        self.payment_module = PaymentModule()
        self.payment_module.show()

    def open_trade_module(self):
        self.trade_module = TradeModule()
        self.trade_module.show()

    def open_reports_module(self):
        self.reports_module = ReportsModule()
        self.reports_module.show()

    def open_settings_module(self):
        self.settings_module = SettingsModule()
        self.settings_module.show()