#make a seperate program that takes the draftkings API and outputs the predictions in an array.


from lxml import html
import requests
import time
import json
import os
import pandas as pd
import statsmodels.formula.api as smf
import constants as cs
import datetime

now = datetime.datetime.now()

months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'DEC': 12, 'NOV':11, 'OCT':10}

number_dict1 = {'block': 24, 'steal': 23, 'assist': 22, 'turnover': 25, 'rebound': 21}
number_dict2 = {'block': 22, 'steal': 21, 'assist': 19, 'turnover': 20, 'rebound': 18}

renameDict = {'kelly_oubre_jr.' : 'kelly_oubre', 'r.j._hunter': 'rj_hunter', 'chris_johnson': 'christapher_johnson', 'raul_neto': 'raulzinho_neto', 'patty_mills': 'patrick_mills', "amar'e_stoudemire": 'amare_stoudemire', 'manu_ginobili': 'emanuel_ginobili','nene_hilario': 'nene', 'danny_green': 'daniel_green','t.j._mcconnell': 'tj_mcconnell', 'c.j._watson': 'cj_watson', 'k.j._mcdaniels': 'kj_mcdaniels', 'c.j._wilcox': 'cj_wilcox', 'd.j._augustin': 'dj_augustin', 'luc_richard_mbah_a_moute': 'luc_mbah_a_moute', 'marcus_thornton': 'marcus_t_thornton','j.j._redick': 'jj_redick', 'j.j._hickson': 'jj_hickson', 'p.j._hairston': 'pj_hairston', 'mo_williams': 'maurice_williams', 't.j._warren': 'tj_warren', 'tristan_thompson': 'tristan_t_thompson', 'p.j._tucker': 'pj_tucker', 'c.j._miles': 'cj_miles', 'j.r._smith': "jr_smith", 'ryan_anderson': 'ryan_j_anderson', 'c.j._mccollum': 'cj_mccollum', 'j.j._barea': 'jose_barea', 'lou_williams': 'louis_williams', "d'angelo_russell": 'dangelo_russell', 'larry_nance_jr.': 'larry_nance', 'o.j._mayo': 'oj_mayo', "kyle_o'quinn": 'kyle_oquinn', "e'twaun_moore" : 'etwaun_moore', 'louis_amundson': 'lou_amundson', "tim_hardaway_jr.": 'timothy_hardaway', "johnny_o'bryant": 'johnny_obryant'}
teamDick = {'nor': 'NOP', 'pho': 'PHX'}
#TODO: ##################################### ALL MY TERRIBLE CODE #############################################
def expectedBetas(playerID, opposingTeam, new_date = now):
    roster = open(cs.rosterDir + opposingTeam + '.json', )
    roster = json.load(roster)
    with open(cs.shotDir + str(playerID) + '.json') as data_file:
        shot_data = json.load(data_file)


    #Every shot the player made
    game_data = []
    for i in shot_data:

        mon = months[i[1][0:3]]
        day = int(i[1][4:6])
        year = int(i[1][8:13])

        current_date = datetime.datetime(year,mon,day)

        if current_date < new_date:
            game_data.append(i)

    #Every shot against the team they're going to be playing against
    defense = []
    for player in roster:
        with open(cs.defenseDir + str(player[0]) + '.json') as defense_stuff:
            defense_data = json.load(defense_stuff)
            for i in defense_data:
                mon = months[i[1][0:3]]
                day = int(i[1][4:6])
                year = int(i[1][8:13])
                current_date = datetime.datetime(year,mon,day)
                if current_date < new_date:
                    defense.append(i)

    playerDefenderDistance = []
    playerShotDistance = []
    playerShotClock = []

    for shot in game_data:
        playerDefenderDistance.append(shot[16])
        playerShotDistance.append(shot[11])
        if shot[8] != None:
            playerShotClock.append(shot[8])

    avgPlayerDefenderDistance = sum(playerDefenderDistance)/len(playerDefenderDistance)
    avgPlayerShotDistance = sum(playerShotDistance)/len(playerShotDistance)
    avgPlayerShotClock = sum(playerShotClock)/len(playerShotClock)

    teamDefenderDistance = []
    teamShotDistance = []
    teamShotClock = []

    for shot in defense:
        teamDefenderDistance.append(shot[16])
        teamShotDistance.append(shot[11])
        if shot[8] != None:
            teamShotClock.append(shot[8])

    avgTeamDefenderDistance =  sum(teamDefenderDistance)/len(teamDefenderDistance)
    avgTeamShotDistance = sum(teamShotDistance)/len(teamShotDistance)
    avgTeamShotClock = sum(teamShotClock)/len(teamShotClock)

    #TODO: Find a better way to get these numbers
    leagueShotClock = 12.4624577172
    leagueDefenderDistance = 4.13361607305
    leagueShotDistance = 13.6198586128

    teamDiffShotClock = (leagueShotClock - avgTeamShotClock) / leagueShotClock
    teamDiffShotDistance = (leagueShotDistance - avgTeamShotDistance) / leagueShotDistance
    teamDiffDefenderDistance = (leagueDefenderDistance - avgTeamDefenderDistance) / leagueDefenderDistance

    return [avgPlayerShotClock, avgPlayerShotDistance, avgPlayerDefenderDistance, teamDiffShotClock, teamDiffShotDistance, teamDiffDefenderDistance]

