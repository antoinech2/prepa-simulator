"""
Gestion des lignes de texte
"""

import yaml

CURRENT_LANGUAGE = "fr"
LOCALE_DIR = f"res/locale/{CURRENT_LANGUAGE}/"

def get_dir():
    """Retourne l'emplacement des fichiers de traduction"""
    return(LOCALE_DIR)


def get_string(file, str_id):
    with open(f"{LOCALE_DIR}{file}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings[str_id])


def getstring_dialogue(str_id):
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings["dialogue"][str_id])

def getstring_infobox(str_id):
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings["infobox"][str_id])

def getstring_system(str_id):
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings["system"][str_id])