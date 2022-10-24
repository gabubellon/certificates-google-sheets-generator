import toml
from loguru import logger


class Settings:
    def __init__(self):
        pass

    def load_settings(self, file_path):
        self.settings = toml.load(file_path)

    def get_setting(self, setting):
        return self.settings.get(setting)
