import sys
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import uic
import requests,  json

import showMainWindow

summonerName = ""
summonerId = ""
apiKey = "9a5609ad-2d90-4aff-a09f-dc86632f3770"

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(QMainWindow,  self).__init__()
        self.ui = uic.loadUi('C:/Users/cheek/Documents/Code/LoL-Performance-Tracker/MainWindow.ui')
        
        summonerInfoResponse = requests.get("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/Transatlantacism?api_key=" + apiKey)
        summonerInfoResponse = json.loads(summonerInfoResponse.text)
        summonerName = "transatlantacism"
        summonerId = summonerInfoResponse[summonerName]["id"]
        
        self.ui.summonerNameLabel.setText(str(summonerId))
        
        self.ui.show()


def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()
