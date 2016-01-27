import requests
import json
import os
import datetime
import constants as cs
from lxml import html



#Change to 2014-15 for other year of data
season = '2015-16'
months = {'APR' : 4, 'JAN' : 1,'FEB' : 2,'MAR' : 3,'MAY' : 5,'JUN' : 6,'JUL' : 7,'AUG' : 8,'SEP' : 9,'OCT' : 10,'NOV' : 11,'DEC' : 12, '01' : 1, '02' : 2, '03' : 3,'04' : 4, '05' : 5, '06' : 4, '07' : 7, '08' : 8, '09' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15, '16' : 16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22, '23' : 23, '24' : 24, '25' : 25, '26' : 26, '27' : 27, '28' : 28, '29' : 29, '30' : 30, '31' : 31}

players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=' + season
shots_url = 'http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
rebound_url = 'http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
gamelog_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=' + season + '&SeasonType=Regular+Season&Sorter=PTS'
team_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&Season=' + season + '&SeasonType=Regular+Season&Sorter=PTS'
opponent_url = 'http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Opponent&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='
roster_dir = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=' + season

#Dates Function
def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])
'''
#Player ID Data
players_response = requests.get(players_url)
players_response.raise_for_status() # raise exception if invalid response
players = players_response.json()['resultSets'][0]['rowSet']


####### REBOUNDS SETUP #######
#Change year under 'requests.get', currently set to 2015-2016
for player in players:
    with open(cs.reboundDir + str(player[0]) + '.json', 'a') as outfile:
        players_response = requests.get('http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=' + str(player[0]) + '&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision=')
        players_response.raise_for_status() # raise exception if invalid response
        shots = players_response.json()['resultSets'][0]['rowSet']
        json.dump(shots, outfile)


#Creates rebound files by game by play
for i in os.listdir(cs.reboundDir):
    if not i.startswith('.'):
        with open(cs.reboundDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                if not os.path.exists(cs.gameDir + shot[1][15:18]):
                    os.makedirs(cs.gameDir + shot[1][15:18])
                with open(cs.gameDir + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_rebound.json', 'a') as outfile:
                    json.dump(shot, outfile)
#End of Rebounds Setup

####### SHOTS SETUP #######
#HChange year under 'requests.get', currently set to 2015-2016
for player in players:
    with open(cs.shotDir + str(player[0]) + '.json', 'a') as outfile:
        players_response = requests.get('http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=' + str(player[0]) + '&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision=')
        players_response.raise_for_status() # raise exception if invalid response
        players = players_response.json()['resultSets'][0]['rowSet']
        json.dump(players, outfile)

#Creates shot files by game by shot
for i in os.listdir(cs.shotDir):
    if not i.startswith('.'):
        with open(cs.shotDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                if not os.path.exists(cs.gameDir + shot[1][15:18]):
                    os.makedirs(cs.gameDir + shot[1][15:18])
                with open(cs.gameDir + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_shot.json', 'a') as outfile:
                    json.dump(shot, outfile)
#End of Shots Setup


####### DEFENSE SETUP #######


for i in os.listdir(cs.shotDir):
    if not i.startswith('.'):
        with open(cs.shotDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                with open(cs.defenseDir + str(shot[15]) + '.json', 'a') as outfile:
                    json.dump(shot, outfile)


#Uncomment this code if you wish to group defense by the team a given player was playing defense against
                #f shot[1][19] == 'v':
                #    if not os.path.exists(cs.defenseDir + shot[1][23:26]):
                #        os.makedirs(cs.defenseDir + shot[1][23:26])
                #elif shot[1][19] == '@':
                #    if not os.path.exists(cs.defenseDir + shot[1][21:24]):
                #        os.makedirs(cs.defenseDir + shot[1][21:24])



####### PLAYER GAMELOG SETUP #######

#Getting gamelog data by player
games_response = requests.get(gamelog_url)
games_response.raise_for_status() # raise exception if invalid response
games = games_response.json()['resultSets'][0]['rowSet']

#Make files for gamelog by team by player
for player in games:
    with open(cs.gameDir + player[3] +'/' + player[6] + '_gamelog.json', 'a') as outfile:
        json.dump(player, outfile)

#Make files for gamelog by player
for player in games:
    with open(cs.gamelogDir + str(player[1]) + '.json', 'a') as outfile:
        json.dump(player, outfile)

#End of Player GameLog Setup



####### TEAM GAMELOG SETUP #######

team_response = requests.get(team_url)
team_response.raise_for_status() # raise exception if invalid response
team = team_response.json()['resultSets'][0]['rowSet']
teams = {}
for game in team:
    if game[3] not in teams:
        teams[game[3]] = game[2]
    with open(cs.teamDir + game[2] + '_game.json', 'a') as outfile:
        json.dump(game, outfile)



####### OPPONENT DATA SETUP #######

opponent_response = requests.get(opponent_url)
opponent_response.raise_for_status() # raise exception if invalid response
opponent = opponent_response.json()['resultSets'][0]['rowSet']

for game in opponent:
    temp = teams[game[1]]
    with open(cs.teamDir + temp + '_opponent.json', 'a') as outfile:
        json.dump(game, outfile)

###### ROSTER DATA SETUP ########
rosters_response = requests.get(roster_dir)
rosters_response.raise_for_status()
rosters = rosters_response.json()['resultSets'][0]['rowSet']

for player in rosters:
    with open(cs.rosterDir + player[9] + '.json', 'a') as outfile:
        json.dump(player, outfile)



####### DK POINTS SETUP #######
for i in os.listdir(cs.gamelogDir):
    if not i.startswith('.'):
        with open(cs.gamelogDir + i, 'r') as dataFile:
            data = json.load(dataFile)
            for player in data:
                ddpoints = [player[27], player[21], player[22], player[23], player[24]]
                dfsPoints = player[27] + 0.5 * player[13] + 1.25 * player[21] + 1.5 * player[22] + 2 * player[23] + 2 * player[24] - 0.5 * player[25]
                temp = 0
                for i in ddpoints:
                    if i > 10:
                        temp += 1
                if temp >= 2:
                    dfsPoints += 1.5
                if temp >= 3:
                    dfsPoints += 3
                newPlayer = [player[1], player[2], player[3], player[7], dfsPoints]

                with open(cs.dkPointsDir + player[6], 'a') as dataFile:
                    json.dump(newPlayer, dataFile)


#"SEASON_ID",
"PLAYER_ID", 0
"PLAYER_NAME", 1
"TEAM_ABBREVIATION", 2
"TEAM_NAME", 3
"GAME_ID", 4
"GAME_DATE", 5
"MATCHUP",  6
"WL", 7
"MIN", 8
"FGM", 9
"FGA", 10
"FG_PCT", 11
"FG3M", 12
"FG3A", 13
"FG3_PCT", 14
"FTM", 15
"FTA", 16
"FT_PCT", 17
"OREB", 18
"DREB", 19
"REB", 20
"AST", 21
"STL", 22
"BLK", 23
"TOV", 24
"PF", 25
"PTS", 26
"PLUS_MINUS", 27
"VIDEO_AVAILABLE", 28
'''