#Returns average shot percentage for given player
def expectedShotPercentage(player,team, new_date = now):
    shot_data = []
    with open(cs.shotDir + str(player) + '.json', ) as data_file:
        data = json.load(data_file)
        for shot in data:
            mon = months[shot[1][0:3]]
            day = int(shot[1][4:6])
            year = int(shot[1][8:13])
            current_date = datetime.datetime(year,mon,day)
            if current_date < new_date:
                shot_data.append(shot)


    pd_shot_data = pd.DataFrame(shot_data)
    try:
        pd_shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]
    except ValueError:
        return 1

    lm = smf.ols(formula='FGM ~ CLOSE_DEF_DIST + SHOT_DIST + SHOT_CLOCK', data=pd_shot_data).fit()

    intercept = lm.params[0]
    defenderDistance = lm.params[1]
    shotDistance = lm.params[2]
    shotClock = lm.params[3]

    teamDiff = expectedBetas(player,team, new_date)

    #Shooting Percent against specific team
    spefTeam = intercept + shotClock*(teamDiff[0] + teamDiff[3]*teamDiff[0]) + shotDistance*(teamDiff[1] + teamDiff[4]*teamDiff[1]) + defenderDistance*(teamDiff[2] + teamDiff[5]*teamDiff[2])

    return spefTeam

#How many total shots the team he plays for takes on average
def expectedTeamShots(team, new_date = now):
    totalShots = []
    for i in os.listdir(cs.gameDir + str(team)):
        if not i.startswith('.') and not i.endswith('rebound.json') and not i.endswith('gamelog.json'):
            with open(cs.gameDir + team + '/' + i) as data_file:
                data = json.load(data_file)
                mon = months[data[0][1][0:3]]
                day = int(data[0][1][4:6])
                year = int(data[0][1][8:13])
                current_date = datetime.datetime(year,mon,day)
                if current_date < new_date:
                    totalShots.append(data)

    shots = 0.0

    for i in totalShots:
        shots += len(i)

    #Total number of shots that a team takes on average
    avgTeamShots = float(shots)/float(len(totalShots))
    return avgTeamShots


