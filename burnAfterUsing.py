
import requests
import json
import os
import datetime
months = {'APR' : 4, 'JAN' : 1,'FEB' : 2,'MAR' : 3,'MAY' : 5,'JUN' : 6,'JUL' : 7,'AUG' : 8,'SEP' : 9,'OCT' : 10,'NOV' : 11,'DEC' : 12, '01' : 1, '02' : 2, '03' : 3,'04' : 4, '05' : 5, '06' : 4, '07' : 7, '08' : 8, '09' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15, '16' : 16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22, '23' : 23, '24' : 24, '25' : 25, '26' : 26, '27' : 27, '28' : 28, '29' : 29, '30' : 30, '31' : 31}
date = [u'0021401217', u'APR 15, 2015 - CHI vs. ATL', u'H', u'W', 6, 1, 1, u'3:37', u'Defensive', u'Uncontested', 0, 2.61, u'Carroll, DeMarre', 201960, u'missed 3FG', 24.09, 0, 1, 1]


def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])

for i in os.listdir('/Users/christianholmes/NBA/players/2015/Shots/'):
    if not i.startswith('.'):
        with open('/Users/christianholmes/NBA/players/2015/Shots/' + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                if not os.path.exists('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18]):
                    os.makedirs('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18])
                with open('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_shot.json', 'a') as outfile:
                    json.dump(shot, outfile)

for i in os.listdir('/Users/christianholmes/NBA/players/2015/Rebounds/'):
    if not i.startswith('.'):
        with open('/Users/christianholmes/NBA/players/2015/Rebounds/' + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                if not os.path.exists('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18]):
                    os.makedirs('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18])
                with open('/Users/christianholmes/NBA/players/2015/Games/' + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_rebound.json', 'a') as outfile:
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
    with open('/Users/christianholmes/NBA/players/2015/Games/' + player[3] +'/' + player[6] + '_gamelog.json', 'a') as outfile:
        json.dump(player, outfile)