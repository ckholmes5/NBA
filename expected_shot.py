import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf





#The point of this file is to find the expected number of points a certain player will score in a given game. If you have the expected points that each player will score, you can predict winners, losers, and scores of each game.

#The first step to accomplish this we're going to use Benjamin Morris's formula of glm(made ~ SHOT_CLOCK + SHOT_DIST + CLOSE_DEF_DIST,family=binomial,data=filter(shots,!is.na(SHOT_CLOCK)))
#In english, he is predicting if a shot will be made depending on three variables: amount of time left on shot clock, the distance the shot is taken from, and the distance of the closest defender.
#To fill in this formula, we'll need to predict all three of those variables.




#1. Regress all the data we have using Morris's equation. Determine the likelihood of making a shot having those parameters
#2. Determine the expected of number of shots a player will take in a game. TODO: how to determine the expected number of shots?
#3.




#Regression for the likelihood of making a shot:

shot_data = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/708.json', )
shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]


def expectedBetas(opposingTeam):
    roster = open('/Users/christianholmes/NBA/players/2014/Rosters/' + opposingTeam + '.json', )
    roster = json.load(roster)

    defense = pd.read_json('/Users/christianholmes/NBA/players/2014/Defense/' + str(roster[0][0]) + '.json' , 'r')
    defense.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]

    for player in roster[1:]:
        #TODO: DELETE THE IF STATEMENT AFTER YOU"RE DONE TESTING IT
        if player[0] < 1000000:

            defense1 = pd.read_json('/Users/christianholmes/NBA/players/2014/Defense/' + str(player[0]) + '.json' , 'r')
            defense1.columns = ["GAME_ID", "MATCHUP", "LOCATION", "W", "FINAL_MARGIN", "SHOT_NUMBER", "PERIOD", "GAME_CLOCK", "SHOT_CLOCK", "DRIBBLES", "TOUCH_TIME", "SHOT_DIST", "PTS_TYPE", "SHOT_RESULT", "CLOSEST_DEFENDER", "CLOSEST_DEFENDER_PLAYER_ID", "CLOSE_DEF_DIST", "FGM", "PTS"]
            defense.append(defense1)

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

    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + player + '.json', )

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

    teamDiff = expectedBetas(team)

    leagueShotClock = 12.4624577172
    leagueDefenderDistance = 4.13361607305
    leagueShotDistance = 13.6198586128

    #Shooting Percent against average team
    avgTeam = intercept + shotClock*leagueShotClock + shotDistance*leagueShotDistance + defenderDistance*leagueDefenderDistance

    #Shooting Percent against specific team
    spefTeam = intercept + shotClock*teamDiff[0] + shotDistance*teamDiff[1] + defenderDistance*teamDiff[2]

    #return [teamDiffShotClock, teamDiffShotDistance, teamDiffDefenderDistance]

    actualTeam = intercept + shotClock*avgShotClock + shotDistance*avgShotDistance + defenderDistance*avgDefenderDistance

    return spefTeam


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









print expectedShotsTaken(708, 'CHI')





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


def expectedPoints(player,opposingTeam):

    shot_data = pd.read_json('/Users/christianholmes/NBA/players/2014/Shots/' + player + '.json', )
    shot_data.columns = ["GAME_ID","MATCHUP","LOCATION","W","FINAL_MARGIN","SHOT_NUMBER","PERIOD","GAME_CLOCK","SHOT_CLOCK","DRIBBLES","TOUCH_TIME","SHOT_DIST","PTS_TYPE","SHOT_RESULT","CLOSEST_DEFENDER","CLOSEST_DEFENDER_PLAYER_ID","CLOSE_DEF_DIST","FGM","PTS"]






'''
Intercept         0.361120
CLOSE_DEF_DIST    0.049962
SHOT_DIST        -0.011816
SHOT_CLOCK        0.004599
'''

leagueShotClock = 12.4624577172
leagueDefenderDistance = 13.6198586128
leagueShotDistance = 4.13361607305

#Find league averages of closest defender. (Should I do by shooting guard/center?). Then pop the averages into that formula. Then find the average distance of the closest defender in the team you're playing against.
#Pop that number into the equation. Figure out the difference between the two. Then you know the expected difference in points per shot.
#After that you need to find the expected number of shots he'll take in a game. Find the percentage of the total shots that he takes per game. Then find the average number of shots that the opposing team allows per year, vs the league average.
#Then you can figure out the percent difference in total shots and the number of shots you expect this player's team to take. Then find the expected number of shots he'll take. Finally, multiply that number by the points per shot equation above. Then you know the number of shots he'll take per game!


#Sean's idea:


#To Do:
#Find the league averages for the closest defender, for the shot distribution, and for the shot clock.
#