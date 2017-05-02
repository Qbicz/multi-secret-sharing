from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_dynamic_gui import Ui_multisecret_gui

from multisecret.Dealer import Dealer
import sys
import json
import jsonpickle
from copy import deepcopy


class MultiSecretController(Ui_multisecret_gui):
    def __init__(self, window):
        Ui_multisecret_gui.__init__(self)
        self.setupUi(window)

        self.button_split.clicked.connect(self.split_secret)
        self.button_combine.clicked.connect(self.combine_secret)
        self.button_load_share_1.clicked.connect(lambda: self.load_pseudo_shares_from_user(1) )
        self.button_load_share_2.clicked.connect(lambda: self.load_pseudo_shares_from_user(2) )
        self.button_load_share_3.clicked.connect(lambda: self.load_pseudo_shares_from_user(3) )
        self.button_load_public_info.clicked.connect(self.load_public_reconstruction_info)
        
        # TODO: get from the GUI
        self.user_count = 3
        self.user_data = [None] * self.user_count


        
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
        with open('public_info.json', 'w') as public_info_file:
            json.dump(public_info_json_string, public_info_file)
        
        #
        # Save user shares (for each secret and group) and user ID to json file
        #
        for user in range(1, dealer.n+1):
            
            user_shares = dealer.get_pseudo_shares_for_participant(user)
            user_data = {'user' : user,
                         'id' : dealer.random_id[user-1],
                         'shares' : user_shares }
        
            user_json_string = jsonpickle.encode(user_data)
            filename = 'user' + str(user) + '.json'
            with open(filename, 'w') as file:
                json.dump(user_json_string, file)
        

    def load_public_reconstruction_info(self):
        """ Load prime, access structures and public shares
            to controller's internal public_info dictionary.
        """
        try:
            with open('public_info.json', 'r') as file:
                json_string = json.load(file)
        except FileNotFoundError as e:
            self.textBrowser.append('Cannot open file {}'.format('public_info.json') )
            return
    
        self.public_info = jsonpickle.decode(json_string)
        print('loaded data from JSON', self.public_info)
        
    
    def load_pseudo_shares_from_user(self, participant):
        """ Load user ID and user's pseudo shares for each secret.
        """
        
        userfile = 'user' + str(participant) + '.json'
        try:
            with open(userfile, 'r') as file:
                json_string = json.load(file)
        except FileNotFoundError as e:
            self.textBrowser.append('Cannot open file {}'.format(userfile) )
            return
    
        self.user_data[participant-1] = jsonpickle.decode(json_string)
        print('loaded data from JSON', self.user_data[participant-1])
        
        
    def combine_secret(self):
        """ Combine secret from JSON loaded information.
            TODO: Validate all pieces needed to reconstruct.
        """
        
        try:
            # TODO: create a Combiner class
            combiner = Dealer(self.public_info['prime'],
                              3,
                              [0]*3,
                              self.public_info['access_structures'])
            combiner.public_shares_M = self.public_info['public_shares_M']
        except AttributeError as e:
            self.textBrowser.append('There is not enough information to reconstruct!')
            return
        
        combiner.random_id = [None] * combiner.n
        
        # create a structure for pseudo shares
        combiner.pseudo_shares = deepcopy(combiner.access_structures)
        
        for user in range(1, combiner.n+1):
            
            # ID from user
            print('\nID from user', self.user_data[user-1]['id'])
            combiner.random_id[user-1] = self.user_data[user-1]['id']
            
            # pseudo shares from user
            print(self.user_data[user-1])
            user_shares = self.user_data[user-1]['shares']
            combiner.set_pseudo_shares_from_participant(user, user_shares)
            
        print('pseudo_shares:', combiner.pseudo_shares)
        obtained_shares = combiner.pseudo_shares
        print('obtained_shares[0][0]', obtained_shares[0][0])
        secret1 = combiner.combine_secret(0, 0, obtained_shares[0][0])
        secret2 = combiner.combine_secret(1, 0, obtained_shares[1][0])
        secret3 = combiner.combine_secret(2, 0, obtained_shares[2][0])
        
        self.textBrowser.append('Combined a secret: {}'.format(secret1) )
        self.textBrowser.append('Combined a secret: {}'.format(secret2) )
        self.textBrowser.append('Combined a secret: {}'.format(secret3) )
        
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QDialog()
    
    ui = MultiSecretController(window)
    
    window.show()
    sys.exit(app.exec_())
