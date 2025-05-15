# Whisper Transcriber

A modular transcription tool using OpenAI Whisper with a GUI and CLI interface.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to set:

- `model`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`)
- `max_threads`: Maximum concurrent transcription jobs
- `output_dir`: Folder where transcripts and summaries are saved
- `watch_folder`: `true` to enable watch-folder mode on startup
- `watch_path`: Directory path to monitor for new audio/video files
- `openai_api_key`: Your OpenAI API key (for auto-summarization)

## CLI Usage

Transcribe files in headless mode:

```bash
python cli.py --cli --files /path/to/file1.mp3 /path/to/file2.wav --out /path/to/output --verbose
```

- `--cli`: Use command-line mode (no GUI)
- `--files`: One or more input files
- `--out`: Output directory override
- `--verbose`: Print detailed status and errors

## GUI Usage

Launch the graphical interface:

```bash
python cli.py
```

### GUI Features

- **Select Clips**: Choose files to transcribe  
- **Set Output Directory**: Configure where transcripts go  
- **Start Transcription**: Begin batch processing  
- **Retry Failed Files**: Retry any that errored  
- **Clear Logs**: Remove old log files  
- **Toggle Watch**: Enable/disable watch-folder mode  
- **Minimize to Tray**: Send GUI to system tray  
- **Quit**: Exit the application  

A per-file status and overall progress bar display live updates.

## Watch-Folder Mode

If enabled in `config.json` or via **Toggle Watch**, the tool monitors `watch_path` and auto-processes new files dropped into that folder.

## Archive Management

Transcript folders older than 7 days are automatically zipped into `<output_dir>/archive/YYYY-MM-DD.zip` and removed, keeping your storage organized.

## Project Structure

- `config.py` – load and validate settings  
- `db.py` – SQLite database layer  
- `transcribe.py` – core transcription, diarization, and summarization  
- `watcher.py` – folder watching and archival logic  
- `gui.py` – Tkinter GUI and system tray integration  
- `cli.py` – command-line entrypoint  
- `logging_config.py` – centralized logging setup  
- `requirements.txt` – Python dependencies  
- `README.md` – this documentation  
- `config.json` – user-editable settings  

## Logging

Logs are written to both the console and `logs/app.log` (rotated, max 5MB per file, 5 backups).

## Troubleshooting

- **Missing OpenAI key**: Summaries are skipped if `openai_api_key` is empty.  
- **Model load errors**: Check that `torch` can access CUDA or CPU properly.  
- **Permission issues**: Ensure the script has write access to `output_dir` and `logs/`.  
- **Watch errors**: Verify `watch_path` exists and `watch_folder` is true.

Enjoy streamlined, automated transcriptions!