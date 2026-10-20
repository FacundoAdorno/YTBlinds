import ctypes
import os
import platform
import queue
import threading

import pyttsx3


class AccessibilityManager:
    def __init__(self):
        self._nvda_dll = None
        self.engine = None
        self.speech_queue = queue.Queue()

        self._load_libraries()

        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _load_nvda_dll(self):
        """Carga la libreria de NVDA correspondiente a la arquitectura de Python que estés ejecutando."""
        import struct
        try:
            py_arch = struct.calcsize("P") * 8
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dll_name = "nvdaControllerClient_x86.dll" if py_arch == 32 else "nvdaControllerClient_x64.dll"
            dll_path = os.path.join(base_dir, "lib", "nvda_202533", dll_name)
            if os.path.exists(dll_path):
                self._nvda_dll = ctypes.windll.LoadLibrary(dll_path)
                print("DLL " + dll_path + " cargada correctamente")
        except Exception as e:
            print("Error al cargar la DLL:", repr(e))

    def _load_pytts(self):
        """Carga el engine de PyTTSx3."""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "es-419" in voice.id.lower() or "spanish" in voice.id.lower() or "es" in voice.id.lower():
                    self.engine.setProperty("voice", voice.id)
                    print("Voz seleccionada:", voice.id)
                    break
            self.engine.setProperty('rate', 140)
            self.engine.setProperty('volume', 1)    ## Volumen al 100%.
        except Exception as e:
            print("Error al inicializar pyttsx3:", repr(e))

    def _load_libraries(self):
        if platform.system() == "Windows":
            self._load_nvda_dll()
            if self._nvda_dll is not None:
                try:
                    if self._nvda_dll.nvdaController_testIfRunning() > 0:
                        print("[ERROR] Debe iniciar NVDA para poder utilizar. Se utilizará el TextToSpeech por defecto de esta aplicación.")
                        print("Si inicia NVDA, tiene que cerrar y abrir nuevamente esta aplicación")
                        self._nvda_dll = None
                        self._load_pytts()
                except Exception:
                    self._load_pytts()
            else:
                self._load_pytts()
        else:
            self._load_pytts()

    def announce(self, text):
        print(f"[ACCESSIBILITY ANNOUNCE]: {text}")
        if platform.system() == "Windows" and self._nvda_dll is not None:
            try:
                if self._nvda_dll.nvdaController_testIfRunning() == 0 and self._nvda_dll.nvdaController_speakText(ctypes.c_wchar_p(text)) == 0:
                    return
            except Exception as e:
                print("Error al hablar texto con NVDA:", repr(e))

        self.speech_queue.put(text)

    def stop_announces(self):
        """Elimina los anuncios siguientes a procesar en la cola."""
        # if platform.system() == "Windows" and self._nvda_dll is not None:
        #     try:
        #         self._nvda_dll.nvdaController_cancelSpeech()
        #     except Exception:
        #         pass

        if platform.system() == "Linux":
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break

    def _process_queue(self):
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            if self.engine is not None:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print("Error al hablar texto:", repr(e))
            self.speech_queue.task_done()

accessibility_manager = AccessibilityManager()
