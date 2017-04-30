from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_dynamic_gui import Ui_multisecret_gui

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
        self.load_share_1.clicked.connect(self.load_pseudo_shares_from_user, 1)

        
    def split_secret(self):
        secret1 = int(self.secret_1.text())
        secret2 = int(self.secret_2.text())
        secret3 = int(self.secret_3.text())
        secrets = [secret1, secret2, secret3]
        
        prime = 2**256 - 2**224 + 2**192 + 2**96 - 1

        # multi secret sharing parameters
        n_participants = 3
        access_structures = [[[1,2,3]], [[1,3]], [[1,2,3]]]
        dealer = Dealer(prime, n_participants, secrets, access_structures)
        pseudo_shares = dealer.split_secrets()
        
        for secret_shares in pseudo_shares:
            print(' secret')
            for group_shares in secret_shares:
                print('  group')
                for user_share in group_shares:
                    print('  user', user_share)
                    
        # save params: prime, structure, ID (user x), to file to recreate Dealer later
        self.save_pseudo_shares_to_file(dealer,
                                        pseudo_shares,
                                        'shares.json')
        
        self.statusbar.setText('Secret split!')
    
    
    def save_pseudo_shares_to_file(self, dealer, pseudo_shares, filename):
        """ Save python dictionary with data needed for secret reconstruction.
            jsonpickle is used for encoding because data contains bytes objects,
            not recognized by json encoder """
        
        # Save public data to public_info.json
        # TODO: add timestamps and FileChooser dialogs
        public_info = { 'prime' : dealer.p,
                     'access_structures' : dealer.access_structures,
                     'public_shares_M' : dealer.public_shares_M }
        
        public_info_json_string = jsonpickle.encode(public_info)
        print('public_info to json', public_info_json_string)
        
        with open(filename, 'w') as public_info_file:
            json.dump(public_info_json_string, public_info_file)
        
        #
        # Save user shares (for each secret and group) and user ID to json file
        #
        for user in range(1, dealer.n+1):
            
            user_shares = dealer.get_pseudo_shares_for_participant(user)
            user_data = {'id' : dealer.random_id[user-1],
                         'shares' : user_shares }
        
            user_json_string = jsonpickle.encode(user_data)
            print('user share and ID to json', user_json_string)
            
            filename = 'user' + str(user) + '.json'
            with open(filename, 'w') as file:
                json.dump(user_json_string, file)
        

    def load_pseudo_shares_from_user(self, participant):
        
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
        
        assert(self.loaded_structures and self.loaded_shares
               and self.loaded_ids and self.loaded_prime)
    
        
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretProgram(window)
    
    window.show()
    sys.exit(app.exec_())
