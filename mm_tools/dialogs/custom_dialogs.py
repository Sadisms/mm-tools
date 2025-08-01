from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class SelectOption:
    label: str
    value: str
    icon_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "label": self.label,
            "value": self.value
        }
        if self.icon_url:
            result["icon_url"] = self.icon_url
        return result


class CustomDialogElement:
    def __init__(self, element_type: str, name: str, label: Optional[str] = None, 
                 required: bool = False, on_update: bool = False, 
                 value: Any = None, placeholder: Optional[str] = None):
        self.type = element_type
        self.name = name
        self.label = label
        self.required = required
        self.on_update = on_update
        self.value = value
        self.placeholder = placeholder
        
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "name": self.name,
            "required": self.required
        }
        
        if self.label:
            result["label"] = self.label
        if self.on_update:
            result["on_update"] = self.on_update
        if self.value is not None:
            result["value"] = self.value
        if self.placeholder:
            result["placeholder"] = self.placeholder
            
        return result


class TextElement(CustomDialogElement):
    def __init__(self, name: str, label: Optional[str] = None, required: bool = False,
                 on_update: bool = False, value: Optional[str] = None, 
                 placeholder: Optional[str] = None, min_length: Optional[int] = None,
                 max_length: Optional[int] = None, is_number: bool = False):
        super().__init__("text", name, label, required, on_update, value, placeholder)
        self.min_length = min_length
        self.max_length = max_length
        self.is_number = is_number
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.max_length is not None:
            result["max_length"] = self.max_length
        if self.is_number:
            result["is_number"] = self.is_number
        return result


class TextAreaElement(CustomDialogElement):
    def __init__(self, name: str, label: Optional[str] = None, required: bool = False,
                 on_update: bool = False, value: Optional[str] = None, 
                 placeholder: Optional[str] = None, rows: int = 1,
                 min_length: Optional[int] = None, max_length: Optional[int] = None):
        super().__init__("textarea", name, label, required, on_update, value, placeholder)
        self.rows = rows
        self.min_length = min_length
        self.max_length = max_length
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["rows"] = self.rows
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.max_length is not None:
            result["max_length"] = self.max_length
        return result


class SelectElement(CustomDialogElement):
    def __init__(self, name: str, options: List[SelectOption], 
                 label: Optional[str] = None, required: bool = False,
                 on_update: bool = False, value: Optional[str] = None,
                 is_multi: bool = False):
        super().__init__("select", name, label, required, on_update, value)
        self.options = options
        self.is_multi = is_multi
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["options"] = [option.to_dict() for option in self.options]
        if self.is_multi:
            result["is_multi"] = self.is_multi
        return result


class CheckboxElement(CustomDialogElement):
    
    def __init__(self, name: str, label: Optional[str] = None, 
                 on_update: bool = False, value: bool = False):
        super().__init__("checkbox", name, label, False, on_update, value)
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["required"] = False
        return result


class RadioElement(CustomDialogElement):
    def __init__(self, name: str, options: List[SelectOption], 
                 label: Optional[str] = None, required: bool = False,
                 on_update: bool = False, value: Optional[str] = None):
        super().__init__("radio", name, label, required, on_update, value)
        self.options = options
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["options"] = [option.to_dict() for option in self.options]
        return result


class StaticTextElement(CustomDialogElement):
    def __init__(self, label: str, name: Optional[str] = None):
        super().__init__("static_text", name or "", label, False, False)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "label": self.label
        }
        if self.name:
            result["name"] = self.name
        return result


class FileElement(CustomDialogElement):    
    def __init__(self, name: str, label: Optional[str] = None, required: bool = False,
                 on_update: bool = False, is_multi: bool = False,
                 allowed_types: Optional[List[str]] = None, max_size: Optional[int] = None):
        super().__init__("file", name, label, required, on_update)
        self.is_multi = is_multi
        self.allowed_types = allowed_types or []
        self.max_size = max_size
        
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.is_multi:
            result["is_multi"] = self.is_multi
        if self.allowed_types:
            result["allowed_types"] = self.allowed_types
        if self.max_size is not None:
            result["max_size"] = self.max_size
        return result


class CustomDialog:    
    def __init__(
        self, 
        title: str, 
        user_id: str, elements: List[CustomDialogElement],
        callback_url_on_submit: Optional[str] = None,
        callback_url_on_update: Optional[str] = None,
        callback_id: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None, 
        submit_button_text: Optional[str] = None,
        close_button_text: Optional[str] = None
):
        self.title = title
        self.user_id = user_id
        self.elements = elements
        self.callback_url_on_submit = callback_url_on_submit
        self.callback_url_on_update = callback_url_on_update
        self.callback_id = callback_id
        self.state = state or {}
        self.submit_button_text = submit_button_text
        self.close_button_text = close_button_text
        self.dialog_id: Optional[str] = None
        

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "title": self.title,
            "user_id": self.user_id,
            "elements": [element.to_dict() for element in self.elements]
        }
        
        if self.callback_url_on_submit:
            result["callback_url_on_submit"] = self.callback_url_on_submit
        if self.callback_url_on_update:
            result["callback_url_on_update"] = self.callback_url_on_update
        if self.callback_id:
            result["callback_id"] = self.callback_id
        if self.state:
            result["state"] = self.state
        if self.submit_button_text:
            result["submit_button_text"] = self.submit_button_text
        if self.close_button_text:
            result["close_button_text"] = self.close_button_text
            
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

