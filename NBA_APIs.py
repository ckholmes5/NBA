import requests
import json
import os
import datetime
import constants as cs

#Change to 2014-15 for other year of data
season = '2015-16'

players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=' + season
shots_url = 'http://stats.nba.com/stats/playerdashptshotlog?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
rebound_url = 'http://stats.nba.com/stats/playerdashptreboundlogs?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=202322&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision='
gamelog_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=' + season + '&SeasonType=Regular+Season&Sorter=PTS'
team_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&Season=' + season + '&SeasonType=Regular+Season&Sorter=PTS'
opponent_url = 'http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Opponent&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='


#Dates Function
def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])

#Player ID Data
players_response = requests.get(players_url)
players_response.raise_for_status() # raise exception if invalid response
players = players_response.json()['resultSets'][0]['rowSet']


####### REBOUNDS SETUP #######
#Change year under 'requests.get', currently set to 2015-2016
for player in players:
    with open(cs.shotDir + str(player[0]) + '.json', 'w') as outfile:
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
    with open(cs.shotDir + str(player[0]) + '.json', 'w') as outfile:
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

months = cs.months

for i in os.listdir(cs.shotDir):
    if not i.startswith('.'):
        with open(cs.shotDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                with open(cs.defenseDir + str(shot[15]) + '.json', 'a') as outfile:
                    json.dump(shot, outfile)

'''
#Uncomment this code if you wish to group defense by the team a given player was playing defense against
                if shot[1][19] == 'v':
                    if not os.path.exists(cs.defenseDir + shot[1][23:26]):
                        os.makedirs(cs.defenseDir + shot[1][23:26])
                elif shot[1][19] == '@':
                    if not os.path.exists(cs.defenseDir + shot[1][21:24]):
                        os.makedirs(cs.defenseDir + shot[1][21:24])
'''


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

#TODO: NEED TEAMDIR AND ROSTERDIR



