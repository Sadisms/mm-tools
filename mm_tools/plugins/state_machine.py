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
            for state in states:
                if state in (plugin.state.get_state(message_or_event.user_id) or ''):
                    return await func(plugin, message_or_event)

        return wrapper

    return decorator
