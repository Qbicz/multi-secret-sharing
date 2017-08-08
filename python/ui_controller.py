#! /usr/bin/env python3

import sys
import json
import jsonpickle
from copy import deepcopy
import functools
import time

from PyQt5 import QtCore, QtWidgets
from gui.multisecret_dynamic_gui import MultiSecretGui

import multisecret.MultiSecretRoyAdhikari
import multisecret.MultiSecretLinYeh
import multisecret.MultiSecretHerranzRuizSaez
import multisecret.byteHelper as bytehelper

INITIAL_USER_COUNT = 3
INITIAL_SECRET_COUNT = 3


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        widgetToRemove = layout.itemAt(i).widget()
        layout.removeWidget(widgetToRemove)
        widgetToRemove.setParent(None)


class MultiSecretController(MultiSecretGui):
    def __init__(self):
        # pass methods which will be run from menubar to GUI
        menu_callbacks = {
            'save_output' : self.menu_save_output
        }
        super(MultiSecretController, self).__init__(menu_callbacks)

        # Initialize algorithm list available
        self.init_algorithm_list()

        # Initialize problem size in UI
        self.number_of_users.setProperty('value', INITIAL_USER_COUNT)
        self.number_of_secrets.setProperty("value", INITIAL_SECRET_COUNT)

        # Redraw dynamic tab when value changed in "Problem size"
        self.number_of_users.valueChanged.connect(
            self.refresh_dynamic_widgets_secrets_users)
        self.number_of_secrets.valueChanged.connect(
            self.refresh_dynamic_widgets_secrets_users)

        self.user_count = INITIAL_USER_COUNT
        self.secret_count = INITIAL_SECRET_COUNT

        self.secret_to_combine = 0

    def menu_save_output(self):
        print('Save output')

        output = self.textBrowser_dyn.toPlainText()
        print(output)

        filename = QtWidgets.QFileDialog.getSaveFileName()[0] # filename is first element of a tuple
        try:
            with open(filename, 'w') as f:
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S_", time.localtime())
                f.write(timestamp + '\n')
                f.write(output)
        except FileNotFoundError as e:
            print('File not specified.', e) # user aborted choosing a file

    def refresh_dynamic_widgets_secrets_users(self):

        self.user_count = self.number_of_users.value()
        self.secret_count = self.number_of_secrets.value()
        print('users:', self.user_count)
        print('secrets:', self.secret_count)

        self.user_data = [None] * self.user_count

        self.refresh_dynamic_split_tab(self.secret_count, self.user_count,
                                       self.gridLayout_dyn,
                                       self.gridLayoutWidget_dyn)
        self.refresh_dynamic_combine_tab(self.secret_count, self.user_count,
                                         self.gridLayout_dyn_reconstr,
                                         self.gridLayoutWidget_dyn_reconstr)

    def refresh_dynamic_split_tab(self, secrets, users, layout, parent_widget):
        # remove old widgets
        clear_layout(layout)

        _translate = QtCore.QCoreApplication.translate
        self.secret_labels = [None] * secrets
        self.secret_inputs = [None] * secrets
        # for 2D lists, list comprehensions HAVE TO be used in order to avoid having copies of lists
        self.checkboxes = [[[None] for _ in range(users)] for _ in
                           range(secrets)]

        self.old_secret_number = secrets

        for secret in range(secrets):
            self.secret_labels[secret] = QtWidgets.QLabel(parent_widget)
            layout.addWidget(self.secret_labels[secret], secret, 0,
                                          1, 1)
            self.secret_labels[secret].setText('Secret {}'.format(secret))

            self.secret_inputs[secret] = QtWidgets.QLineEdit(parent_widget)
            layout.addWidget(self.secret_inputs[secret], secret, 1, 1, 1)

            for user in range(users):
                self.checkboxes[secret][user] = QtWidgets.QCheckBox(parent_widget)
                layout.addWidget(self.checkboxes[secret][user],
                                              secret, 2 + user, 1, 1)
                self.checkboxes[secret][user].setText('User ' + str(user + 1))

        self.algorithm_label = QtWidgets.QLabel(parent_widget)
        layout.addWidget(self.algorithm_label, secrets + 1, 0, 1, 1)
        self.algorithm_label.setText('Algorithm ')

        self.algorithm_combobox = QtWidgets.QComboBox(parent_widget)
        layout.addWidget(self.algorithm_combobox, secrets + 1, 1, 1, users)
        for algorithm in self.algorithm_list:
            self.algorithm_combobox.addItem(algorithm)
        self.algorithm_combobox.currentIndexChanged.connect(
            self.update_algorithm)

        self.button_split_dyn = QtWidgets.QPushButton(parent_widget)
        layout.addWidget(self.button_split_dyn,
                                      secrets + 2, 1, 1, users)
        self.button_split_dyn.setText('Split secrets')

        self.button_split_dyn.clicked.connect(self.split_secret_dynamic)

        # after redrawing, call QWidget.update
        self.tab_dyn.update()

    def refresh_dynamic_combine_tab(self, secrets, users, layout, parent_widget):
        clear_layout(layout)

        _translate = QtCore.QCoreApplication.translate
        self.secret_labels = [None] * users

        self.reconstr_user_labels = [None] * users
        self.user_data_reconstr_buttons = [None] * users

        self.button_load_public_info_dyn = QtWidgets.QPushButton(parent_widget)
        layout.addWidget(self.button_load_public_info_dyn,
                                               0, 0, 1, 1)
        self.button_load_public_info_dyn.clicked.connect(
            self.load_public_info_dynamic)

        for user in range(users):
            self.user_data_reconstr_buttons[user] = QtWidgets.QPushButton(
                parent_widget)
            layout.addWidget(
                self.user_data_reconstr_buttons[user], user + 1, 0, 1, 1)
            # Connect loading pseudo shares to each button
            # functools.partial() is used instead of lambda, to pass actual value of user
            # to connected function and not the variable captured in closure
            self.user_data_reconstr_buttons[user].clicked.connect(
                functools.partial(self.load_pseudo_shares_from_user, user + 1))

        self.button_reconstr_dyn = QtWidgets.QPushButton(parent_widget)
        layout.addWidget(self.button_reconstr_dyn, 0, 1, 1, 1)
        self.button_reconstr_dyn.clicked.connect(self.combine_secret_dynamic)

        # Spinbox for choosing a secret to reconstruct
        self.spinbox_secret = QtWidgets.QSpinBox()
        layout.addWidget(self.spinbox_secret, 0, 2, 1, 1)
        print('secrets:', secrets)
        self.spinbox_secret.setRange(0, secrets - 1)
        self.spinbox_secret.valueChanged.connect(self.choose_secret_to_combine)

        self.textBrowser_dyn = QtWidgets.QTextBrowser(
            parent_widget)
        self.gridLayout_dyn_reconstr.addWidget(self.textBrowser_dyn, 1, 1,
                                               users + 1, 3)

        # Text in buttons
        for user in range(users):
            self.user_data_reconstr_buttons[user].setText(
                'Load pseudo share from user ' + str(user + 1) + '...')
        self.button_reconstr_dyn.setText('Reconstruct secret')
        self.button_load_public_info_dyn.setText('Load public info')

    def choose_secret_to_combine(self):
        self.secret_to_combine = self.spinbox_secret.value()

    def init_algorithm_list(self):
        self.algorithm_list = [
            'Roy-Adhikari',
            'Lin-Yeh',
            'Herranz-Ruiz-Saez'
        ]
        self.algorithm = self.algorithm_list[0]

    def update_algorithm(self, algorithm_index):
        self.algorithm = self.algorithm_list[algorithm_index]
        print('Algorithm changed to', self.algorithm)

    def split_secret_dynamic(self):

        users_count = self.number_of_users.value()
        secrets_count = self.number_of_secrets.value()

        # Get secrets
        secrets = [None] * secrets_count
        try:
            for s in range(secrets_count):
                secret_text = self.secret_inputs[s].text()
                secret_bytes = bytes([ord(char) for char in secret_text])
                secrets[s] = int.from_bytes(secret_bytes, byteorder='big')
        except ValueError as e:
            print('Secrets missing. Error %r' % e)
            self.showdialog()
            return

        prime = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1

        # Using list comprehension, with [[]]*secrets_count we would obtain copies of the same list
        access_structures = [[] for _ in range(secrets_count)]

        for s in range(secrets_count):
            list_of_users = [(user + 1) * int(checkbox.isChecked()) for
                             user, checkbox
                             in enumerate(self.checkboxes[s]) if
                             checkbox.isChecked()]
            # GUI supports only a single access group to a secret
            access_structures[s].append(list_of_users)

        print(access_structures)
        try:
            if self.algorithm == 'Roy-Adhikari':
                dealer = multisecret.MultiSecretRoyAdhikari.Dealer(prime,
                                                                   users_count,
                                                                   secrets,
                                                                   access_structures)
            elif self.algorithm == 'Lin-Yeh':
                dealer = multisecret.MultiSecretLinYeh.Dealer(prime,
                                                              users_count,
                                                              secrets,
                                                              access_structures)
            elif self.algorithm == 'Herranz-Ruiz-Saez':
                dealer = multisecret.MultiSecretHerranzRuizSaez.Dealer(prime,
                                                              users_count,
                                                              secrets,
                                                              access_structures)
            else:
                print('Wrong algorithm, cannot split.')
                return

        except ValueError as e:
            self.showdialog(str(e))
            print('Error %r' % e)
            return
        dealer.split_secrets()
        self.save_pseudo_shares_to_file(dealer)
        print('Split secret using', self.algorithm)

    def load_public_info_dynamic(self):
        # read public info from json
        self.load_public_reconstruction_info()
        # Show information about secrets and privileged users
        access_structure = self.public_info['access_structures']

        # after loading public info, change GUI to current secrets and users number
        self.user_count = multisecret.MultiSecretCommon.user_count_from_access_structure(
            access_structure)
         # create container for user shares which will be loaded
        self.user_data = [None] * self.user_count

        self.secret_count = len(access_structure)
        self.refresh_dynamic_combine_tab(self.secret_count, self.user_count,
                                         self.gridLayout_dyn_reconstr,
                                         self.gridLayoutWidget_dyn_reconstr)

        self.textBrowser_dyn.append(
            'Public info loaded. There are {} secrets.\nThe algorithm is {}.'.format(
                self.secret_count, self.public_info['algorithm']))
        for secret, group in enumerate(access_structure):
            self.textBrowser_dyn.append(
                'Secret {} can be obtained by {}.'.format(secret, str(group)))

    def combine_secret_dynamic(self):
        # if checkbox "reconstruct all at once" is checked, run loop
        print('combine_secret_dynamic')
        self.combine_secret()

    def showdialog(self, text='Please specify all secrets.'):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText(text)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def save_pseudo_shares_to_file(self, dealer):
        """ Save python dictionary with data needed for secret reconstruction.
            jsonpickle is used for encoding because data contains bytes objects,
            not recognized by json encoder """

        # Save public data to public_info.json
        # TODO: add timestamps and FileChooser dialogs
        public_info = {'prime': dealer.p,
                       'access_structures': dealer.access_structures,
                       'public_shares_M': dealer.public_shares_M,
                       'algorithm': self.algorithm}

        public_info_json_string = jsonpickle.encode(public_info)
        with open('public_info.json', 'w') as public_info_file:
            json.dump(public_info_json_string, public_info_file)

        # Save user shares (for each secret and group) and user ID to json file
        for user in range(1, dealer.n + 1):
            user_shares = dealer.get_pseudo_shares_for_participant(user)
            user_data = {'user': user,
                         'id': dealer.random_id[user - 1],
                         'shares': user_shares}

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
            self.textBrowser.append(
                'Cannot open file {}'.format('public_info.json'))
            return

        self.public_info = jsonpickle.decode(json_string)
        self.algorithm = self.public_info['algorithm']
        print('loaded data from JSON', self.public_info)

    def load_pseudo_shares_from_user(self, participant):
        """ Load user ID and user's pseudo shares for each secret.
        """
        self.textBrowser_dyn.append(
            'Load pseudo shares from user {}...'.format(participant))

        userfile = 'user' + str(participant) + '.json'
        try:
            with open(userfile, 'r') as file:
                json_string = json.load(file)
        except FileNotFoundError as e:
            print('caught error %r' % e)
            self.textBrowser_dyn.append('Cannot open file {}'.format(userfile))
            return

        self.user_data[participant - 1] = jsonpickle.decode(json_string)
        print('loaded data from JSON', self.user_data[participant - 1])

    def combine_secret(self):
        """ Combine secret from JSON loaded information.
            TODO: Validate all pieces needed to reconstruct.
        """
        try:
            if self.algorithm == 'Roy-Adhikari':
                combiner = multisecret.MultiSecretRoyAdhikari.Dealer(
                    self.public_info['prime'],
                    self.user_count,
                    [0] * self.secret_count,
                    self.public_info['access_structures'])
            elif self.algorithm == 'Lin-Yeh':
                combiner = multisecret.MultiSecretLinYeh.Dealer(
                    self.public_info['prime'],
                    self.user_count,
                    [0] * self.secret_count,
                    self.public_info['access_structures'])
            elif self.algorithm == 'Herranz-Ruiz-Saez':
                combiner = multisecret.MultiSecretHerranzRuizSaez.Dealer(
                    self.public_info['prime'],
                    self.user_count,
                    [0] * self.secret_count,
                    self.public_info['access_structures'])
            else:
                print('Wrong algorithm, cannot combine.')
                return

            self.textBrowser_dyn.append('Combine secret using {} algorithm.'.format(self.algorithm))
            combiner.public_shares_M = self.public_info['public_shares_M']
        except AttributeError as e:
            print('caught error %r' % e)
            self.textBrowser_dyn.append(
                'There is not enough information to reconstruct!')
            return

        combiner.random_id = [None] * combiner.n

        # create a structure for pseudo shares
        combiner.pseudo_shares = deepcopy(combiner.access_structures)
        combiner.key_shares = deepcopy(combiner.access_structures)

        #try:
        for user in range(1, combiner.n + 1):
            # ID from user
            print('\nID from user', self.user_data[user - 1]['id'])
            combiner.random_id[user - 1] = self.user_data[user - 1]['id']

            # pseudo shares from user
            print(self.user_data[user - 1])
            user_shares = self.user_data[user - 1]['shares']
            assert isinstance(user_shares, dict)
            combiner.set_pseudo_shares_from_participant(user, user_shares)

        #except TypeError as e:
        #    print('caught error %r' % e)
        #    self.textBrowser_dyn.append(
        #        'You have not loaded all shares. Cannot reconstruct!')
        #    return

        if self.algorithm == 'Herranz-Ruiz-Saez':
            print('In HRS algorithm, key shares:', combiner.key_shares)

            print('HRS, combine secret', self.secret_to_combine)

            obtained_shares = combiner.key_shares
            del combiner.pseudo_shares
        else:
            obtained_shares = combiner.pseudo_shares

        # in GUI it's only possible to create 1 access group for secret
        access_group = 0

        if self.algorithm == 'Herranz-Ruiz-Saez':
            secret = combiner.combine_secret(
                self.secret_to_combine, access_group,
                obtained_shares) # Herranz scheme don't use access groups
        else:
            secret = combiner.combine_secret(
                self.secret_to_combine, access_group,
                obtained_shares[self.secret_to_combine][access_group])

        # decode secret
        secret_bytes = secret.to_bytes(bytehelper.bytelen(secret),
                                       byteorder='big')
        secret_text = ''.join([chr(num) for num in secret_bytes])

        self.textBrowser_dyn.append('Combined a secret: s{} = {}'.format(
            self.secret_to_combine, secret_text))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = MultiSecretController()

    sys.exit(app.exec_())
