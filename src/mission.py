import locale

class Mission():
    """Classe des missions"""
    def __init__(self, id, adv):
        self.id = id
        self.max_adv = adv
        self.shown_message = None
        self.name = locale.get_substring("mission_titles", id)

class MissionManager():
    """Classe de gestion des missions et du sous-menu associé"""
    def __init__(self, game):
        self.game = game
        self.dict_of_missions = {}
        mission_list = self.game.game_data_db.execute("select * from missions ;").fetchall()    # Obtention de la liste des missions
        
        for mission in mission_list:
            new_mission = Mission(mission[0], mission[1])
            new_mission.current_adv = self.game.save.execute('select adv from missions where id = ?;', (new_mission.id,)).fetchall()[0][0]
            status_id = self.game.save.execute('select status from missions where id = ?;', (new_mission.id,)).fetchall()[0][0]
            if status_id == 0:      # Mission non découverte
                new_mission.current_status = "blank"
            if status_id == 1:      # Mission découverte mais non commencée
                new_mission.current_status = "new"
            if status_id == 2:      # Mission en cours
                new_mission.current_status = "inprogress"
            if status_id == 3:      # Mission terminée mais récompense non obtenue
                new_mission.current_status = "claim"
            if status_id == 4:      # Mission close
                new_mission.current_status = "done"

            self.dict_of_missions[new_mission.id] = new_mission
    
    def save(self):
        """Sauvegarde de l'état des missions"""
        for mission in list(self.dict_of_missions.values()):
            status = ["blank", "new", "inprogress", "claim", "done"].index(mission.current_status)
            self.game.save.cursor().execute("insert or replace into missions values (?, ?, ?)", (mission.id, status, mission.current_adv))
        self.game.save.commit()