import time
import csv
import io
import sqlite3
from collections import defaultdict
from datetime import datetime
import pickle
import numpy as np
import spacy
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import Response
from werkzeug.exceptions import abort
# Listes modifiées avec le joli nom (display name)
from werkzeug.utils import redirect

list_civ_url = [
    ("abraham lincoln", 'Abraham_Lincoln_29.webp', "Abraham Lincoln"),
    ("alexander", 'Alexander_29.webp', "Alexander"),
    ("amanitore", 'Amanitore_29.webp', "Amanitore"),
    ("ambiorix", 'Ambiorix_29.webp', "Ambiorix"),
    ("basil ii", 'Basil_II_29.webp', "Basil II"),
    ("ba trieu", 'B3Fu_29.webp', "Ba Trieu"),
    ("catherine de medici (black queen)", 'Catherine_de_Medici_29.webp', "Catherine de Medici (Black Queen)"),
    ("chandragupta", 'Chandragupta_29.webp', "Chandragupta"),
    ("cleopatra (egyptian)", 'Cleopatra_29.webp', "Cleopatra (Egyptian)"),
    ("cyrus", 'Cyrus_29.webp', "Cyrus"),
    ("dido", 'Dido_29.webp', "Dido"),
    ("eleanor of aquitaine (england)", 'Eleanor_of_Aquitaine_29_29.webp', "Eleanor of Aquitaine (England)"),
    ("eleanor of aquitaine (france)", 'Eleanor_of_Aquitaine_29_29_fr.webp', "Eleanor of Aquitaine (France)"),
    ("elizabeth i", 'Elizabeth_I_29.webp', "Elizabeth I"),
    ("frederick barbarossa", 'Frederick_Barbarossa_29.webp', "Frederick Barbarossa"),
    ("gandhi", 'Gandhi_29.webp', "Gandhi"),
    ("genghis khan", 'Genghis_Khan_29.webp', "Genghis Khan"),
    ("gilgamesh", 'Gilgamesh_29.webp', "Gilgamesh"),
    ("gitarja", 'Gitarja_29.webp', "Gitarja"),
    ("gorgo", 'Gorgo_29.webp', "Gorgo"),
    ("hammurabi", 'Hammurabi_29.webp', "Hammurabi"),
    ("harald hardrada", 'Harald_Hardrada_29.webp', "Harald Hardrada"),
    ("hojo tokimune", 'Hojo_Tokimune_29.webp', "Hojo Tokimune"),
    ("jadwiga", 'Jadwiga_29.webp', "Jadwiga"),
    ("jaravarman vii", 'Jayavarman_VII_29.webp', "Jayavarman VII"),
    ("joao iii", 'Jo_29.webp', "Joao III"),
    ("john curtin", 'John_Curtin_29.webp', "John Curtin"),
    ("julius caesar", 'Julius_Caesar_29.webp', "Julius Caesar"),
    ("kristina", 'Kristina_29.webp', "Kristina"),
    ("kublai khan (china)", 'Kublai_Khan_29_29.webp', "Kublai Khan (China)"),
    ("kublai khan (mongolia)", 'Kublai_Khan_29_29_mong.webp', "Kublai Khan (Mongolia)"),
    ("kupe", 'Kupe_29.webp', "Kupe"),
    ("lady six sky", 'Lady_Six_Sky_29.webp', "Lady Six Sky"),
    ("lautaro", 'Lautaro_29.webp', "Lautaro"),
    ("ludwig ii", 'Ludwig_II_29.webp', "Ludwig II"),
    ("mansa musa", 'Mansa_Musa_29.webp', "Mansa Musa"),
    ("matthias corvinus", 'Matthias_Corvinus_29.webp', "Matthias Corvinus"),
    ("menelik ii", 'Menelik_II_29.webp', "Menelik II"),
    ("montezuma", 'Montezuma_29.webp', "Montezuma"),
    ("mvemba a nzinga", 'Mvemba_a_Nzinga_29.webp', "Mvemba a Nzinga"),
    ("nader shah", 'Nader_Shah_29.webp', "Nader Shah"),
    ("nzinga mbande", 'Nzinga_Mbande_29.webp', "Nzinga Mbande"),
    ("pachacuti", 'Pachacuti_29.webp', "Pachacuti"),
    ("pedro ii", 'Pedro_II_29.webp', "Pedro II"),
    ("pericles", 'Pericles_29.webp', "Pericles"),
    ("peter", 'Peter_29.webp', "Peter"),
    ("philip ii", 'Philip_II_29.webp', "Philip II"),
    ("poundmaker", 'Poundmaker_29.webp', "Poundmaker"),
    ("qin (mandate of heaven)", 'Qin_Shi_Huang_29.webp', "Qin (Mandate of Heaven)"),
    ("qin (unifier)", 'Qin_Shi_Huang_29_29.webp', "Qin (Unifier)"),
    ("ramses ii", 'Ramses_II_29.webp', "Ramses II"),
    ("robert the bruce", 'Robert_the_Bruce_29.webp', "Robert the Bruce"),
    ("saladin (sultan)", 'Saladin_29_29.webp', "Saladin (Sultan)"),
    ("saladin (vizier)", 'Saladin_29.webp', "Saladin (Vizier)"),
    ("sejong", 'Sejong_29.webp', "Sejong"),
    ("seondeok", 'Seondeok_29.webp', "Seondeok"),
    ("shaka", 'Shaka_29.webp', "Shaka"),
    ("simon bolivar", 'Sim3Fvar_29.webp', "Simon Bolivar"),
    ("suleiman (muhtesem)", 'Suleiman_29_29.webp', "Suleiman (Muhtesem)"),
    ("suleiman (kanuni)", 'Suleiman_29.webp', "Suleiman (Kanuni)"),
    ("soundiata keita", 'Sundiata_Keita_29.webp', "Sundiata Keita"),
    ("tamar", 'Tamar_29.webp', "Tamar"),
    ("teddy roosevelt (bull moose)", 'Teddy_Roosevelt_29.webp', "Teddy Roosevelt (Bull Moose)"),
    ("teddy roosevelt (rough rider)", 'Teddy_Roosevelt_29_29.webp', "Teddy Roosevelt (Rough Rider)"),
    ("theodora", 'Theodora_29.webp', "Theodora"),
    ("tokugawa", 'Tokugawa_29.webp', "Tokugawa"),
    ("tomyris", 'Tomyris_29.webp', "Tomyris"),
    ("trajan", 'Trajan_29.webp', "Trajan"),
    ("victoria", 'Victoria_29.webp', "Victoria"),
    ("victoria age of steam", 'Victoria_29_29.webp', "Victoria Age of Steam"),
    ("wilfrid laurier", 'Wilfrid_Laurier_29.webp', "Wilfrid Laurier"),
    ("wilhelmina", 'Wilhelmina_29.webp', "Wilhelmina"),
    ("wu zetian", 'Wu_Zetian_29.webp', "Wu Zetian"),
    ("yongle", 'Yongle_29.webp', "Yongle"),
    ("harald varangian", 'Harald_Hardrada_29_29.webp', "Harald Varangian"),
    ("cleopatra (ptolemaic)", 'Cleopatra_29_29.webp', "Cleopatra (Ptolemaic)"),
    ("catherine de medici (manificence)", 'Catherine_de_Medici_29_29.webp', "Catherine de Medici (Magnificence)"),
    ("trisong detsen",'Trisong.png',"Trisong Detsen"),
    ("te kinich ii ",'TeKinich.png',"Te' K'inich II"),
    ("olympias",'1Olympias.png',"Olympias"),
    ("kiviuq",'K1iviuq.png',"Kiviuq"),
    ("al-hasan ibn sulaiman",'1AlHasan.png',"Al-Hasan ibn Sulaiman"),
    ("vercingetorix",'Vercingetorix1.png',"Vercingetorix"),
    ("ahiram",'Ahiram2.png',"Ahiram"),
    ("spearthrower",'Spearthrower.png',"Spearthrower"),
]

