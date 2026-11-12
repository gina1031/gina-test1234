"""Word-level transcript of the voiceover for build.py.

Usage: HF_HUB_DISABLE_XET=1 python3 -I tools/transcribe.py <project-dir> <audio-file> [model=medium] [lang=ms]
Writes <project-dir>/transcript.json and prints the phrases.
Needs: pip install faster-whisper, and network access to huggingface.co + its CDN for the first model download.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

proj, audio = Path(sys.argv[1]), sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "medium"
lang = sys.argv[4] if len(sys.argv) > 4 else "ms"
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
    np.frombuffer(pcm, np.int16).astype(np.float32) / 32768, language=lang, word_timestamps=True,
    beam_size=5, condition_on_previous_text=False)
out = []
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
    out.append({"file": Path(audio).name, "start": s.start, "end": s.end, "text": s.text,
                "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
(proj / "transcript.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("wrote", proj / "transcript.json")
