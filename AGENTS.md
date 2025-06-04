This file describes the agents (modular Python scripts) used in the SubSplit project. Each agent is responsible for a specific task in the processing pipeline. The architecture is designed to be modular and extensible. Agents are either run manually or orchestrated by a central manager (planned).

Agent List
transcribe.py
Description: Runs OpenAI Whisper on a given media file to produce a transcription.

Input: Video or audio file path.

Output: Transcription in .srt and/or .json format.

Notes: Supports multilingual input. Uses GPU acceleration if available.

diarize.py
Description: Applies speaker diarization (voice labeling) to the transcript.

Input: Transcript file and source media file.

Output: Modified transcript with speaker labels.

Notes: Optional. Uses PyAnnote when enabled. May fallback to simpler diarization in future.

clipper.py
Description: Cuts input video into clips based on timestamps (e.g. from subtitles or markers).

Input: Video file and timestamp data.

Output: Multiple video clips.

Notes: Uses FFmpeg. Smart merge and padding behavior is planned.

subgen.py
Description: Generates hardcoded subtitles onto video clips.

Input: Video file and subtitle file.

Output: Subtitled video file.

Notes: Supports styling options (font, position, color).

manager.py
Description: Manages execution of agents, job queue, error handling, and status updates.

Input: Config file and job definitions.

Output: Status logs and orchestrated pipeline execution.

Notes: Intended as the orchestrator in future versions.

filewatcher.py (planned)
Description: Watches a folder for new video files and triggers processing.

Input: Directory path.

Output: Job dispatch events.

Notes: Will run as a low-resource daemon or background process.

highlight.py (WIP)
Description: Detects highlights in a video using heuristics or NLP cues (e.g. laughter, keywords).

Input: Transcript and/or audio waveform.

Output: Highlight timestamp ranges.

Notes: Currently in development. Will support keyword exclusion (e.g. soundboard spam filtering).

Notes
All agents should be written as standalone Python modules.

Long-term goal is to run agents asynchronously and independently where possible.

Agents will be moved into a /core or /agents directory once folder refactor is complete.

Logging and CLI interface will be standardized.
