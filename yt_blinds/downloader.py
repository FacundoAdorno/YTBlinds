import json
import os
import sys
import urllib.request
import urllib.parse

# Añadir vendor al sys.path para importar yt_dlp localmente desde vendor/yt_dlp
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vendor_dir = os.path.join(base_dir, "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class Downloader:
    """Encargado de buscar y descargar usando el paquete vendored de yt-dlp en vendor/yt_dlp."""

    def __init__(self, context):
        if context is None:
            raise TypeError("Debe especificar indicar una instancia de AppContext.")
        self.app_context = context

    def search_videos(self, query, max_results=40):
        if not query.strip():
            return [], ""

        if query.startswith("http://") or query.startswith("https://"):
            return [{
                'id': 'url',
                'title': f"URL Directa: {query}",
                'url': query
            }], "URL Directa"

        if yt_dlp is None:
            return self._fallback_search(query, max_results)

        results = []
        source_used = "Desconocido"

        # 1. Búsqueda con yt_dlp (vendored)
        try:
            ydl_opts = {
                'format': 'best',
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'noproxy': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'id': entry.get('id'),
                                'title': entry.get('title', 'Sin título'),
                                'duration': entry.get('duration', 0),
                                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
            if results:
                source_used = "yt-dlp (Vendored)"
        except Exception:
            pass

        # 2. Fallback: API de sugerencias JSON de YouTube
        if not results:
            try:
                encoded_query = urllib.parse.quote(query)
                suggestions_url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={encoded_query}"
                req = urllib.request.Request(suggestions_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if len(data) > 1 and isinstance(data[1], list):
                        for idx, suggestion in enumerate(data[1][:max_results]):
                            results.append({
                                'id': f'sugg_{idx}',
                                'title': suggestion,
                                'url': f"ytsearch:{suggestion}"
                            })
                if results:
                    source_used = "API de sugerencias JSON de YouTube"
            except Exception:
                pass

        # 3. Fallback local
        if not results:
            results, source_used = self._fallback_search(query, max_results)

        return results, source_used

    def _fallback_search(self, query, max_results):
        return [{
            'id': 'mock1',
            'title': f"[Modo Sin Conexión] Resultado simulado para: {query}",
            'url': f"https://www.youtube.com/results?search_query={query}"
        }], "Modo de Respaldo Local"

    def download_media(self, url, download_type='video', output_path=None, progress_callback=None, completion_callback=None, title=None, video_id=None):
        import threading

        from .history import sanitize_filename

        def run():
            if not output_path:
                download_dir = self.app_context.get_download_path(download_type)
            else:
                # Si el valor en configuración tiene ~ en su config (referenciando al HOME del usario), lo expando.
                # Sino, es una ruta absoluta.
                download_dir = output_path if output_path.find('~', 0, 1) == -1 else os.path.expanduser(output_path)

            vid = video_id or url
            self.app_context.history_manager.check_and_cleanup_missing_file(vid, download_type, download_dir)

            if yt_dlp is None:
                if completion_callback:
                    completion_callback(False, "El paquete vendored yt_dlp no está disponible en vendor/yt_dlp.")
                return

            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'noproxy': True,
            }

            if download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                })

            downloaded_file_path = [None]
            if progress_callback:
                def hook(d):
                    if d['status'] == 'downloading':
                        p = d.get('_percent_str', '0%').strip()
                        progress_callback(f"Descargando: {p}")
                    elif d['status'] == 'finished':
                        progress_callback("Descarga finalizada. Procesando archivo...")
                        downloaded_file_path[0] = d.get('filename')
                ydl_opts['progress_hooks'] = [hook]

            try:
                self.app_context.accessibility_manager.announce(f"Iniciando descarga de {download_type}...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not downloaded_file_path[0] and info:
                        downloaded_file_path[0] = ydl.prepare_filename(info)
                    raw_title = title or (info.get('title') if info else url)
                    actual_vid = (info.get('id') if info else None) or vid

                final_path = downloaded_file_path[0]
                if final_path and os.path.exists(final_path):
                    dir_name, file_name = os.path.split(final_path)
                    name_part, ext_part = os.path.splitext(file_name)
                    sanitized_name = sanitize_filename(name_part)
                    new_filename = sanitized_name + ext_part
                    new_filepath = os.path.join(dir_name, new_filename)

                    if final_path != new_filepath:
                        if os.path.exists(new_filepath):
                            os.remove(new_filepath)
                        os.rename(final_path, new_filepath)

                    saved_path = new_filepath
                    downloaded_title = sanitized_name
                else:
                    saved_path = download_dir
                    downloaded_title = sanitize_filename(raw_title)

                self.app_context.history_manager.add_download(actual_vid, downloaded_title, saved_path, download_type)

                self.app_context.accessibility_manager.announce("Descarga completada con éxito.")
                if completion_callback:
                    completion_callback(True, "Descarga completada con éxito.")
            except Exception as e:
                err_msg = f"Error en la descarga: {str(e)}"
                self.app_context.accessibility_manager.announce(err_msg)
                if completion_callback:
                    completion_callback(False, err_msg)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def get_video_details(self, url):
        if yt_dlp is None:
            return None
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True, 'noproxy': True, 'extract_flat': False}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if url.startswith("ytsearch:"):
                    search_info = ydl.extract_info(url, download=False)
                    if 'entries' in search_info and search_info['entries']:
                        entry = search_info['entries'][0]
                        url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"

                info = ydl.extract_info(url, download=False)
                if info:
                    return {
                        'title': info.get('title', 'Desconocido'),
                        'uploader': info.get('uploader') or info.get('channel', 'Desconocido'),
                        'upload_date': info.get('upload_date', 'Desconocida'),
                        'duration': info.get('duration', 0),
                        'categories': info.get('categories', ['Desconocida']),
                        'description': info.get('description', 'Sin descripción')
                    }
        except Exception as e:
            pass
        return None
