import os
import time
import tempfile
import subprocess
from uuid import uuid4
from datetime import datetime

import whisper
import torch
from pydub import AudioSegment
from pyannote.audio import Pipeline

from src.utils.config import get_config
from src.utils.db import insert_transcript
from src.utils.logging_config import logger

_model = None
_diar_pipeline = None

def get_model():
    global _model
    if _model is None:
        cfg = get_config()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Loading Whisper model '{cfg['model']}' on device {device}")
        _model = whisper.load_model(cfg['model'], device=device)
    return _model

def get_diar_pipeline():
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

def process_file(path, outdir):
    cfg = get_config()
    attempts = 0
    backoff = 60
    max_attempts = 3
    tmp_path = None

    while attempts < max_attempts:
        try:
            tmp_path = preprocess_audio(path)
            model = get_model()
            result = model.transcribe(tmp_path, word_timestamps=True)
            whisper_segments = result.get('segments', [])
            text = result.get('text', '')

            segments = []
            diar_pipeline = get_diar_pipeline()
            if diar_pipeline:
                diar = diar_pipeline(tmp_path)
                for turn, _, speaker in diar.itertracks(yield_label=True):
                    seg_texts = []
                    for ws in whisper_segments:
                        if ws['start'] >= turn.start and ws['start'] <= turn.end:
                            seg_texts.append(ws['text'].strip())
                    combined = " ".join(seg_texts).strip()
                    if combined:
                        segments.append({
                            "speaker": speaker,
                            "start": float(turn.start),
                            "end": float(turn.end),
                            "text": combined
                        })
                content = "\n".join(f"{s['speaker']}: {s['text']}" for s in segments)
            else:
                segments = [{
                    "speaker": "SPEAKER_01",
                    "start": 0.0,
                    "end": len(text.split()) / 2.5,
                    "text": text
                }]
                content = text

            date_folder = datetime.now().strftime('%Y-%m-%d')
            full_out = os.path.join(outdir, date_folder)
            os.makedirs(full_out, exist_ok=True)
            base = os.path.basename(path)
            filename = os.path.splitext(base)[0] + '.txt'
            out_path = os.path.join(full_out, filename)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)

            timestamp = datetime.now().isoformat()
            insert_transcript(path, content, timestamp)
            logger.info(f"Successfully processed {path} -> {out_path}")
            return segments

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
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

def generate_ass_from_segments(segments, ass_path):
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
Title: SubSplit Subs
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H00000000,-1,0,1,1.5,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Text
""")
        for seg in segments:
            start = str(datetime.utcfromtimestamp(seg["start"]).strftime("%H:%M:%S.%f")[:-3])
            end = str(datetime.utcfromtimestamp(seg["end"]).strftime("%H:%M:%S.%f")[:-3])
            text = seg["text"].replace('\n', ' ').replace(',', ',,')
            f.write(f"Dialogue: 0,{start},{end},Default,{seg['speaker']}: {text}\n")

def transcribe_video(input_path: str) -> str:
    base = os.path.splitext(os.path.basename(input_path))[0]
    ass_path = f"temp/{base}.ass"
    output_path = f"temp/{base}_subtitled.mp4"
    os.makedirs("temp", exist_ok=True)

    segments = process_file(input_path, "temp")
    generate_ass_from_segments(segments, ass_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"ass={ass_path}",
        "-c:a", "copy",
        output_path
    ], check=True)

    return output_path
