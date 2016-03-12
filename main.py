# Filename: main.py
#
# Description: This file contains the main function that creates an instance of MainWindow, 
# handles the first time opening the application, and processes a configuration file. 

import sys, os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

import requests,  json
from ConfigParser import SafeConfigParser

from workerThreads import MatchHistoryWorkerThread
from buildMatchHistory import BuildMatchHistory

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
        
        if summonerName:
            self.ui.summonerNameLabel.setText(summonerNameFull)
        if summonerRank:
            self.ui.summonerRank.setText(summonerRank)
    
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
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 
                                                    "Are you sure to quit?", 
                                                    QMessageBox.Yes, 
                                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def getSummonerInfo(self):
        global summonerId,  summonerName,  summonerNameFull
        requestURL = ("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" 
                                + summonerName 
                                + "?api_key=" 
                                + apiKey)
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
        requestURL = ("https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/" 
                                + summonerIdStr 
                                + "/entry?api_key=" 
                                + apiKey)
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

    def processConfigFile(self):
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        isFile = os.path.isfile(configFileLocation)
        config = SafeConfigParser()
        
        # If the file hasn't been created, create it, add a section 'main', and set isFirstTimeOpening to True.
        # Otherwise, see if this is still the first time opening. This is possible if the program has created the 
        # config file but hasn't initialized it.
        if not isFile:
            print "created config file"
            file = open(configFileLocation,  'w')
            config.read(configFileLocation)
            config.add_section('main')
            config.set('main',  'isFirstTimeOpening',  'True')
            with open(configFileLocation, 'w') as f:
                config.write(f)
            isFirstTimeOpening = True
            file.close()
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
        
        # If this is the first time opening, initialize important values.
        # Otherwise, read values from the file.
        if isFirstTimeOpening:
            self.showSummonerNameInputBox()
            self.getSummonerInfo()
            summonerRank = self.getSummonerRank()
            config.set('main',  'summonerName',  summonerName)
            config.set('main',  'summonerNameFull',  summonerNameFull)
            config.set('main',  'summonerId',  str(summonerId))
            config.set('main',  'summonerRank',  summonerRank)
            config.set('main',  'isFirstTimeOpening',  'False')
            config.set('main',  'apiKey',  apiKey)
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

    def showSummonerNameInputBox(self):
        text, ok = QInputDialog.getText(self, 'Summoner info', 
            'Enter your summoner name:')
        if ok:
            global summonerName
            summonerName = str(text).replace(" ", "").lower()
        else:
            self.closeApplication()


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    matchHistoryWorkerThread = MatchHistoryWorkerThread(mainWindow)
    matchHistoryWorkerThread.start()
    matchHistoryWorkerThread.wait()
    buildMatchHistory = BuildMatchHistory()
    buildMatchHistory.buildMatchHistory(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
