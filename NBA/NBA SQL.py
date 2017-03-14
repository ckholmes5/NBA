# How to access table from terminal
# cd /usr/local/mysql/bin/
# sudo ./mysql -u root -h localhost -p

# Creating a new database
# CREATE DATABASE nba;

import _mysql
import requests
import pandas as pd

#Connecting to SQL
db = MySQLdb.connect(host = 'localhost',
					user = 'root',
					passwd = 'ckh123',
					db = 'nba')
cur = db.cursor()
#cur.execute('use nba;')
season = '2015-16'

######################################################################################################
##########################################  PLAYER ID DATA  ##########################################
######################################################################################################

#Creating the table to be used
#cur.execute("CREATE TABLE player (PersonID int, Last_First varchar(255), First_Last varchar(255), Roster_Status int,From_Year varchar(255),To_Year varchar(255),Player_Code varchar(255),Team_ID int,Team_City varchar(255),Team_Name varchar(255),Team_Abbrev varchar(255),Team_Code varchar(255),Games_Played_Flag varchar(255));")

add_player = ("INSERT INTO player "
			"(PersonID , Last_First , First_Last , Roster_Status ,From_Year ,To_Year,Player_Code,Team_ID,Team_City,Team_Name,Team_Abbrev,Team_Code,Games_Played_Flag)"
			"VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s)")

#Fetching all player data from stats.nba.com
players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=' + season


playerID_response = requests.get(players_url)
playerID_response.raise_for_status() # raise exception if invalid response
playerID_data = playerID_response.json()['resultSets'][0]['rowSet']


#Dumping data into sql
for playerID in playerID_data:
	cur.execute(add_player, tuple(playerID))



######################################################################################################
##########################################  GAME LOG DATA  ###########################################
######################################################################################################

# Creating Game Log Table
#cur.execute("CREATE TABLE gamelog (SeasonID varchar(255), PlayerID int, Player_Name varchar(255), Team_Abb varchar(255), Team_Name varchar(255), GameID varchar(255), Game_Date varchar(255), Matchup varchar(255), WL varchar(255), Min int, FGM int, FGA int, FG_PCT decimal(4,3), FG3M int, FG3A int, FG3_pct decimal(4,3), FTM int, FTA int, FT_PCT decimal(4,3), OREB int, DREB int, REB int, AST int, STL int, BLK int, TOV int, PF int, PTS int, PLUS_MINUS int, VIDEO_AVAILABLE int, Opponent_Name varchar(255));")

add_game = ("INSERT INTO gamelog "
			"(SeasonID, PlayerID, Player_Name, Team_Abb, Team_Name, GameID, Game_Date, Matchup, WL, Min, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_pct, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, STL, BLK, TOV, PF, PTS, PLUS_MINUS, VIDEO_AVAILABLE, Opponent_Name)"
			"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

game_url = 'http://stats.nba.com/stats/leaguegamelog?Counter=10000000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=' + season + '&SeasonType=Regular+Season&Sorter=PTS'

gamelog_response = requests.get(game_url)
gamelog_response.raise_for_status() # raise exception if invalid response
gamelog_data = gamelog_response.json()['resultSets'][0]['rowSet']

team_dict = {'ATL': "Atlanta Hawks", 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets', 'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons', 'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers', 'LAC': 'LA Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies', 'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks', 'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns', 'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs', 'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'}

#Dumping data into sql
for game in gamelog_data:
    game.append(team_dict[game[7][-3:]])
    print tuple(game)
    cur.execute(add_game, tuple(game))
    # example:('22015', '977', 'Kobe Bryant', 'LAL', 'Los Angeles Lakers', '0021501228', '2016-04-13', 'LAL vs. UTA', 'W', '42', '22', '50', '0.44', '6', '21', '0.286', '10', '12', '0.833', '0', '4', '4', '4', '1', '1', '2', '1', '60', '7', '1')


###################################################################################################################
############################################  TEAM OPPONENT DATA  #################################################
###################################################################################################################

team_url = 'http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Opponent&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='

#cur.execute("CREATE TABLE teams (TEAM_ID int,TEAM_NAME varchar(255), GP int, W int, L int, W_PCT decimal(4,3), MIN int, OPP_FGM int, OPP_FGA int, OPP_FG_PCT decimal(4,3), OPP_FG3M int, OPP_FG3A int, OPP_FG3_PCT decimal(4,3), OPP_FTM int, OPP_FTA int, OPP_FT_PCT decimal(4,3), OPP_OREB int, OPP_DREB int, OPP_REB int, OPP_AST int, OPP_TOV int, OPP_STL int, OPP_BLK int, OPP_BLKA int, OPP_PF int, OPP_PFD int, OPP_PTS int, PLUS_MINUS int, CFID int, CFPARAMS varchar(255));")

team_response = requests.get(team_url)
team_response.raise_for_status() # raise exception if invalid response
teams = team_response.json()['resultSets'][0]['rowSet']

add_team = ("INSERT INTO teams "
			"(TEAM_ID,TEAM_NAME,GP,W,L,W_PCT,MIN,OPP_FGM,OPP_FGA,OPP_FG_PCT,OPP_FG3M,OPP_FG3A,OPP_FG3_PCT,OPP_FTM,OPP_FTA,OPP_FT_PCT,OPP_OREB,OPP_DREB,OPP_REB,OPP_AST,OPP_TOV,OPP_STL,OPP_BLK,OPP_BLKA,OPP_PF,OPP_PFD,OPP_PTS,PLUS_MINUS,CFID, CFPARAMS)"
			"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

for team in teams:
    print team
    cur.execute(add_team, tuple(team))


# Selecting and merging the defensive stats by season and the players gamelogs
cur.execute ("SELECT * FROM teams;")
team_data = cur.fetchall ()
new_data = []

for row in team_data:
    print list(row)
    new_data.append(list(row))

team_df = pd.DataFrame(new_data, columns=["TEAM_ID","TEAM_NAME","GP","W","L","W_PCT","MIN","OPP_FGM","OPP_FGA","OPP_FG_PCT","OPP_FG3M","OPP_FG3A","OPP_FG3_PCT","OPP_FTM","OPP_FTA","OPP_FT_PCT","OPP_OREB","OPP_DREB","OPP_REB","OPP_AST","OPP_TOV","OPP_STL","OPP_BLK","OPP_BLKA","OPP_PF","OPP_PFD","OPP_PTS","PLUS_MINUS","CFID"," CFPARAMS"])

cur.execute ("SELECT * FROM gamelog;")
gamelog_data = cur.fetchall ()
new_data = []

for row in gamelog_data:
    print list(row)
    new_data.append(list(row))

gamelog_df = pd.DataFrame(new_data, columns=["SeasonID", "PlayerID", "Player_Name", "Team_Abb", "Team_Name", "GameID", "Game_Date", "Matchup", "WL", "Min", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_pct", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS", "VIDEO_AVAILABLE", "Opponent_Name"])

new_df = pd.merge(gamelog_df, team_df, right_on = 'TEAM_NAME', left_on= 'Opponent_Name')

new_df.to_csv('/Users/cholmes/Desktop/NBA/New Stuff/gamelog_opponent_merge.csv')

db.commit()

db.close()
