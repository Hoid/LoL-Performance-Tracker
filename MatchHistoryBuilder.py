# Filename: MatchHistoryBuilder.py
#
# Description: This file contains the MatchHistoryBuilder class that parses match_history.txt
# and match_history_details.txt, creates averages for the user, and builds the UI assets
# that hold match information to be put into the matchHistoryScrollArea container.

import sys, os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from decimal import *

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
        
        self.matchHistoryStatistics = {}
    
    def buildMatch(self, summonerId, matchIndex, matchId):
        # This method takes the matchIndex and matchId as an input, builds a match object, and returns it. As a part of 
        # building each match object, this method calls calculateMatchStatistics() and calculateAverages. It might be 
        # prudent later to only call self.calculateAverages() once, rather than every time, but I'm not sure.
        # Globals: none
        
        # Check whether we have match data for the matchID in question. If we do, 
        # continue. If not, call getMatchDetails for the match and store that data in matchHistoryDetails.
        # Keys of the matchHistoryDetails dictionary will be unicode strings. Convert the matchId to unicode 
        # before using as a key or lookup element.
        matchId = unicode(matchId)
        knownMatchIds = self.matchHistoryDetails.keys()
        if matchId not in knownMatchIds:
            self.matchHistoryDetails[matchId] = self.getMatchDetails(summonerId, matchId)
        
        self.calculateAverages()
        
        # Load champion name from getChampionName() and lane from matchHistoryList
        championId = self.matchHistoryList["matches"][matchIndex]["champion"]
        championName = self.getChampionName(championId)
        
        # Build the match GroupBox itself with the champion name as the title
        match = QGroupBox(championName)
        match.setFixedHeight(180)
        match.setFixedWidth(898)
        
        # Build GroupBox's for statistics and set their sizes, positions, and object names
        scoreBox = QGroupBox(match)
        killParticipationPercentBox = QGroupBox(match)
        goldPerMinBox = QGroupBox(match)
        kdaBox = QGroupBox(match)
        wardScoreBox = QGroupBox(match)
        csPerMinBox = QGroupBox(match)
        laneLabel = QLabel(match)
        resultLabel = QLabel(match)
        
        scoreBox.setFixedWidth(130)
        scoreBox.setFixedHeight(70)
        scoreBox.setGeometry(QRect(280, 20, 130, 70))
        scoreBox.setAlignment(Qt.AlignCenter)
        scoreBox.setTitle("score")
        scoreBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        scoreBox.setToolTip("Score, in the format of kills-deaths-assists")
        
        scoreValue = QLabel(scoreBox)
        scoreValue.setFixedWidth(130)
        scoreValue.setFixedHeight(70)
        scoreValue.setGeometry(QRect(0, 10, 120, 60))
        scoreValue.setAlignment(Qt.AlignCenter)
        scoreValue.setStyleSheet('font: 9pt "Calibri";')
        
        killParticipationPercentBox.setFixedWidth(130)
        killParticipationPercentBox.setFixedHeight(70)
        killParticipationPercentBox.setGeometry(QRect(440, 20, 130, 70))
        killParticipationPercentBox.setAlignment(Qt.AlignCenter)
        killParticipationPercentBox.setTitle("Kill part. %")
        killParticipationPercentBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        killParticipationPercentBox.setToolTip("The percentage of your teams kills you contributed to")
        
        killParticipationPercentValue = QLabel(killParticipationPercentBox)
        killParticipationPercentValue.setFixedWidth(130)
        killParticipationPercentValue.setFixedHeight(70)
        killParticipationPercentValue.setGeometry(QRect(0, 10, 120, 60))
        killParticipationPercentValue.setAlignment(Qt.AlignCenter)
        killParticipationPercentValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        
        goldPerMinBox.setFixedWidth(130)
        goldPerMinBox.setFixedHeight(70)
        goldPerMinBox.setGeometry(QRect(440, 90, 130, 70))
        goldPerMinBox.setAlignment(Qt.AlignCenter)
        goldPerMinBox.setTitle("gold/min")
        goldPerMinBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        goldPerMinBox.setToolTip("Gold earned per minute")
        
        goldPerMinValue = QLabel(goldPerMinBox)
        goldPerMinValue.setFixedWidth(130)
        goldPerMinValue.setFixedHeight(70)
        goldPerMinValue.setGeometry(QRect(0, 10, 120, 60))
        goldPerMinValue.setAlignment(Qt.AlignCenter)
        goldPerMinValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        
        kdaBox.setFixedWidth(130)
        kdaBox.setFixedHeight(70)
        kdaBox.setGeometry(QRect(280, 90, 130, 70))
        kdaBox.setAlignment(Qt.AlignCenter)
        kdaBox.setTitle("KDA")
        kdaBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        kdaBox.setToolTip("Calculated by (kills+deaths)/assists")
        
        kdaValue = QLabel(kdaBox)
        kdaValue.setFixedWidth(130)
        kdaValue.setFixedHeight(70)
        kdaValue.setGeometry(QRect(0, 10, 120, 60))
        kdaValue.setAlignment(Qt.AlignCenter)
        
        wardScoreBox.setFixedWidth(130)
        wardScoreBox.setFixedHeight(70)
        wardScoreBox.setGeometry(QRect(600, 20, 130, 70))
        wardScoreBox.setAlignment(Qt.AlignCenter)
        wardScoreBox.setTitle("ward score")
        wardScoreBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        wardScoreBox.setToolTip("Calculated by wards placed + wards killed")
        
        wardScoreValue = QLabel(wardScoreBox)
        wardScoreValue.setFixedWidth(130)
        wardScoreValue.setFixedHeight(70)
        wardScoreValue.setGeometry(QRect(0, 10, 120, 60))
        wardScoreValue.setAlignment(Qt.AlignCenter)
        wardScoreValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        
        csPerMinBox.setFixedWidth(130)
        csPerMinBox.setFixedHeight(70)
        csPerMinBox.setGeometry(QRect(600, 90, 130, 70))
        csPerMinBox.setAlignment(Qt.AlignCenter)
        csPerMinBox.setTitle("cs/min")
        csPerMinBox.setStyleSheet('QGroupBox {font: 8pt "Calibri"}')
        csPerMinBox.setToolTip("Creeps killed per minute")
        
        csPerMinValue = QLabel(csPerMinBox)
        csPerMinValue.setFixedWidth(130)
        csPerMinValue.setFixedHeight(70)
        csPerMinValue.setGeometry(QRect(0, 10, 120, 60))
        csPerMinValue.setAlignment(Qt.AlignCenter)
        csPerMinValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        
        laneLabel.setGeometry(QRect(20, 120, 140, 50))
        laneLabel.setStyleSheet('font: 10pt "Calibri";')
        laneLabel.setToolTip("Lane")
        
        resultLabel.setFixedWidth(120)
        resultLabel.setFixedHeight(50)
        resultLabel.setGeometry(QRect(780, 20, 120, 50))
        resultLabel.setAlignment(Qt.AlignCenter)
        resultLabel.setStyleSheet('font: 12pt "Calibri"')
        resultLabel.setToolTip("Match result")
        
        # Set values for each item
        matchWon = self.matchHistoryStatistics["matches"][matchId]["won"]
        if matchWon:
            result = "Win"
        else:
            result = "Loss"
        score = self.matchHistoryStatistics["matches"][matchId]["score"]
        kda = self.matchHistoryStatistics["matches"][matchId]["kda"]
        kdaAverage = self.matchHistoryStatistics["kdaAverage"]
        killParticipationPercent = self.matchHistoryStatistics["matches"][matchId]["killParticipationPercent"]
        killParticipationPercentAverage = self.matchHistoryStatistics["killParticipationPercentAverage"]
        wardScore = self.matchHistoryStatistics["matches"][matchId]["wardScore"]
        wardScoreAverage = self.matchHistoryStatistics["wardScoreAverage"]
        goldPerMin = self.matchHistoryStatistics["matches"][matchId]["goldPerMin"]
        goldPerMinAverage = self.matchHistoryStatistics["goldPerMinAverage"]
        csPerMin = self.matchHistoryStatistics["matches"][matchId]["csPerMin"]
        csPerMinAverage = self.matchHistoryStatistics["csPerMinAverage"]
        lane = self.matchHistoryList["matches"][matchIndex]["lane"].lower().capitalize()
        if lane == "Bottom":
            lane = "Bot"
        
        resultLabel.setText(result)
        scoreValue.setText(str(score))
        kdaValue.setText(str(kda))
        killParticipationPercentValue.setText(str(killParticipationPercent))
        wardScoreValue.setText(str(wardScore))
        goldPerMinValue.setText(str(goldPerMin))
        csPerMinValue.setText(str(csPerMin))
        laneLabel.setText(lane)
        
        if result == "Win":
            resultLabel.setStyleSheet('color: green; font: 12pt "Calibri";')
        else:
            resultLabel.setStyleSheet('color: red; font: 12pt "Calibri";')
        if kda > kdaAverage:
            kdaValue.setStyleSheet('color: green; font: 9pt "Calibri";')
        else:
            kdaValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        if killParticipationPercent > killParticipationPercentAverage:
            killParticipationPercentValue.setStyleSheet('color: green; font: 9pt "Calibri";')
        else:
            killParticipationPercentValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        if wardScore > wardScoreAverage:
            wardScoreValue.setStyleSheet('color: green; font: 9pt "Calibri";')
        else:
            wardScoreValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        if goldPerMin > goldPerMinAverage:
            goldPerMinValue.setStyleSheet('color: green; font: 9pt "Calibri";')
        else:
            goldPerMinValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        if csPerMin > csPerMinAverage:
            csPerMinValue.setStyleSheet('color: green; font: 9pt "Calibri";')
        else:
            csPerMinValue.setStyleSheet('color: red; font: 9pt "Calibri";')
        
        return match
    
    def calculateAverages(self):
        # This method pulls the statistics for the matchId argument and includes them in the calculations of 
        # the user's new averages. This method calculates averages for the last 20 games in addition to the
        # averages over all games.
        # Globals: self.matchHistoryStatistics, self.matchHistoryDetails
        
        kdaTotalLastTwentyGames = 0
        killParticipationPercentTotalLastTwentyGames = 0
        wardScoreTotalLastTwentyGames = 0
        goldPerMinTotalLastTwentyGames = 0
        csPerMinTotalLastTwentyGames = 0
        kdaTotal = 0
        killParticipationPercentTotal = 0
        wardScoreTotal = 0
        goldPerMinTotal = 0
        csPerMinTotal = 0
        matchHistoryStatisticsData = self.matchHistoryStatistics["matches"]
        numberOfMatches = len(matchHistoryStatisticsData)
        
        for matchId, match in matchHistoryStatisticsData.iteritems():
            # If the match is in the first 20, include it in the last 20 games average. If not, just add it
            # to the total running all-time average.
            matchIndex = match["matchIndex"]
            if (numberOfMatches - matchIndex) < 20:
                kdaTotalLastTwentyGames += match["kda"]
                killParticipationPercentTotalLastTwentyGames += match["killParticipationPercent"]
                wardScoreTotalLastTwentyGames += match["wardScore"]
                goldPerMinTotalLastTwentyGames += match["goldPerMin"]
                csPerMinTotalLastTwentyGames += match["csPerMin"]
            kdaTotal += match["kda"]
            killParticipationPercentTotal += match["killParticipationPercent"]
            wardScoreTotal += match["wardScore"]
            goldPerMinTotal += match["goldPerMin"]
            csPerMinTotal += match["csPerMin"]
        
        kdaAverage = kdaTotal / numberOfMatches
        killParticipationPercentAverage = killParticipationPercentTotal / numberOfMatches
        wardScoreAverage = wardScoreTotal / numberOfMatches
        goldPerMinAverage = goldPerMinTotal / numberOfMatches
        csPerMinAverage = csPerMinTotal / numberOfMatches
        
        self.matchHistoryStatistics["kdaAverage"] = kdaAverage
        self.matchHistoryStatistics["killParticipationPercentAverage"] = killParticipationPercentAverage
        self.matchHistoryStatistics["wardScoreAverage"] = wardScoreAverage
        self.matchHistoryStatistics["goldPerMinAverage"] = goldPerMinAverage
        self.matchHistoryStatistics["csPerMinAverage"] = csPerMinAverage\
    
    def calculateStatistics(self, summonerId):
        # This method looks at self.matchHistoryList, and for every match, looks at self.matchHistoryDetails, 
        # calculates useful statistics for its matchId, and stores the statistics in the dictionary 
        # self.matchHistoryStatistics with the matchId as the key
        # Globals: self.matchHistoryStatistics, self.matchHistoryDetails
        
        matchHistoryListData = self.matchHistoryList["matches"]
        summonerId = int(summonerId)
        self.matchHistoryStatistics = {}
        self.matchHistoryStatistics["matches"] = {}
        
        for index, match in enumerate(matchHistoryListData):
            
            matchId = str(match["matchId"])
            matchDetails = self.matchHistoryDetails[unicode(matchId)]
            self.matchHistoryStatistics["matches"][matchId] = {}
            self.matchHistoryStatistics["matches"][matchId]["matchIndex"] = int(index)
        
            # Set participantId and participantIndex
            for index, participant in enumerate(matchDetails["participantIdentities"]):
                participantSummonerId = participant["player"]["summonerId"]
                if participantSummonerId == summonerId:
                    participantId = participant["participantId"]
                    participantIndex = index
            
            # Pull the match details for the user into a more usable variable
            participantDetails = matchDetails["participants"][participantIndex]
            
            # Set participantTeamNumber
            participantTeamId = participantDetails["teamId"]
            for index, team in enumerate(matchDetails["teams"]):
                teamNumber = team["teamId"]
                if team["teamId"] == participantTeamId:
                    participantTeamNumber = index
            
            # Calculate game result (win/lose)
            matchWon = matchDetails["teams"][participantTeamNumber]["winner"]
            self.matchHistoryStatistics["matches"][matchId]["won"] = matchWon
            
            # Calculate kda
            getcontext().prec = 3 # Sets the significant figures of precision to 3
            kills = participantDetails["stats"]["kills"]
            deaths = participantDetails["stats"]["deaths"]
            assists = participantDetails["stats"]["assists"]
            if deaths == 0:
                kda = Decimal(kills) + Decimal(assists)
            else:
                kda = (Decimal(kills) + Decimal(assists))/Decimal(deaths)
            self.matchHistoryStatistics["matches"][matchId]["kda"] = kda
            
            # Calculate score (kills-deaths-assists)
            score = str(kills) + '-' + str(deaths) + '-' + str(assists)
            self.matchHistoryStatistics["matches"][matchId]["score"] = score
            
            # Calculate kill participation %
            getcontext().prec = 4
            teamKills = 0
            for index, participant in enumerate(matchDetails["participants"]):
                if participant["teamId"] == participantTeamId:
                    teamKills = teamKills + participant["stats"]["kills"]
            killParticipationPercent = (Decimal(kills) + Decimal(assists)) / Decimal(teamKills)
            self.matchHistoryStatistics["matches"][matchId]["killParticipationPercent"] = killParticipationPercent*100
            
            # Calculate ward score
            wardsPlaced = participantDetails["stats"]["wardsPlaced"]
            wardsKilled = participantDetails["stats"]["wardsKilled"]
            wardScore = wardsPlaced + wardsKilled
            self.matchHistoryStatistics["matches"][matchId]["wardScore"] = wardScore
            
            # Calculate gold per minute and cs per minute
            getcontext().prec = 4
            matchTimeInSeconds = matchDetails["matchDuration"]
            matchTimeInMinutes = Decimal(matchTimeInSeconds/60)
            goldEarned = participantDetails["stats"]["goldEarned"]
            goldPerMinute = Decimal(goldEarned/matchTimeInMinutes)
            self.matchHistoryStatistics["matches"][matchId]["goldPerMin"] = goldPerMinute
            minionsKilled = participantDetails["stats"]["minionsKilled"]
            neutralMinionsKilled = participantDetails["stats"]["neutralMinionsKilled"]
            cs = minionsKilled + neutralMinionsKilled
            csPerMinute = Decimal(cs/matchTimeInMinutes)
            self.matchHistoryStatistics["matches"][matchId]["csPerMin"] = csPerMinute
    
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
                id = championListResponse[champion]["id"]
                name = championListResponse[champion]["name"]
                self.config.set('champions', str(id), name)
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
    
    def updateMatchHistoryVariables(self, newMatchHistoryList, matchHistoryDetails):
        # This method refreshes the self.matchHistoryList and self.matchHistoryDetails variables in this class.
        # Globals: self.matchHistoryList, self.matchHistoryDetails
        
        self.matchHistoryList = newMatchHistoryList
        self.matchHistoryDetails = matchHistoryDetails
        self.matchHistoryStatistics = {}
