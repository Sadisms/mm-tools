import json
from uuid import uuid4

from mm_tools.helpers import compress_json


class DialogElement:
    def __init__(self):
        self.type = None
        self.display_name = None
        self.options = []
        self.optional = False
        self.default = ''
        self.element_id = uuid4().hex
        self.help_text = ''
        self.placeholder = ''
        self.subtype = ''
        self.data_source = ''
        self.min_length = None
        self.max_length = None

    def to_dict(self) -> dict:
        data = {
            'type': self.type,
            'subtype': self.subtype,
            'display_name': self.display_name,
            'options': [
                x.to_dict()
                for x in self.options
            ] if self.options else None,
            'optional': self.optional,
            'default': self.default,
            'name': self.element_id,
            'help_text': self.help_text,
            'placeholder': self.placeholder,
            'data_source': self.data_source
        }

        if self.min_length is not None:
            data['min_length'] = self.min_length
        if self.max_length is not None:
            data['max_length'] = self.max_length

        return data


class ElementOption:
    def __init__(
            self,
            text: str,
            value: str
    ):
        self.text = text
        self.value = value

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'value': self.value
        }


class RadioButtonElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            options: list[ElementOption],
            default: str = None,
            optional: bool = False,
            help_text: str = None
    ):
        super().__init__()
        self.type = 'radio'
        self.options = options
        self.optional = optional
        self.display_name = display_name
        self.default = default or options[0].value
        self.element_id = element_id
        self.help_text = help_text


class CheckBoxElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: bool = False,
            optional: bool = False,
            help_text: str = None
    ):
        super().__init__()
        self.type = 'bool'
        self.display_name = display_name
        self.element_id = element_id
        self.default = str(default).lower()
        self.optional = optional
        self.help_text = help_text


class StaticSelectElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            options: list[ElementOption],
            optional: bool = False,
            default: ElementOption = None,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'select'
        self.options = options
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.help_text = help_text
        self.placeholder = placeholder

        if default:
            self.default = default.value


class SelectChannelElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            optional: bool = False,
            default: ElementOption = None,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'select'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.data_source = 'channels'
        self.help_text = help_text
        self.placeholder = placeholder

        if default:
            self.default = default.value


class SelectUserElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            optional: bool = False,
            default: ElementOption = None,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'select'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.data_source = 'users'
        self.help_text = help_text
        self.placeholder = placeholder

        if default:
            self.default = default.value


class InputTextElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None,
            min_length: int | None = None,
            max_length: int | None = None
    ):
        super().__init__()
        self.type = 'text'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length


class InputTextAreaElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None,
            min_length: int | None = None,
            max_length: int | None = None
    ):
        super().__init__()
        self.type = 'textarea'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length


class InputEmailElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'text'
        self.subtype = 'email'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class InputPhoneElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'text'
        self.subtype = 'tel'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class InputNumberElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'text'
        self.subtype = 'number'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class InputPasswordElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'text'
        self.subtype = 'password'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class InputUrlElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None
    ):
        super().__init__()
        self.type = 'text'
        self.subtype = 'url'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class Dialog:
    def __init__(
            self,
            title: str,
            action_id: str,
            elements: list[DialogElement],
            trigger_id: str,
            url: str,
            callback_id: str = "",
            introduction_text: str = "",
            session_id: str = "",
            submit_label: str = None,
            notify_on_cancel: bool = False,
            icon_url: str = None,
            payload: dict = None
    ):
        self.title = title
        self.action_id = action_id
        self.callback_id = callback_id
        self.elements = elements
        self.trigger_id = trigger_id
        self.url = url
        self.introduction_text = introduction_text
        self.session_id = session_id
        self.submit_label = submit_label
        self.notify_on_cancel = notify_on_cancel
        self.icon_url = icon_url
        self.payload = payload

    def to_dict(self) -> dict:
        state_data = {'session_id': self.session_id}
        
        if self.payload:
            state_data['payload'] = compress_json(self.payload)
        
        return {
            'trigger_id': self.trigger_id,
            'url': self.url + '/' + self.action_id,
            'dialog': {
                'title': self.title,
                'introduction_text': self.introduction_text,
                'callback_id': f"{uuid4().hex}:{self.callback_id}",
                'state': json.dumps(state_data, separators=(',', ':')),
                'elements': [
                    x.to_dict()
                    for x in self.elements
                ],
                **({'submit_label': self.submit_label} if self.submit_label else {}),
                **({'notify_on_cancel': self.notify_on_cancel} if self.notify_on_cancel else {}),
                **({'icon_url': self.icon_url} if self.icon_url else {})
            }
        }
