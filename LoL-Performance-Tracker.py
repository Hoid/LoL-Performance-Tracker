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
from WorkerThreads import InitMatchHistory,  RefreshMatchHistory

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
        
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\MainWindow.ui' 
        self.ui = uic.loadUi(fileLocation,  self)
        
        self.refreshMatchHistoryButton.clicked.connect(self.refreshMatchHistory)
        
        self.processConfigFile()
        
        if summonerName:
            self.ui.summonerNameLabel.setText(summonerNameFull)
        if summonerRank:
            self.ui.summonerRank.setText(summonerRank)
        
        self.ui.show()
        
        self.processMatchHistoryFiles()
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        
        # If matchHistoryDetails is just an empty directory, call initMatchHistory(). Once the thread
        # finishes, buildMatchHistory() will be called. If it's not empty, simply call buildMatchHistory().
        if self.matchHistoryDetails == {}:
            self.initMatchHistory()
        else:
            self.buildMatchHistory()
    
    def buildMatchHistory(self):
        # This method takes whatever matches are in self.matchHistoryList, calls MatchHistoryBuilder.buildMatch() on each, 
        # and builds the GUI objects for the match history into the matchHistoryScrollArea.
        # Globals: self.matchHistoryBuilder
        
        print "Entered buildMatchHistory"
        
        # Pull self.matchHistoryList into a local variable
        matchHistoryListData = self.matchHistoryList
        matchHistoryListData = matchHistoryListData["matches"]
        
        # Scroll Area Properties
        self.matchHistory = self.ui.matchHistoryScrollArea
        self.matchHistory.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.matchHistory.setWidgetResizable(True)
        
        # Container Widget
        widget = QWidget()
        # Layout of Container Widget
        layout = QVBoxLayout()
        for matchIndex, matchInstance in enumerate(matchHistoryListData):
            matchId = matchInstance["matchId"]
            match = self.matchHistoryBuilder.buildMatch(summonerId, matchIndex, matchId)
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
        # This method takes an event as input, opens a message box for the user confirming they want to exit the application,
        # and fulfills their preference. If the user wants to exit, write the self.matchHistoryList and self.matchHistoryDetails
        # to their corresponding files.
        # Globals: none
        
        reply = QMessageBox.question(self, 'Message', 
                                                    "Are you sure you want to quit?", 
                                                    QMessageBox.Yes, 
                                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
            with open(fileLocation, 'w') as f:
                json.dump(self.matchHistoryList, f)
            fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
            with open(fileLocation, 'w') as f:
                json.dump(self.matchHistoryDetails, f)
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
    
    def incrementProgressBar(self, matchIndex):
        # This method increments the progress bar that shows our progress in populating match history files
        # Globals: self.ui.initMatchHistoryProgressBar
        
        self.initMatchHistoryProgressDialog.setLabelText("Pulling data for match %s. " % matchIndex +  
                                                                            "\nThis process will only happen the " +
                                                                            "\n first time you run the application.")
        value = self.initMatchHistoryProgressDialog.value() + 1
        self.initMatchHistoryProgressDialog.setValue(value)
    
    def initMatchHistory(self):
        # This method creates a progress dialog that will get updated as we initialize the match history files and spawns a new thread that 
        # initializes the match history files. When the thread is finished, buildMatchHistory() gets called.
        # Globals: none
        
        self.initMatchHistoryProgressDialog()
        
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
        with open(fileLocation, 'w') as f:
            json.dump(self.matchHistoryDetails, f)
        
        self.initMatchHistoryWorkerThread = QThread(self)
        self.initMatchHistory = InitMatchHistory()
        self.initMatchHistory.moveToThread(self.initMatchHistoryWorkerThread)
        self.initMatchHistory.matchDetailsPulled.connect(self.incrementProgressBar)
        QObject.connect(self.initMatchHistoryWorkerThread, SIGNAL('started()'), self.initMatchHistory.run)
        QObject.connect(self.initMatchHistory, SIGNAL('finished()'), self.initMatchHistoryWorkerThread.quit)
        QObject.connect(self.initMatchHistory, SIGNAL('finished()'), self.initMatchHistory.deleteLater)
        QObject.connect(self.initMatchHistory, SIGNAL('finished()'), self.buildMatchHistory)
        QObject.connect(self.initMatchHistoryWorkerThread, SIGNAL('finished()'), self.initMatchHistoryWorkerThread.deleteLater)
        self.initMatchHistory.finished.connect(self.buildMatchHistory)
        self.initMatchHistoryWorkerThread.start()
    
    def initMatchHistoryProgressDialog(self):
        # This method creates a progress bar to show the progress of initializing match history files.
        # Globals: none
        
        self.initMatchHistoryProgressDialog = QProgressDialog(self)
        self.initMatchHistoryProgressDialog.setMinimum(1)
        self.initMatchHistoryProgressDialog.setMaximum(numberOfMatches)
        self.initMatchHistoryProgressDialog.setFixedSize(600, 300)
        self.initMatchHistoryProgressDialog.setWindowTitle("Getting match history data")
        self.initMatchHistoryProgressDialog.show()

    def processConfigFile(self):
        # This method sets up and processes the config file we use to store useful data between sessions of the application. 
        # We read things like summonerId and summonerName on startup to reduce unnecessary API calls on startup.
        # Globals: summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        
        global summonerName, summonerNameFull, summonerId, summonerRegion,  summonerRank
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
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
            config.set('main',  'apiKey',  apiKey)
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
                apiKey = str(config.get('main', 'apiKey'))
            # Pull api_key from internal file
            else:
                print "Was forced to use api_key.txt in MainWindow"
                apiKeyFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\api_key.txt"
                with open(apiKeyFileLocation, 'r') as f:
                    apiKey = f.read()
                if not apiKey:
                    print "no API Key available"
                else:
                    config.set('main', 'apiKey', apiKey)
                    with open(configFileLocation, 'w') as f:
                        config.write(f)
    
    def processMatchHistoryFiles(self):
        # This method ensures that the match history files exist, that they are initialized, and that the self.matchHistoryList and 
        # self.matchHistoryDetails variables tied to this class are populated.
        # Globals: self.matchHistoryList, self.matchHistoryDetails
        
        # If match_history_details.txt isn't yet a file, create it and initialize it with an empty dictionary. If it is, make sure it's not empty.
        # If it's empty, meaning not having at least an empty directory, initialize it. If it's not, load matchHistoryDetailsData into self.matchHistoryDetails
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
        isFile = os.path.isfile(fileLocation)
        if not isFile:
            with open(fileLocation, 'w') as newFile:
                print "Created and initialized match_history_details.txt"
                matchHistoryDetailsData = {}
                json.dump(matchHistoryDetailsData, newFile)
        else:
            with open(fileLocation, 'r') as f:
                matchHistoryDetailsData = json.load(f)
        if not matchHistoryDetailsData:
            with open(fileLocation, 'w') as f:
                print "Initialized match_history_details.txt"
                matchHistoryDetailsData = {}
                json.dump(matchHistoryDetailsData, f)
        self.matchHistoryDetails = matchHistoryDetailsData
        
        # If match_history.txt isn't yet a file, create it and initialize it with match history data. If it is, make sure it's not empty.
        # If it's empty, initialize it. If it's not empty, load matchHistoryListData into self.matchHistoryList
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
        isFile = os.path.isfile(fileLocation)
        if not isFile:
            with open(fileLocation, 'w') as newFile:
                print "Created and initialized match_history.txt"
                matchHistoryListData = self.matchHistoryBuilder.getMatchHistory(summonerId)
                json.dump(matchHistoryListData, newFile)
        else:
            with open(fileLocation, 'r') as f:
                matchHistoryListData = json.load(f)
        if not matchHistoryListData:
            with open(fileLocation, 'w') as f:
                print "Initialized match_history.txt"
                matchHistoryListData = self.matchHistoryBuilder.getMatchHistory(summonerId)
                json.dump(matchHistoryListData, f)
        self.matchHistoryList = matchHistoryListData

    def refreshMatchHistory(self):
    # This method creates a new thread that builds a new match history, only downloading game details for new games.
    # Globals: none
    
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
        with open(fileLocation, 'w') as f:
            json.dump(self.matchHistoryDetails, f)
        
        self.refreshMatchHistoryWorkerThread = QThread(self)
        self.refreshMatchHistory = RefreshMatchHistory()
        self.refreshMatchHistory.moveToThread(self.refreshMatchHistoryWorkerThread)
        QObject.connect(self.refreshMatchHistoryWorkerThread, SIGNAL('started()'), self.refreshMatchHistory.run)
        QObject.connect(self.refreshMatchHistoryWorkerThread, SIGNAL('finished()'), self.refreshMatchHistoryWorkerThread.deleteLater)
        QObject.connect(self.refreshMatchHistory, SIGNAL('finished()'), self.refreshMatchHistoryWorkerThread.quit)
        QObject.connect(self.refreshMatchHistory, SIGNAL('finished()'), self.refreshMatchHistory.deleteLater)
        self.refreshMatchHistory.finished.connect(self.buildMatchHistory)
        self.refreshMatchHistoryWorkerThread.start()

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
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
