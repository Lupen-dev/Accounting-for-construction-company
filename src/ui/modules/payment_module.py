from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

class PaymentModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Taksit/Ödeme Takibi")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)