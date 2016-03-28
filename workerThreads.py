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
    
    def __init__(self):
        super(QObject,  self).__init__()
    
    def run(self):
    
        global apiKey
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        summonerId = config.get('main',  'summonerId')
        apiKey = config.get('main', 'apiKey')
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        
        # If match_history_details.txt isn't yet a file, create it
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history_details.txt'
        isFile = os.path.isfile(fileLocation)
        if not isFile:
            with open(fileLocation, 'w') as newFile:
                print "Created match_history_details.txt"
                matchHistoryDetails = {}
                json.dump(matchHistoryDetails, newFile)
        
        # Open match_history.txt and read json data into matchHistoryData
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history.txt'
        with open(fileLocation,  'r') as f:
            matchHistoryData = json.load(f)
        matchHistoryData = matchHistoryData["matches"]
        
        # For each match in match history, open match_history_details and check whether we have match data for the 
        # matchID in question. If not, call getMatchDetails for the match and store that data in match_history_details.txt.
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history_details.txt'
        with open(fileLocation, 'r') as f:
                matchHistoryDetails = json.load(f)
        for matchIndex, matchInstance in enumerate(matchHistoryData):
            matchId = matchInstance["matchId"]
            if str(matchId) not in matchHistoryDetails.keys():
                matchDetails = self.matchHistoryBuilder.getMatchDetails(summonerId, matchId)
                if not matchDetails:
                    time.sleep(10)
                    matchDetails = self.matchHistoryBuilder.getMatchDetails(summonerId, matchId)
                matchHistoryDetails[matchId] = matchDetails
                self.matchDetailsPulled.emit(str(matchIndex))
                with open(fileLocation, 'w') as f:
                    json.dump(matchHistoryDetails, f)
