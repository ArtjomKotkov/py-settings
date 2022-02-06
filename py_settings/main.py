from __future__ import annotations

import re
import json
import pathlib

from typing import Iterable


__all__ = ['Settings', 'LocalSettings']


SIMPLE_OPTION_TYPE = str | int | bool | Iterable | None


class Settings:
    
    @staticmethod
    def from_dict(data: dict) -> Settings:
        parent = Settings()

        for key, value in data.items():
            if type(value) == dict:
                value = Settings.from_dict(value)
            setattr(parent, key, value)
        return parent

    def get_by_regex(self, regex_str: re.Pattern) -> Iterable[Settings]:
        output = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Settings) and regex_str.match(attr_name):
                output.append(attr)
        return output

    def get_nested(self) -> Iterable[Settings]:
        return {
            attr_name: getattr(self, attr_name) for attr_name in dir(self) if isinstance(getattr(self, attr_name), Settings)
        }

    def has(self, key: str) -> bool:
        return hasattr(self, key)
    
    @classmethod
    def _load_settings_file(cls, path: str) -> dict:
        with pathlib.Path(path).open() as file:
            return json.load(file)


class LocalSettings:
    def __init__(self, settings: Settings | LocalSettings):
        for key, path, type_ in self._attributes:
            if isinstance(settings, Settings):
                value = self._get_option_by_path(settings, path)
            else:
                value = getattr(settings, key)
            assert isinstance(value, type_), f'[{self.__class__.__name__}] Invalid {key} setting option definition, {type_} expected, got {type(value)}'
            setattr(self, key, value)

    @property
    def _attributes(self) -> Iterable:
        return (
            (key, getattr(self, key), type_) if hasattr(self, key) else (key, None, type_)
            for key, type_
            in self.__annotations__.items()
        )

    @staticmethod
    def _get_option_by_path(settings: Settings, path_str: str) -> SIMPLE_OPTION_TYPE | Settings:
        paths = path_str.split('.')
        for path in paths:
            try:
                settings = getattr(settings, path)
            except AttributeError as e:
                print(f'Path "{path_str}" is unreachable! Failed on {path}.')
                raise e
        return settings
