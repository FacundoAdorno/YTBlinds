import tkinter as tk
import subprocess
import sys
import os

class AccessibilityManager:
    """Gestiona anuncios de voz simples o hooks para lectores de pantalla."""
    @staticmethod
    def announce(text):
        print(f"[ACCESSIBILITY ANNOUNCE]: {text}")
        # En el futuro se puede integrar pyttsx3 o similar si se desea.
