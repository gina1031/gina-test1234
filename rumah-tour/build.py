"""Generates index.html from the voiceover word timestamps (transcript.json).

Run: python3 build.py
All timing is derived from the voiceover: pauses are tightened (CUTS), then every
graphic, cut and caption is keyed to the word it belongs to.
"""
import json, html, re
from pathlib import Path

ROOT = Path(__file__).parent
words = []
for seg in json.loads((ROOT / "transcript.json").read_text()):
    if not seg["file"].endswith(".mp3"):
        continue
    for w in seg["words"]:
        words.append({"w": w["w"].strip(), "s": w["s"], "e": w["e"]})

# Merge tokens whisper split ("4" ",102"), fix spelling.
merged = []
for w in words:
    if merged and re.match(r"^[,.]\d", w["w"]):
        merged[-1]["w"] += w["w"]; merged[-1]["e"] = w["e"]
    else:
        merged.append(dict(w))
FIX = {"Syah": "Shah", "4,102": "4,102", "RM598,888.": "RM598,888."}
for w in merged:
    w["w"] = FIX.get(w["w"], w["w"])

# Voiceover pauses to tighten: (start, end) in source seconds, removed from the film.
CUTS = [(10.685, 10.91), (20.548, 20.809), (27.23, 27.505), (35.87, 36.087)]
VO_END = 37.956


def T(t):
    """Source voiceover time -> film time."""
    off = 0.0
    for a, b in CUTS:
        if t >= b:
            off += b - a
        elif t > a:
            off += t - a
    return round(t - off, 3)


def at(word, n=1):
    """Film time of the n-th occurrence of a word (exact match, punctuation stripped)."""
    k = 0
    for w in merged:
        if w["w"].lower().strip(",.?!") == word.lower():
            k += 1
            if k == n:
                return T(w["s"])
    raise KeyError(word)


D = round(T(VO_END) + 1.6, 2)

# ---------- VO pieces ----------
pieces, prev = [], 0.0
for a, b in CUTS + [(VO_END, VO_END)]:
    pieces.append((prev, a)); prev = b
vo_html = "\n".join(
    f'      <audio id="vo-{i}" src="assets/vo/voiceover.m4a" data-start="{T(s)}" data-duration="{round(e - s, 3)}" '
    f'data-media-start="{s}" data-volume="1" data-track-index="9"></audio>'
    for i, (s, e) in enumerate(pieces))

# ---------- Scenes (visual track) ----------
t_jom = at("Jom")                 # "Jom tengok rumah setingkat..."
t_rumah_ini = at("Rumah", 3)      # "Rumah ini ada 3 bilik..."
t_dua_air = at("2", 2)               # "...2 bilik air"
t_best = at("Yang", 2)               # "Yang paling best"
t_bahagian = at("Bahagian")
t_nak_buat = at("Nak", 3)         # "Nak buat mini garden"
t_siap = at("Rumah", 5)           # "Rumah dah siap"
t_dp = at("Downpayment")
t_berminat = at("Berminat")

S = []  # (id, src, start, end, media_start, kind)
def scene(i, src, a, b, ms=0, kind="video"):
    S.append((i, src, round(a, 3), round(b, 3), ms, kind))

