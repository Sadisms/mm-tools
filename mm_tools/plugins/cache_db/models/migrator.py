from peewee_moves import DatabaseManager
from .base_model import pooled_database


manager = DatabaseManager(
    database=pooled_database,
    table_name='plugins_migrations',
    directory='plugins/cache_db/models/migrations'
)