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

apiKey = ""

class BuildMatchHistory(QWidget):
    
    def __init__(self):
        super(QWidget,  self).__init__()
        config = SafeConfigParser()
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        config.read(configFileLocation)
        apiKey = config.get('main', 'apiKey')
    
    def buildMatch(self, matchIndex):
        
        # Open match_history.txt and store json data in matchHistoryData
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history.txt'
        f = open(fileLocation,  'r')
        matchHistoryData = json.load(f)
        matchHistoryData = json.loads(matchHistoryData)
        
        # Load champion name and lane from matchHistoryData
        championId = matchHistoryData["matches"][matchIndex]["champion"]
        championName = self.getChampionName(championId)
        lane = matchHistoryData["matches"][matchIndex]["lane"].lower().capitalize()
        
        # Close the open file
        f.close()
        
        # Build the match GroupBox itself with the champion name played as the title
        match = QGroupBox(championName)
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
        laneLabel.setText(lane)
        
        return match
    
    def buildMatchHistory(self,  mainWindow):
        
        # Open match_history.txt and store json data in matchHistoryData
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history.txt'
        f = open(fileLocation,  'r')
        matchHistoryData = json.load(f)
        matchHistoryData = json.loads(matchHistoryData)
        
        # Find the number of matches in matchHistoryData
        numberOfMatches = matchHistoryData["totalGames"]
        
        # Close the open file
        f.close()
        
        # Container Widget       
        widget = QWidget()
        # Layout of Container Widget
        layout = QVBoxLayout(self)
        for matchIndex in range(numberOfMatches):
            match = self.buildMatch(matchIndex)
            layout.addWidget(match)
        widget.setLayout(layout)
        
        # Scroll Area Properties
        matchHistory = mainWindow.ui.matchHistoryScrollArea
        matchHistory.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        matchHistory.setWidgetResizable(True)
        matchHistory.setWidget(widget)
    
    def calculateAverages(self):
        pass
    
    def checkResponseCode(self,  response):
        codes = {
            200: "ok", 
            400: "bad request", 
            401: "unauthorized", 
            404: "entity not found", 
            429: "rate limit exceeded", 
            500: "internal server error", 
            503: "service unavailable"
        }
        responseMessage = codes.get(response.status_code,  response.status_code)
        return str(responseMessage)
    
    def getChampionName(self, championId):
        
        # Check if config file has a section for champions
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        hasSection = config.has_section('champions')
        
        # If so, check if we already know what the champion name is from prior API calls
        if hasSection:
            hasChampName = config.has_option('champions',  str(championId))
            if hasChampName:
                championName = config.get('champions',  str(championId))
                return championName
            else:
                pass
        
        # If we don't have the section altogether, make it and then make the API call
        else:
            config.add_section('champions')
            with open(configFileLocation, 'w') as f:
                config.write(f)
            config.read(configFileLocation)
        
        # If we get to this point, we make the API call and store the names of all champions in the config file
        requestURL = ("https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?champData=info&api_key=" + apiKey)
        championListResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(championListResponse)
        if responseMessage == "ok":
            championListResponse = championListResponse.text
            championListResponse = json.loads(championListResponse)
            championListResponse = championListResponse["data"]
            for champion in championListResponse:
                championId = championListResponse[champion]["id"]
                championName = championListResponse[champion]["name"]
                config.set('champions', str(championId), championName)
            with open(configFileLocation, 'w') as f:
                config.write(f)
            config.read(configFileLocation)
            if config.has_option('champions',  str(championId)):
                championName = config.get('champions',  str(championId))
                return championName
            else:
                print "An error occurred in getChampionName method"
                return "Champion name unknown"
        else:
            print responseMessage + ", from getChampionName method"
            return "Champion name unknown"
    
    def parseMatchHistoryDetails(self):
        pass
