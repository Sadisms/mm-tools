import asyncio
import json
from functools import wraps

from peewee_async import Manager

from .cache_db.models.base_model import pooled_database
from .cache_db.models.plugins_models import PluginsCacheState


class StateMachine:
    state_data = {}
    db_name = '.plugins.db'
    database_manager = Manager(pooled_database)

    def set_state(self, user_id: str, state: str | None) -> None:
        self.state_data[user_id] = {
            **self.state_data.get(user_id, {}),
            'state': state,
        }

    def state_finish(self, user_id: str) -> None:
        self.set_state(user_id, None)

    def get_state(self, user_id: str) -> str | None:
        return self.state_data.get(user_id, {}).get('state')

    def set_value(self, user_id: str, **kwargs) -> None:
        old_cache = self.state_data.get(user_id, {}).get('cache', {})
        self.state_data[user_id] = {
            **self.state_data.get(user_id, {}),
            'cache': {**old_cache, **kwargs},
        }

    def get_value(self, user_id: str):
        return self.state_data.get(user_id, {}).get('cache', {})

    def clear_values(self, user_id):
        if self.state_data.get('user_id', {}).get('cache'):
            self.state_data[user_id].pop('cache')

    @staticmethod
    def init_tables():
        return PluginsCacheState.create_table()

    @staticmethod
    async def get_value_from_db(user_id: str) -> dict:
        query = PluginsCacheState.select(
            PluginsCacheState.cache
        ).where(
            PluginsCacheState.user_id == user_id
        )
        if await StateMachine.database_manager.count(query) > 0:
            for data in await StateMachine.database_manager.execute(query):
                return data.cache

    @staticmethod
    async def set_value_from_db(user_id: str, **kw):
        old_value = await StateMachine.get_value_from_db(user_id)
        new_value = {**(old_value or {}), **kw}

        cache, _ = await StateMachine.database_manager.get_or_create(
            PluginsCacheState,
            user_id=user_id
        )
        cache.cache = new_value
        cache.save()

    @staticmethod
    async def clear_values_from_db(user_id: str):
        await StateMachine.database_manager.delete(
            PluginsCacheState.delete().where(
                PluginsCacheState.user_id == user_id
            )
        )

    @staticmethod
    async def clear_value_from_db(user_id: str, key_value: str):
        old_value = await StateMachine.get_value_from_db(user_id)
        old_value.pop(key_value)

        await StateMachine.set_value_from_db(user_id, **old_value)


def on_state(states: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
                plugin,
                message_or_event
        ):
            state_db = plugin.state.get_state(message_or_event.user_id)

            for state in states:
                if not state and not state_db:
                    return await func(plugin, message_or_event)

                if not state and state_db:
                    return

                if state in (state_db or ''):
                    return await func(plugin, message_or_event)

        return wrapper

    return decorator


def on_filter(filters: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
                plugin,
                message_or_event
        ):
            for f in filters:
                if asyncio.iscoroutinefunction(f):
                    if not await f(message_or_event, plugin.driver):
                        return

                else:
                    if not f(message_or_event, plugin.driver):
                        return

            return await func(plugin, message_or_event)

        return wrapper

    return decorator
