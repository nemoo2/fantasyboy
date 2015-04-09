from fantasyScraper import team,player,gameInfo
import pickle
import pytg
import os
from pytg.utils import coroutine, broadcast
from pytg.tg import (
dialog_list, chat_info, message, user_status,
)
from time import sleep
from datetime import datetime, timedelta
import sys


def updateDb():
    return pickle.load( open("leagueDb.pl","rb"))



def getCaptains(fantasyTeams):
    print fantasyTeams
    toRet = "Here are the captains right now:\n"
    capDict = {}
    for user, team in fantasyTeams.items():
        captain = team.getCaptain()
        if captain is not None:
            capName = captain.getName()
            if capName in capDict:
                capDict[capName].append(user)
            else:
                capDict[capName] = [user]
    print capDict

    for captain, users in capDict.items():
        toRet += captain + ": "
        for user in users:
            toRet += user + ","
        toRet += "\n"
    return toRet

def findTheirTeam(username, fantasyTeams):
    toRet = ""
    for user, team in fantasyTeams.items():
        if user.lower().find(username) != -1:
            toRet += user + " : " 
            for player in team.getPlayers():
                if player.isCaptain():
                    toRet += player.getName() + "*,"
                else:
                    toRet += player.getName() + ","
            break
    if toRet != "" : return toRet
    else: return "I couldn't find this user buddy"

def findWhoHas(player,fantasyTeams):
    toRet = ""
    if len(player) < 3: return "Query too short, can you give me more to work with?"
    foundPlayers = {}
    for user, team in fantasyTeams.items():
        for myPlayer in team.getPlayers():
            if myPlayer.getName().lower().find(player) != -1:                
                if myPlayer.getName() in foundPlayers:
                    foundPlayers[myPlayer.getName()].append(user)
                else:
                    foundPlayers[myPlayer.getName()] = [user]
    uniquePlayers = len(foundPlayers.keys())
    if uniquePlayers > 2: return "I found too many similar-named players. Can you do better?"
    elif uniquePlayers > 0:
        for foundPlayer, foundUsers in foundPlayers.items():
            toRet += foundPlayer + " owned by "
            for foundUser in foundUsers:
                toRet += foundUser + ","
            toRet += "\n"
        return toRet
    else: return "Sorry, I couldnt find that player. Perhaps refine your query?"

def getHelpMenu():
    print  "Help requested"
    toRet = "My commands are (prefix with bot:)\n"
    toRet += "captains\n"
    toRet += "whohas <playername>\n"
    toRet += "user <username>\n"
    toRet += "status\n"
    toRet += "update\n"
    toRet += "from <country>\n"
    toRet += "next\n"
    toRet += "stop"
    return toRet

def getStatus():
    toRet = "I'm good"
    return toRet

def updateDatabase():
    os.system("python ./fantasyScraper.py")

def fromCountry(teamName,fantasyTeams):
    print "Someone wants to know players from:" + teamName
    print fantasyTeams
    country = "???"
    playerTeamMapping = {}
    for user,team in fantasyTeams.items():
        for player in team.getPlayers():
            if player.getTeam().lower().find(teamName) != -1:
                country = player.getTeam()
                if player.getName() in playerTeamMapping:
                    playerTeamMapping[player.getName()].append(user)
                else: playerTeamMapping[player.getName()] = [user]
    if len(playerTeamMapping.keys()) > 0:
        toRet = "Following from " + country + " found:\n"
        for player,users in playerTeamMapping.items():
            toRet += player + " owned by "
            for user in users:
                toRet += user + ","
            toRet += "\n"
    else:
        toRet = "No players found from " + teamName
    return toRet
        
def getNextInfo(game):
    if game is None: return "Cannot get next game info"
    now = datetime.now()
    td = game.getGameTime()-now+timedelta(hours=1)
    toRet = "Next game: " + game.getTeams() + " in " + str(td.days) + " days " + str(td.seconds/60) + " minutes"
    return toRet


@coroutine
def command_parser(chat_group, tg):
    [game,fantasyTeams] = updateDb()
    #fantasyTeams = updateDb()
    try:
        while True:
            msg = (yield)
            Response = None
            if  'gid' in msg and (msg['gid'] == chat_group or msg['gid'] == '(null)'):
                query = msg['message'].lower().strip()
                if  query == 'bot:help':
                    Response = getHelpMenu()
                elif query == 'bot:status':
                    print "Status requested"
                    Response = getStatus()
                elif query == 'bot:next':
                    print "Next game requested"
                    Response = getNextInfo(game)
                elif query.find('bot:user') != -1:
                    username = query.split('bot:user')[1].strip()
                    Response = findTheirTeam(username, fantasyTeams)
                elif query.find('bot:from') != -1:
                    country = query.split('bot:from')[1].strip()
                    Response = fromCountry(country,fantasyTeams)
                elif query.find('bot:whohas') != -1:
                    player = query.split('bot:whohas')[1].strip()
                    print "Someone wants to know who has "+ player
                    Response = findWhoHas(player,fantasyTeams)
                elif query == 'bot:captains':
                    print "Someone wants to know captains"
                    Response = getCaptains(fantasyTeams)
                elif query == 'bot:stop':
                    tg.msg(chat_group,"Stopping. Bye")
                    print "Stopping program"
                    break
                elif query == 'bot:update':
                    print "Someone asked me to update the database"
                    tg.msg(chat_group,"I'm going to fetch updates. It may take upto 3 minutes")
                    updateDatabase()
                    [game, fantasyTeams] = updateDb()
                    #fantasyTeams = updateDb()
                    tg.msg(chat_group,"Okay, done")
                if Response is not None:
                    print Response
                    for line in Response.split('\n'):
                        tg.msg(chat_group,line.rstrip(','))
    except GeneratorExit:
        pass


telegram = os.environ.get("TG_BIN")
pubkey = os.environ.get("TG_PUBKEY")
if telegram is None or pubkey is None:
    print "Please set TG_PATH environment variable"
    print "Set TG_PUBKEY to point to your public key"
    sys.exit(0)



tg = pytg.Telegram(telegram, pubkey)

pipeline = message(command_parser('Ipl', tg))

tg.register_pipeline(pipeline)

tg.start()
while True:
    try:
        tg.poll()
    except Exception,e:
        print "Exception thrown, lets deal with it"
        sleep(1)
tg.quit()
