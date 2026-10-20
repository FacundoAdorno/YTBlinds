import tkinter as tk

from yt_blinds.accessibility import accessibility_manager
from yt_blinds.context.app_context import app_context


class HistoryWindow:

    def __init__(self):
        pass

    @staticmethod
    def show_history_window(root, color_scheme):
        accessibility_manager.stop_announces()
        accessibility_manager.announce("Abriendo historial de archivos descargados.")

        history_win = tk.Toplevel(root)
        history_win.title("Historial de Archivos Descargados - YTBlinds")
        history_win.geometry("750x550")
        history_win.configure(bg=color_scheme.bg_color)
        history_win.grab_set()

        lbl_title = tk.Label(history_win, text="Historial de Archivos Descargados (Use Tab para navegar, Escape para cerrar)", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        lbl_title.pack(anchor=tk.W, padx=15, pady=10)

        # Filtro por nombre
        filter_frame = tk.Frame(history_win, bg=color_scheme.bg_color)
        filter_frame.pack(fill=tk.X, padx=15, pady=5)

        lbl_filter = tk.Label(filter_frame, text="Filtrar por nombre:", bg=color_scheme.bg_color, fg=color_scheme.fg_color, font=("Arial", 11, "bold"))
        lbl_filter.pack(side=tk.LEFT, padx=5)

        entry_filter = tk.Entry(filter_frame, font=("Arial", 12), bg="#222222", fg=color_scheme.fg_color, insertbackground=color_scheme.fg_color)
        entry_filter.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        entry_filter.bind("<FocusIn>", lambda e: accessibility_manager.announce("Campo de filtro por nombre."))

        # Selector de tipo (Video / Audio)
        type_frame = tk.Frame(history_win, bg=color_scheme.bg_color)
        type_frame.pack(fill=tk.X, padx=15, pady=5)

        current_type = tk.StringVar(value="video")

        def load_history_items():
            listbox_history.delete(0, tk.END)
            q = entry_filter.get().strip()
            t = current_type.get()
            items = app_context.history_manager.get_history(download_type=t, filter_query=q)
            for item in items:
                display_str = f"[{item[2]}] {item[0]} - Ruta: {item[1]}"
                listbox_history.insert(tk.END, display_str)
            accessibility_manager.announce(f"Se encontraron {len(items)} elements en {t}s.")

        btn_video_tab = tk.Button(type_frame, text="Videos", command=lambda: [current_type.set("video"), load_history_items()], bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_video_tab.pack(side=tk.LEFT, padx=5)
        btn_video_tab.bind("<FocusIn>", lambda e: accessibility_manager.announce("Pestaña Videos"))

        btn_audio_tab = tk.Button(type_frame, text="Audios", command=lambda: [current_type.set("audio"), load_history_items()], bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_audio_tab.pack(side=tk.LEFT, padx=5)
        btn_audio_tab.bind("<FocusIn>", lambda e: accessibility_manager.announce("Pestaña Audios"))

        entry_filter.bind("<KeyRelease>", lambda e: load_history_items())

        # Listbox navegable de historial
        list_container = tk.Frame(history_win, bg=color_scheme.bg_color)
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        listbox_history = tk.Listbox(
            list_container,
            font=("Arial", 11),
            bg="#111111",
            fg=color_scheme.fg_color,
            selectbackground=color_scheme.accent_color,
            selectforeground="#000000"
        )
        listbox_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox_history.bind("<FocusIn>", lambda e: accessibility_manager.announce("Lista de archivos descargados. Use flechas arriba y abajo para navegar."))

        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=listbox_history.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox_history.config(yscrollcommand=scrollbar.set)

        def on_history_select(event):
            selection = listbox_history.curselection()
            if selection:
                accessibility_manager.stop_announces()
                idx = selection[0]
                text = listbox_history.get(idx)
                accessibility_manager.announce(f"Seleccionado: {text}")

        listbox_history.bind("<<ListboxSelect>>", on_history_select)

        btn_close = tk.Button(history_win, text="Cerrar (Escape)", command=history_win.destroy, bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=10)
        btn_close.bind("<FocusIn>", lambda e: accessibility_manager.announce("Botón Cerrar"))

        history_win.bind("<Escape>", lambda e: history_win.destroy())

        load_history_items()
        history_win.after(300, lambda: entry_filter.focus_set())
