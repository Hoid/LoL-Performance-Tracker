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
from Summoner import Summoner

class MainWindow(QMainWindow):
    
    def __init__(self):
        
        global summonerName, summonerNameFull, summonerId, summonerRegion, summonerRank, apiKey
        super(QMainWindow,  self).__init__()
        
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\MainWindow.ui' 
        self.ui = uic.loadUi(fileLocation,  self)
        
        self.matchHistoryList = {}
        self.matchHistoryDetails = {}
        
        self.processConfigFile()
        
        self.ui.summonerNameLabel.setText(self.summoner.fullName)
        self.ui.summonerRank.setText(self.summoner.rank)
        
        self.refreshMatchHistoryButton.clicked.connect(self.refreshEvent)
        
        self.ui.show()
        
        self.matchHistoryBuilder = MatchHistoryBuilder()
        self.processMatchHistoryFiles()
        self.matchHistoryBuilder.updateMatchHistoryVariables(self.matchHistoryList, self.matchHistoryDetails)
        
        # If matchHistoryDetails is just an empty directory, call initMatchHistory(). Once the thread
        # finishes, buildMatchHistory() will be called. If it's not empty, simply call buildMatchHistory().
        if self.matchHistoryDetails == {}:
            self.initMatchHistory()
        else:
            self.buildMatchHistory()
    
    def buildMatchHistory(self):
        # This method takes whatever matches are in self.matchHistoryList, calls MatchHistoryBuilder.buildMatch() on each, 
        # and builds the GUI objects for the match history into the matchHistoryScrollArea.
        # Globals: self.matchHistoryBuilder, self.matchHistoryList, self.matchHistoryDetails
        
        print "Entered buildMatchHistory"
        
        self.matchHistoryBuilder.updateMatchHistoryVariables(self.matchHistoryList, self.matchHistoryDetails)
        matchHistoryListData = self.matchHistoryList["matches"]
        
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
            match = self.matchHistoryBuilder.buildMatch(self.summoner.id, matchIndex, matchId)
            layout.addWidget(match)
        widget.setLayout(layout)
    
        self.matchHistory.setWidget(widget)
        
        self.updateMatchHistoryVariables(self.matchHistoryBuilder.matchHistoryList, self.matchHistoryBuilder.matchHistoryDetails)
    
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
            if self.matchHistoryList:
                fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
                with open(fileLocation, 'w') as f:
                    f.write(json.dumps(self.matchHistoryList))
            if self.matchHistoryDetails:
                fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history_details.txt'
                with open(fileLocation, 'w') as f:
                    f.write(json.dumps(self.matchHistoryDetails))
            event.accept()
        else:
            event.ignore()
    
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
        
        self.initMatchHistoryWorkerThread = QThread(self)
        self.initMatchHistory = InitMatchHistory(self.matchHistoryList, self.matchHistoryDetails)
        self.initMatchHistory.moveToThread(self.initMatchHistoryWorkerThread)
        self.initMatchHistory.matchDetailsPulled.connect(self.incrementProgressBar)
        self.initMatchHistory.newMatchHistoryValues.connect(self.updateMatchHistoryVariables)
        QObject.connect(self.initMatchHistoryWorkerThread, SIGNAL('started()'), self.initMatchHistory.run)
        QObject.connect(self.initMatchHistory, SIGNAL('finished()'), self.initMatchHistoryWorkerThread.quit)
        QObject.connect(self.initMatchHistory, SIGNAL('finished()'), self.initMatchHistory.deleteLater)
        QObject.connect(self.initMatchHistoryWorkerThread, SIGNAL('finished()'), self.initMatchHistoryWorkerThread.deleteLater)
        self.initMatchHistory.finished.connect(self.buildMatchHistory)
        self.initMatchHistoryWorkerThread.start()
    
    def initMatchHistoryProgressDialog(self):
        # This method creates a progress bar to show the progress of initializing match history files.
        # Globals: none
        
        numberOfMatches = self.matchHistoryList["totalGames"]
        self.initMatchHistoryProgressDialog = QProgressDialog(self)
        self.initMatchHistoryProgressDialog.setMinimum(1)
        self.initMatchHistoryProgressDialog.setMaximum(numberOfMatches)
        self.initMatchHistoryProgressDialog.setFixedSize(600, 300)
        self.initMatchHistoryProgressDialog.setWindowTitle("Getting match history data")
        self.initMatchHistoryProgressDialog.show()

    def processConfigFile(self):
        # This method sets up and processes the config file we use to store useful data between sessions of the application. 
        # We read things like summonerId and summonerName on startup to reduce unnecessary API calls on startup.
        # Globals: self.summoner
        
        configFileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\config.ini"
        isFile = os.path.isfile(configFileLocation)
        config = SafeConfigParser()
        config.read(configFileLocation)
        
        # If the file hasn't been created, create it, add a section 'main', and set shouldInit to True.
        # Otherwise, if the file hasn't been initialized correctly, set shouldInit to True.
        if not isFile:
            print "Created config file"
            with open(configFileLocation,  'w') as configFile:
                config.add_section('main')
                config.set('main',  'isFirstTimeOpening',  'True')
                config.write(configFile)
                config.read(configFileLocation)
                shouldInit = True
        elif not config.has_section('main'):
            config.add_section('main')
            with open(configFileLocation,  'w') as configFile:
                config.write(configFile)
            config.read(configFileLocation)
            shouldInit = True
        else:
            shouldInit = False
        
        # If this is the first time opening, initialize important values.
        # Otherwise, read values from the file.
        if shouldInit:
            self.showSummonerQueryDialog()
            self.summoner = Summoner(self.internalSummonerName, self.apiKey)
            self.summoner.pullSummonerInfo()
            config.set('main',  'summonerName',  self.summoner.internalName)
            config.set('main',  'summonerNameFull',  self.summoner.fullName)
            config.set('main',  'summonerId',  str(self.summoner.id))
            config.set('main',  'summonerRank',  self.summoner.rank)
            config.set('main',  'isFirstTimeOpening',  'False')
            config.set('main',  'apiKey',  self.apiKey)
            with open(configFileLocation, 'w') as configFile:
                    config.write(configFile)
        else:
            config.read(configFileLocation)
            self.internalSummonerName = config.get('main',  'summonerName')
            self.apiKey = config.get('main',  'apiKey')
            self.summoner = Summoner(self.internalSummonerName, self.apiKey)
            self.summoner.fullName = config.get('main',  'summonerNameFull')
            self.summoner.id = config.get('main',  'summonerId')
            self.summoner.rank = config.get('main',  'summonerRank')
    
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
                newFile.write(json.dumps(self.matchHistoryDetails))
        else:
            with open(fileLocation, 'r') as f:
                matchHistoryDetailsData = json.loads(f.read())
        if matchHistoryDetailsData is None:
            with open(fileLocation, 'w') as f:
                print "Initialized match_history_details.txt"
                matchHistoryDetailsData = {}
                f.write(json.dumps(self.matchHistoryDetails))
        self.matchHistoryDetails = matchHistoryDetailsData
        
        # If match_history.txt isn't yet a file, create it and initialize it with match history data. If it is, make sure it's not empty.
        # If it's empty, initialize it. If it's not empty, load matchHistoryListData into self.matchHistoryList
        fileLocation = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\match_history.txt'
        isFile = os.path.isfile(fileLocation)
        if not isFile:
            with open(fileLocation, 'w') as newFile:
                print "Created and initialized match_history.txt"
                matchHistoryListData = self.matchHistoryBuilder.getMatchHistory(self.summoner.id)
                newFile.write(json.dumps(self.matchHistoryList))
        else:
            with open(fileLocation, 'r') as f:
                matchHistoryListData = json.loads(f.read())
        if matchHistoryListData is None:
            with open(fileLocation, 'w') as f:
                print "Initialized match_history.txt"
                matchHistoryListData = self.matchHistoryBuilder.getMatchHistory(self.summoner.id)
                newFile.write(json.dumps(self.matchHistoryList))
        self.matchHistoryList = matchHistoryListData
    
    def refreshEvent(self):
        # This method is the result of the user pressing the refresh button. 
        # Globals: none
        
        self.summoner.pullSummonerInfo()
        self.ui.summonerNameLabel.setText(self.summoner.fullName)
        self.ui.summonerRank.setText(self.summoner.rank)
        self.refreshMatchHistory()

    def refreshMatchHistory(self):
        # This method creates a new thread that builds a new match history, only downloading game details for new games.
        # Globals: none
        
        self.refreshMatchHistoryWorkerThread = QThread(self)
        self.refreshMatchHistory = RefreshMatchHistory(self.matchHistoryList, self.matchHistoryDetails)
        self.refreshMatchHistory.moveToThread(self.refreshMatchHistoryWorkerThread)
        self.refreshMatchHistory.newMatchHistoryValues.connect(self.updateMatchHistoryVariables)
        QObject.connect(self.refreshMatchHistoryWorkerThread, SIGNAL('started()'), self.refreshMatchHistory.run)
        QObject.connect(self.refreshMatchHistoryWorkerThread, SIGNAL('finished()'), self.refreshMatchHistoryWorkerThread.deleteLater)
        QObject.connect(self.refreshMatchHistory, SIGNAL('finished()'), self.refreshMatchHistoryWorkerThread.quit)
        QObject.connect(self.refreshMatchHistory, SIGNAL('finished()'), self.refreshMatchHistory.deleteLater)
        self.refreshMatchHistory.finished.connect(self.buildMatchHistory)
        self.refreshMatchHistoryWorkerThread.start()

    def showSummonerQueryDialog(self):
        # This method opens an input dialog box for the user to input their full summoner name (the name we show them
        # in the UI) and API key
        # Globals: self.fullSummonerName, self.apiKey
        
        summonerNameInput, ok = QInputDialog.getText(self, 'Summoner info', 'Enter your summoner name:')
        if ok and summonerNameInput:
            self.internalSummonerName = str(summonerNameInput).replace(" ", "").lower()
        else:
            sys.exit()
        
        apiKeyInput, ok = QInputDialog.getText(self, 'API Key', 'Enter your API Key:')
        if ok and apiKeyInput:
            self.apiKey = str(apiKeyInput).replace(" ", "").lower()
        else:
            sys.exit()
    
    def updateMatchHistoryVariables(self, newMatchHistoryList, matchHistoryDetails):
        # This method refreshes the self.matchHistoryList and self.matchHistoryDetails variables in this class and calls 
        # methods to do the same in other classes.
        # Globals: self.matchHistoryList, self.matchHistoryDetails
        
        self.matchHistoryList = newMatchHistoryList
        self.matchHistoryDetails = matchHistoryDetails
        self.matchHistoryBuilder.updateMatchHistoryVariables(newMatchHistoryList, matchHistoryDetails)


def main():
    # This method makes an instance of MainWindow and starts the application.
    # Globals: none
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
