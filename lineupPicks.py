#make a seperate program that takes the draftkings API and outputs the predictions in an array.


from lxml import html
import requests
import operator
import time
import json
import os
import pandas as pd
import statsmodels.formula.api as smf
import constants

#TODO: ##################################### ALL MY TERRIBLE CODE #############################################
def expectedBetas(playerID, opposingTeam):
    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2015/Shots/' + str(playerID) + '.json', )
    shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    roster = open('/Users/christianholmes/NBA/players/2015/Rosters/' + opposingTeam + '.json', )
    roster = json.load(roster)

    defense = pd.read_json('/Users/christianholmes/NBA/players/2015/Defense/' + str(roster[0][0]) + '.json' , 'r')
    defense.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    means = shot_data.mean()

    avgDefenderDistance = means[10]
    avgShotDistance = means[7]
    avgShotClock = means[4]

    leagueShotClock = 12.4624577172
    leagueShotDistance = 13.6198586128
    leagueDefenderDistance = 4.13361607305

    teamDiffShotClock = (leagueShotClock - avgShotClock) / leagueShotClock
    teamDiffShotDistance = (leagueShotDistance - avgShotDistance) / leagueShotDistance
    teamDiffDefenderDistance = (leagueDefenderDistance - avgDefenderDistance) / leagueDefenderDistance

    return [avgShotClock, avgShotDistance, avgDefenderDistance, teamDiffShotClock, teamDiffShotDistance, teamDiffDefenderDistance]


#Returns average shot percentage for given player -DONE
def expectedShotPercentage(player,team):

    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2015/Shots/' + str(player) + '.json', )

    shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    lm = smf.ols(formula='FGM ~ CLOSE_DEF_DIST + SHOT_DIST + SHOT_CLOCK', data=shot_data).fit()

    intercept = lm.params[0]
    defenderDistance = lm.params[1]
    shotDistance = lm.params[2]
    shotClock = lm.params[3]

    #determine averages for player in question:
    means = shot_data.mean()


    avgDefenderDistance = means[10]
    avgShotDistance = means[7]
    avgShotClock = means[4]

    teamDiff = expectedBetas(player,team)

    leagueShotClock = 12.4624577172
    leagueDefenderDistance = 4.13361607305
    leagueShotDistance = 13.6198586128

    #Shooting Percent against average team
    avgTeam = intercept + shotClock*leagueShotClock + shotDistance*leagueShotDistance + defenderDistance*leagueDefenderDistance

    #Shooting Percent against specific team
    spefTeam = intercept + shotClock*teamDiff[0] + shotDistance*teamDiff[1] + defenderDistance*teamDiff[2]

    actualTeam = intercept + shotClock*avgShotClock + shotDistance*avgShotDistance + defenderDistance*avgDefenderDistance

    return spefTeam

#How many total shots the team he plays for takes on average
def expectedTeamShots(team):
    totalShots = []
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Games/' + team):
        if not i.startswith('.') and not i.endswith('rebound.json') and not i.endswith('gamelog.json'):
            with open('/Users/christianholmes/NBA/players/2015/Games/' + team + '/' + i) as data_file:
                data = json.load(data_file)
                totalShots.append(data)
    shots = 0

    for i in totalShots:
        shots += len(i)

    #Total number of shots that a team takes on average
    print totalShots
    avgTeamShots = float(shots)/float(len(totalShots))
    return avgTeamShots