def teamFinder(player):
    for i in os.listdir(cs.rosterDir):
        if not i.startswith('.'):
            with open(cs.rosterDir + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        if roster[9] == '':
                            return None
                        team = roster[9]
                        id = roster[0]
                        return team

def expectedShotsTaken(player, opponent, new_date = now):

    #First find out which team he plays for by going through the rosters
    team = teamFinder(player)
    #How many total shots the team he plays for takes on average
    if team != None:
        totalShots = expectedTeamShots(team)
    if team == None:
        totalShots = 1

    with open(cs.shotDir + str(player) + '.json', ) as data_file:
        data = json.load(data_file)
        shot_data = []
        for shot in data:
            mon = months[shot[1][0:3]]
            day = int(shot[1][4:6])
            year = int(shot[1][8:13])
            current_date = datetime.datetime(year,mon,day)
            if current_date < new_date:
                shot_data.append(shot)

    shots = pd.DataFrame(shot_data)
    try:
        shots.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]
    except ValueError:
        return 0
    oldRows = float(len(shots.index))
    shots = shots.groupby('GAME_ID').median()
    rows = float(len(shots.index))
    avgPlayerShots = float(oldRows/rows)

    #Percentage of total shots that a player takes
    pctPlayerShots = avgPlayerShots/totalShots

    #Defense's effect on shots
    totalOpponentShots = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalOpponentShots += data[0][8]

    totalOpponentShots = totalOpponentShots/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        teamOpponentShots = data[0][8]

    #Percent that defense lowers total shots
    defenseShotPercentDifference =  (teamOpponentShots - totalOpponentShots) / teamOpponentShots


    #Expected number of shots that a player will take against a given opponent
    playerShots = (totalShots + (totalShots * defenseShotPercentDifference)) * pctPlayerShots

    return playerShots




def leagueAverage(year):
    avgShotDistance = []
    avgShotClock = []
    avgDefenderDistance = []

    for i in os.listdir('/Users/christianholmes/NBA/players/' +str(year) + '/Defense/'):
        if not i.startswith('.'):
            with open('/Users/christianholmes/NBA/players/' +str(year) + '/Defense/' + i, 'r') as data_file:
                data = json.load(data_file)
                for shot in data:
                    if shot[8] != None:
                        avgShotClock.append(shot[8])
                    if shot[11] != None:
                        avgShotDistance.append(shot[11])
                    if shot[16] != None:
                        avgDefenderDistance.append(shot[16])

    shotClock = sum(avgShotClock)/len(avgShotClock)
    shotDistance = sum(avgShotDistance)/len(avgShotDistance)
    defenderDistance = sum(avgDefenderDistance)/len(avgDefenderDistance)

    print shotClock
    print shotDistance
    print defenderDistance


def expectedFouls(player,opponent, new_date = now):
    #Find the number of fouls he draws per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        fouls = []
        madeShots = []
        for game in dataFile:
            mon = int(game[6][5:7])
            day = int(game[6][8:10])
            year = int(game[6][0:4])
            current_date = datetime.datetime(year,mon,day)
            if new_date > current_date:
                fouls.append(game[17])
                madeShots.append(game[16])
        if len(fouls) > 0:
            avgPlayerFTs = float(sum(fouls))/float(len(fouls))
        else:
            avgPlayerFTs = 0
        if float(sum(madeShots)) > 0:
            fgPCT = float(sum(madeShots)/float(sum(fouls)))
        else:
            fgPCT = 0.75

    totalFTs = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalFTs += data[0][17]

    avgFouls = totalFTs/30

    #16 = Made Fouls
    #17 = Attempted Fouls

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamFTs = data[0][17]


    #Percent that defense lowers total shots
    defenseFoulPercentDifference =  (opponentTeamFTs - avgFouls) / opponentTeamFTs

    #Expected number of shots that a player will take against a given opponent
    avgPlayerFTs = avgPlayerFTs + (avgPlayerFTs * defenseFoulPercentDifference)

    return fgPCT*avgPlayerFTs

