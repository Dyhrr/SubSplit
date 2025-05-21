import os
import re
import threading
import zipfile
import shutil
from datetime import datetime, timedelta

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import get_config
from transcribe import process_file

# Retention period for archives (days)
ARCHIVE_DAYS = 7

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, exts=None):
        # File extensions to watch for
        self.exts = exts or ['.mp3', '.wav', '.m4a', '.flac', '.mp4', '.mov']

    def on_created(self, event):
        # Ignore directory events
        if event.is_directory:
            return
        _, ext = os.path.splitext(event.src_path)
        if ext.lower() in self.exts:
            cfg = get_config()
            outdir = cfg.get('output_dir')
            if not outdir:
                return
            # Launch transcription in a background thread
            threading.Thread(
                target=process_file,
                args=(event.src_path, outdir),
                daemon=True
            ).start()

def start_watcher():
    """
    Initialize and start the folder watcher based on config settings.
    """
    cfg = get_config()
    watch_path = cfg.get('watch_path')
    if not cfg.get('watch_folder') or not watch_path:
        return None
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_path, recursive=False)
    observer.start()
    return observer

def archive_old():
    """
    Zip and remove date-stamped transcript folders older than ARCHIVE_DAYS.
    Also prunes old .zip files in the archive directory.
    """
    cfg = get_config()
    outdir = cfg.get('output_dir')
    if not outdir:
        return
    archive_dir = os.path.join(outdir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    now = datetime.now()
    pattern = re.compile(r'^\\d{4}-\\d{2}-\\d{2}$')
    # Archive old date-stamped folders
    for entry in os.scandir(outdir):
        if entry.is_dir() and pattern.match(entry.name):
            try:
                folder_date = datetime.strptime(entry.name, '%Y-%m-%d')
            except ValueError:
                continue
            if now - folder_date > timedelta(days=ARCHIVE_DAYS):
                zip_name = os.path.join(archive_dir, f'{entry.name}.zip')
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(entry.path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, outdir)
                            zipf.write(file_path, arcname)
                shutil.rmtree(entry.path)

    # Prune old zip files
    for entry in os.scandir(archive_dir):
        if entry.is_file() and entry.name.endswith('.zip'):
            date_str = entry.name[:-4]
            try:
                zip_date = datetime.strptime(date_str, '%Y-%m-%d')
                if now - zip_date > timedelta(days=ARCHIVE_DAYS):
                    os.remove(entry.path)
            except ValueError:
                continue