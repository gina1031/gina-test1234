"""DRAFT Malay voiceover from a script, for timing/preview only.

Uses facebook/mms-tts-zlm (licence CC-BY-NC 4.0: NON-commercial). Replace with a real recording
before posting; build.py retimes everything after you re-run transcribe.py on the new audio.

Usage (torch + transformers + faster-whisper needed, e.g. in a venv):
  HF_HUB_DISABLE_XET=1 python -I tools/tts_draft.py <say.txt> <target.txt> <out.m4a> [variants=4] [rate=1.02]
  say.txt    one sentence per line, spelled phonetically for the TTS ("frihold", "open taitel", numbers as words)
  target.txt same lines as they should be heard/captioned ("freehold", "open title", "86")
Each line is synthesized N times; the take Whisper understands best is kept.
"""
import difflib, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf, torch
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, VitsModel

say = [l.strip() for l in open(sys.argv[1]) if l.strip()]
tgt = [l.strip() for l in open(sys.argv[2]) if l.strip()]
out, N = sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 4
rate = float(sys.argv[5]) if len(sys.argv) > 5 else 1.02
assert len(say) == len(tgt), "say.txt and target.txt need the same number of lines"
tts = VitsModel.from_pretrained("facebook/mms-tts-zlm"); tok = AutoTokenizer.from_pretrained("facebook/mms-tts-zlm")
tts.speaking_rate, tts.noise_scale, sr = rate, 0.5, tts.config.sampling_rate
asr = WhisperModel("medium", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
tmp = tempfile.mkdtemp(); takes = []
for i, (l, t) in enumerate(zip(say, tgt)):
    best = (-1, None, "")
    for seed in range(N):
        torch.manual_seed(100 * i + seed)
        with torch.no_grad():
            w = tts(**tok(l, return_tensors="pt")).waveform[0].numpy()
        a16 = np.interp(np.arange(0, len(w), sr / 16000), np.arange(len(w)), w).astype(np.float32)
        heard = " ".join(s.text for s in asr.transcribe(a16, language="ms", beam_size=5)[0])
        sc = difflib.SequenceMatcher(None, norm(heard), norm(t)).ratio()
        if sc > best[0]:
            best = (sc, w, heard)
    print(f"{i}: {best[0]:.2f}  {best[2].strip()}")
    takes += [best[1], np.zeros(int(sr * 0.28), np.float32)]
wav = f"{tmp}/vo.wav"; sf.write(wav, np.concatenate(takes), sr)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", "highpass=f=80,loudnorm=I=-16:TP=-1.5",
                "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "160k", out], check=True)
print("wrote", out)
