# Filename: buildMatchHistory.py
#
# Description: This file contains the buildMatchHistory class that parses match_history.txt
# and match_history_details.txt, creates averages for the user, and builds the UI assets
# that hold match information to be put into the matchHistoryScrollArea container.

import sys, os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

import requests,  json
from ConfigParser import SafeConfigParser

class BuildMatchHistory(QWidget):
    
    def __init__(self):
        super(QWidget,  self).__init__()
    
    def buildMatch(self):
        champion = "champion"
        match = QGroupBox(champion)
        match.setFixedHeight(170)
        match.setFixedWidth(940)
        
        # Build the grid layout that holds multiple statistics GroupBox's
#        statisticsGridLayout = QGridLayout()
#        statisticsGridLayout
        
        return match
    
    def buildMatchHistory(self,  mainWindow):
        
        # Container Widget       
        widget = QWidget()
        # Layout of Container Widget
        layout = QVBoxLayout(self)
        for _ in range(20):
            match = self.buildMatch()
            layout.addWidget(match)
        widget.setLayout(layout)

        # Scroll Area Properties
        matchHistory = mainWindow.ui.matchHistoryScrollArea
        matchHistory.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        matchHistory.setWidgetResizable(True)
        matchHistory.setWidget(widget)
    
    def calculateAverages(self):
        pass
    
    def parseMatchHistoryDetails(self):
        pass
