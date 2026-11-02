from pathlib import Path
import subprocess
import tempfile
import unittest
from converter import Conversion, Cancelled, FORMATS, ffmpeg, FLAGS


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = ffmpeg()
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.wav = cls.root / 'audio prueba á.wav'
        cls.video = cls.root / 'video.mp4'
        def generate(args):
            subprocess.run([cls.exe, '-hide_banner', '-loglevel', 'error', '-y'] + args,
                           check=True, creationflags=FLAGS)
        generate(['-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.4', str(cls.wav)])
        generate(['-f', 'lavfi', '-i', 'color=c=blue:s=160x120:d=0.4',
                  '-i', str(cls.wav), '-c:v', 'libx264', '-c:a', 'aac', '-shortest', str(cls.video)])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_formats_decode(self):
        for fmt in FORMATS:
            with self.subTest(fmt=fmt):
                output = self.root / ('resultado.' + fmt)
                Conversion().run(self.video, output, fmt, exe=self.exe)
                subprocess.run([self.exe, '-v', 'error', '-i', str(output), '-f', 'null', '-'],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=FLAGS)
                self.assertGreater(output.stat().st_size, 0)

    def test_original_protected(self):
        original = self.wav.read_bytes()
        with self.assertRaises(ValueError):
            Conversion().run(self.wav, self.wav, 'wav', exe=self.exe)
        self.assertEqual(original, self.wav.read_bytes())

    def test_audio_to_video_fails_and_preserves_destination(self):
        dest = self.root / 'protected.mp4'
        dest.write_bytes(b'original destination')
        with self.assertRaises(RuntimeError):
            Conversion().run(self.wav, dest, 'mp4', exe=self.exe)
        self.assertEqual(dest.read_bytes(), b'original destination')
        self.assertFalse(list(self.root.glob('.mediaforge-*')))

    def test_cancel_preserves_destination(self):
        dest = self.root / 'cancel.ogg'
        dest.write_bytes(b'keep')
        job = Conversion()
        job.cancel()
        with self.assertRaises(Cancelled):
            job.run(self.wav, dest, 'ogg', exe=self.exe)
        self.assertEqual(dest.read_bytes(), b'keep')
        self.assertFalse(list(self.root.glob('.mediaforge-*')))

    def test_missing_source(self):
        with self.assertRaises(ValueError):
            Conversion().run(self.root / 'missing.wav', self.root / 'missing.ogg', 'ogg', exe=self.exe)


if __name__ == '__main__':
    unittest.main()
