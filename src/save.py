
import yaml
import os

PLAYER_CONFIGURATION_FILE = "sav/player.yaml"

def load_player_config():
    try:
        with open(PLAYER_CONFIGURATION_FILE, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        create_default_player_config()
        return load_player_config()

def create_default_player_config():
    config = {"map_id" : 1, "position" : [1600,1200], "speed" : 1.5}
    with open(PLAYER_CONFIGURATION_FILE, 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config

def save_player_config(map, position, speed):
    config = {"map_id" : map, "position" : position, "speed" : speed}
    with open(PLAYER_CONFIGURATION_FILE, 'w') as file:
        yaml.dump(config, file) #Ecriture du fichier de config
