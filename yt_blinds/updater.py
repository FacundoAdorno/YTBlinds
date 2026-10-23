import subprocess
import sys
import os

class Updater:
    """Gestiona la actualización de yt-dlp desde la propia aplicación."""
    @staticmethod
    def update_yt_dlp():
        try:
            if getattr(sys, 'frozen', False):
                cmds = [
                    ["pip", "install", "--upgrade", "yt-dlp"],
                    ["python3", "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    ["python", "-m", "pip", "install", "--upgrade", "yt-dlp"]
                ]
            else:
                cmds = [
                    [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"]
                ]

            success = False
            last_err = ""
            for cmd in cmds:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    success = True
                    break
                except Exception as ex:
                    last_err = str(ex)

            if success:
                return True, "yt-dlp actualizado correctamente."
            else:
                return False, f"No se pudo actualizar yt-dlp. Detalle: {last_err}"
        except Exception as e:
            return False, f"Error al actualizar yt-dlp: {str(e)}"
