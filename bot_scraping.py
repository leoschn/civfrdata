import os

import discord
import datetime
import pandas as pd
from unidecode import unidecode
import sqlite3
import re

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
            messages = [{'message':message.content,'date' : message.created_at} async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30))]
            df1 = pd.DataFrame(messages)
            df1 = extract_from_serie_raw(df1, player_id_dict, role_id_dict)
            df1['Division'] = '1'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d2')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30))]
            df2 = pd.DataFrame(messages)
            df2 = extract_from_serie_raw(df2, player_id_dict, role_id_dict)
            df2['Division'] = '2'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d3a')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30))]
            df3a= pd.DataFrame(messages)
            df3a = extract_from_serie_raw(df3a, player_id_dict, role_id_dict)
            df3a['Division'] = '3a'

            c_channel = discord.utils.get(guild.text_channels, name='s15-reporting-d3b')
            messages = [{'message':message.content,'date' : message.created_at}  async for message in c_channel.history(after=datetime.datetime(2025,1,17,14,30))]
            df3b = pd.DataFrame(messages)
            df3b = extract_from_serie_raw(df3b, player_id_dict, role_id_dict)
            df3b['Division'] = '3b'

            df = pd.concat([df1, df2, df3a, df3b], axis=0)
            df.to_csv('data_S15.csv', index=False)

    print('report scrapped')

    connection = sqlite3.connect('database.db')

    connection.execute("DROP TABLE IF EXISTS games")

    data = pd.read_csv('data_S15.csv')
    data['id'] = data.index
    data.to_sql('games', connection)

    connection.commit()
    connection.close()

    await client.close()

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-1]
rel_path = "token.txt"
path = "/".join(script_directory) + "/" + rel_path
with open(path, 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)

