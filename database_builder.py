import os
import sqlite3

def add_new_tables_to_db(db_file):
    # Connexion à la base de données source (contenant la table "games")
    conn = sqlite3.connect(db_file)
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
    print(f"Nouvelles tables ajoutées dans '{db_file}' : {len(players_dict)} joueurs et {len(teams_dict)} équipes.")

if __name__ == '__main__':
    script_path = os.path.abspath(__file__)
    path_list = script_path.split(os.sep)
    script_directory = path_list[0:len(path_list) - 1]
    rel_path = "database.db"
    path = "/".join(script_directory) + "/" + rel_path # Nom de votre base de données initiale
    add_new_tables_to_db(path)
