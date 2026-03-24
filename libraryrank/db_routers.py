class KohaReadOnlyRouter:
    """
    All Django ORM reads/writes → 'default' (LibraryRank MySQL DB).
    The 'koha' connection is never used by ORM — only raw SQL in sync command.
    """
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Only migrate LibraryRank's own 'default' MySQL database.
        # NEVER touch the Koha database.
        return db == 'default'
