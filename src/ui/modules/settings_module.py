from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QFormLayout
from PySide6.QtCore import Qt
from core.localization import set_language, LANGUAGES

class SettingsModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayarlar")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        for lang_code, lang_name in LANGUAGES.items():
            self.language_combo.addItem(lang_name, lang_code)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        form_layout.addRow("Dil / Language:", self.language_combo)
        
        # Add form to main layout
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
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
            QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
    
    def change_language(self, index):
        lang_code = self.language_combo.currentData()
        if lang_code:
            set_language(lang_code)
            # Here you would typically emit a signal to update the UI language