"""Conversion engine; no UI dependency."""
import os
from pathlib import Path
import subprocess
import tempfile
import threading

AUDIO = {'mp3': ['-c:a', 'libmp3lame'], 'ogg': ['-c:a', 'libvorbis'],
         'wav': ['-c:a', 'pcm_s16le'], 'flac': ['-c:a', 'flac'],
         'm4a': ['-c:a', 'aac'], 'opus': ['-c:a', 'libopus']}
VIDEO = {'mp4': ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart'],
         'mkv': ['-c:v', 'libx264', '-c:a', 'aac'],
         'webm': ['-c:v', 'libvpx-vp9', '-c:a', 'libopus']}
FORMATS = tuple(AUDIO) + tuple(VIDEO)
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def command(exe, source, destination, fmt, bitrate='192'):
    if fmt not in FORMATS:
        raise ValueError('Formato de salida no admitido.')
    args = [exe, '-hide_banner', '-nostdin', '-y', '-i', str(source)]
    if fmt in AUDIO:
        args += ['-map', '0:a:0', '-vn'] + AUDIO[fmt]
        if fmt not in ('wav', 'flac'):
            args += ['-b:a', bitrate + 'k']
    else:
        args += ['-map', '0:V:0', '-map', '0:a:0?', '-vf',
                 'scale=trunc(iw/2)*2:trunc(ih/2)*2'] + VIDEO[fmt]
    return args + ['-progress', 'pipe:1', '-nostats', str(destination)]


class Cancelled(Exception):
    pass


class Conversion:
    def __init__(self):
        self.cancelled = threading.Event()

    def cancel(self):
        self.cancelled.set()

    def run(self, source, destination, fmt, bitrate='192', progress=lambda s: None, exe=None):
        source, destination = Path(source).resolve(), Path(destination).resolve()
        if not source.is_file():
            raise ValueError('Selecciona un archivo de entrada válido.')
        if source == destination:
            raise ValueError('La salida debe ser diferente del archivo original.')
        if destination.suffix.lower() != '.' + fmt:
            raise ValueError('La extensión de salida no coincide con el formato.')
        if not destination.parent.is_dir():
            raise ValueError('La carpeta de salida no existe.')
        if bitrate not in ('64', '96', '128', '160', '192', '256', '320'):
            raise ValueError('Bitrate no válido.')
        if fmt == 'opus' and int(bitrate) > 256:
            raise ValueError('Para Opus selecciona hasta 256 kbps.')
        fd, temp = tempfile.mkstemp(prefix='.mediaforge-', suffix='.' + fmt, dir=destination.parent)
        os.close(fd)
        try:
            with tempfile.TemporaryFile(mode='w+b') as errors:
                proc = subprocess.Popen(command(exe or ffmpeg(), source, temp, fmt, bitrate),
                                        stdout=subprocess.PIPE, stderr=errors,
                                        text=True, encoding='utf-8', errors='replace', creationflags=FLAGS)
                def monitor():
                    while proc.poll() is None:
                        if self.cancelled.wait(.1):
                            if proc.poll() is None:
                                try:
                                    proc.terminate()
                                except OSError:
                                    pass
                            return
                watcher = threading.Thread(target=monitor, daemon=True)
                watcher.start()
                try:
                    for line in proc.stdout:
                        if line.startswith('out_time='):
                            progress(line.strip().split('=', 1)[1])
                    code = proc.wait()
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
                    proc.stdout.close()
                    watcher.join()
                if self.cancelled.is_set():
                    raise Cancelled('Conversión cancelada.')
                if code:
                    errors.seek(0, 2)
                    size = errors.tell()
                    errors.seek(max(0, size - 6000))
                    detail = errors.read().decode('utf-8', errors='replace')
                    raise RuntimeError('No se pudo convertir. Verifica que la entrada tenga audio o video '
                                       'según la salida elegida.\n\n' + detail)
                if not Path(temp).stat().st_size:
                    raise RuntimeError('FFmpeg produjo un archivo vacío.')
                os.replace(temp, destination)
        finally:
            Path(temp).unlink(missing_ok=True)
