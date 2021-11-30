
import pygame as pg

def handle_pressed_key(game):
    pressed = pg.key.get_pressed() #Gestion des touches du clavier
    if not game.player.is_talking:
        # On envoie le statut des 4 touches de déplacement pour être traité
        game.player.move([pressed[pg.K_UP], pressed[pg.K_RIGHT], pressed[pg.K_DOWN], pressed[pg.K_LEFT]], pressed[pg.K_RCTRL] or pressed[pg.K_LCTRL])

def handle_key_down_event(game, event):
    if event.key == pg.K_SPACE:  # si Espace est pressée
        game.player.space_pressed()
