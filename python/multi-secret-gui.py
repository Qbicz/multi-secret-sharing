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
        self.button_combine.clicked.connect(self.combine_secret)
        self.load_share_1.clicked.connect(self.load_pseudo_shares)

        
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
        self.save_pseudo_shares_to_file(dealer.p,
                                        dealer.access_structures,
                                        pseudo_shares,
                                        dealer.random_id,
                                        dealer.public_shares_M,
                                        'shares.json')
        
        self.statusbar.setText('Secret split!')
    
    
    def save_pseudo_shares_to_file(self, prime, access,
                                   pseudo_shares, user_ids,
                                   public_shares_M, filename):
        """ Save python dictionary with data needed for secret reconstruction.
            jsonpickle is used for encoding because data contains bytes objects,
            not recognized by json encodera """
        
        # TODO: public data save to timestamp_public_info.json
        # TODO: user share save to timestamp_pseudo_share_X.json
        
        data = { 'prime' : prime,
                 'access_structures' : access,
                 'pseudo_shares' : pseudo_shares,
                 'ids' : user_ids,
                 'public_shares_M' : public_shares_M}
        
        json_string = jsonpickle.encode(data)
        print('to json', json_string)
        
        with open(filename, 'w') as file:
            json.dump(json_string, file)
        

    def load_pseudo_shares(self):
        
        with open('shares.json', 'r') as file:
            json_string = json.load(file)
    
        data = jsonpickle.decode(json_string)
        print('loaded data from JSON', data)
        
        # TODO: create a Combiner class
        combiner = Dealer(data['prime'],
                          3,
                          [0],
                          data['access_structures'])
        combiner.random_id = data['ids']
        combiner.public_shares_M = data['public_shares_M']
        
        secret = combiner.combine_secret(0, 0, data['pseudo_shares'][0][0])
        print('secret:', secret)
        
        self.textBrowser.append('Combined a secret: {}'.format(secret) )
    
        
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
