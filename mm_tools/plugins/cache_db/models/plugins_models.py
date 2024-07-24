import peewee
from playhouse.postgres_ext import JSONField

from .base_model import BaseModel


class PluginsCacheState(BaseModel):
    id = peewee.AutoField()
    user_id = peewee.CharField()
    cache = JSONField(default={})

    class Meta:
        db_table = 'plugins_cache_state'
