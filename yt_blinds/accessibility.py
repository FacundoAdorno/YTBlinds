import os
import platform
import ctypes
import threading
import pyttsx3

_nvda_dll = None
engine = None   # PyTTSx3 Engine
if platform.system() == "Windows":
    import struct
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

else:   # otherwise is Linux
    engine = pyttsx3.init()
    # Cambiar la voz a español
    voices = engine.getProperty('voices')
    for voice in voices:
        # Busca una voz que contenga 'spanish' o 'es' en sus idiomas
        if 'es' in voice.languages or 'spanish' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    # Ajustar velocidad (opcional)
    engine.setProperty('rate', 140)

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
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print("Error al hablar texto:", repr(e))
            threading.Thread(target=speak, daemon=True).start()
        except ImportError:
            pass
