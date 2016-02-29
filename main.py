import sys
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import uic

import showMainWindow

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(QMainWindow,  self).__init__()
        self.ui = uic.loadUi('C:/Users/cheek/Documents/Code/LoL-Performance-Tracker/MainWindow.ui')
        self.ui.show()




def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()
