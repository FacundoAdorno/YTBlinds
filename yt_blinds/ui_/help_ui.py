import tkinter as tk

from ..audio.audio_helpers import play_audio_file


class HelpWindow:

    @staticmethod
    def show_help(root, color_scheme, app_context,):
        play_audio_file(app_context.project_path + "/assets/sounds/low/open_window_low.wav")
        help_text_tuple = (
            "- Teclas Tab y Shift+Tab: Moverse entre elementos.\n",
            "- Tecla Escape: cerrar cualquier ventana desplegada.\n",
            "- Teclas Alt + B: Ir al cuadro de búsqueda.\n",
            "- Tecla Enter (al escribir en Búsqueda): Realizar búsqueda.\n",
            "- Flechas Arriba/Abajo: Navegar por los resultados de búsqueda.\n",
            "- Tecla I: Ver información detallada del video (campos navegables por Tab).\n",
            "- Tecla Enter en Resultado ó Teclas Alt + V: Comenzar a descargar resultado como Video.\n",
            "- Teclas Alt + A: Comenzar a descargar resultado como Audio MP3.\n",
            "- Teclas Alt + H: Ver historial de archivos descargados (Videos y Audios).\n",
            "- Teclas Control + Alt + V: Abrir carpeta de videos descargados.\n",
            "- Teclas Control + Alt + F: Abrir carpeta de audios descargados.\n",
            "- Teclas Alt + U: Actualizar yt-dlp a la última versión.\n",
            "- Tecla F1: Mostrar esta ayuda.\n",
            "- \n",
            "YTBlinds es una aplicación sencilla pensada para la gente no vidente o con baja visibilidad.\n",
            "Su objetivo es descargar videos desde Youtube en formato audio ó video.\n"
        )

        help_text = "".join(help_text_tuple)

        # Ventana modal personalizada para asegurar ajuste automático y accesibilidad
        help_win = tk.Toplevel(root)
        help_win.grab_set() # Hacer ventana Modal
        help_win.title("Ayuda de Atajos - YTBlinds")
        help_win.geometry("600x600")
        help_win.configure(bg=color_scheme.bg_color)

        lbl_title = tk.Label(help_win, text="Ayuda de Atajos (Presione Escape para cerrar)", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        lbl_title.pack(anchor=tk.W, padx=15, pady=10)

        txt_help = tk.Text(help_win, wrap=tk.WORD, bg="#111111", fg=color_scheme.fg_color, font=("Arial", 14), padx=10, pady=10, relief=tk.SOLID, bd=1)
        txt_help.insert(tk.END, help_text)
        txt_help.config(state=tk.DISABLED)
        txt_help.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        txt_help.focus_set()

        btn_close = tk.Button(help_win, text="Cerrar (Escape)", command=help_win.destroy, bg="#222222", fg=color_scheme.accent_color, font=("Arial", 11, "bold"))
        btn_close.pack(pady=3)

        def cerrar_ventana_ayuda(e):
            app_context.accessibility_manager.stop_announces()
            play_audio_file(app_context.project_path + "/assets/sounds/low/close_window_low.wav")
            help_win.destroy()

        help_win.bind("<Escape>", cerrar_ventana_ayuda)

        ## Leyendo los textos de ayuda.
        def announce_help():
            app_context.accessibility_manager.announce("Mostrando ventana de ayuda.")
            for teclas_atajos in help_text_tuple:
                app_context.accessibility_manager.announce(teclas_atajos)

        help_win.after(300, announce_help)
