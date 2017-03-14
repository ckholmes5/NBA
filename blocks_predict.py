import json
import os
import pandas as pd


#Helper function from expected_shot
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

    shots = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + str(player) + '.json')
    shots.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    oldRows = float(len(shots.index))
    shots = shots.groupby('GAME_ID').median()
    rows = float(len(shots.index))
    avgPlayerShots = float(oldRows/rows)

    #Percentage of total shots that a player takes
    pctPlayerShots = avgPlayerShots/avgTeamShots

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
    playerShots = (avgTeamShots + (avgTeamShots * defenseShotPercentDifference)) * pctPlayerShots

    return playerShots


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

def expectedAssists2(player,opponent, startDate='0000-01-01', endDate='9000-01-01'):
    with open('/Users/christianholmes/NBA/players/2014/GameLogs/' + str(player) + '.json') as dataFile:
        dataFile = json.load(dataFile)
        assists = []
        for game in dataFile:
            if game[6] > startDate and game[6] <= endDate:
                assists.append(game[22])
        avgPlayerAssists = float(sum(assists))/float(len(assists))

    totalAssists = 0
    totalSuccessfulShots = 0

    for i in os.listdir('/Users/christianholmes/NBA/players/2014/Teams/'):
        if not i.startswith('.') and not i.endswith('_game.json'):
            with open ('/Users/christianholmes/NBA/players/2014/Teams/' + i) as data_file:
                data = json.load(data_file)
                totalAssists += data[0][19]
                totalSuccessfulShots += data[0][7]
    avgAssists = totalAssists/30

    avgSuccessfulShots = totalSuccessfulShots/30
    assistsPerShot = avgAssists/avgSuccessfulShots
    shots = expectedTeamShots(opponent)
    #avgPlayerAssists =

    return assistsPerShot * shots

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





#"SEASON_ID","PLAYER_ID","PLAYER_NAME","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE","MATCHUP","WL","MIN","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT","FTM" [16],"FTA" [17],"FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS","PLUS_MINUS","VIDEO_AVAILABLE"


#Assists
#Option 2
#1. Figure out the pct of shots that are from assists by team
#2. Figure out the total predicted assists per night based on the number of expected shots per night
#3. Figure out pct of assists the player has from his team
#4. Multiply those numbers together and return total predicted assists

#Option 1
#1. Do it with the the other method of team allowed vs league allowed

#Looks like we should run a test?

#So I'm going to have two different models. I'll use 80% of the data to model and 20% to predict. I'll start by using dates (take data from October to mid-February then predict the rest. There's probably a better way to do it rather than using dates, #TODO: ask sean if he can think of a better way.
#It would be nice if I could write both algorithms then put the limiting dates in the testing function, rather than hard code the dates into the other function.

#Once the dates are worked out, apply the function to the first four months.
#Cycle through the next two months for every player, taking in the team they're playing and return the expected  number of assists they'll have. Subtract actual from expected and take the absolute value. Sum all those results.
#Go back and apply the second function. Do the same thing as above, then compare the two results. Whichever has the lowest should be the best.


















print expectedBlocks(1891,'NYK')
print expectedSteals(1891, 'NYK')
print expectedAssists1(1891, 'NYK')
print expectedAssists2(1891, 'NYK','2014-09-01', '2014-11-30')
print expectedFouls(1891, 'NYK')
