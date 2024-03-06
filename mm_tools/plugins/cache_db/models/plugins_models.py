import peewee
from playhouse.postgres_ext import JSONField

from .base_model import BaseModel


class PluginsCacheProps(BaseModel):
    id = peewee.AutoField()
    bot_user_id = peewee.CharField()
    post_id = peewee.CharField()
    props = JSONField(null=True)
    message = peewee.TextField(null=True)
    integration_url = peewee.TextField(null=True)

    class Meta:
        db_table = 'plugins_cache_props'


class PluginsCacheState(BaseModel):
    id = peewee.AutoField()
    user_id = peewee.CharField()
    cache = JSONField(default={})

    class Meta:
        db_table = 'plugins_cache_state'