scene("v-hook", "assets/clips/20261017_130833.mp4", 0, t_jom - 0.15, 0)
scene("v-front", "assets/clips/20261017_130938.mp4", t_jom - 0.15, t_jom + 1.55, 0)
scene("v-hall", "assets/clips/20261017_130855.mp4", t_jom + 1.55, t_rumah_ini - 0.65, 0)
scene("v-bed", "assets/clips/20261017_130929.mp4", t_rumah_ini - 0.65, t_rumah_ini + 1.15, 0)
scene("v-room", "assets/clips/20261017_130945.mp4", t_rumah_ini + 1.15, t_dua_air + 0.35, 1.2)
scene("v-bath", "assets/clips/20261017_130923.mp4", t_dua_air + 0.35, t_best, 0)
scene("i-land", "assets/stills/land-end.jpg", t_best, t_bahagian - 0.2, 0, "img")
scene("v-side", "assets/clips/land_slow.mp4", t_bahagian - 0.2, t_nak_buat - 0.15, 0)
scene("i-gc", "assets/stills/land-end.jpg", t_nak_buat - 0.15, t_siap - 0.15, 0, "imgblur")
scene("v-ready", "assets/clips/front_slow.mp4", t_siap - 0.15, t_dp - 0.15, 0.3)
scene("i-price", "assets/stills/bedroom.jpg", t_dp - 0.15, D, 0, "imgblur")
for i, src, a, b, ms, kind in S:
    if kind == "video":
        assert b - a <= {"assets/clips/20261017_130833.mp4": 2.86, "assets/clips/20261017_130938.mp4": 1.73,
                         "assets/clips/20261017_130855.mp4": 2.56, "assets/clips/20261017_130929.mp4": 1.83,
                         "assets/clips/20261017_130945.mp4": 3.3, "assets/clips/20261017_130923.mp4": 1.2,
                         "assets/clips/land_slow.mp4": 5.73, "assets/clips/front_slow.mp4": 3.5}[src] - ms + 0.01, (i, b - a)

def scene_html(i, src, a, b, ms, kind):
    d = round(b - a, 3)
    if kind == "video":
        return (f'      <video id="{i}" class="clip" src="{src}" data-start="{a}" data-duration="{d}" '
                f'data-media-start="{ms}" muted data-track-index="0"></video>')
    cls = "clip bg-blur" if kind == "imgblur" else "clip"
    return f'      <img id="{i}" class="{cls}" src="{src}" data-start="{a}" data-duration="{d}" data-track-index="0" />'
scenes_html = "\n".join(scene_html(*s) for s in S)
SC = {s[0]: s for s in S}
def span(i):
    return SC[i][2], round(SC[i][3] - SC[i][2], 3)

# ---------- Captions: chunks of <=4 words, active word highlighted ----------
# One caption per spoken phrase (whisper segment); long phrases split into balanced halves.
chunks, i = [], 0
for seg in json.loads((ROOT / "transcript.json").read_text()):
    if not seg["file"].endswith(".mp3"):
        continue
    n = len([w for w in seg["words"] if not re.match(r"^[,.]\d", w["w"].strip())])
    phrase = merged[i:i + n]; i += n
    if len(phrase) <= 6:
        chunks.append(phrase)
    else:
        h = (len(phrase) + 1) // 2
        chunks += [phrase[:h], phrase[h:]]
cap_html, cap_js = [], []
for ci, ch in enumerate(chunks):
    a = T(ch[0]["s"])
    b = T(chunks[ci + 1][0]["s"]) if ci + 1 < len(chunks) else D
    spans = " ".join(f'<span class="cw" id="cw{ci}_{k}">{html.escape(w["w"])}</span>' for k, w in enumerate(ch))
    cap_html.append(f'        <div class="cap" id="cap{ci}">{spans}</div>')
    cap_js.append(f'tl.set("#cap{ci}", {{ autoAlpha: 1 }}, {a}).set("#cap{ci}", {{ autoAlpha: 0 }}, {b});')
    cap_js.append(f'tl.fromTo("#cap{ci}", {{ scale: 0.85 }}, {{ scale: 1, duration: 0.15, ease: "back.out(3)" }}, {a});')
    for k, w in enumerate(ch):
        cap_js.append(f'tl.set("#cw{ci}_{k}", {{ color: "#ffd400" }}, {T(w["s"])})'
                      f'.set("#cw{ci}_{k}", {{ color: "#ffffff" }}, {T(w["e"]) + 0.05});')

# ---------- Key word times ----------
K = dict(
    corner=at("corner"), tanah=at("tanah"), lombong=at("Lombong"), seksyen=at("seksyen"),
    tiga=at("3"), dua=t_dua_air, best=t_best, luas_n=at("4,102"), kaki=at("kaki"),
    bahagian=t_bahagian, empat=at("4"), kereta=at("kereta"), mini=at("mini"), tempat=at("tempat"),
    ruang=at("ruang"), siap=t_siap, dp=t_dp, harga=at("harga"), rm=at("RM598,888"), berminat=t_berminat,
    whatsapp=at("WhatsApp"),
)
K = {k: round(v, 3) for k, v in K.items()}

