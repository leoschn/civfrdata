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


@app.route('/')
def index():
    conn = get_db_connection()
    games = conn.execute('SELECT * FROM games').fetchall()
    list_map = conn.execute('SELECT DISTINCT "Map played" FROM games').fetchall()
    list_team = conn.execute('SELECT DISTINCT "Team A" FROM games').fetchall()
    list_div = conn.execute('SELECT DISTINCT "Division" FROM games').fetchall()
    conn.close()
    return render_template('index_search_bar.html', games=games, url_civ=CIV_ASSETS_NAMES,
                           url_map=MAP_ASSETS_NAME,list_map=list_map, list_team=list_team, list_div=list_div)

@app.route('/<int:game_id>', methods=['GET', 'POST'])
def game(game_id):
    game = get_game(game_id)
    return render_template('games.html', game=game, url_civ=CIV_ASSETS_NAMES, url_map=MAP_ASSETS_NAME)


@app.route('/search', methods=['GET', 'POST'])
def search():
    team = request.form.get('team')
    map = request.form.get('map')
    div = request.form.get('div')
    print(map,team,div)
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
