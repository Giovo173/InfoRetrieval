class ClusteredGamesRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'clustered_games':
            return 'clustered_games'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'clustered_games':
            return 'clustered_games'
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'clustered_games':
            return db == 'clustered_games'
        return None
