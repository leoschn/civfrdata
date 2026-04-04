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
cwc_name = 'CivWorldCup'


@client.event
async def on_ready():
    #
    #
    for guild in client.guilds:
        if guild.name == cwc_name:

            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}\n'
            )
            # Building user database
            player_id_map_cwc= {}
            for member in guild.members:
                id = member.id
                name = member.display_name
                role_list = member.roles
                role_list = [role.id for role in role_list]
                player_id_map_cwc[id]={}
                player_id_map_cwc[id]["name"] = name
                player_id_map_cwc[id]["role_list"] = role_list

        #Building role database (team)
            role_id_map_cwc= {}
            for role in guild.roles:
                id = role.id
                name = role.name
                role_id_map_cwc[id]=name
            print(role_id_map_cwc)
            c_channel = discord.utils.get(guild.text_channels, name='game-reports')
            messages = [{'message': message.content, 'date': message.created_at} async for message in
                        c_channel.history(after=datetime.datetime(2026, 4, 1, 8, 30), limit=1000)]
            df1 = pd.DataFrame(messages)
            df1 = extract_from_serie_raw(df1, format='civfr')
            df1['Division'] = 'CWC'

            for col in ['PlayerA1','PlayerB1','PlayerA2','PlayerB2','PlayerA3','PlayerB3','PlayerA4','PlayerB4']:
                df1[col]= df1[col].map(lambda x :player_id_map_cwc[int(x)]["name"] )

            for col in ['Team A','Team B','Winner']:
                df1[col] = df1[col].map(lambda x: role_id_map_cwc[int(x)])
            df1.to_csv('~/public_html/civfrdata/cwc_database.csv',index=False)
    await client.close()

path_token = base_path + "token.txt"
with open(path_token, 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)