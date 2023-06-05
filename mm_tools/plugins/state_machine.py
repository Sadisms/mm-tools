from functools import wraps


class StateMachine:
    state_data = {}

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


def on_state(states: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
                plugin,
                message_or_event
        ):
            state_db = await plugin.state.get_state(message_or_event.user_id)

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
