import platform
import subprocess


def play_audio_file(file_path):
    print(f"Reproduciento audio {file_path}...")
    current_os = platform.system()

    if current_os == "Windows":
        import winsound
        # SND_FILENAME indica que es un archivo, SND_ASYNC evita que se congele la interfaz (Tkinter)
        winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    elif current_os == "Linux":
        # Intentamos con aplay (ALSA), paplay (PulseAudio/Pipewire) o ffplay (si usas FFmpeg)
        played = False
        for player in [["aplay", file_path], ["paplay", file_path], ["ffplay", "-nodisp", "-autoexit", file_path]]:
            try:
                subprocess.Popen(player, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                played = True
                break
            except FileNotFoundError:
                continue
        if not played:
            print("Aviso: No se encontró un reproductor de audio compatible en Linux (aplay, paplay o ffplay).")