def expectedPoints(player,opposingTeam, new_date = now):
    shotPCT = expectedShotPercentage(player, opposingTeam, new_date)
    expectedShots = expectedShotsTaken(player, opposingTeam, new_date)
    fouls = expectedFouls(player,opposingTeam, new_date)

    with open(cs.shotDir + str(player) + '.json') as data_file:
        shots = json.load(data_file)
        twos = 0
        shot_data = []
        for shot in shots:
            mon = months[shot[1][0:3]]
            day = int(shot[1][4:6])
            year = int(shot[1][8:13])
            current_date = datetime.datetime(year,mon,day)
            if current_date < new_date:
                shot_data.append(shot)
                if shot[12] == 2:
                    twos += 1
        if len(shot_data) > 0:
            twoPercent = float(twos)/float(len(shot_data))
        else:
            twoPercent = 0.65
        threePercent = 1.0 - twoPercent


    points = (shotPCT*expectedShots*twoPercent*2) + (shotPCT*expectedShots*threePercent*3) + fouls
    threePointers = shotPCT*expectedShots*threePercent

    return [points, threePointers]

leagueShotClock2014 = 12.4624577172
leagueDefenderDistance2014 = 13.6198586128
leagueShotDistance2014 = 4.13361607305

def statChanger(player,opponent, stat, new_date = now):
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
    stats = []
    for game in dataFile:
        mon = int(game[6][5:7])
        day = int(game[6][8:10])
        year = int(game[6][0:4])

        current_date = datetime.datetime(year,mon,day)

        if current_date < new_date:
            stats.append(game[number_dict1[stat]])
    if len(stats) == 0:
        avgPlayerStat = 0
    else:
        avgPlayerStat = float(sum(stats))/float(len(stats))

    totalStats = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalStats += data[0][number_dict2[stat]]

    avgStats = totalStats/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamStats = data[0][number_dict2[stat]]

    defenseStatPercentDifference =  (opponentTeamStats - avgStats) / opponentTeamStats

    avgPlayerStats = avgPlayerStat + (avgPlayerStat * defenseStatPercentDifference)

    return avgPlayerStats


def expectedSteals(player, opponent, new_date = now):
    return statChanger(player, opponent, 'steal', new_date)

def expectedBlocks(player, opponent, new_date = now):
    return statChanger(player, opponent, 'block', new_date)

def expectedAssists1(player, opponent, new_date = now):
    return statChanger(player, opponent, 'assist', new_date)

def expectedTurnovers(player, opponent, new_date = now):
    return statChanger(player, opponent, 'turnover', new_date)

def expectedRebounds(player, opponent, new_date = now):
    return statChanger(player, opponent, 'rebound', new_date)


def DKPoints(player, opponent, new_date = now):
    pointStuff = expectedPoints(player, opponent, new_date)
    points = pointStuff[0]
    threePointers = pointStuff[1]
    assists = expectedAssists1(player, opponent, new_date)
    rebounds = expectedRebounds(player, opponent, new_date)
    blocks = expectedBlocks(player, opponent, new_date)
    steals = expectedSteals(player, opponent, new_date)
    turnover = expectedTurnovers(player, opponent, new_date)

    totalPoints = points + (0.5 * threePointers) + (1.5 * assists) + (1.25 * rebounds) + (2 * blocks) + (2 * steals) - (0.5 * turnover)

    totalPointsList = [points, assists, rebounds, blocks, steals]

    temp = 0
    for i in totalPointsList:
        if i >= 10:
            temp += 1

    if temp >= 3:
        totalPoints += 3

    if temp >= 2:
        totalPoints += 1.5

    return totalPoints



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

#This has been commented out
'''
class playersPull:
    requests.get('http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=${season}',headers={'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"})

    players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=${season}'
    apiPull = None

    def __init__(self, player_macros=None):
         if player_macros is None:
              player_macros = cs.player_macro
         self.apiPull = ApiPull(self.players_url, player_macros)

    def get(self):
         return requests.get('http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=${season}',headers={'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"})
'''


