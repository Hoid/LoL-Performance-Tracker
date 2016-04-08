# Filename: WorkerThreads.py
#
# Description: This file contains a worker thread that populates match_history.txt
# and match_history_details.txt. 

import sys, os, time

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import requests,  json
from ConfigParser import SafeConfigParser
from MatchHistoryBuilder import MatchHistoryBuilder

class InitMatchHistory(QObject):
    
    matchDetailsPulled = pyqtSignal(object)
    finished = pyqtSignal()
    
    def __init__(self):
        super(QObject,  self).__init__()
    
    def run(self):
    
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        self.summonerId = config.get('main',  'summonerId')
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        
        # Open match_history.txt and read json data into matchHistoryList
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
        with open(fileLocation,  'r') as f:
            matchHistoryList = json.load(f)
        matchHistoryList = matchHistoryList["matches"]
        
        # For each match in match history, open match_history_details and check whether we have match data for the 
        # matchID in question. If not, call getMatchDetails for the match and store that data in match_history_details.txt.
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
        with open(fileLocation, 'r') as f:
                matchHistoryDetails = json.load(f)
        for matchIndex, matchInstance in enumerate(matchHistoryList):
            matchId = matchInstance["matchId"]
            if str(matchId) not in matchHistoryDetails.keys():
                matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                if not matchDetails:
                    time.sleep(10)
                    matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                matchHistoryDetails[matchId] = matchDetails
                self.matchDetailsPulled.emit(str(matchIndex))
                with open(fileLocation, 'w') as f:
                    json.dump(matchHistoryDetails, f)
        
        self.finished.emit()

class RefreshMatchHistory(QObject):
    
    finished = pyqtSignal()
    
    def __init__(self):
        super(QObject,  self).__init__()
    
    def run(self):
    
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        self.summonerId = config.get('main',  'summonerId')
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        
        try:
            
            # Open match_history.txt and read json data into oldMatchHistoryList
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
            with open(fileLocation,  'r') as f:
                    oldMatchHistoryList = json.load(f)
            oldMatches = oldMatchHistoryList["matches"]
            
            # Open match_history_details.txt and read json data into matchHistoryDetails
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
            with open(fileLocation, 'r') as f:
                    matchHistoryDetails = json.load(f)
            
            # Call getMatchHistory and for any new matches, call getMatchDetails and update match_history_details.txt
            newMatchHistoryList = self.matchHistoryBuilder.getMatchHistory(self.summonerId)
            newMatches = newMatchHistoryList["matches"]
            numberOfNewMatches = newMatchHistoryList["totalGames"] - oldMatchHistoryList["totalGames"]
            while numberOfNewMatches > 0:
                matchId = newMatches[numberOfNewMatches-1]["matchId"]
                if str(matchId) not in matchHistoryDetails.keys():
                    matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                    if not matchDetails:
                        time.sleep(10)
                        matchDetails = self.matchHistoryBuilder.getMatchDetails(self.summonerId, matchId)
                    matchHistoryDetails[matchId] = matchDetails
                numberOfNewMatches -= 1
            with open(fileLocation, 'w') as f:
                json.dump(matchHistoryDetails, f)

            # When done, store the new match history in match_history.txt
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
            with open(fileLocation, 'w') as f:
                json.dump(newMatchHistoryList, f)
                print "Updated match_history.txt"
            
        except IOError:
            print "One or both of the match history files are missing, from refreshMatchHistory"
        
        finally:
            self.finished.emit()
