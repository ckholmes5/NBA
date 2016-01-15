
import requests
import json
import os
import datetime
import constants

# If these ever change, now you only have to change them in one location

months = {'APR' : 4, 'JAN' : 1,'FEB' : 2,'MAR' : 3,'MAY' : 5,'JUN' : 6,'JUL' : 7,'AUG' : 8,'SEP' : 9,'OCT' : 10,'NOV' : 11,'DEC' : 12, '01' : 1, '02' : 2, '03' : 3,'04' : 4, '05' : 5, '06' : 4, '07' : 7, '08' : 8, '09' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15, '16' : 16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22, '23' : 23, '24' : 24, '25' : 25, '26' : 26, '27' : 27, '28' : 28, '29' : 29, '30' : 30, '31' : 31}
date = [u'0021401217', u'APR 15, 2015 - CHI vs. ATL', u'H', u'W', 6, 1, 1, u'3:37', u'Defensive', u'Uncontested', 0, 2.61, u'Carroll, DeMarre', 201960, u'missed 3FG', 24.09, 0, 1, 1]

intMonths = [11,12,1,2,3,4,5]
intDays = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
intYears = [2014]

class ApiPull:
    url=''
    macros={}
    
    def __init__(self, url, macros):
        self.url = url
        self.macros = macros
    
    def get(self):
         response = requests.get(self.getActualUrl())
         response.raise_for_status()
         return response.json()['resultSets'][0]['rowSet']
     
    def getActualUrl(self):
        tmp=self.url
        for k,v in self.macros.iteritems():
              tmp = tmp.replace('${' + k + '}', v)
        return tmp

class playersPull:
    players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=${season}'     
    apiPull = None
    
    def __init__(self, player_macros=None):
         if player_macros is None:
              player_macros = {'season': '2015-16'}
         self.apiPull = ApiPull(self.players_url, player_macros)
    
    def get(self):
         return self.apiPull.get()

class shotsPull:
    shots_url = 'http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=${playerid}&Season=${season}&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
    apiPull = None
    
    def __init__(self, shots_macros=None):
         if shots_macros is None:
              shots_macros = {'season': '2014-15', 'playerid': '202322'}
         self.apiPull = ApiPull(self.shots_url, shots_macros)
    
    def get(self):
         return self.apiPull.get()

class reboundPull:
    rebound_url = 'http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=${playerid}&Season=${season}&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
    apiPull = None
    
    def __init__(self, rebound_macros=None):
         if rebound_macros is None:
              rebound_macros = {'season': '2014-15', 'playerid': '202322'}
         self.apiPull = ApiPull(self.rebound_url, rebound_macros)
    
    def get(self):
         return self.apiPull.get()         

class gamelogPull:
    gamelog_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=${season}&SeasonType=Regular+Season&Sorter=PTS'
    apiPull = None
    
    def __init__(self, gamelog_macros=None):
         if gamelog_macros is None:
              gamelog_macros = {'season': '2014-15'}
         self.apiPull = ApiPull(self.gamelog_url, gamelog_macros)
    
    def get(self):
         return self.apiPull.get()        

class teamPull:
    team_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&Season=${season}&SeasonType=Regular+Season&Sorter=PTS'
    apiPull = None
    
    def __init__(self, team_macros=None):
         if team_macros is None:
              team_macros = {'season': '2014-15'}
         self.apiPull = ApiPull(self.team_url, team_macros)
    
    def get(self):
         return self.apiPull.get()

class teamOpponentPull:
    team_opponent_url = 'http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Opponent&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=${season}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='
    apiPull = None
    
    def __init__(self, team_opponent_macros=None):
         if team_opponent_macros is None:
              team_opponent_macros = {'season': '2014-15'}
         self.apiPull = ApiPull(self.team_opponent_url, team_opponent_macros)
    
    def get(self):
         return self.apiPull.get()
#class priceScrape:

#    def __init__(self, )


class saveFile:
    file=None
    def __init__(self, file):
         self.file=file
	
    def save(jsonData):
         with open(file, 'w') as outfile:
              json.dumps(jsonData, outfile)
	



