"""Property-tour video builder: config.json + transcript.json -> index.html (HyperFrames).

    python3 build.py            # writes index.html, prints the timeline

Everything is timed off the voiceover's words. A time reference ("ref") in config.json is:
    0 / 2.5                  seconds in the finished film
    "w:tanah"                when the 1st spoken word "tanah" starts   (punctuation ignored, case-insensitive)
    "w:rumah#3-0.65"         0.65s before the 3rd "rumah"
    "s:hall.end+0.2"         0.2s after scene "hall" ends   (.start / .end)
    "end"                    end of the film
Voiceover pauses longer than `pause_max` are shortened to `pause_keep` automatically.
"""
import html, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
CFG = json.loads((ROOT / "config.json").read_text())
TX = [s for s in json.loads((ROOT / CFG.get("transcript", "transcript.json")).read_text())]
TXT = CFG["text"]

# ---------------- words ----------------
words = []
for seg in TX:
    seg_words = []
    for w in seg["words"]:
        t = w["w"].strip()
        if seg_words and (re.match(r"^[,.]\d", t) or re.match(r"^-\w", t)):  # "4" ",102" / "built" "-up"
            seg_words[-1]["w"] += t; seg_words[-1]["e"] = w["e"]
        else:
            seg_words.append({"w": t, "s": w["s"], "e": w["e"]})
    for w in seg_words:
        w["w"] = CFG.get("fix_words", {}).get(w["w"], w["w"])
    seg["_words"] = seg_words
    words += seg_words

# ---------------- pause tightening ----------------
# Cut only where the voiceover is actually quiet (measured loudness), never on word-gap guesses:
# whisper's word ends can be early for long spoken numbers ("lapan puluh enam" -> "86").
pmax, pkeep = CFG.get("pause_max", 0.3), CFG.get("pause_keep", 0.1)
# Loudness every 50 ms; "quiet" = within `quiet_db` (default 6 dB) of the recording's own noise floor
# (10th percentile), so room tone / cloned-voice hiss doesn't hide the pauses.
_rms = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / CFG["voiceover"]), "-af",
                       "aresample=16000,asetnsamples=800,astats=metadata=1:reset=1,"
                       "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"],
                      capture_output=True, text=True).stdout
_lv = [max(-90.0, float(x)) if x not in ("-inf", "inf") else -90.0 for x in re.findall(r"RMS_level=(-?[\d.]+|-?inf)", _rms)]
_floor = sorted(_lv)[len(_lv) // 10] if _lv else -90
_q = [v < _floor + CFG.get("quiet_db", 6) for v in _lv]
_runs, i = [], 0
while i < len(_q):
    if _q[i]:
        j = i
        while j < len(_q) and _q[j]:
            j += 1
        _runs.append((i * 0.05, j * 0.05)); i = j
    else:
        i += 1
_st = [a for a, b in _runs]; _en = [b for a, b in _runs]
CUTS = [(round(a + pkeep / 2, 3), round(b - pkeep / 2, 3)) for a, b in _runs
        if a > 0.05 and b - a > pmax and a < words[-1]["s"]]
VO_END = min(words[-1]["e"] + 0.5, _st[-1] + 0.05) if _st and _st[-1] > words[-1]["s"] else words[-1]["e"] + 0.3


def T(t):
    off = 0.0
    for a, b in CUTS:
        off += (b - a) if t >= b else max(0.0, t - a)
    return round(t - off, 3)


D = round(T(VO_END) + CFG.get("end_hold", 1.3), 2)
norm = lambda s: s.lower().strip(",.?!:;\"'“”‘’")


def word_t(word, n=1):
    hits = [w for w in words if norm(w["w"]) == norm(word)]
    if len(hits) < n:
        raise SystemExit(f'config error: word "{word}" #{n} not in transcript (found {len(hits)}). '
                         f'Words: {" ".join(norm(w["w"]) for w in words)}')
    return T(hits[n - 1]["s"])


SCENE_T = {}
REF = re.compile(r"^(?:w:(?P<w>[^#+]+?)(?:#(?P<n>\d+))?|s:(?P<s>[\w-]+)\.(?P<edge>start|end)|(?P<end>end))(?P<off>[+-]\d*\.?\d+)?$")


def ref(r):
    if isinstance(r, (int, float)):
        return float(r)
    m = REF.match(r.strip())
    if not m:
        raise SystemExit(f"config error: bad time ref {r!r}")
    off = float(m["off"] or 0)
    if m["w"]:
        base = word_t(m["w"], int(m["n"] or 1))
    elif m["s"]:
        base = SCENE_T[m["s"]][0 if m["edge"] == "start" else 1]
    else:
        base = D
    return round(base + off, 3)


# ---------------- voiceover pieces ----------------
vo_src = CFG["voiceover"]
pieces, prev = [], 0.0
for a, b in CUTS + [(VO_END, VO_END)]:
    pieces.append((prev, a)); prev = b
VO = "\n".join(f'      <audio id="vo-{i}" src="{vo_src}" data-start="{T(s)}" data-duration="{round(e - s, 3)}" '
               f'data-media-start="{s}" data-volume="{CFG.get("vo_volume", 1)}" data-track-index="9"></audio>'
               for i, (s, e) in enumerate(pieces))

# ---------------- SFX helper ----------------
SFX = [("impact", 0.0, 0.85)]
def sfx(kind, t, v=0.55):
    SFX.append((kind, round(t, 3), v))

# ---------------- scenes ----------------
def media_len(src):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                     str(ROOT / src)], capture_output=True, text=True, check=True).stdout)
    except Exception:
        return None

