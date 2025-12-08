"""
Image Annotation Tool - Application Entry Point

This is the main entry point for the PyQt6 desktop application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """
    Main application entry point.

    Creates the QApplication, initializes the main window,
    and starts the event loop.
    """
    # Create Qt application
    app = QApplication(sys.argv)

    # Create and configure main window
    window = MainWindow()
    window.setWindowTitle("Image Annotation Tool")
    window.resize(1200, 800)
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
