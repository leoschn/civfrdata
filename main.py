import sqlite3
from flask import Flask, render_template, url_for, request
from werkzeug.exceptions import abort
from collections import defaultdict

list_civ_url = [("abraham lincoln", 'Abraham_Lincoln_29.webp'),
    ("alexander", 'Alexander_29.webp'),
    ("amanitore", 'Amanitore_29.webp'),
    ("ambiorix", 'Ambiorix_29.webp'),
    ("basil ii", 'Basil_II_29.webp'),
    ("ba trieu", 'B3Fu_29.webp'),
    ("catherine de medici (black queen)", 'Catherine_de_Medici_29.webp'),
    ("chandragupta", 'Chandragupta_29.webp'),
    ("cleopatra (egyptian)", 'Cleopatra_29.webp'),
    ("cyrus", 'Cyrus_29.webp'),
    ("dido", 'Dido_29.webp'),
    ("eleanor of aquitaine (england)", 'Eleanor_of_Aquitaine_29_29.webp'),
    ("eleanor of aquitaine (france)", 'Eleanor_of_Aquitaine_29_29_fr.webp'),
    ("elizabeth i", 'Elizabeth_I_29.webp'),
    ("frederick barbarossa", 'Frederick_Barbarossa_29.webp'),
    ("gandhi", 'Gandhi_29.webp'),
    ("genghis khan", 'Genghis_Khan_29.webp'),
    ("gilgamesh", 'Gilgamesh_29.webp'),
    ("gitarja", 'Gitarja_29.webp'),
    ("gorgo", 'Gorgo_29.webp'),
    ("hammurabi", 'Hammurabi_29.webp'),
    ("harald hardrada", 'Harald_Hardrada_29.webp'),
    ("hojo tokimune", 'Hojo_Tokimune_29.webp'),
    ("jadwiga", 'Jadwiga_29.webp'),
    ("jaravarman vii", 'Jayavarman_VII_29.webp'),
    ("joao iii", 'Jo_29.webp'),
    ("john curtin", 'John_Curtin_29.webp'),
    ("julius caesar", 'Julius_Caesar_29.webp'),
    ("kristina", 'Kristina_29.webp'),
    ("kublai khan (china)", 'Kublai_Khan_29_29.webp'),
    ("kublai khan (mongolia)", 'Kublai_Khan_29_29_mong.webp'),
    ("kupe", 'Kupe_29.webp'),
    ("lady six sky", 'Lady_Six_Sky_29.webp'),
    ("lautaro", 'Lautaro_29.webp'),
    ("ludwig ii", 'Ludwig_II_29.webp'),
    ("mansa musa", 'Mansa_Musa_29.webp'),
    ("matthias corvinus", 'Matthias_Corvinus_29.webp'),
    ("menelik ii", 'Menelik_II_29.webp'),
    ("montezuma", 'Montezuma_29.webp'),
    ("mvemba a nzinga", 'Mvemba_a_Nzinga_29.webp'),
    ("nader shah", 'Nader_Shah_29.webp'),
    ("nzinga mbande", 'Nzinga_Mbande_29.webp'),
    ("pachacuti", 'Pachacuti_29.webp'),
    ("pedro ii", 'Pedro_II_29.webp'),
    ("pericles", 'Pericles_29.webp'),
    ("peter", 'Peter_29.webp'),
    ("philip ii", 'Philip_II_29.webp'),
    ("poundmaker", 'Poundmaker_29.webp'),
    ("qin (mandate of heaven)", 'Qin_Shi_Huang_29.webp'),
    ("qin (unifier)", 'Qin_Shi_Huang_29_29.webp'),
    ("ramses ii", 'Ramses_II_29.webp'),
    ("robert the bruce", 'Robert_the_Bruce_29.webp'),
    ("saladin (sultan)", 'Saladin_29_29.webp'),
    ("saladin (vizier)", 'Saladin_29.webp'),
    ("sejong", 'Sejong_29.webp'),
    ("seondeok", 'Seondeok_29.webp'),
    ("shaka", 'Shaka_29.webp'),
    ("simon bolivar", 'Sim3Fvar_29.webp'),
    ("suleiman (muhtesem)", 'Suleiman_29_29.webp'),
    ("suleiman (kanuni)", 'Suleiman_29.webp'),
    ("soundiata keita", 'Sundiata_Keita_29.webp'),
    ("soundiata", 'Sundiata_Keita_29.webp'),
    ("tamar", 'Tamar_29.webp'),
    ("teddy roosevelt (bm)", 'Teddy_Roosevelt_29.webp'),
    ("teddy roosevelt (rough rider)", 'Teddy_Roosevelt_29_29.webp'),
    ("teddy rr", 'Teddy_Roosevelt_29_29.webp'),
    ("theodora", 'Theodora_29.webp'),
    ("tokugawa", 'Tokugawa_29.webp'),
    ("tomyris", 'Tomyris_29.webp'),
    ("trajan", 'Trajan_29.webp'),
    ("victoria", 'Victoria_29.webp'),
    ("victoria age of steam", 'Victoria_29_29.webp'),
    ("wilfred laurier", 'Wilfrid_Laurier_29.webp'),
    ("wilhelmina", 'Wilhelmina_29.webp'),
    ("wu zetian", 'Wu_Zetian_29.webp'),
    ("yongle", 'Yongle_29.webp'),
    ("harald varangian", 'Harald_Hardrada_29_29.webp'),
    ("cleopatra (ptolemaic)", 'Cleopatra_29_29.webp'),
    ("catherine de medici (manificence)", 'Catherine_de_Medici_29_29.webp')]