#TODO: ENDED HERE ON 1/17 ####### PRICE SCRAPING FROM ROTOGURU ########
class playerDayFromRotoWorld:

     def __init__(self, statArray):
         self.date = statArray[0]
         self.gid = statArray[1]
         self.pos = statArray[2]
         self.name = statArray[3]
         self.starter = len(statArray[4]) == 0
         if statArray[5] == 'None':
             self.dkpoints = 0
         else:
             self.dkpoints = float(statArray[5])
         if statArray[6] == 'N/A':
             self.salary = 100000
         else:
             self.salary = int(statArray[6].strip('$').replace(',',''))
         self.team = statArray[7]
         self.home = statArray[8] == 'H'
         self.opponent = statArray[9]
         self.team_score = statArray[10]
         self.opponent_score = statArray[11]
         self.minutes = statArray[12]
         statLine = statArray[13].split(' ')
         for stat in statLine:
             if stat.find('pt') > -1:
                  self.points = int(stat.strip('pt'))
             if stat.find('rb') > -1:
                  self.rebounds = int(stat.strip('rb'))
             if stat.find('as') > -1:
                  self.assists = int(stat.strip('as'))
             if stat.find('st') > -1:
                  self.steals = int(stat.strip('st'))
             if stat.find('to') > -1:
                  self.turnovers = int(stat.strip('to'))
             if stat.find('trey') > -1:
                  self.threes = int(stat.strip('trey'))
             if stat.find('fg') > -1:
                  self.field_goals_attempted = int(stat.strip('fg').split('-')[1])
                  self.field_goals_made = int(stat.strip('fg').split('-')[0])
             if stat.find('ft') > -1:
                  self.free_throws_attempted = int(stat.strip('ft').split('-')[1])
                  self.free_throws_made = int(stat.strip('ft').split('-')[0])

     def getValue(self):
         if self.dkpoints == 0:
             return -10000
         return self.dkpoints * self.dkpoints * self.dkpoints / self.salary

     def __lt__(self, other):
         return self.getValue() > other.getValue()
     def out(self):
        print self.name + ' ' + self.salary + ' '

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
    players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=${season}'
    apiPull = None

    def __init__(self, player_macros=None):
         if player_macros is None:
              player_macros = {'season': '2015-16'}
         self.apiPull = ApiPull(self.players_url, player_macros)

    def get(self):
         return self.apiPull.get()

