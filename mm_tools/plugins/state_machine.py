import asyncio
import json
from functools import wraps

from .cache_db.models.base_model import manager
from .cache_db.models.plugins_models import PluginsCacheState


class StateMachine:
    state_data = {}
    db_name = '.plugins.db'

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
    async def init_tables():
        async with manager:
            async with manager.connection():
                await PluginsCacheState.create_table()

    @staticmethod
    async def get_value_from_db(user_id: str) -> dict:
        async with manager:
            async with manager.connection():
                query = PluginsCacheState.select(
                        PluginsCacheState.cache
                ).where(
                    PluginsCacheState.user_id == user_id
                )
                if await query.count() > 0:
                    async for data in query:
                        return json.loads(data.cache)

    @staticmethod
    async def set_value_from_db(user_id: str, **kw):
        old_value = await StateMachine.get_value_from_db(user_id)
        new_value = json.dumps({**old_value, **kw}, ensure_ascii=False)

        async with manager:
            async with manager.connection():
                cache, _ = await PluginsCacheState.get_or_create(
                    user_id=user_id
                )
                cache.cache = json.dumps(new_value)
                await cache.save()

    @staticmethod
    async def clear_values_from_db(user_id: str):
        async with manager:
            async with manager.connection():
                await PluginsCacheState.delete().where(
                    PluginsCacheState.user_id == user_id
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
