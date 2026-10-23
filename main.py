import sys
from pathlib import Path

from yt_blinds import Updater

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: Tkinter no está instalado en el sistema operativo.")
    sys.exit(1)

from yt_blinds.context.app_context import AppContext
from yt_blinds.ui_.main_ui import MainWindow
from yt_blinds.utils.audio_helpers import play_audio_file


def main():
    app_context = AppContext()

    ## Verificando que existan dependencias necesarias, no administradas por 'pip'.
    yt_dlp_path = Path(app_context.project_path + "/vendor/yt_dlp")
    if ( not yt_dlp_path.exists() ):
        mensaje = "Se está instalando yt-dlp ya que no se encuentra en los paquetes del programa.\nPresione Enter para continuar y espere..."
        play_audio_file(app_context.project_path + "/assets/sounds/low/open_window_low.wav")
        app_context.accessibility_manager.announce(mensaje)
        messagebox.showwarning("Instalando dependencia", mensaje)
        success, msg = Updater.update_yt_dlp()
        if (not success):
            play_audio_file(app_context.project_path + "/assets/sounds/low/error_low.wav")
            messagebox.showerror("Error al instalar yt_dlp: " + msg)
            sys.exit(1)
        else:
            play_audio_file(app_context.project_path + "/assets/sounds/ok.wav")

    root = tk.Tk()
    app = MainWindow(root, app_context)
    root.mainloop()

if __name__ == "__main__":
    main()