scenes = CFG["scenes"]
starts = [ref(s["from"]) for s in scenes]
for i, s in enumerate(scenes):
    SCENE_T[s["id"]] = (starts[i], starts[i + 1] if i + 1 < len(scenes) else D)
SC_HTML, KB, problems = [], [], []
SLIDE = CFG.get("transitions", "flash") == "slide"
ENTER = [("xPercent", 100), ("yPercent", 100), ("scale", 1.35), ("xPercent", -100)]


def img_size(src):
    try:
        w, h = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                               str(ROOT / src)], capture_output=True, text=True, check=True).stdout.strip().split(",")[:2]
        return int(w), int(h)
    except Exception:
        return 1080, 1920


for si, s in enumerate(scenes):
    a, b = SCENE_T[s["id"]]; kind = s.get("kind", "video"); sid = "sc-" + s["id"]
    last = si == len(scenes) - 1
    d = round(b - a + (0 if last or not SLIDE else 0.5), 3)      # overlap so the next scene slides in over this one
    if not (ROOT / s["src"]).exists():
        problems.append(f'scene "{s["id"]}": file not found: {s["src"]}')
    if b - a <= 0:
        problems.append(f'scene "{s["id"]}" has no length ({a}->{b}); check its "from" against the next scene')
    k0, k1 = s.get("kb", [1.0, 1.1] if kind == "video" else [1.12, 1.25])
    if kind == "video":
        ms = s.get("media_start", 0); L = media_len(s["src"])
        if L is not None and d > L - ms + 0.02:
            problems.append(f'scene "{s["id"]}" needs {d:.2f}s but {s["src"]} has {L - ms:.2f}s after media_start '
                            f'(use a slow-mo copy, a still, or move the cut)')
        SC_HTML.append(f'      <video id="{sid}" class="clip" src="{s["src"]}" data-start="{a}" data-duration="{d}" '
                       f'data-media-start="{ms}" muted data-track-index="0"></video>')
        KB.append(f'tl.fromTo("#{sid}", {{ scale: {k0} }}, {{ scale: {k1}, duration: {d}, ease: "none" }}, {a});')
    elif kind == "card":                                   # framed photo over its own blurred copy, floats, can zoom to spots
        iw, ih = img_size(s["src"]); W = s.get("width", 1000); H = round(W * ih / iw)
        top = s.get("top", round(1000 - H / 2))
        pin = ""
        if s.get("pin"):
            px, py = s["pin"]["x"], s["pin"]["y"]
            pin = (f'<div class="sc-pin" style="left:{px}%;top:{py}%"><div class="pin-pulse"></div>'
                   f'<div class="pin-dot">📍</div></div>')
        SC_HTML.append(f'      <div id="{sid}" class="clip scard" data-start="{a}" data-duration="{d}" data-track-index="0">'
                       f'<img class="sc-bg" src="{s["src"]}" />'
                       f'<div class="sc-wrap" style="top:{top}px;left:{(1080 - W) // 2}px;width:{W}px;height:{H}px">'
                       f'<div class="sc-zoom"><img class="sc-fg" src="{s["src"]}" />{pin}</div></div></div>')
        KB += [f'tl.fromTo("#{sid} .sc-bg", {{ scale: 1.25, x: 30 }}, {{ scale: 1.4, x: -30, duration: {d}, ease: "none" }}, {a});',
               f'tl.fromTo("#{sid} .sc-wrap", {{ scale: 0.72, rotation: -5, y: 140, opacity: 0 }}, {{ scale: 1, rotation: 0, y: 0, opacity: 1, duration: 0.7, ease: "back.out(1.6)" }}, {a + 0.05});',
               f'tl.to("#{sid} .sc-wrap", {{ y: -14, rotation: 0.6, duration: {round(max(0.8, (d - 0.8) / 2), 3)}, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {a + 0.75});']
        focus = s.get("focus", [])
        if not focus:
            KB.append(f'tl.fromTo("#{sid} .sc-zoom", {{ scale: {k0} }}, {{ scale: {k1}, duration: {d}, ease: "none" }}, {a});')
        for f in focus:                                    # zoom inside the frame to a point (x%, y%)
            t = ref(f["at"]); z = f.get("s", 2.2)
            tx = round((0.5 - f["x"] / 100) * W * z); ty = round((0.5 - f["y"] / 100) * H * z)
            KB.append(f'tl.to("#{sid} .sc-zoom", {{ scale: {z}, x: {tx}, y: {ty}, duration: 0.7, ease: "power3.inOut" }}, {t});')
            sfx("whoosh", t, 0.45)
        if s.get("focus_out"):
            KB.append(f'tl.to("#{sid} .sc-zoom", {{ scale: 1, x: 0, y: 0, duration: 0.7, ease: "power3.inOut" }}, {ref(s["focus_out"])});')
        if s.get("pin"):
            pt = ref(s["pin"].get("at", a + 0.6))
            sfx("pop", pt, 0.6)
            KB += [f'tl.fromTo("#{sid} .pin-dot", {{ y: -260, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.55, ease: "bounce.out" }}, {pt});',
                   f'tl.fromTo("#{sid} .pin-pulse", {{ scale: 0.4, opacity: 0.9 }}, {{ scale: 3.2, opacity: 0, duration: 1.1, ease: "power1.out", repeat: {max(0, int((b - pt) / 1.1) - 1)} }}, {pt + 0.4});']
    elif kind == "pan":                                    # tall image (floor plan) scrolled top -> bottom
        iw, ih = img_size(s["src"]); H = round(1080 * ih / iw); travel = max(0, H - 1920)
        SC_HTML.append(f'      <div id="{sid}" class="clip span" data-start="{a}" data-duration="{d}" data-track-index="0">'
                       f'<img class="sc-bg" src="{s["src"]}" /><img class="sc-pan" src="{s["src"]}" style="height:{H}px" /></div>')
        frm, to = (0, -travel) if s.get("dir", "down") == "down" else (-travel, 0)
        KB += [f'tl.fromTo("#{sid} .sc-pan", {{ y: {frm} }}, {{ y: {to}, duration: {d}, ease: "sine.inOut" }}, {a});',
               f'tl.fromTo("#{sid} .sc-bg", {{ scale: 1.3 }}, {{ scale: 1.45, duration: {d}, ease: "none" }}, {a});']
    else:
        cls = "clip bg-blur" if kind == "blur" else "clip"
        SC_HTML.append(f'      <img id="{sid}" class="{cls}" src="{s["src"]}" data-start="{a}" data-duration="{d}" data-track-index="0" />')
        KB.append(f'tl.fromTo("#{sid}", {{ scale: {k0} }}, {{ scale: {k1}, duration: {d}, ease: "none" }}, {a});')
    if SLIDE and si > 0:                                   # scene enters by sliding / zooming over the previous one
        prop, v = ENTER[si % len(ENTER)]
        frm = f"{prop}: {v}" + (", opacity: 0" if prop == "scale" else "")
        to = f"{prop}: {1 if prop == 'scale' else 0}" + (", opacity: 1" if prop == "scale" else "")
        KB.append(f'tl.fromTo("#{sid}", {{ {frm} }}, {{ {to}, duration: 0.5, ease: "power3.out", immediateRender: false }}, {a});')
