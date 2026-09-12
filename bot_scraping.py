import discord
import datetime
import pandas as pd
from unidecode import unidecode
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
            data['Team B']  = 'UNKNOWN'

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
            data['discord_message_id'] = row[1]['message_id']
        except :
            # Not a report (e.g. no 'vs' in the first line) - correctly
            # dropped here, same as before. A report message that gets
            # EDITED into something unparseable also lands here and is
            # dropped the same way; see merge_season_games for what that
            # means for a game that used to exist at this message id.
            pass
        else:
            l.append(data.copy())
    return pd.DataFrame(l)


# ============================================================================
# Season configuration - THE ONLY BLOCK YOU SHOULD NEED TO EDIT AT THE START
# OF A NEW SEASON. No database file renaming, no manually-counted id offset:
# the merge step below (merge_season_games) figures both out automatically
# from what's already in database_complete.db.
# ============================================================================
SEASON = 18
LEAGUE = "civfr"
SEASON_START = datetime.datetime(2026, 8, 30, 8, 30)
DIVISION_CHANNELS = {
    "1": "s18-reporting-d1",
    "2": "s18-reporting-d2",
    "3": "s18-reporting-d3",
    "4": "s18-reporting-d4",
}
DATABASE_PATH = base_path + "database_complete.db"
# ============================================================================


def merge_season_games(conn, df, season, league, player_id_map, role_id_map):
    """
    Merge one season's freshly-scraped games into the persistent
    database_complete.db, replacing the old approach of copying a growing
    chain of baseline snapshot files (database_s15_s16_cpl.db, ...) and
    hand-counting a `data.index += N` id offset each season.

    df: DataFrame of this (season, league)'s games, same columns as before,
        no 'id' column yet.
    player_id_map: {player_id: {"name": str, "role_list": [role_id, ...]}}
    role_id_map:   {role_id: team_name}

    Returns (n_games_merged, id_offset_used).

    Tested against a copy of the real database in /home/steam/db_test
    (season_merge.py + run_tests.py, plus test_edit_scenario.py for the
    message-edit behaviour below) before being wired in here.

    Id assignment is keyed off each report's Discord message id (df must
    have a `discord_message_id` column - see extract_from_serie_raw), not
    its position in the scraped list. This matters because a message can be
    EDITED after the fact (correcting a mistake): Discord's history() always
    returns a message's current content, so a rescrape just sees updated
    text at the same message id - matching on that id means the same game
    gets updated in place, not duplicated or reassigned a new id. A message
    that fails to parse as a report (never was one, or was edited into
    something that no longer looks like one) is simply absent from df and
    its game - if it had one - is dropped when this season+league's rows are
    replaced below, without disturbing any other game's id.

    (An earlier, positional version of this function assigned ids by row
    order instead, which had exactly this problem: dropping or reordering
    one message silently reassigned every later game's id. See
    test_edit_scenario.py for a reproduction.)
    """
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(games)")
    if "discord_message_id" not in {row[1] for row in cursor.fetchall()}:
        cursor.execute("ALTER TABLE games ADD COLUMN discord_message_id INTEGER")

    # Match each scraped report to an existing game by Discord message id.
    # NB: MAX(existing ids)+1 for brand-new messages is still safe against
    # the Season=5/CPL id range being historically higher than later civfr
    # seasons, because we only ever look at THIS season+league's own ids.
    existing = dict(cursor.execute(
        "SELECT discord_message_id, id FROM games WHERE Season=? AND league=? AND discord_message_id IS NOT NULL",
        (season, league),
    ).fetchall())

    if existing:
        next_new_id = max(existing.values()) + 1
    else:
        (max_id,) = cursor.execute("SELECT COALESCE(MAX(id), -1) FROM games").fetchone()
        next_new_id = max_id + 1
    offset = next_new_id

    ids = []
    for msg_id in df["discord_message_id"]:
        if msg_id in existing:
            ids.append(existing[msg_id])
        else:
            ids.append(next_new_id)
            next_new_id += 1

    # Idempotent rerun: wipe this season+league's existing footprint first.
    # player_games/team_games are safe to delete-and-rebuild by game_id since
    # a game belongs to exactly one season. team_players/team_players_legacy
    # are NOT season-scoped (no season column - they're a team's all-time
    # roster), so they must never be deleted this way; only added to, below.
    cursor.execute(
        "DELETE FROM player_games WHERE game_id IN (SELECT id FROM games WHERE Season=? AND league=?)",
        (season, league),
    )
    cursor.execute(
        "DELETE FROM team_games WHERE game_id IN (SELECT id FROM games WHERE Season=? AND league=?)",
        (season, league),
    )
    cursor.execute("DELETE FROM games WHERE Season=? AND league=?", (season, league))

    df = df.copy()
    df.index = ids
    df["id"] = ids

    cols = list(df.columns)
    placeholders = ",".join("?" for _ in cols)
    col_list = ",".join(f'"{c}"' for c in cols)
    cursor.executemany(
        f"INSERT INTO games ({col_list}) VALUES ({placeholders})",
        [tuple(row) for row in df.itertuples(index=False, name=None)],
    )

    players_dict = {}
    teams_dict = {}
    row_name_player_A = ["PlayerA1", "PlayerA2", "PlayerA3", "PlayerA4"]
    row_name_player_B = ["PlayerB1", "PlayerB2", "PlayerB3", "PlayerB4"]

    for row in df.to_dict(orient="records"):
        game_id = row["id"]
        division = row["Division"]
        teamA, teamB = row["Team A"], row["Team B"]

        if teamA != "UNKNOWN":
            teamA = int(teamA)
            teams_dict.setdefault(teamA, {"players": set(), "games": set(), "division": division, "league": league})
            teams_dict[teamA]["games"].add(str(game_id))
            for rn in row_name_player_A:
                teams_dict[teamA]["players"].add(row[rn])
        if teamB != "UNKNOWN":
            teamB = int(teamB)
            teams_dict.setdefault(teamB, {"players": set(), "games": set(), "division": division, "league": league})
            teams_dict[teamB]["games"].add(str(game_id))
            for rn in row_name_player_B:
                teams_dict[teamB]["players"].add(row[rn])

        for col, team in (("PlayerA1", teamA), ("PlayerA2", teamA), ("PlayerA3", teamA), ("PlayerA4", teamA),
                          ("PlayerB1", teamB), ("PlayerB2", teamB), ("PlayerB3", teamB), ("PlayerB4", teamB)):
            try:
                pid = int(row[col])
            except (TypeError, ValueError):
                continue
            players_dict.setdefault(pid, {"teams": {}, "games": set(),
                                           "pseudo": player_id_map.get(pid, {}).get("name", "UNKNOWN")})
            players_dict[pid]["games"].add(str(game_id))
            if team:
                players_dict[pid]["teams"][int(team)] = players_dict[pid]["teams"].get(int(team), 0) + 1

    for pid, info in players_dict.items():
        current_team = "NONE"
        for team_id in info["teams"]:
            if pid in player_id_map and team_id in player_id_map[pid].get("role_list", []):
                current_team = team_id
        cursor.execute(
            "REPLACE INTO players (player_id, player_name, team_civfr, team_cpl) VALUES (?, ?, ?, ?)",
            (pid, info["pseudo"], current_team, None),
        )
        for gid in info["games"]:
            cursor.execute("INSERT INTO player_games (player_id, game_id) VALUES (?, ?)", (pid, int(gid)))

    for team_id, info in teams_dict.items():
        for gid in info["games"]:
            cursor.execute("INSERT INTO team_games (team_id, game_id) VALUES (?, ?)", (team_id, int(gid)))
        for pid in info["players"]:
            # Additive only (see comment above): never wipe a team's roster
            # history, just make sure this (team, player) pair exists once.
            cursor.execute(
                "INSERT INTO team_players (team_id, player_id) "
                "SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM team_players WHERE team_id=? AND player_id=?)",
                (team_id, pid, team_id, pid),
            )
            cursor.execute(
                "INSERT INTO team_players_legacy (team_id, player_id) "
                "SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM team_players_legacy WHERE team_id=? AND player_id=?)",
                (team_id, pid, team_id, pid),
            )
        cursor.execute(
            "REPLACE INTO teams (team_id, team_name, division, league) VALUES (?, ?, ?, ?)",
            (team_id, role_id_map.get(team_id, f"team_{team_id}"), info["division"], league),
        )

    conn.commit()
    return len(df), offset


