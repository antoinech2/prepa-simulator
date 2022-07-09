import pygame as pg

import locale
import numpy

class MGManager():
    """Classe de gestion des mini-jeux"""
    
    def __init__(self, game):
        self.game = game
        self.running_mg = None
    
    def update(self):
        if self.running_mg is not None:
            self.game.player.can_move = False
            self.game.minigame_opened = True
            self.running_mg.update_graphics()
        else:
            if not self.game.menu_is_open:
                self.game.player.can_move = True
            self.game.minigame_opened = False

    def launch(self, mgm, *args):
        """Lancement d'un mini-jeu passé en argument"""
        if mgm == "select":
            texts = locale.get_string("select", args[0])
            self.running_mg = SelectGame(self.game, texts["qu"], [texts[p] for p in ['a', 'b', 'c', 'd', 'e']], texts["correct"])

    def key(self, key):
        """Gestion de l'appui d'une touche"""
        try:
            if key == "up":
                self.running_mg.up()
            if key == "down":
                self.running_mg.down()
            if key == "left":
                self.running_mg.left()
            if key == "right":
                self.running_mg.right()
            if key == "enter":
                self.running_mg.enter()
        except AttributeError:    
            pass        # Touche non supportée dans le mini-jeu courant ou pas de mini-jeu

class Minigame():
    """Classe des mini-jeux"""
    
    def __init__(self, game):
        self.game = game
    
    def launch(self):
        """Exécute un mini-jeu"""
        self.game.mgm_manager.running_mg = self
    
    def terminate(self):
        """Arrête l'exécution d'un mini-jeu"""
        self.game.mgm_manager.running_mg = None