def doSaveRebounds():
	players = playersPull().get()
	rebound_macros={'season': '2014-15'}
	for player in players:
		p = str(player[0])
		outputFile = saveFile(constants.reboundDir + p + '.json')
		rebound_macros['playerid'] = p
		outputFile.save(reboundPull(rebound_macros).get())


def doSaveShots():
	players = playersPull().get()
	shots_macros={'season': '2014-15'}
	for player in players:
		p = str(player[0])
		outputFile = saveFile(constants.shotDir + p + '.json')
		shots_macros['playerid'] = p
		outputFile.save(shotPull(shots_macros).get())
     
#Creates rebound files by game by play
def transformReboundsToPerGamePerPlay():
	for i in os.listdir(reboundDir):
		if not i.startswith('.'):
			with open(constants.reboundDir + i , 'r') as data_file:
				data = json.load(data_file)
				for shot in data:
					if not os.path.exists(constants.gameDir + shot[1][15:18]):
						os.makedirs(constants.gameDir + shot[1][15:18])
					with open(constants.gameDir + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_rebound.json', 'a') as outfile:
						json.dump(shot, outfile)

#Creates shot files by game by shot
def transformShotsToPerGamePerShot():
	for i in os.listdir(shotDir):
		if not i.startswith('.'):
			with open(constants.shotDir + i , 'r') as data_file:
				data = json.load(data_file)
				for shot in data:
					if not os.path.exists(constants.gameDir + shot[1][15:18]):
						os.makedirs(constants.gameDir + shot[1][15:18])
					with open(constants.gameDir + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_shot.json', 'a') as outfile:
						json.dump(shot, outfile)


#Another date function. How is this different from the first? Not sure but it works and I don't want to mess with it
def get_date_shots(date):
    month = date[0:3]
    day = date[4:6]
    year = int(float(date[8:12]))
    return datetime.date(year, months[month], months[day])

#Getting gamelog data by player
def doSavePlayerGamelogs():
	games = gamelogPull().get()
	for player in games:
		with open(constants.gameDir + player[3] +'/' + player[6] + '_gamelog.json', 'a') as outfile:
			json.dump(player, outfile)

#Getting game log data by team
def doSaveGames():
    team = teamPull().get()
    teams = {}
    for game in team:
    	if game[3] not in teams:
    		teams[game[3]] = game[2]
    	with open(constants.teamDir + game[2] + '_game.json', 'a') as outfile:
    		json.dump(game, outfile)

    team = teamOpponentPull().get()

    for game in team:
    	temp = teams[game[1]]
    	with open(constants.teamDir + temp + '_opponent.json', 'a') as outfile:
    		json.dump(game, outfile)

doSaveGames()

#[
#"SEASON_ID","TEAM_ID","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE","MATCHUP","WL","MIN","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","PLUS_MINUS","VIDEO_AVAILABLE"
#]

#Gamelogs by player
def doSaveGamelogByPlayer():
	games = gamelogPull().get()
	for player in games:
		with open(constants.gamelogDir + str(player[1]) + '.json', 'a') as outfile:
			json.dump(player, outfile)

shots_response = requests.get('http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16')
shots_response.raise_for_status() # raise exception if invalid response
shots = shots_response.json()['resultSets'][0]['rowSet']


def doSaveRosters():
	shots = playersPull().get()
	for shot in shots:
		with open(constants.rosterDir + shot[9] + '.json', 'a') as outfile:
			json.dump(shot, outfile)

def setupBox():
    os.makedirs(constants.gamelogDir)
    #os.makedirs(constants.teamDir)
    os.makedirs(constants.gameDir)
    os.makedirs(constants.shotDir)
    os.makedirs(constants.reboundDir)
    os.makedirs(constants.rosterDir)
    doSaveRebounds()
    doSaveShots()
    transformReboundsToPerGamePerPlay()
    transformShotsToPerGamePerShot()
    doSavePlayerGamelogs()
    doSaveGames()
    doSaveGamelogByPlayer()
    doSaveRosters()

doSaveRosters()