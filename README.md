# YTBlinds - Descargador Accesible de YouTube

Aplicación de escritorio desarrollada en Python 3 y Tkinter, diseñada específicamente desde cero para ser totalmente accesible para personas no videntes mediante navegación fluida por teclado (`Tab`, flechas) y lectores de pantalla (como NVDA en Windows u Orca en Linux). Utiliza `yt-dlp` como motor de descargas.

## Características Principales

- **Accesibilidad Total**: Diseñada para navegación sin ratón usando exclusivamente la tecla `Tab`, `Shift+Tab`, y flechas de dirección.
- **Alto Contraste**: Interfaz gráfica optimizada con colores de alto contraste (fondo negro y letras blancas/amarillas brillantes) para usuarios con baja visión.
- **Anuncios para Lectores de Pantalla**: Anuncios claros de eventos (búsquedas, selecciones, estado de descargas).
- **Atajos de Teclado Rápidos**:
  - `Alt + B`: Ir directo al campo de búsqueda / URL.
  - `Enter`: Ejecutar búsqueda o descargar el elemento seleccionado.
  - `Alt + V`: Descargar video de alta calidad.
  - `Alt + A`: Descargar audio en formato MP3.
  - `Alt + U`: Actualizar `yt-dlp` a la última versión desde la app.
  - `F1`: Ventana de ayuda con todos los atajos disponibles.
- **Multiplataforma**: Compatible con Windows y Linux.

## Estructura del Código

- `main.py`: Punto de entrada de la aplicación.
- `yt_blinds/ui.py`: Interfaz gráfica accesible.
- `yt_blinds/downloader.py`: Integración con `yt-dlp` para búsquedas y descargas en segundo plano (multihilo).
- `yt_blinds/updater.py`: Autogestión y actualización de dependencias (`yt-dlp`).
- `yt_blinds/accessibility.py`: Utilidades para anuncios de voz / accesibilidad.

## Ejecución

```bash
python3 main.py
```
