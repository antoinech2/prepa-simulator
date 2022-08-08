
import pygame as pg
import shutil

"""Affichage du menu de débug"""

FONT = "consolas"
FONT_SIZE = 18

def show_debug_menu(game):
    text = f"Debug menu (F3) \n\
    ==== GAME ==== \n\
Ticks since Session Start : {game.internal_clock.ticks_since_sessionstart} \n\
Ticks since Epoch : {game.internal_clock.ticks_since_epoch} \n\
Dialogue : {game.dialogue is not None}\n\
Inputs : {'locked' if game.input_lock else 'unlocked'}\n\
    ==== Clock ==== \n\
Current Weekday : {game.internal_clock.dayname}, Time : {game.internal_clock.hour}:{game.internal_clock.minute} \n\
    ==== Graphic ====   \n\
FPS : {round(game.internal_clock.pgclock.get_fps(), 2)} (expected {game.TICK_PER_SECOND}), Tick time : {game.internal_clock.pgclock.get_time()} ms,\n\
Effective tick time : {game.internal_clock.pgclock.get_rawtime()} ms,\n\
    ==== Player ====   \n\
World name : {game.map_manager.map_file}, World id : {game.map_manager.map_id}, \n\
Position : {[round(pos, 2) for pos in game.player.position]}, Speed : {game.player.base_walk_speed * (game.player.SPRINT_MULTIPLIER if game.player.is_sprinting else 1)}, \n\
Animated : {game.player.is_animated}, Sprinting : {game.player.is_sprinting}, Can Move : {game.player.can_move}, Collision : {game.player.boop} \n\
Energy : {game.player.stamina} \n\
    ==== Script ==== \n\
Script Tree : {[scr[0].name for scr in game.script_tree]} \n\
Current Script Name : {game.script_tree[-1][0].name if game.script_tree != [] else None} \n\
Current Instruction : {game.script_tree[-1][0].contents[game.script_tree[-1][1]-1] if game.script_tree != [] else None} \n\
Current World's Flags : {game.script_manager.read_flags(-1)} \n\
Moving Entities : {[key for key in game.moving_people]} \n\
Movement Memory : {game.movement_mem} \n\
Permanently Moving People : {[key for key in game.persistent_move]}"

    splited_text = text.split("\n")
    for (number, cur_text) in enumerate(splited_text):
        game.screen.blit(pg.font.SysFont(FONT, FONT_SIZE).render(cur_text, True, (255, 255, 0)), (0, number*(FONT_SIZE + 5)))

def reset_config(game):
    shutil.rmtree("stg")
    game.is_running = False
    game.restart = True

def reset_save(game):
    game.save.close()
    shutil.rmtree("sav")
    game.is_running = False
    game.restart = True
