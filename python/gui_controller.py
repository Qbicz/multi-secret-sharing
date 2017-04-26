from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_simple_gui import Ui_scada_gui

from multisecret.Dealer import Dealer
import sys

class MultiSecretProgram(Ui_scada_gui):
    def __init__(self, window):
        Ui_scada_gui.__init__(self)
        self.setupUi(window)

        self.button_split.clicked.connect(self.split_secret)

        
    def split_secret(self):
        secret = int(self.secret_1.text())
        
        prime = 15487469

        # multi secret sharing parameters
        n_participants = 3
        access_structures = [[[1,2,3]]]
        self.dealer = Dealer(prime, n_participants, [secret], access_structures)
        self.pseudo_shares = self.dealer.split_secrets()
        
        # save params: prime, structure, d, x, to file to recreate Dealer later
        
        self.statusbar.setText('Secret split!')
    
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretProgram(window)
    
    window.show()
    sys.exit(app.exec_())
