from splinter import Browser
import re	
from bs4 import BeautifulSoup
import pickle


LeagueUrl = "https://fantasy.icc-cricket.com/cwc/homepage/homepage/"
DefaultSigninPage = "http://fantasy.icc-cricket.com/"

MY_USERNAME=""
MY_PASSWORD=""

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

class team:
	def __init__(self):
		self.captain = None
		self.players = []
	
	def setPlayers(self,playersString):
		items = playersString.split('\n')
		for i in range(0,11):
			self.players.append(items[3*i+1])

	def setCaptain(self,captain):
		self.captain = captain

        def getCaptain(self):
                return self.captain

        def getPlayers(self):
                return self.players

	def __str__(self):
		toRet = ""
		for player in self.players:
			toRet += player
			if(player == self.captain): toRet += "*\n"
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



if __name__=="__main__":
	mySession = initFantasyPage()
        leagueTeams = {}
	for user,number in LeagueTeams.items():
		usersTeam = getTeam(number, mySession)
                leagueTeams[user] = usersTeam
        pickle.dump(leagueTeams, open("leagueDb.pl", "wb"))
