from functools import wraps
from uuid import uuid4

import sqlite3
import json
import threading
from typing import Optional


def generate_session_id() -> str:
    return str(uuid4())


class BaseSession:
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id

    def get(self) -> dict:
        raise NotImplementedError

    def set(self, data: dict) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def clear_all_sessions(self) -> None:
        raise NotImplementedError


class SQLiteSession(BaseSession):
    """Хранение состояния диалога в локальной SQLite базе.

    Таблица schema:
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, session_id)
        )
    """

    _DB_PATH = '.sessions.db'
    _TABLE = 'sessions'
    _INIT_LOCK = threading.Lock()
    _INITIALIZED = False

    def __init__(self, user_id: str, session_id: Optional[str]):
        super().__init__(user_id, session_id)
        
        self._client = sqlite3.connect(self._DB_PATH, check_same_thread=False)
        self._client.execute('PRAGMA journal_mode=WAL;')
        self._client.execute('PRAGMA foreign_keys=ON;')
        self._init_db()

    def _init_db(self) -> None:
        if self.__class__._INITIALIZED:
            return
        with self.__class__._INIT_LOCK:
            if self.__class__._INITIALIZED:
                return
            self._client.execute(
                f'''CREATE TABLE IF NOT EXISTS {self._TABLE} (
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(user_id, session_id)
                )'''
            )
            self._client.commit()
            self.__class__._INITIALIZED = True

    def get(self) -> dict:
        cur = self._client.cursor()
        cur.execute(
            f'SELECT data FROM {self._TABLE} WHERE user_id=? AND session_id=?',
            (self.user_id, self.session_id)
        )
        row = cur.fetchone()
        if not row or row[0] is None:
            return {}
        try:
            return json.loads(row[0])
        except Exception:
            self.clear()
            return {}

    def set(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise TypeError('Session data must be dict')

        json_payload = json.dumps(data, ensure_ascii=False)
        self._client.execute(
            f'''INSERT INTO {self._TABLE} (user_id, session_id, data, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, session_id) DO UPDATE SET
                    data=excluded.data,
                    updated_at=CURRENT_TIMESTAMP''',
            (self.user_id, self.session_id, json_payload)
        )
        self._client.commit()

    def clear(self) -> None:
        self._client.execute(
            f'DELETE FROM {self._TABLE} WHERE user_id=? AND session_id=?',
            (self.user_id, self.session_id)
        )
        self._client.commit()

    def clear_all_sessions(self) -> None:
        self._client.execute(
            f'DELETE FROM {self._TABLE} WHERE user_id=?',
            (self.user_id,)
        )
        self._client.commit()

    def __del__(self):
        self._client.close()


def stateful_dialog(session_class: type[BaseSession] = SQLiteSession):
    """
    Декоратор: создаёт/обновляет сессию и передаёт её в целевую корутину.
    Ожидаемый сигнатурный вид целевой функции:
        async def handler(self, event, session: BaseSession)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, event):
            session_id = event.body.get("state")
            session = session_class(event.user_id, session_id)
            return await func(self, event, session)
        return wrapper
    return decorator


def stateful_attachment(session_class: type[BaseSession] = SQLiteSession):
    """
    Декоратор: создаёт/обновляет сессию и передаёт её в целевую корутину.
    Ожидаемый сигнатурный вид целевой функции:
        async def handler(self, event, session: BaseSession)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, event):
            session_id = event.body.get("context", {}).get("session_id")
            session = session_class(event.user_id, session_id)
            return await func(self, event, session)
        return wrapper
    return decorator