def statArraySetup(urlNumber, new_date = now):
    shots_response = requests.get('https://www.draftkings.com/lineup/getavailableplayers?draftGroupId=' + str(urlNumber))
    shots_response.raise_for_status()
    shots = shots_response.json()['playerList']

    with open(cs.rosterDir + 'All.json') as data_file:
        allPlayers = json.load(data_file)
        predictedPoints = {}

        playerArray = "Date;GID;Pos;Name;Starter;DK Pts;DK Salary;Team;H/A;Oppt;Team Score;Oppt Score;Minutes;Stat line\n"

        for player in shots:
            statArray = ""

            name = player['fnu'] + ' ' + player['lnu']
            name = name.replace(' ', '_').lower()

            if name in renameDict:
                name = renameDict[name]

            teamDict = {1: 'ATL', 2: 'BOS', 3: 'NOP', 4: 'DEN', 5: 'CLE', 6: 'DAL', 7: 'CHI', 8: 'DET', 9: 'GSW', 10: 'HOU', 11: 'IND', 12: 'LAC', 13: 'LAL', 14: 'MIA', 15: 'MIL', 16: 'MIN', 17: 'BKN', 18: 'NYK', 19: 'ORL', 20: 'PHI', 21: 'PHX', 22:'POR', 23: 'SAC', 24: 'SAS', 25: 'OKC', 26: 'UTA', 27: 'WAS', 28: 'TOR', 29: 'MEM', 5312: 'CHA'}
            for i in allPlayers:
                if i[5] == name:
                    id = i[0]
                    if player['i'] == "O":
                        predictedPoints[name] = 0
                        break
                    dkPoints = DKPoints(id, str(teamDict[player['tid']]), new_date)
                    predictedPoints[name] = dkPoints

            statArray = statArray + time.strftime("%Y%m%d") + ';'
            statArray = statArray + 'None' + ';' #'gameID'
            statArray = statArray + str(player['pn']) + ';'
            statArray = statArray + str(name) + ';'
            statArray = statArray + 'None' + ';' #'Starter?

            statArray = statArray + str(predictedPoints[name]) + ';'

            statArray = statArray + str(player['s']) + ';'
            statArray = statArray + 'None' + ';' #'Team'
            statArray = statArray + 'None' + ';' #'Home?'
            statArray = statArray + 'None' + ';' #'Opponent'
            statArray = statArray + 'None' + ';' #'teamScore'
            statArray = statArray + 'None' + ';' #'opponentScore'
            statArray = statArray + 'None' + ';' #'minutes'
            statArray = statArray + 'None' + ';' #'statLine'
            playerArray = playerArray + statArray + "|||"
    return [playerArray]




#TODO ########################################### THE END OF MY TERRIBLE CODE ################################################

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
         return self.dkpoints / self.salary

     def __lt__(self, other):
         return self.getValue() > other.getValue()

     def out(self):
        print self.name, self.salary

class shotScrapeRG:
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

    def getRG(self, predict = False, reset=False, new_date = now):
        if reset or self.data is None:
            page = requests.get(self.url)
            self.data = page.content
        t = html.fromstring(self.data)
        rawDayData = t.xpath('//table/pre/text()')
        players = []

        with open(cs.rosterDir + 'All.json') as datafile:

            allPlayers = json.load(datafile)


            for player in rawDayData[0].split('\n')[1:]:
                if player is '' :
                    continue
                fName = player.split(';')[3].split(', ')[1].lower()
                lName = player.split(';')[3].split(', ')[0].lower()
                name = fName + '_' + lName
                team = player.split(';')[7]

                if name in renameDict:
                    name = renameDict[name]

                if team in teamDick:
                    team = teamDick[team]

                for i in allPlayers:
                    if i[5] == name:
                        id = i[0]
                        dkPoints = DKPoints(id, team, new_date)
                        predictedPoints = dkPoints
                scrote = player.split(';')
                if predict == True:
                    scrote[5] = str(predictedPoints)

                players.append(playerDayFromRotoWorld(scrote))
        return players


