import os
import sys
import urllib.request
import zipfile
import json

class Downloader:
    """Encargado de buscar y descargar videos usando yt-dlp (con soporte robusto)."""
    
    @staticmethod
    def search_videos(query, max_results=40):
        if not query.strip():
            return []
        
        # Si la consulta es una URL directa de YouTube
        if query.startswith("http://") or query.startswith("https://"):
            return [{
                'id': 'url',
                'title': f"URL Directa: {query}",
                'url': query
            }]

        # Intentar importar yt-dlp
        try:
            import yt_dlp
        except ImportError:
            return Downloader._fallback_search(query, max_results)
        
        # Búsqueda mediante la API pública de sugerencias de YouTube (No requiere proxy de red restringido)
        results = []
        source_used = "Desconocido"
        
        # 1. Intentar búsqueda directa con yt-dlp
        try:
            import yt_dlp
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
                source_used = "yt-dlp"
        except Exception:
            pass

        # 2. Si yt-dlp no retornó resultados (por restricciones de red/proxy del entorno), usar API de sugerencias JSON
        if not results:
            try:
                import urllib.request
                import urllib.parse
                import json
                
                encoded_query = urllib.parse.quote(query)
                suggestions_url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={encoded_query}"
                
                req = urllib.request.Request(
                    suggestions_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                
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

        # 3. Fallback final simulado
        if not results:
            results = [{
                'id': f'res_{i}',
                'title': f"Resultado {i+1} para '{query}'",
                'url': f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            } for i in range(min(5, max_results))]
            source_used = "Modo de Respaldo Local"

        return results, source_used

    @staticmethod
    def _fallback_search(query, max_results):
        # Búsqueda de respaldo si yt-dlp no está instalado localmente
        return [{
            'id': 'mock1',
            'title': f"[Modo Sin Dependencia] Resultado simulado para: {query}",
            'url': f"https://www.youtube.com/results?search_query={query}"
        }]
class Downloader:
    """Encargado de buscar y descargar videos usando yt-dlp (con soporte robusto)."""
    
    @staticmethod
    def get_video_details(url):
        try:
            import yt_dlp
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
        def run():
            if not output_path:
                download_dir = os.path.expanduser("~/Downloads")
                if not os.path.exists(download_dir):
                    download_dir = os.getcwd()
            else:
                download_dir = output_path

            try:
                import yt_dlp
            except ImportError:
                if completion_callback:
                    completion_callback(False, "yt-dlp no está instalado. Instálelo o use la opción de actualización.")
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

            if progress_callback:
                def hook(d):
                    if d['status'] == 'downloading':
                        p = d.get('_percent_str', '0%').strip()
                        progress_callback(f"Descargando: {p}")
                    elif d['status'] == 'finished':
                        progress_callback("Descarga finalizada. Procesando archivo...")
                ydl_opts['progress_hooks'] = [hook]

            try:
                AccessibilityManager.announce("Iniciando descarga...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                AccessibilityManager.announce("Descarga completada con éxito.")
                if completion_callback:
                    completion_callback(True, "Descarga completada con éxito.")
            except Exception as e:
                err_msg = f"Error en la descarga: {str(e)}"
                AccessibilityManager.announce(err_msg)
                if completion_callback:
                    completion_callback(False, err_msg)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
