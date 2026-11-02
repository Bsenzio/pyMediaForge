"""MediaForge — desktop audio/video converter."""
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from converter import Conversion, Cancelled, FORMATS


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MediaForge | Conversor de audio y video')
        self.geometry('780x540')
        self.minsize(640, 500)
        self.configure(bg='#111827')
        self.job = None
        self.events = queue.Queue()
        self.source = tk.StringVar()
        self.output = tk.StringVar()
        self.fmt = tk.StringVar(value='ogg')
        self.bitrate = tk.StringVar(value='192')
        self.status = tk.StringVar(value='Listo para convertir • Procesamiento local')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#111827')
        style.configure('TLabel', background='#111827', foreground='#e5e7eb', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 26, 'bold'), foreground='#fb923c')
        style.configure('TButton', font=('Segoe UI', 10), padding=9)
        frame = ttk.Frame(self, padding=26)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text='MediaForge', style='Title.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(frame, text='Tu audio y video, en el formato que necesitas.').grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 20))
        ttk.Label(frame, text='1. Archivo de entrada').grid(row=2, column=0, sticky='w')
        self.input_entry = ttk.Entry(frame, textvariable=self.source, state='readonly')
        self.input_entry.grid(row=3, column=0, sticky='ew', pady=7)
        self.browse = ttk.Button(frame, text='Elegir archivo…', command=self.choose)
        self.browse.grid(row=3, column=1, padx=(10, 0))
        ttk.Label(frame, text='2. Formato de salida').grid(row=4, column=0, sticky='w', pady=(12, 0))
        options = ttk.Frame(frame)
        options.grid(row=5, column=0, columnspan=2, sticky='w', pady=8)
        self.formats = ttk.Combobox(options, values=FORMATS, textvariable=self.fmt, state='readonly', width=12)
        self.formats.pack(side='left')
        self.formats.bind('<<ComboboxSelected>>', self.change_format)
        ttk.Label(options, text='   Bitrate de audio (kbps)   ').pack(side='left')
        self.rates = ttk.Combobox(options, values=('64', '96', '128', '160', '192', '256', '320'), textvariable=self.bitrate, state='readonly', width=7)
        self.rates.pack(side='left')
        ttk.Label(frame, text='MP4 → OGG extrae audio. Audio → video requiere una pista de video.', wraplength=650).grid(row=6, column=0, columnspan=2, sticky='w')
        ttk.Label(frame, text='3. Guardar resultado').grid(row=7, column=0, sticky='w', pady=(18, 0))
        ttk.Entry(frame, textvariable=self.output, state='readonly').grid(row=8, column=0, sticky='ew', pady=8)
        self.save = ttk.Button(frame, text='Guardar como…', command=self.choose_output)
        self.save.grid(row=8, column=1, padx=(10, 0))
        actions = ttk.Frame(frame)
        actions.grid(row=9, column=0, columnspan=2, sticky='w', pady=15)
        self.convert = ttk.Button(actions, text='▶ Convertir', command=self.start)
        self.convert.pack(side='left')
        self.cancel_button = ttk.Button(actions, text='Cancelar', command=self.cancel, state='disabled')
        self.cancel_button.pack(side='left', padx=10)
        ttk.Button(actions, text='Abrir carpeta', command=self.open_folder).pack(side='left')
        self.bar = ttk.Progressbar(frame, mode='indeterminate')
        self.bar.grid(row=10, column=0, columnspan=2, sticky='ew')
        ttk.Label(frame, textvariable=self.status, wraplength=650).grid(row=11, column=0, columnspan=2, sticky='w', pady=10)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.after(100, self.poll)

    def choose(self):
        p = filedialog.askopenfilename(filetypes=[('Multimedia', '*.mp3 *.mp4 *.wav *.ogg *.flac *.m4a *.aac *.opus *.mkv *.mov *.avi *.webm *.wma *.aiff *.mpeg *.m4v'), ('Todos los archivos', '*.*')])
        if p:
            self.source.set(p)
            self.default_output()

    def default_output(self):
        if self.source.get():
            p = Path(self.source.get())
            self.output.set(str(p.with_name(p.stem + '_convertido.' + self.fmt.get())))

    def change_format(self, event=None):
        self.default_output()
        self.rates.configure(state='disabled' if self.fmt.get() in ('wav', 'flac', 'mp4', 'mkv', 'webm') else 'readonly')

    def choose_output(self):
        fmt = self.fmt.get()
        p = filedialog.asksaveasfilename(defaultextension='.' + fmt,
            initialfile=Path(self.output.get()).name if self.output.get() else 'convertido.' + fmt,
            filetypes=[(fmt.upper(), '*.' + fmt)])
        if p:
            self.output.set(p)

    def busy(self, yes):
        for widget in (self.browse, self.save, self.convert):
            widget.configure(state='disabled' if yes else 'normal')
        self.formats.configure(state='disabled' if yes else 'readonly')
        self.rates.configure(state='disabled' if yes or self.fmt.get() in ('wav', 'flac', 'mp4', 'mkv', 'webm') else 'readonly')
        self.cancel_button.configure(state='normal' if yes else 'disabled')
        if yes:
            self.bar.start(12)
        else:
            self.bar.stop()

    def start(self):
        if not self.source.get() or not self.output.get():
            messagebox.showinfo('Falta un archivo', 'Selecciona la entrada y la ubicación de salida.')
            return
        if Path(self.source.get()).resolve() == Path(self.output.get()).resolve():
            messagebox.showerror('Salida no válida', 'Elige una salida diferente del original.')
            return
        if Path(self.output.get()).exists() and not messagebox.askyesno('Reemplazar', 'La salida ya existe. ¿Quieres reemplazarla?'):
            return
        args = (self.source.get(), self.output.get(), self.fmt.get(), self.bitrate.get())
        self.job = Conversion()
        job = self.job
        self.busy(True)
        self.status.set('Convirtiendo…')
        def worker():
            try:
                job.run(*args, progress=lambda t: self.events.put(('progress', t)))
                self.events.put(('done', 'Archivo convertido correctamente.'))
            except Cancelled:
                self.events.put(('cancel', 'Conversión cancelada.'))
            except Exception as e:
                self.events.put(('error', str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, text = self.events.get_nowait()
                if kind == 'progress':
                    self.status.set('Convirtiendo • Tiempo procesado: ' + text)
                else:
                    self.job = None
                    self.busy(False)
                    self.status.set(text.split('\n')[0])
                    if kind == 'error':
                        messagebox.showerror('Error de conversión', text)
                    elif kind == 'done':
                        messagebox.showinfo('Conversión terminada', text + '\n' + self.output.get())
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def cancel(self):
        if self.job:
            self.job.cancel()
            self.status.set('Cancelando…')

    def close(self):
        if self.job:
            self.cancel()
            messagebox.showinfo('Cancelando', 'Espera a que termine la cancelación y vuelve a cerrar.')
        else:
            self.destroy()

    def open_folder(self):
        p = Path(self.output.get()).parent if self.output.get() else Path.home()
        if os.name == 'nt':
            os.startfile(str(p))


if __name__ == '__main__':
    App().mainloop()
