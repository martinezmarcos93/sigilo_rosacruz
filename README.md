✡️ Generador de Sigilos sobre Rosacruz — Auto-Snap 2D
Este script genera sigilos trazados automáticamente sobre una imagen de la Rosacruz (`rosacruz.png`), usando detección automática de bordes y ajuste preciso 2D.
Convierte palabras latinas a hebreo, calcula su valor guemátrico y dibuja las letras conectadas en la posición correspondiente en los anillos de la cruz.
✨ Características
- Transliteración automática de caracteres latinos a hebreo.
- Cálculo de guematría con valores tradicionales.
- Clasificación de letras (Madres, Dobles, Simples) para colocación en anillos.
- Ajuste automático a los bordes mediante búsqueda angular y radial (snap 2D).
- Dibujo de puntos, letras y líneas conectando cada nodo.
- Guardado automático con contador (`sigilo_01.png`, `sigilo_02.png`...).
- Modo de depuración opcional que dibuja centros y anillos de referencia.
⚙️ Requisitos
- Python 3.8+
- Librerías:
  - Pillow (para imágenes)

Instalación:
pip install pillow
🚀 Ejecución
Coloca una imagen llamada `rosacruz.png` en la misma carpeta que el script y ejecuta:

python rosacruz_sigilo_auto_snap2d.py

Luego escribe la palabra a sigilizar cuando el programa lo pida.
📂 Salida
Se generará un archivo de salida en la misma carpeta, por ejemplo:
`sigilo_01.png`, `sigilo_02.png`... según la cantidad de sigilos creados.
🛠 Ajustes avanzados
- `RADIUS_REL`: controla el radio de cada anillo.
- `ANGLES_DEG`: ajusta la posición angular de cada letra.
- `GLOBAL_ROT_DEG`: permite rotar toda la figura.
- `SEARCH`: define el rango de búsqueda angular y radial para el auto-ajuste.
- Activar `debug=True` en `crear_sigilo()` dibuja guías de verificación.
⚠️ Aviso
Este script está pensado para estudio de simbología esotérica y generación artística de sigilos.
El uso práctico en contextos rituales queda a discreción del usuario.
📖 Licencia
MIT — Libre para modificar y compartir.
