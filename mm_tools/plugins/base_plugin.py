import asyncio
import io
from functools import lru_cache

from mattermostautodriver import AsyncDriver
from mattermostautodriver.exceptions import NotEnoughPermissions, ResourceNotFound
from mmpy_bot import Plugin, ActionEvent, Message
from mmpy_bot.driver import Driver
from mmpy_bot.wrappers import EventWrapper
from peewee_async import Manager

from .cache_db.models.base_model import pooled_database
from .state_machine import StateMachine
from .cache_db.models.plugins_models import PluginsCacheProps


def _find_url(d):
    for k, v in d.items():
        if k == 'url':
            return v
        elif isinstance(v, dict):
            result = _find_url(v)
            if result is not None:
                return result

        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    result = _find_url(item)
                    if result is not None:
                        return result

                elif isinstance(item, list):
                    result = _find_url({"temporary_key": item})
                    if result is not None:
                        return result
    return None


def _replace_url(d, new_url):
    for k, v in d.items():
        if k == 'url':
            _v_split = v.split('/')
            d[k] = new_url + ('/' if new_url[-1] != '/' else '') + '/'.join(_v_split[6:])

        elif isinstance(v, dict):
            _replace_url(v, new_url)

        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    _replace_url(item, new_url)


class BasePlugin(Plugin):
    state = StateMachine()
    last_log = None
    database_manager = Manager(pooled_database)

    def __init__(self, logger):
        self.logger = logger
        super().__init__()

    async def call_function(
            self,
            function,
            event: EventWrapper,
            groups=[],
    ):
        """ Логирование """

        if event.body != BasePlugin.last_log:
            self.logger.info(event.body)
            BasePlugin.last_log = event.body

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

        self.driver.posts.update_post(
            post_id=post_id,
            options={
                'id': post_id,
                'message': message,
                'props': props
            }
        )

        if await self.get_cache_message(post_id):
            await self.update_cache_message(
                post_id=post_id,
                props=props,
                message=message
            )

        elif props:
            await self.add_cache_message(
                post_id=post_id,
                props=props,
                message=message
            )

    async def delete_message(
            self,
            event: ActionEvent = None,
            post_id: str = None
    ) -> None:
        if event:
            post_id = event.post_id

        self.driver.posts.delete_post(
            post_id=post_id
        )

        await self.delete_cache_message(post_id)

    def get_file(
            self,
            file_id: str
    ) -> bytes:
        return self.driver.files.get_file(file_id).content

    def upload_file(
            self,
            channel_id: str,
            files: list[tuple[str, io.BytesIO]],
    ):
        files_ids = []
        for file in files:
            files_ids.append(
                self.driver.files.upload_file(
                    data={'channel_id': channel_id},
                    files={
                        'files': file
                    }
                )['file_infos'][0]['id']
            )

        self.driver.posts.create_post(
            options={
                'channel_id': channel_id,
                'file_ids': files_ids
            }
        )

    @lru_cache
    def get_user_info(self, user_id: str) -> dict:
        return self.driver.users.get_user(user_id=user_id)

    @lru_cache
    def get_user_name(self, user_id: str):
        return self.get_user_info(user_id)['username']

    @lru_cache
    def get_user_full_name(self, user_id: str) -> str:
        user_info = self.get_user_info(user_id)
        if user_info['first_name'] and user_info['last_name']:
            return f'{user_info["first_name"]} {user_info["last_name"]}'

        return user_info['username'].title()

    @lru_cache
    def get_direct_from_user(self, user_id: str) -> str:
        return self.driver.channels.create_direct_channel([self.driver.user_id, user_id])["id"]

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

    def send_files_from_message(self, message: Message, channel_id: str) -> list[str]:
        return [
            self.driver.files.upload_file(
                data={'channel_id': channel_id},
                files={
                    'files': (file['name'], self.driver.files.get_file(file['id']).content)
                }
            )['file_infos'][0]['id']
            for file in message.body['data']['post']['metadata']['files']
        ]

    @staticmethod
    def init_tables():
        PluginsCacheProps.create_table()

    @staticmethod
    async def static_create_post_with_cache_props(
            driver: Driver,
            channel_id: str = None,
            receiver_id: str = None,
            message: str = '',
            props: dict = None
    ):
        if not channel_id and receiver_id:
            channel_id = driver.channels.create_direct_channel([driver.user_id, receiver_id])["id"]

        post = driver.create_post(
            channel_id=channel_id,
            message=message,
            props=props
        )

        if props and _find_url(props):
            await BasePlugin.add_cache_message(
                post_id=post['id'],
                props=props,
                message=message
            )

        return post

    async def create_post_with_cache_props(
            self,
            channel_id: str = None,
            receiver_id: str = None,
            message: str = '',
            props: dict = None
    ):
        return await self.static_create_post_with_cache_props(
            driver=self.driver,
            channel_id=channel_id,
            receiver_id=receiver_id,
            message=message,
            props=props
        )

    @staticmethod
    async def _gather_update_post(new_url, row, async_driver):
        if new_url not in row.integration_url:
            _replace_url(row.props, new_url)

            # Check message
            try:
                await async_driver.posts.get_post(row.post_id)

            except ResourceNotFound:
                await BasePlugin.delete_cache_message(row.post_id)
                return

            try:
                await async_driver.posts.update_post(
                    post_id=row.post_id,
                    options={
                        'id': row.post_id,
                        'message': row.message,
                        'props': row.props
                    }
                )

                await BasePlugin.update_cache_message(
                    post_id=row.post_id,
                    props=row.props,
                    integration_url=new_url
                )

            except Exception:  # NOQA
                pass

    @staticmethod
    async def update_integrations(
            driver: Driver,
            new_url: str
    ):
        async_driver = AsyncDriver(driver.client._options)

        rows = await BasePlugin.database_manager.execute(PluginsCacheProps.select())

        await asyncio.gather(*[
            BasePlugin._gather_update_post(new_url, row, async_driver)
            for row in rows
        ])

    @staticmethod
    async def add_cache_message(
            post_id: str,
            props: dict,
            message: str
    ):
        await BasePlugin.database_manager.create(
            PluginsCacheProps,
            post_id=post_id,
            props=props,
            integration_url=_find_url(props),
            message=message
        )

    @staticmethod
    async def get_cache_message(post_id: str):
        query = PluginsCacheProps.select().where(
            PluginsCacheProps.post_id == post_id
        )
        if await BasePlugin.database_manager.count(query) > 0:
            for data in await BasePlugin.database_manager.execute(query):
                return data

    @staticmethod
    async def delete_cache_message(post_id: str):
        await BasePlugin.database_manager.execute(
            PluginsCacheProps.delete().where(
                PluginsCacheProps.post_id == post_id
            )
        )

    @staticmethod
    async def update_cache_message(
            post_id: str,
            props: dict = None,
            message: str = None,
            integration_url: str = None
    ):
        if props:
            update_data = {}
            if props:
                update_data['props'] = props

            if message:
                update_data['message'] = message

            if integration_url:
                update_data['integration_url'] = integration_url

            await BasePlugin.database_manager.execute(
                PluginsCacheProps.update(
                    **update_data
                ).where(
                    PluginsCacheProps.post_id == post_id
                )
            )

        else:
            await BasePlugin.delete_cache_message(post_id)

    async def check_alive_message(self):
        for row in await BasePlugin.database_manager.execute(PluginsCacheProps.select()):
            post_id = row.post_id

            try:
                self.driver.posts.get_post(
                    post_id=post_id
                )

            except NotEnoughPermissions:
                await self.delete_cache_message(post_id)
