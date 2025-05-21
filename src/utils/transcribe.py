"""
Audio preprocessing, Whisper transcribe + diarization, summary, retry logic
"""
import os
import time
import tempfile
from uuid import uuid4
from datetime import datetime

import whisper
import torch
from openai import OpenAI
from pydub import AudioSegment
from pyannote.audio import Pipeline

from config import get_config
from db import insert_transcript
from logging_config import logger

# Module‐level caches
_model = None
_diar_pipeline = None

def get_model():
    """Load Whisper model once, using config settings."""
    global _model
    if _model is None:
        cfg = get_config()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Loading Whisper model '{cfg['model']}' on device {device}")
        _model = whisper.load_model(cfg['model'], device=device)
    return _model

def get_diar_pipeline():
    """Load Pyannote speaker diarization pipeline once."""
    global _diar_pipeline
    if _diar_pipeline is None:
        try:
            logger.info("Loading diarization pipeline 'pyannote/speaker-diarization'")
            token = os.getenv('HUGGINGFACE_TOKEN')
            _diar_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization",
                use_auth_token=token
            )
        except Exception as e:
            logger.warning(f"Diarization pipeline load failed: {e}")
            _diar_pipeline = None
    return _diar_pipeline

def preprocess_audio(path):
    """Normalize audio and export to a temp WAV file."""
    try:
        audio = AudioSegment.from_file(path)
        audio = audio.normalize()
        tmp_filename = f"transcriber_{uuid4().hex}.temp.wav"
        tmp_path = os.path.join(tempfile.gettempdir(), tmp_filename)
        audio.export(tmp_path, format="wav")
        return tmp_path
    except Exception as e:
        logger.error(f"Audio preprocessing failed for {path}: {e}", exc_info=True)
        raise

def summarize_text(text):
    """Split text into chunks and summarize via OpenAI v1 client."""
    cfg = get_config()
    key = cfg.get("openai_api_key")
    if not key:
        logger.warning("No OpenAI API key; skipping summary")
        return None

    # Instantiate the v1 client
    client = OpenAI(api_key=key)

    # Build ~2 000‑char chunks on sentence boundaries
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 2 > 2000:
            chunks.append(current)
            current = s + ". "
        else:
            current += s + ". "
    if current:
        chunks.append(current)

    summary = ""
    for chunk in chunks:
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": chunk}],
                temperature=0.5,
            )
            summary += resp.choices[0].message.content.strip() + "\n"
        except Exception as e:
            logger.error(f"Summarization failed: {e}", exc_info=True)
            break

    return summary.strip() if summary else None




def process_file(path, outdir):
    """
    Full transcription pipeline:
      - Preprocess audio
      - Whisper transcription
      - Speaker diarization
      - Summary (if API key)
      - Save to dated folder
      - Insert into DB
    """
    cfg = get_config()
    attempts = 0
    backoff = 60
    max_attempts = 3
    tmp_path = None

    while attempts < max_attempts:
        try:
            # 1) Preprocess
            tmp_path = preprocess_audio(path)

            # 2) Transcribe
            model = get_model()
            result = model.transcribe(tmp_path)
            text = result.get('text', '')

            # 3) Diarization
            diar_pipeline = get_diar_pipeline()
            if diar_pipeline:
                diar = diar_pipeline(tmp_path)
                content = ''
                for turn, _, speaker in diar.itertracks(yield_label=True):
                    start_ms = int(turn.start * 1000)
                    end_ms = int(turn.end * 1000)
                    segment_text = text[start_ms:end_ms].strip()
                    content += f"{speaker}: {segment_text}\n"
            else:
                content = text

            # 4) Summarize
            summary = summarize_text(text)

            # 5) Save to file
            date_folder = datetime.now().strftime('%Y-%m-%d')
            full_out = os.path.join(outdir, date_folder)
            os.makedirs(full_out, exist_ok=True)
            base = os.path.basename(path)
            filename = os.path.splitext(base)[0] + '.txt'
            out_path = os.path.join(full_out, filename)
            with open(out_path, 'w', encoding='utf-8') as f:
                if summary:
                    f.write('=== Summary ===\n')
                    f.write(summary + '\n\n')
                    f.write('=== Transcript ===\n')
                f.write(content)

            # 6) DB insert
            timestamp = datetime.now().isoformat()
            insert_transcript(path, content, timestamp, summary)

            logger.info(f"Successfully processed {path} -> {out_path}")
            return out_path

        except Exception as e:
            attempts += 1
            logger.error(f"Error processing {path} (attempt {attempts}/{max_attempts}): {e}", exc_info=True)
            if attempts < max_attempts:
                time.sleep(backoff)
                backoff *= 2
            else:
                logger.error(f"Max retries reached for {path}; skipping.")
                raise

        finally:
            # Cleanup temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
