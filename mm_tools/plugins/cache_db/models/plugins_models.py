from peewee_aio import AIOModel, fields

from .base_model import manager


@manager.register
class PluginsCacheProps(AIOModel):
    id = fields.AutoField()
    post_id = fields.CharField()
    props = fields.TextField()
    message = fields.TextField()
    integration_url = fields.TextField()


@manager.register
class PluginsCacheState(AIOModel):
    id = fields.AutoField()
    user_id = fields.CharField()
    cache = fields.TextField()
