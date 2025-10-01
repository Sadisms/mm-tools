from typing import List, Union


class ActionElement:
    def to_dict(self):
        raise NotImplementedError


class Button(ActionElement):
    def __init__(
            self,
            text: str,
            action_id: str,
            url: str,
            value: str = None,
            style: str = None,
            session_id: str = None
    ):
        self.value = value
        self.text = text
        self.url = url
        self.style = style
        self.action_id = action_id
        self.session_id = session_id

    def to_dict(self) -> dict:
        data = {
            "name": self.text,
            "type": "button",
            "integration": {
                "url": self.url + f'/{self.action_id}',
                "context": {
                    "value": self.value,
                    "session_id": self.session_id
                }
            }
        }

        if self.style:
            data["style"] = self.style

        return data


class Field:
    def __init__(
            self,
            title: str = None,
            text: str = None,
            short: bool = False
    ):
        self.title = title
        self.text = text
        self.short = short

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'value': self.text,
            'short': self.short
        }


class SelectOption:
    def __init__(
            self,
            text: str,
            value: str
    ):
        self.text = text
        self.value = value

    def to_dict(self):
        return {
            'text': self.text,
            'value': self.value
        }


class Select(ActionElement):
    def __init__(
            self,
            action_id: str,
            url: str,
            options: list[SelectOption],
            text: str = '',
            block_id: str = None,
            default: SelectOption = None,
            session_id: str = None
    ):
        self.text = text
        self.action_id = action_id
        self.options = options
        self.url = url
        self.block_id = block_id
        self.session_id = session_id

        if default:
            self.default = default.value

        else:
            self.default = None

    def to_dict(self):
        return {
            "name": self.text,
            "type": "select",
            "default": self.default,
            "integration": {
                "url": self.url + f'/{self.action_id}',
                "context": {
                    "block_id": self.block_id,
                    "session_id": self.session_id
                }
            },
            "options": [
                x.to_dict()
                for x in self.options
            ]
        }


class SelectUsers(ActionElement):
    def __init__(
            self,
            action_id: str,
            url: str,
            text: str = '',
            block_id: str = None,
            session_id: str = None
    ):
        self.text = text
        self.action_id = action_id
        self.url = url
        self.block_id = block_id
        self.session_id = session_id

    def to_dict(self):
        return {
            "name": self.text,
            "type": "select",
            "data_source": "users",
            "integration": {
                "url": self.url + f'/{self.action_id}',
                "context": {
                    "block_id": self.block_id,
                    "session_id": self.session_id
                }
            },
        }

class Attachment:
    def __init__(
            self,
            fields: List[Field] = None,
            actions: List[Union[ActionElement]] = None,
            text: str = None,
            title: str = None,
            title_link: str = None,
            color: str = None,
            fallback: str = None,
            pretext: str = None,
            author_name: str = None,
            author_link: str = None,
            author_icon: str = None,
            image_url: str = None,
            thumb_url: str = None,
            footer: str = None,
            footer_icon: str = None
    ):
        self.actions = actions or []
        self.fields = fields or []
        self.text = text
        self.title_link = title_link
        self.title = title
        self.color = color
        self.fallback = fallback
        self.pretext = pretext
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon

    def to_dict(self) -> dict:
        attachments = {'attachments': [{}]}

        # Fields from Mattermost attachment specification
        if self.fallback:
            attachments['attachments'][0]['fallback'] = self.fallback

        if self.pretext:
            attachments['attachments'][0]['pretext'] = self.pretext

        if self.author_name:
            attachments['attachments'][0]['author_name'] = self.author_name
            if self.author_link:
                attachments['attachments'][0]['author_link'] = self.author_link
            if self.author_icon:
                attachments['attachments'][0]['author_icon'] = self.author_icon

        if self.fields:
            attachments['attachments'][0]['fields'] = [
                x.to_dict()
                for x in self.fields
            ]

        if self.actions:
            attachments['attachments'][0]['actions'] = [
                x.to_dict()
                for x in self.actions
            ]

        if self.text:
            attachments['attachments'][0]['text'] = self.text

        if self.title:
            attachments['attachments'][0]['title'] = self.title

            if self.title_link:
                attachments['attachments'][0]['title_link'] = self.title_link

        if self.color:
            attachments['attachments'][0]['color'] = self.color

        if self.image_url:
            attachments['attachments'][0]['image_url'] = self.image_url

        if self.thumb_url:
            attachments['attachments'][0]['thumb_url'] = self.thumb_url

        if self.footer:
            attachments['attachments'][0]['footer'] = self.footer
            if self.footer_icon:
                attachments['attachments'][0]['footer_icon'] = self.footer_icon

        return attachments

    @staticmethod
    def glue_attachments(
            attachments: List['Attachment']
    ):
        return {
            'attachments': [
                x.to_dict()['attachments'][0]
                for x in attachments
            ]
        }

