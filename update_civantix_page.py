import os
import random

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-1]
base_path =  "/".join(script_directory) + "/"


# Fonction pour charger les URL depuis le fichier
def load_sources_from_file(file_path): #fluk
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sources = file.readlines()
            # Nettoyer les URLs pour supprimer les espaces ou lignes vides
            sources = [url.strip() for url in sources if url.strip()]
            return sources
    except FileNotFoundError:
        print("Le fichier de sources n'a pas été trouvé.")
        return []

def get_random_source(): #fluk
    sources = load_sources_from_file("sources.txt")
    if sources:
        return random.choice(sources)
    else:
        return None

new_source = get_random_source()

with open('daily_source.txt','w') as f:
    f.write(new_source)