class shotScrapeDK:
    def __init__(self, id):
        self.id = id

    def getDK(self, new_date = now, reset=False):
        rawDayData = statArraySetup(self.id, new_date)
        players = []
        for player in rawDayData[0].split('|||')[1:]:
            if player is '':
                continue
            players.append(playerDayFromRotoWorld(player.split(';')))

        return players




#TODO: 2/4: You just finished the above class, and it looks like you can now make real predictions based on the team they're going against and over a certain date range. The next step is to write a function that checks the predicted team vs the ideal team. It should output some ratio of predicted points/ideal points and then fuck with that.
class dkTeam:
    team_salary=50000
    def __init__(self):
        self.players = []
        self.pg = None
        self.sg = None
        self.sf = None
        self.c = None
        self.pf = None
        self.util = None
        self.g = None
        self.f = None

    def isOverCap(self):
        return sum([p.salary for p in self.players]) > self.team_salary

    def isValidTeam(self):
        if self.isOverCap():
            return False
        if self.pg is None or self.sg is None or self.sf is None or self.pf is None:
            return False
        if self.util is None or self.c is None or self.f is None or self.g is None:
            return False
        return True

    def getNumRemainingPlayers(self):
        return 8 - len(self.players)

    def copy(self, other):
        other.players = list(self.players)
        other.pg = self.pg
        other.sg = self.sg
        other.sf = self.sf
        other.c = self.c
        other.pf = self.pf
        other.util = self.util
        other.g = self.g
        other.f = self.f

    def clearPlayers(self):
        self.players=[]
        self.pg = None
        self.sg = None
        self.sf = None
        self.c = None
        self.pf = None
        self.util = None
        self.g = None
        self.f = None

    def addPG(self, pg):
        if self.pg is not None:
            return False
        if pg.pos != 'PG':
            return False
        self.pg = pg
        if self.isOverCap() or pg in self.players:
            self.pg = None
            return False
        self.players.append(pg)
        return True

    def removePG(self):
        if self.pg is not None:
            self.players.remove(self.pg)
            self.pg = None

    def addSG(self, sg):
        if self.sg is not None:
            return False
        if sg.pos != 'SG':
            return False
        self.sg = sg
        if self.isOverCap() or sg in self.players:
            self.sg = None
            return False
        self.players.append(sg)
        return True

    def removeSG(self):
        if self.sg is not None:
            self.players.remove(self.sg)
            self.sg = None

    def addPF(self, pf):
        if self.pf is not None:
            return False
        if pf.pos != 'PF':
            return False
        self.pf = pf
        if self.isOverCap() or pf in self.players:
            self.pf = None
            return False
        self.players.append(pf)
        return True

    def removePF(self):
        if self.pf is not None:
            self.players.remove(self.pf)
            self.pf = None

    def addSF(self, sf):
        if self.sf is not None:
            return False
        if sf.pos != 'SF':
            return False
        self.sf = sf
        if self.isOverCap() or sf in self.players:
            self.sf = None
            return False
        self.players.append(sf)
        return True

    def removeSF(self):
        if self.sf is not None:
            self.players.remove(self.sf)
            self.sf = None

    def addC(self, c):
        if self.c is not None:
            return False
        if c.pos != 'C':
            return False
        self.c = c
        if self.isOverCap() or c in self.players:
            self.c = None
            return False
        self.players.append(c)
        return True

    def removeC(self):
        if self.c is not None:
            self.players.remove(self.c)
            self.c = None

    def addG(self, g):
        if self.g is not None:
            return False
        if g.pos != 'PG' and g.pos != 'SG':
            return False
        self.g = g
        if self.isOverCap() or g in self.players:
            self.g = None
            return False
        self.players.append(g)
        return True

    def removeG(self):
        if self.g is not None:
            self.players.remove(self.g)
            self.g = None

    def addF(self, f):
        if self.f is not None:
            return False
        if f.pos != 'PF' and f.pos != 'SF':
            return False
        self.f = f
        if self.isOverCap() or f in self.players:
            self.f = None
            return False
        self.players.append(f)
        return True

    def removeF(self):
        if self.f is not None:
            self.players.remove(self.f)
            self.f = None

    def addUtil(self, util):
        if self.util is not None:
            return False
        self.util = util
        if self.isOverCap() or util in self.players:
            self.util = None
            return False
        self.players.append(util)
        return True

    def removeUtil(self):
        if self.util is not None:
            self.players.remove(self.util)
            self.util = None

    def getScore(self):
        return sum([q.dkpoints for q in self.players])

    def getRemainingBudget(self):
        return self.team_salary - sum([p.salary for p in self.players])

    #def printTeam(self):
        #print 'PG / SG / SF / PF / C / G / F / Util: ' + self.pg.print() + self.sg.print() + self.sf.print() + self.pf.print() + self.c.print() + self.g.print() + self.f.print() + self.util.print()


