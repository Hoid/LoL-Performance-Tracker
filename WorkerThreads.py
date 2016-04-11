# Filename: WorkerThreads.py
#
# Description: This file contains worker thread objects that other classes can run.

import sys, os, time

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import requests,  json
from ConfigParser import SafeConfigParser
from MatchHistoryBuilder import MatchHistoryBuilder

class InitMatchHistory(QObject):
    
    matchDetailsPulled = pyqtSignal(object)
    newMatchHistoryValues = pyqtSignal(object, object)
    finished = pyqtSignal()
    
    def __init__(self, matchHistoryList, matchHistoryDetails):
        super(QObject,  self).__init__()
        self.matchHistoryList = matchHistoryList
        self.matchHistoryDetails = matchHistoryDetails
    
    def run(self):
    
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        self.summonerId = config.get('main',  'summonerId')
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        self.matchHistoryBuilder.updateMatchHistoryVariables(self.matchHistoryList, self.matchHistoryDetails)
        
        matchHistoryList = self.matchHistoryList["matches"]
        
        # For each match in match history, check whether we have match data in matchHistoryDetails for the 
        # matchID in question. If not, call getMatchDetails for the match and store that data in matchHistoryDetails.
        for matchIndex, matchInstance in enumerate(matchHistoryList):
            matchId = int(matchInstance["matchId"])
            if matchId not in self.matchHistoryDetails.keys():
                matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                if not matchDetails:
                    time.sleep(10)
                    matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                self.matchHistoryDetails[matchId] = matchDetails
                self.matchDetailsPulled.emit(str(matchIndex))
        
        self.newMatchHistoryValues.emit(self.matchHistoryList, self.matchHistoryDetails)
        
        self.finished.emit()

class RefreshMatchHistory(QObject):
    
    newMatchHistoryValues = pyqtSignal(object, object)
    finished = pyqtSignal()
    
    def __init__(self, oldMatchHistoryList, matchHistoryDetails):
        super(QObject,  self).__init__()
        self.oldMatchHistoryList = oldMatchHistoryList
        self.matchHistoryDetails = matchHistoryDetails
    
    def run(self):
    
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        self.summonerId = config.get('main',  'summonerId')
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        self.matchHistoryBuilder.updateMatchHistoryVariables(self.oldMatchHistoryList, self.matchHistoryDetails)
        self.newMatchHistoryList = self.matchHistoryBuilder.getMatchHistory(self.summonerId)

        # Call getMatchHistory and for any new matches, call getMatchDetails and update match_history_details.txt
        newMatches = self.newMatchHistoryList["matches"]
        numberOfNewMatches = self.newMatchHistoryList["totalGames"] - self.oldMatchHistoryList["totalGames"]
        while numberOfNewMatches > 0:
            matchId = int(newMatches[numberOfNewMatches-1]["matchId"])
            if matchId not in self.matchHistoryDetails.keys():
                matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                if not matchDetails:
                    time.sleep(10)
                    matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                self.matchHistoryDetails[matchId] = matchDetails
            numberOfNewMatches -= 1
        
        # When done, send the new match history variable values back to MainWindow
        self.newMatchHistoryValues.emit(self.newMatchHistoryList, self.matchHistoryDetails)

        self.finished.emit()
