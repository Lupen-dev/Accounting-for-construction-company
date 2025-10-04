from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QPushButton, QLabel, QLineEdit, QGridLayout,
    QMessageBox, QTableWidgetItem, QComboBox, QDateEdit, QInputDialog, QDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from core.localization import get_text
from core.database import get_db
from services.cheque_service import ChequeService
from models.cheque import ChequeType, ChequeStatus, ChequeDirection
from datetime import datetime

class ChequeModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("cheque_module.title"))
        self.setMinimumSize(1000, 700)
        
        # Initialize database service
        db = next(get_db())
        self.cheque_service = ChequeService(db)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create form layout for cheque details
        form_layout = QGridLayout()
        
        # Add form fields
        self._setup_form_fields(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        self._setup_buttons(button_layout)
        
        # Add status filter
        filter_layout = QHBoxLayout()
        self._setup_filters(filter_layout)
        
        # Add table widget for cheques
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            get_text("cheque_module.cheque_no"),
            get_text("cheque_module.type"),
            get_text("cheque_module.direction"),
            get_text("cheque_module.amount"),
            get_text("cheque_module.due_date"),
            get_text("cheque_module.bank"),
            get_text("cheque_module.drawer"),
            get_text("cheque_module.status")
        ])
        
        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        
        # Initialize state
        self.current_cheque_id = None
        
        # Set modern style
        self._set_style()
        
        # Load initial data
        self.load_cheques()

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
            QLineEdit, QDateEdit, QComboBox {
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

    def _setup_form_fields(self, layout):
        """Setup the input fields for cheque details"""
        # Cheque Number
        layout.addWidget(QLabel(get_text("cheque_module.cheque_no")), 0, 0)
        self.cheque_no_input = QLineEdit()
        layout.addWidget(self.cheque_no_input, 0, 1)

        # Type
        layout.addWidget(QLabel(get_text("cheque_module.type")), 0, 2)
        self.type_combo = QComboBox()
        self.type_combo.addItems([ct.value for ct in ChequeType])
        layout.addWidget(self.type_combo, 0, 3)

        # Direction
        layout.addWidget(QLabel(get_text("cheque_module.direction")), 0, 4)
        self.direction_combo = QComboBox()
        self.direction_combo.addItems([cd.value for cd in ChequeDirection])
        layout.addWidget(self.direction_combo, 0, 5)

        # Amount
        layout.addWidget(QLabel(get_text("cheque_module.amount")), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        layout.addWidget(self.amount_input, 1, 1)

        # Due Date
        layout.addWidget(QLabel(get_text("cheque_module.due_date")), 1, 2)
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.due_date_input, 1, 3)

        # Bank
        layout.addWidget(QLabel(get_text("cheque_module.bank")), 1, 4)
        self.bank_input = QLineEdit()
        layout.addWidget(self.bank_input, 1, 5)

        # Drawer
        layout.addWidget(QLabel(get_text("cheque_module.drawer")), 2, 0)
        self.drawer_input = QLineEdit()
        layout.addWidget(self.drawer_input, 2, 1)

    def _setup_buttons(self, layout):
        """Setup action buttons"""
        # Save button
        self.save_btn = QPushButton(get_text("common.save"))
        self.save_btn.clicked.connect(self.save_cheque)
        layout.addWidget(self.save_btn)

        # Clear button
        clear_btn = QPushButton(get_text("common.clear"))
        clear_btn.clicked.connect(self.clear_form)
        layout.addWidget(clear_btn)

        # Change Status button
        change_status_btn = QPushButton(get_text("cheque_module.change_status"))
        change_status_btn.clicked.connect(self.change_status)
        layout.addWidget(change_status_btn)

    def _setup_filters(self, layout):
        """Setup status filter"""
        layout.addWidget(QLabel(get_text("cheque_module.filter_status")))
        self.status_filter = QComboBox()
        self.status_filter.addItem(get_text("common.all"))
        self.status_filter.addItems([cs.value for cs in ChequeStatus])
        self.status_filter.currentTextChanged.connect(self.load_cheques)
        layout.addWidget(self.status_filter)

    def load_cheques(self):
        """Load cheques into the table"""
        self.table.setRowCount(0)
        filter_status = self.status_filter.currentText()
        
        cheques = self.cheque_service.get_all()
        if filter_status != get_text("common.all"):
            cheques = [c for c in cheques if c.status == filter_status]

        for row, cheque in enumerate(cheques):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(cheque.cheque_no))
            self.table.setItem(row, 1, QTableWidgetItem(cheque.type))
            self.table.setItem(row, 2, QTableWidgetItem(cheque.direction))
            self.table.setItem(row, 3, QTableWidgetItem(f"{cheque.amount:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(cheque.due_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 5, QTableWidgetItem(cheque.bank))
            self.table.setItem(row, 6, QTableWidgetItem(cheque.drawer))
            self.table.setItem(row, 7, QTableWidgetItem(cheque.status))

            # Color rows based on status
            color = self._get_status_color(cheque.status)
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                item.setBackground(color)

        self.table.resizeColumnsToContents()

    def _get_status_color(self, status):
        """Get background color for cheque status"""
        colors = {
            ChequeStatus.PENDING.value: QColor("#FFFFFF"),  # White
            ChequeStatus.PAID.value: QColor("#C8E6C9"),    # Light Green
            ChequeStatus.BOUNCED.value: QColor("#FFCDD2"), # Light Red
            ChequeStatus.CANCELLED.value: QColor("#CFD8DC") # Light Grey
        }
        return colors.get(status, QColor("#FFFFFF"))

    def clear_form(self):
        """Clear all form fields"""
        self.current_cheque_id = None
        self.cheque_no_input.clear()
        self.amount_input.clear()
        self.bank_input.clear()
        self.drawer_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.direction_combo.setCurrentIndex(0)
        self.due_date_input.setDate(QDate.currentDate())

    def save_cheque(self):
        """Save or update a cheque"""
        try:
            cheque_data = {
                'cheque_no': self.cheque_no_input.text(),
                'type': self.type_combo.currentText(),
                'direction': self.direction_combo.currentText(),
                'amount': float(self.amount_input.text()),
                'due_date': self.due_date_input.date().toPython(),
                'bank': self.bank_input.text(),
                'drawer': self.drawer_input.text(),
                'status': ChequeStatus.PENDING.value
            }

            if not all([cheque_data['cheque_no'], cheque_data['amount'], 
                       cheque_data['bank'], cheque_data['drawer']]):
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("common.fill_required_fields"))
                return

            if self.current_cheque_id:
                self.cheque_service.update(self.current_cheque_id, cheque_data)
            else:
                self.cheque_service.create(cheque_data)

            self.clear_form()
            self.load_cheques()
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("common.save_success"))

        except ValueError as e:
            QMessageBox.warning(self, get_text("common.error"),
                              get_text("common.invalid_amount"))
        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"),
                               str(e))

    def change_status(self):
        """Change the status of the selected cheque"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, get_text("common.warning"),
                              get_text("cheque_module.select_cheque"))
            return

        row = selected_items[0].row()
        cheque_no = self.table.item(row, 0).text()
        cheque = next((c for c in self.cheque_service.get_all() 
                      if c.cheque_no == cheque_no), None)
        
        if not cheque:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(get_text("cheque_module.change_status"))
        layout = QVBoxLayout(dialog)

        status_combo = QComboBox()
        status_combo.addItems([cs.value for cs in ChequeStatus])
        status_combo.setCurrentText(cheque.status)
        layout.addWidget(status_combo)

        buttons = QHBoxLayout()
        ok_button = QPushButton(get_text("common.ok"))
        cancel_button = QPushButton(get_text("common.cancel"))
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            new_status = status_combo.currentText()
            self.cheque_service.update(cheque.id, {'status': new_status})
            self.load_cheques()