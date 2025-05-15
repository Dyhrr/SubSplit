# 🟪 SubSplit

### "Because your clips deserve more than subtitles thrown on with a prayer."

**SubSplit** is a dark-mode-only, GPU-aware, multi-threaded subtitle generation tool built for content creators who are tired of basic captions and even more tired of doing it manually.

Powered by [OpenAI's Whisper](https://github.com/openai/whisper), SubSplit doesn't just transcribe. It:
- Detects who's talking (yes, multiple speakers—imagine that).
- Assigns each speaker a color (because you’re not a robot).
- Embeds fully stylized, readable subtitles back into the video.
- Supports multiple video/audio files at once.
- Gives you a slick UI, drag-and-drop ease, and background task handling with ETA tracking.

## ⚙️ Features

- 🎤 **Diarization** — Separate speakers like a courtroom drama.
- 🎨 **Color-coded Subtitles** — Each voice gets its own shade. You’re welcome.
- 🎛️ **Custom Whisper Settings** — Control which Whisper model you use, temp folder paths, and language.
- 📁 **Multi-file Support** — Process all your unedited chaos at once.
- 🧠 **Error Handling + Logs** — Because real devs build for when stuff breaks.
- 💻 **Dark Mode UI** — If you use light mode, this isn't for you.
- 🐢 **Built for Creators** — Especially if you’re broke, tired, or allergic to Premiere Pro.

## 🧠 Tech Stack

- **Python** (obviously)
- **Whisper** (for transcribing)
- **PyQt6** (for GUI)
- **FFmpeg** (for audio/video handling)
- **You, panicking at 3AM** (for inspiration)

## 🖥️ Screenshot

*Coming soon—because screenshots require effort and you’re reading this instead of contributing.*

## 🚀 Getting Started

Clone it. Run it. Watch the magic.

```bash
git clone https://github.com/Dyhrr/SubSplit
cd SubSplit
pip install -r requirements.txt
python cli.py
```
Whisper and FFmpeg must be installed separately. Google is your friend. Or not. I’m not your dad.

📦 Roadmap
OBS Replay Buffer integration

Highlight system triggers

Full web version (eventually)

Optional turtle mascot (probably cursed)

🐞 Known Issues
Whisper large model may break your Pi and your spirit.

UI is “functional” but not emotionally supportive yet.

No unit tests (yet). Sue me.

🧙 Author
Nick / Dyhrrr
Dev.
Creates tools for others, forgets to finish my own.
Sleeps on the floor, but builds like a king.
