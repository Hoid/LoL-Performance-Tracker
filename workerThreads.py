# Filename: WorkerThreads.py
#
# Description: This file contains a worker thread that populates match_history.txt
# and match_history_details.txt. 

import sys,  os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import requests,  json
from ConfigParser import SafeConfigParser

class MatchHistoryWorkerThread(QThread):
    
    def __init__(self):
        super(QThread,  self).__init__()
    
    def run(self):
        global apiKey
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        config = SafeConfigParser()
        config.read(configFileLocation)
        summonerId = config.get('main',  'summonerId')
        apiKeyFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        apiKeyFileLocation = apiKeyFileLocation + "\\api_key.txt"
        with open(apiKeyFileLocation, 'r') as f:
            apiKey = f.read()
        
        self.getMatchHistoryDetails(summonerId)
    
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
        responseMessage = codes.get(response.status_code,  "response code" + response.status_code + " not recognized")
        return responseMessage
    
    def getMatchHistory(self,  summonerId):
        requestURL = ("https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/" 
                                + str(summonerId) 
                                + "?seasons=SEASON2016&api_key=" 
                                + apiKey)
        matchHistoryResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(matchHistoryResponse)
        if responseMessage == "ok":
            
            # Write match history in json form to a file
            matchHistoryResponse = matchHistoryResponse.text
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            fileLocation = fileLocation + '\match_history.txt'
            f = open(fileLocation,  'w')
            f.close()
            
            json.dump(matchHistoryResponse,  f)
            # Decode match history from json and return it
            matchHistoryResponse = json.loads(matchHistoryResponse)
            return matchHistoryResponse
            
        else:
            print responseMessage + ", from getMatchHistory method"
            return "Could not get match history"

    def getMatchHistoryDetails(self,  summonerId):
        matchHistory = self.getMatchHistory(summonerId)
        matchHistory = matchHistory["matches"]
        matchHistoryDetails = [] # For now, just make a new match history each time we start the program. Afterwards, read match history from file and only load the matches that are new.
        for match in range(5):
            matchId = matchHistory[match]["matchId"]
            requestURL = ("https://na.api.pvp.net/api/lol/na/v2.2/match/" 
                                    + str(matchId) 
                                    + "?api_key=" 
                                    + apiKey)
            matchDetailsResponse = requests.get(requestURL)
            responseMessage = self.checkResponseCode(matchDetailsResponse)
            if responseMessage == "ok":
                matchDetailsResponse = json.loads(matchDetailsResponse.text)
                matchHistoryDetails.append(matchDetailsResponse)
            else:
                print "For match " + matchId + ", " + responseMessage + ", from getMatchHistoryDetails method"
        matchHistoryDetailsJson = json.dumps(matchHistoryDetails)
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history_details.txt'
        f = open(fileLocation,  'w')
        json.dump(matchHistoryDetailsJson,  f)
        f.close()
        print "Populated match_history_details"