list_map_url=[("pangaea standard", 'Map_Pangaea_29.webp'),
    ("seven seas", 'Map_Seven_Seas_29.webp'),
    ("rich highlands", 'Map_Highlands_29.webp'),
    ("lakes", 'Map_Lakes_29.webp'),
    ("tilted axis", 'Map_Tilted_Axis_(Civ6).webp'),
    ("primordial", 'Map_Primodial_29.webp'),
    ("inland sea", 'Map_Inland_Sea_29.webp')]

list_map_name = [x for (x,y) in list_map_url]

CIV_ASSETS_NAMES = defaultdict(lambda :'../static/assets/unknown-18-512.png')
for k, v in list_civ_url:
    CIV_ASSETS_NAMES[k]='../static/assets/'+v

MAP_ASSETS_NAME = defaultdict(lambda :'../static/assets/unknown-18-512.png')
for k, v in list_map_url:
    MAP_ASSETS_NAME[k]='../static/assets/'+v

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
    players = conn.execute('SELECT pseudo FROM players ORDER BY pseudo ASC').fetchall()
    conn.close()
    return players

def get_all_teams():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    teams = conn.execute('SELECT team_name, division FROM teams ORDER BY team_name ASC').fetchall()
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
                matches.append({
                    "opponent": opponent,
                    "result": result,
                    "civilization": civilization,
                    "map": map_played,
                    "date": date,
                    "id": game_id
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
                    matches.append({
                        "opponent": opponent,
                        "result": result,
                        "civilization": civilization,
                        "map": map_played,
                        "date": date,
                        "id": game_id
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

        matches.append({
            "opponent": opponent,
            "result": result,
            "date": match_date,
            "map": map_played,
            "id": id
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


            print(f"Équipe {team['team_name']} en division {div} a { team["wins"]} victoires. Rang: {rank}")
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
    return render_template('player.html', player=player, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME)

@app.route('/team/<team_name>')
def team_details(team_name):
    team = get_team_stats(team_name)
    if team is None:
        abort(404)
    return render_template('team.html', team=team, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME)



@app.route('/search', methods=['GET', 'POST'])
def search():
    team = request.form.get('team')
    map = request.form.get('map')
    div = request.form.get('div')
    conn = get_db_connection()
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
    return render_template('index.html', games=games, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME)

if __name__ == '__main__':
  app.run()
