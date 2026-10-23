import os
import shutil
import tarfile
from pathlib import Path

from .utils.file_helpers import download_file


class Updater:
    """Gestiona la actualización del paquete vendored de yt-dlp descargando el tar.gz oficial."""
    @staticmethod
    def update_yt_dlp():
        try:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz"
            base_dir = Path(__file__).resolve().parent.parent
            tmp_dir = base_dir / "data" / "tmp_update"
            vendor_dir = base_dir / "vendor"

            # 1. Descargar tar.gz usando file_helpers.download_file
            tar_path = download_file(url, tmp_dir)

            # 2. Extraer tar.gz
            extract_dir = tmp_dir / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)

            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(extract_dir)

            # 3. Buscar el directorio yt_dlp dentro de lo extraído y reemplazar vendor/yt_dlp
            src_yt_dlp = None
            for root, dirs, files in os.walk(extract_dir):
                if "yt_dlp" in dirs and "__init__.py" in os.listdir(os.path.join(root, "yt_dlp")):
                    src_yt_dlp = Path(root) / "yt_dlp"
                    break

            if not src_yt_dlp or not src_yt_dlp.exists():
                return False, "No se encontró el paquete yt_dlp en el archivo descargado."

            target_vendor_yt_dlp = vendor_dir / "yt_dlp"
            print("Existe ? ", target_vendor_yt_dlp.exists())
            if target_vendor_yt_dlp.exists():
                print("Entre")
                shutil.rmtree(target_vendor_yt_dlp)
            print("Existe ? ", target_vendor_yt_dlp.exists())

            target_vendor_yt_dlp.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_yt_dlp, target_vendor_yt_dlp, dirs_exist_ok=True)

            # Limpiar temporales
            shutil.rmtree(tmp_dir, ignore_errors=True)

            return True, "yt-dlp (vendor) actualizado correctamente."
        except Exception as e:
            return False, f"Error al actualizar yt-dlp: {str(e)}"