SFX = [
    ("impact", 0.0, 0.85), ("pop", K["corner"], 0.55), ("pop", K["tanah"], 0.55),
    ("whoosh", t_jom - 0.4, 0.8), ("pop", K["lombong"], 0.5), ("pop", K["seksyen"], 0.45),
    ("whoosh", SC["v-hall"][2] - 0.25, 0.6), ("whoosh", SC["v-bed"][2] - 0.25, 0.7),
    ("impact", K["tiga"], 0.5), ("whoosh", SC["v-room"][2] - 0.25, 0.6), ("pop", K["dua"], 0.55),
    ("riser", K["best"] - 0.9, 0.5), ("impact", K["best"], 0.75), ("tick", K["luas_n"], 0.6),
    ("ding", K["kaki"], 0.55), ("whoosh", SC["v-side"][2] - 0.25, 0.8),
    ("pop", K["empat"], 0.55), ("pop", K["empat"] + 0.2, 0.55), ("pop", K["empat"] + 0.4, 0.55), ("pop", K["empat"] + 0.6, 0.55),
    ("whoosh", SC["i-gc"][2] - 0.25, 0.7), ("tick", K["mini"], 0.7), ("tick", K["tempat"], 0.7), ("tick", K["ruang"], 0.7),
    ("whoosh", SC["v-ready"][2] - 0.25, 0.8), ("pop", K["siap"] + 0.1, 0.55),
    ("whoosh", SC["i-price"][2] - 0.25, 0.8), ("pop", K["dp"] + 0.05, 0.6), ("tick", K["harga"] + 0.4, 0.8),
    ("impact", K["rm"], 0.75), ("ding", K["rm"] + 0.05, 0.65), ("pop", K["whatsapp"], 0.6),
]
DUR = {"impact": 0.9, "pop": 0.12, "whoosh": 0.6, "tick": 0.06, "riser": 1.2, "ding": 1.2}
sfx_html = "\n".join(
    f'      <audio id="s{i:02d}" src="assets/sfx/{f}.wav" data-start="{round(t, 3)}" data-duration="{DUR[f]}" '
    f'data-volume="{v}" data-track-index="{4 + i % 4}"></audio>'
    for i, (f, t, v) in enumerate(sorted(SFX, key=lambda x: x[1])))

cuts = sorted({s[2] for s in S if s[2] > 0})
g = {k: span(k) for k in SC}

tpl = (ROOT / "index.tpl").read_text()
out = tpl
for k, v in dict(
    D=D, SCENES=scenes_html, VO=vo_html, SFX=sfx_html, CAPS="\n".join(cap_html), CAPJS="\n      ".join(cap_js),
    CUTS=json.dumps(cuts), K=json.dumps(K),
    HOOK=f'data-start="0" data-duration="{g["v-hook"][1]}"',
    LOC=f'data-start="{K["lombong"] - 0.2}" data-duration="{round(SC["v-hall"][3] - K["lombong"] + 0.2, 3)}"',
    BED=f'data-start="{SC["v-bed"][2]}" data-duration="{round(SC["v-bath"][3] - SC["v-bed"][2], 3)}"',
    LAND=f'data-start="{g["i-land"][0]}" data-duration="{g["i-land"][1]}"',
    SIDE=f'data-start="{g["v-side"][0]}" data-duration="{g["v-side"][1]}"',
    GC=f'data-start="{g["i-gc"][0]}" data-duration="{g["i-gc"][1]}"',
    READY=f'data-start="{g["v-ready"][0]}" data-duration="{g["v-ready"][1]}"',
    PRICE=f'data-start="{g["i-price"][0]}" data-duration="{g["i-price"][1]}"',
).items():
    out = out.replace("{{" + k + "}}", str(v))
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
(ROOT / "index.html").write_text(out)
print("duration", D)
for s in S:
    print(f"  {s[0]:9s} {s[2]:6.2f}-{s[3]:6.2f}")
print(K)
