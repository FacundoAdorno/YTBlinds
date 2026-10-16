# Contexto del Proyecto
  - **Lenguaje/Stack:** Python 3.14, CustomTkinter, etc.
  - **Dependencia externa**: yt-dlp.
    - Esta debe poder actualizarse desde la misma aplicación.
- **Objetivo:** Aplicación para buscar y descargar contenido desde youtube.
  - Debe ser pensada para que sea navegable para gente no vidente, de forma fluida mediante tecla TAB.
  - Que tenga ciertos atajos para moverse también rápidamente.
  - Diseñado principalmente para que pueda leerse por lectores de pantalla como NVDA.

# Reglas de Código (Estilo)
- Sé extremadamente conciso. No des explicaciones teóricas a menos que se pidan explícitamente.
- No agregues comentarios redundantes en el código.
- Prefiere soluciones simples y directas.
- Dividela en módulos manejables (si lo requieres), no hagas una aplicación contenida en un único archivo. Quiero evitar archivos super largos.
- Que sea orientada a objetos, para que sea mas legible.

# Restricciones
- No uses dependencias externas pesadas.
- La aplicación debería funcionar en Windows, aunque las pruebas las realizaré en Linux.
- Si necesitas elegir colores, elige de alto contraste, para personas con visión disminuida.
- Utilizar virtualenv.
- Las búsquedas sólo las realizará dentro de Youtube. Retorna como máximo 40 resultados.
