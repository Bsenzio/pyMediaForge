# MediaForge

Conversor de audio y video para Windows en Python, con interfaz Tkinter en español y motor FFmpeg. Procesa los archivos localmente.

## Funciones

- Elegir entrada y destino desde el explorador de Windows.
- Audio de salida: **MP3, OGG (Vorbis), WAV (PCM 16 bits), FLAC, M4A (AAC), Opus**.
- Video de salida: **MP4 (H.264/AAC), MKV (H.264/AAC), WebM (VP9/Opus)**.
- Extraer audio: por ejemplo **MP4 → OGG** para Unity.
- Seleccionar bitrate para audio con pérdida, cancelar y abrir carpeta.
- Mostrar tiempo procesado y actividad. No muestra porcentaje estimado.
- Confirmar reemplazos; conservar el original y proteger una salida existente ante fallos o cancelaciones.

Entradas habituales: MP3, MP4, WAV, OGG, FLAC, M4A, AAC, Opus, MOV, MKV, AVI, WebM, WMA y AIFF. Se puede elegir cualquier archivo, pero la compatibilidad depende de su contenido y de los decodificadores del FFmpeg incluido. No convierte documentos ni archivos con DRM.

Audio → video requiere una pista real de video; no genera imágenes para acompañar audio. Usa la primera pista de audio y, en video, la primera pista de video real más la primera de audio si existe. No preserva subtítulos ni pistas adicionales. Recodifica el video; ajusta dimensiones impares al entero par inferior. El bitrate se aplica a MP3/OGG/M4A/Opus; WAV/FLAC no lo usan. Los perfiles de video usan la calidad predeterminada de sus códecs.

## Ejecutar en Windows

Instala **Python 3.11 o 3.12 de 64 bits**, con Tcl/Tk y el lanzador `py` (opciones habituales de python.org). Extrae el proyecto y abre PowerShell en su carpeta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Run.ps1
```

La primera vez requiere Internet para instalar dependencias. Después puedes iniciarlo sin reinstalar:

```powershell
.\.venv\Scripts\python.exe app.py
```

FFmpeg viene en `imageio-ffmpeg`. No hace falta instalarlo por separado. Puedes usar otra compilación con la variable `IMAGEIO_FFMPEG_EXE` apuntando a su ejecutable.

## Compilar el EXE

Desde la carpeta del proyecto, **en Windows**:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Build_Executable.ps1
```

Resultado: **`dist\MediaForge.exe`**. Incluye FFmpeg y puede copiarse a otro Windows de 64 bits sin instalar Python. El script crea `.venv`, instala dependencias, ejecuta las pruebas y compila con PyInstaller. La compilación inicial necesita Internet. No cambia permanentemente la política de PowerShell.

Si `py` no se reconoce, instala el lanzador o crea `.venv` con `python -m venv .venv` y vuelve a ejecutar. No reutilices un entorno virtual de otro sistema operativo.

## Subir a GitHub

Sube **el contenido de esta carpeta** a la raíz de un repositorio, incluyendo `.github`. No subas `.venv`, `build` ni `dist`.

```powershell
git init
git add .
git commit -m "Initial MediaForge converter"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/mediaforge.git
git push -u origin main
```

El workflow **Windows executable** prueba y compila en GitHub Actions. En **Actions**, abre una ejecución correcta y descarga **MediaForge-Windows-x64** en Artifacts. También puedes ejecutarlo con **Run workflow**. No crea un Release automáticamente.

## Pruebas y validación

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Generan muestras de audio y video, convierten a nueve formatos y comprueban su decodificación. Verifican protección del original, entradas inválidas, cancelación y preservación de salidas ante errores.

La interfaz y el EXE deben comprobarse manualmente en Windows: elegir audio/video, convertir, cancelar una conversión larga, usar rutas con espacios/acentos y abrir carpeta. El paquete entregado contiene código fuente, no un EXE Windows ya validado.

## Archivos

- `app.py`: interfaz; hilo de conversión y cola de eventos para Tkinter.
- `converter.py`: motor y perfiles; salida temporal y reemplazo atómico al terminar.
- `Run.ps1`: instalación y ejecución.
- `Build_Executable.ps1`: pruebas y compilación.
- `.github/workflows/windows-build.yml`: compilación Windows en GitHub.
- `tests/`: pruebas de integración.

## Licencias

Código del proyecto bajo MIT. FFmpeg y las dependencias conservan sus licencias; revisa `THIRD_PARTY_NOTICES.md` antes de distribuir binarios.

Referencias: [FFmpeg](https://ffmpeg.org/documentation.html), [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg), [PyInstaller](https://pyinstaller.org/en/stable/usage.html).
