
import yaml
import os

CONFIGURATION_FILES = {
    "player" : "sav/player.yaml",
    "window" : "sav/window.yaml"
    }

DEFAULT_CONFIG = {
    "player" : {"map_id" : 1, "position" : [1600,1200], "speed" : 1.5},
    "window" : {"size" : (1000, 600), "fullscreen" : False}
    }

def load_config(object):
    try:
        with open(CONFIGURATION_FILES[object], 'r') as file:
            config = yaml.load(file, Loader = yaml.FullLoader)
        return config
    except FileNotFoundError:
        create_default_config(object)
        return load_config(object)

def create_default_config(object):
    config = DEFAULT_CONFIG[object]
    with open(CONFIGURATION_FILES[object], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def save_player_config(map, position, speed):
    config = {"map_id" : map, "position" : position, "speed" : speed}
    with open(CONFIGURATION_FILES["player"], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def save_window_config(size = None, fullscreen = None):
    base_config = load_config("window")
    new_size = size if size is not None else base_config["size"]
    new_fullscreen = fullscreen if fullscreen is not None else base_config["fullscreen"]
    config = {"size" : new_size, "fullscreen" : new_fullscreen}
    with open(CONFIGURATION_FILES["window"], 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config
