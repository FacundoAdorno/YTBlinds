import os
import platform
import ctypes
import threading
import pyttsx3

_nvda_dll = None
engine = None   # PyTTSx3 Engine


def load_NVDA_dll():
    """Carga la libreria de NVDA correspondiente a la arquitectura de Python que estés ejecutando."""
    import struct
    global _nvda_dll
    try:
        py_arch =  struct.calcsize("P") * 8;
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if (py_arch == 32):
            dll_name = "nvdaControllerClient_x86.dll"
        else:
            dll_name = "nvdaControllerClient_x64.dll"
        dll_path = os.path.join(base_dir, "lib", "nvda_202533", dll_name)
        if os.path.exists(dll_path):
            _nvda_dll = ctypes.windll.LoadLibrary(dll_path)
            print("DLL " + dll_path + " cargada correctamente")

    except Exception as e:
        print("Error al cargar la DLL:", repr(e))

def load_PYTTS():
    """Carga el engine de PyTTSx3, el utilizado por defecto por la aplicación en caso de no contar con NVDA."""
    global engine
    # TODO: en el futuro se podría cambiar por PIPER-TTS (https://github.com/Bigbynth/piper-tts)
    engine = pyttsx3.init()
    # Cambiar la voz a español
    voices = engine.getProperty('voices')
    for voice in voices:
        # Busca una voz que contenga 'spanish' o 'es' en sus idiomas
        if "es-419" in voice.id.lower():
            engine.setProperty("voice", voice.id)
            print("Voz seleccionada:", voice.id)
            break

    # Ajustar velocidad (opcional)
    engine.setProperty('rate', 140)


### CARGANDO LIBRERIAS
if platform.system() == "Windows":
    load_NVDA_dll()
    if _nvda_dll is not None and _nvda_dll.nvdaController_testIfRunning() > 0:
        print("[ERROR] Debe iniciar NVDA para poder utilizar. Se utilizará el TextToSpeech por defecto de esta aplicación.")
        print("Si inicia NVDA, tiene que cerrar y abrir nuevamente esta aplicación")
        _nvda_dll = None    # La seteamos en None ya que NVDA no está actualmente activo.
        load_PYTTS()

else:   # otherwise is Linux
    load_PYTTS()

### FIN CARGANDO LIBRERIAS


class AccessibilityManager:
    @staticmethod
    def announce(text):
        print(f"[ACCESSIBILITY ANNOUNCE]: {text}")
        if platform.system() == "Windows" and _nvda_dll is not None:
            try:
                if _nvda_dll.nvdaController_testIfRunning() == 0 and _nvda_dll.nvdaController_speakText(ctypes.c_wchar_p(text)) == 0:
                    return
            except Exception as e:
                print("Error al hablar texto:", repr(e))

        try:
            def speak():
                if engine is None:
                    print("ERROR - Engine pyttsx3 no inicializado...")
                    return
                try:
                    print("Hablando por PyTTSx3...")
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print("Error al hablar texto:", repr(e))
            threading.Thread(target=speak, daemon=True).start()
        except ImportError:
            pass
