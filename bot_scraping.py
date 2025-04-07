import os

import discord
import datetime
import pandas as pd
from sympy import limit
from unidecode import unidecode
import sqlite3
import re

import os
import sqlite3

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-1]
base_path =  "/".join(script_directory) + "/"


def add_new_tables_to_db(db_file):
    # Connexion à la base de données source (contenant la table "games")
    conn = sqlite3.connect(db_file)



def extract_from_string_raw(s, player_id_dict, role_id_dict, verbose=False):
    data = {}
    pattern_role = r'\<@&(.*?)\>'
    pattern_user = r'\<@(.*?)\>'
    splited_s = unidecode(s).lower()
    splited_s = splited_s.split('\n')
    splited_s = [i for i in splited_s if i != '']

    dec = 0

    #check if message is a report and extract winner
    if not 'vs' in splited_s[0].replace('team',''):
        dec = 1

    #ban sur 2 lignes
    if '/' in splited_s[4+dec].strip() and '/' in splited_s[5+dec].strip() :
        splited_s = splited_s[:4]+[splited_s[4]+splited_s[5]]+splited_s[6:]

    #extract team and winner
    if 'vs' in splited_s[0+dec]:

        try :
            data['Team A'] = role_id_dict[int(re.findall(pattern_role, splited_s[0+dec].split('vs')[0])[0])]
        except:
            data['Team A']  = 'UNKNOWN'

        try :
            data['Team B'] = role_id_dict[int(re.findall(pattern_role, splited_s[0+dec].split('vs')[1])[0])]
        except:
            data['Team B'] = 'UNKNOWN'

        #extract winner
        try :
            data['Winner'] = role_id_dict[int(re.findall(pattern_role, splited_s[1+dec])[0])]
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
        if 'map' in splited_s[3+dec]:

            line = splited_s[3+dec].split(':')
            bans = line[1].split('/')
            for i in range(6) :
                try :
                    data['Map ban{0}'.format(i+1)]=bans[i].strip()
                except :
                    data['Map ban{0}'.format(i+1)]=0

        #extract leader bans
        if 'leader' in splited_s[4+dec]:

            line = splited_s[4+dec].split(':')
            bans = line[1].split('/')
            for i in range(14) :
                try :
                    data['Ban{0}'.format(i+1)]=bans[i].strip()
                except :
                    data['Ban{0}'.format(i+1)]='UNKNOWN'


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
                data['PlayerA{0}'.format(i+1)]=player_id_dict[int(re.findall(pattern_user, splited_s[6+i+dec])[0])]
            except:
                data['PlayerA{0}'.format(i+1)] = 'UNKNOWN'
            try:
                data['PlayerB{0}'.format(i+1)] =player_id_dict[int(re.findall(pattern_user, splited_s[11+i+dec])[0])]
            except:
                data['PlayerB{0}'.format(i+1)] = 'UNKNOWN'

    else:
        if verbose:
            print('Matching failed')
            print(s)
        raise 'Matching failed'
    return data

def extract_from_serie_raw(s, player_id_dict, role_id_dict, verbose=False):
    l=[]
    for row in s.iterrows():
        try :
            data = extract_from_string_raw(row[1]['message'], player_id_dict, role_id_dict, verbose)
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
civ_fr_id = 'Civfr.com'