class shotScrape:
    def __init__(self, days, mons, years, url=None, do_replacement=False):
        self.data=None
        self.days = days
        self.mons = mons
        self.years = years
        if url is None:
            self.url='http://rotoguru1.com/cgi-bin/hyday.pl?mon=${mon}&day=${day}&year=${year}&game=dk&scsv=10'
        if do_replacement:
            self.url = self.url.replace('${mon}', self.mons)
            self.url = self.url.replace('${day}', self.days)
            self.url = self.url.replace('${year}', self.years)

    def get(self, reset=False):
        if reset or self.data is None:
            page = requests.get(self.url)
            self.data = page.content
        t = html.fromstring(self.data)
        rawDayData = t.xpath('//table/pre/text()') #TODO: This is the toggle between using draftkings and rotoworld.
    	#rawDayData = statArraySetup(8266)
        rawDayDataList = rawDayData[0].split('\n')
        prices = []

        for i in rawDayDataList:
            prices.append(i.split(';'))

        del prices[0]
        del prices[-1]


        for player in prices:
            if player[3] != '':
                name = player[3].split(', ')
                name = name[1] + ' ' + name[0]
                name = name.replace(' ', '_').lower()


                renameDict = {'j.j._barea': 'jose_barea', 'lou_williams': 'louis_williams', "d'angelo_russell": 'dangelo_russell', 'larry_nance_jr.': 'larry_nance', 'o.j._mayo': 'oj_mayo', "kyle_o'quinn": 'kyle_oquinn', "e'twaun_moore" : 'etwaun_moore', 'louis_amundson': 'lou_amundson', "tim_hardaway_jr.": 'timothy_hardaway', "johnny_o'bryant": 'johnny_obryant'}

                if name in renameDict:
                    name == renameDict[name]


                date = player[0][0:4] + '-' + player[0][4:6] + '-' + player[0][6:8]

                newPlayer = [name, player[6],player[12]]
                print newPlayer

                with open(cs.priceDir + str(date), 'a') as outfile:
                    json.dump(newPlayer,outfile)


relDays = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
relMonths = ['10','11','12','1','2','3','4','5', '6']
relYears = ['2014','2015','2016']

#2014 = 10/28/14 - 4/15/2015
#2015 = 10/27/15 - 4/13/2016

def getRotoGuru(day, month, year):
    opponent = shotScrape(day, month, year, None, True).get()
    print opponent

def getAllDays(days, months, years):
    for year in years:
        for month in months:
            for day in days:
                getRotoGuru(day, month, year)

#getAllDays(relDays,relMonths,relYears)
getAllDays(relDays, relMonths, relYears)