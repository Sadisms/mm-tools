from uuid import uuid4


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

    def to_dict(self) -> dict:
        return {
            'type': self.type,
            'subtype': self.subtype,
            'display_name': self.display_name,
            'options': [
                x.to_dict()
                for x in self.options
            ] if self.options else None,
            'optional': self.optional,
            'default': self.default,
            'name': self.element_id ,
            'help_text': self.help_text,
            'placeholder': self.placeholder
        }


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
            optional: bool = False
    ):
        super().__init__()
        self.type = 'radio'
        self.options = options
        self.optional = optional
        self.display_name = display_name
        self.default = default or options[0].value
        self.element_id = element_id


class CheckBoxElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            default: bool = False,
            optional: bool = False
    ):
        super().__init__()
        self.type = 'bool'
        self.display_name = display_name
        self.element_id = element_id
        self.default = str(default).lower()
        self.optional = optional


class StaticSelectElement(DialogElement):
    def __init__(
            self,
            display_name: str,
            element_id: str,
            options: list[ElementOption],
            optional: bool = False
    ):
        super().__init__()
        self.type = 'select'
        self.options = options
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id


class InputTextElement(DialogElement):
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
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


class InputTextAreaElement(DialogElement):
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
        self.type = 'textarea'
        self.optional = optional
        self.display_name = display_name
        self.element_id = element_id
        self.default = default
        self.help_text = help_text
        self.placeholder = placeholder


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


class Dialog:
    def __init__(
            self,
            title: str,
            action_id: str,
            elements: list[DialogElement],
            trigger_id: str,
            url: str,
            callback_id: str = None
    ):
        self.title = title
        self.action_id = action_id
        self.callback_id = callback_id
        self.elements = elements
        self.trigger_id = trigger_id
        self.url = url

    def to_dict(self) -> dict:
        return {
            'trigger_id': self.trigger_id,
            'url': self.url + '/' + self.action_id,
            'dialog': {
                'title': self.title,
                'callback_id': f"{uuid4().hex}:{self.callback_id}",
                'elements': [
                    x.to_dict()
                    for x in self.elements
                ]
            }
        }
