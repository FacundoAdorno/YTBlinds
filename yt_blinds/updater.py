import subprocess
import sys
import os

class Updater:
    """Gestiona la actualización de yt-dlp desde la propia aplicación."""
    @staticmethod
    def update_yt_dlp():
        try:
            python_executable = sys.executable
            # Intento actualizar yt-dlp usando pip con --upgrade
            result = subprocess.run(
                [python_executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True,
                check=True
            )
            return True, "yt-dlp actualizado correctamente."
        except Exception as e:
            return False, f"Error al actualizar yt-dlp: {str(e)}"
