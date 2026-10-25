import os
import tkinter as tk
from pathlib import Path

from ..utils.audio_helpers import play_audio_file


def resolver_ruta(ruta_texto):
    """
    Expande variables de entorno (%USERPROFILE%, $HOME) y la tilde (~)
    de forma compatible con Windows y Linux usando pathlib.
    """
    # 1. os.path.expandvars resuelve %VAR% (Windows) o $VAR (Linux)
    # 2. .expanduser() resuelve la tilde (~) al directorio home en cualquier sistema
    return Path(os.path.expandvars(ruta_texto)).expanduser()

class HistoryWindow:

    def __init__(self):
        pass

    @staticmethod
    def show_history_window(root, color_scheme, context):
        context.accessibility_manager.stop_announces()
        play_audio_file(context.project_path + "/assets/sounds/low/open_window_low.wav")
        context.accessibility_manager.announce("Abriendo historial de archivos descargados. Navegue filtros mediante Tab. Cierre con Escape.")

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
        entry_filter.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Posicionado en campo de filtro por nombre."))
        entry_filter.bind("<Control-a>", lambda e: (entry_filter.select_range(0, tk.END), "break")[1])
        history_win.bind("<Alt-b>", lambda e: entry_filter.focus_set())

        # Botón de Filtrar al lado
        btn_filter = tk.Button(filter_frame, text="Filtrar", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 11, "bold"), relief=tk.FLAT, cursor="hand2")
        btn_filter.pack(side=tk.LEFT, padx=5)
        btn_filter.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Botón Filtrar"))
        btn_filter.bind("<Return>", lambda e: [play_audio_file(context.project_path + "/assets/sounds/low/enter_low.wav"), load_history_items()])
        btn_filter.bind("<space>", lambda e: [play_audio_file(context.project_path + "/assets/sounds/low/enter_low.wav"), load_history_items()])

        # Selector de tipo (Video / Audio)
        type_frame = tk.Frame(history_win, bg=color_scheme.bg_color)
        type_frame.pack(fill=tk.X, padx=15, pady=5)

        current_type = tk.StringVar(value="video")

        def on_filter_key(event, context):
            context.accessibility_manager.stop_announces()
            if event.keysym == "BackSpace":
                context.accessibility_manager.announce("Borrar")
            if event.keysym == "space":
                current_text = entry_filter.get()
                play_audio_file(context.project_path + "/assets/sounds/low/spacebar_low.wav")
                context.accessibility_manager.announce(current_text)
            elif event.char and event.char.isprintable():
                play_audio_file(context.project_path + "/assets/sounds/akey.wav")
                context.accessibility_manager.announce(event.char)

        def load_history_items(focus_on_list=True):
            listbox_history.delete(0, tk.END)
            q = entry_filter.get().strip()
            t = current_type.get()
            items = context.history_manager.get_history(download_type=t, filter_query=q)
            for item in items:
                display_str = f"[{t.upper()}]. {item[0]}. Ruta: {resolver_ruta(item[1])}. Fecha de descarga: {item[2]}"
                listbox_history.insert(tk.END, display_str)
            if (len(items) > 0 and focus_on_list):
                listbox_history.focus_set()
            context.accessibility_manager.announce(f"Se encontraron {len(items)} elementos en {t}s.")

        btn_video_tab = tk.Button(type_frame, text="Videos", command=lambda: [current_type.set("video"), load_history_items()], bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_video_tab.pack(side=tk.LEFT, padx=5)
        btn_video_tab.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Filtro Sólo Videos"))

        btn_audio_tab = tk.Button(type_frame, text="Audios", command=lambda: [current_type.set("audio"), load_history_items()], bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_audio_tab.pack(side=tk.LEFT, padx=5)
        btn_audio_tab.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Filtro Sólo Audios"))

        entry_filter.bind("<KeyPress>", lambda e: on_filter_key(e, context))
        entry_filter.bind("<Return>", lambda e: [play_audio_file(context.project_path + "/assets/sounds/low/enter_low.wav"), load_history_items()])

        # Listbox navegable de historial
        list_container = tk.Frame(history_win, bg=color_scheme.bg_color)
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        listbox_history = tk.Listbox(
            list_container,
            font=("Arial", 12),
            height=14,
            bg="#111111",
            fg=color_scheme.fg_color,
            selectbackground=color_scheme.accent_color,
            selectforeground="#000000"
        )
        listbox_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox_history.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Posicionado en resultados historial. Navegue con flechas arriba y abajo."))

        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=listbox_history.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox_history.config(yscrollcommand=scrollbar.set)

        def on_history_select(event):
            selection = listbox_history.curselection()
            if selection:
                context.accessibility_manager.stop_announces()
                play_audio_file(context.project_path + "/assets/sounds/arrow_key.wav")
                idx = selection[0]
                text = listbox_history.get(idx)
                context.accessibility_manager.announce(f"Seleccionado: {text}")

        listbox_history.bind("<<ListboxSelect>>", on_history_select)

        btn_close = tk.Button(history_win, text="Cerrar (Escape)", command=history_win.destroy, bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=10)
        btn_close.bind("<FocusIn>", lambda e: context.accessibility_manager.announce("Botón Cerrar"))

        history_win.bind("<Escape>", lambda e: [play_audio_file(context.project_path + "/assets/sounds/low/close_window_low.wav"), history_win.destroy()])

        load_history_items(focus_on_list=False)
        history_win.after(300, lambda: entry_filter.focus_set())
