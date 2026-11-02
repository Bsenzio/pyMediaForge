# Componentes de terceros

- Python: https://docs.python.org/3/license.html
- Tcl/Tk: https://www.tcl.tk/software/tcltk/license.html
- imageio-ffmpeg (BSD-2-Clause): https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE
- PyInstaller: https://pyinstaller.org/en/stable/license.html
- FFmpeg: https://ffmpeg.org/legal.html

La licencia MIT de este proyecto no sustituye las licencias de estos componentes. El wheel de imageio-ffmpeg proporciona FFmpeg; su configuración puede incluir componentes GPL como libx264. Antes de redistribuir un EXE, inspecciona el binario exacto con `ffmpeg -version` y `ffmpeg -buildconf`, conserva avisos y cumple los requisitos de disponibilidad de código fuente correspondiente de esa compilación. Este repositorio no incluye un binario FFmpeg propio. PyInstaller recopila el paquete con `--collect-all imageio_ffmpeg`.
