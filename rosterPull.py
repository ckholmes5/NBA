import requests
import os
import json
import time

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

shots_response = requests.get('https://www.draftkings.com/lineup/getavailableplayers?draftGroupId=8266')
shots_response.raise_for_status() # raise exception if invalid response
shots = shots_response.json()['playerList']
statArray = []
for i in range(14):
    statArray.append('')

stuff = playersPull().get()
print stuff



for shot in shots:
    statArray[0] = time.strftime("%m/%d/%Y")
    statArray[1] = None #'gameID'
    statArray[2] = shot['pn']
    statArray[3] = shot['fnu'] + ' ' + shot['lnu']
    statArray[4] = None #'Starter?
    statArray[5] = 'DK Points' #TODO: Where the predictions will go!
    statArray[6] = shot['s']
    statArray[7] = None #'Team'
    statArray[8] = None #'Home?'
    statArray[9] = None #'Opponent'
    statArray[10] = None #'teamScore'
    statArray[11] = None #'opponentScore'
    statArray[12] = None #'minutes'
    statArray[13] = None #'statLine'

    name = statArray[3].replace(' ', '_').lower()




    print statArray


#{u'ppg': u'5.0', u'htid': 4, u'lnu': u'Vaughn', u'pid': 847010, u'pp': 0, u'atid': 15, u'ln': u'Vaughn', u'pcode': 5477, u'tid': 15, u'swp': False, u'pn': u'SG', u'ExceptionalMessages': [], u'tsid': 3991220, u'IsDisabledFromDrafting': False, u'news': 0, u'htabbr': u'Chi', u'fn': u'Rashad', u'fnu': u'Rashad', u'posid': 33, u'atabbr': u'Mil', u'i': u'', u's': 3000, u'slo': None, u'or': 5}
