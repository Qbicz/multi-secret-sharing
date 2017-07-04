from PyQt5 import QtCore, QtWidgets
import functools

class MultiSecretGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        print('__init__ MultiSecretGui')
        self.secrets = 3
        self.users = 3
        self.setup_ui()

    def add_menu_bar(self):
        exitAction = QtWidgets.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)

        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    def setup_ui(self):
        self.resize(751, 481)
        self.add_menu_bar()

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.tabWidget = QtWidgets.QTabWidget(self)
        #self.tabWidget.setGeometry(QtCore.QRect(0, 0, 751, 481))

        # put QTabWidget in a layout to enable resizing
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        layout.addWidget(self.tabWidget)

        self.tab = QtWidgets.QWidget()

        #
        # Dynamically created split tab
        #
        self.tab_dyn = QtWidgets.QWidget(self)
        self.gridLayoutWidget_dyn = QtWidgets.QWidget(self.tab_dyn)
        self.gridLayoutWidget_dyn.setGeometry(QtCore.QRect(10, 40, 711, 391))
        self.gridLayout_dyn = QtWidgets.QGridLayout(self.gridLayoutWidget_dyn)
        self.gridLayout_dyn.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        _translate = QtCore.QCoreApplication.translate

        #self.algorithm_label = QtWidgets.QLabel(self.gridLayoutWidget_dyn)
        #self.gridLayout_dyn.addWidget(self.algorithm_label, 0, 0, 1, 1)
        #self.algorithm_label.setText('Algorithm ')

        self.secret_labels = [None]*self.secrets
        self.secret_inputs = [None]*self.secrets
        self.checkboxes = [[[None] for _ in range(self.users)] for _ in range(self.secrets)]

        for secret in range(self.secrets):
            self.secret_labels[secret] = QtWidgets.QLabel(self.gridLayoutWidget_dyn)
            self.gridLayout_dyn.addWidget(self.secret_labels[secret], secret+1, 0, 1, 1)

            self.secret_inputs[secret] = QtWidgets.QLineEdit(self.gridLayoutWidget_dyn)
            self.gridLayout_dyn.addWidget(self.secret_inputs[secret], secret+1, 1, 1, 1)

            for user in range(self.users):
                self.checkboxes[secret][user] = QtWidgets.QCheckBox(self.gridLayoutWidget_dyn)
                self.gridLayout_dyn.addWidget(self.checkboxes[secret][user], secret+1, 2+user, 1, 1)
                self.checkboxes[secret][user].setText(_translate("multisecret_gui", "User "+str(user+1)))

        self.algorithm_label = QtWidgets.QLabel(self.gridLayoutWidget_dyn)
        self.gridLayout_dyn.addWidget(self.algorithm_label,
                                      self.secrets + 1, 0, 1, 1)
        self.algorithm_label.setText('Algorithm ')

        self.algorithm_combobox = QtWidgets.QComboBox(self.gridLayoutWidget_dyn)
        self.gridLayout_dyn.addWidget(self.algorithm_combobox,
                                      self.secrets + 1, 1, 1, self.users)
        self.algorithm_combobox.addItem('Roy-Adhikari')
        self.algorithm_combobox.addItem('Lin-Yeh')
        self.algorithm_combobox.currentIndexChanged.connect(self.update_algorithm)

        self.button_split_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn)
        self.gridLayout_dyn.addWidget(self.button_split_dyn,
                                      self.secrets + 2, 1, 1, self.users)
        self.button_split_dyn.setText('Split secrets')

        self.button_split_dyn.clicked.connect(self.split_secret_dynamic)

        self.tabWidget.addTab(self.tab_dyn, "")
        # end of tab

        #
        # Dynamically created reconstruction tab
        #
        self.tab_dyn_reconstr = QtWidgets.QWidget()
        self.gridLayoutWidget_dyn_reconstr = QtWidgets.QWidget(self.tab_dyn_reconstr)
        self.gridLayoutWidget_dyn_reconstr.setGeometry(QtCore.QRect(10, 40, 711, 391))
        self.gridLayout_dyn_reconstr = QtWidgets.QGridLayout(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        _translate = QtCore.QCoreApplication.translate
        self.reconstr_user_labels = [None] * self.users
        self.user_data_reconstr_buttons = [None] * self.users

        self.button_load_public_info_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.addWidget(self.button_load_public_info_dyn, 0, 0, 1, 1)
        self.button_load_public_info_dyn.clicked.connect(self.load_public_info_dynamic)

        for user in range(self.users):
            self.user_data_reconstr_buttons[user] = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
            self.gridLayout_dyn_reconstr.addWidget(self.user_data_reconstr_buttons[user], user+1, 0, 1, 1)
            # Connect loading pseudo shares to each button
            print('connect user', user)
            self.user_data_reconstr_buttons[user].clicked.connect(
                functools.partial(self.load_pseudo_shares_from_user, user + 1))

        self.button_reconstr_dyn = QtWidgets.QPushButton(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.addWidget(self.button_reconstr_dyn, 0, 1, 1, 1)
        self.button_reconstr_dyn.clicked.connect(self.combine_secret_dynamic)

        # Spinbox for choosing a secret to reconstruct
        self.spinbox_secret = QtWidgets.QSpinBox()
        self.gridLayout_dyn_reconstr.addWidget(self.spinbox_secret, 0, 2, 1, 1)
        self.spinbox_secret.setRange(0, self.secrets - 1)
        self.spinbox_secret.valueChanged.connect(self.choose_secret_to_combine)

        self.textBrowser_dyn = QtWidgets.QTextBrowser(self.gridLayoutWidget_dyn_reconstr)
        self.gridLayout_dyn_reconstr.addWidget(self.textBrowser_dyn, 1, 1, 4, 3)

        self.tabWidget.addTab(self.tab_dyn_reconstr, "")
        # end of tab

        #
        # Problem size tab
        #
        self.tab_3 = QtWidgets.QWidget()
        self.layoutWidget = QtWidgets.QWidget(self.tab_3)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 691, 181))
        self.gridLayout_3 = QtWidgets.QGridLayout(self.layoutWidget)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.number_of_secrets = QtWidgets.QSpinBox(self.layoutWidget)
        self.number_of_secrets.setMinimum(2)
        self.number_of_secrets.setMaximum(16)
        self.gridLayout_3.addWidget(self.number_of_secrets, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.gridLayout_3.addWidget(self.label_2, 0, 2, 1, 1)
        self.number_of_users = QtWidgets.QSpinBox(self.layoutWidget)
        self.number_of_users.setMinimum(2)
        self.gridLayout_3.addWidget(self.number_of_users, 0, 3, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        # end of tab

        self.actionSetSecretsNumber = QtWidgets.QAction(self)
        self.actionSetSecretsNumber.setObjectName("actionSetSecretsNumber")

        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.show()


    def retranslateUi(self, multisecret_gui):
        _translate = QtCore.QCoreApplication.translate
        multisecret_gui.setWindowTitle(_translate("multisecret_gui", "Multi-secret Sharing Tool"))

        # Text for problem size tab
        self.label.setText(_translate("multisecret_gui", "Number of secrets"))
        self.label_2.setText(_translate("multisecret_gui", "Number of users"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("multisecret_gui", "Problem size"))

        # Text for dynamic split tab
        for secret in range(self.secrets):
            self.secret_labels[secret].setText(_translate("multisecret_gui", "Secret "+str(secret+1)))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_dyn), _translate("multisecret_gui", "Dynamic split"))

        # Text for dynamic reconstruction tab
        for user in range(self.users):
            self.user_data_reconstr_buttons[user].setText(_translate("multisecret_gui", "Load pseudo share from user "+str(user+1)+"..."))
        self.button_reconstr_dyn.setText(_translate("multisecret_gui", "Reconstruct secret"))
        self.button_load_public_info_dyn.setText(_translate("multisecret_gui", "Load public info"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_dyn_reconstr), _translate("multisecret_gui", "Dynamic reconstruction"))

        self.actionSetSecretsNumber.setText(_translate("multisecret_gui", "setSecretsNumber"))
