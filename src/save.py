#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import yaml
import sqlite3 as sql

DATA_DATABASE_LOCATION = "res/game_data.db"
SAVE_DATABASE_LOCATION = "sav/save.db"

CONFIGURATION_FILES = {
    "entities" : "sav/entities.yaml",
    "window" : "stg/window.yaml",
    "controls" : "stg/controls.yaml",
    "internals" : "sav/internals.yaml"
    }

DEFAULT_CONFIG = {
    "entities" : {"player":                 #TODO Ajouter un dictionnaire de valeurs pour chaque PNJ (position seulement)
                    {"map_id" : 1,
                    "position" : [1600,1200],
                    "speed" : 1.85,
                    "stamina" : 300,
                    "cash" : 10.}
                 },
                 
    "window" : {"size" : (1280, 720),
                "fullscreen" : False},

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

        # Contrôle des mini-jeux
        "MINIGAME_UP" : "UP",
        "MINIGAME_DOWN" : "DOWN",
        "MINIGAME_LEFT" : "LEFT",
        "MINIGAME_RIGHT" : "RIGHT",
        "MINIGAME_ENTER" : "RETURN",

        # Contrôle de la fenêtre
        "GAME_FULLSCREEN" : "F11",
        "GAME_TERMINATE" : "ESCAPE",

        # Debug du jeu
        "DEBUG" : "F3",
        "RESET_CONFIG" : "F5",
        "RESET_SAVE" : "F6"
        },

    "internals" : {"ticks" : 0,
                   "day" : 0,
                   "hour" : 7,
                   "minute" : 0},
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
    npc_list = data_db.cursor().execute('select * from npc;').fetchall()
    mapobj_list = data_db.cursor().execute('select id from objects;').fetchall()
    mission_list = data_db.cursor().execute('select id from missions;').fetchall()
    save_db = sql.connect(SAVE_DATABASE_LOCATION)
    save_db.cursor().execute('CREATE TABLE IF NOT EXISTS "bag" ("id_item" INTEGER NOT NULL PRIMARY KEY, "quantity" INTEGER NOT NULL)')
    save_db.cursor().execute('create table if not exists "maps" ("map_id" integer not null primary key,\
                                                                 "mapscript_triggered" integer not null,\
                                                                 "flags" text);')
    save_db.cursor().execute('create table if not exists "npc" ("npc_id" integer not null primary key,\
                                                                "flags" text);')
    save_db.cursor().execute('create table if not exists "mapobjects" ("mapobj_id" integer not null primary key,\
                                                                       "obtained" integer);')
    save_db.cursor().execute('create table if not exists "events" ("tag" text not null primary key,\
                                                                   "state" integer);')
    save_db.cursor().execute('create table if not exists "missions" ("id" integer not null primary key,\
                                                                     "status" integer,\
                                                                     "adv" integer);')

    # Création de la sauvegarde des maps
    if save_db.cursor().execute('select * from maps;').fetchall() == []:
        for map in map_list:
            save_db.cursor().execute('insert into maps values (?, 0, "[0,0,0,0]");', (map[0],)) # Temporaire : 4 flags par map
                                                                                              # Proposition : passer en binaire (ordre des flags inversé, l'état "flags 3 et 1 levés" est alors symbolisé par l'entier 10)
    # Création de la sauvegarde des PNJ
    if save_db.cursor().execute('select * from npc;').fetchall() == []:
        for npc in npc_list:
            save_db.cursor().execute('insert into npc values (?, "[0,0,0,0]");', (npc[0],))     # Même proposition
    # Création de la sauvegarde des objets sur la carte
    if save_db.cursor().execute('select * from mapobjects;').fetchall() == []:
        for mapobj in mapobj_list:
            save_db.cursor().execute('insert into mapobjects values (?, 0);', (mapobj[0],))
    # Création de la sauvegarde de la progression des missions
    if save_db.cursor().execute('select * from missions;').fetchall() == []:
        for mission in mission_list:
            save_db.cursor().execute('insert into missions values (?, 0, 0);', (mission[0],))
            for status in ["discovered", "unclaimed", "cleared"]:
                save_db.cursor().execute('insert into events values (?, 0);', (f"{status}Mission{mission[0]}",))
    save_db.commit()
    data_db.close()
    return save_db
