#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion du Sac et de l'inventaire
"""

import objects

class Bag():

    def __init__(self):
        self.contents = {} # Temporaire
        self.object_count = len(self.contents)

    def pickup_object(self, mapobject):
        """Incrémentation de la quantité d'un objet lorsqu'il est ramassé"""
        if not mapobject.parent.id in self.contents:
            self.contents[mapobject.parent.id] = 1
        else:
            self.contents[mapobject.parent.id] += 1
        mapobject.exists = False
        print(self.contents)
    
    def separate(self, interval):
        """Séparation du contenu du Sac en groupes (listes)"""
        objects = list(self.contents.keys())
        amounts = list(self.contents.values())
        groups = []
        current_group = []
        while objects != []:
            current_group.append((objects[0], amounts[0]))
            if len(current_group) >= interval:
                groups.append(current_group)
                current_group = []
            del(objects[0])
            del(amounts[0])
        groups.append(current_group)
        return(groups)