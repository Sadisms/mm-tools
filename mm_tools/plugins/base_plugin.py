import importlib
import io
from typing import Dict, Optional

from mmpy_bot import Plugin, ActionEvent, Message
from mmpy_bot.function import Function
from mmpy_bot.wrappers import EventWrapper
from peewee_async import Manager

from .cache_db.models.base_model import pooled_database
from .state_machine import StateMachine


class BasePlugin(Plugin):
    state = StateMachine()
    last_log = None
    database_manager = Manager(pooled_database)

    def __init__(
            self,
            logger,
            sentry_profile: bool = False,
            sentry_profile_prefix: str = None
    ):
        self.logger = logger

        self.sentry_profile_prefix = sentry_profile_prefix
        self.sentry_module = None
        if sentry_profile:
            try:
                self.sentry_module = importlib.import_module("sentry_sdk")

            except ImportError:
                raise ImportError("Install sentry_sdk! pip install sentry-sdk")

        super().__init__()

    async def logging_event(self, event: EventWrapper) -> None:
        self.logger.info(event.body)

    async def call_function(
            self,
            function: Function,
            event: EventWrapper,
            groups=[],
    ):
        """ Логирование """

        if event.body != BasePlugin.last_log:
            await self.logging_event(event)
            BasePlugin.last_log = event.body

        if self.sentry_module:
            profile_name = function.name
            if isinstance(self.sentry_profile_prefix, str):
                profile_name = self.sentry_profile_prefix + profile_name

            with self.sentry_module.start_transaction(name=profile_name):
                await super().call_function(function, event, groups)

        else:
            await super().call_function(function, event, groups)

    async def update_message(
            self,
            post_id: str,
            message: str,
            props: dict = None,
            **kwargs
    ):
        if not props:
            props = {}

        await self.driver.posts.update_post(
            post_id=post_id,
            options={
                'id': post_id,
                'message': message,
                'props': props,
                **kwargs
            }
        )

    async def delete_message(
            self,
            event: ActionEvent = None,
            post_id: str = None
    ) -> None:
        if event:
            post_id = event.post_id

        await self.driver.posts.delete_post(
            post_id=post_id
        )

    async def get_file(
            self,
            file_id: str
    ) -> bytes:
        return await self.driver.files.get_file(file_id).content

    async def upload_file(
            self,
            channel_id: str,
            files: list[tuple[str, io.BytesIO]],
    ):
        files_ids = []
        for file in files:
            files_ids.append(
                (await self.driver.files.upload_file(
                    data={'channel_id': channel_id},
                    files={
                        'files': file
                    }
                ))['file_infos'][0]['id']
            )

        await self.driver.posts.create_post(
            options={
                'channel_id': channel_id,
                'file_ids': files_ids
            }
        )

    async def get_user_info(self, user_id: str) -> dict:
        return await self.driver.users.get_user(user_id=user_id)

    async def get_user_name(self, user_id: str):
        return (await self.get_user_info(user_id))['username']

    async def get_user_full_name(self, user_id: str) -> str:
        user_info = await self.get_user_info(user_id)
        if user_info['first_name'] and user_info['last_name']:
            return f'{user_info["first_name"]} {user_info["last_name"]}'

        return user_info['username'].title()

    async def get_direct_from_user(self, user_id: str) -> str:
        return (await self.driver.channels.create_direct_channel([self.driver.user_id, user_id]))["id"]

    async def direct_post(
            self,
            receiver_id: str,
            message: str = "",
            file_paths: Optional[str] = None,
            root_id: str = "",
            props=None,
            ephemeral_user_id: Optional[str] = None,
    ) -> Dict:

        if props is None:
            props = {}

        direct_id = await self.get_direct_from_user(receiver_id)

        return await self.driver.create_post(
            channel_id=direct_id,
            message=message,
            props=props,
            root_id=root_id,
            file_paths=file_paths,
            ephemeral_user_id=ephemeral_user_id
        )

    def message_to_action_event(self, message: Message, context: dict = None, post_id: str = None):
        action_event = ActionEvent(
            body={
                'channel_id': message.channel_id,
                'context': context or {},
                'post_id': post_id,
                'user_id': message.user_id,
                'user_name': self.get_user_name(message.user_id),
                'team_id': message.team_id
            },
            request_id='',
            webhook_id=''
        )
        return action_event

    async def send_files_from_message(self, message: Message, channel_id: str) -> list[str]:
        return [
            (await self.driver.files.upload_file(
                data={'channel_id': channel_id},
                files={
                    'files': (file['name'], (await self.driver.files.get_file(file['id'])).content)
                }
            ))['file_infos'][0]['id']
            for file in message.body['data']['post']['metadata']['files']
        ]
