
import yaml
import os

CONFIGURATION_FILES = {
    "player" : "sav/player.yaml"
    }

def load_config(object):
    try:
        with open(CONFIGURATION_FILES[object], 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        create_default_config(object)
        return load_config(object)

def create_default_config(object):
    if object == "player":
        config = {"map_id" : 1, "position" : [1600,1200], "speed" : 1.5}
    with open(CONFIGURATION_FILES[object], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def save_player_config(map, position, speed):
    config = {"map_id" : map, "position" : position, "speed" : speed}
    with open(CONFIGURATION_FILES["player"], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config