if problems:
    raise SystemExit("\n".join(["Timeline problems:"] + problems))
if CFG.get("whoosh_on_cuts", True):
    SFX += [("whoosh", max(0, starts[i] - 0.25), 0.7) for i in range(1, len(scenes))]

E = lambda s: html.escape(str(s))
BACK = 'back.out(2.2)'

# ---------------- graphic blocks ----------------
# Each block: (config) -> (html, [js lines]). `c` holds resolved cue times.
def b_hook(c):
    h = f'''        <div class="shade-top"></div>
        <div id="hook-a" class="cx"><span class="tag" style="font-size:{min(76, int(1200 / max(1, len(TXT["hook_tag"]))))}px">{E(TXT["hook_tag"])}</span></div>
        <div id="hook-b" class="cx t-stroke">{E(TXT["hook_line1"])}<br /><span class="y">{E(TXT["hook_line2"])}</span> {E(TXT.get("hook_emoji", ""))}</div>'''
    sfx("pop", c["tag"]); sfx("pop", c["line"])
    return h, [f'tl.fromTo("#hook-a", {{ scale: 2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "{BACK}" }}, {c["tag"]});',
               f'tl.fromTo("#hook-b", {{ scale: 2.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.28, ease: "{BACK}" }}, {c["line"]});',
               f'tl.to("#hook-b", {{ scale: 1.05, duration: 0.15, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {c["line"] + 0.4});']

