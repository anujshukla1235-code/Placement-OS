import json
import pathlib
import re

BASE = pathlib.Path(__file__).parent
with open(BASE / "skills_dictionary.json") as f:
    SKILLS = [s.lower() for s in json.load(f)]


def normalize(t):
    return re.sub(r"[^a-z0-9+.# ]", " ", t.lower())


def extract_skills(text):
    if not text:
        return []
    nt = normalize(text)
    found = []
    for skill in SKILLS:
        # handle multi-word
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, nt):
            found.append(skill)
        else:
            # fuzzy for variants like react.js -> react
            if skill in nt:
                found.append(skill)
    return list(set(found))
