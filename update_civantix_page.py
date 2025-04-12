import os
import pickle
import random
import regex
import requests
import spacy
from bs4 import BeautifulSoup

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-1]
base_path =  "/".join(script_directory) + "/"

nlp = spacy.load("fr_core_news_lg")

CATEGORIES_DICT = {"concepts": "CONCEPTS", "civilizations": "CIVILISATIONS & DIRIGEANTS", "citystates": "CITES ETATS",
                   "districts": "QUARTIERS", "buildings": "BATIMENTS", "wonders": "MERVEILLES & PROJETS",
                   "units": "UNITES", "unitpromotions": "PROMOTIONS D'UNITES", "greatpeople": "PERSONNAGES ILLUSTRES",
                   "technologies": "TECHNOLOGIES", "civics": "DOGMES", "governments": "GOUVERNEMENTS & DOCTRINES",
                   "religions": "RELIGIONS & CROYANCES",
                   "features": "TERRAINS, CARACTERISTIQUES & MERVEILLES NATURELLES",
                   "resources": "RESSSOURCES", "improvements": "AMENAGEMENTS", "governors": "GOUVERNEURS ET PROMOTIONS"}

TITLE_CLASS = "App_pageHeaderText__SsfWm App_mainTextColor__6NGqD App_mainTextColor__6NGqD"
TEXT_CLASS = "Component_paragraphs__tSvTZ App_mainTextColor__6NGqD"

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

def load_data_from_url(url, title_class, text_class):
    response = requests.get(url)
    if not response.ok:
        return "", ""

    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(class_=text_class)
    if not elements:
        return "", ""

    last_element = elements[-1]
    full_text = last_element.get_text(separator=" ", strip=True)

    # Utiliser spaCy pour diviser le texte en phrases
    doc = nlp(full_text)

    # Récupérer les 5 premières phrases
    sentences = [sent.text for sent in doc.sents][:6]

    # Rejoindre les 5 phrases en un seul bloc de texte
    limited_text = " ".join(sentences)

    title = soup.find_all(class_=title_class)[0].get_text(separator=" ", strip=True)

    return title, limited_text

def get_random_source(): #fluk
    sources = load_sources_from_file(base_path+"sources.txt")
    if sources:
        return random.choice(sources)
    else:
        return None



def init_token(token_list):
    dico_embd = {}
    for i, token in enumerate(token_list):
        if not token["is_word"]:
            continue
        emb_d = nlp(token["lower"])
        dico_embd[token["lower"]] = (emb_d.vector,emb_d.vector_norm)
    return dico_embd

def init_data(url):
    title, text = load_data_from_url(url, TITLE_CLASS, TEXT_CLASS)

    # Pour conserver majuscules et ponctuation
    full_title_tokens = regex.findall(r'\p{L}+|\p{P}+|\p{N}+', title)
    full_text_tokens = regex.findall(r'\p{L}+|\p{P}+|\p{N}+', text)

    def process_tokens(tokens, is_title=False):
        result = []
        for tok in tokens:
            if regex.match(r'\p{L}+|\p{N}+', tok):
                result.append({
                    "word": tok,
                    "lower": tok.lower(),
                    "is_word": True,
                    "is_title": is_title,
                    "revealed": False,
                    "guess": None
                })
            else:
                result.append({
                    "word": tok,
                    "is_word": False
                })
        return result

    structured_title = process_tokens(full_title_tokens, is_title=True)
    structured_text = process_tokens(full_text_tokens, is_title=False)

    structured_text_embd = init_token(structured_text)
    structured_title_embd = init_token(structured_title)

    with open("structured_text", 'wb') as f:
        pickle.dump(structured_text, f)

    with open("structured_title", 'wb') as f:
        pickle.dump(structured_title, f)

    with open("structured_text_embd", 'wb') as f:
        pickle.dump(structured_text_embd, f)

    with open("structured_title_embd", 'wb') as f:
        pickle.dump(structured_title_embd, f)

new_source = get_random_source()

with open(base_path+'daily_source.txt', 'w') as f:
    f.write(new_source)

with open(base_path+'daily_source.txt', 'r') as f:
    url = f.readline(-1)

# Stockage global (réinitialisable)
init_data(url)




