from typing import Optional, Any

from aiogram.types import InlineKeyboardButton


class Button:
    callback_suffix: str = "_callback"

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.txt = text

    @property
    def text(self):
        return self.txt

    @property
    def callback(self):
        return self.name.lower() + self.callback_suffix

    def get_button(self,
                   new_text: Optional[str] = None,
                   parameters: Optional[list[Any]] = None,
                   ) -> InlineKeyboardButton:
        callback = self.callback
        if parameters:
            callback = callback + "#" + "#".join([str(p) for p in parameters])

        text = new_text if new_text else self.txt
        return InlineKeyboardButton(text=text, callback_data=callback)

    def has_that_callback(self, received_callback: str):
        return received_callback.startswith(self.callback)