def b_location(c):
    chip = f'\n          <div id="loc-chip"><span class="tag">{E(TXT["location_chip"])}</span></div>' if TXT.get("location_chip") else ""
    h = f'''        <div id="loc">
          <div class="card">
            <div class="l1">📍 {E(TXT["location"])}</div>
            <div class="l2">{E(TXT.get("area", ""))}</div>
            <div class="l3">{E(TXT.get("property_type", ""))}</div>
          </div>{chip}
        </div>'''
    sfx("pop", c["start"], 0.5)
    js = [f'tl.fromTo("#loc .card", {{ x: -1100 }}, {{ x: 0, duration: 0.45, ease: "power4.out" }}, {c["start"]});']
    if chip:
        sfx("pop", c["chip"], 0.45)
        js.append(f'tl.fromTo("#loc-chip", {{ scale: 0, opacity: 0, transformOrigin: "left center" }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["chip"]});')
    return h, js

def b_rooms(c):
    h = f'''        <div class="shade-top"></div>
        <div id="bilik-num" class="cx t-stroke y">{E(TXT["bedrooms"])}</div>
        <div id="bilik-word" class="cx t-stroke">{E(TXT.get("bedrooms_label", "BILIK TIDUR 🛏️"))}</div>
        <div id="bilikair" class="cx"><span class="pill y">+ {E(TXT["bathrooms"])} {E(TXT.get("bathrooms_label", "BILIK AIR 🚿"))}</span></div>'''
    sfx("impact", c["bed"], 0.5); sfx("pop", c["bath"])
    return h, [f'tl.fromTo("#bilik-num", {{ scale: 3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "power4.out" }}, {c["bed"]});',
               f'tl.fromTo("#bilik-word", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c["bed"] + 0.25});',
               f'tl.fromTo("#bilikair", {{ x: 900, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power4.out" }}, {c["bath"]});']

def b_land(c):
    dims = f'\n        <div id="luas-dim" class="cx"><span class="tag" style="background:#fff;color:#111">{E(TXT["land_dims"])}</span></div>' if TXT.get("land_dims") else ""
    h = f'''        <div class="shade-top"></div>
        <div id="best" class="cx"><span class="pill">{E(TXT.get("land_label", "YANG PALING BEST 🔥"))}</span></div>
        <div id="luas-num" class="cx t-stroke y">0</div>
        <div id="luas-unit" class="cx t-stroke">{E(TXT.get("land_unit", "KAKI PERSEGI"))}</div>{dims}'''
    cs = c.get("count_from", c["start"] + 0.8)
    sfx("riser", c["start"] - 0.9, 0.5); sfx("impact", c["start"], 0.75); sfx("tick", c["number"], 0.6); sfx("ding", c["unit"], 0.55)
    js = [f'tl.fromTo("#best", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c["start"]});',
          f'tl.fromTo("#luas-num", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, {cs});',
          f'(() => {{ const n = {{ v: 0 }}, el = document.querySelector("#luas-num"); tl.fromTo(n, {{ v: 0 }}, {{ v: {int(TXT["land_sqft"])}, duration: {round(max(0.3, c["number"] - cs), 3)}, ease: "power2.out", onUpdate: () => {{ el.textContent = Math.round(n.v).toLocaleString("en-US"); }} }}, {cs}); }})();',
          f'tl.to("#luas-num", {{ scale: 1.12, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }}, {c["number"]});',
          f'tl.fromTo("#luas-unit", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c["unit"]});']
    if dims:
        js.append(f'tl.fromTo("#luas-dim", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c.get("dims", c["number"] + 0.3)});')
    return h, js

