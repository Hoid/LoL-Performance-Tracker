# Filename: MatchHistoryBuilder.py
#
# Description: This file contains the MatchHistoryBuilder class that parses match_history.txt
# and match_history_details.txt, creates averages for the user, and builds the UI assets
# that hold match information to be put into the matchHistoryScrollArea container.

import sys, os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

import requests,  json
from ConfigParser import SafeConfigParser

class MatchHistoryBuilder(QObject):
    
    def __init__(self):
        super(QObject,  self).__init__()
        
        self.config = SafeConfigParser()
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        self.config.read(configFileLocation)
        self.apiKey = str(self.config.get('main',  'apiKey'))
        if not self.apiKey:
            # Pull api_key from internal file
            print "Was forced to use api_key.txt in MatchHistoryBuilder"
            apiKeyFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\api_key.txt"
            with open(apiKeyFileLocation, 'r') as f:
                self.apiKey = f.read()
            if not self.apiKey:
                print "no API Key available"
    
    def buildMatch(self, summonerId, matchIndex, matchId):
        # This method takes the matchIndex and matchId as an input, builds a match object, and returns it. 
        # Globals: none
        
        # Check whether we have match data for the matchID in question. If we do, 
        # continue. If not, call getMatchDetails for the match and store that data in match_history_details.txt.
        matchId = int(matchId)
        knownMatchIds = self.matchHistoryDetails.keys()
        knownMatchIds = map(int, knownMatchIds)
        if matchId not in knownMatchIds:
            self.matchHistoryDetails[matchId] = self.getMatchDetails(summonerId, matchId)
        
        # Load champion name from getChampionName() and lane from matchHistoryList
        championId = self.matchHistoryList["matches"][matchIndex]["champion"]
        championName = self.getChampionName(championId)
        lane = self.matchHistoryList["matches"][matchIndex]["lane"].lower().capitalize()
        
        # Build the match GroupBox itself with the champion name as the title
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
    
    def calculateAverages(self):
        pass
    
    def checkResponseCode(self,  response):
        # This method takes the API call response as input and returns a response message
        # If the code was as expected of a successful request, we return "ok". Otherwise we return
        # a response message that corresponds to the code.
        # Globals: none
        
        codes = {
            200: "ok", 
            400: "bad request", 
            401: "unauthorized", 
            404: "entity not found", 
            429: "rate limit exceeded", 
            500: "internal server error", 
            503: "service unavailable"
        }
        responseMessage = codes.get(response.status_code,  "response code" + str(response.status_code) + " not recognized")
        return str(responseMessage)
    
    def getChampionName(self, championId):
        # This method takes the championId as input and returns the champion name associated with it
        # If our config file doesn't have the champion name, it makes an API call to get a list of all 
        # champion names and stores them in config
        # Globals: none
        
        # Check if config file has a section for champions
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        self.config.read(configFileLocation)
        hasSection = self.config.has_section('champions')
        
        # If so, check if we already know what the champion name is from prior API calls
        if hasSection:
            hasChampName = self.config.has_option('champions',  str(championId))
            if hasChampName:
                championName = self.config.get('champions',  str(championId))
                return championName
            else:
                pass
        
        # If we don't have the section altogether, make it and then make the API call
        else:
            self.config.add_section('champions')
            with open(configFileLocation, 'w') as f:
                self.config.write(f)
            self.config.read(configFileLocation)
        
        # If we get to this point, we make the API call and store the names of all champions in the config file
        requestURL = ("https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?champData=info&api_key=" + self.apiKey)
        championListResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(championListResponse)
        if responseMessage == "ok":
            championListResponse = json.loads(championListResponse.text)
            championListResponse = championListResponse["data"]
            for champion in championListResponse:
                championId = championListResponse[champion]["id"]
                championName = championListResponse[champion]["name"]
                self.config.set('champions', str(championId), championName)
            with open(configFileLocation, 'w') as f:
                self.config.write(f)
            self.config.read(configFileLocation)
            if self.config.has_option('champions',  str(championId)):
                championName = self.config.get('champions',  str(championId))
                return championName
            else:
                print "An error occurred while trying to write the config file, from in getChampionName method"
                return None
        else:
            print responseMessage + ", from getChampionName method"
            return None
    
    def getMatchHistory(self,  summonerId):
        # This method takes the summonerId as input and fetches basic match history data and 
        # returns it as a usable json object
        # Globals: none
        
        requestURL = ("https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/" + str(summonerId) + "?seasons=SEASON2016&api_key=" + self.apiKey)
        matchHistoryResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(matchHistoryResponse)
        if responseMessage == "ok":
            matchHistoryResponse = json.loads(matchHistoryResponse.text)
            return matchHistoryResponse
        else:
            print responseMessage + ", from getMatchHistory method"
            return None

    def getMatchDetails(self,  summonerId, matchId):
        # This method takes the summonerId and matchId as inputs and fetches detailed match history data 
        # for the match indicated and returns it as a usable json object
        # Globals: none
        
        requestURL = ("https://na.api.pvp.net/api/lol/na/v2.2/match/" 
                                + str(matchId) + "?api_key=" 
                                + self.apiKey)
        matchDetailsResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(matchDetailsResponse)
        if responseMessage == "ok":
            matchDetailsResponse = json.loads(matchDetailsResponse.text)
            return matchDetailsResponse
        else:
            print "For match " + str(matchId) + ", " + responseMessage + ", from getMatchDetails method"
            return None 
    
    def parseMatchHistoryDetails(self):
        pass
    
    def updateMatchHistoryVariables(self, newMatchHistoryList, matchHistoryDetails):
        # This method refreshes the self.matchHistoryList and self.matchHistoryDetails variables in this class.
        # Globals: self.matchHistoryList, self.matchHistoryDetails
        
        self.matchHistoryList = newMatchHistoryList
        self.matchHistoryDetails = matchHistoryDetails
