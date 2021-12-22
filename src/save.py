#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import yaml
import os
import objects

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
        "DEBUG" : "F3"
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
    config = load_config(object)
    for arg in args.items():
        config[arg[0]] = arg[1]
    with open(CONFIGURATION_FILES[object], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config