def b_side(c):
    n = int(TXT.get("cars", 4)); cars = "".join(f"<span>{'🚗' if i % 2 == 0 else '🚙'}</span>" for i in range(n))
    h = f'''        <div class="shade-top"></div>
        <div id="side-a" class="cx t-stroke">{E(TXT.get("side_line1", "Bahagian tepi"))}<br /><span class="y">{E(TXT.get("side_line2", "MEMANG LUAS"))}</span></div>
        <div id="side-b" class="cx t-stroke">{n} KERETA</div>
        <div id="cars-row">{cars}</div>'''
    for i in range(n):
        sfx("pop", c["cars"] + i * 0.2)
    return h, [f'tl.fromTo("#side-a", {{ y: -80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["title"]});',
               f'tl.fromTo("#side-b", {{ scale: 2.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "power4.out" }}, {c["cars"]});',
               f'gsap.utils.toArray("#cars-row span").forEach((el, i) => tl.fromTo(el, {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 0, duration: 0.25, ease: "{BACK}" }}, {c["cars"]} + i * 0.2));']

def b_uses(c):
    items = "\n".join(f'          <div class="item"><span class="e">{E(e)}</span>{E(t)}</div>' for e, t in TXT["uses"])
    h = f'''        <div id="gc-title" class="cx t-stroke">{E(TXT.get("uses_line1", "Ruang tepi ni"))}<br /><span class="y">{E(TXT.get("uses_line2", "BOLEH JADI…"))}</span></div>
        <div id="gc-list">
{items}
        </div>'''
    js = [f'tl.fromTo("#gc-title", {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }}, {c["start"]});']
    for i, t in enumerate(c["items"]):
        sfx("tick", t, 0.7)
        js.append(f'tl.fromTo("#gc-list .item:nth-child({i + 1})", {{ x: {-900 if i % 2 == 0 else 900}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {round(t - 0.1, 3)});')
    return h, js

def b_ready(c):
    h = f'''        <div class="shade-top"></div>
        <div id="ready-a" class="cx"><span class="pill g">{E(TXT.get("ready_pill", "✅ RUMAH DAH SIAP"))}</span></div>
        <div id="ready-b" class="cx t-stroke">{E(TXT.get("ready_line1", "Boleh terus"))} <span class="y">{E(TXT.get("ready_line2", "MASUK!"))}</span></div>'''
    sfx("pop", c["pill"])
    return h, [f'tl.fromTo("#ready-a", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["pill"]});',
               f'tl.fromTo("#ready-b", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c.get("line", c["pill"] + 0.4)});']

def b_price(c):
    old = f'<div id="spa">{E(TXT["price_old"])}<div id="spa-strike"></div></div>' if TXT.get("price_old") else ""
    bonus = f'\n        <div id="bonus" class="cx"><span class="tag">{E(TXT["bonus"])}</span></div>' if TXT.get("bonus") else ""
    dp = (f'\n        <div id="dp" class="cx t-stroke y">{E(TXT["dp_big"])}</div>\n        <div id="dp-sub" class="cx t-stroke">{E(TXT.get("dp_small", ""))}</div>'
          if TXT.get("dp_big") else "")
    h = f'''{dp}
        <div id="price-card">
          {old}
          <div id="net-label">{E(TXT.get("price_label", "HARGA BERSIH"))}</div>
          <div id="net">{E(TXT["price"])}</div>
          <div id="fine">{E(TXT.get("fine_print", ""))}</div>
        </div>{bonus}
        <div id="cta" class="cx"><span class="pill">{E(TXT["cta"])}</span></div>'''
    js = []
    if dp:
        sfx("pop", c["dp"] + 0.05, 0.6)
        js += [f'tl.fromTo("#dp", {{ scale: 2.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.28, ease: "power4.out" }}, {c["dp"]});',
               f'tl.fromTo("#dp-sub", {{ y: 50, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c["dp"] + 0.2});']
    js.append(f'tl.fromTo("#price-card", {{ y: 1100 }}, {{ y: 0, duration: 0.45, ease: "power4.out" }}, {c["card"]});')
    if old:
        sfx("tick", c["card"] + 0.5, 0.8)
        js.append(f'tl.fromTo("#spa-strike", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, {c["card"] + 0.5});')
    sfx("impact", c["price"], 0.75); sfx("ding", c["price"] + 0.05, 0.65); sfx("pop", c["cta_pulse"], 0.6)
    js += [f'tl.fromTo("#net", {{ scale: 2.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }}, {c["price"]});',
           f'tl.to("#net", {{ scale: 1.06, duration: 0.45, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {c["price"] + 0.4});',
           f'tl.fromTo("#cta", {{ y: 120, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["cta"]});',
           f'tl.to("#cta", {{ scale: 1.06, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {c["cta_pulse"]});']
    if bonus:
        js.append(f'tl.fromTo("#bonus", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c.get("bonus", c["price"] + 1.2)});')
    return h, js

