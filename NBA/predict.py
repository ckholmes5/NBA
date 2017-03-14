import pandas as pd
import requests

todays_url = 11435
rename_dict = {'kelly_oubre_jr.' : 'kelly_oubre', 'r.j._hunter': 'rj_hunter', 'chris_johnson': 'christapher_johnson', 'raul_neto': 'raulzinho_neto', 'patty_mills': 'patrick_mills', "amar'e_stoudemire": 'amare_stoudemire', 'manu_ginobili': 'emanuel_ginobili','nene_hilario': 'nene', 'danny_green': 'daniel_green','t.j._mcconnell': 'tj_mcconnell', 'c.j._watson': 'cj_watson', 'k.j._mcdaniels': 'kj_mcdaniels', 'c.j._wilcox': 'cj_wilcox', 'd.j._augustin': 'dj_augustin', 'luc_richard_mbah_a_moute': 'luc_mbah_a_moute', 'marcus_thornton': 'marcus_t_thornton','j.j._redick': 'jj_redick', 'j.j._hickson': 'jj_hickson', 'p.j._hairston': 'pj_hairston', 'mo_williams': 'maurice_williams', 't.j._warren': 'tj_warren', 'tristan_thompson': 'tristan_t_thompson', 'p.j._tucker': 'pj_tucker', 'c.j._miles': 'cj_miles', 'j.r._smith': "jr_smith", 'ryan_anderson': 'ryan_j_anderson', 'c.j._mccollum': 'cj_mccollum', 'j.j._barea': 'jose_barea', 'lou_williams': 'louis_williams', "d'angelo_russell": 'dangelo_russell', 'larry_nance_jr.': 'larry_nance', 'o.j._mayo': 'oj_mayo', "kyle_o'quinn": 'kyle_oquinn', "e'twaun_moore" : 'etwaun_moore', 'louis_amundson': 'lou_amundson', "tim_hardaway_jr.": 'timothy_hardaway', "johnny_o'bryant": 'johnny_obryant'}

#Calculate total points, couldn't figure out how to do double or triple doubles
df = pd.read_csv('/Users/cholmes/Desktop/NBA/New Stuff/gamelog_opponent_merge.csv')
df['dk_points'] = df['PTS'] + df['FG3M']*.5 + df['REB']*1.25 + df['AST']*1.5 + df['STL']*2 + df['BLK']*2 + df['TOV']*-.5

#Pulling in players who are playing today from DraftKings
def get_players_DK(dk_url_num):
    DK_player_response = requests.get('https://www.draftkings.com/lineup/getavailableplayers?draftGroupId=' + str(dk_url_num))
    DK_player_response.raise_for_status()
    dk_players = DK_player_response.json()['playerList']

    names = []

    for player in dk_players:
        if player['IsDisabledFromDrafting'] != True:
            names.append(player['fn'] + ' ' + player['ln'])

    return names


#Limit Dataframe to only players who are playing today
current_players = get_players_DK(todays_url)
for name in current_players:
    print df[df['Player_Name'] == name]

#For each player, train a regression model using the defense statistics


#Get the stats for who they're playing against


#Using the coefficents you calculated, use the defensive stats to predict their total score


