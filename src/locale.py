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

def get_substring(section, str_id):
    """Obtention de la chaîne de caractères d'une section du fichier locale"""
    with open(f"{LOCALE_DIR}{CURRENT_LANGUAGE}.yaml", 'r', encoding = "utf-8") as file:
        strings = yaml.load(file, Loader = yaml.FullLoader)
    return(strings[section][str_id])