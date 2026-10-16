import sys
import subprocess
import os

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: Tkinter no está instalado en el sistema operativo.")
    sys.exit(1)

from yt_blinds.ui import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
