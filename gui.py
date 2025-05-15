
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pystray
from PIL import Image, ImageDraw

from config import get_config, save_config
from watcher import start_watcher, archive_old
from transcribe import process_file
from db import init_db
from logging_config import logger

class TranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Whisper Transcriber')
        self.root.geometry('800x600')

        # 1) Load config & init DB
        self.config = get_config()
        init_db()

        # 2) Prepare state
        self.files = []
        self.failed_files = []
        self.tree_items = {}
        self.progress_var = tk.DoubleVar(value=0.0)
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_threads', 2)
        )
        self.observer = None

        # 3) Build the UI once
        self._build_ui()

        # 4) Non‐blocking model preload
        self.loading_label = ttk.Label(self.root, text="Loading Whisper model…")
        self.loading_label.pack(side='bottom', pady=5)
        threading.Thread(target=self._load_model_bg, daemon=True).start()

        # 5) Watcher & archive
        if self.config.get('watch_folder'):
            self.observer = start_watcher()
        archive_old()

        # 6) Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit)


    def _load_model_bg(self):
        logger.info("🛠️  _load_model_bg started")
        print(">> loading thread running")  # visible in your console
        from transcribe import get_model
        try:
            get_model()   # this will load to GPU off the UI thread
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Model load error", str(e)))
        finally:
            self.root.after(0, self.loading_label.destroy)

    def _build_ui(self):
        # Button frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text='Select Clips', command=self.open_file_dialog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Set Output Directory', command=self.set_output_dir).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Start Transcription', command=self.start_transcription).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Retry Failed Files', command=self.retry_failed).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Clear Logs', command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Toggle Watch', command=self.toggle_watch).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Minimize to Tray', command=self.hide_window).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Quit', command=self.quit).pack(side='left', padx=5)

        # Treeview for file statuses
        cols = ('status', 'progress')
        self.tree = ttk.Treeview(self.root, columns=cols, show='headings')
        self.tree.heading('status', text='Status')
        self.tree.heading('progress', text='Progress')
        self.tree.column('status', width=500)
        self.tree.column('progress', width=100, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress.pack(fill='x', padx=5, pady=5)

    def open_file_dialog(self):
        paths = filedialog.askopenfilenames(
            title='Select Clips',
            filetypes=[('Audio/Video','*.mp3 *.wav *.m4a *.flac *.mp4 *.mov')]
        )
        if not paths:
            return
        # Reset state
        self.files = list(paths)
        self.failed_files.clear()
        self.tree.delete(*self.tree.get_children())
        self.progress_var.set(0.0)

        # Populate tree
        for p in self.files:
            item = self.tree.insert('', 'end', values=('Waiting', '0%'))
            self.tree_items[p] = item

    def set_output_dir(self):
        directory = filedialog.askdirectory(title='Select Output Directory')
        if directory:
            self.config['output_dir'] = directory
            save_config(self.config)
            messagebox.showinfo('Output Directory', f'Set to: {directory}')

    def clear_logs(self):
        logs_dir = 'logs'
        if os.path.isdir(logs_dir):
            for f in os.listdir(logs_dir):
                try:
                    os.remove(os.path.join(logs_dir, f))
                except Exception:
                    pass
            messagebox.showinfo('Logs Cleared', 'All logs removed.')

    def retry_failed(self):
        if not self.failed_files:
            messagebox.showinfo('Retry Failed', 'No failed files to retry.')
            return
        for p in list(self.failed_files):
            item = self.tree_items.get(p)
            if item:
                self.tree.set(item, 'status', 'Retrying')
            # Submit retry
            self._submit_task(p)
        self.failed_files.clear()

    def toggle_watch(self):
        # Toggle watch setting
        self.config['watch_folder'] = not self.config.get('watch_folder', False)
        save_config(self.config)
        if self.config['watch_folder']:
            self.observer = start_watcher()
            messagebox.showinfo('Watcher', 'Folder watching enabled.')
        else:
            if self.observer:
                self.observer.stop()
                self.observer = None
            messagebox.showinfo('Watcher', 'Folder watching disabled.')

    def start_transcription(self):
        outdir = self.config.get('output_dir')
        if not self.files or not outdir:
            messagebox.showwarning('Missing Info', 'Select clips and output directory first.')
            return
        total = len(self.files)
        self.progress_var.set(0.0)
        # Submit all tasks
        for p in self.files:
            self.tree.set(self.tree_items[p], 'status', 'Queued')
            self._submit_task(p)

    def _submit_task(self, path):
        # Submit to thread pool
        future = self.executor.submit(process_file, path, self.config['output_dir'])
        future.add_done_callback(lambda f, p=path: self.root.after(0, self._on_task_done, f, p))

    def _on_task_done(self, future, path):
        item = self.tree_items.get(path)
        try:
            out_path = future.result()
            self.tree.set(item, 'status', 'Done')
        except Exception as e:
            logger.error(f'Task failed for {path}: {e}')
            self.tree.set(item, 'status', 'Failed')
            self.failed_files.append(path)
        # Update progress
        done = sum(1 for p in self.files if self.tree.set(self.tree_items[p], 'status') == 'Done')
        percent = (done / len(self.files)) * 100
        self.progress_var.set(percent)

    def hide_window(self):
        self.root.withdraw()

    def create_tray_image(self):
        # Create a simple icon with "W"
        img = Image.new('RGB', (64,64), color='white')
        d = ImageDraw.Draw(img)
        d.text((16,16), 'W', fill='black')
        return img

    def show_window(self, icon, item):
        self.root.deiconify()

    def quit(self, icon=None, item=None):
        # Stop watcher
        if self.observer:
            self.observer.stop()
        # Shutdown executor
        self.executor.shutdown(wait=False)
        # Stop tray icon
        try:
            icon.stop()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def run(self):
        # Setup tray icon
        menu = pystray.Menu(
            pystray.MenuItem('Open', self.show_window),
            pystray.MenuItem('Quit', self.quit)
        )
        self.tray_icon = pystray.Icon('WhisperTranscriber', self.create_tray_image(),
                                      'WhisperTranscriber', menu)
        self.tray_icon.run_detached()
        # Run Tk loop
        self.root.mainloop()
