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
        self.min_date = None
        self.max_date = None
        self.time_interval = None
        self.multiselect = False
        self.data_source_url = None
        self.refresh = False

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
        if self.min_date is not None:
            data['min_date'] = self.min_date
        if self.max_date is not None:
            data['max_date'] = self.max_date
        if self.time_interval is not None:
            data['time_interval'] = self.time_interval
        if self.multiselect:
            data['multiselect'] = self.multiselect
        if self.data_source_url is not None:
            data['data_source_url'] = self.data_source_url
        if self.refresh:
            data['refresh'] = True

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
            default: ElementOption | str = None,
            help_text: str = None,
            placeholder: str = None,
            multiselect: bool = False,
            refresh: bool = False
    ):
        super().__init__()
        self.type = 'select'
        self.options = options
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.help_text = help_text
        self.placeholder = placeholder
        self.multiselect = multiselect
        self.refresh = refresh

        if default:
            self.default = default if isinstance(default, str) else default.value


class SelectChannelElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            optional: bool = False,
            default: ElementOption | str = None,
            help_text: str = None,
            placeholder: str = None,
            multiselect: bool = False
    ):
        super().__init__()
        self.type = 'select'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.data_source = 'channels'
        self.help_text = help_text
        self.placeholder = placeholder
        self.multiselect = multiselect

        if default:
            self.default = default if isinstance(default, str) else default.value


class SelectUserElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            optional: bool = False,
            default: str = None,
            help_text: str = None,
            placeholder: str = None,
            multiselect: bool = False
    ):
        super().__init__()
        self.type = 'select'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.data_source = 'users'
        self.help_text = help_text
        self.placeholder = placeholder
        self.multiselect = multiselect

        if default:
            self.default = default


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


class DateElement(DialogElement):
    """Date picker element for selecting dates without time.
    
    Minimum Server Version: 11.1
    """
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None,
            min_date: str = None,
            max_date: str = None
    ):
        super().__init__()
        self.type = 'date'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder
        self.min_date = min_date
        self.max_date = max_date


class DateTimeElement(DialogElement):
    """DateTime picker element for selecting date and time with timezone support.
    
    Minimum Server Version: 11.1
    """
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: str = None,
            optional: bool = False,
            help_text: str = None,
            placeholder: str = None,
            min_date: str = None,
            max_date: str = None,
            time_interval: int = 60
    ):
        super().__init__()
        self.type = 'datetime'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder
        self.min_date = min_date
        self.max_date = max_date
        self.time_interval = time_interval


class DynamicSelectElement(DialogElement):
    """Select element with dynamic options loaded from external API.
    
    Minimum Server Version: 11.0
    """
    def __init__(
            self,
            display_name: str,
            element_id: str,
            data_source_url: str,
            optional: bool = False,
            default: str = None,
            help_text: str = None,
            placeholder: str = None,
            multiselect: bool = False
    ):
        super().__init__()
        self.type = 'select'
        self.data_source = 'dynamic'
        self.data_source_url = data_source_url
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder
        self.multiselect = multiselect


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
            payload: dict = None,
            is_multistep: bool = False,
            source_url: str | None = None,
            step: str = ""
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
        self.is_multistep = is_multistep
        self.source_url = source_url
        self.step = step

    def _build_dialog_dict(self) -> dict:
        state_data: dict = {'session_id': self.session_id}
        if self.step:
            state_data['step'] = self.step
        if self.payload:
            state_data['payload'] = compress_json(self.payload)

        return {
            'title': self.title,
            'introduction_text': self.introduction_text,
            'callback_id': f"{uuid4().hex}:{self.callback_id}",
            'state': json.dumps(state_data, separators=(',', ':')),
            'elements': [x.to_dict() for x in self.elements],
            **({'submit_label': self.submit_label} if self.submit_label else {}),
            **({'notify_on_cancel': self.notify_on_cancel} if self.notify_on_cancel else {}),
            **({'icon_url': self.icon_url} if self.icon_url else {}),
            **({'is_multistep': self.is_multistep} if self.is_multistep else {}),
            **({'source_url': self.source_url} if self.source_url else {}),
        }

    def to_dict(self) -> dict:
        return {
            'trigger_id': self.trigger_id,
            'url': self.url + '/' + self.action_id,
            'dialog': self._build_dialog_dict(),
        }

    def to_form_response(self) -> dict:
        """Returns the response payload for multistep step transitions and field refresh.

        Use when responding to dialog_submission (intermediate step) or
        dialog_field_refresh events instead of closing the dialog.
        """
        return {'type': 'form', 'form': self._build_dialog_dict()}
