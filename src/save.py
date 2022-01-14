#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import yaml
import sqlite3 as sql

DATA_DATABASE_LOCATION = "res/game_data.db"
SAVE_DATABASE_LOCATION = "sav/save.db"

CONFIGURATION_FILES = {
    "player" : "sav/player.yaml",
    "window" : "stg/window.yaml",
    "objects" : "sav/objects.yaml",
    "controls" : "stg/controls.yaml"
    }

DEFAULT_CONFIG = {
    "player" : {"map_id" : 1, "position" : [1600,1200], "speed" : 1.5},
    "window" : {"size" : (1000, 600), "fullscreen" : False},
    "controls" : {
        # Contrôle du mouvement
        "PLAYER_MOVE_UP" : "UP",
        "PLAYER_MOVE_DOWN" : "DOWN",
        "PLAYER_MOVE_LEFT" : "LEFT",
        "PLAYER_MOVE_RIGHT" : "RIGHT",
        "PLAYER_SPRINT" : "LEFT CTRL",
        "PLAYER_SPRINT_SEC" : "RIGHT CTRL",

        # Contrôle des mécanismes du jeu
        "ACTION_INTERACT" : "SPACE",

        # Contrôle des menus
        "MENU_SHOW_SIDEBAR" : "LEFT SHIFT",
        "MENU_MOVE_UP" : "UP",
        "MENU_MOVE_DOWN" : "DOWN",
        "MENU_MOVE_LEFT" : "LEFT",
        "MENU_MOVE_RIGHT" : "RIGHT",
        "MENU_INTERACT" : "SPACE",
        "MENU_CANCEL" : "x",

        # Contrôle de la fenêtre
        "GAME_FULLSCREEN" : "F11",
        "GAME_TERMINATE" : "ESCAPE",

        # Debug du jeu
        "DEBUG" : "F3",
        "RESET_CONFIG" : "F5",
        "RESET_SAVE" : "F6"
        },
    "objects" : {1 : True} # Temporaire
    }


def load_config(object):
    """Charge une configuration YAML"""
    try:
        with open(CONFIGURATION_FILES[object], 'r') as file:
            config = yaml.load(file, Loader = yaml.FullLoader)
        return config
    except FileNotFoundError: # Cas où le fichier n'existe pas
        create_default_config(object)
        return load_config(object)

def create_default_config(object):
    """Créé le fichier avec une configuration par défaut"""
    config = DEFAULT_CONFIG[object]
    with open(CONFIGURATION_FILES[object], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def save_config(object, **args):
    """Sauvegarde en modifiant les données passées en paramètres"""
    try:
        config = load_config(object)
    except FileNotFoundError:
        print("Impossible d'accéder au fichier de {} lors de la sauvegarde. Cela peut être dû à une réinitialisation des données...".format(object))
        return
    for arg in args.items():
        config[arg[0]] = arg[1]
    with open(CONFIGURATION_FILES[object], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def init_save_database():
    """Création du fichier de sauvegarde"""
    data_db = sql.connect(DATA_DATABASE_LOCATION)
    map_list = data_db.cursor().execute('select id from maps;').fetchall()
    save_db = sql.connect(SAVE_DATABASE_LOCATION)
    save_db.cursor().execute('CREATE TABLE IF NOT EXISTS "bag" ("id_item" INTEGER NOT NULL PRIMARY KEY, "quantity" INTEGER NOT NULL)')
    save_db.cursor().execute('create table if not exists "mapscripts" ("map_id" integer not null primary key,\
                                                                  "marked" integer not null);')
    if save_db.cursor().execute('select * from mapscripts;') == []:
        for map in map_list:
            save_db.cursor().execute('insert into mapscripts values (?, 0);', (map[0],))
    
    data_db.close()
    return save_db
