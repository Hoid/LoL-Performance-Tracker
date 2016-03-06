# main.py
#
# This file contains the main function that creates an instance of MainWindow, 
# pulls the summonerName, summonerRegion, and summonerId, and handles
# the first time opening the application

import sys
from PyQt4.QtGui import QApplication, QMainWindow,  QInputDialog,  QMessageBox
from PyQt4 import uic
import requests,  json

import showMainWindow,  config

summonerName = ""
summonerNameFull = ""
summonerRegion = ""
summonerId = ""
apiKey = "9a5609ad-2d90-4aff-a09f-dc86632f3770"

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(QMainWindow,  self).__init__()
        self.ui = uic.loadUi('C:/Users/cheek/Documents/Code/LoL-Performance-Tracker/MainWindow.ui')
        global summonerId,  summonerRegion
        summonerRegion = "na"
        
        self.showSummonerNameInputBox()
        self.getSummonerInfo()
        summonerRank = self.getSummonerRank()
        
        if summonerName:
            self.ui.summonerNameLabel.setText(summonerNameFull)
        if summonerRank:
            self.ui.summonerRank.setText(summonerRank)
        
        self.ui.show()

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

    def closeApplication(self):
        choice = QMessageBox.question(self,  "Quit",  "Are you sure you want to quit?",  QMessageBox.Yes | QMessageBox.No)
        #TODO: Handle closing of the application gracefully and store needed information for later
        if (choice == QMessageBox.Yes):
            print "Exiting application"
            sys.exit()
        else: 
            pass



def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