class SelectGame(Minigame):
    """Classe du mini-jeu de sélection"""
    BANK = f"{locale.get_dir()}/select.yaml"            # Chemin vers la banque de questions
    TEXTURES_FOLDER = "res/textures/minigame/select/"   # Dossier des textures associées au mini-jeu
    OFFSET_FROM_BORDER = 30                             # La boîte associée à la question est décalée de tant par rapport au bord haut
    OFFSET_TO_BOTTOM = 30                               # La dernière boîte (Valider) est décalée de tant par rapport au bord bas
    SPACE_BETWEEN_LINES = 42
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    FONT = "consolas"
    QUESTION_FSIZE = 22                                 #? Utiliser du LaTeX pour certaines questions, nécessite l'implémentation de la possibilité de mettre des images
    PROPOSITION_FSIZE = 16

    
    def __init__(self, game, question, props, correct):
        super().__init__(game)

        self.bgm = "it's concours time"
        self.question = question    # Intitulé de la question
        self.props = props          # Liste des propositions
        self.number_of_props = len([prop for prop in props if prop != ""])
        self.correct = correct      # Lettre de la proposition correcte

        self.order = numpy.random.permutation(self.number_of_props)    # Ordre d'apparition des propositions
        while len(self.order) <= len(self.props):                   # Valeur par défaut pour les propositions vides
            self.order = numpy.append(self.order, len(self.order))
        self.order = list(self.order)

        # Mémoire interne
        self.choices = [0 for _ in self.props]  # Liste des choix faits par le joueur
        self.cursor_position = 0        # Position du curseur de sélection

        # Graphiques : textures de la boîte d'affichage de la question
        self.greenbox = pg.image.load(f"{self.TEXTURES_FOLDER}greenbg.png").convert()
        self.greenbox.set_colorkey([255, 255, 255])
        self.orangebox = pg.image.load(f"{self.TEXTURES_FOLDER}orangebg.png").convert()
        self.orangebox.set_colorkey([255, 255, 255])
        self.redbox = pg.image.load(f"{self.TEXTURES_FOLDER}redbg.png").convert()
        self.redbox.set_colorkey([255, 255, 255])
        self.violetbox = pg.image.load(f"{self.TEXTURES_FOLDER}violetbg.png").convert()
        self.violetbox.set_colorkey([255, 255, 255])
        # Police associée
        self.qu_font = pg.font.SysFont(self.FONT, self.QUESTION_FSIZE)
        self.qu_font_width = max([metric[1] for metric in self.qu_font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie
        self.qu_row_length = self.greenbox.get_size()[0] / self.qu_font_width - 7  # cf dialogue
        self.qu_row_height = self.qu_font.get_linesize()
        # Texte de la question
        self.qu_texts = []
        for line in self.format(self.question):
            self.qu_texts.append(self.qu_font.render(line, True, [0, 0, 0]))

        # Graphiques : textures des boîtes de sélection
        self.choiceoff = pg.image.load(f"{self.TEXTURES_FOLDER}choiceoff.png").convert()
        self.choiceoff.set_colorkey([255, 255, 255])
        self.choiceon = pg.image.load(f"{self.TEXTURES_FOLDER}choiceon.png").convert()
        self.choiceon.set_colorkey([255, 255, 255])
        self.validate = pg.image.load(f"{self.TEXTURES_FOLDER}choiceoff.png").convert()
        self.validate.set_colorkey([255, 255, 255])
        # Police associée
        self.prop_font = pg.font.SysFont(self.FONT, self.PROPOSITION_FSIZE)
        self.prop_font_width = max([metric[1] for metric in self.prop_font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie
        self.row_length = self.greenbox.get_size()[0] / self.prop_font_width - 7  # cf dialogue
        self.row_height = self.prop_font.get_linesize()
        # Textes des propositions (dans l'ordre du fichier yaml)
        self.props_tex = []
        for prop in self.props:
            self.props_tex.append(self.prop_font.render(prop, True, [0, 0, 0]))
        self.props_tex.append(self.prop_font.render("Valider", True, [0, 0, 0]))
    
        # Graphiques : flèche
        self.arrow_tex = pg.image.load(f"{self.TEXTURES_FOLDER}arrow.png").convert()
        self.arrow_tex.set_colorkey([255, 255, 255])
    
    def down(self):
        self.cursor_position += 1
        if self.cursor_position == len(self.props) + 1: # On prend en compte le bouton valider
            self.cursor_position = 0
    
    def up(self):
        self.cursor_position -= 1
        if self.cursor_position == -1:
            self.cursor_position = len(self.props)
    
    def enter(self):
        if self.cursor_position == 5:       # Dans tous les cas (moins de 5 propositions...) le bouton valider est en 6ème position
            answer = set([self.ALPHABET[self.order.index(i)] for i in range(len(self.choices)) if self.choices[i] == 1])    # Ensemble des réponses sous forme de lettres
            if answer == self.correct:      # On lève un drapeau interne pour symboliser une partie gagnante ou non
                self.game.script_manager.change_event("passedSelectMG", 1)
            else:
                self.game.script_manager.change_event("passedSelectMG", 0)
            self.terminate()
        else:
            self.choices[self.cursor_position] = 1 - self.choices[self.cursor_position]
    
    def format(self, text):
        """Découpage d'un texte en plusieurs lignes de taille adéquate"""
        # C'est la même fonction que pour les dialogues
        formatted_text = []
        splitted_text = text.split()
        text_line = ""
        line_length = 0
        while splitted_text != []:
            word_length = len(splitted_text[0])
            if line_length + word_length > self.qu_row_length:
                formatted_text.append(text_line)
                text_line = ""
                line_length = 0
            text_line += splitted_text[0] + " "
            line_length += word_length + 1
            del(splitted_text[0])
        formatted_text.append(text_line)
        return(formatted_text)

    def update_graphics(self):
        """Mise à jour de l'affichage des textures des boutons et de la boîte de dialogue"""
        # Affichage de la boîte de question
        rect_box = self.greenbox.get_rect(center=(self.game.screen.get_size()[0]/2, self.OFFSET_FROM_BORDER + self.greenbox.get_size()[1]/2))
        self.game.screen.blit(self.greenbox, rect_box)
        for line in range(len(self.qu_texts)):
            text_box = self.qu_texts[line].get_rect(center = (self.game.screen.get_size()[0]/2, self.OFFSET_FROM_BORDER + self.greenbox.get_size()[1]/2 + (line-len(self.qu_texts)/2) * self.qu_row_height))
            self.game.screen.blit(self.qu_texts[line], text_box)

        # Affichage des boîtes de choix
        rect_A = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - (4-self.order[0]+1)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        if self.choices[self.order[0]]:
            self.game.screen.blit(self.choiceon, rect_A)
        else:
            self.game.screen.blit(self.choiceoff, rect_A)
        text_box = self.props_tex[0].get_rect(center = rect_A.center)
        self.game.screen.blit(self.props_tex[0], text_box)
        
        rect_B = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - (4-self.order[1]+1)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        if self.choices[self.order[1]]:
            self.game.screen.blit(self.choiceon, rect_B)
        else:
            self.game.screen.blit(self.choiceoff, rect_B)
        text_box = self.props_tex[1].get_rect(center = rect_B.center)
        self.game.screen.blit(self.props_tex[1], text_box)
        
        rect_C = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - (4-self.order[2]+1)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        if self.choices[self.order[2]]:
            self.game.screen.blit(self.choiceon, rect_C)
        else:
            self.game.screen.blit(self.choiceoff, rect_C)
        text_box = self.props_tex[2].get_rect(center = rect_C.center)
        self.game.screen.blit(self.props_tex[2], text_box)
        
        rect_D = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - (4-self.order[3]+1)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        if self.choices[self.order[3]]:
            self.game.screen.blit(self.choiceon, rect_D)
        else:
            self.game.screen.blit(self.choiceoff, rect_D)
        text_box = self.props_tex[3].get_rect(center = rect_D.center)
        self.game.screen.blit(self.props_tex[3], text_box)
        
        rect_E = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - (4-self.order[4]+1)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        if self.choices[self.order[4]]:
            self.game.screen.blit(self.choiceon, rect_E)
        else:
            self.game.screen.blit(self.choiceoff, rect_E)
        text_box = self.props_tex[4].get_rect(center = rect_E.center)
        self.game.screen.blit(self.props_tex[4], text_box)
        
        rect_val = self.choiceoff.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1] - self.OFFSET_FROM_BORDER - self.choiceoff.get_size()[1]/2))
        self.game.screen.blit(self.choiceoff, rect_val)
        text_box = self.props_tex[5].get_rect(center = rect_val.center)
        self.game.screen.blit(self.props_tex[5], text_box)

        # Affichage de la flèche
        rect_arrow = self.arrow_tex.get_rect(center = (self.game.screen.get_size()[0]/2 - self.choiceoff.get_size()[0]/2 + 22,  # Terme correctif
                                                       self.game.screen.get_size()[1] - self.OFFSET_TO_BOTTOM - (5 - self.cursor_position)*self.SPACE_BETWEEN_LINES - self.choiceoff.get_size()[1]/2))
        self.game.screen.blit(self.arrow_tex, rect_arrow)