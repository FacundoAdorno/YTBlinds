import tkinter as tk
from tkinter import ttk, messagebox
import threading
from .downloader import Downloader
from .updater import Updater
from .accessibility import AccessibilityManager

class MainWindow:
    """Ventana principal accesible para personas no videntes."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("YTBlinds - Descargador Accesible de YouTube")
        self.root.geometry("800x650")
        
        # Configurar colores de alto contraste (Fondo oscuro, texto blanco/amarillo)
        self.bg_color = "#000000"
        self.fg_color = "#FFFFFF"
        self.accent_color = "#FFFF00" # Amarillo brillante
        self.select_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        
        # Estilo ttk para alto contraste
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color, fieldbackground=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Arial", 12, "bold"))
        self.style.configure("TButton", background="#222222", foreground=self.accent_color, font=("Arial", 12, "bold"), borderwidth=2)
        self.style.map("TButton", background=[('active', '#444444')])

        self.create_widgets()
        self.bind_shortcuts()
        
        AccessibilityManager.announce("YTBlinds iniciado. Presione F1 para ayuda de atajos, o navegue con Tabulador.")

    def create_widgets(self):
        # Marco superior: Búsqueda
        search_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=10)
        search_frame.pack(fill=tk.X)
        
        lbl_search = tk.Label(search_frame, text="Buscar video o pegar URL (Alt+B):", bg=self.bg_color, fg=self.accent_color, font=("Arial", 12, "bold"))
        lbl_search.pack(anchor=tk.W, pady=2)
        
        self.entry_search = tk.Entry(search_frame, font=("Arial", 14), bg="#222222", fg=self.fg_color, insertbackground=self.fg_color)
        self.entry_search.pack(fill=tk.X, pady=5)
        self.entry_search.focus_set()
        
        btn_search = tk.Button(search_frame, text="Buscar (Enter)", command=self.perform_search, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        btn_search.pack(anchor=tk.W, pady=2)

        # Marco central: Resultados de Búsqueda
        results_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=5)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        lbl_results = tk.Label(results_frame, text="Resultados (Use Flechas Arriba/Abajo para navegar):", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11, "bold"))
        lbl_results.pack(anchor=tk.W)
        
        # Listbox con scrollbar accesible
        list_container = tk.Frame(results_frame, bg=self.bg_color)
        list_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.listbox_results = tk.Listbox(
            list_container, 
            font=("Arial", 12), 
            bg="#111111", 
            fg=self.fg_color, 
            selectbackground=self.accent_color,
            selectforeground="#000000",
            activestyle='dotbox'
        )
        self.listbox_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_results.bind("<<ListboxSelect>>", self.on_select_item)
        self.listbox_results.bind("<Return>", lambda e: self.download_selected("video"))

        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.listbox_results.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_results.config(yscrollcommand=scrollbar.set)

        # Marco inferior: Acciones y Estado
        action_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=10)
        action_frame.pack(fill=tk.X)
        
        self.btn_video = tk.Button(action_frame, text="Descargar Video (Alt+V)", command=lambda: self.download_selected("video"), bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        self.btn_video.pack(side=tk.LEFT, padx=5)
        
        self.btn_audio = tk.Button(action_frame, text="Descargar Audio MP3 (Alt+A)", command=lambda: self.download_selected("audio"), bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        self.btn_audio.pack(side=tk.LEFT, padx=5)

        self.btn_update = tk.Button(action_frame, text="Actualizar yt-dlp (Alt+U)", command=self.update_ytdlp, bg="#222222", fg="#00FF00", font=("Arial", 11, "bold"))
        self.btn_update.pack(side=tk.RIGHT, padx=5)

        # Estado y Progreso
        status_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=5)
        status_frame.pack(fill=tk.X)
        
        self.lbl_status = tk.Label(status_frame, text="Listo.", bg=self.bg_color, fg=self.accent_color, font=("Arial", 11, "bold"))
        self.lbl_status.pack(anchor=tk.W)

        self.current_results = []

    def bind_shortcuts(self):
        # Atajos de teclado accesibles globales
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<Alt-b>", lambda e: self.entry_search.focus_set())
        self.root.bind("<Alt-v>", lambda e: self.download_selected("video"))
        self.root.bind("<Alt-a>", lambda e: self.download_selected("audio"))
        self.root.bind("<Alt-u>", lambda e: self.update_ytdlp())
        self.entry_search.bind("<Return>", lambda e: self.perform_search())
        self.listbox_results.bind("<i>", lambda e: self.show_video_info())
        self.listbox_results.bind("<I>", lambda e: self.show_video_info())

    def show_help(self):
        help_text = (
            "Ayuda de Atajos de Teclado (YTBlinds):\n\n"
            "• Tab / Shift+Tab: Moverse entre elementos.\n"
            "• Alt + B: Ir al cuadro de búsqueda.\n"
            "• Enter en Búsqueda: Ejecutar búsqueda.\n"
            "• Flechas Arriba/Abajo: Navegar por los resultados.\n"
            "• Enter en Resultado o Alt + V: Descargar como Video.\n"
            "• Alt + A: Descargar como Audio MP3.\n"
            "• Alt + U: Actualizar yt-dlp a la última versión.\n"
            "• F1: Mostrar esta ayuda."
        )
        AccessibilityManager.announce("Mostrando ventana de ayuda.")
        messagebox.showinfo("Ayuda de Atajos - YTBlinds", help_text)

    def perform_search(self):
        query = self.entry_search.get().strip()
        if not query:
            AccessibilityManager.announce("Escriba un término de búsqueda o URL.")
            messagebox.showwarning("Aviso", "Escriba un término de búsqueda o URL de YouTube.")
            return

        self.lbl_status.config(text="Buscando...")
        AccessibilityManager.announce("Buscando videos, por favor espere.")

        def search_thread():
            if query.startswith("http://") or query.startswith("https://"):
                self.current_results = [{
                    'id': 'direct',
                    'title': f"URL Directa: {query}",
                    'url': query
                }]
                source_desc = "URL Directa"
            else:
                self.current_results, source_desc = Downloader.search_videos(query, max_results=40)
            
            self.root.after(0, lambda: self.update_results_ui(source_desc))

        threading.Thread(target=search_thread, daemon=True).start()

    def show_video_info(self):
        selection = self.listbox_results.curselection()
        if not selection:
            AccessibilityManager.announce("Ningún elemento seleccionado para ver información.")
            messagebox.showwarning("Aviso", "Seleccione un video de la lista para ver su información detallada.")
            return

        index = selection[0]
        item = self.current_results[index]
        url = item['url']

        self.lbl_status.config(text=f"Obteniendo información detallada...")
        AccessibilityManager.announce("Obteniendo información detallada del video, por favor espere.")

        def fetch_info_thread():
            details = Downloader.get_video_details(url)
            self.root.after(0, lambda: self._display_video_info(details, item['title']))

        threading.Thread(target=fetch_info_thread, daemon=True).start()

    def _display_video_info(self, details, fallback_title):
        if not details:
            msg = f"Título: {fallback_title}\nCanal: Desconocido\nFecha: Desconocida\nDuración: Desconocida\nCategoría: Desconocida\nDescripción: No disponible"
        else:
            dur_min = details['duration'] // 60 if details['duration'] else 0
            dur_sec = details['duration'] % 60 if details['duration'] else 0
            duration_str = f"{dur_min} min {dur_sec} seg" if details['duration'] else "Desconocida"
            
            categories_str = ", ".join(details['categories']) if details['categories'] else "Desconocida"
            
            msg = (
                f"• Título: {details['title']}\n\n"
                f"• Canal: {details['uploader']}\n\n"
                f"• Fecha de subida: {details['upload_date']}\n\n"
                f"• Duración: {duration_str}\n\n"
                f"• Categoría: {categories_str}\n\n"
                f"• Descripción:\n{details['description']}"
            )

        AccessibilityManager.announce("Información detallada cargada.")
        
        # Ventana modal accesible de información
        info_win = tk.Toplevel(self.root)
        info_win.title("Información Detallada del Video")
        info_win.geometry("600x500")
        info_win.configure(bg=self.bg_color)
        
        lbl_title = tk.Label(info_win, text="Detalles del Video (Presione Escape para cerrar)", bg=self.bg_color, fg=self.accent_color, font=("Arial", 12, "bold"))
        lbl_title.pack(anchor=tk.W, padx=10, pady=10)

        txt_info = tk.Text(info_win, wrap=tk.WORD, bg="#111111", fg=self.fg_color, font=("Arial", 11), padx=10, pady=10)
        txt_info.insert(tk.END, msg)
        txt_info.config(state=tk.DISABLED)
        txt_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        txt_info.focus_set()

        btn_close = tk.Button(info_win, text="Cerrar (Escape)", command=info_win.destroy, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=10)

        info_win.bind("<Escape>", lambda e: info_win.destroy())
        self.listbox_results.delete(0, tk.END)
        if not self.current_results:
            self.lbl_status.config(text="No se encontraron resultados.")
            AccessibilityManager.announce("No se encontraron resultados.")
            return

        for item in self.current_results:
            self.listbox_results.insert(tk.END, item['title'])
        
        status_msg = f"Se encontraron {len(self.current_results)} resultados (Fuente: {source_desc})."
        self.lbl_status.config(text=status_msg)
        AccessibilityManager.announce(f"Se encontraron {len(self.current_results)} resultados usando {source_desc}.")
        self.listbox_results.focus_set()
        if self.current_results:
            self.listbox_results.selection_set(0)

    def on_select_item(self, event):
        selection = self.listbox_results.curselection()
        if selection:
            index = selection[0]
            title = self.current_results[index]['title']
            AccessibilityManager.announce(f"Seleccionado: {title}")

    def download_selected(self, download_type):
        selection = self.listbox_results.curselection()
        if not selection:
            AccessibilityManager.announce("Ningún elemento seleccionado para descargar.")
            messagebox.showwarning("Aviso", "Seleccione un video de la lista para descargar.")
            return

        index = selection[0]
        item = self.current_results[index]
        url = item['url']
        
        # Si es una consulta de sugerencia, resolver la URL real de búsqueda mediante yt-dlp
        if url.startswith("ytsearch:"):
            self.lbl_status.config(text=f"Buscando enlace directo para: {item['title']}...")
            def resolve_and_download():
                try:
                    import yt_dlp
                    ydl_opts = {'default_search': 'ytsearch1', 'extract_flat': True, 'quiet': True, 'noproxy': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if 'entries' in info and info['entries']:
                            real_url = info['entries'][0].get('url') or f"https://www.youtube.com/watch?v={info['entries'][0].get('id')}"
                        else:
                            real_url = url
                except Exception:
                    real_url = f"https://www.youtube.com/results?search_query={item['title']}"

                self.root.after(0, lambda: self._start_real_download(real_url, download_type))

            import threading
            threading.Thread(target=resolve_and_download, daemon=True).start()
        else:
            self._start_real_download(url, download_type)

    def _start_real_download(self, url, download_type):
        self.lbl_status.config(text=f"Iniciando descarga...")
        
        def progress(msg):
            self.root.after(0, lambda: self.lbl_status.config(text=msg))

        def completion(success, msg):
            self.root.after(0, lambda: messagebox.showinfo("Estado de Descarga", msg) if success else messagebox.showerror("Error", msg))

        Downloader.download_media(url, download_type=download_type, progress_callback=progress, completion_callback=completion)

    def update_ytdlp(self):
        self.lbl_status.config(text="Actualizando yt-dlp...")
        AccessibilityManager.announce("Actualizando yt-dlp, por favor espere.")

        def update_thread():
            success, msg = Updater.update_yt_dlp()
            def finish():
                self.lbl_status.config(text=msg)
                AccessibilityManager.announce(msg)
                messagebox.showinfo("Actualización", msg)
            self.root.after(0, finish)

        threading.Thread(target=update_thread, daemon=True).start()
