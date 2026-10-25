import os
import platform
import subprocess
import tkinter as tk
import webbrowser
from importlib.metadata import PackageNotFoundError, version

from PIL import Image, ImageTk

from ..utils.audio_helpers import play_audio_file


class AboutWindow:
    """Ventana modal 'Acerca de' con información del sistema, versiones y enlace al repositorio."""
    @staticmethod
    def show_about(root, color_scheme, app_context):
        play_audio_file(app_context.project_path + "/assets/sounds/low/open_window_low.wav")
        app_context.accessibility_manager.stop_announces()

        version_str = "UNK"
        try:
            version_file = os.path.join(app_context.project_path, "VERSION")
            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as f:
                    version_str = f.read().strip()
        except Exception:
            pass

        ytdlp_ver = "Desconocida"
        try:
            from yt_dlp.version import __version__
            ytdlp_ver = __version__
        except Exception:
            pass

        ffmpeg_ver = "No detectado"
        try:
            res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                first_line = res.stdout.splitlines()[0] if res.stdout else ""
                ffmpeg_ver = first_line.split("version")[1].strip().split()[0] if "version" in first_line else "Detectado"
        except Exception:
            pass

        tts_info = "UNK"
        try:
            acc_mgr = app_context.accessibility_manager
            if platform.system() == "Windows" and getattr(acc_mgr, "_nvda_dll", None) is not None:
                tts_info = "NVDA 2025.3.3 (DLL)"
            else:
                tts_info = f"Pyttsx3 (v{version('pyttsx3')})"
        except (AttributeError, PackageNotFoundError) as e:
            print("[WARN] No se pudo determinar el motor TTS: %s", e)

        python_info = f"Python {platform.python_version()} ({platform.architecture()[0]})"
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

        info_text_tuple = (
            f"YTBlinds v{version_str}\n",
            "Descargador accesible de YouTube para personas ciegas o con baja visión.\n\n",
            "• Repositorio: https://github.com/FacundoAdorno/YTBlinds\n",
            f"• Python: {python_info}\n",
            f"• SO: {os_info}\n",
            f"• yt-dlp: {ytdlp_ver}\n",
            f"• FFmpeg: {ffmpeg_ver}\n",
            f"• Text-To-Speech Engine: {tts_info}"
        )

        about_win = tk.Toplevel(root)
        about_win.grab_set()
        about_win.title("Acerca de - YTBlinds")
        about_win.geometry("450x400")
        about_win.resizable(False, False)
        about_win.configure(bg=color_scheme.bg_color)

        lbl_title = tk.Label(about_win, text=f"YTBlinds v{version_str}", bg=color_scheme.bg_color, fg=color_scheme.accent_color, font=("Arial", 16, "bold"))
        lbl_title.pack(pady=8)

        # Cargar y redimensionar el logo
        try:
            logo_path = os.path.join(app_context.project_path, "assets", "images", "ytblinds.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)

                lbl_logo = tk.Label(about_win, image=logo_img, bg=color_scheme.bg_color)
                lbl_logo.image = logo_img  # IMPORTANTE: mantener referencia para evitar recolección de basura
                lbl_logo.pack(pady=5)
        except Exception as e:
            print("No se pudo cargar el logo:", repr(e))

        txt_info = tk.Text(about_win, wrap=tk.WORD, bg="#111111", fg=color_scheme.fg_color, font=("Arial", 13), padx=8, pady=8, relief=tk.SOLID, bd=1)
        txt_info.insert(tk.END, "".join(info_text_tuple))
        txt_info.config(state=tk.DISABLED)
        txt_info.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        def open_link(e):
            webbrowser.open("https://github.com/FacundoAdorno/YTBlinds")

        lbl_link = tk.Label(about_win, text="GitHub: github.com/FacundoAdorno/YTBlinds", bg=color_scheme.bg_color, fg="#00BFFF", font=("Arial", 9, "underline"), cursor="hand2")
        lbl_link.pack(pady=3)
        lbl_link.bind("<Button-1>", open_link)

        def copy_info():
            root.clipboard_clear()
            root.clipboard_append("".join(info_text_tuple))
            app_context.accessibility_manager.announce("Información copiada al portapapeles.")

        btn_copy = tk.Button(about_win, text="Copiar Información (F2)", command=copy_info, bg="#222222", fg=color_scheme.accent_color, font=("Arial", 10, "bold"))
        btn_copy.pack(pady=3)

        btn_close = tk.Button(about_win, text="Cerrar (Escape)", command=lambda: close_about(None), bg="#222222", fg=color_scheme.accent_color, font=("Arial", 10, "bold"))
        btn_close.pack(pady=5)

        def close_about(e=None):
            app_context.accessibility_manager.stop_announces()
            play_audio_file(app_context.project_path + "/assets/sounds/low/close_window_low.wav")
            about_win.destroy()

        about_win.bind("<Escape>", close_about)
        about_win.bind("<Control-c>", lambda e: (copy_info(), "break")[1])
        about_win.bind("<Control-C>", lambda e: (copy_info(), "break")[1])
        txt_info.focus_set()

        ## Leyendo los textos de información del sistema.
        def announce_info():
            app_context.accessibility_manager.stop_announces()
            app_context.accessibility_manager.announce("Ventana 'Acerca de'. Presione Control+C para copiar la información del sistema en su portapapeles.")
            for info_sis in info_text_tuple:
                app_context.accessibility_manager.announce(info_sis)

        about_win.after(300, announce_info)
