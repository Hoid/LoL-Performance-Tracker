# main.py
#
# This file contains the main function that creates an instance of MainWindow, 
# pulls the summonerName, summonerRegion, and summonerId, and handles
# the first time opening the application. Right now, this file does everything.

import sys,  os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import requests,  json
from ConfigParser import SafeConfigParser

import showMainWindow

summonerName = ""
summonerNameFull = ""
summonerRegion = "na"
summonerId = ""
summonerRank = ""
apiKey = "9a5609ad-2d90-4aff-a09f-dc86632f3770"

class MainWindow(QMainWindow):
    
    def __init__(self):
        
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        super(QMainWindow,  self).__init__()
        
        # load UI
        self.ui = uic.loadUi('C:/Users/cheek/Documents/Code/LoL-Performance-Tracker/MainWindow.ui',  self)
        
        # set up or read config.ini
        self.processConfigFile()
        
        self.getMatchHistoryWorkerThread = getMatchHistoryWorkerThread()
        self.getMatchHistoryWorkerThread.start()
        
        if summonerName:
            self.ui.summonerNameLabel.setText(summonerNameFull)
        if summonerRank:
            self.ui.summonerRank.setText(summonerRank)
        
        #self.ui.btnExit.clicked.connect(self.close)
        #self.ui.actionExit.triggered.connect(self.close)

    def processConfigFile(self):
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        isFile = os.path.isfile(configFileLocation)
        config = SafeConfigParser()
        if not isFile:
            print "created config file"
            file = open(configFileLocation,  'w')
            config.read(configFileLocation)
            config.add_section('main')
            config.set('main',  'isFirstTimeOpening',  'True')
            with open(configFileLocation, 'w') as f:
                config.write(f)
            isFirstTimeOpening = True
        else:
            config.read(configFileLocation)
            if not config.has_section('main'):
                config.add_section('main')
                config.set('main',  'isFirstTimeOpening',  'True')
                with open(configFileLocation, 'w') as f:
                    config.write(f)
                config.read(configFileLocation)
            isFirstTimeOpening = config.get('main',  'isFirstTimeOpening')
            if isFirstTimeOpening == "False":
                isFirstTimeOpening = False
            else:
                isFirstTimeOpening = True
        if isFirstTimeOpening:
            self.showSummonerNameInputBox()
            self.getSummonerInfo()
            summonerRank = self.getSummonerRank()
            config.set('main',  'summonerName',  summonerName)
            config.set('main',  'summonerNameFull',  summonerNameFull)
            config.set('main',  'summonerId',  str(summonerId))
            config.set('main',  'summonerRank',  summonerRank)
            config.set('main',  'isFirstTimeOpening',  'False')
            with open(configFileLocation, 'w') as f:
                config.write(f)
        else: 
            config.read(configFileLocation)
            hasMainSection = config.has_section('main')
            if not hasMainSection:
                config.add_section('main')
            # read summoner info from config file
            summonerName = config.get('main',  'summonerName')
            summonerNameFull = config.get('main',  'summonerNameFull')
            summonerId = config.get('main',  'summonerId')
            summonerRank = config.get('main',  'summonerRank')

    def getSummonerInfo(self):
        global summonerId,  summonerName,  summonerNameFull
        requestURL = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" + summonerName + "?api_key=" + apiKey
        summonerInfoResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(summonerInfoResponse)
        if responseMessage == "ok":
            summonerInfoResponse = json.loads(summonerInfoResponse.text)
            summonerId = summonerInfoResponse[summonerName]["id"]
            summonerNameFull = summonerInfoResponse[summonerName]["name"]
        else:
            print responseMessage

    def getSummonerRank(self):
        summonerIdStr = str(summonerId)
        requestURL = "https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/" + summonerIdStr + "/entry?api_key=" + apiKey
        summonerInfoResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(summonerInfoResponse)
        if responseMessage == "ok":
            summonerInfoResponse = json.loads(summonerInfoResponse.text)
            summonerTier = summonerInfoResponse[summonerIdStr][0]["tier"].lower().capitalize()
            summonerDivision = summonerInfoResponse[summonerIdStr][0]["entries"][0]["division"]
            summonerLp = summonerInfoResponse[summonerIdStr][0]["entries"][0]["leaguePoints"]
            summonerRank = summonerTier + " " + summonerDivision + ", " + str(summonerLp) + "lp"
            return summonerRank
        else:
            print responseMessage
            return "Could not get summoner rank"

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
        responseMessage = codes.get(response.status_code,  "code not recognized")
        return responseMessage

    def showSummonerNameInputBox(self):
        text, ok = QInputDialog.getText(self, 'Summoner info', 
            'Enter your summoner name:')
        if ok:
            global summonerName
            summonerName = str(text).replace(" ", "").lower()
        else:
            self.closeApplication()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class getMatchHistoryWorkerThread(QThread):
    
    def __init__(self):
        super(getMatchHistoryWorkerThread,  self).__init__()
    
    def run(self):
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        self.getMatchHistoryDetails()
    
    def getMatchHistory(self):
        requestURL = "https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/" + str(summonerId) + "?seasons=SEASON2016&api_key=" + apiKey
        matchHistoryResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(matchHistoryResponse)
        if responseMessage == "ok":
            
            # write match history in json form to a file
            matchHistoryResponse = matchHistoryResponse.text
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            fileLocation = fileLocation + '\match_history.txt'
            f = open(fileLocation,  'w')
            json.dump(matchHistoryResponse,  f)
            
            #decode match history from json and return it
            matchHistoryResponse = json.loads(matchHistoryResponse)
            return matchHistoryResponse
            
        else:
            print responseMessage
            return "Could not get match history"

    def getMatchHistoryDetails(self):
        matchHistory = self.getMatchHistory()
        matchHistory = matchHistory["matches"]
        matchHistoryDetails = [] # For now, just make a new match history each time we start the program. Afterwards, read match history from file and only load the matches that are new.
        for match in range(5):
            matchId = matchHistory[match]["matchId"]
            requestURL = "https://na.api.pvp.net/api/lol/na/v2.2/match/" + str(matchId) + "?api_key=" + apiKey
            matchDetailsResponse = requests.get(requestURL)
            responseMessage = self.checkResponseCode(matchDetailsResponse)
            if responseMessage == "ok":
                matchDetailsResponse = json.loads(matchDetailsResponse.text)
                matchHistoryDetails.append(matchDetailsResponse)
            else:
                print "For match " + matchId + ", " + responseMessage
        matchHistoryDetailsJson = json.dumps(matchHistoryDetails)
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history_details.txt'
        f = open(fileLocation,  'w')
        json.dump(matchHistoryDetailsJson,  f)
        print "Populated match_history_details"
    
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
        responseMessage = codes.get(response.status_code,  "code not recognized")
        return responseMessage

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
