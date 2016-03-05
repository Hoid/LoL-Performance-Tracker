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
        
        self.ui.summonerNameLabel.setText(str(summonerName))
        self.ui.summonerRank.setText(str(summonerId))
        
        self.ui.show()

    def getSummonerInfo(self):
        global summonerId,  summonerName
        summonerInfoResponse = requests.get("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" + summonerName + "?api_key=" + apiKey)
        summonerInfoResponse = json.loads(summonerInfoResponse.text)
        summonerId = summonerInfoResponse[summonerName]["id"]
        summonerName = summonerInfoResponse[summonerName]["name"]

    def showSummonerNameInputBox(self):
        text, ok = QInputDialog.getText(self, 'Summoner info', 
            'Enter your summoner name:')
        if ok:
            global summonerName
            summonerName = str(text)
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
