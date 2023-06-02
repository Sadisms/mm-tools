from typing import List, Union


class Button:
    def __init__(
            self,
            text: str,
            action_id: str,
            url: str,
            value: str = None,
            style: str = None
    ):
        self.value = value
        self.text = text
        self.url = url
        self.style = style
        self.action_id = action_id

    def to_dict(self) -> dict:
        data = {
            "name": self.text,
            "type": "button",
            "integration": {
                "url": self.url + f'/{self.action_id}',
                "context": {
                    "value": self.value
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


class Select:
    def __init__(
            self,
            action_id: str,
            url: str,
            options: list[SelectOption],
            text: str = '',
            block_id: str = None
    ):
        self.text = text
        self.action_id = action_id
        self.options = options
        self.url = url
        self.block_id = block_id

    def to_dict(self):
        return {
            "name": self.text,
            "type": "select",
            "integration": {
                "url": self.url + f'/{self.action_id}',
                "context": {
                    "block_id": self.block_id
                }
            },
            "options": [
                x.to_dict()
                for x in self.options
            ]
        }


class Attachment:
    def __init__(
            self,
            fields: List[Field] = None,
            actions: List[Union[Button, Select]] = None,
            text: str = None,
    ):
        self.actions = actions or []
        self.fields = fields or []
        self.text = text

    def to_dict(self) -> dict:
        attachments = {'attachments': [{}]}

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
