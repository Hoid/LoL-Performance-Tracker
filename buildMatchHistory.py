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
        
        # Build the match GroupBox itself with the champion name played as the title
        champion = "champion"
        match = QGroupBox(champion)
        match.setFixedHeight(170)
        match.setFixedWidth(940)
        
        # For each match, build GroupBox's for statistics and set their sizes, positions, and object names
        scoreBox = QGroupBox(match)
        scoreBox.setFixedWidth(130)
        scoreBox.setFixedHeight(60)
        scoreBox.setGeometry(QRect(280, 20, 130, 60))
        scoreBox.setAlignment(Qt.AlignCenter)
        scoreBox.setObjectName("scoreBox")
        killParticipationPercentBox = QGroupBox(match)
        killParticipationPercentBox.setFixedWidth(130)
        killParticipationPercentBox.setFixedHeight(60)
        killParticipationPercentBox.setGeometry(QRect(440, 20, 130, 60))
        killParticipationPercentBox.setAlignment(Qt.AlignCenter)
        killParticipationPercentBox.setObjectName("killParticipationPercentBox")
        goldPerMinBox = QGroupBox(match)
        goldPerMinBox.setFixedWidth(130)
        goldPerMinBox.setFixedHeight(60)
        goldPerMinBox.setGeometry(QRect(440, 90, 130, 60))
        goldPerMinBox.setAlignment(Qt.AlignCenter)
        goldPerMinBox.setObjectName("goldPerMinBox")
        kdaBox = QGroupBox(match)
        kdaBox.setFixedWidth(130)
        kdaBox.setFixedHeight(60)
        kdaBox.setGeometry(QRect(280, 90, 130, 60))
        kdaBox.setAlignment(Qt.AlignCenter)
        kdaBox.setObjectName("kdaBox")
        wardScoreBox = QGroupBox(match)
        wardScoreBox.setFixedWidth(130)
        wardScoreBox.setFixedHeight(60)
        wardScoreBox.setGeometry(QRect(600, 20, 130, 60))
        wardScoreBox.setAlignment(Qt.AlignCenter)
        wardScoreBox.setObjectName("wardScoreBox")
        csPerMinBox = QGroupBox(match)
        csPerMinBox.setFixedWidth(130)
        csPerMinBox.setFixedHeight(60)
        csPerMinBox.setGeometry(QRect(600, 90, 130, 60))
        csPerMinBox.setAlignment(Qt.AlignCenter)
        csPerMinBox.setObjectName("groupBox_7")
        changeInLPLabel = QLabel(match)
        changeInLPLabel.setGeometry(QRect(820, 90, 101, 61))
        changeInLPLabel.setObjectName("changeInLP")
        laneLabel = QLabel(match)
        laneLabel.setGeometry(QRect(20, 100, 141, 51))
        laneLabel.setStyleSheet("font: 10pt \"Verdana\";")
        laneLabel.setObjectName("lane")
        
        # Set titles of each item
        scoreBox.setTitle("score")
        killParticipationPercentBox.setTitle("Kill part. %")
        goldPerMinBox.setTitle("gold/min")
        kdaBox.setTitle("KDA")
        wardScoreBox.setTitle("ward score")
        csPerMinBox.setTitle("cs/min")
        changeInLPLabel.setText("+lp")
        laneLabel.setText("Lane")
        
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
