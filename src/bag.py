#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion du Sac et de l'inventaire
"""

import objects
import numpy as np

class Bag():

    def __init__(self, save):
        self.save_db = save
        data = np.array(self.save_db.cursor().execute("SELECT * FROM bag").fetchall())
        self.contents = dict(zip(data[:,0], data[:,1])) if data != [] else {}

    def pickup_object(self, mapobject):
        """Incrémentation de la quantité d'un objet lorsqu'il est ramassé"""
        if not mapobject.parent.id in self.contents:
            self.contents[mapobject.parent.id] = 1
        else:
            self.contents[mapobject.parent.id] += 1
        mapobject.exists = False
        print(self.contents)

    def save(self):
        """Sauvegarde le contenu du sac dans la base de données"""
        cursor = self.save_db.cursor()
        for item, count in self.contents.items():
            cursor.execute("INSERT OR REPLACE INTO bag VALUES (?, ?)", (item, count))

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