class SetOfPlayers:
    def key1(self, a):
        return(a.salary, -a.dkpoints)

    def getValidPlayers(self,players,num=3):
        tmp1=[0] * num
        players.sort(key=self.key1)
        counter=0
        while counter < len(players):
            tmp1.sort(reverse=True)
            player = players[counter]
            if player.dkpoints <= tmp1[-1]:
                players.remove(player)
                continue
            tmp1.pop()
            tmp1.append(player.dkpoints)
            counter += 1
        return players

    def __init__(self, players):
        players.sort()
        self.bestVal = players[0].dkpoints / players[0].salary
        self.pgs=self.getValidPlayers([x for x in players if x.pos == 'PG' and x.dkpoints > 0])
        self.sgs=self.getValidPlayers([x for x in players if x.pos == 'SG' and x.dkpoints > 0])
        self.gs=self.getValidPlayers( self.sgs + self.pgs )
        self.pfs=self.getValidPlayers([x for x in players if x.pos == 'PF' and x.dkpoints > 0])
        self.sfs=self.getValidPlayers([x for x in players if x.pos == 'SF' and x.dkpoints > 0])
        self.fs=self.getValidPlayers( self.pfs + self.sfs )
        self.cs=self.getValidPlayers([x for x in players if x.pos == 'C' and x.dkpoints > 0], 2)
        self.uts=self.getValidPlayers( self.gs + self.fs + self.cs )

    def notGoingToWork(self, team, bestTeam):
        if team.getNumRemainingPlayers() * 3000 > team.getRemainingBudget():
            return True
        if team.getRemainingBudget() * self.bestVal + team.getScore() < bestTeam.getScore():
            return True
        return False

    def getPerms(self):

        return len(self.pgs) * len(self.sgs) * len(self.gs) * len(self.sfs) * len(self.pfs) * len(self.cs)* len(self.fs) * len(self.uts)

    def getStats(self):
        #TODO: I added this logic to fix it when it divides by zero. Not sure if this was the right way to do this, so check it out later.
        if self.getPerms() == 0:
            return (self.bestTeam.getScore(), self.tries, self.getPerms(), float(self.tries) / 1, len(self.improvements), self.improvements)
        return (self.bestTeam.getScore(), self.tries, self.getPerms(), float(self.tries) / self.getPerms(), len(self.improvements), self.improvements)

    def findBest(self):
        self.pgs.sort()
        self.sgs.sort()
        self.gs.sort()
        self.pfs.sort()
        self.sfs.sort()
        self.cs.sort()
        self.fs.sort()
        self.uts.sort()
        self.bestTeam = dkTeam()
        self.tries = 0
        self.improvements = []
        for pg in self.pgs:
            team = dkTeam()
            team.removePF()
            if not team.addPG(pg) or self.notGoingToWork(team, self.bestTeam):
                team.removePG()
                continue
            for sg in self.sgs:
                if not team.addSG(sg) or self.notGoingToWork(team, self.bestTeam):
                    team.removeSG()
                    continue
                for g in self.gs:
                    if not team.addG(g) or self.notGoingToWork(team, self.bestTeam):
                        team.removeG()
                        continue
                    for pf in self.pfs:
                        if not team.addPF(pf) or self.notGoingToWork(team, self.bestTeam):
                            team.removePF()
                            continue
                        for sf in self.sfs:
                            if not team.addSF(sf) or self.notGoingToWork(team, self.bestTeam):
                                team.removeSF()
                                continue
                            for f in self.fs:
                                if not team.addF(f) or self.notGoingToWork(team, self.bestTeam):
                                    team.removeF()
                                    continue
                                for c in self.cs or self.notGoingToWork(team, self.bestTeam):
                                    if not team.addC(c) or self.notGoingToWork(team, self.bestTeam):
                                        team.removeC()
                                        continue
                                    for ut in self.uts:
                                        if not team.addUtil(ut) or self.notGoingToWork(team, self.bestTeam):
                                            team.removeUtil()
                                            continue
                                        self.tries += 1
                                        if team.getScore() > self.bestTeam.getScore() and team.isValidTeam():
                                            self.improvements.append((self.tries, self.bestTeam.getScore()))
                                            self.bestTeam.clearPlayers()
                                            team.copy(self.bestTeam)
                                        team.removeUtil()
                                    team.removeC()
                                team.removeF()
                            team.removeSF()
                        team.removePF()
                    team.removeG()
                team.removeSG()



