import os
import subprocess
import sys

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: Tkinter no está instalado en el sistema operativo.")
    sys.exit(1)

from yt_blinds.ui import MainWindow
from yt_blinds.context.app_context import AppContext


def main():
    root = tk.Tk()
    app_context = AppContext()
    app = MainWindow(root, app_context)
    root.mainloop()

if __name__ == "__main__":
    main()
