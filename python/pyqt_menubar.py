import sys
from PyQt5 import QtWidgets, QtGui


class Gui(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):               
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Menubar')    
        #self.show()
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
 
        self.show()
 
class MyTableWidget(QtWidgets.QWidget):        
 
    def __init__(self, parent):   
        super(QtWidgets.QWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()	
        self.tab2 = QtWidgets.QWidget()
        self.tabs.resize(300,200) 
 
        # Add tabs
        self.tabs.addTab(self.tab1,"Tab 1")
        self.tabs.addTab(self.tab2,"Tab 2")
 
        # Create first tab
        self.tab1.layout = QtWidgets.QVBoxLayout(self)
        self.pushButton1 = QtWidgets.QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)
 
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def draw_combine_tab(self, secrets, users, layout):
        """ Draw widgets for combining secrets in a layout.
            Can be called again when the number of secrets/users change. """

        # TODO: implement here ui_controller -> refresh_dynamic_combine_tab(self, secrets, users):

        # TODO: in this class refactor drawing GUI, then add MenuBar and StatusBar


class Controller(Gui):
    def __init__(self):
        super(Controller, self).__init__()
        print('Controller initialized!')

        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())  
    
