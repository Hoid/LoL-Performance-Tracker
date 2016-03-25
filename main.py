# Filename: main.py
#
# Description: This file contains the main function that creates an instance of MainWindow, 
# handles the first time opening the application, processes a configuration file, and starts
# building the match history.

import sys, os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

import requests,  json
from ConfigParser import SafeConfigParser

from MatchHistoryBuilder import MatchHistoryBuilder

summonerName = ""
summonerNameFull = ""
summonerRegion = "na"
summonerId = ""
summonerRank = ""
apiKey = ""

class MainWindow(QMainWindow):
    
    def __init__(self):
        
        global summonerName, summonerNameFull, summonerId, summonerRegion, summonerRank, apiKey
        super(QMainWindow,  self).__init__()
        
        # Load UI
        self.ui = uic.loadUi('C:/Users/cheek/Documents/Code/LoL-Performance-Tracker/MainWindow.ui',  self)
        
        # Set up or read config.ini
        self.processConfigFile()
        
        if summonerName:
            self.ui.summonerNameLabel.setText(summonerNameFull)
        if summonerRank:
            self.ui.summonerRank.setText(summonerRank)
        
        # What I want to do:
        #       Match history shouldn't start building until we are done initializing the program and showing it. Move all match 
        #       history stuff back into the MatchHistoryBuilder class and initialize this class once the MainWindow is initialized.
        #       If we already have match history data in files, start a new thread that reads it and displays it. Don't keep the
        #       program from starting until this thread is done.
        #       If we have data displayed and the user hits the refresh button, pull a new match list from Riot, 
        #           store it in match_history.txt, identify new matches, pull details for those matches (5 at a time), 
        #           append them to match_history_details.txt, build the new matches, and add them to the UI
        #       If we don't have data yet, initialize match history doing what we do above but for all matches, because all are new
        
        # New way of building UI:
        #       Initialize the mainWindow just like normal. It won't have anything there because we haven't built it yet.
        #       Start a new thread that calls buildMatchHistory just like we do below, but after we start the app, from main probably.
        #       Remove the widget we have in the scroll area at the time first, then add the new widget with new match history stuff.
        
        self.matchHistoryBuilder = MatchHistoryBuilder(self)
        
        # If match_history.txt exists, call buildMatchHistory. If not, call getMatchHistory first, then call buildMatchHistory.
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history.txt'
        isFile = os.path.isfile(fileLocation)
        if isFile:
            self.buildMatchHistory()
        else:
            matchHistoryResponse = matchHistoryBuilder.getMatchHistory(summonerId)
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            fileLocation = fileLocation + '\match_history.txt'
            with open(fileLocation,  'w') as f:
                json.dump(matchHistoryResponse,  f)
            self.buildMatchHistory()
    
    def buildMatchHistory(self):
        # This method takes whatever matches are in match_history.txt, calls MatchHistoryBuilder.buildMatch() on each, 
        # and builds the GUI objects for the match history into the matchHistoryScrollArea.
        # Globals: self.matchHistoryBuilder
        
        matchHistoryBuilder = self.matchHistoryBuilder
        
        # Open match_history.txt and read json data into matchHistoryData
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        fileLocation = fileLocation + '\match_history.txt'
        with open(fileLocation,  'r') as f:
            matchHistoryData = json.load(f)
        matchHistoryData = matchHistoryData["matches"]
        
        # Scroll Area Properties
        self.matchHistory = self.ui.matchHistoryScrollArea
        self.matchHistory.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.matchHistory.setWidgetResizable(True)
        
        # Container Widget       
        widget = QWidget()
        # Layout of Container Widget
        layout = QVBoxLayout()
        for matchIndex, matchInstance in enumerate(matchHistoryData):
            matchId = matchInstance["matchId"]
            match = matchHistoryBuilder.buildMatch(summonerId, matchIndex, matchId)
            layout.addWidget(match)
        widget.setLayout(layout)
    
        self.matchHistory.setWidget(widget)
    
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
        return responseMessage
    
    def closeEvent(self, event):
        # This method takes an event as input, opens a message box for the user confirming they want to exit
        # the application, and fulfills their preference.
        # Globals: none
        
        reply = QMessageBox.question(self, 'Message', 
                                                    "Are you sure you want to quit?", 
                                                    QMessageBox.Yes, 
                                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def getSummonerInfo(self):
        # This method fetches summoner info using a summoner name and sets the summonerId and 
        # summonerNameFull variables. 
        # Globals: summonerId, summonerName, summonerNameFull
        
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
        # This method fetches summoner rank using summoner Id, builds a string containing the information,
        #  and returns it
        # Globals: none
        
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
        # This method sets up and processes the config file we use to store useful data between sessions of
        # the application. We read things like summonerId and summonerName on startup to reduce startup
        # time.
        # Globals: summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFileLocation = configFileLocation + "\config.ini"
        isFile = os.path.isfile(configFileLocation)
        config = SafeConfigParser()
        
        # If the file hasn't been created, create it, add a section 'main', add a section 'champions', and set 
        # isFirstTimeOpening to True.
        if not isFile:
            print "created config file"
            with open(configFileLocation,  'w') as file:
                config.read(configFileLocation)
                config.add_section('main')
                config.set('main',  'isFirstTimeOpening',  'True')
                with open(configFileLocation, 'w') as f:
                    config.write(f)
                isFirstTimeOpening = True
            
        # Otherwise, see if this is still the first time opening. This is possible if the program has created the 
        # config file but hasn't initialized it.
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
            self.showSummonerQueryDialog()
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
                with open(configFileLocation, 'w') as f:
                    config.write(f)
                config.read(configFileLocation)
            # read summoner info from config file
            summonerName = config.get('main',  'summonerName')
            summonerNameFull = config.get('main',  'summonerNameFull')
            summonerId = config.get('main',  'summonerId')
            summonerRank = config.get('main',  'summonerRank')
        
        # Ensure the api key in config file is correct. If needed, pull the key from api_key.txt.
        config.read(configFileLocation)
        global apiKey
        if apiKey:
            config.set('main', 'apiKey', apiKey)
        else:
            if config.has_option('main', 'apiKey'):
                apiKey = config.get('main', 'apiKey')
            # Pull api_key from internal file
            else:
                print "Was forced to use api_key.txt in MainWindow"
                apiKeyFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                apiKeyFileLocation = apiKeyFileLocation + "\\api_key.txt"
                with open(apiKeyFileLocation, 'r') as f:
                    apiKey = f.read()
                if not apiKey:
                    print "no API Key available"
                else:
                    config.set('main', 'apiKey', apiKey)
                    with open(configFileLocation, 'w') as f:
                        config.write(f)

    def showSummonerQueryDialog(self):
        # This method opens an input dialog box for the user to input their summoner name and API key
        # Globals: summonerName
        
        summonerNameInput, ok = QInputDialog.getText(self, 'Summoner info', 
            'Enter your summoner name:')
        if ok:
            global summonerName
            summonerName = str(summonerNameInput).replace(" ", "").lower()
        else:
            self.closeApplication()
        
        apiKeyInput, ok = QInputDialog.getText(self, 'API Key', 
            'Enter your API Key:')
        if ok:
            global apiKey
            apiKey = str(apiKeyInput).replace(" ", "").lower()
        else:
            self.closeApplication()


def main():
    # This method makes an instance of MainWindow and starts the application
    # Globals: none
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