list_map_url = [
    ("pangaea standard", 'Pangaea_Standard-cb7cdd6b.png', "Pangaea Standard"),
    ("pangaea classic", 'Pangaea_Classic-4f1cfc97.png', "Pangaea Classic"),
    ("seven seas", 'Map_Seven_Seas_29.webp', "Seven Seas"),
    ("rich highlands", 'Map_Highlands_29.webp', "Rich Highlands"),
    ("lakes", 'Map_Lakes_29.webp', "Lakes"),
    ("tilted axis", 'Map_Tilted_Axis_(Civ6).webp', "Tilted Axis"),
    ("primordial", 'Map_Primodial_29.webp', "Primordial"),
    ("inland sea", 'Map_Inland_Sea_29.webp', "Inland Sea"),
    ("pangaea est-west", 'Inland_Est_West-25322f67.png', "Pangaea Est-West "),
    ("inland est-west","Inland_Est_West-25322f67.png","Inland Est-West")
]

# Dictionnaires pour les assets (chemin vers l'image)
CIV_ASSETS_NAMES = defaultdict(lambda: '../static/assets/unknown-18-512.png')
for ident, fichier, _ in list_civ_url:
    CIV_ASSETS_NAMES[ident] = '../static/assets/' + fichier

MAP_ASSETS_NAME = defaultdict(lambda: '../static/assets/unknown-18-512.png')
for ident, fichier, _ in list_map_url:
    MAP_ASSETS_NAME[ident] = '../static/assets/' + fichier

# Dictionnaires pour les jolis noms (display names)
CIV_DISPLAY_NAMES = {ident: display for ident, _, display in list_civ_url}
MAP_DISPLAY_NAMES = {ident: display for ident, _, display in list_map_url}

