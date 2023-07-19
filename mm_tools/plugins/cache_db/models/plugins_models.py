from peewee_aio import AIOModel, fields, Manager

manager = Manager("aiosqlite:///.plugins.db")


@manager.register
class PluginsCacheProps(AIOModel):
    id = fields.AutoField()
    post_id = fields.CharField()
    props = fields.TextField(null=True)
    message = fields.TextField(null=True)
    integration_url = fields.TextField(null=True)

    class Meta:
        db_table = 'plugins_cache_props'


@manager.register
class PluginsCacheState(AIOModel):
    id = fields.AutoField()
    user_id = fields.CharField()
    cache = fields.TextField(default="{}")

    class Meta:
        db_table = 'plugins_cache_state'