def b_text(c, i=[0]):
    """Free-form headline + optional pill: {"block":"text","line":"...","pill":"..."}"""
    i[0] += 1; k = i[0]; g = c["_g"]
    pill = f'\n        <div id="tx{k}-p" class="cx" style="top:{g.get("top", 330) + 160}px"><span class="pill y">{E(g["pill"])}</span></div>' if g.get("pill") else ""
    h = f'''        <div class="shade-top"></div>
        <div id="tx{k}" class="cx t-stroke" style="top:{g.get("top", 330)}px;font-weight:900;font-size:{g.get("size", 92)}px">{E(g["line"])}</div>{pill}'''
    sfx("pop", c["start"])
    js = [f'tl.fromTo("#tx{k}", {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }}, {c["start"]});']
    if pill:
        js.append(f'tl.fromTo("#tx{k}-p", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c.get("pill", c["start"] + 0.35)});')
    return h, js

def b_cta(c):
    """Closing card for listings without a price: title, ✅ checklist, CTA pill."""
    checks = "\n".join(f'          <div class="check"><span class="bx">✓</span>{E(t)}</div>' for t in TXT["cta_checks"])
    h = f'''        <div id="cta-title" class="cx t-stroke">{E(TXT.get("cta_title", ""))}</div>
        <div id="cta-list">
{checks}
        </div>
        <div id="cta" class="cx"><span class="pill">{E(TXT["cta"])}</span></div>''' + (
        f'\n        <div id="cta-phone" class="cx">📞 {E(CFG["phone"])}</div>' if CFG.get("phone") else "")
    js = [f'tl.fromTo("#cta-title", {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }}, {c["start"]});']
    for i in range(len(TXT["cta_checks"])):
        t = round(c.get("checks", c["start"] + 0.3) + i * c["_g"].get("check_gap", 0.35), 3)
        sfx("tick", t, 0.7)
        js.append(f'tl.fromTo("#cta-list .check:nth-child({i + 1})", {{ x: -900, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {t});')
    sfx("pop", c["cta"], 0.6)
    if CFG.get("phone"):
        js.append(f'tl.fromTo("#cta-phone", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["cta"] + 0.3});')
    js += [f'tl.fromTo("#cta", {{ y: 120, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["cta"]});',
           f'tl.to("#cta", {{ scale: 1.06, duration: 0.3, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {c["cta"] + 0.4});']
    return h, js

