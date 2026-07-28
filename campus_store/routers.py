class DBRouter:
    """
    A database router to control all database operations on models in the
    campus_store project.

    Routing rules:
    - 'orders' app_label -> 'orders_db' (PostgreSQL via Neon.tech)
    - Django authentication, sessions, content types, and admin -> 'auth_db'
    - 'catalog' and other business apps -> 'default' (MySQL)
    """

    def db_for_read(self, model, **hints):
        """Point read operations to assigned database."""
        if model._meta.app_label == 'orders':
            return 'orders_db'
        elif model._meta.app_label in ('auth', 'sessions', 'contenttypes', 'admin'):
            return 'auth_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """Point write operations to assigned database."""
        if model._meta.app_label == 'orders':
            return 'orders_db'
        elif model._meta.app_label in ('auth', 'sessions', 'contenttypes', 'admin'):
            return 'auth_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between models residing in the same database."""
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure each app_label migrates to its assigned database.
        """
        if app_label == 'orders':
            return db == 'orders_db'
        elif app_label in ('auth', 'sessions', 'contenttypes', 'admin'):
            return db == 'auth_db'
        else:
            return db == 'default'
