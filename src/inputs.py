
import pygame as pg

def handle_pressed_key(game):
    """Transmet toutes les touches préssées"""
    pressed = pg.key.get_pressed() #Gestion des touches du clavier
    # On envoie le statut des 4 touches de déplacement pour être traité
    game.player.move([pressed[pg.K_UP], pressed[pg.K_RIGHT], pressed[pg.K_DOWN], pressed[pg.K_LEFT]], pressed[pg.K_RCTRL] or pressed[pg.K_LCTRL])

def handle_key_down_event(game, event):
    """Transmet l'évènement d'une toucher qui vient d'être pressée"""
    if event.key == pg.K_SPACE:  # si Espace est pressée
        if game.dialogue == None:
            game.map_manager.object_manager.pickup_check()
            game.map_manager.npc_manager.check_talk()
        else:
            game.dialogue.next_dialogue()
    elif event.key == pg.K_F11:
        game.change_window_size(fullscreen = (not game.is_fullscreen))
    elif event.key == pg.K_ESCAPE:
        game.is_running = False
