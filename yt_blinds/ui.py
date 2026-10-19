import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import locale
from .downloader import Downloader
from .updater import Updater
from .accessibility import accessibility_manager

class MainWindow:
    """Ventana principal accesible para personas no videntes."""

    def __init__(self, root):
        locale.setlocale(locale.LC_TIME, "es_ES")

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
        self.style.configure("Horizontal.TProgressbar", troughcolor="#222222", background=self.accent_color, darkcolor=self.accent_color, lightcolor=self.accent_color, bordercolor="#444444")

        self.create_widgets()
        self.bind_shortcuts()

        # Interceptar el cierre de la ventana principal para pedir doble Escape
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.root.bind("<Escape>", lambda e: self.confirm_exit())

        self.root.after(300, lambda: accessibility_manager.announce("YTBlinds iniciado. Presione F1 para ayuda de atajos, o navegue con Tabulador. Presione Escape para salir."))
        self.root.after(310, lambda: self.entry_search.focus_set())

    def confirm_exit(self):
        self.root.after(300, lambda: accessibility_manager.announce("¿Desea salir de la aplicación? Presione Escape nuevamente para confirmar, o Enter para cancelar."))

        exit_win = tk.Toplevel(self.root)
        exit_win.title("Confirmar Salida - YTBlinds")
        exit_win.geometry("450x200")
        exit_win.configure(bg=self.bg_color)
        exit_win.grab_set() # Hacer ventana modal

        lbl_msg = tk.Label(
            exit_win,
            text="¿Está seguro de que desea salir?\n\nPresione ESCAPE nuevamente para confirmar la salida,\no ENTER para cancelar.",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Arial", 12, "bold"),
            justify=tk.CENTER
        )
        lbl_msg.pack(expand=True, padx=20, pady=20)

        btn_frame = tk.Frame(exit_win, bg=self.bg_color)
        btn_frame.pack(pady=10)

        btn_cancel = tk.Button(btn_frame, text="Cancelar (Enter)", command=exit_win.destroy, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        btn_cancel.pack(side=tk.LEFT, padx=10)
        btn_cancel.focus_set()

        btn_confirm = tk.Button(btn_frame, text="Salir (Escape)", command=self.root.destroy, bg="#222222", fg="#FF5555", font=("Arial", 11, "bold"))
        btn_confirm.pack(side=tk.LEFT, padx=10)

        exit_win.bind("<Escape>", lambda e: self.root.destroy())
        exit_win.bind("<Return>", lambda e: exit_win.destroy())

    def create_widgets(self):
        # Marco superior: Búsqueda
        search_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=10)
        search_frame.pack(fill=tk.X)

        lbl_search = tk.Label(search_frame, text="Buscar video o pegar URL (Alt+B):", bg=self.bg_color, fg=self.accent_color, font=("Arial", 12, "bold"))
        lbl_search.pack(anchor=tk.W, pady=2)

        self.entry_search = tk.Entry(search_frame, font=("Arial", 14), bg="#222222", fg=self.fg_color, insertbackground=self.fg_color)
        self.entry_search.pack(fill=tk.X, pady=5)
        self.entry_search.bind("<FocusIn>", lambda e: accessibility_manager.announce("Posicionando cursor en campo de búsqueda. Escriba un término o URL de YouTube y presione Enter."))
        self.entry_search.bind("<Key>", self.on_search_key)
        self.entry_search.bind("<Control-a>", lambda e: (self.entry_search.select_range(0, tk.END), "break")[1])

        self.btn_search = tk.Button(search_frame, text="Buscar (Enter)", command=self.perform_search, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        self.btn_search.pack(anchor=tk.W, pady=2)
        self.btn_search.bind("<FocusIn>", lambda e: accessibility_manager.announce("Botón Buscar (Enter)"))

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
        self.btn_video.bind("<FocusIn>", lambda e: accessibility_manager.announce("Botón Descargar Video (Alt+V)"))

        self.btn_audio = tk.Button(action_frame, text="Descargar Audio MP3 (Alt+A)", command=lambda: self.download_selected("audio"), bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        self.btn_audio.pack(side=tk.LEFT, padx=5)
        self.btn_audio.bind("<FocusIn>", lambda e: accessibility_manager.announce("Botón Descargar Audio MP3 (Alt+A)"))

        self.btn_update = tk.Button(action_frame, text="Actualizar yt-dlp (Alt+U)", command=self.update_ytdlp, bg="#222222", fg="#00FF00", font=("Arial", 11, "bold"))
        self.btn_update.pack(side=tk.RIGHT, padx=5)
        self.btn_update.bind("<FocusIn>", lambda e: accessibility_manager.announce("Botón Actualizar yt-dlp (Alt+U)"))

        # Estado y Progreso
        status_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=5)
        status_frame.pack(fill=tk.X)

        self.lbl_status = tk.Label(status_frame, text="Listo.", bg=self.bg_color, fg=self.accent_color, font=("Arial", 11, "bold"))
        self.lbl_status.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=300, mode="determinate", maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar['value'] = 0

        status_frame.bind("<FocusIn>", lambda e: accessibility_manager.announce("Estado actual: " + self.lbl_status.cget("text")))

        self.current_results = []

    def bind_shortcuts(self):
        # Atajos de teclado accesibles globales
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<Alt-b>", lambda e: self.on_search_focus())
        self.root.bind("<Alt-v>", lambda e: self.download_selected("video"))
        self.root.bind("<Alt-a>", lambda e: self.download_selected("audio"))
        self.root.bind("<Alt-u>", lambda e: self.update_ytdlp())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.entry_search.bind("<Return>", lambda e: self.perform_search())
        self.listbox_results.bind("<i>", lambda e: self.show_video_info())
        self.listbox_results.bind("<I>", lambda e: self.show_video_info())

    def show_help(self):
        help_text_tuple = (
            "- Teclas Tab y Shift+Tab: Moverse entre elementos.\n",
            "- Teclas Alt + B: Ir al cuadro de búsqueda.\n",
            "- Tecla Enter (al escribir en Búsqueda): Ejecutar búsqueda.\n",
            "- Flechas Arriba/Abajo: Navegar por los resultados de búsqueda.\n",
            "- Tecla I: Ver información detallada del video (campos navegables por Tab).\n",
            "- Tecla Enter en Resultado ó Teclas Alt + V: Comenzar a descargar resultado como Video.\n",
            "- Teclas Alt + A: Comenzar a descargar resultado como Audio MP3.\n",
            "- Teclas Alt + U: Actualizar yt-dlp a la última versión.\n",
            "- Tecla F1: Mostrar esta ayuda."
        )

        help_text = "".join(help_text_tuple)

        # Ventana modal personalizada para asegurar ajuste automático y accesibilidad
        help_win = tk.Toplevel(self.root)
        help_win.title("Ayuda de Atajos - YTBlinds")
        help_win.geometry("500x400")
        help_win.configure(bg=self.bg_color)

        lbl_title = tk.Label(help_win, text="Ayuda de Atajos (Presione Escape para cerrar)", bg=self.bg_color, fg=self.accent_color, font=("Arial", 11, "bold"))
        lbl_title.pack(anchor=tk.W, padx=15, pady=10)

        txt_help = tk.Text(help_win, wrap=tk.WORD, bg="#111111", fg=self.fg_color, font=("Arial", 14), padx=10, pady=10, relief=tk.SOLID, bd=1)
        txt_help.insert(tk.END, help_text)
        txt_help.config(state=tk.DISABLED)
        txt_help.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        txt_help.focus_set()

        btn_close = tk.Button(help_win, text="Cerrar (Escape)", command=help_win.destroy, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=15)

        help_win.bind("<Escape>", lambda e: help_win.destroy())

        ## Leyendo los textos de ayuda.
        def announce_help():
            accessibility_manager.announce("Mostrando ventana de ayuda.")
            for teclas_atajos in help_text_tuple:
                accessibility_manager.announce(teclas_atajos)

        help_win.after(300, announce_help)


    def perform_search(self):
        query = self.entry_search.get().strip()
        if not query:
            accessibility_manager.announce("Escriba un término de búsqueda o URL.")
            messagebox.showwarning("Aviso", "Escriba un término de búsqueda o URL de YouTube.")
            return

        self.lbl_status.config(text="Buscando...")
        accessibility_manager.announce("Buscando videos, por favor espere.")

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
            accessibility_manager.announce("Ningún elemento seleccionado para ver información.")
            messagebox.showwarning("Aviso", "Seleccione un video de la lista para ver su información detallada.")
            return

        index = selection[0]
        item = self.current_results[index]
        url = item['url']

        self.lbl_status.config(text=f"Obteniendo información detallada...")
        accessibility_manager.announce("Obteniendo información detallada del video, por favor espere.")

        def fetch_info_thread():
            details = Downloader.get_video_details(url)
            self.root.after(0, lambda: self._display_video_info(details, item['title']))

        threading.Thread(target=fetch_info_thread, daemon=True).start()

    def _display_video_info(self, details, fallback_title):
        if not details:
            info_fields = [
                ("Título", fallback_title),
                ("Canal", "Desconocido"),
                ("Fecha de subida", "Desconocida"),
                ("Duración", "Desconocida"),
                ("Categoría", "Desconocida"),
                ("Descripción", "No disponible")
            ]
        else:
            dur_min = details['duration'] // 60 if details['duration'] else 0
            dur_sec = details['duration'] % 60 if details['duration'] else 0
            duration_str = f"{dur_min} min {dur_sec} seg" if details['duration'] else "Desconocida"
            categories_str = ", ".join(details['categories']) if details['categories'] else "Desconocida"

            upload_date_str = details['upload_date']
            try:
                upload = datetime.strptime(details['upload_date'], '%Y%m%d')
                upload_date_str = upload.strftime("%A, %d de %B de %Y")
            except ValueError:
                print("Fecha en formato incorrecto desde origen...")

            info_fields = [
                ("Título", details['title']),
                ("Canal", details['uploader']),
                ("Fecha de subida", upload_date_str),
                ("Duración", duration_str),
                ("Categoría", categories_str),
                ("Descripción", details['description'])
            ]

        accessibility_manager.announce("Información detallada cargada. Use Tab para navegar entre los metadatos.")

        # Ventana modal accesible de información con campos navegables por Tab
        info_win = tk.Toplevel(self.root)
        info_win.title("Información Detallada del Video")
        info_win.geometry("650x550")
        info_win.configure(bg=self.bg_color)

        lbl_title = tk.Label(info_win, text="Detalles del Video (Use Tab para navegar, Escape para cerrar)", bg=self.bg_color, fg=self.accent_color, font=("Arial", 11, "bold"))
        lbl_title.pack(anchor=tk.W, padx=10, pady=10)

        # Contenedor con scroll
        canvas = tk.Canvas(info_win, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(info_win, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Crear campos individuales navegables mediante Tab
        for label_text, value_text in info_fields:
            field_frame = tk.Frame(scrollable_frame, bg=self.bg_color, pady=5)
            field_frame.pack(fill=tk.X, padx=5, expand=True)

            lbl = tk.Label(field_frame, text=f"{label_text}:", bg=self.bg_color, fg=self.accent_color, font=("Arial", 12, "bold"), anchor="w")
            lbl.pack(anchor=tk.W, padx=5, pady=2)

            if label_text == "Descripción":
                # Usar Textarea accesible con scroll para la descripción
                txt_val = tk.Text(field_frame, height=8, wrap=tk.WORD, font=("Arial", 12), bg="#111111", fg="#FFFFFF", insertbackground=self.fg_color, relief=tk.SOLID, bd=1)
                txt_val.insert("1.0", str(value_text))
                txt_val.config(state=tk.DISABLED)
                txt_val.pack(fill=tk.X, expand=True, padx=5, pady=2)
            else:
                entry_val = tk.Entry(field_frame, font=("Arial", 13), bg="#111111", fg="#000000", insertbackground=self.fg_color, relief=tk.SOLID, bd=1)
                entry_val.insert(0, str(value_text))
                entry_val.config(state="readonly")
                entry_val.pack(fill=tk.X, expand=True, padx=5, pady=2)

        # Botón cerrar al final del Tab
        btn_close = tk.Button(scrollable_frame, text="Cerrar (Escape)", command=info_win.destroy, bg="#222222", fg=self.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=15, padx=5, anchor=tk.W)

        info_win.bind("<Escape>", lambda e: info_win.destroy())
        # Dar foco al primer campo navegable
        scrollable_frame.winfo_children()[0].winfo_children()[1].focus_set()

    def update_results_ui(self, source_desc=""):
        self.listbox_results.delete(0, tk.END)
        if not self.current_results:
            self.lbl_status.config(text="No se encontraron resultados.")
            accessibility_manager.announce("No se encontraron resultados.")
            return

        for item in self.current_results:
            self.listbox_results.insert(tk.END, item['title'])

        status_msg = f"Se encontraron {len(self.current_results)} resultados (Fuente: {source_desc})."
        self.lbl_status.config(text=status_msg)
        accessibility_manager.announce(f"Se encontraron {len(self.current_results)} resultados.")
        self.listbox_results.focus_set()
        if self.current_results:
            self.listbox_results.selection_set(0)
            self.on_select_item(None)

    def on_select_item(self, event):
        selection = self.listbox_results.curselection()
        if selection:
            index = selection[0]
            title = self.current_results[index]['title']
            accessibility_manager.announce(f"Seleccionado: {title}")

    def on_search_focus(self):
        self.entry_search.focus_set()
        self.entry_search.select_range(0, "end")

    def on_search_key(self, event):
        if event.keysym == "space":
            current_text = self.entry_search.get()
            accessibility_manager.announce(current_text)
        elif event.char and event.char.isprintable():
            accessibility_manager.announce(event.char)

    def download_selected(self, download_type):
        selection = self.listbox_results.curselection()
        if not selection:
            accessibility_manager.announce("Ningún elemento seleccionado para descargar.")
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
        self.progress_bar['value'] = 0
        self.last_announced_percent = -1

        # Deshabilitar controles durante la descarga
        self.entry_search.config(state=tk.DISABLED)
        self.btn_search.config(state=tk.DISABLED)
        self.btn_video.config(state=tk.DISABLED)
        self.btn_audio.config(state=tk.DISABLED)
        self.btn_update.config(state=tk.DISABLED)

        def progress(msg):
            self.root.after(0, lambda: self.lbl_status.config(text=msg))
            try:
                if "%" in msg:
                    import re
                    clean_msg = re.sub(r'\x1b\[[0-9;]*m', '', msg)
                    percent_str = clean_msg.split(":")[-1].replace("%", "").strip()
                    val = float(percent_str)
                    self.root.after(0, lambda v=val: self.progress_bar.config(value=v))

                    ival = int(val)
                    if ival in (25, 50, 75, 100) and ival != self.last_announced_percent:
                        self.last_announced_percent = ival
                        accessibility_manager.announce(f"Descargando: {ival}%")
            except Exception:
                pass

        def completion(success, msg):
            self.root.after(0, lambda: [
                self.progress_bar.config(value=100 if success else 0),
                self.entry_search.config(state=tk.NORMAL),
                self.btn_search.config(state=tk.NORMAL),
                self.btn_video.config(state=tk.NORMAL),
                self.btn_audio.config(state=tk.NORMAL),
                self.btn_update.config(state=tk.NORMAL),
                messagebox.showinfo("Estado de Descarga", msg) if success else messagebox.showerror("Error", msg)
            ])

        Downloader.download_media(url, download_type=download_type, progress_callback=progress, completion_callback=completion)

    def update_ytdlp(self):
        self.lbl_status.config(text="Actualizando yt-dlp...")
        accessibility_manager.announce("Actualizando yt-dlp, por favor espere.")

        def update_thread():
            success, msg = Updater.update_yt_dlp()
            def finish():
                self.lbl_status.config(text=msg)
                accessibility_manager.announce(msg)
                messagebox.showinfo("Actualización", msg)
            self.root.after(0, finish)

        threading.Thread(target=update_thread, daemon=True).start()