# enabling intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
civfr_id = 'Civfr.com'
cpl_name = 'CivPlayers Leagues'


@client.event
async def on_ready():
    player_id_map_civfr = {}
    role_id_map_civfr = {}

    for guild in client.guilds:
        if guild.name == civfr_id:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}\n'
            )
            # Building user database
            for member in guild.members:
                player_id_map_civfr[member.id] = {
                    "name": member.display_name,
                    "role_list": [role.id for role in member.roles],
                }

            # Building role database (team)
            for role in guild.roles:
                role_id_map_civfr[role.id] = role.name

            # Scrape each division's reporting channel (channel names/season
            # start date come from the config block at the top of this file -
            # that's the only thing to edit for a new season).
            dfs = []
            for division, channel_name in DIVISION_CHANNELS.items():
                c_channel = discord.utils.get(guild.text_channels, name=channel_name)
                messages = [{'message': message.content, 'date': message.created_at, 'message_id': message.id}
                            async for message in c_channel.history(after=SEASON_START, limit=1000)]
                df_div = pd.DataFrame(messages)
                df_div = extract_from_serie_raw(df_div, format='civfr')
                df_div['Division'] = division
                dfs.append(df_div)

        # CPL scraping is currently disabled (channel/report format was never
        # finalized for it) - the guild's member/role maps are left ready so
        # it can be turned back on by uncommenting a channel scrape above and
        # calling merge_season_games(conn, df_cpl, season=SEASON, league="cpl",
        # player_id_map=player_id_map_cpl, role_id_map=role_id_map_cpl).
        # if guild.name == cpl_name:
        #     ...

    df = pd.concat(dfs, axis=0)
    df['league'] = LEAGUE
    df['Season'] = SEASON
    df.to_csv(base_path + f'data_S{SEASON}.csv', index=False)
    print('report scrapped')

    conn = sqlite3.connect(DATABASE_PATH)
    n_games, offset = merge_season_games(
        conn, df, season=SEASON, league=LEAGUE,
        player_id_map=player_id_map_civfr, role_id_map=role_id_map_civfr,
    )
    conn.close()
    print(f"Season {SEASON}: merged {n_games} games into {DATABASE_PATH} (id offset {offset}).")

    await client.close()

path_token = base_path + "token.txt"
with open(path_token, 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)
