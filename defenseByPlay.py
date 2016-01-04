import os
import json

for i in os.listdir('/Users/christianholmes/NBA/players/2014/Shots/'):
    if not i.startswith('.'):
        with open('/Users/christianholmes/NBA/players/2014/Shots/' + i , 'r') as data_file:
            data = json.load(data_file)
            for shot in data:

                with open('/Users/christianholmes/NBA/players/2014/Defense/' + str(shot[15]) + '.json', 'a') as outfile:
                    json.dump(shot, outfile)



                '''
                if shot[1][19] == 'v':
                    if not os.path.exists('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][23:26]):
                        os.makedirs('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][23:26])
                elif shot[1][19] == '@':
                    if not os.path.exists('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][21:24]):
                        os.makedirs('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][21:24])
                '''

            '''
                if not os.path.exists('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][15:18]):
                    os.makedirs('/Users/christianholmes/NBA/players/2014/Defense/' + shot[1][15:18])
                with open('/Users/christianholmes/NBA/players/2014/Games/' + shot[1][15:18] + '/' + str(get_date_shots(shot[1][0:12])) + '_rebound.json', 'a') as outfile:
                    json.dump(shot, outfile)

            '''
            '''
            if not os.path.exists('/Users/christianholmes/NBA/players/2014/Defense/' + str(shot[15])):
                    os.makedirs('/Users/christianholmes/NBA/players/2014/Defense/' + str(shot[15]))
            '''

#[u'0021401215', u'APR 14, 2015 - WAS @ IND', u'A', u'L', -4, 1, 1, u'11:11', 16.0, 0, 1.0, 22.5, 3, u'missed', u'Hill, George', 201588, 9.6, 0, 0]