
import pygame as pg
import shutil

"""Affichage du menu de débug"""

FONT = "arial"
FONT_SIZE = 18

def show_debug_menu(game):
    text = "Debug menu (F3) \n\
    ==== GAME ==== \n\
Ticks since Session Start : {} \n\
Ticks since Epoch : {} \n\
Dialogue : {}\n\
    ==== Clock ==== \n\
Current Weekday : {} \n\
Time : {}:{} \n\
    ==== Graphic ====   \n\
FPS : {} (expected {}), Tick time : {} ms,\n\
Effective tick time : {} ms,\n\
    ==== Player ====   \n\
World name : {}, World id : {}, \n\
Position : {}, Speed : {}, \n\
Animated : {}, Sprinting : {}, \n\
Can Move : {} \n\
    ==== Script ==== \n\
Script Tree : {} \n\
Current Script Name : {} \n\
Current Instruction : {} \n\
Current World's Flags : {} \n".format(
    game.internal_clock.ticks_since_sessionstart, game.internal_clock.ticks_since_epoch, game.dialogue is not None,
    game.internal_clock.dayname, game.internal_clock.hour, game.internal_clock.minute,
    round(game.internal_clock.pgclock.get_fps(), 2), game.TICK_PER_SECOND, game.internal_clock.pgclock.get_time(), game.internal_clock.pgclock.get_rawtime(),
    game.map_manager.map_file, game.map_manager.map_id, [round(pos, 2) for pos in game.player.position], game.player.base_walk_speed * (game.player.SPRINT_WALK_SPEED_MULTIPLIER if game.player.is_sprinting else 1), game.player.is_animated, game.player.is_sprinting, game.player.can_move,
    [scr[0].name for scr in game.script_tree], game.script_tree[-1][0].name if game.script_tree != [] else None, game.script_tree[-1][0].contents[game.script_tree[-1][1]-1] if game.script_tree != [] else None, game.script_manager.read_flags(-1))
    
    splited_text = text.split("\n")
    for (number, cur_text) in enumerate(splited_text):
        game.screen.blit(pg.font.SysFont(FONT, FONT_SIZE).render(cur_text, True, (255, 0, 0)), (0, number*(FONT_SIZE + 5)))

def reset_config(game):
    shutil.rmtree("stg")
    game.is_running = False
    game.restart = True

def reset_save(game):
    game.save.close()
    shutil.rmtree("sav")
    game.is_running = False
    game.restart = True