def b_titlecard(c):
    """Opening title card: small top line, giant Anton name, white pill, italic script line, optional corner text."""
    g = c["_g"]; T2 = {**TXT, **g}
    big = "".join(f'<span class="tcl">{E(x)}</span>' for x in T2["tc_big"].split("\n"))
    size = g.get("tc_size", 250)
    pill_top = int(740 + (T2["tc_big"].count("\n") + 1) * size * 0.95 + 40)   # sit just under the big title
    h = f'''        <div class="shade-top"></div>
        <div id="tc-top" class="cx">{E(T2.get("tc_top", ""))}</div>
        <div id="tc-big" class="cx" style="font-size:{size}px">{big}<div id="tc-shine"></div></div>
        <div id="tc-pill" class="cx" style="top:{pill_top}px"><span>{E(T2.get("tc_pill", ""))}</span></div>
        <div id="tc-script" class="cx" style="top:{pill_top + 105}px;font-size:{g.get("tc_script_size", 74)}px">{E(T2.get("tc_script", ""))}</div>''' + (
        f'\n        <div id="tc-corner">{E(T2["tc_corner"])}</div>' if T2.get("tc_corner") else "")
    a = c["start"]
    sfx("impact", a + 0.05, 0.7); sfx("pop", c.get("pill", a + 0.55), 0.5)
    js = [f'tl.fromTo("#tc-top", {{ y: -40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {a + 0.05});',
          f'gsap.utils.toArray("#tc-big .tcl").forEach((el, i) => tl.fromTo(el, {{ y: 120, scale: 1.5, rotation: i % 2 ? 4 : -4, opacity: 0 }}, {{ y: 0, scale: 1, rotation: 0, opacity: 1, duration: 0.45, ease: "back.out(2)" }}, {a + 0.1} + i * 0.22));',
          f'tl.fromTo("#tc-shine", {{ xPercent: -120 }}, {{ xPercent: 120, duration: 0.9, ease: "power2.inOut" }}, {a + 1.0});',
          f'tl.fromTo("#tc-pill", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "{BACK}" }}, {c.get("pill", a + 0.55)});',
          f'tl.fromTo("#tc-script", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power2.out" }}, {c.get("script", a + 0.8)});',
          f'tl.to("#tc-big", {{ scale: 1.03, duration: 1.2, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {a + 0.6});']
    if T2.get("tc_corner"):
        js.append(f'tl.fromTo("#tc-corner", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {a + 0.3});')
    return h, js

def b_nearby(c):
    """Location card: title + rows [emoji, place, distance/time], each row on its cue (cues.items list)."""
    g = c["_g"]
    rows = "\n".join(f'          <div class="nb-row"><span class="nb-e">{E(e)}</span><span class="nb-p">{E(p)}</span><span class="nb-t">{E(t)}</span></div>'
                     for e, p, t in g["items"])
    h = f'''        <div class="shade-top"></div>
        <div id="nb-title" class="cx t-stroke">{E(g.get("title", "📍 NEARBY"))}</div>
        <div id="nb-list">
{rows}
        </div>'''
    js = [f'tl.fromTo("#nb-title", {{ y: -50, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "{BACK}" }}, {c["start"] + 0.1});']
    for i, t in enumerate(c.get("items", [c["start"] + 0.4 + 0.4 * k for k in range(len(g["items"]))])):
        sfx("tick", t, 0.7)
        js.append(f'tl.fromTo("#nb-list .nb-row:nth-child({i + 1})", {{ x: {-900 if i % 2 == 0 else 900}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {round(t - 0.1, 3)});')
    return h, js

BLOCKS = dict(nearby=b_nearby, titlecard=b_titlecard, cta=b_cta, hook=b_hook, location=b_location, rooms=b_rooms, land=b_land, side=b_side, uses=b_uses,
              ready=b_ready, price=b_price, text=b_text)

G_HTML, G_JS = [], []
for gi, g in enumerate(CFG["graphics"]):
    sc = g.get("scene")
    a = ref(g["from"]) if "from" in g else SCENE_T[sc][0]
    b = ref(g["to"]) if "to" in g else SCENE_T[sc][1]
    c = {"start": a, "end": b, "_g": g}
    if g["block"] not in BLOCKS:
        raise SystemExit(f'config error: unknown block "{g["block"]}" (have: {", ".join(BLOCKS)})')
    for k, v in g.get("cues", {}).items():
        c[k] = [ref(x) for x in v] if isinstance(v, list) else ref(v)
    body, js = BLOCKS[g["block"]](c)
    G_HTML.append(f'      <div id="g{gi}-{g["block"]}" class="clip" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="1">\n{body}\n      </div>')
    G_JS.append(f"// {g['block']}\n      " + "\n      ".join(js))

# ---------------- persistent phone number (top-right, whole film) ----------------
if CFG.get("phone"):
    G_HTML.append(f'      <div id="phone-mark" class="clip" data-start="0" data-duration="{D}" data-track-index="2">'
                  f'<div id="phone">{E(CFG["phone"])}</div></div>')
    G_JS.append('// phone\n      tl.fromTo("#phone", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0.2);')

