import requests
import os
import json

shots_response = requests.get('http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16')
shots_response.raise_for_status() # raise exception if invalid response
shots = shots_response.json()['resultSets'][0]['rowSet']



for shot in shots:
    with open('/Users/christianholmes/NBA/players/2014/Rosters/' + shot[9] + '.json', 'a') as outfile:
        json.dump(shot, outfile)
        #with open('/Users/christianholmes/NBA/players/2014/Rosters/' + shot[9] , 'r') as data_file:
        #    data = json.load(data_file)
        #    for shot in data:
