import configparser
import os
from ..downloader import Downloader
from ..history import DownloadHistoryManager

class AppContext:
    """Contexto centralizado de la aplicación que administra servicios y dependencias."""
    def __init__(self):
        self.config = self._load_config()
        self.history_manager = DownloadHistoryManager(
            db_relative_path = self.config['DATA']['db_relativepath_dir'],
            db_filename = self.config['DATA']['db_path_filename'],
        )
        self.downloader = Downloader(self)

    def _load_config(self):
        config_parser = configparser.ConfigParser()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "ytblinds.ini")
        if os.path.exists(config_path):
            config_parser.read(config_path)
        return config_parser
