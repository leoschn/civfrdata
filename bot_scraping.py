import os

import discord
import datetime
import pandas as pd
from unidecode import unidecode
import sqlite3
import re
import shutil
import os
import sqlite3

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-1]
base_path =  "/".join(script_directory) + "/"


def extract_from_string_raw(s, format,verbose=False):
    data = {}
    pattern_role = r'\<@&(.*?)\>'
    pattern_user = r'\<@(.*?)\>'
    pattern_number=r'\d+'
    splited_s = unidecode(s).lower()
    splited_s = splited_s.split('\n')
    splited_s = [i for i in splited_s if i != '']

    dec = 0
    if format=='cpl':
        if re.findall(pattern_number, splited_s[0]):
            data['Division'] = 'cpl_' + re.findall(pattern_number,splited_s[0])[0]
            dec +=1




    #check if message is a report and extract winner
    if not 'vs' in splited_s[0+dec].replace('team',''):
        dec += 1

    #ban sur 2 lignes
    if '/' in splited_s[4+dec].strip() and '/' in splited_s[5+dec].strip() :
        splited_s = splited_s[:4]+[splited_s[4]+splited_s[5]]+splited_s[6:]

    #extract team and winner
    if 'vs' in splited_s[0+dec]:

        try :
            data['Team A'] = re.findall(pattern_role, splited_s[0+dec].split('vs')[0])[0]
        except:
            data['Team A']  = 'UNKNOWN'


        try :
            data['Team B'] = re.findall(pattern_role, splited_s[0+dec].split('vs')[1])[0]
        except:
            data['Team B'] = 'UNKNOWN'

        #extract winner
        try :
            data['Winner'] = re.findall(pattern_role, splited_s[1+dec])[0]
        except:
            data['Winner'] ='UNKNOWN'

        # extract victory type
        if ' cc ' in  splited_s[1 + dec].strip():
            data['Victory']= 'CC'
        elif 'diplo' in  splited_s[1 + dec].strip():
            data['Victory'] = 'Diplomatic'
        elif 'scien' in  splited_s[1 + dec].strip():
            data['Victory'] = 'Scientific'
        elif 'cultur' in  splited_s[1 + dec].strip():
            data['Victory'] = 'Cultural'
        elif 'milita' in  splited_s[1 + dec].strip():
            data['Victory'] = 'Military'
        elif 'religi' in  splited_s[1 + dec].strip():
            data['Victory'] = 'Religious'
        else :
            data['Victory'] = 'UNKNOWN'

        # extract victory turn
        try :

            data['Victory Turn'] = int(re.findall(r'\d+', splited_s[1 + dec])[-1])
            if data['Victory Turn'] > 200 :
                data['Victory Turn'] = 'UNKNOWN'
        except :
            data['Victory Turn']  = 'UNKNOWN'




        data['Map played'] = splited_s[2 + dec].strip()

        #extract map
        data['Map played']=splited_s[2+dec].strip()

        #extract map bans
        if 'map bans' in splited_s[3+dec]:

            line = splited_s[3+dec].split(':')
            bans = line[1].split('/')
            for i in range(6) :
                try :
                    data['Map ban{0}'.format(i+1)]=bans[i].strip()
                except :
                    data['Map ban{0}'.format(i+1)]=0
        else :
            dec-=1

        #extract leader bans
        if 'leader' in splited_s[4+dec]:

            line = splited_s[4+dec].split(':')
            bans = line[1].split('/')
            for i in range(16) :
                try :
                    data['Ban{0}'.format(i+1)]=bans[i].strip()
                except :
                    data['Ban{0}'.format(i+1)]=0


            #extract leaders picks
        for i in range(4):
            try :
                data['PickA{0}'.format(i+1)]=' '.join(splited_s[6+i+dec].split('>')[1:]).strip().split('<')[0].strip()
            except:
                data['PickA{0}'.format(i+1)] = 'UNKNOWN'
            try:
                data['PickB{0}'.format(i+1)] = ' '.join(splited_s[11+i+dec].split('>')[1:]).strip().split('<')[0].strip()
            except:
                data['PickB{0}'.format(i+1)] = 'UNKNOWN'

            #extract player
        for i in range(4):
            try :
                data['PlayerA{0}'.format(i+1)]=re.findall(pattern_user, splited_s[6+i+dec])[0]
            except:
                data['PlayerA{0}'.format(i+1)] = 'UNKNOWN'
            try:
                data['PlayerB{0}'.format(i+1)] =re.findall(pattern_user, splited_s[11+i+dec])[0]
            except:
                data['PlayerB{0}'.format(i+1)] = 'UNKNOWN'

    else:
        if verbose:
            print('Matching failed')
            print(s)
        raise 'Matching failed'
    return data

