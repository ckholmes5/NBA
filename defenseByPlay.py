import os
import json
import datetime
import constants as cs

months = cs.months


def get_date_shots(date):
    month = str(date[0:3])
    day = str(date[4:6])
    year = int(date[8:12])
    return datetime.date(year, months[month], months[day])

for i in os.listdir(cs.shotDir):
    if not i.startswith('.'):
        with open(cs.shotDir + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:
                with open(cs.defenseDir + str(shot[15]) + '.json', 'a') as outfile:
                    json.dump(shot, outfile)

'''
#Uncomment this code if you wish to sort defense by the team a given player was playing defense against
                if shot[1][19] == 'v':
                    if not os.path.exists(cs.defenseDir + shot[1][23:26]):
                        os.makedirs(cs.defenseDir + shot[1][23:26])
                elif shot[1][19] == '@':
                    if not os.path.exists(cs.defenseDir + shot[1][21:24]):
                        os.makedirs(cs.defenseDir + shot[1][21:24])
'''
