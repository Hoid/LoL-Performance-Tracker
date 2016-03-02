# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1706, 1120)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.mainTabView = QtGui.QTabWidget(self.centralwidget)
        self.mainTabView.setGeometry(QtCore.QRect(50, 160, 1611, 871))
        self.mainTabView.setStatusTip(_fromUtf8(""))
        self.mainTabView.setWhatsThis(_fromUtf8(""))
        self.mainTabView.setTabPosition(QtGui.QTabWidget.North)
        self.mainTabView.setTabShape(QtGui.QTabWidget.Rounded)
        self.mainTabView.setIconSize(QtCore.QSize(32, 32))
        self.mainTabView.setElideMode(QtCore.Qt.ElideNone)
        self.mainTabView.setObjectName(_fromUtf8("mainTabView"))
        self.soloQueueTab = QtGui.QWidget()
        self.soloQueueTab.setObjectName(_fromUtf8("soloQueueTab"))
        self.mainTabView.addTab(self.soloQueueTab, _fromUtf8(""))
        self.compareTab = QtGui.QWidget()
        self.compareTab.setObjectName(_fromUtf8("compareTab"))
        self.mainTabView.addTab(self.compareTab, _fromUtf8(""))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(50, 30, 1611, 111))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.summonerNameLabel = QtGui.QLabel(self.groupBox)
        self.summonerNameLabel.setGeometry(QtCore.QRect(70, 40, 471, 51))
        self.summonerNameLabel.setObjectName(_fromUtf8("summonerNameLabel"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1706, 38))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.mainTabView.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "LoL Performance Tracker", None))
        self.mainTabView.setToolTip(_translate("MainWindow", "<html><head/><body><p>Solo Queue</p></body></html>", None))
        self.mainTabView.setTabText(self.mainTabView.indexOf(self.soloQueueTab), _translate("MainWindow", "Solo Queue", None))
        self.mainTabView.setTabText(self.mainTabView.indexOf(self.compareTab), _translate("MainWindow", "Summoner Comparison", None))
        self.groupBox.setTitle(_translate("MainWindow", "Summoner Info", None))
        self.summonerNameLabel.setText(_translate("MainWindow", "Stuff", None))

