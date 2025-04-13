import csv
import io
import sqlite3
from collections import defaultdict
from datetime import datetime
import time
import pickle

import numpy as np
import regex
import requests
import spacy
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
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
    ("soundiata", 'Sundiata_Keita_29.webp', "Sundiata"),
    ("tamar", 'Tamar_29.webp', "Tamar"),
    ("teddy roosevelt (bm)", 'Teddy_Roosevelt_29.webp', "Teddy Roosevelt (BM)"),
    ("teddy roosevelt (rough rider)", 'Teddy_Roosevelt_29_29.webp', "Teddy Roosevelt (Rough Rider)"),
    ("teddy rr", 'Teddy_Roosevelt_29_29.webp', "Teddy Roosevelt (RR)"),
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
    ("catherine de medici (manificence)", 'Catherine_de_Medici_29_29.webp', "Catherine de Medici (Magnificence)")
]

list_map_url = [
    ("pangaea standard", 'Map_Pangaea_29.webp', "Pangaea Standard"),
    ("seven seas", 'Map_Seven_Seas_29.webp', "Seven Seas"),
    ("rich highlands", 'Map_Highlands_29.webp', "Rich Highlands"),
    ("lakes", 'Map_Lakes_29.webp', "Lakes"),
    ("tilted axis", 'Map_Tilted_Axis_(Civ6).webp', "Tilted Axis"),
    ("primordial", 'Map_Primodial_29.webp', "Primordial"),
    ("inland sea", 'Map_Inland_Sea_29.webp', "Inland Sea")
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
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_game(game_id):
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE id = ?',
                        (game_id,)).fetchone()
    conn.close()
    if game is None:
        abort(404)

    return game

app = Flask(__name__)

def get_all_players():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    players = conn.execute('SELECT pseudo FROM players ORDER BY LOWER(pseudo) ASC').fetchall()
    conn.close()
    return players

def get_all_teams():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    teams = conn.execute('SELECT team_name, division FROM teams ORDER BY LOWER(team_name) ASC').fetchall()
    conn.close()
    return teams


