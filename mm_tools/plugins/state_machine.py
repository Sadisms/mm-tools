import asyncio
import json
from functools import wraps

import aiosqlite


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
        if self.state_data[user_id].get('cache'):
            self.state_data[user_id].pop('cache')

    @staticmethod
    async def init_tables():
        async with aiosqlite.connect(StateMachine.db_name) as db:
            await db.execute(
                """
                    CREATE TABLE IF NOT EXISTS "plugins_cache_state" (
                        "user_id" VARCHAR(255) NOT NULL PRIMARY KEY, 
                        "cache" TEXT
                    );
                """
            )
            await db.commit()

    @staticmethod
    async def get_value_from_db(user_id: str) -> dict:
        async with aiosqlite.connect(StateMachine.db_name) as db:
            async with db.execute(
                    """
                        SELECT "user_id", "cache"
                        FROM "plugins_cache_state"
                        WHERE user_id = ?;
                    """,
                    (user_id,)
            ) as cursor:
                value = await cursor.fetchone()
                return json.loads(value or '{}')

    @staticmethod
    async def set_value_from_db(user_id: str, **kw):
        old_value = await StateMachine.get_value_from_db(user_id)
        new_value = json.dumps({**kw, **old_value}, ensure_ascii=False)

        async with aiosqlite.connect(StateMachine.db_name) as db:
            await db.execute(
                """
                   INSERT OR REPLACE INTO plugins_cache_state("user_id", "cache") 
                   values(?, ?);
                """,
                (user_id, new_value, )
            )
            await db.commit()

    @staticmethod
    async def clear_values_from_db(user_id: str):
        async with aiosqlite.connect(StateMachine.db_name) as db:
            await db.execute(
                """
                    DELETE FROM plugins_cache_state
                    WHERE user_id = ?
                """,
                (user_id, )
            )
            await db.commit()


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
