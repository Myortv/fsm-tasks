import logging

from typing import Optional, Any


import toml

from pydantic import BaseModel


from core.configs import settings


class FromTomlFile(BaseModel):
    def __init__(self, path: str, *args, **kwargs):
        with open(path, 'r') as file:
            loaded_data = toml.load(file).get(self.__class__.__name__)
            return super().__init__(**loaded_data)

    def get(
        self,
        key: str,
        default: Optional[Any] = None,
    ):
        if settings.DEBUG:
            logging.info(f"From-toml-file key: {key}")
        return self.model_dump().get(key, default)
