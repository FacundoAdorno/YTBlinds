import locale
import platform
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import NamedTuple

from yt_blinds.utils.audio_helpers import play_audio_file

from ..updater import Updater
from .detail_ui import DetailWindow
from .help_ui import HelpWindow
from .history_ui import HistoryWindow
from .about_ui import AboutWindow


class MainWindow:
    """Ventana principal accesible para personas no videntes."""

    def __init__(self, root, context):
        self.app_context = context
        locale.setlocale(locale.LC_TIME, self.app_context.config['GENERAL']['locale'])

        self.root = root
        self.root.title("Descargador Accesible de YouTube - YTBlinds")
        if platform.system() == "Windows":
            root.iconbitmap(context.project_path + '/assets/images/ytblinds.ico')
        else:   # could be Linux
            icon_image = tk.PhotoImage(file=context.project_path + '/assets/images/ytblinds.png')
            root.iconphoto(False, icon_image)
        win_h = self.app_context.config['GENERAL'].getint('win_height', 650)
        win_w = self.app_context.config['GENERAL'].getint('win_width', 800)
        self.root.geometry(f"{win_w}x{win_h}")

        # Configurar colores de alto contraste (Fondo oscuro, texto blanco/amarillo)
        self.color_scheme = ColorScheme(bg_color=self.app_context.config['STYLES']['bg_color'],
            fg_color=self.app_context.config['STYLES']['fg_color'],
            accent_color=self.app_context.config['STYLES']['accent_color'],
            select_color=self.app_context.config['STYLES']['select_color'])
        self.root.configure(bg=self.color_scheme.bg_color)

        # Estilo ttk para alto contraste
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(".", background=self.color_scheme.bg_color, foreground=self.color_scheme.fg_color, fieldbackground=self.color_scheme.bg_color)
        self.style.configure("TLabel", background=self.color_scheme.bg_color, foreground=self.color_scheme.fg_color, font=("Arial", 12, "bold"))
        self.style.configure("TButton", background="#222222", foreground=self.color_scheme.accent_color, font=("Arial", 12, "bold"), borderwidth=2)
        self.style.map("TButton", background=[('active', '#444444')])
        self.style.configure("Horizontal.TProgressbar", troughcolor="#222222", background=self.color_scheme.accent_color, darkcolor=self.color_scheme.accent_color, lightcolor=self.color_scheme.accent_color, bordercolor="#444444")

        self.create_widgets()
        self.bind_shortcuts()

        # Interceptar el cierre de la ventana principal para pedir doble Escape
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.root.bind("<Escape>", lambda e: self.confirm_exit())

        self.root.after(300, lambda: self.app_context.accessibility_manager.announce("Presione F1 para ayuda. Presione Escape para salir."))
        self.root.after(310, lambda: self.entry_search.focus_set())

    def close_app(self, event=None):
        import sys
        self.app_context.accessibility_manager.stop_announces()
        try:
            play_audio_file(self.app_context.project_path + "/assets/sounds/low/exit_window_low.wav")
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

    def confirm_exit(self):
        self.app_context.accessibility_manager.stop_announces()
        play_audio_file(self.app_context.project_path + "/assets/sounds/low/open_window_low.wav")
        self.root.after(300, lambda: self.app_context.accessibility_manager.announce("¿Desea salir de la aplicación? Presione Escape nuevamente para confirmar, o Enter para cancelar."))

        exit_win = tk.Toplevel(self.root)
        exit_win.title("Confirmar Salida - YTBlinds")
        exit_win.geometry("450x200")
        exit_win.configure(bg=self.color_scheme.bg_color)
        exit_win.grab_set() # Hacer ventana modal

        lbl_msg = tk.Label(
            exit_win,
            text="¿Está seguro de que desea salir?\n\nPresione ESCAPE nuevamente para confirmar la salida,\no ENTER para cancelar.",
            bg=self.color_scheme.bg_color,
            fg=self.color_scheme.accent_color,
            font=("Arial", 12, "bold"),
            justify=tk.CENTER
        )
        lbl_msg.pack(expand=True, padx=20, pady=20)

        btn_frame = tk.Frame(exit_win, bg=self.color_scheme.bg_color)
        btn_frame.pack(pady=10)

        btn_cancel = tk.Button(btn_frame, text="Cancelar (Enter)", command=exit_win.destroy, bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_cancel.pack(side=tk.LEFT, padx=10)
        btn_cancel.focus_set()

        btn_confirm = tk.Button(btn_frame, text="Salir (Escape)", command=self.close_app, bg="#222222", fg="#FF5555", font=("Arial", 11, "bold"))
        btn_confirm.pack(side=tk.LEFT, padx=10)

        def _exit_app(event):
            self.close_app()

        exit_win.bind("<Escape>", lambda e: _exit_app(e))
        exit_win.bind("<Return>", lambda e: exit_win.destroy())

    def create_widgets(self):
        # Marco superior: Búsqueda
        search_frame = tk.Frame(self.root, bg=self.color_scheme.bg_color, padx=10, pady=10)
        search_frame.pack(fill=tk.X)

        lbl_search = tk.Label(search_frame, text="Buscar video o pegar URL (Alt+B):", bg=self.color_scheme.bg_color, fg=self.color_scheme.accent_color, font=("Arial", 12, "bold"))
        lbl_search.pack(anchor=tk.W, pady=2)

        self.entry_search = tk.Entry(search_frame, font=("Arial", 14), bg="#222222", fg=self.color_scheme.fg_color, insertbackground=self.color_scheme.fg_color)
        self.entry_search.pack(fill=tk.X, pady=5)
        self.entry_search.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Cursor posicionado en campo de búsqueda. Escriba su búsqueda y luego presione Enter."))
        self.entry_search.bind("<Key>", self.on_search_key)
        self.entry_search.bind("<Control-a>", lambda e: (self.entry_search.select_range(0, tk.END), "break")[1])

        self.btn_search = tk.Button(search_frame, text="Buscar (Enter)", command=self.perform_search, bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_search.pack(anchor=tk.W, pady=2)
        self.btn_search.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Buscar (Enter)"))

        # Marco central: Resultados de Búsqueda
        results_frame = tk.Frame(self.root, bg=self.color_scheme.bg_color, padx=10, pady=5)
        results_frame.pack(fill=tk.BOTH, expand=True)

        lbl_results = tk.Label(results_frame, text="Resultados (Use Flechas Arriba/Abajo para navegar):", bg=self.color_scheme.bg_color, fg=self.color_scheme.fg_color, font=("Arial", 11, "bold"))
        lbl_results.pack(anchor=tk.W)

        # Listbox con scrollbar accesible
        list_container = tk.Frame(results_frame, bg=self.color_scheme.bg_color)
        list_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox_results = tk.Listbox(
            list_container,
            font=("Arial", 12),
            bg="#111111",
            fg=self.color_scheme.fg_color,
            selectbackground=self.color_scheme.accent_color,
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
        action_frame = tk.Frame(self.root, bg=self.color_scheme.bg_color, padx=10, pady=10)
        action_frame.pack(fill=tk.X)

        # Primera fila de botones
        row1 = tk.Frame(action_frame, bg=self.color_scheme.bg_color)
        row1.pack(fill=tk.X, pady=3)

        self.btn_video = tk.Button(row1, text="Descargar Video (Alt+V)", command=lambda: self.download_selected("video"), bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_video.pack(side=tk.LEFT, padx=5)
        self.btn_video.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Descargar Video (Alt+V)"))

        self.btn_audio = tk.Button(row1, text="Descargar Audio MP3 (Alt+A)", command=lambda: self.download_selected("audio"), bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_audio.pack(side=tk.LEFT, padx=5)
        self.btn_audio.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Descargar Audio MP3 (Alt+A)"))

        self.btn_history = tk.Button(row1, text="Historial (Alt+H)", command=lambda: HistoryWindow.show_history_window(self.root, self.color_scheme, self.app_context), bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_history.pack(side=tk.LEFT, padx=5)
        self.btn_history.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Historial de Descargas (Alt+H)"))

        # Segunda fila de botones
        row2 = tk.Frame(action_frame, bg=self.color_scheme.bg_color)
        row2.pack(fill=tk.X, pady=3)

        self.btn_folder_video = tk.Button(row2, text="Carpeta Videos (Ctrl+Alt+V)", command=lambda: self.app_context.open_folder("video"), bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_folder_video.pack(side=tk.LEFT, padx=5)
        self.btn_folder_video.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Abrir Carpeta Videos (Control+Alt+V)"))

        self.btn_folder_audio = tk.Button(row2, text="Carpeta Audios (Ctrl+Alt+F)", command=lambda: self.app_context.open_folder("audio"), bg="#222222", fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.btn_folder_audio.pack(side=tk.LEFT, padx=5)
        self.btn_folder_audio.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Abrir Carpeta Audios (Control+Alt+A)"))

        self.btn_update = tk.Button(row2, text="Actualizar yt-dlp (Alt+U)", command=self.update_ytdlp, bg="#222222", fg="#00FF00", font=("Arial", 11, "bold"))
        self.btn_update.pack(side=tk.RIGHT, padx=5)
        self.btn_update.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Botón Actualizar yt-dlp (Alt+U)"))

        # Estado y Progreso
        status_frame = tk.Frame(self.root, bg=self.color_scheme.bg_color, padx=10, pady=5)
        status_frame.pack(fill=tk.X)

        self.lbl_status = tk.Label(status_frame, text="Listo.", bg=self.color_scheme.bg_color, fg=self.color_scheme.accent_color, font=("Arial", 11, "bold"))
        self.lbl_status.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=300, mode="determinate", maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar['value'] = 0

        status_frame.bind("<FocusIn>", lambda e: self.app_context.accessibility_manager.announce("Estado actual: " + self.lbl_status.cget("text")))

        self.current_results = []

    def bind_shortcuts(self):
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<F2>", lambda e: AboutWindow.show_about(self.root, self.color_scheme, self.app_context))
        self.root.bind("<Alt-b>", lambda e: self.on_search_focus())
        self.root.bind("<Alt-v>", lambda e: self.download_selected("video"))
        self.root.bind("<Alt-a>", lambda e: self.download_selected("audio"))
        self.root.bind("<Alt-h>", lambda e: HistoryWindow.show_history_window(self.root, self.color_scheme, self.app_context))
        self.root.bind("<Alt-H>", lambda e: HistoryWindow.show_history_window(self.root, self.color_scheme, self.app_context))
        def abrir_carpeta(event, tipo):
            self.app_context.accessibility_manager.announce(f"Abriendo carpeta de {tipo}s.")
            self.app_context.open_folder(tipo)
        self.root.bind("<Control-Alt-v>", lambda e: abrir_carpeta(e, "video"))
        self.root.bind("<Control-Alt-V>", lambda e: abrir_carpeta(e, "video"))
        self.root.bind("<Control-Alt-f>", lambda e: abrir_carpeta(e, "audio"))
        self.root.bind("<Control-Alt-F>", lambda e: abrir_carpeta(e, "audio"))
        self.root.bind("<Alt-u>", lambda e: self.update_ytdlp())
        self.root.bind("<Escape>", lambda e: self.close_app())
        self.entry_search.bind("<Return>", lambda e: self.perform_search())
        self.listbox_results.bind("<i>", lambda e: self.show_video_info())
        self.listbox_results.bind("<I>", lambda e: self.show_video_info())

    def show_help(self):
        HelpWindow.show_help(self.root, self.color_scheme, self.app_context)


    def perform_search(self):
        self.app_context.accessibility_manager.stop_announces()

        query = self.entry_search.get().strip()
        if not query:
            self.app_context.accessibility_manager.announce("Escriba un término de búsqueda o URL.")
            messagebox.showwarning("Aviso", "Escriba un término de búsqueda o URL de YouTube.")
            return

        self.lbl_status.config(text="Buscando...")
        play_audio_file(self.app_context.project_path + "/assets/sounds/low/enter_low.wav")
        self.app_context.accessibility_manager.announce(f"Buscando videos sobre {query}.")

        def search_thread():
            if query.startswith("http://") or query.startswith("https://"):
                self.current_results = [{
                    'id': 'direct',
                    'title': f"URL Directa: {query}",
                    'url': query
                }]
                source_desc = "URL Directa"
            else:
                max_results_displayed = self.app_context.config.getint('YTDLP', 'max_results_displayed') if self.app_context.config.has_option('YTDLP', 'max_results_displayed') else 40
                self.current_results, source_desc = self.app_context.downloader.search_videos(query, max_results_displayed)

            self.root.after(0, lambda: self.update_results_ui(source_desc))

        threading.Thread(target=search_thread, daemon=True).start()

    def show_video_info(self):
        DetailWindow.show_detail_window(self.root, self.color_scheme, self.app_context, self.listbox_results, self.current_results)

    def update_results_ui(self, source_desc=""):
        self.app_context.accessibility_manager.stop_announces()

        self.listbox_results.delete(0, tk.END)
        if not self.current_results:
            self.lbl_status.config(text="No se encontraron resultados.")
            self.app_context.accessibility_manager.announce("No se encontraron resultados.")
            return

        for item in self.current_results:
            self.listbox_results.insert(tk.END, item['title'])

        status_msg = f"Se encontraron {len(self.current_results)} resultados (Fuente: {source_desc})."
        self.lbl_status.config(text=status_msg)
        self.app_context.accessibility_manager.announce(f"Se encontraron {len(self.current_results)} resultados.")
        self.listbox_results.focus_set()
        if self.current_results:
            self.listbox_results.selection_set(0)
            self.on_select_item(None)

    def on_select_item(self, event):
        selection = self.listbox_results.curselection()
        if selection:
            self.app_context.accessibility_manager.stop_announces()
            play_audio_file(self.app_context.project_path + "/assets/sounds/arrow_key.wav")
            index = selection[0]
            title = self.current_results[index]['title']
            self.app_context.accessibility_manager.announce(f"Seleccionado: {title}")

    def on_search_focus(self):
        self.entry_search.focus_set()
        self.entry_search.select_range(0, "end")

    def on_search_key(self, event):
        self.app_context.accessibility_manager.stop_announces()
        if event.keysym == "BackSpace":
            self.app_context.accessibility_manager.announce("Borrar")
        if event.keysym == "space":
            current_text = self.entry_search.get()
            play_audio_file(self.app_context.project_path + "/assets/sounds/low/spacebar_low.wav")
            self.app_context.accessibility_manager.announce(current_text)
        elif event.char and event.char.isprintable():
            play_audio_file(self.app_context.project_path + "/assets/sounds/akey.wav")
            self.app_context.accessibility_manager.announce(event.char)

    def download_selected(self, download_type):
        self.app_context.accessibility_manager.stop_announces()
        selection = self.listbox_results.curselection()
        if not selection:
            self.app_context.accessibility_manager.announce("Ningún elemento seleccionado para descargar.")
            messagebox.showwarning("Aviso", "Seleccione un video de la lista para descargar.")
            return

        index = selection[0]
        item = self.current_results[index]
        url = item['url']
        video_title = item['title']
        video_id = item.get('id') or url

        self.lbl_status.config(text=f"Verificando detalles de descarga...")
        self.app_context.accessibility_manager.announce("Verificando tamaño de descarga.")

        try:
             details = self.app_context.downloader.get_video_details(url)
             if details:
                 size = details.get('video_size', 0) if download_type == 'video' else details.get('audio_size', 0)
                 download_size_before_confirm_gb = self.app_context.config['YTDLP'].getfloat('download_size_before_confirm', 0.5)
                 _download_size_config_bytes = (download_size_before_confirm_gb * 1024 * 1024 * 1024)
                 print(f"size en bytes: {size} > {_download_size_config_bytes} = {size > _download_size_config_bytes}")
                 if size > _download_size_config_bytes:  # check if size is > coeficient GB
                     size_gb = size / (1024 * 1024 * 1024)
                     size_mb = size / (1024 * 1024)
                     msg = f"Tamaño estimado de descarga del {download_type} es de { f"{size_mb:.1f} megabytes" if size_mb < 1024 else f"{size_gb:.2f} gigabytes"}.\n¿Desea continuar con la descarga?"
                     play_audio_file(self.app_context.project_path + "/assets/sounds/low/open_window_low.wav")
                     self.app_context.accessibility_manager.announce(f"{msg}. Presione Enter para aceptar o Escape para cancelar.")
                     continue_download = messagebox.askyesno("Archivo a descargar es grande.", msg, parent=self.root)
                     if not continue_download:
                         play_audio_file(self.app_context.project_path + "/assets/sounds/cancel.wav")
                         self.root.after(0, lambda: self.lbl_status.config(text="Descarga cancelada."))
                         self.app_context.accessibility_manager.announce("Descarga cancelada.")
                         return
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error al verificar el tamaño de descarga: {e}")
            self.root.after(0, lambda: self.lbl_status.config(text="No se pudo verificar el tamaño de la descarga."))
            self.app_context.accessibility_manager.announce( "No se pudo verificar el tamaño de la descarga. La operación fue cancelada.")
            return

        def resolve_and_download():
            # Si es una consulta de sugerencia, resolver la URL real de búsqueda mediante yt-dlp
            if url.startswith("ytsearch:"):
                self.lbl_status.config(text=f"Buscando enlace directo para: {video_title}...")
                try:
                    import yt_dlp
                    ydl_opts = {'default_search': 'ytsearch1', 'extract_flat': True, 'quiet': True, 'noproxy': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if 'entries' in info and info['entries']:
                            entry = info['entries'][0]
                            real_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            resolved_id = entry.get('id') or video_id
                        else:
                            real_url = url
                            resolved_id = video_id
                except Exception:
                    real_url = f"https://www.youtube.com/results?search_query={video_title}"
                    resolved_id = video_id

                self.root.after(0, lambda: self._start_real_download(real_url, download_type, title=video_title, video_id=resolved_id))
            else:
                self.root.after(0, lambda: self._start_real_download(url, download_type, title=video_title, video_id=video_id))

        import threading
        threading.Thread(target=resolve_and_download, daemon=True).start()

    def _start_real_download(self, url, download_type, title=None, video_id=None):
        play_audio_file(self.app_context.project_path + "/assets/sounds/low/tab_low.wav")
        self.lbl_status.config(text=f"Iniciando descarga de {download_type}...")
        self.progress_bar['value'] = 0
        self.last_announced_percent = -1

        # Deshabilitar controles durante la descarga
        self.entry_search.config(state=tk.DISABLED)
        self.btn_search.config(state=tk.DISABLED)
        self.btn_video.config(state=tk.DISABLED)
        self.btn_audio.config(state=tk.DISABLED)
        self.btn_history.config(state=tk.DISABLED)
        self.btn_folder_video.config(state=tk.DISABLED)
        self.btn_folder_audio.config(state=tk.DISABLED)
        self.btn_update.config(state=tk.DISABLED)

        def progress(msg):
            self.app_context.accessibility_manager.stop_announces()
            self.root.after(0, lambda: self.lbl_status.config(text=msg))
            try:
                if "%" in msg:
                    import re
                    clean_msg = re.sub(r'\x1b\[[0-9;]*m', '', msg)
                    percent_str = clean_msg.split(":")[-1].replace("%", "").strip()
                    val = float(percent_str)
                    self.root.after(0, lambda v=val: self.progress_bar.config(value=v))

                    ival = int(val)
                    if (ival % 5 == 0 or ival == 100) and ival != self.last_announced_percent:
                        self.last_announced_percent = ival
                        self.app_context.accessibility_manager.announce(f"Descargando: {ival}%")
            except Exception:
                pass

        def completion(success, msg):
            self.root.after(0, lambda: [
                self.progress_bar.config(value=100 if success else 0),
                self.entry_search.config(state=tk.NORMAL),
                self.btn_search.config(state=tk.NORMAL),
                self.btn_video.config(state=tk.NORMAL),
                self.btn_audio.config(state=tk.NORMAL),
                self.btn_history.config(state=tk.NORMAL),
                self.btn_folder_video.config(state=tk.NORMAL),
                self.btn_folder_audio.config(state=tk.NORMAL),
                self.btn_update.config(state=tk.NORMAL),
                messagebox.showinfo("Estado de Descarga", msg) if success else messagebox.showerror("Error", msg)
            ])
            play_audio_file(self.app_context.project_path + "/assets/sounds/ok.wav")

        self.app_context.downloader.download_media(url, download_type=download_type, progress_callback=progress,
            completion_callback=completion, title=title, video_id=video_id)

    def update_ytdlp(self):
        self.app_context.accessibility_manager.stop_announces()
        self.lbl_status.config(text="Actualizando yt-dlp...")
        self.app_context.accessibility_manager.announce("Actualizando yt-dlp, por favor espere.")

        def update_thread():
            success, msg = Updater.update_yt_dlp()
            def finish(was_success):
                success_msg = ""
                if (was_success):
                    print("Código fuente de yt-dlp fue actualizado correctamente.")
                    success_msg = "Se cerrará la aplicación para hacer efectivos los cambios.\nPresione Enter para finalizar..."
                mensaje = f"{msg}. {success_msg}"
                self.lbl_status.config(text=msg)
                self.app_context.accessibility_manager.announce(mensaje)
                play_audio_file(self.app_context.project_path + "/assets/sounds/low/open_window_low.wav")
                messagebox.showinfo("Actualización", mensaje)
                if (was_success):
                    play_audio_file(self.app_context.project_path + "/assets/sounds/low/exit_window_low.wav")
                    self.close_app()
            self.root.after(0, finish(success))

        threading.Thread(target=update_thread, daemon=True).start()

class ColorScheme(NamedTuple):
    bg_color: str
    fg_color: str
    accent_color: str
    select_color: str
