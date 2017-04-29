from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_simple_gui import Ui_multisecret_gui

from multisecret.Dealer import Dealer
import sys
import json
import jsonpickle


class MultiSecretProgram(Ui_multisecret_gui):
    def __init__(self, window):
        Ui_multisecret_gui.__init__(self)
        self.setupUi(window)

        self.button_split.clicked.connect(self.split_secret)
        self.button_split_2.clicked.connect(self.combine_secret)
        self.button_split_3.clicked.connect(self.load_pseudo_shares)

        
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
        self.save_pseudo_shares_to_file(pseudo_shares,
                                        dealer.access_structures,
                                        dealer.p,
                                        dealer.random_id,
                                        'shares.json')
        
        self.statusbar.setText('Secret split!')
    
    
    def save_pseudo_shares_to_file(self, prime, access,
                                   pseudo_shares, user_ids, filename):
        
        data = { 'prime' : prime,
                 'access_structure' : access,
                 'pseudo_shares' : pseudo_shares,
                 'ids' : user_ids }
        
        json_string = jsonpickle.encode(data)
        
        with open(filename, 'w') as file:
            json.dump(json_string, file)
        

    def load_pseudo_shares(self):
        
        with open('shares.json', 'r') as file:
            json_string = json.load(file)
    
        data = jsonpickle.decode(json_string)
        print(data)
        print(data['pseudo_shares'])
    
        
    def combine_secret(self):
        """ Combine secret from JSON loaded information.
            First, check if we have all pieces needed to reconstruct. """
        
        assert(self.access_structures and self.loaded_shares
               and self.loaded_ids and self.loaded_prime)
    
        
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretProgram(window)
    
    window.show()
    sys.exit(app.exec_())
