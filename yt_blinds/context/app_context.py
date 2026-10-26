import configparser
import os
import platform
import subprocess
from ..downloader import Downloader
from ..history import DownloadHistoryManager
from ..accessibility import AccessibilityManager

class AppContext:
    """Contexto centralizado de la aplicación que administra servicios y dependencias."""
    def __init__(self):
        # Specify the base path for the project
        self.project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        self.config = self._load_config()
        self.history_manager = DownloadHistoryManager(
            db_relative_path = self.config['DATA']['db_relativepath_dir'],
            db_filename = self.config['DATA']['db_path_filename'],
        )
        self.downloader = Downloader(self)

        self.accessibility_manager = AccessibilityManager(self)

    def _load_config(self):
        config_parser = configparser.ConfigParser(interpolation=None)
        config_path = os.path.join(self.project_path, "config", "ytblinds.ini")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    # Limpiar espacios en blanco al inicio de cada línea antes de parsear
                    cleaned_lines = [line.lstrip() for line in f]
                config_parser.read_string("".join(cleaned_lines))
            except configparser.Error as e:
                print(f"Error al parsear la configuración: {e}")
        return config_parser

    def get_download_path(self, download_type='video'):
        key = 'download_path_video' if download_type == 'video' else 'download_path_audio'
        output_path = self.config['DATA'].get(key, '~/Descargas').strip()
        if not output_path:
            download_dir = os.path.expanduser("~/Descargas")
        else:
            download_dir = output_path if output_path.find('~', 0, 1) == -1 else os.path.expanduser(output_path)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        return download_dir

    def open_folder(self, download_type='video'):
        folder_path = self.get_download_path(download_type)
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            print("Error al abrir carpeta:", repr(e))

app_context = AppContext()
