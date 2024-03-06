from peewee_moves import Migrator


def upgrade(migrator: Migrator):
    migrator.add_column('plugins_cache_props', 'bot_user_id', 'varchar', null=True)


def downgrade(migrator: Migrator):
    migrator.drop_column('plugins_cache_props', 'bot_user_id')