def extract_from_serie_raw(s, format,verbose=False):
    l=[]
    for row in s.iterrows():
        try :
            data = extract_from_string_raw(row[1]['message'],format, verbose)
            data['Date'] = row[1]['date'].strftime("%d/%m/%y")
        except :

            pass
        else:
            l.append(data.copy())
    return pd.DataFrame(l)

# enabling intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
civfr_id = 'Civfr.com'
cpl_name = 'CivPlayers Leagues'


@client.event
async def on_ready():
    #
    #
    for guild in client.guilds:
        if guild.name == civfr_id:

            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}\n'
            )
            # Building user database
            player_id_map_civfr= {}
            for member in guild.members:
                id = member.id
                name = member.display_name
                role_list = member.roles
                role_list = [role.id for role in role_list]
                player_id_map_civfr[id]={}
                player_id_map_civfr[id]["name"] = name
                player_id_map_civfr[id]["role_list"] = role_list

        #Building role database (team)
            role_id_map_civfr = {}
            for role in guild.roles:
                id = role.id
                name = role.name
                role_id_map_civfr[id]=name

            c_channel = discord.utils.get(guild.text_channels, name='s16-reporting-d1')
            messages = [{'message':message.content,'date' : message.created_at} async for message in c_channel.history(after=datetime.datetime(2025,8,28,8,30),limit=1000)]
            df1 = pd.DataFrame(messages)
            df1 = extract_from_serie_raw(df1,format='civfr')
            df1['Division'] = '1'

            c_channel = discord.utils.get(guild.text_channels, name='s16-reporting-d2')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,8,28,8,30),limit=1000)]
            df2 = pd.DataFrame(messages)
            df2 = extract_from_serie_raw(df2,format='civfr')
            df2['Division'] = '2'

            c_channel = discord.utils.get(guild.text_channels, name='s16-reporting-d3')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,8,28,8,30),limit=1000)]
            df3= pd.DataFrame(messages)
            df3 = extract_from_serie_raw(df3,format='civfr')
            df3['Division'] = '3'

        if guild.name == cpl_name:

            player_id_map_cpl= {}
            for member in guild.members:
                id = member.id
                name = member.display_name
                role_list = member.roles
                role_list = [role.id for role in role_list]
                player_id_map_cpl[id]={}
                player_id_map_cpl[id]["name"] = name
                player_id_map_cpl[id]["role_list"] = role_list

            # Building role database (team)
            role_id_map_cpl = {}
            for role in guild.roles:
                id = role.id
                name = role.name
                role_id_map_cpl[id] = name

            print('scraping cpl')
            c_channel = discord.utils.get(guild.text_channels, name='pl-game-reports')
            messages = [{'message': message.content, 'date': message.created_at}  async for message in
                        c_channel.history(after=datetime.datetime(2025, 8, 20, 8, 30), limit=1000)]
            dfcpl = pd.DataFrame(messages)
            dfcpl.to_csv('temp_cpl.csv')
            dfcpl = extract_from_serie_raw(dfcpl,format='cpl')


    df = pd.concat([df1, df2, df3], axis=0)
    df['league'] = 'civfr'
    df['Season'] = 16
    df.to_csv(base_path + 'data_S16.csv', index=False)

    dfcpl['Season'] = 5
    dfcpl['league'] = 'cpl'
    dfcpl.to_csv(base_path + 'data_CPL5.csv', index=False)

    print('report scrapped')

    shutil.copyfile(base_path + 'database_s15_legacy.db', base_path + 'database_complete.db')
    conn = sqlite3.connect(base_path + 'database_complete.db')

    conn_s16 = sqlite3.connect(base_path + 'database_s16.db')
    data = pd.read_csv(base_path + 'data_S16.csv')
    nb_game_s16 = data.shape[1]
    data.index+=306 #number of s15 games
    data['id']=data.index

    data_cpl = pd.read_csv(base_path + 'data_CPL5.csv')
    conn_cpl = sqlite3.connect(base_path + 'database_CPL5.db')
    data_cpl.index += 306 + 1500  #au cas ou bcp de games CPL (temporary fix)
    data_cpl['id']=data_cpl.index

    # Dictionnaire pour stocker les games uniques.
    # Clé : id du joueur.
    # Valeur : dictionnaire contenant :
    #   - "TeamA/TeamB"             : ID de l'équipe
    #   - "Winner"                  : ID de l'équipe ga gnante
    #   - "PlayerAX/playerBX"       : ID du joueur
    #   - "Season": numero de la saison

    cursor_s16 = conn_s16.cursor()
    cursor_cpl = conn_cpl.cursor()
    cursor_s16.execute("DROP TABLE IF EXISTS games")
    cursor_cpl.execute("DROP TABLE IF EXISTS games")
    data.to_sql('games', conn_s16,dtype={'Team A':'INTEGER','Team B':'INTEGER','Winner':'INTEGER','PlayerA1':'INTEGER'
                                     ,'PlayerA2':'INTEGER','PlayerA3':'INTEGER','PlayerA4':'INTEGER','PlayerB1':'INTEGER'
                                     ,'PlayerB2':'INTEGER','PlayerB3':'INTEGER','PlayerB4':'INTEGER'})
    data_cpl.to_sql('games', conn_cpl,
                dtype={'Team A': 'INTEGER', 'Team B': 'INTEGER', 'Winner': 'INTEGER', 'PlayerA1': 'INTEGER'
                    , 'PlayerA2': 'INTEGER', 'PlayerA3': 'INTEGER', 'PlayerA4': 'INTEGER', 'PlayerB1': 'INTEGER'
                    , 'PlayerB2': 'INTEGER', 'PlayerB3': 'INTEGER', 'PlayerB4': 'INTEGER'})
    conn_s16.commit()
    conn_cpl.commit()


    conn_s16.row_factory = sqlite3.Row  # Pour accéder aux colonnes par leur nom
    conn_cpl.row_factory = sqlite3.Row
    cursor_s16 = conn_s16.cursor()
    cursor_cpl = conn_cpl.cursor()
    cursor = conn.cursor()

    cursor.execute("ALTER TABLE games ADD Ban15 TINYTEXT")
    cursor.execute("ALTER TABLE games ADD Ban16 TINYTEXT")
    cursor.execute("ALTER TABLE games ADD league TEXT DEFAULT 'civfr'")
    cursor.execute("ALTER TABLE teams ADD league TEXT DEFAULT 'civfr'")
    cursor.execute("ALTER TABLE players ADD team_cpl INTEGER DEFAULT NULL")
    cursor.execute("ALTER TABLE players RENAME COLUMN team TO team_civfr")

    # Récupération de toutes les lignes de la table "games"
    cursor_s16.execute("SELECT * FROM games")
    games_data = cursor_s16.fetchall()
    cursor_cpl.execute("SELECT * FROM games")
    games_cpl_data  = cursor_cpl.fetchall()
    # Dictionnaire pour stocker les joueurs uniques.
    # Clé : id du joueur.
    # Valeur : dictionnaire contenant :
    #   - "teams"       : dictionnaire avec comme clé l'ID de l'équipe et comme valeur le nombre de matchs joués pour cette équipe.
    #   - "games"       : ensemble des IDs des matchs où il apparaît.
    #   - "pseudo"      : player pseudo
    #   - "current_team": current player team based on its discord role
    players_dict = {}

    # Dictionnaire pour stocker les équipes.
    # Clé : nom de l'équipe.
    # Valeur : dictionnaire contenant :
    #   - "players" : ensemble des IDs appartenant à l'équipe.
    #   - "games"   : ensemble des IDs des matchs où l'équipe a joué.
    #   - "name"    : team name
    #   - "division": la division de l'équipe (prise lors de la première occurrence).
    teams_dict = {}
    teams_dict_legacy = {}
    row_name_player_A = ['PlayerA1', 'PlayerA2', 'PlayerA3', 'PlayerA4']
    row_name_player_B = ['PlayerB1', 'PlayerB2', 'PlayerB3', 'PlayerB4']
    for row in games_data:
        cursor.execute(
            "INSERT INTO games ('Team A','Team B',Winner,Victory,'Victory Turn','Map played','Map ban1','Map ban2','Map ban3','Map ban4','Map ban5','Map ban6',Ban1,Ban2,Ban3,Ban4,Ban5,Ban6,Ban7,Ban8,Ban9,Ban10,Ban11,Ban12,Ban13,Ban14,Ban15,Ban16,PickA1,PickB1,PickA2,PickB2,PickA3,PickB3,PickA4,PickB4,PlayerA1,PlayerB1,PlayerA2,PlayerB2,PlayerA3,PlayerB3,PlayerA4,PlayerB4,Date,Division,Season,id,League) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (row["Team A"], row["Team B"], row["Winner"], row["Victory"], row["Victory Turn"], row["Map played"],
             row["Map ban1"], row["Map ban2"],
             row["Map ban3"], row["Map ban4"], row["Map ban5"], row["Map ban6"], row["Ban1"], row["Ban2"], row["Ban3"],
             row["Ban4"],
             row["Ban5"], row["Ban6"], row["Ban7"], row["Ban8"], row["Ban9"], row["Ban10"], row["Ban11"], row["Ban12"],
             row["Ban13"], row["Ban14"], row["Ban15"], row["Ban16"], row["PickA1"], row["PickB1"], row["PickA2"],
             row["PickB2"],
             row["PickA3"], row["PickB3"], row["PickA4"], row["PickB4"], row["PlayerA1"], row["PlayerB1"],
             row["PlayerA2"],
             row["PlayerB2"], row["PlayerA3"], row["PlayerB3"], row["PlayerA4"], row["PlayerB4"], row["Date"],
             row["Division"], row["Season"], row['id'], row['League']))
        game_id = row["id"]
        division = row["Division"]
        teamA = row["Team A"]
        teamB = row["Team B"]

        # Mise à jour des informations pour Team A et Team B dans teams_dict
        if teamA != 'UNKNOWN':
            teamA = int(teamA)
            if teamA not in teams_dict:
                teams_dict[teamA] = {"players": set(), "games": set(), "division": division,"league":"civfr"}
            teams_dict[teamA]["games"].add(str(game_id))
            if teamA not in teams_dict_legacy:
                teams_dict_legacy[teamA] = {"players": set()}
            for row_name in row_name_player_A :
                teams_dict_legacy[teamA]["players"].add(row[row_name])
        if teamB != 'UNKNOWN':
            teamB = int(teamB)
            if teamB not in teams_dict:
                teams_dict[teamB] = {"players": set(), "games": set(), "division": division,"league":"civfr"}
            teams_dict[teamB]["games"].add(str(game_id))

            if teamB not in teams_dict_legacy:
                teams_dict_legacy[teamB] = {"players": set()}
            for row_name in row_name_player_B :
                teams_dict_legacy[teamB]["players"].add(row[row_name])

        # Pour les joueurs de l'équipe A (PlayerA1 à PlayerA4)
        for col in ["PlayerA1", "PlayerA2", "PlayerA3", "PlayerA4"]:
            try :
                id = int(row[col])
                if id not in players_dict:
                    players_dict[id] = {"teams_cpl": {},"teams_civfr": {}, "games": set(),'pseudo': player_id_map_civfr[id]['name']}
                players_dict[id]["games"].add(str(game_id))
                if teamA:
                    # Incrémente le compteur pour teamA
                    players_dict[id]["teams_civfr"][int(teamA)] = players_dict[id]["teams_civfr"].get(int(teamA), 0) + 1
            except :
                pass

        # Pour les joueurs de l'équipe B (PlayerB1 à PlayerB4)
        for col in ["PlayerB1", "PlayerB2", "PlayerB3", "PlayerB4"]:
            try :
                id = int(row[col])
                if id not in players_dict:
                    players_dict[id] = {"teams_cpl": {},"teams_civfr": {}, "games": set(),'pseudo': player_id_map_civfr[id]['name']}
                players_dict[id]["games"].add(str(game_id))
                if teamB:
                    # Incrémente le compteur pour teamB
                    players_dict[id]["teams_civfr"][int(teamB)] = players_dict[id]["teams_civfr"].get(int(teamB), 0) + 1
            except :
                pass

    for row in games_cpl_data:
        cursor.execute("INSERT INTO games ('Team A','Team B',Winner,Victory,'Victory Turn','Map played','Map ban1','Map ban2','Map ban3','Map ban4','Map ban5','Map ban6',Ban1,Ban2,Ban3,Ban4,Ban5,Ban6,Ban7,Ban8,Ban9,Ban10,Ban11,Ban12,Ban13,Ban14,Ban15,Ban16,PickA1,PickB1,PickA2,PickB2,PickA3,PickB3,PickA4,PickB4,PlayerA1,PlayerB1,PlayerA2,PlayerB2,PlayerA3,PlayerB3,PlayerA4,PlayerB4,Date,Division,Season,id,League) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (row["Team A"],row["Team B"],row["Winner"],row["Victory"],row["Victory Turn"],row["Map played"],row["Map ban1"],row["Map ban2"],
                                         row["Map ban3"],row["Map ban4"],row["Map ban5"],row["Map ban6"],row["Ban1"],row["Ban2"],row["Ban3"],row["Ban4"],
                                         row["Ban5"],row["Ban6"],row["Ban7"],row["Ban8"],row["Ban9"],row["Ban10"],row["Ban11"],row["Ban12"],
                                         row["Ban13"],row["Ban14"],row["Ban15"],row["Ban16"],row["PickA1"],row["PickB1"],row["PickA2"],row["PickB2"],
                                         row["PickA3"],row["PickB3"],row["PickA4"],row["PickB4"],row["PlayerA1"],row["PlayerB1"],row["PlayerA2"],
                                         row["PlayerB2"],row["PlayerA3"],row["PlayerB3"],row["PlayerA4"],row["PlayerB4"],row["Date"],row["Division"],row["Season"],row['id'],row['League']))
        game_id = row["id"]
        division = row["Division"]
        teamA = row["Team A"]
        teamB = row["Team B"]

        # Mise à jour des informations pour Team A et Team B dans teams_dict
        if teamA != 'UNKNOWN':
            teamA = int(teamA)
            if teamA not in teams_dict:
                teams_dict[teamA] = {"players": set(), "games": set(), "division": division,"league":"cpl"}
            teams_dict[teamA]["games"].add(str(game_id))
            if teamA not in teams_dict_legacy:
                teams_dict_legacy[teamA] = {"players": set()}
            for row_name in row_name_player_A :
                teams_dict_legacy[teamA]["players"].add(row[row_name])
        if teamB != 'UNKNOWN':
            teamB = int(teamB)
            if teamB not in teams_dict:
                teams_dict[teamB] = {"players": set(), "games": set(), "division": division,"league":"cpl"}
            teams_dict[teamB]["games"].add(str(game_id))

            if teamB not in teams_dict_legacy:
                teams_dict_legacy[teamB] = {"players": set()}
            for row_name in row_name_player_B :
                teams_dict_legacy[teamB]["players"].add(row[row_name])

        # Pour les joueurs de l'équipe A (PlayerA1 à PlayerA4)
        for col in ["PlayerA1", "PlayerA2", "PlayerA3", "PlayerA4"]:
            try :
                id = int(row[col])
                if id not in players_dict:
                    players_dict[id] = {"teams_cpl": {},"teams_civfr": {}, "games": set(),'pseudo': player_id_map_cpl[id]['name']}
                players_dict[id]["games"].add(str(game_id))
                if teamA:
                    # Incrémente le compteur pour teamA
                    players_dict[id]["teams_cpl"][int(teamA)] = players_dict[id]["teams_cpl"].get(int(teamA), 0) + 1
            except :
                pass

        # Pour les joueurs de l'équipe B (PlayerB1 à PlayerB4)
        for col in ["PlayerB1", "PlayerB2", "PlayerB3", "PlayerB4"]:
            try :
                id = int(row[col])
                if id not in players_dict:
                    players_dict[id] = {"teams_cpl": {},"teams_civfr": {}, "games": set(),'pseudo': player_id_map_cpl[id]['name']}
                players_dict[id]["games"].add(str(game_id))
                if teamB:
                    # Incrémente le compteur pour teamB
                    players_dict[id]["teams_cpl"][int(teamB)] = players_dict[id]["teams_cpl"].get(int(teamB), 0) + 1
            except :
                pass



    # Pour chaque joueur, déterminer son équipe actuelle
    for id, info in players_dict.items():
        info["current_team_cpl"] = 'NONE'

        for team_id in info['teams_cpl'].keys() :
            if team_id is not None and id in player_id_map_cpl and team_id in player_id_map_cpl[id]['role_list'] :
                info["current_team_cpl"] = team_id

        info["current_team_civfr"] = 'NONE'
        for team_id in info['teams_civfr'].keys() :
            if team_id is not None and id in player_id_map_civfr and team_id in player_id_map_civfr[id]['role_list']:
                info["current_team_civfr"] = team_id


    # Compléter teams_dict avec la liste des joueurs extraits
    for id, info in players_dict.items():
        team = info["current_team_cpl"]
        if team != 'NONE':
            if team not in teams_dict:
                teams_dict[team] = {"players": set(), "games": set(), "division": "","league":"cpl"}
            teams_dict[team]["players"].add(id)

        team = info["current_team_civfr"]
        if team != 'NONE':
            if team not in teams_dict:
                teams_dict[team] = {"players": set(), "games": set(), "division": "","league":"civfr"}
            teams_dict[team]["players"].add(id)

    # Suppression des tables existantes si elles existent déjà
    cursor_s16.execute("DROP TABLE IF EXISTS players")
    cursor_s16.execute("DROP TABLE IF EXISTS player_games")
    cursor_s16.execute("DROP TABLE IF EXISTS teams")
    cursor_s16.execute("DROP TABLE IF EXISTS team_players")
    cursor_s16.execute("DROP TABLE IF EXISTS team_games")
    cursor_s16.execute("DROP TABLE IF EXISTS team_players_legacy")


    # Création de la table players (pour les joueurs)
    cursor_s16.execute('''
            CREATE TABLE players (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
               team_civfr INTEGER NOT NULL,
               team_cpl INTEGER
            )
        ''')

    # Création de la table player_games (liaison joueur - match)
    cursor_s16.execute('''
            CREATE TABLE player_games (
                player_id INTEGER,
                game_id INTEGER,
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        ''')

    # Création de la table teams (pour les équipes)
    cursor_s16.execute('''
            CREATE TABLE teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT,
                division TEXT,
                league TEXT
            )
        ''')

    # Création de la table team_players (liaison équipe - joueur)
    cursor_s16.execute('''
            CREATE TABLE team_players (
                team_id INTEGER,
                player_id INTEGER,
                FOREIGN KEY(team_id) REFERENCES teams(team_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        ''')

    # Création de la table team_players_legacy (liaison équipe - joueur)
    cursor_s16.execute('''
            CREATE TABLE team_players_legacy (
                team_id INTEGER,
                player_id INTEGER,
                FOREIGN KEY(team_id) REFERENCES teams(team_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        ''')

    # Création de la table team_games (liaison équipe - match)
    cursor_s16.execute('''
            CREATE TABLE team_games (
                team_id INTEGER,
                game_id INTEGER,
                FOREIGN KEY(team_id) REFERENCES teams(team_id)
            )
        ''')

    # Suppression des tables existantes si elles existent déjà
    cursor_cpl.execute("DROP TABLE IF EXISTS players")
    cursor_cpl.execute("DROP TABLE IF EXISTS player_games")
    cursor_cpl.execute("DROP TABLE IF EXISTS teams")
    cursor_cpl.execute("DROP TABLE IF EXISTS team_players")
    cursor_cpl.execute("DROP TABLE IF EXISTS team_games")
    cursor_cpl.execute("DROP TABLE IF EXISTS team_players_legacy")

    # Création de la table players (pour les joueurs)
    cursor_cpl.execute('''
               CREATE TABLE players (
                   player_id INTEGER PRIMARY KEY,
                   player_name TEXT NOT NULL,
                   team_civfr INTEGER NOT NULL,
                   team_cpl INTEGER
               )
           ''')

    # Création de la table player_games (liaison joueur - match)
    cursor_cpl.execute('''
               CREATE TABLE player_games (
                   player_id INTEGER,
                   game_id INTEGER,
                   FOREIGN KEY(player_id) REFERENCES players(player_id)
               )
           ''')

    # Création de la table teams (pour les équipes)
    cursor_cpl.execute('''
               CREATE TABLE teams (
                   team_id INTEGER PRIMARY KEY,
                   team_name TEXT,
                   division TEXT,
                   league TEXT
               )
           ''')

    # Création de la table team_players (liaison équipe - joueur)
    cursor_cpl.execute('''
               CREATE TABLE team_players (
                   team_id INTEGER,
                   player_id INTEGER,
                   FOREIGN KEY(team_id) REFERENCES teams(team_id),
                   FOREIGN KEY(player_id) REFERENCES players(player_id)
               )
           ''')

    # Création de la table team_players_legacy (liaison équipe - joueur)
    cursor_cpl.execute('''
               CREATE TABLE team_players_legacy (
                   team_id INTEGER,
                   player_id INTEGER,
                   FOREIGN KEY(team_id) REFERENCES teams(team_id),
                   FOREIGN KEY(player_id) REFERENCES players(player_id)
               )
           ''')

    # Création de la table team_games (liaison équipe - match)
    cursor_cpl.execute('''
               CREATE TABLE team_games (
                   team_id INTEGER,
                   game_id INTEGER,
                   FOREIGN KEY(team_id) REFERENCES teams(team_id)
               )
           ''')


    # Insertion des joueurs dans la table players et création du mapping pseudo -> player_id
    player_id_dict = {}
    for id, info in players_dict.items():
        team_civfr = info["current_team_civfr"]
        team_cpl = info["current_team_cpl"]
        if team_civfr !='NONE' :
            player_name = player_id_map_civfr[id]['name']
            cursor_s16.execute("INSERT INTO players (player_id, player_name, team_civfr, team_cpl) VALUES (?,?, ?, ?)", (id,player_name, team_civfr,team_cpl))

        elif team_cpl !='NONE':
            player_name = player_id_map_cpl[id]['name']
            cursor_cpl.execute("INSERT INTO players (player_id, player_name, team_civfr, team_cpl) VALUES (?,?, ?, ?)", (id,player_name, team_civfr,team_cpl))
        cursor.execute("REPLACE INTO players (player_id, player_name, team_civfr, team_cpl) VALUES (?,?, ?, ?)", (id, player_name, team_civfr,team_cpl))


        #TODO isoler cpl civ fr
        for game_id in info["games"]:
            cursor.execute("INSERT INTO player_games (player_id, game_id) VALUES (?, ?)", (id, int(game_id)))
            cursor_s16.execute("INSERT INTO player_games (player_id, game_id) VALUES (?, ?)", (id, int(game_id)))


    # Insertion des équipes dans la table teams et dans les tables de liaison
    for team_id, info in teams_dict.items():
        if team_id!='UNKNOWN':
            division = info.get("division", "")

            for game_id in info["games"]:

                cursor.execute("INSERT INTO team_games (team_id, game_id) VALUES (?, ?)", (team_id, int(game_id)))
                cursor_s16.execute("INSERT INTO team_games (team_id, game_id) VALUES (?, ?)", (team_id, int(game_id)))
            for id in info["players"]:
                cursor.execute("INSERT INTO team_players (team_id, player_id) VALUES (?, ?)", (team_id, id))
                cursor_s16.execute("INSERT INTO team_players (team_id, player_id) VALUES (?, ?)", (team_id, id))

            if info['league']=='civfr':
                cursor.execute("REPLACE INTO teams (team_id, team_name, division, league) VALUES (?, ?, ?, ?)",
                               (team_id, role_id_map_civfr[team_id], division, info['league']))
                cursor_s16.execute("REPLACE INTO teams (team_id, team_name, division, league) VALUES (?, ?, ?, ?)",
                                   (team_id, role_id_map_civfr[team_id], division,info['league']))
            elif info['league']=='cpl':
                cursor.execute("REPLACE INTO teams (team_id, team_name, division, league) VALUES (?, ?, ?, ?)",
                               (team_id, role_id_map_cpl[team_id], division, info['league']))
                cursor_cpl.execute("REPLACE INTO teams (team_id, team_name, division, league) VALUES (?, ?, ?, ?)",
                                   (team_id, role_id_map_cpl[team_id], division,info['league']))

    for team_id, info in teams_dict_legacy.items():
        if team_id != 'UNKNOWN':
            team_id = int(team_id)
            for id in info["players"]:
                cursor.execute("INSERT INTO team_players_legacy (team_id, player_id) VALUES (?, ?)",
                           (team_id, id))
                cursor_s16.execute("INSERT INTO team_players_legacy (team_id, player_id) VALUES (?, ?)",
                               (team_id, id))

    conn.commit()
    conn_s16.commit()
    conn_cpl.commit()
    conn_cpl.close()
    conn_s16.close()
    conn.close()
    print(f"Nouvelles tables ajoutées dans database.db' : {len(players_dict)} joueurs et {len(teams_dict)} équipes.")



    await client.close()

path_token = base_path + "token.txt"
with open(path_token, 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)


