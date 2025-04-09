from flask import Flask, render_template, request, jsonify, redirect, url_for
import re
import os
import requests
from bs4 import BeautifulSoup
import spacy
import regex
import numpy as np
import random

app = Flask(__name__)
nlp = spacy.load("fr_core_news_lg")

CATEGORIES_DICT =  {"concepts" : "CONCEPTS", "civilizations" : "CIVILISATIONS & DIRIGEANTS", "citystates" : "CITES ETATS",
                    "districts" : "QUARTIERS", "buildings" : "BATIMENTS", "wonders" : "MERVEILLES & PROJETS", 
                    "units" : "UNITES", "unitpromotions" : "PROMOTIONS D'UNITES", "greatpeople" : "PERSONNAGES ILLUSTRES",
                    "technologies" : "TECHNOLOGIES", "civics" : "DOGMES", "governments" : "GOUVERNEMENTS & DOCTRINES",
                    "religions" : "RELIGIONS & CROYANCES", "features" : "TERRAINS, CARACTERISTIQUES & MERVEILLES NATURELLES",
                    "resources" : "RESSSOURCES", "improvements" : "AMENAGEMENTS", "governors" : "GOUVERNEURS ET PROMOTIONS"}

# ---  Scraping ---
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

# Fonction pour charger les URL depuis le fichier
def load_sources_from_file(file_path): #fluk
    try:
        with open(os.path.join(os.path.dirname(__file__), "static", file_path), 'r', encoding='utf-8') as file:
            sources = file.readlines()
            # Nettoyer les URLs pour supprimer les espaces ou lignes vides
            sources = [url.strip() for url in sources if url.strip()]
            return sources
    except FileNotFoundError:
        print("Le fichier de sources n'a pas été trouvé.")
        return []

# Choisir une URL aléatoire
def get_random_source(): #fluk
    sources = load_sources_from_file("sources.txt")
    if sources:
        return random.choice(sources)
    else:
        return None
    
TITLE_CLASS = "App_pageHeaderText__SsfWm App_mainTextColor__6NGqD App_mainTextColor__6NGqD"
TEXT_CLASS = "Component_paragraphs__tSvTZ App_mainTextColor__6NGqD"
#url = get_random_source()  # Choisir une URL aléatoire dans sources.txt #fluk
url = "https://www.civilopedia.net/fr/gathering-storm/wonders/building_machu_picchu" #fluk
print(url)
category = CATEGORIES_DICT[url.split("/")[-2]]
    
# 🔁 Données initiales
def init_data():
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
    return structured_title, structured_text

# Stockage global (réinitialisable)
structured_title, structured_text = init_data()

@app.route('/')
def civantix():
    return render_template("civantix.html", title=structured_title, text=structured_text, clue=category)

@app.route('/guess', methods=['POST'])
def guess():
    global structured_title, structured_text
    data = request.json
    guess_word = data.get("word", "").lower()

    if not guess_word:
        return jsonify({"status": "empty"})

    # Vérifie si déjà deviné
    all_words = [t for t in structured_title + structured_text if t.get("is_word")]
    
    # Vérifie si dans le texte
    in_text = any(t.get("lower") == guess_word for t in all_words)

    # Vérifie si dans le lexique du modèle spaCy
    in_vocab = nlp.vocab.has_vector(guess_word)

    if not in_text and not in_vocab:
        return jsonify({"status": "not_found"})


    updated = []

    def update_tokens(token_list):
        nonlocal updated
        for i, entry in enumerate(token_list):
            if not entry.get("is_word") or entry.get("revealed"):
                continue
            score = nlp(entry["lower"]).similarity(nlp(guess_word))
            if entry["lower"] == guess_word:
                entry["revealed"] = True
                if entry.get("is_title"):
                    entry["guess"] = None
            elif score > 0.6:
                entry["guess"] = guess_word
                entry["score"] = score
            else:
                continue
            updated.append({
                "section": "title" if entry.get("is_title") else "text",
                "index": i,
                "word": entry["word"] if entry["revealed"] else entry["guess"],
                "revealed": entry["revealed"],
                "score": entry.get("score", None)
            })

    update_tokens(structured_title)
    update_tokens(structured_text)

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
    
@app.route('/giveup', methods=['POST'])
def give_up():
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

    return jsonify({ "updates": updates, "victory": False })

@app.route('/reset')
def reset():
    global structured_title, structured_text
    structured_title, structured_text = init_data()
    return redirect(url_for("civantix"))

if __name__ == '__main__':
    app.run(debug=True)
