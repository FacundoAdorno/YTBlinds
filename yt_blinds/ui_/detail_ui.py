import tkinter as tk
from datetime import datetime

from ..utils.audio_helpers import play_audio_file


class DetailWindow:
    """Ventana modal accesible para mostrar información detallada de un video."""
    @staticmethod
    def show_detail_window(root, color_scheme, app_context, listbox_results, current_results):
        selection = listbox_results.curselection()
        if not selection:
            app_context.accessibility_manager.announce("Ningún elemento seleccionado para ver información.")
            return

        index = selection[0]
        item = current_results[index]
        url = item['url']

        app_context.accessibility_manager.announce("Obteniendo información detallada del video.")

        def fetch_info_thread():
            details = app_context.downloader.get_video_details(url)
            root.after(0, lambda: _display_video_info(root, color_scheme, app_context, listbox_results, index, details, item['title']))

        import threading
        threading.Thread(target=fetch_info_thread, daemon=True).start()

def _display_video_info(root, color_scheme, app_context, listbox_results, selected_index, details, fallback_title):
    play_audio_file(app_context.project_path + "/assets/sounds/low/open_window_low.wav")
    app_context.accessibility_manager.stop_announces()

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
        duration_str = f"{dur_min} minutos {dur_sec} segundos" if details['duration'] else "Desconocida"
        categories_str = ", ".join(details['categories']) if details['categories'] else "Desconocida"

        upload_date_str = details['upload_date']
        try:
            upload = datetime.strptime(details['upload_date'], '%Y%m%d')
            upload_date_str = upload.strftime("%A, %d de %B de %Y")
        except ValueError:
            pass

        info_fields = [
            ("Título", details['title']),
            ("Canal", details['uploader']),
            ("Fecha de subida", upload_date_str),
            ("Duración", duration_str),
            ("Categoría", categories_str),
            ("Descripción", details['description'])
        ]

    app_context.accessibility_manager.announce("Información detallada cargada. Use Tab para navegar entre los metadatos.")

    info_win = tk.Toplevel(root)
    info_win.title("Información Detallada del Video")
    info_win.geometry("650x550")
    info_win.configure(bg=color_scheme.bg_color)
    info_win.grab_set()

    def restore_focus(e=None):
        app_context.accessibility_manager.stop_announces()
        play_audio_file(app_context.project_path + "/assets/sounds/low/close_window_low.wav")
        listbox_results.focus_set()
        if listbox_results.size() > selected_index:
            listbox_results.selection_clear(0, tk.END)
            listbox_results.selection_set(selected_index)
            listbox_results.activate(selected_index)
        info_win.destroy()

    lbl_title = tk.Label(info_win, text="Detalles del Video (Use Tab para navegar, Escape para cerrar)", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
    lbl_title.pack(anchor=tk.W, padx=10, pady=10)

    canvas = tk.Canvas(info_win, bg=color_scheme.bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(info_win, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=color_scheme.bg_color)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def bloquear_edicion(event):
        return "break"

    for label_text, value_text in info_fields:
        field_frame = tk.Frame(scrollable_frame, bg=color_scheme.bg_color, pady=5)
        field_frame.pack(fill=tk.X, padx=5, expand=True)

        lbl = tk.Label(field_frame, text=f"{label_text}:", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 12, "bold"), anchor="w")
        lbl.pack(anchor=tk.W, padx=5, pady=2)

        def tab_metadata(event, lt, vt):
            valor_accesible = "Metadato {metadata_name} - Valor: {metadata_value}"
            play_audio_file(app_context.project_path + "/assets/sounds/low/tab_low.wav")
            app_context.accessibility_manager.announce(valor_accesible.format(metadata_name=lt, metadata_value=vt))

        if label_text == "Descripción":
            txt_val = tk.Text(field_frame, height=8, wrap=tk.WORD, font=("Arial", 12), bg="#111111", fg="#FFFFFF", insertbackground=color_scheme.fg_color, relief=tk.SOLID, bd=1, takefocus=True)
            txt_val.insert("1.0", str(value_text))
            txt_val.bind("<Key>", bloquear_edicion)
            txt_val.bind("<Tab>", lambda e: (txt_val.tk_focusNext().focus_set(), "break")[1])
            txt_val.bind("<Shift-Tab>", lambda e: (txt_val.tk_focusPrev().focus_set(), "break")[1])
            txt_val.pack(fill=tk.X, expand=True, padx=5, pady=2)
            max_chars_toread = app_context.config['ACCESSIBILITY'].getint('detailed_video.description.max_chars_read', 500)
            if max_chars_toread > 0:
                txt_val.bind("<FocusIn>", lambda e, lt=label_text, vt=value_text[0:max_chars_toread]: tab_metadata(e, lt, vt))
            txt_val.bind("<Escape>", restore_focus)
        else:
            entry_val = tk.Entry(field_frame, font=("Arial", 13), bg="#111111", fg="#000000", insertbackground=color_scheme.fg_color, relief=tk.SOLID, bd=1)
            entry_val.insert(0, str(value_text))
            entry_val.config(state="readonly")
            entry_val.pack(fill=tk.X, expand=True, padx=5, pady=2)
            entry_val.bind("<FocusIn>", lambda e, lt=label_text, vt=value_text: tab_metadata(e, lt, vt))
            entry_val.bind("<Escape>", restore_focus)

    btn_close = tk.Button(scrollable_frame, text="Cerrar (Escape)", command=restore_focus, bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
    btn_close.pack(pady=15, padx=5, anchor=tk.W)
    btn_close.bind("<FocusIn>", lambda e: tab_metadata(e, "Botón", "Cerrar ventana"))

    info_win.bind("<Escape>", restore_focus)
    info_win.protocol("WM_DELETE_WINDOW", restore_focus)

    if scrollable_frame.winfo_children():
        scrollable_frame.winfo_children()[0].winfo_children()[1].focus_set()
