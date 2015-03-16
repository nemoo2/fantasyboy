from splinter import Browser
import re	
from bs4 import BeautifulSoup
import pickle
import time
from time import mktime
from datetime import datetime
import os
import sys

LeagueUrl = "https://fantasy.icc-cricket.com/cwc/homepage/homepage/"
DefaultSigninPage = "http://fantasy.icc-cricket.com/"

MY_USERNAME=os.environ.get("FANTASY_USERNAME")
MY_PASSWORD=os.environ.get("FANTASY_PASSWORD")

if MY_USERNAME is None or MY_PASSWORD is None:
        print "Fantasy username/password not found. Please set them using"
        print "FANTASY_USERNAME and FANTASY_PASSWORD environment variables"
        sys.exit(0)

LeagueTeams = dict()

LeagueTeams['Akshay'] = "233314"
LeagueTeams['Ripu'] = "46933"
LeagueTeams['Yenan'] = "122160"
LeagueTeams['Sri'] = "167401"
LeagueTeams['Shreyas'] = "46941"
LeagueTeams['Vinish'] = "187254"
LeagueTeams['Ali'] = "46943"
LeagueTeams['Tom'] = "147897"
LeagueTeams['Atin'] = "169823"


def initFantasyPage():
	b = Browser()
	b.visit(DefaultSigninPage)

	signinbtn = b.find_by_id('signinbtn_n')
	signinbtn.click()

	user = b.find_by_id('username')
	user.fill(MY_USERNAME)

	password = b.find_by_id('password')
	password.fill(MY_PASSWORD)

	signin = b.find_by_id('signinenter')
	signin.click()
	return b

class player:
        def __init__(self):
                self.captain = False
                self.name = ""
                self.team = ""
        def setName(self,name):
                self.name = name
        def setAsCaptain(self):
                self.captain = True
        def setTeam(self,team):
                self.team = team
        def getName(self):
                return self.name
        def isCaptain(self):
                return self.captain
        def getTeam(self):
                return self.team
        def __eq__(self,other):
                return self.getName() == other.getName() and self.getTeam() == other.getTeam()
        def __has__(self):
                return self.getName()+self.getTeam()

class team:
	def __init__(self):
		self.players = []
	
	def setPlayers(self,playersString):
		items = playersString.split('\n')
		for i in range(0,11):
                        playerX = player()
                        playerX.setName(items[3*i+1])
                        playerX.setTeam(items[3*i+0])
			self.players.append(playerX)

	def setCaptain(self,captain):
                for player in self.players:
                        if player.getName() == captain:
                                player.setAsCaptain()

        def getCaptain(self):
                for player in self.players:
                        if player.isCaptain(): return player

        def getPlayers(self):
                return self.players

	def __str__(self):
		toRet = ""
		for player in self.players:
			toRet += player
			if player.isCaptain(): toRet += "*\n"
			else: toRet += "\n"
		return toRet


def getTeam(number, browserSession):
	browserSession.visit(LeagueUrl+number)
	playersTeam = team()

	players = browserSession.find_by_id('selectmyplayers')
	playersTeam.setPlayers(players.text)
	
	soup = BeautifulSoup(browserSession.html)
	captain = soup.find("li", {"class":"playercard_dc powerplayer_dc"})["ss"]
	
	playersTeam.setCaptain(captain)
	return playersTeam


class gameInfo:
        def __init__(self):
                self.team1 = ""
                self.team2 = ""
                self.gameTime = None
        def setTeams(self,team1, team2):
                self.team1 = team1
                self.team2 = team2
        def setGameTime(self,gameTime):
                self.gameTime = gameTime
        def getTeams(self):
                return self.team1 + " vs " + self.team2
        def getGameTime(self):
                return self.gameTime

def getNextGame(mySession):
        mySession.visit(LeagueUrl)
        matchInfo = mySession.find_by_id('expectedmatchdate').text
        team1 = mySession.find_by_id('nextmatchfull1').text
        team2 = mySession.find_by_id('nextmatchfull2').text
        now = datetime.now()
        matchTimeString = matchInfo.split('(')[0]
        matchDate = time.strptime(matchTimeString + " " + str(now.year),  "%d %b %I:%M:%S %p %Y")
        matchTime = datetime.fromtimestamp(mktime(matchDate))
        nextGame = gameInfo()
        nextGame.setGameTime(matchTime)
        nextGame.setTeams(team1, team2)
        return nextGame

if __name__=="__main__":
	mySession = initFantasyPage()
        nextGameInfo = getNextGame(mySession)
        leagueTeams = {}
	for user,number in LeagueTeams.items():
		usersTeam = getTeam(number, mySession)
                leagueTeams[user] = usersTeam
        pickle.dump([nextGameInfo,leagueTeams], open("leagueDb.pl", "wb"))
        #pickle.dump(leagueTeams, open("leagueDb.pl", "wb"))
