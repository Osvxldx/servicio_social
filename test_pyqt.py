"""
Test simple para verificar que PyQt5 funciona
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

def test_pyqt():
    app = QApplication(sys.argv)
    
    msg = QMessageBox()
    msg.setWindowTitle("Test PyQt5")
    msg.setText("¡PyQt5 funciona correctamente!")
    msg.exec_()
    
    return 0

if __name__ == "__main__":
    sys.exit(test_pyqt())
