import peewee
import peewee_async

pooled_database = peewee_async.PooledPostgresqlDatabase(None)


class BaseModel(peewee.Model):
    """Base model class."""

    class Meta(object):
        """Base model options."""

        database = pooled_database


def set_database(**kwargs):
    pooled_database.init(**kwargs)
