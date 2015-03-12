from fantasyScraper import team
import pickle
import pytg
import os
from pytg.utils import coroutine, broadcast
from pytg.tg import (
dialog_list, chat_info, message, user_status,
)
from time import sleep


def updateDb():
    return pickle.load( open("leagueDb.pl","rb"))



def getCaptains(fantasyTeams):
    print fantasyTeams
    toRet = ""
    capDict = {}
    for user, team in fantasyTeams.items():
        captain = team.getCaptain()
        if capDict.has_key(captain):
            capDict[captain].append(user)
        else:
            capDict[captain] = [user]
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
                if player == team.getCaptain():
                    toRet += player + "*,"
                else:
                    toRet += player + ","
            break
    if toRet != "" : return toRet
    else: return None

def findWhoHas(player,fantasyTeams):
    toRet = ""
    owners = ""
    playerName = ""
    for user, team in fantasyTeams.items():
        for myPlayer in team.getPlayers():
            if myPlayer.lower().find(player) != -1:                
                playerName = myPlayer
                owners += user + ","
                break
    toRet = playerName + " owned by " + owners
    if playerName != "": return toRet
    else: return None

@coroutine
def command_parser(chat_group, tg):
    fantasyTeams = updateDb()
    try:
        while True:
            msg = (yield)
            if  msg.has_key('group') and msg['group'] == chat_group:
                query = msg['message'].lower().strip()
                if  query == 'bot:help':
                    print "Help requested"
                    tg.msg(chat_group,"My commands are (prefix with bot:)")
                    tg.msg(chat_group,"captains")
                    tg.msg(chat_group,"whohas <playername>")
                    tg.msg(chat_group,"user <username>")
                    tg.msg(chat_group,"status")
                    tg.msg(chat_group,"update")
                    tg.msg(chat_group,"stop")
                elif query == 'bot:status':
                    print "Status requested"
                    tg.msg(chat_group,"I'm good")
                elif query.find('bot:user') != -1:
                    username = query.split('bot:user')[1].strip()
                    Response = findTheirTeam(username, fantasyTeams)
                    if Response is not None:
                        print Response
                        for line in Response.split('\n'):
                            tg.msg(chat_group,line)
                    else:
                        tg.msg(chat_group,"I couldn't find this user buddy")
                elif query.find('bot:whohas') != -1:
                    player = query.split('bot:whohas')[1].strip()
                    print "Someone wants to know who has "+ player
                    Response = findWhoHas(player,fantasyTeams)
                    if Response is not None:
                        print Response
                        tg.msg(chat_group,Response)
                    else:
                        tg.msg(chat_group,"Sorry, I couldnt find that player. Perhaps refine your query?")
                #    tg.msg(chat_group,"I'm good")
                elif query == 'bot:captains':
                    print "Someone wants to know captains"
                    Response = getCaptains(fantasyTeams)
                    print Response
                    tg.msg(chat_group,"Here are the captains right now..")
                    for line in Response.split('\n'):
                        tg.msg(chat_group,line)
                elif query == 'bot:stop':
                    tg.msg(chat_group,"Stopping. Bye")
                    print "Stopping program"
                    break
                elif query == 'bot:update':
                    print "Someone asked me to update the database"
                    tg.msg(chat_group,"I'm going to fetch updates. It may take upto 3 minutes")
                    os.system("python ./fantasyScraper.py")
                    fantasyTeams = updateDb()
                    tg.msg(chat_group,"Okay, done")
                
    except GeneratorExit:
        pass


telegram = '/home/shreyas/Programs/Scraper/pytg/tg/telegram'
pubkey = '/home/shreyas/Programs/Scraper/pytg/tg/tg.pub'

tg = pytg.Telegram(telegram, pubkey)

pipeline = message(command_parser('cwc', tg))

tg.register_pipeline(pipeline)

tg.start()
while True:
    tg.poll()
    
tg.quit()