# ---------------- captions ----------------
CAP_HTML, CAP_JS, chunks = [], [], []
if CFG.get("captions", True):
    def split(ph):
        ends = [i + 1 for i, w in enumerate(ph[:-1]) if w["w"][-1] in ".?!" and not w["w"].endswith("...")]   # one sentence per caption
        if ends:
            k = min(ends, key=lambda i: abs(i - len(ph) / 2))
            return split(ph[:k]) + split(ph[k:])
        if len(ph) <= 6:
            return [ph]
        for marks in (",;",):                  # then commas, then halves
            cut = [i + 1 for i, w in enumerate(ph[:-1]) if w["w"][-1] in marks and 2 <= i + 1 <= len(ph) - 2]
            if cut:
                k = min(cut, key=lambda i: abs(i - len(ph) / 2))
                return split(ph[:k]) + split(ph[k:])
        conj = [i for i, w in enumerate(ph) if 2 <= i <= len(ph) - 2 and norm(w["w"]) in
                ("and", "with", "but", "or", "dan", "atau", "untuk", "sehingga", "hingga")]
        if conj:                               # then just before a conjunction
            k = min(conj, key=lambda i: abs(i - len(ph) / 2))
            return split(ph[:k]) + split(ph[k:])
        h = (len(ph) + 1) // 2
        return [ph[:h], ph[h:]]
    chunks = split([w for seg in TX for w in seg["_words"]])   # whole script, split by sentence/comma/length
    i = 0
    while i < len(chunks) - 1:                                  # fold one-word chunks ("Hey!") into the next
        if len(chunks[i]) == 1 and len(chunks[i]) + len(chunks[i + 1]) <= 7:
            chunks[i:i + 2] = [chunks[i] + chunks[i + 1]]
        else:
            i += 1
    for ci, ch in enumerate(chunks):
        a = T(ch[0]["s"]); b = T(chunks[ci + 1][0]["s"]) if ci + 1 < len(chunks) else D
        CAP_HTML.append(f'        <div class="cap" id="cap{ci}"><span class="cap-in">' + " ".join(
            f'<span class="cw" id="cw{ci}_{k}">{E(w["w"])}</span>' for k, w in enumerate(ch)) + "</span></div>")
        CAP_JS.append(f'tl.set("#cap{ci}", {{ autoAlpha: 1 }}, {a}).set("#cap{ci}", {{ autoAlpha: 0 }}, {b});'
                      f' tl.fromTo("#cap{ci}", {{ scale: 0.85 }}, {{ scale: 1, duration: 0.15, ease: "back.out(3)" }}, {a});')
        for k, w in enumerate(ch):
            if CFG.get("caption_highlight", True):
                CAP_JS.append(f'tl.set("#cw{ci}_{k}", {{ color: "#ffd400" }}, {T(w["s"])}).set("#cw{ci}_{k}", {{ color: "#ffffff" }}, {T(w["e"]) + 0.05});')

# ---------------- write ----------------
DUR = {"impact": 0.9, "pop": 0.12, "whoosh": 0.6, "tick": 0.06, "riser": 1.2, "ding": 1.2}
SFX_HTML = "\n".join(f'      <audio id="sfx{i:02d}" src="assets/sfx/{k}.wav" data-start="{max(0, round(t, 3))}" data-duration="{DUR[k]}" '
                     f'data-volume="{v}" data-track-index="{4 + i % 4}"></audio>'
                     for i, (k, t, v) in enumerate(sorted(SFX, key=lambda x: x[1])))
out = (ROOT / "index.tpl").read_text()
for k, v in dict(THEME=" ".join("theme-" + t for t in CFG.get("theme", "bold").split()), D=D, SCENES="\n".join(SC_HTML), GRAPHICS="\n\n".join(G_HTML), CAPS="\n".join(CAP_HTML), VO=VO, SFX=SFX_HTML,
                 BED_VOL=CFG.get("music_volume", 0.15), CUTS=json.dumps([] if SLIDE else starts[1:]), KB="\n      ".join(KB),
                 GJS="\n\n      ".join(G_JS), CAPJS="\n      ".join(CAP_JS)).items():
    out = out.replace("{{" + k + "}}", str(v))
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
(ROOT / "index.html").write_text(out)

print(f"index.html written — {D}s, {len(CUTS)} pauses tightened ({sum(b - a for a, b in CUTS):.2f}s saved)")
for s in scenes:
    a, b = SCENE_T[s["id"]]
    print(f"  {a:6.2f}-{b:6.2f}  {s['id']:10s} {s['src']}")
