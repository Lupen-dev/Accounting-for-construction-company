from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QTabWidget,
    QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from core.localization import get_text
from core.database import get_db
from services.property_service import PropertyService
from models.property import (
    Property, Deed, PropertyDocument,
    PropertyType, PropertyStatus, OwnershipType, DocumentType
)
import json
from datetime import datetime
import os

class PropertyModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text("property_module.title"))
        self.setMinimumSize(1200, 800)
        
        # Initialize database service
        db = next(get_db())
        self.property_service = PropertyService(db)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Create tabs
        property_tab = QWidget()
        deed_tab = QWidget()
        document_tab = QWidget()
        
        tabs.addTab(property_tab, get_text("property_module.tab_properties"))
        tabs.addTab(deed_tab, get_text("property_module.tab_deeds"))
        tabs.addTab(document_tab, get_text("property_module.tab_documents"))
        
        # Setup each tab
        self._setup_property_tab(property_tab)
        self._setup_deed_tab(deed_tab)
        self._setup_document_tab(document_tab)
        
        # Set style
        self._set_style()
        
        # Load initial data
        self.load_properties()

    def _set_style(self):
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
            QLineEdit, QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
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

    def _setup_property_tab(self, tab):
        """Setup the property management tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for property details
        form = QGridLayout()
        
        # Property number
        form.addWidget(QLabel(get_text("property_module.property_no")), 0, 0)
        self.property_no_input = QLineEdit()
        form.addWidget(self.property_no_input, 0, 1)
        
        # Title
        form.addWidget(QLabel(get_text("property_module.title")), 0, 2)
        self.title_input = QLineEdit()
        form.addWidget(self.title_input, 0, 3)
        
        # Type
        form.addWidget(QLabel(get_text("property_module.type")), 0, 4)
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in PropertyType])
        form.addWidget(self.type_combo, 0, 5)
        
        # Status
        form.addWidget(QLabel(get_text("property_module.status")), 1, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in PropertyStatus])
        form.addWidget(self.status_combo, 1, 1)
        
        # Address
        form.addWidget(QLabel(get_text("property_module.address")), 2, 0)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form.addWidget(self.address_input, 2, 1, 1, 3)
        
        # City
        form.addWidget(QLabel(get_text("property_module.city")), 3, 0)
        self.city_input = QLineEdit()
        form.addWidget(self.city_input, 3, 1)
        
        # District
        form.addWidget(QLabel(get_text("property_module.district")), 3, 2)
        self.district_input = QLineEdit()
        form.addWidget(self.district_input, 3, 3)
        
        # Postal code
        form.addWidget(QLabel(get_text("property_module.postal_code")), 3, 4)
        self.postal_code_input = QLineEdit()
        form.addWidget(self.postal_code_input, 3, 5)
        
        # Area
        form.addWidget(QLabel(get_text("property_module.area")), 4, 0)
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(0, 999999.99)
        self.area_input.setDecimals(2)
        form.addWidget(self.area_input, 4, 1)
        
        # Construction year
        form.addWidget(QLabel(get_text("property_module.construction_year")), 4, 2)
        self.year_input = QSpinBox()
        self.year_input.setRange(1800, 2100)
        self.year_input.setValue(datetime.now().year)
        form.addWidget(self.year_input, 4, 3)
        
        # Financial details
        form.addWidget(QLabel(get_text("property_module.purchase_price")), 5, 0)
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setRange(0, 9999999999.99)
        self.purchase_price_input.setDecimals(2)
        form.addWidget(self.purchase_price_input, 5, 1)
        
        form.addWidget(QLabel(get_text("property_module.current_value")), 5, 2)
        self.current_value_input = QDoubleSpinBox()
        self.current_value_input.setRange(0, 9999999999.99)
        self.current_value_input.setDecimals(2)
        form.addWidget(self.current_value_input, 5, 3)
        
        form.addWidget(QLabel(get_text("property_module.monthly_rent")), 5, 4)
        self.monthly_rent_input = QDoubleSpinBox()
        self.monthly_rent_input.setRange(0, 999999.99)
        self.monthly_rent_input.setDecimals(2)
        form.addWidget(self.monthly_rent_input, 5, 5)
        
        layout.addLayout(form)
        
        # Features
        features_layout = QHBoxLayout()
        features_layout.addWidget(QLabel(get_text("property_module.features")))
        self.features_input = QTextEdit()
        self.features_input.setMaximumHeight(60)
        features_layout.addWidget(self.features_input)
        layout.addLayout(features_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(get_text("common.save"))
        self.save_btn.clicked.connect(self.save_property)
        button_layout.addWidget(self.save_btn)
        
        clear_btn = QPushButton(get_text("common.clear"))
        clear_btn.clicked.connect(self.clear_property_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.property_table = QTableWidget()
        self.property_table.setColumnCount(8)
        self.property_table.setHorizontalHeaderLabels([
            get_text("property_module.property_no"),
            get_text("property_module.title"),
            get_text("property_module.type"),
            get_text("property_module.status"),
            get_text("property_module.city"),
            get_text("property_module.area"),
            get_text("property_module.current_value"),
            get_text("property_module.monthly_rent")
        ])
        layout.addWidget(self.property_table)
        
        # Connect table selection
        self.property_table.itemSelectionChanged.connect(self.on_property_selected)

    def _setup_deed_tab(self, tab):
        """Setup the deed management tab"""
        layout = QVBoxLayout(tab)
        
        # Property selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel(get_text("property_module.select_property")))
        self.deed_property_combo = QComboBox()
        selector_layout.addWidget(self.deed_property_combo)
        layout.addLayout(selector_layout)
        
        # Form layout for deed details
        form = QGridLayout()
        
        # Deed number
        form.addWidget(QLabel(get_text("property_module.deed_no")), 0, 0)
        self.deed_no_input = QLineEdit()
        form.addWidget(self.deed_no_input, 0, 1)
        
        # Registration date
        form.addWidget(QLabel(get_text("property_module.registration_date")), 0, 2)
        self.registration_date_input = QDateEdit()
        self.registration_date_input.setCalendarPopup(True)
        self.registration_date_input.setDate(QDate.currentDate())
        form.addWidget(self.registration_date_input, 0, 3)
        
        # Ownership type
        form.addWidget(QLabel(get_text("property_module.ownership_type")), 1, 0)
        self.ownership_type_combo = QComboBox()
        self.ownership_type_combo.addItems([ot.value for ot in OwnershipType])
        form.addWidget(self.ownership_type_combo, 1, 1)
        
        # Owner details
        form.addWidget(QLabel(get_text("property_module.owner_name")), 1, 2)
        self.owner_name_input = QLineEdit()
        form.addWidget(self.owner_name_input, 1, 3)
        
        form.addWidget(QLabel(get_text("property_module.owner_id")), 2, 0)
        self.owner_id_input = QLineEdit()
        form.addWidget(self.owner_id_input, 2, 1)
        
        # Share ratio
        form.addWidget(QLabel(get_text("property_module.share_ratio")), 2, 2)
        self.share_ratio_input = QDoubleSpinBox()
        self.share_ratio_input.setRange(0, 1)
        self.share_ratio_input.setDecimals(4)
        self.share_ratio_input.setValue(1)
        form.addWidget(self.share_ratio_input, 2, 3)
        
        # Purchase price
        form.addWidget(QLabel(get_text("property_module.purchase_price")), 3, 0)
        self.deed_purchase_price_input = QDoubleSpinBox()
        self.deed_purchase_price_input.setRange(0, 9999999999.99)
        self.deed_purchase_price_input.setDecimals(2)
        form.addWidget(self.deed_purchase_price_input, 3, 1)
        
        # Notes
        form.addWidget(QLabel(get_text("property_module.notes")), 3, 2)
        self.deed_notes_input = QLineEdit()
        form.addWidget(self.deed_notes_input, 3, 3)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_deed_btn = QPushButton(get_text("property_module.save_deed"))
        save_deed_btn.clicked.connect(self.save_deed)
        button_layout.addWidget(save_deed_btn)
        
        clear_deed_btn = QPushButton(get_text("common.clear"))
        clear_deed_btn.clicked.connect(self.clear_deed_form)
        button_layout.addWidget(clear_deed_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.deed_table = QTableWidget()
        self.deed_table.setColumnCount(8)
        self.deed_table.setHorizontalHeaderLabels([
            get_text("property_module.deed_no"),
            get_text("property_module.registration_date"),
            get_text("property_module.ownership_type"),
            get_text("property_module.owner_name"),
            get_text("property_module.share_ratio"),
            get_text("property_module.purchase_price"),
            get_text("property_module.notes"),
            get_text("property_module.is_active")
        ])
        layout.addWidget(self.deed_table)

    def _setup_document_tab(self, tab):
        """Setup the document management tab"""
        layout = QVBoxLayout(tab)
        
        # Property selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel(get_text("property_module.select_property")))
        self.doc_property_combo = QComboBox()
        selector_layout.addWidget(self.doc_property_combo)
        layout.addLayout(selector_layout)
        
        # Form layout for document details
        form = QGridLayout()
        
        # Document type
        form.addWidget(QLabel(get_text("property_module.document_type")), 0, 0)
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems([dt.value for dt in DocumentType])
        form.addWidget(self.doc_type_combo, 0, 1)
        
        # Title
        form.addWidget(QLabel(get_text("property_module.document_title")), 0, 2)
        self.doc_title_input = QLineEdit()
        form.addWidget(self.doc_title_input, 0, 3)
        
        # Description
        form.addWidget(QLabel(get_text("property_module.description")), 1, 0)
        self.doc_description_input = QLineEdit()
        form.addWidget(self.doc_description_input, 1, 1, 1, 3)
        
        # Dates
        form.addWidget(QLabel(get_text("property_module.issue_date")), 2, 0)
        self.issue_date_input = QDateEdit()
        self.issue_date_input.setCalendarPopup(True)
        self.issue_date_input.setDate(QDate.currentDate())
        form.addWidget(self.issue_date_input, 2, 1)
        
        form.addWidget(QLabel(get_text("property_module.expiry_date")), 2, 2)
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDate(QDate.currentDate())
        form.addWidget(self.expiry_date_input, 2, 3)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        upload_btn = QPushButton(get_text("property_module.upload_document"))
        upload_btn.clicked.connect(self.upload_document)
        button_layout.addWidget(upload_btn)
        
        clear_doc_btn = QPushButton(get_text("common.clear"))
        clear_doc_btn.clicked.connect(self.clear_document_form)
        button_layout.addWidget(clear_doc_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.document_table = QTableWidget()
        self.document_table.setColumnCount(6)
        self.document_table.setHorizontalHeaderLabels([
            get_text("property_module.document_type"),
            get_text("property_module.document_title"),
            get_text("property_module.description"),
            get_text("property_module.issue_date"),
            get_text("property_module.expiry_date"),
            get_text("property_module.file_path")
        ])
        layout.addWidget(self.document_table)

    def load_properties(self):
        """Load properties into tables and combo boxes"""
        self.property_table.setRowCount(0)
        properties = self.property_service.get_all_properties()
        
        # Clear and reload combo boxes
        self.deed_property_combo.clear()
        self.doc_property_combo.clear()
        
        for row, property in enumerate(properties):
            self.property_table.insertRow(row)
            self.property_table.setItem(row, 0, QTableWidgetItem(property.property_no))
            self.property_table.setItem(row, 1, QTableWidgetItem(property.title))
            self.property_table.setItem(row, 2, QTableWidgetItem(property.type.value))
            self.property_table.setItem(row, 3, QTableWidgetItem(property.status.value))
            self.property_table.setItem(row, 4, QTableWidgetItem(property.city))
            self.property_table.setItem(row, 5, QTableWidgetItem(f"{property.area:.2f}" if property.area else ""))
            self.property_table.setItem(row, 6, QTableWidgetItem(f"{property.current_value:.2f}" if property.current_value else ""))
            self.property_table.setItem(row, 7, QTableWidgetItem(f"{property.monthly_rent:.2f}" if property.monthly_rent else ""))
            
            # Add to combo boxes
            combo_text = f"{property.property_no} - {property.title}"
            self.deed_property_combo.addItem(combo_text, property.id)
            self.doc_property_combo.addItem(combo_text, property.id)
        
        self.property_table.resizeColumnsToContents()

    def clear_property_form(self):
        """Clear all property form fields"""
        self.property_no_input.clear()
        self.title_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.address_input.clear()
        self.city_input.clear()
        self.district_input.clear()
        self.postal_code_input.clear()
        self.area_input.setValue(0)
        self.year_input.setValue(datetime.now().year)
        self.purchase_price_input.setValue(0)
        self.current_value_input.setValue(0)
        self.monthly_rent_input.setValue(0)
        self.features_input.clear()

    def clear_deed_form(self):
        """Clear all deed form fields"""
        self.deed_no_input.clear()
        self.registration_date_input.setDate(QDate.currentDate())
        self.ownership_type_combo.setCurrentIndex(0)
        self.owner_name_input.clear()
        self.owner_id_input.clear()
        self.share_ratio_input.setValue(1)
        self.deed_purchase_price_input.setValue(0)
        self.deed_notes_input.clear()

    def clear_document_form(self):
        """Clear all document form fields"""
        self.doc_type_combo.setCurrentIndex(0)
        self.doc_title_input.clear()
        self.doc_description_input.clear()
        self.issue_date_input.setDate(QDate.currentDate())
        self.expiry_date_input.setDate(QDate.currentDate())

    def save_property(self):
        """Save or update property information"""
        try:
            # Convert features text to JSON
            features_text = self.features_input.toPlainText().strip()
            features_dict = {}
            if features_text:
                try:
                    # Try parsing as JSON
                    features_dict = json.loads(features_text)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as comma-separated list
                    features = [f.strip() for f in features_text.split(',')]
                    features_dict = {f"feature_{i+1}": f for i, f in enumerate(features)}

            property_data = {
                'property_no': self.property_no_input.text(),
                'title': self.title_input.text(),
                'type': PropertyType(self.type_combo.currentText()),
                'status': PropertyStatus(self.status_combo.currentText()),
                'address': self.address_input.toPlainText(),
                'city': self.city_input.text(),
                'district': self.district_input.text(),
                'postal_code': self.postal_code_input.text(),
                'area': self.area_input.value() or None,
                'construction_year': self.year_input.value(),
                'features': features_dict,
                'purchase_price': self.purchase_price_input.value() or None,
                'current_value': self.current_value_input.value() or None,
                'monthly_rent': self.monthly_rent_input.value() or None
            }

            if not all([property_data['property_no'], property_data['title'],
                       property_data['address'], property_data['city']]):
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("common.fill_required_fields"))
                return

            self.property_service.create_property(property_data)
            self.clear_property_form()
            self.load_properties()
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("common.save_success"))

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))

    def save_deed(self):
        """Save deed information"""
        try:
            property_id = self.deed_property_combo.currentData()
            if not property_id:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("property_module.select_property_warning"))
                return

            deed_data = {
                'property_id': property_id,
                'deed_no': self.deed_no_input.text(),
                'registration_date': self.registration_date_input.date().toPython(),
                'ownership_type': OwnershipType(self.ownership_type_combo.currentText()),
                'owner_name': self.owner_name_input.text(),
                'owner_id_number': self.owner_id_input.text(),
                'share_ratio': self.share_ratio_input.value(),
                'purchase_price': self.deed_purchase_price_input.value() or None,
                'notes': self.deed_notes_input.text(),
                'is_active': True
            }

            if not all([deed_data['deed_no'], deed_data['owner_name']]):
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("common.fill_required_fields"))
                return

            self.property_service.create_deed(deed_data)
            self.clear_deed_form()
            self.load_deeds(property_id)
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("common.save_success"))

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))

    def upload_document(self):
        """Upload and save document"""
        try:
            property_id = self.doc_property_combo.currentData()
            if not property_id:
                QMessageBox.warning(self, get_text("common.warning"),
                                  get_text("property_module.select_property_warning"))
                return

            # Get file from user
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                get_text("property_module.select_document"),
                "",
                get_text("property_module.document_file_types")
            )
            
            if not file_path:
                return

            document = self.property_service.store_document(
                property_id=property_id,
                file_path=file_path,
                doc_type=DocumentType(self.doc_type_combo.currentText()),
                title=self.doc_title_input.text(),
                description=self.doc_description_input.text(),
                issue_date=self.issue_date_input.date().toPython(),
                expiry_date=self.expiry_date_input.date().toPython()
            )

            self.clear_document_form()
            self.load_documents(property_id)
            QMessageBox.information(self, get_text("common.success"),
                                  get_text("property_module.document_upload_success"))

        except Exception as e:
            QMessageBox.critical(self, get_text("common.error"), str(e))

    def on_property_selected(self):
        """Handle property selection in the table"""
        selected_items = self.property_table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        property_no = self.property_table.item(row, 0).text()
        property = self.property_service.get_property_by_no(property_no)
        
        if property:
            # Update form fields
            self.property_no_input.setText(property.property_no)
            self.title_input.setText(property.title)
            self.type_combo.setCurrentText(property.type.value)
            self.status_combo.setCurrentText(property.status.value)
            self.address_input.setPlainText(property.address)
            self.city_input.setText(property.city)
            self.district_input.setText(property.district or "")
            self.postal_code_input.setText(property.postal_code or "")
            self.area_input.setValue(property.area or 0)
            self.year_input.setValue(property.construction_year or datetime.now().year)
            self.purchase_price_input.setValue(property.purchase_price or 0)
            self.current_value_input.setValue(property.current_value or 0)
            self.monthly_rent_input.setValue(property.monthly_rent or 0)
            
            # Handle features JSON
            if property.features:
                try:
                    features_dict = json.loads(property.features)
                    if isinstance(features_dict, dict):
                        features_text = json.dumps(features_dict, indent=2)
                    else:
                        features_text = str(features_dict)
                    self.features_input.setPlainText(features_text)
                except:
                    self.features_input.setPlainText(property.features)
            else:
                self.features_input.clear()

    def load_deeds(self, property_id: int):
        """Load deeds for the selected property"""
        self.deed_table.setRowCount(0)
        deeds = self.property_service.get_property_deeds(property_id)
        
        for row, deed in enumerate(deeds):
            self.deed_table.insertRow(row)
            self.deed_table.setItem(row, 0, QTableWidgetItem(deed.deed_no))
            self.deed_table.setItem(row, 1, QTableWidgetItem(str(deed.registration_date)))
            self.deed_table.setItem(row, 2, QTableWidgetItem(deed.ownership_type.value))
            self.deed_table.setItem(row, 3, QTableWidgetItem(deed.owner_name))
            self.deed_table.setItem(row, 4, QTableWidgetItem(f"{deed.share_ratio:.4f}"))
            self.deed_table.setItem(row, 5, QTableWidgetItem(f"{deed.purchase_price:.2f}" if deed.purchase_price else ""))
            self.deed_table.setItem(row, 6, QTableWidgetItem(deed.notes or ""))
            self.deed_table.setItem(row, 7, QTableWidgetItem("Yes" if deed.is_active else "No"))
        
        self.deed_table.resizeColumnsToContents()

    def load_documents(self, property_id: int):
        """Load documents for the selected property"""
        self.document_table.setRowCount(0)
        documents = self.property_service.get_property_documents(property_id)
        
        for row, doc in enumerate(documents):
            self.document_table.insertRow(row)
            self.document_table.setItem(row, 0, QTableWidgetItem(doc.type.value))
            self.document_table.setItem(row, 1, QTableWidgetItem(doc.title))
            self.document_table.setItem(row, 2, QTableWidgetItem(doc.description or ""))
            self.document_table.setItem(row, 3, QTableWidgetItem(str(doc.issue_date) if doc.issue_date else ""))
            self.document_table.setItem(row, 4, QTableWidgetItem(str(doc.expiry_date) if doc.expiry_date else ""))
            self.document_table.setItem(row, 5, QTableWidgetItem(doc.file_path))
        
        self.document_table.resizeColumnsToContents()
        self.setCentralWidget(central_widget)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)