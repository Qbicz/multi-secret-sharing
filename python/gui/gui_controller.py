from PyQt5 import QtCore, QtGui, QtWidgets
from multisecret_simple_gui import Ui_scada_gui

import sys

class MultiSecretProgram(Ui_scada_gui):
    def __init__(self, window):
        Ui_scada_gui.__init__(self)
        self.setupUi(window)

        self.button_split.clicked.connect(self.split_secret)
        
    def split_secret(self):
        self.statusbar.setText('Secret split!')
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretProgram(window)
    
    window.show()
    sys.exit(app.exec_())
