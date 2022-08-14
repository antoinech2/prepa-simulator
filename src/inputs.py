import pygame as pg
import save
import debug

def init():
    global controls
    controls = save.load_config("controls")
    for cur_key in controls.keys():
        controls[cur_key] = pg.key.key_code(controls[cur_key])

def handle_pressed_key(game):
    """Transmet toutes les touches préssées"""
    pressed = pg.key.get_pressed() #Gestion des touches du clavier
    # On envoie le statut des 4 touches de déplacement pour être traité, si le clavier n'est pas bloqué
    if not game.input_lock and game.dialogue is None:
        game.player.move([pressed[controls["PLAYER_MOVE_UP"]], pressed[controls["PLAYER_MOVE_RIGHT"]], pressed[controls["PLAYER_MOVE_DOWN"]], pressed[controls["PLAYER_MOVE_LEFT"]]], pressed[controls["PLAYER_SPRINT"]] or pressed[controls["PLAYER_SPRINT_SEC"]])

def handle_key_down_event(game, event):
    """Transmet l'évènement d'une toucher qui vient d'être pressée"""
    if event.key == controls["MENU_INTERACT"] and game.menu_manager.choicebox is not None:     # si une boîte de choix est présente
        game.menu_manager.choicebox.choice_taken()
    elif event.key == controls["ACTION_INTERACT"] and not game.menu_is_open:  # si Espace est pressée
        if game.dialogue is None and not game.input_lock:
            game.map_manager.get_warps()
            game.map_manager.object_manager.pickup_check()
            game.map_manager.npc_manager.check_talk()
            game.menu_manager.sidemenu.bagmenu.refresh_groups() # Augmentation de la capacité affichée à l'écran de l'objet
        elif game.dialogue is not None:
            game.dialogue.next_dialogue()
    elif event.key == controls["MENU_SHOW_SIDEBAR"]:
        game.menu_manager.toggle_sidemenu()
    elif event.key == controls["MENU_INTERACT"] and game.menu_is_open:
        game.menu_manager.open_menu()
    elif event.key == controls["MENU_CANCEL"]:
        game.menu_manager.close_menu()
    elif event.key == controls["MENU_MOVE_UP"] and (game.menu_is_open or game.menu_manager.choicebox is not None):
        game.menu_manager.menu_move("up")
    elif event.key == controls["MENU_MOVE_DOWN"] and (game.menu_is_open or game.menu_manager.choicebox is not None):
        game.menu_manager.menu_move("down")
    elif event.key == controls["MENU_MOVE_LEFT"] and (game.menu_is_open or game.menu_manager.choicebox is not None):
        game.menu_manager.menu_move("left")
    elif event.key == controls["MENU_MOVE_RIGHT"] and (game.menu_is_open or game.menu_manager.choicebox is not None):
        game.menu_manager.menu_move("right")
    elif event.key == controls["MINIGAME_UP"] and game.minigame_opened:
        game.mgm_manager.key("up")
    elif event.key == controls["MINIGAME_DOWN"] and game.minigame_opened:
        game.mgm_manager.key("down")
    elif event.key == controls["MINIGAME_LEFT"] and game.minigame_opened:
        game.mgm_manager.key("left")
    elif event.key == controls["MINIGAME_RIGHT"] and game.minigame_opened:
        game.mgm_manager.key("right")
    elif event.key == controls["MINIGAME_ENTER"] and game.minigame_opened:
        game.mgm_manager.key("enter")
    elif event.key == controls["GAME_FULLSCREEN"]:
        game.change_window_size(fullscreen = (not game.is_fullscreen))
    elif event.key == controls["GAME_TERMINATE"]:
        game.is_running = False
    elif event.key == controls["DEBUG"]:
        game.debug = not game.debug
    elif event.key == controls["RESET_CONFIG"] and event.mod & pg.KMOD_SHIFT and event.mod & pg.KMOD_CTRL:#controls["CONFIRM_DEBUG_KEY"]:
        debug.reset_config(game)
    elif event.key == controls["RESET_SAVE"] and event.mod & pg.KMOD_SHIFT and event.mod & pg.KMOD_CTRL:#controls["CONFIRM_DEBUG_KEY"]:
        debug.reset_save(game)
