"""
Gestion des lignes de texte
"""

import yaml

LOCALE_DIR = "res/locale/"
CURRENT_LANGUAGE = "fr"

def getstring_dialogue(str_id):
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings["dialogue"][str_id])

def getstring_infobox(str_id):
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings["infobox"][str_id])