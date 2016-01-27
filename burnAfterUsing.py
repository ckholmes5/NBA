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
now = datetime.datetime.now()
months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'DEC': 12, 'NOV':11, 'OCT':10}

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

slap = datetime.datetime(2015,12,31)


print expectedShotPercentage(977, 'BOS', slap)