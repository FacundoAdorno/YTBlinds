import tkinter as tk
import subprocess
import sys
import os

class AccessibilityManager:
    """Gestiona anuncios de voz simples o hooks para lectores de pantalla."""
    @staticmethod
    def announce(text):
        print(f"[ACCESSIBILITY ANNOUNCE]: {text}")
        # Integración opcional con síntesis de voz multiplataforma (pyttsx3) si está disponible
        try:
            # Inicializar en un hilo separado para evitar bloqueos en la interfaz gráfica
            import threading
            import pyttsx3
            def speak():
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass
            threading.Thread(target=speak, daemon=True).start()
        except ImportError:
            pass
