import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.config import setup_environment
from core.database import init_database
from core.localization import setup_translations

def main():
    # Initialize application
    app = QApplication(sys.argv)
    
    # Setup environment and configurations
    setup_environment()
    
    # Initialize database
    init_database()
    
    # Setup translations
    setup_translations()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