def teamFinder(player):
    #First find out which team he plays for by going through the rosters
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Rosters/'):
        if not i.startswith('.'):
            with open('/Users/christianholmes/NBA/players/2015/Rosters/' + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        team = roster[9]
                        id = roster[0]
                        break


def expectedShotsTaken(player,opponent):

    #First find out which team he plays for by going through the rosters
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Rosters/'):
        if not i.startswith('.'):
            with open('/Users/christianholmes/NBA/players/2015/Rosters/' + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        team = roster[9]
                        id = roster[0]
                        break

    #How many total shots the team he plays for takes on average
    totalShots = expectedTeamShots(team)

    shots = pd.read_json('/Users/christianholmes/NBA/players/2015/Shots/' + str(player) + '.json')
    shots.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    oldRows = float(len(shots.index))
    shots = shots.groupby('GAME_ID').median()
    rows = float(len(shots.index))
    avgPlayerShots = float(oldRows/rows)

    #Percentage of total shots that a player takes
    pctPlayerShots = avgPlayerShots/totalShots

    #Defense's effect on shots
    totalOpponentShots = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalOpponentShots += data[0][8]

    totalOpponentShots = totalOpponentShots/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
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


def expectedFouls(player,opponent):
    #Find the number of fouls he draws per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        fouls = []
        for game in dataFile:
            fouls.append(game[17])
        avgPlayerFTs = float(sum(fouls))/float(len(fouls))


    totalFTs = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalFTs += data[0][16]

    avgFouls = totalFTs/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamFTs = data[0][16]


    #Percent that defense lowers total shots
    defenseFoulPercentDifference =  (opponentTeamFTs - avgFouls) / opponentTeamFTs

    #Expected number of shots that a player will take against a given opponent
    avgPlayerFTs = avgPlayerFTs + (avgPlayerFTs * defenseFoulPercentDifference)

    return avgPlayerFTs

def expectedFouls(player,opponent):
    #Find the number of fouls he draws per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        fouls = []
        madeShots = []
        for game in dataFile:
            fouls.append(game[17])
            madeShots.append(game[16])
        avgPlayerFTs = float(sum(fouls))/float(len(fouls))
        if float(sum(madeShots)) > 0:
            fgPCT = float(sum(madeShots)/float(sum(fouls)))
        else:
            fgPCT = 0.75

    totalFTs = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalFTs += data[0][14]

    avgFouls = totalFTs/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamFTs = data[0][14]


    #Percent that defense lowers total shots
    defenseFoulPercentDifference =  (opponentTeamFTs - avgFouls) / opponentTeamFTs

    #Expected number of shots that a player will take against a given opponent
    avgPlayerFTs = avgPlayerFTs + (avgPlayerFTs * defenseFoulPercentDifference)


    return fgPCT*avgPlayerFTs


def expectedPoints(player,opposingTeam):
    shotPCT = expectedShotPercentage(player, opposingTeam)
    expectedShots = expectedShotsTaken(player, opposingTeam)
    fouls = expectedFouls(player,opposingTeam)
    #TODO: This should be a seperate function

    with open('/Users/christianholmes/NBA/players/2015/Shots/' + str(player) + '.json') as data_file:
        shots = json.load(data_file)
        twos = 0
        for shot in shots:
            if shot[12] == 2:
                twos += 1
        twoPercent = float(twos)/float(len(shots))
        threePercent = 1.0 - twoPercent


    points = (shotPCT*expectedShots*twoPercent*2) + (shotPCT*expectedShots*threePercent*3) + fouls
    threePointers = shotPCT*expectedShots*threePercent

    return [points, threePointers]

#shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]



leagueShotClock = 12.4624577172
leagueDefenderDistance = 13.6198586128
leagueShotDistance = 4.13361607305

#Find league averages of closest defender. (Should I do by shooting guard/center?). Then pop the averages into that formula. Then find the average distance of the closest defender in the team you're playing against.
#Pop that number into the equation. Figure out the difference between the two. Then you know the expected difference in points per shot.
#After that you need to find the expected number of shots he'll take in a game. Find the percentage of the total shots that he takes per game. Then find the average number of shots that the opposing team allows per year, vs the league average.
#Then you can figure out the percent difference in total shots and the number of shots you expect this player's team to take. Then find the expected number of shots he'll take. Finally, multiply that number by the points per shot equation above. Then you know the number of shots he'll take per game!


########################REST OF DK POINTS####################################
def expectedBlocks(player,opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        blocks = []
        for game in dataFile:
            blocks.append(game[24])
        avgPlayerBlocks = float(sum(blocks))/float(len(blocks))

    totalBlocks = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalBlocks += data[0][22]

    avgBlocks = totalBlocks/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamBlocks = data[0][22]

    #Percent that defense lowers total shots
    defenseBlockPercentDifference =  (opponentTeamBlocks - avgBlocks) / opponentTeamBlocks

    #Expected number of shots that a player will take against a given opponent
    avgPlayerBlocks = avgPlayerBlocks + (avgPlayerBlocks * defenseBlockPercentDifference)

    return avgPlayerBlocks


def expectedSteals(player,opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        steals = []
        for game in dataFile:
            steals.append(game[23])
        avgPlayerSteals = float(sum(steals))/float(len(steals))

    totalSteals = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalSteals += data[0][21]

    avgSteals = totalSteals/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamSteals = data[0][21]

    #Percent that defense lowers total shots
    defenseStealPercentDifference =  (opponentTeamSteals - avgSteals) / opponentTeamSteals

    #Expected number of shots that a player will take against a given opponent
    avgPlayerSteals = avgPlayerSteals + (avgPlayerSteals * defenseStealPercentDifference)

    return avgPlayerSteals

def expectedAssists1(player,opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        assists = []
        for game in dataFile:
            assists.append(game[22])
        avgPlayerAssists = float(sum(assists))/float(len(assists))

    totalAssists = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalAssists += data[0][19]

    avgAssists = totalAssists/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamAssists = data[0][19]

    #Percent that defense lowers total shots
    defenseAssistPercentDifference =  (opponentTeamAssists - avgAssists) / opponentTeamAssists

    #Expected number of shots that a player will take against a given opponent
    avgPlayerAssists = avgPlayerAssists + (avgPlayerAssists * defenseAssistPercentDifference)

    return avgPlayerAssists

def expectedTurnovers(player, opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        turnovers = []
        for game in dataFile:
            turnovers.append(game[25])
        avgPlayerTurnovers = float(sum(turnovers))/float(len(turnovers))

    totalTurnovers = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalTurnovers += data[0][20]

    avgTurnovers = totalTurnovers/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamTurnovers = data[0][20]

    #Percent that defense lowers total shots
    defenseTurnoverPercentDifference =  (opponentTeamTurnovers - avgTurnovers) / opponentTeamTurnovers

    #Expected number of shots that a player will take against a given opponent
    avgPlayerTurnovers = avgPlayerTurnovers + (avgPlayerTurnovers * defenseTurnoverPercentDifference)

    return avgPlayerTurnovers


def expectedRebounds(player, opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2015/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        rebounds = []
        for game in dataFile:
            rebounds.append(game[21])
        avgPlayerRebounds = float(sum(rebounds))/float(len(rebounds))

    totalRebounds = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2015/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2015/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalRebounds += data[0][18]

    avgRebounds = totalRebounds/30

    with open('/Users/christianholmes/NBA/players/2015/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamRebounds = data[0][18]

    #Percent that defense lowers total shots
    defenseReboundPercentDifference =  (opponentTeamRebounds - avgRebounds) / opponentTeamRebounds

    #Expected number of shots that a player will take against a given opponent
    avgPlayerRebounds = avgPlayerRebounds + (avgPlayerRebounds * defenseReboundPercentDifference)

    return avgPlayerRebounds

def DKPoints(player, opponent):
    pointStuff = expectedPoints(player, opponent)
    points = pointStuff[0]
    threePointers = pointStuff[1]
    assists = expectedAssists1(player, opponent)
    rebounds = expectedRebounds(player, opponent)
    blocks = expectedBlocks(player, opponent)
    steals = expectedSteals(player, opponent)
    turnover = expectedTurnovers(player, opponent)

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

class playersPull:
    players_url = 'http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=${season}'
    apiPull = None

    def __init__(self, player_macros=None):
         if player_macros is None:
              player_macros = {'season': '2015-16'}
         self.apiPull = ApiPull(self.players_url, player_macros)

    def get(self):
         return self.apiPull.get()


#TODO: Open the directory of players

def statArraySetup(urlNumber):
    shots_response = requests.get('https://www.draftkings.com/lineup/getavailableplayers?draftGroupId=' + str(urlNumber))
    shots_response.raise_for_status() # raise exception if invalid response
    shots = shots_response.json()['playerList']

    allPlayers = playersPull().get()
    roster = {}
    todaysPlayers = {}
    print allPlayers
    print shots
    playerArray = "Date;GID;Pos;Name;Starter;DK Pts;DK Salary;Team;H/A;Oppt;Team Score;Oppt Score;Minutes;Stat line\n"

    for player in shots:
        statArray = ""

        name = player['fnu'] + ' ' + player['lnu']
        name = name.replace(' ', '_').lower()

        if name == 'j.j._barea':
            name = 'jose_barea' #TODO: WTF jj barea
        if name == 'lou_williams':
            name = 'louis_williams' #TODO: OMG
        if name == "d'angelo_russell":
            name = 'dangelo_russell'
        if name == 'larry_nance_jr.':
            name = 'larry_nance'
        if name == 'o.j._mayo':
            name = 'oj_mayo'
        if name == "kyle_o'quinn":
            name = 'kyle_oquinn'
        if name == "e'twaun_moore":
            name = 'etwaun_moore'
        if name == 'louis_amundson':
            name = 'lou_amundson'
        if name == "tim_hardaway_jr.":
            name = 'timothy_hardaway'
        if name == "johnny_o'bryant":
            name = 'johnny_obryant'
        print name
        for i in allPlayers:
            if i[5] == name:
                id = i[0]

                if player['i'] == "O":
                    todaysPlayers[name] = 0
                    break
                try:
                    dkPoints = DKPoints(id, 'NYK')
                    todaysPlayers[name] = dkPoints
                except ValueError: #TODO: Only for 2014, this can be removed once we have 2015...right?
                    todaysPlayers[name] = 'None'

        statArray = statArray + time.strftime("%Y%m%d") + ';'
        statArray = statArray + 'None' + ';' #'gameID'
        statArray = statArray + str(player['pn']) + ';'
        statArray = statArray + str(name) + ';'
        statArray = statArray + 'None' + ';' #'Starter?
        statArray = statArray + str(todaysPlayers[name]) + ';' #TODO: Where the predictions will go!
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
         return self.dkpoints * self.dkpoints * self.dkpoints / self.salary

     def __lt__(self, other):
         return self.getValue() > other.getValue()

	 def out(self):
		 print self.name + ' ' + self.salary + ' '

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
    	#rawDayData = t.xpath('//table/pre/text()') #TODO: You
    	#print "this is rawDayData: "
    	#print rawDayData
    	rawDayData = statArraySetup(8266)
    	print "This is rawDayData:"
    	print rawDayData

    	players = []
        for player in rawDayData[0].split('|||')[1:]:
            print player
            if player is '' :
                continue
            players.append(playerDayFromRotoWorld(player.split(';')))
        return players

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
        print n.getPerms()
        print len(n.improvements)
        print n.improvements
        print n.getStats()
        if len(n.bestTeam.players) is not 0:
            print [x.name for x in n.bestTeam.players]





def __main__():
    yesterday=shotScrape('0','0','0', None, True)
    players=yesterday.get()
    players.sort()
    doThing(players)

print __main__()



