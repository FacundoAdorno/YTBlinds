import urllib.request
import zipfile
from pathlib import Path


def download_file(url: str, destination_dir: str | Path) -> Path:
    """
    Descarga un archivo desde una URL a un directorio destino.

    Args:
        url: URL del archivo que se desea descargar.
        destination_dir: Directorio donde se guardará el archivo.

    Returns:
        Path: Ruta del archivo descargado.

    Raises:
        OSError: Si ocurre un error al crear o escribir el archivo.
        ValueError: Si la URL no contiene un nombre de archivo.
    """
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(url.split("?")[0].rstrip("/")).name

    if not filename:
        raise ValueError("La URL no contiene un nombre de archivo.")

    destination_file = destination_dir / filename

    urllib.request.urlretrieve(url, destination_file)

    return destination_file


def extract_zip(
    zip_path: str | Path,
    destination_dir: str | Path
) -> Path:
    """
    Descomprime un archivo ZIP en un directorio destino.

    Args:
        zip_path: Ruta del archivo ZIP.
        destination_dir: Directorio donde se extraerá el contenido.

    Returns:
        Path: Directorio donde se extrajeron los archivos.

    Raises:
        FileNotFoundError: Si el archivo ZIP no existe.
        zipfile.BadZipFile: Si el archivo no es un ZIP válido.
    """
    zip_path = Path(zip_path)
    destination_dir = Path(destination_dir)

    if not zip_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo ZIP: {zip_path}"
        )

    destination_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(destination_dir)

    return destination_dir