def get_player_stats(player_name):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

   # Récupérer les informations du joueur dans la table players
    player_row = conn.execute(
        'SELECT * FROM players WHERE pseudo = ?', (player_name,)
    ).fetchone()
    if player_row is None:
        conn.close()
        return None  # Le joueur n'existe pas

    player_id = player_row['player_id']
    team = player_row['team']

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
            'SELECT * FROM games WHERE "index" = ?', (game_id,)
        ).fetchone()
        if game is None:
            continue

        found_slot = False
        # Vérifier si le joueur est dans l'équipe A
        for pos in ["1", "2", "3", "4"]:
            player_col = "PlayerA" + pos
            if game[player_col] and game[player_col].strip() == player_name:
                # Le joueur est dans l'équipe A
                opponent = game["Team B"].strip() if game["Team B"] else ""
                # Le résultat est "win" si Team A est gagnante, sinon "loss"
                result = "win" if game["Team A"] and game["Winner"] and game["Team A"].strip() == game["Winner"].strip() else "loss"
                date = game["Date"]
                if result == "win":
                    wins += 1
                civilization = game["PickA" + pos].strip() if game["PickA" + pos] else ""
                map_played = game["Map played"].strip() if game["Map played"] else ""

                # Récupérer le type et tour de victoire
                v_type = game['Victory']
                v_turn = game['Victory Turn']

                matches.append({
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
                if game[player_col] and game[player_col].strip() == player_name:
                    opponent = game["Team A"].strip() if game["Team A"] else ""
                    result = "win" if game["Team B"] and game["Winner"] and game["Team B"].strip() == game["Winner"].strip() else "loss"
                    date = game["Date"]
                    if result == "win":
                        wins += 1
                    civilization = game["PickB" + pos].strip() if game["PickB" + pos] else ""
                    map_played = game["Map played"].strip() if game["Map played"] else ""

                    # Récupérer le type et tour de victoire
                    v_type = game['Victory']
                    v_turn = game['Victory Turn']

                    matches.append({
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

    return {
        "pseudo": player_name,
        "team": team,
        "matches": matches,
        "total_games": total_games,
        "wins": wins,
        "winrate": winrate,
        "civilizations": civ_counts,
        "maps": map_counts
    }

def get_team_stats(team_name):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    # Récupérer tous les matchs où l'équipe est impliquée (Team A ou Team B)
    matches_query = """
      SELECT *
      FROM games
      WHERE "Team A" = ? OR "Team B" = ?
    """
    matches_data = conn.execute(matches_query, (team_name, team_name)).fetchall()

    matches = []
    wins = 0
    maps_counts = {}

    for game in matches_data:
        div = game["Division"]
        # On suppose que la colonne "Date" existe et contient la date du match.
        match_date = game["Date"] if "Date" in game.keys() else "N/A"
        # Identifier de quel côté se trouve l'équipe et déterminer l'opposant et le résultat.
        if game["Team A"].strip() == team_name:
            opponent = game["Team B"].strip() if game["Team B"] else ""
            result = "win" if game["Winner"] and game["Team A"].strip() == game["Winner"].strip() else "loss"
        elif game["Team B"].strip() == team_name:
            opponent = game["Team A"].strip() if game["Team A"] else ""
            result = "win" if game["Winner"] and game["Team B"].strip() == game["Winner"].strip() else "loss"
        else:
            continue  # Ce cas ne devrait pas se produire

        if result == "win":
            wins += 1

        # Récupérer la map jouée (colonne "Map played")
        map_played = game["Map played"].strip() if game["Map played"] else ""
        if map_played:
            maps_counts[map_played] = maps_counts.get(map_played, 0) + 1
        id = game["index"]

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
    players = conn.execute('SELECT * FROM players WHERE team = ?', (team_name,)).fetchall()
    conn.close()

    return {
        "team": team_name,
        "matches": matches,
        "total_games": total_games,
        "wins": wins,
        "winrate": winrate,
        "maps": maps_counts,
        "players": players,
        "division": div,
        "loses": loses,
    }

def get_minimal_team_stats(team_name):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    # Récupérer tous les matchs où l'équipe est impliquée (Team A ou Team B)
    matches_query = """
      SELECT *
      FROM games
      WHERE "Team A" = ? OR "Team B" = ?
    """
    matches_data = conn.execute(matches_query, (team_name, team_name)).fetchall()

    wins = 0
    loses = 0

    for game in matches_data:
        div = game["Division"]
        # Identifier de quel côté se trouve l'équipe et déterminer l'opposant et le résultat.
        if game["Team A"].strip() == team_name:
            opponent = game["Team B"].strip() if game["Team B"] else ""
            result = "win" if game["Winner"] and game["Team A"].strip() == game["Winner"].strip() else "loss"
        elif game["Team B"].strip() == team_name:
            opponent = game["Team A"].strip() if game["Team A"] else ""
            result = "win" if game["Winner"] and game["Team B"].strip() == game["Winner"].strip() else "loss"
        else:
            continue  # Ce cas ne devrait pas se produire

        if result == "win":
            wins += 1
        if result == "loss":
            loses += 1


    total_games = len(matches_data)


    return {
        "team": team_name,
        "total_games": total_games,
        "wins": wins,
        "loses": loses,
        "win_rate": wins/total_games,
    }


@app.route('/')
def landingpage():
    teams = get_all_teams()
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
            stats = get_minimal_team_stats(team['team_name'])
            team["wins"] = stats["wins"]
            team["loses"] = stats["loses"]
            team["total_games"] = stats["total_games"]

        sorted_teams = sorted(team_list, key=lambda t: int(t.get("wins", 0)), reverse=True)
        for rank, team in enumerate(sorted_teams, start=1):
            team["ranking"] = rank

        divisions[div] = sorted_teams

    # Optionnel : définir l'ordre des divisions à afficher (par exemple, 1, 2, 3a, 3b)
    order = ['1', '2', '3a', '3b']

    return render_template('landingpage.html', divisions=divisions, order=order)

@app.route('/data')
def index():
    conn = get_db_connection()
    games = conn.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT DISTINCT "Team A" FROM games').fetchall()
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()
    conn.close()
    # tri des games par date, décroissant
    games = sorted(games, key=lambda game: datetime.strptime(game['Date'], '%d/%m/%y'), reverse=True)
    return render_template('index_search_bar.html', games=games, url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div)


@app.route('/games/<int:game_id>', methods=['GET', 'POST'])
def game(game_id):
    game = get_game(game_id)
    return render_template('games.html', game=game, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME)

@app.route('/player')
def player_list():
    players = get_all_players()
    return render_template('player_list.html', players=players)

@app.route('/team')
def team_list():
    teams = get_all_teams()
    return render_template('team_list.html', teams=teams)

@app.route('/player/<player_name>')
def player_details(player_name):
    # Récupère toutes les infos détaillées du joueur
    player = get_player_stats(player_name)
    if player is None:
        abort(404)
    return render_template('player.html', player=player,url_civ=CIV_ASSETS_NAMES, display_civ=CIV_DISPLAY_NAMES,
                           url_map=MAP_ASSETS_NAME, display_map=MAP_DISPLAY_NAMES)

@app.route('/team/<team_name>')
def team_details(team_name):
    team = get_team_stats(team_name)
    if team is None:
        abort(404)
    return render_template('team.html', team=team, url_civ=CIV_ASSETS_NAMES, display_civ=CIV_DISPLAY_NAMES,
                           url_map=MAP_ASSETS_NAME, display_map=MAP_DISPLAY_NAMES)



@app.route('/search', methods=['GET', 'POST'])
def search():
    team = request.form.get('team')
    map = request.form.get('map')
    div = request.form.get('div')
    conn = get_db_connection()
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT DISTINCT "Team A" FROM games').fetchall()
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()


    if map == 'None' and div=='None' and team=='None':
        games = conn.execute('SELECT * FROM games ').fetchall()
    elif map == 'None' and div=='None':
        games = conn.execute('SELECT * FROM games WHERE ("Team A" = ? OR "Team B" = ?)',(team,team)).fetchall()
    elif team == 'None' and div=='None':
        games = conn.execute('SELECT * FROM games WHERE ("Map played" = ? )', (map,)).fetchall()
    elif team == 'None' and map =='None':
        games = conn.execute('SELECT * FROM games WHERE ("Division" = ? )', (div,)).fetchall()
    elif div == 'None':
        games = conn.execute('SELECT * FROM games WHERE ("Team A" = ? OR "Team B" = ?) AND ("Map played" = ? )', (team,team,map,)).fetchall()
    elif team =='None':
        games = conn.execute('SELECT * FROM games WHERE ("Map played" = ? ) AND ("Division" = ? )', (map,div,)).fetchall()
    elif map =='None':
        games = conn.execute('SELECT * FROM games WHERE  ("Team A" = ? OR "Team B" = ?) AND ("Division" = ? )', (team,team,div,)).fetchall()
    else :
        games = conn.execute('SELECT * FROM games WHERE ("Team A" = ? OR "Team B" = ?) AND ("Map played" = ? ) AND ("Division" = ? )', (team, team, map, div)).fetchall()
    conn.close()
    games = sorted(games, key=lambda game: datetime.strptime(game['Date'], '%d/%m/%y'), reverse=True)
    return render_template('index.html', games=games,url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME, list_map=list_map, list_team=list_team, list_div=list_div)


@app.route('/download_csv/<csv_type>', methods=['GET'])
def download_csv(csv_type):
    conn = get_db_connection()
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
                group_concat(DISTINCT p.pseudo) AS players,
                (
                    SELECT group_concat(map_info, ', ')
                    FROM (
                        SELECT g."Map played" || ' (' || COUNT(*) || ')' AS map_info
                        FROM team_games tg2
                        JOIN games g ON tg2.game_id = g.id
                        WHERE tg2.team_name = t.team_name
                        GROUP BY g."Map played"
                    )
                ) AS maps_played
            FROM teams t
            LEFT JOIN team_players tp ON t.team_name = tp.team_name
            LEFT JOIN players p ON tp.player_id = p.player_id
            GROUP BY t.team_name
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            header = [desc[0] for desc in cursor.description]

        elif csv_type == 'players':
            query = """
            SELECT 
                p.pseudo AS player_name,
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
                        WHERE picks.player = p.pseudo
                        GROUP BY civ
                    )
                ) AS civ_picks
            FROM players p
            LEFT JOIN team_players tp ON p.player_id = tp.player_id
            LEFT JOIN teams t ON tp.team_name = t.team_name
            GROUP BY p.player_id, p.pseudo, t.team_name
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

#
nlp = spacy.load("fr_core_news_lg")

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
print(url)
category = CATEGORIES_DICT[url.split("/")[-2]]


def similarity(embd_1,embd_2):
    sim = np.dot(embd_1[0], embd_2[0]) / (embd_1[1] * embd_2[1] + 10e-7)
    return sim

# 🔁 Données initiales
def load_structured_data():
    with open("structured_text", "rb") as fp:
        structured_text = pickle.load(fp)
    with open("structured_title", "rb") as fp:
        structured_title = pickle.load(fp)
    with open("structured_text_embd", "rb") as fp:
        structured_text_embd = pickle.load(fp)
    with open("structured_title_embd", "rb") as fp:
        structured_title_embd = pickle.load(fp)
    return structured_title, structured_text, structured_title_embd, structured_text_embd


@app.before_request
def before_request():
    g.structured_title, g.structured_text, g.structured_title_embd, g.structured_text_embd = load_structured_data()

@app.route('/civantix')
def civantix():
    print('civantix')
    return render_template("civantix.html", title=g.structured_title, text=g.structured_text, clue=category)


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
    data = request.json
    with open('log_data.txt', 'a') as f:
        f.write(data.__repr__())
        f.write('\n')
    current_guess_word = data.get("word", "").lower()

    if not current_guess_word:
        return jsonify({"status": "empty"})

    # Vérifie si déjà deviné
    all_words = [t for t in g.structured_title + g.structured_text if t.get("is_word")]

    # Vérifie si dans le texte
    in_text = any(t.get("lower") == current_guess_word for t in all_words)

    # Vérifie si dans le lexique du modèle spaCy
    in_vocab = nlp.vocab.has_vector(current_guess_word)

    if not in_text and not in_vocab:
        return jsonify({"status": "not_found"})

    updated = []



    current_guess_token = nlp(current_guess_word)
    updated = update_tokens(g.structured_title, g.structured_title_embd, current_guess_token, current_guess_word, updated)
    updated = update_tokens(g.structured_text, g.structured_text_embd, current_guess_token, current_guess_word, updated)

    victory = all(tok.get("revealed") for tok in g.structured_title if tok.get("is_word"))
    if victory:
        for i, token in enumerate(g.structured_title):
            if token.get("is_word") and not token.get("revealed"):
                token["revealed"] = True
                updated.append({
                    "section": "title",
                    "index": i,
                    "word": token["word"],
                    "revealed": True
                })
        for i, token in enumerate(g.structured_text):
            if token.get("is_word") and not token.get("revealed"):
                token["revealed"] = True
                updated.append({
                    "section": "text",
                    "index": i,
                    "word": token["word"],
                    "revealed": True
                })
    with open('log_update.txt', 'a') as f:
        f.write('Update\n')
        f.write(updated.__repr__())
        f.write('\n')
        f.write('victory\n')
        f.write(victory.__repr__())



    return jsonify({
        "updates": updated,
        "victory": victory,
        "status": "ok"
    })


@app.route('/civantix/giveup', methods=['POST'])
def give_up():
    print('give_up')
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

    reveal_all(g.structured_title, "title")
    reveal_all(g.structured_text, "text")

    return jsonify({"updates": updates, "victory": False})


@app.route('/civantix/reset')
def reset():
    print('reset')
    g.structured_title, g.structured_text, g.structured_title_embd, g.structured_text_embd = load_structured_data()
    return redirect(url_for("civantix"))

@app.route('/civantix/log_error', methods=['POST'])
def log_error():
    log = request.json

    with open('log_error.txt', 'a') as f:
        f.write(log.__repr__())
        f.write('\n')


# if __name__ == '__main__':
#   app.run()
