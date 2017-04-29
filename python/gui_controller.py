from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_simple_gui import Ui_multisecret_gui

from multisecret.Dealer import Dealer
import sys
import json

class BytesEncoder(json.JSONEncoder):
    """ Provide encoding method for writing bytes to JSON """
    def default(self, byteobject):
        return byteobject.hex()
        

class MultiSecretProgram(Ui_multisecret_gui):
    def __init__(self, window):
        Ui_multisecret_gui.__init__(self)
        self.setupUi(window)

        self.button_split.clicked.connect(self.split_secret)

        
    def split_secret(self):
        secret1 = int(self.secret_1.text())
        secret2 = int(self.secret_2.text())
        secrets = [secret1, secret2]
        
        prime = 15487469

        # multi secret sharing parameters
        n_participants = 3
        access_structures = [[[1,2,3]], [[1,2]]]
        dealer = Dealer(prime, n_participants, secrets, access_structures)
        pseudo_shares = dealer.split_secrets()
        
        for secret_shares in pseudo_shares:
            print(' secret')
            for group_shares in secret_shares:
                print('  group')
                for user_share in group_shares:
                    print('  user', user_share.hex())
                    
                    
        # save params: prime, structure, ID (user x), to file to recreate Dealer later
        self.save_pseudo_shares_to_file(pseudo_shares, dealer.p, 'shares_dict.log')
        
        self.statusbar.setText('Secret split!')
    
    
    def save_pseudo_shares_to_file(self, pseudo_shares, prime, filename):
        
        data = { 'prime' : prime,
                 'pseudo_shares' : pseudo_shares,
                 'id' : 'lol1' }
        
        with open(filename, 'w') as file:
            json.dump(data, file, cls=BytesEncoder)
        
        """
        with open(filename, 'w') as file:
            for secret_shares in pseudo_shares:
            print(' secret')
            for group_shares in secret_shares:
                print('  group')
                for user_share in group_shares:
                    print('  user', user_share.hex())
                        file.write('\nShare')
                        file.write(user_share.hex())
                        """
    
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretProgram(window)
    
    window.show()
    sys.exit(app.exec_())
