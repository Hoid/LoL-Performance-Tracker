# Filename: Summoner.py
#
# Description: This file contains the Summoner class that defines certain information about the summoner,
# such as name, id, and rank. Use this class by instantiating it and calling the getter methods needed. 

import requests,  json

class Summoner:
    
    def __init__(self, internalName, apiKey):
        self.fullName = ""
        self.apiKey = apiKey
        self.internalName = internalName
        self.rank = ""
        self.id = 0
    
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
        return str(responseMessage)
    
    
    def pullSummonerInfo(self):
        # This method fetches summoner info using the summoner's internalName and sets the id and 
        # fullName variables. 
        # Globals: 
        
        # Pull summoner id and full name (name displayed to the user) from API
        requestURL = ("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" 
                                + self.internalName 
                                + "?api_key=" 
                                + self.apiKey)
        summonerInfoResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(summonerInfoResponse)
        if responseMessage == "ok":
            summonerInfoResponse = json.loads(summonerInfoResponse.text)
            self.id = summonerInfoResponse[self.internalName]["id"]
            self.fullName = summonerInfoResponse[self.internalName]["name"]
        else:
            print responseMessage
    
        # Pull summoner tier, division, and lp from API and use them to define the full summoner's rank
        requestURL = ("https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/" 
                                + str(self.id) 
                                + "/entry?api_key=" 
                                + self.apiKey)
        summonerInfoResponse = requests.get(requestURL)
        responseMessage = self.checkResponseCode(summonerInfoResponse)
        if responseMessage == "ok":
            summonerInfoResponse = json.loads(summonerInfoResponse.text)
            summonerTier = summonerInfoResponse[str(self.id)][0]["tier"].lower().capitalize()
            summonerDivision = summonerInfoResponse[str(self.id)][0]["entries"][0]["division"]
            summonerLp = summonerInfoResponse[str(self.id)][0]["entries"][0]["leaguePoints"]
            summonerRank = summonerTier + " " + summonerDivision + ", " + str(summonerLp) + "lp"
            self.rank = summonerRank
        else:
            print responseMessage
            return "Could not get summoner rank"
