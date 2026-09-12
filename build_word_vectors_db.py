"""
One-time offline export of spaCy's fr_core_news_lg word vectors into a static
SQLite database, so the live Flask app (main.py) never has to load spaCy at
request time for the civantix guessing game.

Run once (not part of the daily cron job):
    .venv/bin/python build_word_vectors_db.py

Produces word_vectors.db with a single table:
    vectors(word TEXT PRIMARY KEY, vector BLOB, norm REAL)
  - vector: 300 float32s, packed via numpy.tobytes() (little-endian)
  - norm:   precomputed L2 norm of the vector (avoids recomputing per guess)

Only lowercase entries are kept, since the live app always lowercases the
guessed word before lookup (`data.get("word", "").lower()`), so uppercase /
mixed-case vocab entries would never be queried.

The model's vectors are static (pinned to fr_core_news_lg==3.8.0), so this
only needs to be re-run if the model is ever upgraded.
"""
import sqlite3
import time

import numpy as np
import spacy

DB_PATH = "word_vectors.db"

print("Loading fr_core_news_lg (vectors only, no tagger/parser/ner)...")
t0 = time.time()
nlp = spacy.load(
    "fr_core_news_lg",
    exclude=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler", "morphologizer"],
)
print(f"  loaded in {time.time() - t0:.1f}s")

conn = sqlite3.connect(DB_PATH)
conn.execute("DROP TABLE IF EXISTS vectors")
conn.execute(
    "CREATE TABLE vectors (word TEXT PRIMARY KEY, vector BLOB NOT NULL, norm REAL NOT NULL)"
)

t0 = time.time()
rows = []
total = 0
kept = 0
for key in nlp.vocab.vectors.keys():
    total += 1
    word = nlp.vocab.strings[key]
    if not word.islower():
        continue
    vec = np.asarray(nlp.vocab.vectors[key], dtype=np.float32)
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        continue
    rows.append((word, vec.tobytes(), norm))
    kept += 1
    if len(rows) >= 5000:
        conn.executemany("INSERT OR REPLACE INTO vectors VALUES (?, ?, ?)", rows)
        rows = []

if rows:
    conn.executemany("INSERT OR REPLACE INTO vectors VALUES (?, ?, ?)", rows)

conn.commit()
conn.execute("VACUUM")
conn.close()

print(f"  processed {total} vocab entries, kept {kept} lowercase entries in {time.time() - t0:.1f}s")
print(f"Wrote {DB_PATH}")
