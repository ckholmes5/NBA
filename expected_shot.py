import json
import os
import pandas as pd
import statsmodels.formula.api as smf


#The point of this file is to find the expected number of points a certain player will score in a given game.

#The first step to accomplish this we're going to use Benjamin Morris's formula of glm(made ~ SHOT_CLOCK + SHOT_DIST + CLOSE_DEF_DIST,family=binomial,data=filter(shots,!is.na(SHOT_CLOCK)))
#In english, he is predicting if a shot will be made depending on three variables: amount of time left on shot clock, the distance the shot is taken from, and the distance of the closest defender.
#To fill in this formula, we'll need to predict all three of those variables.

#Regression for the likelihood of making a shot:


def expectedBetas(playerID, opposingTeam):
    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + str(playerID) + '.json', )
    shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    roster = open('/Users/christianholmes/NBA/players/2014/Rosters/' + opposingTeam + '.json', )
    roster = json.load(roster)

    defense = pd.read_json('/Users/christianholmes/NBA/players/2014/Defense/' + str(roster[0][0]) + '.json' , 'r')
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

    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + str(player) + '.json', )

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
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Games/' + team):
        if not i.startswith('.') and not i.endswith('rebound.json') and not i.endswith('gamelog.json'):
            with open('/Users/christianholmes/NBA/players/2014/Games/' + team + '/' + i) as data_file:
                data = json.load(data_file)
                totalShots.append(data)
    shots = 0

    for i in totalShots:
        shots += len(i)

    #Total number of shots that a team takes on average
    avgTeamShots = float(shots)/float(len(totalShots))
    return avgTeamShots


def teamFinder(player):
    #First find out which team he plays for by going through the rosters
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Rosters/'):
        if not i.startswith('.'):
            with open('/Users/christianholmes/NBA/players/2014/Rosters/' + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        team = roster[9]
                        id = roster[0]
                        break


def expectedShotsTaken(player,opponent):

    #First find out which team he plays for by going through the rosters
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Rosters/'):
        if not i.startswith('.'):
            with open('/Users/christianholmes/NBA/players/2014/Rosters/' + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        team = roster[9]
                        id = roster[0]
                        break

    #How many total shots the team he plays for takes on average
    totalShots = expectedTeamShots(team)

    shots = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + str(player) + '.json')
    shots.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    oldRows = float(len(shots.index))
    shots = shots.groupby('GAME_ID').median()
    rows = float(len(shots.index))
    avgPlayerShots = float(oldRows/rows)

    #Percentage of total shots that a player takes
    pctPlayerShots = avgPlayerShots/totalShots

    #Defense's effect on shots
    totalOpponentShots = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalOpponentShots += data[0][8]

    totalOpponentShots = totalOpponentShots/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
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
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        fouls = []
        for game in dataFile:
            fouls.append(game[17])
        avgPlayerFTs = float(sum(fouls))/float(len(fouls))

    totalFTs = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalFTs += data[0][16]

    avgFouls = totalFTs/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamFTs = data[0][16]

    #Percent that defense lowers total shots
    defenseFoulPercentDifference =  (opponentTeamFTs - avgFouls) / opponentTeamFTs

    #Expected number of shots that a player will take against a given opponent
    avgPlayerFTs = avgPlayerFTs + (avgPlayerFTs * defenseFoulPercentDifference)

    return avgPlayerFTs

def expectedFouls(player,opponent):
    #Find the number of fouls he draws per game
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        fouls = []
        madeShots = []
        for game in dataFile:
            fouls.append(game[17])
            madeShots.append(game[16])
        avgPlayerFTs = float(sum(fouls))/float(len(fouls))
        fgPCT = float(sum(madeShots)/float(sum(fouls)))

    totalFTs = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalFTs += data[0][14]

    avgFouls = totalFTs/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
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

    with open('/Users/christianholmes/NBA/players/2014/Shots/' + str(player) + '.json') as data_file:
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
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        blocks = []
        for game in dataFile:
            blocks.append(game[24])
        avgPlayerBlocks = float(sum(blocks))/float(len(blocks))

    totalBlocks = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalBlocks += data[0][22]

    avgBlocks = totalBlocks/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamBlocks = data[0][22]

    #Percent that defense lowers total shots
    defenseBlockPercentDifference =  (opponentTeamBlocks - avgBlocks) / opponentTeamBlocks

    #Expected number of shots that a player will take against a given opponent
    avgPlayerBlocks = avgPlayerBlocks + (avgPlayerBlocks * defenseBlockPercentDifference)

    return avgPlayerBlocks


def expectedSteals(player,opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        steals = []
        for game in dataFile:
            steals.append(game[23])
        avgPlayerSteals = float(sum(steals))/float(len(steals))

    totalSteals = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalSteals += data[0][21]

    avgSteals = totalSteals/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamSteals = data[0][21]

    #Percent that defense lowers total shots
    defenseStealPercentDifference =  (opponentTeamSteals - avgSteals) / opponentTeamSteals

    #Expected number of shots that a player will take against a given opponent
    avgPlayerSteals = avgPlayerSteals + (avgPlayerSteals * defenseStealPercentDifference)

    return avgPlayerSteals

def expectedAssists1(player,opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        assists = []
        for game in dataFile:
            assists.append(game[22])
        avgPlayerAssists = float(sum(assists))/float(len(assists))

    totalAssists = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalAssists += data[0][19]

    avgAssists = totalAssists/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamAssists = data[0][19]

    #Percent that defense lowers total shots
    defenseAssistPercentDifference =  (opponentTeamAssists - avgAssists) / opponentTeamAssists

    #Expected number of shots that a player will take against a given opponent
    avgPlayerAssists = avgPlayerAssists + (avgPlayerAssists * defenseAssistPercentDifference)

    return avgPlayerAssists

def expectedTurnovers(player, opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        turnovers = []
        for game in dataFile:
            turnovers.append(game[25])
        avgPlayerTurnovers = float(sum(turnovers))/float(len(turnovers))

    totalTurnovers = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalTurnovers += data[0][20]

    avgTurnovers = totalTurnovers/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamTurnovers = data[0][20]

    #Percent that defense lowers total shots
    defenseTurnoverPercentDifference =  (opponentTeamTurnovers - avgTurnovers) / opponentTeamTurnovers

    #Expected number of shots that a player will take against a given opponent
    avgPlayerTurnovers = avgPlayerTurnovers + (avgPlayerTurnovers * defenseTurnoverPercentDifference)

    return avgPlayerTurnovers


def expectedRebounds(player, opponent):
    #Find the number of blocks he averages per game
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        rebounds = []
        for game in dataFile:
            rebounds.append(game[21])
        avgPlayerRebounds = float(sum(rebounds))/float(len(rebounds))

    totalRebounds = 0
    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalRebounds += data[0][18]

    avgRebounds = totalRebounds/30

    with open('/Users/christianholmes/NBA/players/2014/Teams/' + opponent + '_opponent.json') as data_file:
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

print DKPoints(708, 'PHI')