def doThing(y):
    ys=[y[x:x+20] for x in range(10)]
    ns=[SetOfPlayers(x) for x in ys]
    for n in ns:
        t1=time.time()
        n.findBest()
        t2=time.time()
        print n.getPerms(), 'NPERMS'
        print len(n.improvements), 'LENNNIMPROVEMENTS'
        print n.improvements, 'NIMPROVEMENTS'
        print n.getStats(), 'GETSTATS'
        if len(n.bestTeam.players) is not 0:
            print [x.name for x in n.bestTeam.players], 'BESTSTATS'
        return n.getStats()

        #Uncomment the following code if you want the whole shebang, not just the first lineup's score (which tends to be the highest, #TODO: but you haven't tested as of 2/11
        '''
        print n.getPerms(), 'NPERMS'
        print len(n.improvements), 'LENNNIMPROVEMENTS'
        print n.improvements, 'NIMPROVEMENTS'
        print n.getStats(), 'GETSTATS'
        if len(n.bestTeam.players) is not 0:
            print [x.name for x in n.bestTeam.players], 'BESTSTATS'
        '''





def __mainRG__(day, month, year, predict = True):
    yesterday=shotScrapeRG(str(day),str(month), str(year), None, True)
    players=yesterday.getRG(predict)
    players.sort()
    team = doThing(players)
    return team[0]

def __mainDK__():
    #TODO: Pull this number in dynamically from the draftkings lineup page
    yesterday = shotScrapeDK(8276)
    players = yesterday.getDK()
    players.sort()
    team = doThing(players)
    return team[0]

def lineupComparison(day, month, year, today = now):

    ratios = []
    current_date = datetime.datetime(year,month,day)

    delta = datetime.timedelta(days=1)

    while current_date < today:
        predictTeamRG = __mainRG__(current_date.day, current_date.month, current_date.year, True)
        perfectTeamRG = __mainRG__(current_date.day, current_date.month, current_date.year, False)

        ratios.append(predictTeamRG/perfectTeamRG)

        current_date += delta
        print ratios
    return ratios


print lineupComparison(8, 2, 2016)


#TODO: 2/11: You adjusted the lineup picks function to points/salary instead of points^3/salary. This is because the lineup picks functions breaks because there are too many options to choose from. It'd be great if it didn't break.