@client.event
async def on_ready():


    for guild in client.guilds:
        if guild.name == civ_fr_id:

            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}\n'
            )
            # Building user database
            player_id_dict = {}
            for member in guild.members:
                id = member.id
                name = member.display_name
                player_id_dict[id]=name

        #Building role database (team)
            role_id_dict = {}
            for role in guild.roles:
                id = role.id
                name = role.name
                role_id_dict[id]=name


            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d1')
            messages = [{'message':message.content,'date' : message.created_at} async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30),limit=1000)]
            df1 = pd.DataFrame(messages)
            df1 = extract_from_serie_raw(df1, player_id_dict, role_id_dict)
            df1['Division'] = '1'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d2')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30),limit=1000)]
            df2 = pd.DataFrame(messages)
            df2 = extract_from_serie_raw(df2, player_id_dict, role_id_dict)
            df2['Division'] = '2'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d3a')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30),limit=1000)]
            df3a= pd.DataFrame(messages)
            df3a = extract_from_serie_raw(df3a, player_id_dict, role_id_dict)
            df3a['Division'] = '3a'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d3b')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30),limit=1000)]
            df3b = pd.DataFrame(messages)
            df3b = extract_from_serie_raw(df3b, player_id_dict, role_id_dict)
            df3b['Division'] = '3b'

            df = pd.concat([df1, df2, df3a, df3b], axis=0)
            df.to_csv(base_path + 'data_S15.csv', index=False)

    print('report scrapped')

    conn = sqlite3.connect(base_path + 'database.db')

    conn.execute("DROP TABLE IF EXISTS games")

    data = pd.read_csv(base_path + 'data_S15.csv')
    data['id'] = data.index
    data.to_sql('games', conn)

    conn.commit()

    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par leur nom
    cursor = conn.cursor()

    # Récupération de toutes les lignes de la table "games"
    cursor.execute("SELECT * FROM games")
    games_data = cursor.fetchall()

    # Dictionnaire pour stocker les joueurs uniques.
    # Clé : pseudo du joueur.
    # Valeur : dictionnaire contenant :
    #   - "teams" : dictionnaire avec comme clé le nom de l'équipe et comme valeur le nombre de matchs joués pour cette équipe.
    #   - "games" : ensemble des IDs des matchs où il apparaît.
    players_dict = {}

    # Dictionnaire pour stocker les équipes.
    # Clé : nom de l'équipe.
    # Valeur : dictionnaire contenant :
    #   - "players" : ensemble des pseudos appartenant à l'équipe.
    #   - "games"   : ensemble des IDs des matchs où l'équipe a joué.
    #   - "division": la division de l'équipe (prise lors de la première occurrence).
    teams_dict = {}

    for row in games_data:
        game_id = row["index"]
        division = row["Division"].strip() if row["Division"] else ""
        teamA = row["Team A"].strip() if row["Team A"] else ""
        teamB = row["Team B"].strip() if row["Team B"] else ""

        # Mise à jour des informations pour Team A et Team B dans teams_dict
        if teamA:
            if teamA not in teams_dict:
                teams_dict[teamA] = {"players": set(), "games": set(), "division": division}
            teams_dict[teamA]["games"].add(str(game_id))
        if teamB:
            if teamB not in teams_dict:
                teams_dict[teamB] = {"players": set(), "games": set(), "division": division}
            teams_dict[teamB]["games"].add(str(game_id))

        # Pour les joueurs de l'équipe A (PlayerA1 à PlayerA4)
        for col in ["PlayerA1", "PlayerA2", "PlayerA3", "PlayerA4"]:
            pseudo = row[col]
            if pseudo and pseudo.strip():
                pseudo = pseudo.strip()
                if pseudo not in players_dict:
                    players_dict[pseudo] = {"teams": {}, "games": set()}
                players_dict[pseudo]["games"].add(str(game_id))
                if teamA:
                    # Incrémente le compteur pour teamA
                    players_dict[pseudo]["teams"][teamA] = players_dict[pseudo]["teams"].get(teamA, 0) + 1

        # Pour les joueurs de l'équipe B (PlayerB1 à PlayerB4)
        for col in ["PlayerB1", "PlayerB2", "PlayerB3", "PlayerB4"]:
            pseudo = row[col]
            if pseudo and pseudo.strip():
                pseudo = pseudo.strip()
                if pseudo not in players_dict:
                    players_dict[pseudo] = {"teams": {}, "games": set()}
                players_dict[pseudo]["games"].add(str(game_id))
                if teamB:
                    # Incrémente le compteur pour teamB
                    players_dict[pseudo]["teams"][teamB] = players_dict[pseudo]["teams"].get(teamB, 0) + 1

    # Pour chaque joueur, déterminer l'équipe pour laquelle il a joué le plus de matchs
    for pseudo, info in players_dict.items():
        if info["teams"]:
            best_team = max(info["teams"].items(), key=lambda x: x[1])[0]
            info["team"] = best_team
        else:
            info["team"] = ""

    # Compléter teams_dict avec la liste des joueurs extraits
    for pseudo, info in players_dict.items():
        team = info["team"]
        if team:
            if team not in teams_dict:
                teams_dict[team] = {"players": set(), "games": set(), "division": ""}
            teams_dict[team]["players"].add(pseudo)

    # Suppression des tables existantes si elles existent déjà
    cursor.execute("DROP TABLE IF EXISTS players")
    cursor.execute("DROP TABLE IF EXISTS player_games")
    cursor.execute("DROP TABLE IF EXISTS teams")
    cursor.execute("DROP TABLE IF EXISTS team_players")
    cursor.execute("DROP TABLE IF EXISTS team_games")

    # Création de la table players (pour les joueurs)
    cursor.execute('''
            CREATE TABLE players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                team TEXT NOT NULL
            )
        ''')

    # Création de la table player_games (liaison joueur - match)
    cursor.execute('''
            CREATE TABLE player_games (
                player_id INTEGER,
                game_id INTEGER,
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        ''')

    # Création de la table teams (pour les équipes)
    cursor.execute('''
            CREATE TABLE teams (
                team_name TEXT PRIMARY KEY,
                division TEXT
            )
        ''')

    # Création de la table team_players (liaison équipe - joueur)
    cursor.execute('''
            CREATE TABLE team_players (
                team_name TEXT,
                player_id INTEGER,
                FOREIGN KEY(team_name) REFERENCES teams(team_name),
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        ''')

    # Création de la table team_games (liaison équipe - match)
    cursor.execute('''
            CREATE TABLE team_games (
                team_name TEXT,
                game_id INTEGER,
                FOREIGN KEY(team_name) REFERENCES teams(team_name)
            )
        ''')

    # Insertion des joueurs dans la table players et création du mapping pseudo -> player_id
    player_id_map = {}
    for pseudo, info in players_dict.items():
        team = info["team"]
        cursor.execute("INSERT INTO players (pseudo, team) VALUES (?, ?)", (pseudo, team))
        new_player_id = cursor.lastrowid
        player_id_map[pseudo] = new_player_id
        for game_id in info["games"]:
            cursor.execute("INSERT INTO player_games (player_id, game_id) VALUES (?, ?)", (new_player_id, int(game_id)))

    # Insertion des équipes dans la table teams et dans les tables de liaison
    for team_name, info in teams_dict.items():
        division = info.get("division", "")
        cursor.execute("INSERT INTO teams (team_name, division) VALUES (?, ?)", (team_name, division))
        for game_id in info["games"]:
            cursor.execute("INSERT INTO team_games (team_name, game_id) VALUES (?, ?)", (team_name, int(game_id)))
        for pseudo in info["players"]:
            player_id = player_id_map.get(pseudo)
            if player_id:
                cursor.execute("INSERT INTO team_players (team_name, player_id) VALUES (?, ?)", (team_name, player_id))

    conn.commit()
    conn.close()
    print(f"Nouvelles tables ajoutées dans database.db' : {len(players_dict)} joueurs et {len(teams_dict)} équipes.")
    conn.close()

    await client.close()

path_token = base_path + "token.txt"
with open(path_token, 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)


