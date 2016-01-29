from lxml import html
import requests
import operator
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

def teamFinder(player):
    for i in os.listdir(cs.rosterDir):
        if not i.startswith('.'):
            with open(cs.rosterDir + i) as data_file:
                data = json.load(data_file)

                for roster in data:
                    if roster[0] == player:
                        team = roster[9]
                        id = roster[0]
                        return team

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

    avgTeamDefenderDistance = sum(teamDefenderDistance)/len(teamDefenderDistance)
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
    pd_shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    lm = smf.ols(formula='FGM ~ CLOSE_DEF_DIST + SHOT_DIST + SHOT_CLOCK', data=pd_shot_data).fit()

    intercept = lm.params[0]
    defenderDistance = lm.params[1]
    shotDistance = lm.params[2]
    shotClock = lm.params[3]

    teamDiff = expectedBetas(player,team, new_date)

    #Shooting Percent against specific team
    spefTeam = intercept + shotClock*(teamDiff[0] + teamDiff[3]*teamDiff[0]) + shotDistance*(teamDiff[1] + teamDiff[4]*teamDiff[1]) + defenderDistance*(teamDiff[2] + teamDiff[5]*teamDiff[2])

    return spefTeam
def expectedShotsTaken(player,opponent, new_date = now):

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
    shots.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

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
        avgPlayerFTs = float(sum(fouls))/float(len(fouls))
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

        twoPercent = float(twos)/float(len(shot_data))
        threePercent = 1.0 - twoPercent


    points = (shotPCT*expectedShots*twoPercent*2) + (shotPCT*expectedShots*threePercent*3) + fouls
    threePointers = shotPCT*expectedShots*threePercent

    return [points, threePointers]



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


def expectedBlocks(player,opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        blocks = []
        for game in dataFile:
            blocks.append(game[24])
        avgPlayerBlocks = float(sum(blocks))/float(len(blocks))

    totalBlocks = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalBlocks += data[0][22]

    avgBlocks = totalBlocks/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamBlocks = data[0][22]

    #Percent that defense lowers total shots
    defenseBlockPercentDifference =  (opponentTeamBlocks - avgBlocks) / opponentTeamBlocks

    #Expected number of shots that a player will take against a given opponent
    avgPlayerBlocks = avgPlayerBlocks + (avgPlayerBlocks * defenseBlockPercentDifference)

    return avgPlayerBlocks


def expectedSteals(player,opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        steals = []
        for game in dataFile:
            steals.append(game[23])
        avgPlayerSteals = float(sum(steals))/float(len(steals))

    totalSteals = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalSteals += data[0][21]

    avgSteals = totalSteals/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamSteals = data[0][21]

    #Percent that defense lowers total shots
    defenseStealPercentDifference =  (opponentTeamSteals - avgSteals) / opponentTeamSteals

    #Expected number of shots that a player will take against a given opponent
    avgPlayerSteals = avgPlayerSteals + (avgPlayerSteals * defenseStealPercentDifference)

    return avgPlayerSteals






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


def expectedBlocks(player,opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        blocks = []
        for game in dataFile:
            blocks.append(game[24])
        avgPlayerBlocks = float(sum(blocks))/float(len(blocks))

    totalBlocks = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalBlocks += data[0][22]

    avgBlocks = totalBlocks/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamBlocks = data[0][22]

    #Percent that defense lowers total shots
    defenseBlockPercentDifference =  (opponentTeamBlocks - avgBlocks) / opponentTeamBlocks

    #Expected number of shots that a player will take against a given opponent
    avgPlayerBlocks = avgPlayerBlocks + (avgPlayerBlocks * defenseBlockPercentDifference)

    return avgPlayerBlocks


def expectedSteals(player,opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        steals = []
        for game in dataFile:
            steals.append(game[23])
        avgPlayerSteals = float(sum(steals))/float(len(steals))

    totalSteals = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalSteals += data[0][21]

    avgSteals = totalSteals/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamSteals = data[0][21]

    #Percent that defense lowers total shots
    defenseStealPercentDifference =  (opponentTeamSteals - avgSteals) / opponentTeamSteals

    #Expected number of shots that a player will take against a given opponent
    avgPlayerSteals = avgPlayerSteals + (avgPlayerSteals * defenseStealPercentDifference)

    return avgPlayerSteals

def expectedAssists1(player,opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        assists = []
        for game in dataFile:
            assists.append(game[22])
        avgPlayerAssists = float(sum(assists))/float(len(assists))

    totalAssists = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalAssists += data[0][19]

    avgAssists = totalAssists/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamAssists = data[0][19]

    #Percent that defense lowers total shots
    defenseAssistPercentDifference =  (opponentTeamAssists - avgAssists) / opponentTeamAssists

    #Expected number of shots that a player will take against a given opponent
    avgPlayerAssists = avgPlayerAssists + (avgPlayerAssists * defenseAssistPercentDifference)

    return avgPlayerAssists

def expectedTurnovers(player, opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        turnovers = []
        for game in dataFile:
            turnovers.append(game[25])
        avgPlayerTurnovers = float(sum(turnovers))/float(len(turnovers))

    totalTurnovers = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalTurnovers += data[0][20]

    avgTurnovers = totalTurnovers/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamTurnovers = data[0][20]

    #Percent that defense lowers total shots
    defenseTurnoverPercentDifference =  (opponentTeamTurnovers - avgTurnovers) / opponentTeamTurnovers

    #Expected number of shots that a player will take against a given opponent
    avgPlayerTurnovers = avgPlayerTurnovers + (avgPlayerTurnovers * defenseTurnoverPercentDifference)

    return avgPlayerTurnovers


def expectedRebounds(player, opponent):
    #Find the number of blocks he averages per game
    with open(cs.gamelogDir + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        rebounds = []
        for game in dataFile:
            rebounds.append(game[21])
        avgPlayerRebounds = float(sum(rebounds))/float(len(rebounds))

    totalRebounds = 0
    for i in os.listdir(cs.teamDir):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open (cs.teamDir + i) as data_file:
                data = json.load(data_file)
                totalRebounds += data[0][18]

    avgRebounds = totalRebounds/30

    with open(cs.teamDir + opponent + '_opponent.json') as data_file:
        data = json.load(data_file)
        opponentTeamRebounds = data[0][18]

    #Percent that defense lowers total shots
    defenseReboundPercentDifference =  (opponentTeamRebounds - avgRebounds) / opponentTeamRebounds

    #Expected number of shots that a player will take against a given opponent
    avgPlayerRebounds = avgPlayerRebounds + (avgPlayerRebounds * defenseReboundPercentDifference)

    return avgPlayerRebounds



slap = datetime.datetime(2015,12,31)

print expectedBlocks(977, 'DAL')
print expectedAssists1(977, 'DAL')