import requests
import json
import os
import datetime
import constants as cs


####### DEFENSE SETUP #######

months = cs.months


def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])

for i in os.listdir(cs.shotDir):
    if not i.startswith('.'):
        with open(cs.shotDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                with open(cs.defenseDir + str(shot[15]) + '.json', 'a') as outfile:
                    json.dump(shot, outfile)

'''
#Uncomment this code if you wish to sort defense by the team a given player was playing defense against
                if shot[1][19] == 'v':
                    if not os.path.exists(cs.defenseDir + shot[1][23:26]):
                        os.makedirs(cs.defenseDir + shot[1][23:26])
                elif shot[1][19] == '@':
                    if not os.path.exists(cs.defenseDir + shot[1][21:24]):
                        os.makedirs(cs.defenseDir + shot[1][21:24])
'''

####### END DEFENSE SETUP #######













players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16'

shots_url = 'http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
rebound_url = 'http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='


# request the URL and parse the JSON for players
players_response = requests.get(players_url)
players_response.raise_for_status() # raise exception if invalid response
players = players_response.json()['resultSets'][0]['rowSet']

# request the URL and parse the JSON for shots
shots_response = requests.get(shots_url)
shots_response.raise_for_status() # raise exception if invalid response
shots = shots_response.json()['resultSets'][0]['rowSet']

#Hitting the API for rebounds
for player in players:
    #TODO: externalize Directory so this can run on machines other then your laptop
    with open(cs.shotDir + str(player[0]) + '.json', 'w') as outfile:
        players_response = requests.get('http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=' + str(player[0]) + '&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision=')
        players_response.raise_for_status() # raise exception if invalid response
        players = players_response.json()['resultSets'][0]['rowSet']
        json.dump(players, outfile)



#Hitting the API for shots
for player in players:
    print player
    #TODO: externalize Directory so this can run on machines other then your laptop
    with open(cs.shotDir + str(player[0]) + '.json', 'w') as outfile:
        players_response = requests.get('http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=' + str(player[0]) + '&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision=')
        players_response.raise_for_status() # raise exception if invalid response
        shots = players_response.json()['resultSets'][0]['rowSet']
        json.dump(shots, outfile)




#Get Dates Function
months = {'APR' : 4, 'JAN' : 1,'FEB' : 2,'MAR' : 3,'MAY' : 5,'JUN' : 6,'JUL' : 7,'AUG' : 8,'SEP' : 9,'OCT' : 10,'NOV' : 11,'DEC' : 12, '01' : 1, '02' : 2, '03' : 3,'04' : 4, '05' : 5, '06' : 4, '07' : 7, '08' : 8, '09' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15, '16' : 16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22, '23' : 23, '24' : 24, '25' : 25, '26' : 26, '27' : 27, '28' : 28, '29' : 29, '30' : 30, '31' : 31}
date = [u'0021401217', u'APR 15, 2015 - CHI vs. ATL', u'H', u'W', 6, 1, 1, u'3:37', u'Defensive', u'Uncontested', 0, 2.61, u'Carroll, DeMarre', 201960, u'missed 3FG', 24.09, 0, 1, 1]


def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])


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

#Getting gamelog data by player
gamelog_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=2015-16&SeasonType=Regular+Season&Sorter=PTS'

games_response = requests.get(gamelog_url)
games_response.raise_for_status() # raise exception if invalid response
games = games_response.json()['resultSets'][0]['rowSet']
months = {'APR' : 4, 'JAN' : 1,'FEB' : 2,'MAR' : 3,'MAY' : 5,'JUN' : 6,'JUL' : 7,'AUG' : 8,'SEP' : 9,'OCT' : 10,'NOV' : 11,'DEC' : 12, '01' : 1, '02' : 2, '03' : 3,'04' : 4, '05' : 5, '06' : 4, '07' : 7, '08' : 8, '09' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15, '16' : 16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22, '23' : 23, '24' : 24, '25' : 25, '26' : 26, '27' : 27, '28' : 28, '29' : 29, '30' : 30, '31' : 31}


#Another date function. How is this different from the first? Not sure but it works and I don't want to mess with it
def get_date_shots(date):
    month = date[0:3]
    day = date[4:6]
    year = int(float(date[8:12]))
    return datetime.date(year, months[month], months[day])

#Make files for gamelog per player
for player in games:
    with open(cs.gameDir + player[3] +'/' + player[6] + '_gamelog.json', 'a') as outfile:
        json.dump(player, outfile)


#Getting game log data by team
team_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&Season=2015-16&SeasonType=Regular+Season&Sorter=PTS'

team_response = requests.get(team_url)
team_response.raise_for_status() # raise exception if invalid response
team = team_response.json()['resultSets'][0]['rowSet']
teams = {}
for game in team:
    if game[3] not in teams:
        teams[game[3]] = game[2]
    with open(cs.teamDir + game[2] + '_game.json', 'a') as outfile:
        json.dump(game, outfile)



#Getting oppoent data on a season level
team_url = 'http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Opponent&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2014-15&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='

team_response = requests.get(team_url)
team_response.raise_for_status() # raise exception if invalid response
team = team_response.json()['resultSets'][0]['rowSet']

for game in team:
    temp = teams[game[1]]
    with open(cs.teamDir + temp + '_opponent.json', 'a') as outfile:
        json.dump(game, outfile)

[
"SEASON_ID","TEAM_ID","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE","MATCHUP","WL","MIN","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","PLUS_MINUS","VIDEO_AVAILABLE"
]



#Gamelogs by player
gamelog_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=2015-16&SeasonType=Regular+Season&Sorter=PTS'

["SEASON_ID","PLAYER_ID","PLAYER_NAME","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE","MATCHUP","WL","MIN","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","PLUS_MINUS","VIDEO_AVAILABLE"]

games_response = requests.get(gamelog_url)
games_response.raise_for_status() # raise exception if invalid response
games = games_response.json()['resultSets'][0]['rowSet']

#Make files for gamelog per player
for player in games:
    print player
    with open(cs.gamelogDir + str(player[1]) + '.json', 'a') as outfile:
        json.dump(player, outfile)

