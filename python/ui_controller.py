#! /usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from gui.multisecret_dynamic_gui import Ui_multisecret_gui

from multisecret.Dealer import Dealer
import sys
import json
import jsonpickle
from copy import deepcopy

INITIAL_USER_COUNT = 3

def clear_layout(layout):
    for i in reversed(range(layout.count())):
        widgetToRemove = layout.itemAt(i).widget()
        layout.removeWidget(widgetToRemove)
        widgetToRemove.setParent(None)
        

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

        # Redraw dynamic tab when value changed in "Problem size"
        self.number_of_users.valueChanged.connect(self.refresh_dynamic_widgets_secrets_users)
        self.number_of_secrets.valueChanged.connect(self.refresh_dynamic_widgets_secrets_users)

        self.user_count = INITIAL_USER_COUNT
        self.user_data = [None] * self.user_count

    def refresh_dynamic_widgets_secrets_users(self):
        
        users = self.number_of_users.value()
        secrets = self.number_of_secrets.value()
        print('users:',  users)
        print('secrets:', secrets)
        self.refresh_dynamic_split_tab(secrets, users)
        self.refresh_dynamic_combine_tab(secrets, users)
        
    def refresh_dynamic_split_tab(self, secrets, users):
        # remove old widgets
        clear_layout(self.gridLayout_dyn)
        
        _translate = QtCore.QCoreApplication.translate
        self.secret_labels = [None]*secrets
        self.secret_inputs = [None]*secrets
        # for 2D lists, list comprehensions HAVE TO be used in order to avoid having copies of lists
        self.checkboxes = [[[None] for _ in range(users)] for _ in range(secrets)]
        
        self.old_secret_number = secrets
        
        for secret in range(secrets):
            self.secret_labels[secret] = QtWidgets.QLabel(self.gridLayoutWidget_dyn)
            self.secret_labels[secret].setObjectName("secret_label"+str(secret))
            self.gridLayout_dyn.addWidget(self.secret_labels[secret], secret, 0, 1, 1)
            self.secret_labels[secret].setText('Secret {}'.format(secret))
            
            self.secret_inputs[secret] = QtWidgets.QLineEdit(self.gridLayoutWidget_dyn)
            self.secret_inputs[secret].setObjectName("secret_input"+str(secret))
            self.gridLayout_dyn.addWidget(self.secret_inputs[secret], secret, 1, 1, 1)
        
            for user in range(users):
                self.checkboxes[secret][user] = QtWidgets.QCheckBox(self.gridLayoutWidget_dyn)
                self.checkboxes[secret][user].setObjectName("check_s{}p{}".format(secret, user))
                self.gridLayout_dyn.addWidget(self.checkboxes[secret][user], secret, 2+user, 1, 1)
                self.checkboxes[secret][user].setText(_translate("multisecret_gui", "User "+str(user+1)))
        
        self.button_split_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn)
        self.button_split_dyn.setObjectName("button_split")
        self.gridLayout_dyn.addWidget(self.button_split_dyn, secrets+1, 1, 1, users)
        self.button_split_dyn.setText('Split secrets')
        
        self.button_split_dyn.clicked.connect(self.split_secret_dynamic)
        
        # after redrawing, call QWidget.update
        self.tab_dyn.update()

    def refresh_dynamic_combine_tab(self, secrets, users):
        clear_layout(self.gridLayout_dyn_reconstr)

        self.users = users

        _translate = QtCore.QCoreApplication.translate
        self.secret_labels = [None] * users

        self.reconstr_user_labels = [None] * self.users
        self.user_data_reconstr_buttons = [None] * self.users

        self.button_load_public_info_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.addWidget(self.button_load_public_info_dyn, 0, 0, 1, 1)
        self.button_load_public_info_dyn.clicked.connect(self.load_public_reconstruction_info)


        for user in range(self.users):
            self.user_data_reconstr_buttons[user] = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
            self.gridLayout_dyn_reconstr.addWidget(self.user_data_reconstr_buttons[user], user + 1, 0, 1, 1)
            # Connect loading pseudo shares to each button
            self.user_data_reconstr_buttons[user].clicked.connect(lambda: self.load_pseudo_shares_from_user(user))

        self.button_reconstr_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.addWidget(self.button_reconstr_dyn, 0, 1, 1, 1)
        self.button_reconstr_dyn.clicked.connect(self.combine_secret_dynamic)

        self.textBrowser_dyn = QtWidgets.QTextBrowser(self.gridLayoutWidget_dyn_reconstr)
        self.textBrowser_dyn.setObjectName("textBrowser_dyn")
        self.gridLayout_dyn_reconstr.addWidget(self.textBrowser_dyn, 1, 1, users+1, 1)

        # Text in buttons
        for user in range(self.users):
            self.user_data_reconstr_buttons[user].setText(
                _translate("multisecret_gui", "Load pseudo share from user " + str(user + 1) + "..."))
        self.button_reconstr_dyn.setText(_translate("multisecret_gui", "Reconstruct secrets"))
        self.button_load_public_info_dyn.setText(_translate("multisecret_gui", "Load public info"))

    def split_secret_dynamic(self):
        
        users_count = self.number_of_users.value()
        secrets_count = self.number_of_secrets.value()
        
        # Get secrets
        secrets = [None]*secrets_count
        try:
            for s in range(secrets_count):
                secrets[s] = int(self.secret_inputs[s].text())
        except ValueError as e:
            print('Secrets missing. Error %r' % e)
            self.showdialog()
            return
        
        prime = 2**256 - 2**224 + 2**192 + 2**96 - 1
        
        # Using list comprehension, with [[]]*secrets_count we would obtain copies of the same list
        access_structures = [ [] for _ in range(secrets_count)]
        
        for s in range(secrets_count):
            list_of_users = [(user+1)*int(checkbox.isChecked()) for user, checkbox
                             in enumerate(self.checkboxes[s]) if checkbox.isChecked()]
            # GUI supports only a single access group to a secret
            access_structures[s].append(list_of_users)

        print(access_structures)
        try:
            dealer = Dealer(prime, users_count, secrets, access_structures)
        except ValueError as e:
            self.showdialog(str(e))
            raise
        pseudo_shares = dealer.split_secrets()
        
        self.save_pseudo_shares_to_file(dealer,
                                        pseudo_shares)
        
    def combine_secret_dynamic(self):
        print('combine_secret_dynamic')

    def split_secret(self):
        try:
            secret1 = int(self.secret_1.text())
            secret2 = int(self.secret_2.text())
            secret3 = int(self.secret_3.text())
        except ValueError as e:
            print('Secrets missing. Error %r' % e)
            self.showdialog()
            return
            
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
                                        pseudo_shares)
        
        self.statusbar.setText('Secret split!')
    
    def showdialog(self, text='Please specify all secrets.'):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText(text)
        #msg.setInformativeText("The number of secrets is set to 3. In the next version you will be able to choose a number of secrets.")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
        
    def save_pseudo_shares_to_file(self, dealer, pseudo_shares):
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
        
        # Save user shares (for each secret and group) and user ID to json file
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
            print('caught error %r' % e)
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
            print('caught error %r' % e)
            self.textBrowser.append('There is not enough information to reconstruct!')
            return
        
        combiner.random_id = [None] * combiner.n
        
        # create a structure for pseudo shares
        combiner.pseudo_shares = deepcopy(combiner.access_structures)
        
        try:
            for user in range(1, combiner.n+1):
                
                # ID from user
                print('\nID from user', self.user_data[user-1]['id'])
                combiner.random_id[user-1] = self.user_data[user-1]['id']
                
                # pseudo shares from user
                print(self.user_data[user-1])
                user_shares = self.user_data[user-1]['shares']
                combiner.set_pseudo_shares_from_participant(user, user_shares)
            
        except TypeError as e:
            print('caught error %r' % e)
            self.textBrowser.append('You have not loaded all shares. Cannot reconstruct!')
            return
            
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
