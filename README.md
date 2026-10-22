# YTBlinds - Descargador Accesible de YouTube

YTBlinds es una aplicación de escritorio desarrollada en Python y Tkinter, creada de forma específica para asistir a personas ciegas que necesiten una herramienta completamente accesible, fluida y operable mediante lectores de pantalla. Esta aplicación está pensada para funcionar tanto en sistemas de 32 y 64 bits.

La intención de esta herramienta no es sustituir ninguna existente, solamente brindar una alternativa para aquellas personas ciegas que  tienen equipos de 32 bits antiguos. De ningún modo es algo con fines profesionales, sino con fin de resolver de forma práctica un problema en específico. No fue pensado para verse bonito, sino en ser funcional para personas no videntes. Pueden haber errores.

[Ver video de demostración](./demo/ytblinds_demo_linux.mp4)

[Ver video de demostración en Youtube](https://youtu.be/KcSG1LQQrww)

## Requisitos e Instalación

### LINUX

#### 1. Dependencias del Sistema
Para que la interfaz gráfica (Tkinter), la síntesis de voz (`pyttsx3`) y el motor de descargas (`yt-dlp`) funcionen correctamente en Linux (Debian / Ubuntu / Mint), instale los paquetes del sistema necesarios:
```bash
sudo apt-get update
sudo apt-get install python3-tk espeak ffmpeg
```

### WINDOWS

#### 1. Dependencias del Sistema
Descarga e instala **Python** desde el [sitio oficial de Python](https://www.python.org/downloads/). (Asegúrate de marcar la opción de añadir Python al PATH durante la instalación en Windows).

Esta aplicación utiliza **FFmpeg** para el procesamiento y reproducción de contenidos multimedia.
 - Descarga los binarios oficiales desde el [sitio web de FFmpeg](https://www.ffmpeg.org/download.html#build-windows).
 - Configuración del *PATH* en Windows: Debes descomprimir los binarios y agregar la ruta de la carpeta bin de FFmpeg a las Variables de Entorno (PATH) de tu sistema operativo para que la aplicación pueda ejecutarlos globalmente.

### 2. Dependencias de Python
Ir al directorio donde está descargado el código fuente. Luego instala las dependencias de Python dentro de un entorno virtual (`virtualenv`):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Características Principales

- **Accesibilidad Total**: Navegación fluida por teclado mediante `Tab`, `Shift+Tab` y flechas de dirección.
- **Lectores de Pantalla**: Integración optimizada para lectores de pantalla como NVDA en Windows (vía DLL del controlador) y síntesis de voz multiplataforma (`pyttsx3`) en Linux.
- **Alto Contraste**: Interfaz gráfica en modo de alto contraste (fondo oscuro y acentos brillantes) para usuarios con baja visión.
- **Atajos de Teclado Rápidos**:
  - `Alt + B`: Enfocar cuadro de búsqueda.
  - `Enter`: Buscar o descargar el elemento seleccionado.
  - `Alt + V`: Descargar video.
  - `Alt + A`: Descargar audio (MP3).
  - `Alt + H`: Abrir historial de archivos descargados.
  - `Ctrl + Alt + V` / `Ctrl + Alt + A`: Abrir carpetas de destino de videos y audios.
  - `Alt + U`: Actualizar `yt-dlp`.
  - `F1`: Ventana de ayuda de atajos.

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `yt_blinds/context/`: Contexto de la aplicación y gestión de dependencias.
- `yt_blinds/ui/`: Paquete de interfaces gráficas accesibles (Ventana Principal e Historial).
- `yt_blinds/downloader.py`: Integración con `yt-dlp` para búsquedas y descargas en segundo plano.
- `yt_blinds/history.py`: Gestor SQLite para el historial de descargas persistente.
- `yt_blinds/accessibility.py`: Módulo de síntesis de voz y compatibilidad con NVDA.
- `yt_blinds/updater.py`: Autogestión y actualización de dependencias.

## Ejecución

```bash
python3 main.py
```

## Sobre su desarrollo

Este proyecto fue desarrollado de manera rápida y colaborativa con la asistencia del modelo **Gemini 3.5 Flash-Lite**, con el diseño, control y modificaciones de código a cargo de **Facundo Gabriel Adorno**.
Se utilizó el [editor de código minimalista **Zed**](https://zed.dev/), diseñado en torno al desarrollo agéntico con Inteligencia Artificial.