def get_db_connection(season):
    if season=='all' :
        conn = sqlite3.connect('database_complete.db')
    elif season ==15:
        conn = sqlite3.connect('database_s15_legacy.db')
    elif season ==16 :
        conn = sqlite3.connect('database_s16.db')
    elif season =='cpl5' :
        conn = sqlite3.connect('database_CPL5.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_game(game_id,season='all'):
    conn = get_db_connection(season)
    game = conn.execute('SELECT * FROM games WHERE id = ?',
                        (game_id,)).fetchone()
    conn.close()
    if game is None:
        abort(404)

    return game

app = Flask(__name__)

def get_all_players(season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row
    players = conn.execute('SELECT DISTINCT player_id,player_name FROM players ORDER BY LOWER(player_name) ASC').fetchall()
    conn.close()
    return players

def get_all_teams(season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row
    teams = conn.execute('SELECT DISTINCT team_id, team_name, division FROM teams ORDER BY LOWER(team_name) ASC').fetchall()
    conn.close()
    return teams

def get_civ_data_from_game(games,civs):
    civ_data = {}
    total_game = len(games)
    for civ in civs :
        civ_data[civ]=np.array([0,0,0,0]) #{'win':0,'lose':0,'ban':0,'pick':0}

    for game in games :
        for pick in ['PickA1','PickA2','PickA3','PickA4']:
            if game[pick] in civs:
                if game['Winner'] == game['Team A']:
                    civ_data[game[pick]]=civ_data[game[pick]]+[1,0,0,1]
                elif game['Winner'] == game['Team B']:
                    civ_data[game[pick]] = civ_data[game[pick]] + [0, 1, 0, 1]
                else:
                    civ_data[game[pick]] = civ_data[game[pick]] + [0, 0, 0, 1]

        for pick in ['PickB1','PickB2','PickB3','PickB4']:
            if game[pick] in civs:
                if game['Winner'] == game['Team A']:
                    civ_data[game[pick]]=civ_data[game[pick]] + [0, 1, 0, 1]
                elif game['Winner'] == game['Team B']:
                    civ_data[game[pick]] = civ_data[game[pick]]  +[1,0,0,1]
                else:
                    civ_data[game[pick]] = civ_data[game[pick]] + [0, 0, 0, 1]

        for pick in ['Ban1','Ban2','Ban3','Ban4','Ban5','Ban6','Ban7','Ban8','Ban9','Ban10','Ban11','Ban12']:
            if game[pick] in civs:
                civ_data[game[pick]] = civ_data[game[pick]] + [0, 0, 1, 0]

    for civ in civs :
        data = civ_data[civ].tolist()
        civ_data[civ] = {'win_rate': round(100*data[0]/max(1,data[3]),1),'lose_rate':round(100*data[1]/max(1,data[3]),1),'ban_rate':round(100*data[2]/total_game,1),'pick_rate':round(100*data[3]/total_game,1),'pick':data[3]}
    return civ_data,total_game

def get_player_stats(player_id,season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row

   # Récupérer les informations du joueur dans la table players
    player_row = conn.execute(
        'SELECT * FROM players WHERE player_id = ?', (player_id,)).fetchone()
    if player_row is None:
        conn.close()
        return None  # Le joueur n'existe pas

    player_name = player_row['player_name']
    team_cpl = player_row['team_cpl']
    team_civfr = player_row['team_civfr']

    # Récupérer les game_ids depuis la table de liaison player_games pour ce player_id
    game_rows = conn.execute(
        'SELECT game_id FROM player_games WHERE player_id = ?', (player_id,)
    ).fetchall()
    # Transformation en liste d'entiers
    game_ids = [row['game_id'] for row in game_rows]

    matches = []      # Liste des matchs joués avec infos détaillées
    civ_counts = {}   # Dictionnaire comptant chaque civilisation jouée
    map_counts = {}   # Dictionnaire comptant chaque map jouée
    wins = 0

    # Pour chaque game dans lequel le joueur a joué
    for game_id in game_ids:
        game = conn.execute(
            'SELECT * FROM games WHERE "id" = ?', (game_id,)
        ).fetchone()
        if game is None:
            continue

        found_slot = False
        # Vérifier si le joueur est dans l'équipe A
        for pos in ["1", "2", "3", "4"]:
            player_col = "PlayerA" + pos
            if game[player_col] == player_id:
                # Le joueur est dans l'équipe A
                opponent = game["Team B"]
                player_team = game["Team A"]
                # Le résultat est "win" si Team A est gagnante, sinon "loss"
                result = "win" if game["Team A"] == game["Winner"] else "loss"
                date = game["Date"]
                if result == "win":
                    wins += 1
                civilization = game["PickA" + pos].strip()
                if game["Map played"]:
                    map_played = game["Map played"].strip()
                else:
                    map_played=None

                # Récupérer le type et tour de victoire
                v_type = game['Victory']
                v_turn = game['Victory Turn']

                matches.append({
                    "player_team": player_team,
                    "opponent": opponent,
                    "result": result,
                    "civilization": civilization,
                    "map": map_played,
                    "date": date,
                    "id": game_id,
                    'v_type': v_type,
                    'v_turn': v_turn
                })
                # Comptage des civilisations
                if civilization:
                    civ_counts[civilization] = civ_counts.get(civilization, 0) + 1
                # Comptage des maps
                if map_played:
                    map_counts[map_played] = map_counts.get(map_played, 0) + 1
                found_slot = True
                break

        # Sinon, vérifier dans l'équipe B
        if not found_slot:
            for pos in ["1", "2", "3", "4"]:
                player_col = "PlayerB" + pos
                if game[player_col] == player_id:
                    opponent =  game["Team A"]
                    player_team =  game["Team B"]
                    result = "win" if  game["Team B"] == game["Winner"] else "loss"
                    date = game["Date"]
                    if result == "win":
                        wins += 1
                    civilization = game["PickB" + pos].strip()
                    if game["Map played"]:
                        map_played = game["Map played"].strip()
                    else :
                        map_played = None

                    # Récupérer le type et tour de victoire
                    v_type = game['Victory']
                    v_turn = game['Victory Turn']

                    matches.append({
                        "player_team": player_team,
                        "opponent": opponent,
                        "result": result,
                        "civilization": civilization,
                        "map": map_played,
                        "date": date,
                        "id": game_id,
                        'v_type': v_type,
                        'v_turn': v_turn
                    })
                    if civilization:
                        civ_counts[civilization] = civ_counts.get(civilization, 0) + 1
                    if map_played:
                        map_counts[map_played] = map_counts.get(map_played, 0) + 1
                    found_slot = True
                    break

    total_games = len(matches)
    winrate = wins / total_games if total_games > 0 else 0.0
    conn.close()

    #order matches by date
    matches.sort(key=lambda x : datetime.strptime(x["date"], "%d/%m/%y") )
    return {
        "player_id": player_id,
        "pseudo": player_name,
        "team_civfr": team_civfr,
        "team_cpl": team_cpl,
        "matches": matches,
        "total_games": total_games,
        "wins": wins,
        "winrate": winrate,
        "civilizations": civ_counts,
        "maps": map_counts
    }

def get_all_teams_dict(season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row
    teams = conn.execute('SELECT DISTINCT team_name,team_id from teams').fetchall()
    teams_dict={}
    for team in teams :
        teams_dict[team['team_id']]=team['team_name']
    return teams_dict

def get_all_players_dict(season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row
    teams = conn.execute('SELECT DISTINCT player_name,player_id from players').fetchall()
    players_dict={}
    for player in teams :
        players_dict[player['player_id']]=player['player_name']
    return players_dict

def get_team_stats(team_id,season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row

    # Récupérer tous les matchs où l'équipe est impliquée (Team A ou Team B)
    matches_query = """
      SELECT *
      FROM games
      WHERE "Team A" = ? OR "Team B" = ?
    """
    matches_data = conn.execute(matches_query, (team_id, team_id)).fetchall()
    matches = []
    wins = 0
    maps_counts = {}
    division = None
    date = datetime(1, 1, 1)

    for game in matches_data:
        league = game['League']
        if datetime.strptime(game['Date'], '%d/%m/%y')>date:
            date = datetime.strptime(game['Date'], '%d/%m/%y')
            division = game["Division"]
        # On suppose que la colonne "Date" existe et contient la date du match.
        match_date = game["Date"]
        # Identifier de quel côté se trouve l'équipe et déterminer l'opposant et le résultat.
        if game["Team A"] == team_id:
            opponent = game["Team B"] if game["Team B"] else ""
            result = "win" if game["Winner"] and game["Team A"] == game["Winner"] else "loss"
        elif game["Team B"] == team_id:
            opponent = game["Team A"] if game["Team A"] else ""
            result = "win" if game["Winner"] and game["Team B"] == game["Winner"] else "loss"
        else:
            continue  # Ce cas ne devrait pas se produire


        if result == "win":
            wins += 1

        # Récupérer la map jouée (colonne "Map played")
        map_played = game["Map played"].strip() if game["Map played"] else ""
        if map_played:
            maps_counts[map_played] = maps_counts.get(map_played, 0) + 1
        id = game["id"]

        #Récupérer le type et tour de victoire
        v_type = game['Victory']
        v_turn = game['Victory Turn']
        matches.append({
            "opponent": opponent,
            "result": result,
            "date": match_date,
            "map": map_played,
            "id": id,
            'v_type' : v_type,
            'v_turn' :v_turn
        })

    total_games = len(matches)

    winrate = wins / total_games if total_games > 0 else 0.0
    loses = total_games - wins
    # Récupérer la liste des joueurs qui appartiennent à cette équipe depuis la table players
    if league =='cpl':
        players = conn.execute('SELECT DISTINCT * FROM players WHERE team_cpl = ?', (team_id,)).fetchall()
    elif league =='civfr':
        players = conn.execute('SELECT DISTINCT * FROM players WHERE team_civfr = ?', (team_id,)).fetchall()
    players_legacy = conn.execute('SELECT DISTINCT * FROM team_players_legacy WHERE team_id = ?', (team_id,)).fetchall()
    team_name = conn.execute('SELECT DISTINCT team_name FROM teams WHERE team_id = ?', (team_id,)).fetchall()[0]['team_name']
    conn.close()



    return {
        "team_id": team_id,
        "team_name":team_name,
        "matches": matches,
        "total_games": total_games,
        "wins": wins,
        "winrate": winrate,
        "maps": maps_counts,
        "players": players,
        "players_legacy":players_legacy,
        "division": division,
        "loses": loses,
    }

def get_minimal_team_stats(team_id,season='all'):
    conn = get_db_connection(season)
    conn.row_factory = sqlite3.Row

    # Récupérer tous les matchs où l'équipe est impliquée (Team A ou Team B)
    matches_query = """
      SELECT *
      FROM games
      WHERE "Team A" = ? OR "Team B" = ?
    """
    matches_data = conn.execute(matches_query, (team_id, team_id)).fetchall()

    wins = 0
    loses = 0

    for game in matches_data:
        div = game["Division"]
        # Identifier de quel côté se trouve l'équipe et déterminer l'opposant et le résultat.
        if game["Team A"] == team_id:
            opponent = game["Team B"] if game["Team B"] else ""
            result = "win" if game["Winner"] and game["Team A"] == game["Winner"] else "loss"
        elif game["Team B"] == team_id:
            opponent = game["Team A"] if game["Team A"] else ""
            result = "win" if game["Winner"] and game["Team B"] == game["Winner"] else "loss"
        else:
            continue  # Ce cas ne devrait pas se produire

        if result == "win":
            wins += 1
        if result == "loss":
            loses += 1


    total_games = len(matches_data)


    return {
        "team_id": team_id,
        "total_games": total_games,
        "wins": wins,
        "loses": loses,
        "win_rate": 0 if total_games==0 else wins/total_games,
    }



@app.route('/')
def landingpage():
    teams = get_all_teams(16)
    divisions = {}

    for team in teams:
        team_dict = dict(team)  # Conversion de sqlite3.Row en dictionnaire
        div = team_dict["division"]
        if div not in divisions:
            divisions[div] = []
        divisions[div].append(team_dict)

    # Pour chaque division, trier les équipes par nombre de victoires décroissant et attribuer un rang
    for div, team_list in divisions.items():
    # On s'assure que le nombre de victoires est un entier

        for team in team_list:
            stats = get_minimal_team_stats(team['team_id'],16)
            team["wins"] = stats["wins"]
            team["loses"] = stats["loses"]
            team["total_games"] = stats["total_games"]

        sorted_teams = sorted(team_list, key=lambda t: int(t.get("wins", 0)), reverse=True)
        for rank, team in enumerate(sorted_teams, start=1):
            team["ranking"] = rank

        divisions[div] = sorted_teams

    # Optionnel : définir l'ordre des divisions à afficher (par exemple, 1, 2, 3a, 3b)
    order = ['1', '2', '3']

    return render_template('landingpage.html', divisions=divisions, order=order)


@app.route('/s15')
def landingpages15():
    teams = get_all_teams(15)
    divisions = {}

    for team in teams:
        team_dict = dict(team)  # Conversion de sqlite3.Row en dictionnaire
        div = team_dict["division"]
        if div not in divisions:
            divisions[div] = []
        divisions[div].append(team_dict)

    # Pour chaque division, trier les équipes par nombre de victoires décroissant et attribuer un rang
    for div, team_list in divisions.items():
    # On s'assure que le nombre de victoires est un entier

        for team in team_list:
            stats = get_minimal_team_stats(team['team_id'],15)
            team["wins"] = stats["wins"]
            team["loses"] = stats["loses"]
            team["total_games"] = stats["total_games"]

        sorted_teams = sorted(team_list, key=lambda t: int(t.get("wins", 0)), reverse=True)
        for rank, team in enumerate(sorted_teams, start=1):
            team["ranking"] = rank

        divisions[div] = sorted_teams

    # Optionnel : définir l'ordre des divisions à afficher (par exemple, 1, 2, 3a, 3b)
    order = ['1', '2', '3a','3b']

    return render_template('landingpage.html', divisions=divisions, order=order)

@app.route('/cpl5')
def landingpagescpl5():
    teams = get_all_teams('cpl5')
    divisions = {}
    for team in teams:
        team_dict = dict(team)  # Conversion de sqlite3.Row en dictionnaire
        div = team_dict["division"]
        if div not in divisions:
            divisions[div] = []
        divisions[div].append(team_dict)

    # Pour chaque division, trier les équipes par nombre de victoires décroissant et attribuer un rang
    for div, team_list in divisions.items():
    # On s'assure que le nombre de victoires est un entier

        for team in team_list:
            stats = get_minimal_team_stats(team['team_id'],'cpl5')
            team["wins"] = stats["wins"]
            team["loses"] = stats["loses"]
            team["total_games"] = stats["total_games"]

        sorted_teams = sorted(team_list, key=lambda t: int(t.get("wins", 0)), reverse=True)
        for rank, team in enumerate(sorted_teams, start=1):
            team["ranking"] = rank

        divisions[div] = sorted_teams

    # Optionnel : définir l'ordre des divisions à afficher (par exemple, 1, 2, 3a, 3b)
    order = ['cpl_1', 'cpl_2', 'cpl_3',]

    return render_template('landingpage.html', divisions=divisions, order=order)


@app.route('/data')
def index():
    conn = get_db_connection('all')
    games = conn.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT DISTINCT "team_id" FROM teams').fetchall()
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()
    list_player = conn.execute('SELECT "player_id" FROM players').fetchall()
    list_season = conn.execute('SELECT DISTINCT "Season" FROM games').fetchall()
    list_league = conn.execute('SELECT DISTINCT "League" FROM games').fetchall()
    player_mapping = get_all_players_dict()
    team_mapping=get_all_teams_dict()
    conn.close()
    # tri des games par date, décroissant
    games = sorted(games, key=lambda game: datetime.strptime(game['Date'], '%d/%m/%y'), reverse=True)
    return render_template('index_search_bar.html', games=games, url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div,
                           team_mapping=team_mapping,player_mapping=player_mapping,list_player=list_player,
                           list_season=list_season,list_league=list_league)

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/games/<int:game_id>', methods=['GET', 'POST'])
def game(game_id):
    game = get_game(game_id)
    player_mapping=get_all_players_dict()
    team_mapping=get_all_teams_dict()
    return render_template('games_civ_draft_style.html', game=game, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME,
                           player_mapping=player_mapping,team_mapping=team_mapping)

@app.route('/player')
def player_list():
    players = get_all_players()
    players = [
        {"player_id": str(row["player_id"]), "player_name": row["player_name"]}
        for row in players
    ]
    return render_template('player_list.html', players=players)

@app.route('/team')
def team_list():
    teams = get_all_teams()
    return render_template('team_list.html', teams=teams)

@app.route('/player/<player_id>')
def player_details(player_id):
    # Récupère toutes les infos détaillées du joueur
    player = get_player_stats(int(player_id))
    team_mapping = get_all_teams_dict()
    if player is None:
        abort(404)
    return render_template('player.html', player=player,url_civ=CIV_ASSETS_NAMES, display_civ=CIV_DISPLAY_NAMES,
                           url_map=MAP_ASSETS_NAME, display_map=MAP_DISPLAY_NAMES, team_mapping=team_mapping)

@app.route('/team/<team_id>')
def team_details(team_id):
    conn = get_db_connection('all')
    conn.row_factory = sqlite3.Row
    team = get_team_stats(int(team_id))
    teams_mapping = get_all_teams_dict()
    player_mapping = get_all_players_dict()
    if team is None:
        abort(404)
    return render_template('team.html', team=team, url_civ=CIV_ASSETS_NAMES, display_civ=CIV_DISPLAY_NAMES,
                           url_map=MAP_ASSETS_NAME, display_map=MAP_DISPLAY_NAMES,teams_mapping=teams_mapping,
                           player_mapping=player_mapping)



@app.route('/search', methods=['GET', 'POST'])
def search():
    team_mapping = get_all_teams_dict()
    player_mapping = get_all_players_dict()
    team_name = request.form.get('team')
    player_name = request.form.get('player')
    map = request.form.get('map')
    div = request.form.get('div')
    season = request.form.get('season')
    league = request.form.get('league')
    conn = get_db_connection('all')

    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT "team_id" FROM teams').fetchall()
    list_player = conn.execute('SELECT "player_id" FROM players').fetchall()
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()
    list_season = conn.execute('SELECT DISTINCT "Season" FROM games').fetchall()
    list_league = conn.execute('SELECT DISTINCT "League" FROM games').fetchall()

    if team_name != '"Team A"':
        team_id = conn.execute('SELECT team_id FROM teams WHERE team_id = ?', (team_name,)).fetchone()['team_id']
    else:
        team_id = team_name
    if player_name !='"PlayerA1"':
        player_id = conn.execute('SELECT player_id FROM players WHERE player_id = ?', (player_name,)).fetchone()['player_id']
    else :
        player_id = player_name

    if map != '"Map played"':
        map = "'"+map+"'"

    if div != '"Division"':
        div = "'"+div+"'"

    if season != '"Season"':
        season = season

    if league != '"League"':
        league = "'"+league+"'"

    #use fstring to pass either column name or value as variable
    print(f'SELECT * FROM games WHERE ("League" = {league}) AND ("Season" = {season}) AND ("Team A" = {team_id} OR "Team B" = {team_id}) AND ("Map played" = {map} ) AND ("Division" = {div} ) AND ("PlayerA1" = {player_id} OR "PlayerA2" = {player_id} OR "PlayerA3" = {player_id} OR "PlayerA4" = {player_id} OR "PlayerB1" = {player_id} OR "PlayerB2" = {player_id} OR "PlayerB3" = {player_id} OR "PlayerB4" = {player_id})')
    games = conn.execute(f'SELECT * FROM games WHERE ("League" = {league}) AND ("Season" = {season}) AND ("Team A" = {team_id} OR "Team B" = {team_id}) AND ("Map played" = {map} ) AND ("Division" = {div} ) AND ("PlayerA1" = {player_id} OR "PlayerA2" = {player_id} OR "PlayerA3" = {player_id} OR "PlayerA4" = {player_id} OR "PlayerB1" = {player_id} OR "PlayerB2" = {player_id} OR "PlayerB3" = {player_id} OR "PlayerB4" = {player_id})')
    games = sorted(games, key=lambda game: datetime.strptime(game['Date'], '%d/%m/%y'), reverse=True)
    conn.close()
    return render_template('index_search_bar.html', games=games,url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div,
                           team_mapping=team_mapping,player_mapping=player_mapping,list_player=list_player,
                           list_season=list_season,list_league=list_league)


@app.route('/data_civ')
def index_civ():
    conn = get_db_connection('all')
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT "team_id" FROM teams').fetchall()
    list_civs = [x[0] for x in list_civ_url]
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()
    team_mapping=get_all_teams_dict()
    conn.close()


    return render_template('civ_data_index.html', url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div,
                           team_mapping=team_mapping, list_civs=list_civs)


@app.route('/civ_data_search', methods=['GET', 'POST'])
def civ_data_search():
    team_mapping = get_all_teams_dict()
    team_name = request.form.get('team')
    civ = request.form.get('civ')
    map = request.form.get('map')
    div = request.form.get('div')
    conn = get_db_connection('all')
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT "team_id" FROM teams').fetchall()
    list_civs = [x[0] for x in list_civ_url]
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()

    if team_name != '"Team A"':
        team_id = conn.execute('SELECT team_id FROM teams WHERE team_id = ?', (team_name,)).fetchone()['team_id']
    else:
        team_id = team_name
    if civ =='All civs':
        civs = list_civs
    else:
        civs = [civ]
    if map != '"Map played"':
        map = "'"+map+"'"

    if div != '"Division"':
        div = "'"+div+"'"
    #use fstring to pass either column name or value as variable
    games = conn.execute(f'SELECT * FROM games WHERE ("Team A" = {team_id} OR "Team B" = {team_id}) AND ("Map played" = {map} ) AND ("Division" = {div} ) ').fetchall()
    #compute stats
    civ_data,total_game = get_civ_data_from_game(games,civs)
    conn.close()
    return render_template('civ_data.html', url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div,
                           team_mapping=team_mapping,civ_data = civ_data,total_game=total_game,list_civs=list_civs)

@app.route('/download_csv/<csv_type>', methods=['GET'])
def download_csv(csv_type):
    conn = get_db_connection('all')
    cursor = conn.cursor()
    try:
        if csv_type == 'games':
            # La table "games" contient des colonnes comme "Team A", "Team B", "Winner", "Map played", etc.
            cursor.execute("SELECT * FROM games")
            rows = cursor.fetchall()
            header = [col[0] for col in cursor.description]

        elif csv_type == 'teams':
            query = """
            SELECT 
                t.team_name AS team_name,
                group_concat(DISTINCT p.player_name) AS players,
                (
                    SELECT group_concat(map_info, ', ')
                    FROM (
                        SELECT g."Map played" || ' (' || COUNT(*) || ')' AS map_info
                        FROM team_games tg2
                        JOIN games g ON tg2.game_id = g.id
                        WHERE tg2.team_id = t.team_id
                        GROUP BY g."Map played"
                    )
                ) AS maps_played
            FROM teams t
            LEFT JOIN team_players tp ON t.team_id = tp.team_id
            LEFT JOIN players p ON tp.player_id = p.player_id
            GROUP BY t.team_name
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            header = [desc[0] for desc in cursor.description]

        elif csv_type == 'players':
            query = """
            SELECT 
                p.player_name AS player_name,
                t.team_name AS team_name,
                (
                    SELECT group_concat(civ_info, ', ')
                    FROM (
                        SELECT civ || ' (' || COUNT(*) || ')' AS civ_info
                        FROM (
                            SELECT "PlayerA1" AS player, "PickA1" AS civ FROM games
                            UNION ALL
                            SELECT "PlayerA2", "PickA2" FROM games
                            UNION ALL
                            SELECT "PlayerB1", "PickB1" FROM games
                            UNION ALL
                            SELECT "PlayerB2", "PickB2" FROM games
                            UNION ALL
                            SELECT "PlayerA3", "PickA3" FROM games
                            UNION ALL
                            SELECT "PlayerB3", "PickB3" FROM games
                            UNION ALL
                            SELECT "PlayerA4", "PickA4" FROM games
                            UNION ALL
                            SELECT "PlayerB4", "PickB4" FROM games
                        ) AS picks
                        WHERE picks.player = p.player_id
                        GROUP BY civ
                    )
                ) AS civ_picks
            FROM players p
            LEFT JOIN team_players tp ON p.player_id = tp.player_id
            LEFT JOIN teams t ON tp.team_id = t.team_id
            GROUP BY p.player_id, p.player_name, t.team_name
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            header = [desc[0] for desc in cursor.description]

        else:
            conn.close()
            return redirect(url_for('db_view'))

    except Exception as e:
        conn.close()
        return f"Erreur lors de la récupération des données pour {csv_type}: {e}"
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    csv_content = output.getvalue()
    output.close()

    # Ajout d'une marque BOM pour l'UTF-8 (utile pour Excel)
    csv_content = '\ufeff' + csv_content

    response = Response(csv_content, mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename={csv_type}.csv"
    return response






@app.route('/db_view', methods=['GET'])
def db_view():
    # On affiche des liens pour télécharger les différents CSV
    csv_options = {
        'games': 'Télécharger CSV des Games',
        'teams': 'Télécharger CSV des Équipes',
        'players': 'Télécharger CSV des Joueurs'
    }
    return render_template('db_view.html', csv_options=csv_options)


CATEGORIES_DICT = {"concepts": "CONCEPTS", "civilizations": "CIVILISATIONS & DIRIGEANTS", "citystates": "CITES ETATS",
                   "districts": "QUARTIERS", "buildings": "BATIMENTS", "wonders": "MERVEILLES & PROJETS",
                   "units": "UNITES", "unitpromotions": "PROMOTIONS D'UNITES", "greatpeople": "PERSONNAGES ILLUSTRES",
                   "technologies": "TECHNOLOGIES", "civics": "DOGMES", "governments": "GOUVERNEMENTS & DOCTRINES",
                   "religions": "RELIGIONS & CROYANCES",
                   "features": "TERRAINS, CARACTERISTIQUES & MERVEILLES NATURELLES",
                   "resources": "RESSSOURCES", "improvements": "AMENAGEMENTS", "governors": "GOUVERNEURS ET PROMOTIONS"}


# ---  Scraping ---
with open('daily_source.txt', 'r') as f:
    url = f.readline(-1)
category = CATEGORIES_DICT[url.split("/")[-2]]


def similarity(embd_1,embd_2):
    sim = float(np.dot(embd_1[0], embd_2[0]) / (embd_1[1] * embd_2[1] + 10e-7))
    return sim

# 🔁 Données initiales
with open("structured_text", "rb") as fp:   # Unpickling
    structured_text = pickle.load(fp)

with open("structured_title", "rb") as fp:   # Unpickling
    structured_title = pickle.load(fp)

with open("structured_text_embd", "rb") as fp:  # Unpickling
    structured_text_embd = pickle.load(fp)

with open("structured_title_embd", "rb") as fp:  # Unpickling
    structured_title_embd = pickle.load(fp)


nlp = None
@app.route('/civantix')
def civantix():
    global nlp
    if nlp is None:
        nlp = spacy.load("fr_core_news_lg")
    print('civantix')
    return render_template("civantix.html", title=structured_title, text=structured_text, clue=category)


def update_tokens(token_list,dico_embd, guess_token, guess_word, update):
    for i, entry in enumerate(token_list):
        if not entry.get("is_word") or entry.get("revealed"):
            continue
        score = similarity(dico_embd[entry["lower"]],(guess_token.vector,guess_token.vector_norm))
        if entry["lower"] == guess_word:
            entry["revealed"] = True
            entry["score"] = None
            if entry.get("is_title"):
                entry["guess"] = None
        elif score > 0.6:
            entry["guess"] = guess_word
            entry["score"] = score
        else:
            continue
        update.append({
            "section": "title" if entry.get("is_title") else "text",
            "index": i,
            "word": entry["word"] if entry["revealed"] else entry["guess"],
            "revealed": entry["revealed"],
            "score": entry.get("score", None)
        })
    return update

@app.route('/civantix/guess', methods=['POST'])
def guess():
    print('guess')
    global structured_title, structured_text, nlp
    if nlp is None:
        nlp = spacy.load("fr_core_news_lg")
    data = request.json

    current_guess_word = data.get("word", "").lower()

    if not current_guess_word:
        return jsonify({"status": "empty"})

    # Vérifie si déjà deviné
    all_words = [t for t in structured_title + structured_text if t.get("is_word")]

    # Vérifie si dans le texte
    in_text = any(t.get("lower") == current_guess_word for t in all_words)

    # Vérifie si dans le lexique du modèle spaCy
    in_vocab = nlp.vocab.has_vector(current_guess_word)

    if not in_text and not in_vocab:
        return jsonify({"status": "not_found"})

    updated = []



    current_guess_token = nlp(current_guess_word)
    updated = update_tokens(structured_title, structured_title_embd, current_guess_token, current_guess_word, updated)
    updated = update_tokens(structured_text, structured_text_embd, current_guess_token, current_guess_word, updated)

    victory = all(tok.get("revealed") for tok in structured_title if tok.get("is_word"))
    if victory:
        for i, token in enumerate(structured_title):
            if token.get("is_word") and not token.get("revealed"):
                token["revealed"] = True
                updated.append({
                    "section": "title",
                    "index": i,
                    "word": token["word"],
                    "revealed": True
                })
        for i, token in enumerate(structured_text):
            if token.get("is_word") and not token.get("revealed"):
                token["revealed"] = True
                updated.append({
                    "section": "text",
                    "index": i,
                    "word": token["word"],
                    "revealed": True
                })


    return jsonify({
        "updates": updated,
        "victory": victory,
        "status": "ok"
    })


@app.route('/civantix/giveup', methods=['POST'])
def give_up():
    print('give_up')
    global structured_title, structured_text
    updates = []

    def reveal_all(tokens, section):
        for i, token in enumerate(tokens):
            if token.get("is_word") and not token.get("revealed"):
                token["revealed"] = True
                updates.append({
                    "section": section,
                    "index": i,
                    "word": token["word"],
                    "revealed": True,
                    "score": None
                })

    reveal_all(structured_title, "title")
    reveal_all(structured_text, "text")

    return jsonify({"updates": updates, "victory": False})


@app.route('/civantix/reset')
def reset():
    print('reset')
    start = time.time()
    global structured_title, structured_text, structured_text_embd, structured_title_embd
    with open("structured_text", "rb") as fp:  # Unpickling
        structured_text = pickle.load(fp)

    with open("structured_title", "rb") as fp:  # Unpickling
        structured_title = pickle.load(fp)

    with open("structured_text_embd", "rb") as fp:  # Unpickling
        structured_text_embd = pickle.load(fp)

    with open("structured_title_embd", "rb") as fp:  # Unpickling
        structured_title_embd = pickle.load(fp)


    return redirect(url_for("civantix"))



# if __name__ == '__main__':
#   app.run()
