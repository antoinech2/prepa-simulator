#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import yaml
import os
import objects

CONFIGURATION_FILES = {
    "player" : "sav/player.yaml",
    "window" : "sav/window.yaml",
    "objects" : "sav/objects.yaml"
    }

DEFAULT_CONFIG = {
    "player" : {"map_id" : 1, "position" : [1600,1200], "speed" : 1.5},
    "window" : {"size" : (1000, 600), "fullscreen" : False},
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
