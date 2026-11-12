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
        if seg_words and re.match(r"^[,.]\d", t):          # whisper splits "4" ",102"
            seg_words[-1]["w"] += t; seg_words[-1]["e"] = w["e"]
        else:
            seg_words.append({"w": CFG.get("fix_words", {}).get(t, t), "s": w["s"], "e": w["e"]})
    seg["_words"] = seg_words
    words += seg_words

# ---------------- pause tightening ----------------
pmax, pkeep = CFG.get("pause_max", 0.3), CFG.get("pause_keep", 0.1)
CUTS = []
for a, b in zip(words, words[1:]):
    gap = b["s"] - a["e"]
    if gap > pmax:
        CUTS.append((round(a["e"] + pkeep / 2, 3), round(b["s"] - pkeep / 2, 3)))
VO_END = words[-1]["e"] + 0.3


def T(t):
    off = 0.0
    for a, b in CUTS:
        off += (b - a) if t >= b else max(0.0, t - a)
    return round(t - off, 3)


D = round(T(VO_END) + CFG.get("end_hold", 1.3), 2)
norm = lambda s: s.lower().strip(",.?!:;\"'")


def word_t(word, n=1):
    hits = [w for w in words if norm(w["w"]) == norm(word)]
    if len(hits) < n:
        raise SystemExit(f'config error: word "{word}" #{n} not in transcript (found {len(hits)}). '
                         f'Words: {" ".join(norm(w["w"]) for w in words)}')
    return T(hits[n - 1]["s"])


SCENE_T = {}
REF = re.compile(r"^(?:w:(?P<w>[^#+\-]+?)(?:#(?P<n>\d+))?|s:(?P<s>[\w-]+)\.(?P<edge>start|end)|(?P<end>end))(?P<off>[+-]\d*\.?\d+)?$")


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
for s in scenes:
    a, b = SCENE_T[s["id"]]; d = round(b - a, 3); kind = s.get("kind", "video"); sid = "sc-" + s["id"]
    if not (ROOT / s["src"]).exists():
        problems.append(f'scene "{s["id"]}": file not found: {s["src"]}')
    if d <= 0:
        problems.append(f'scene "{s["id"]}" has no length ({a}->{b}); check its "from" against the next scene')
    if kind == "video":
        ms = s.get("media_start", 0); L = media_len(s["src"])
        if L is not None and d > L - ms + 0.02:
            problems.append(f'scene "{s["id"]}" needs {d:.2f}s but {s["src"]} has {L - ms:.2f}s after media_start '
                            f'(use a slow-mo copy, a still, or move the cut)')
        SC_HTML.append(f'      <video id="{sid}" class="clip" src="{s["src"]}" data-start="{a}" data-duration="{d}" '
                       f'data-media-start="{ms}" muted data-track-index="0"></video>')
    else:
        cls = "clip bg-blur" if kind == "blur" else "clip"
        SC_HTML.append(f'      <img id="{sid}" class="{cls}" src="{s["src"]}" data-start="{a}" data-duration="{d}" data-track-index="0" />')
    k0, k1 = s.get("kb", [1.0, 1.1] if kind == "video" else [1.12, 1.25])
    KB.append(f'tl.fromTo("#{sid}", {{ scale: {k0} }}, {{ scale: {k1}, duration: {d}, ease: "none" }}, {a});')
if problems:
    raise SystemExit("\n".join(["Timeline problems:"] + problems))

# ---------------- SFX helper ----------------
SFX = [("impact", 0.0, 0.85)]
if CFG.get("whoosh_on_cuts", True):
    SFX += [("whoosh", max(0, starts[i] - 0.25), 0.7) for i in range(1, len(scenes))]
def sfx(kind, t, v=0.55):
    SFX.append((kind, round(t, 3), v))

E = lambda s: html.escape(str(s))
BACK = 'back.out(2.2)'

# ---------------- graphic blocks ----------------
# Each block: (config) -> (html, [js lines]). `c` holds resolved cue times.
def b_hook(c):
    h = f'''        <div class="shade-top"></div>
        <div id="hook-a" class="cx"><span class="tag">{E(TXT["hook_tag"])}</span></div>
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

BLOCKS = dict(hook=b_hook, location=b_location, rooms=b_rooms, land=b_land, side=b_side, uses=b_uses,
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

# ---------------- captions ----------------
CAP_HTML, CAP_JS, chunks = [], [], []
if CFG.get("captions", True):
    for seg in TX:
        ph = seg["_words"]
        chunks += [ph] if len(ph) <= 6 else [ph[:(len(ph) + 1) // 2], ph[(len(ph) + 1) // 2:]]
    for ci, ch in enumerate(chunks):
        a = T(ch[0]["s"]); b = T(chunks[ci + 1][0]["s"]) if ci + 1 < len(chunks) else D
        CAP_HTML.append(f'        <div class="cap" id="cap{ci}">' + " ".join(
            f'<span class="cw" id="cw{ci}_{k}">{E(w["w"])}</span>' for k, w in enumerate(ch)) + "</div>")
        CAP_JS.append(f'tl.set("#cap{ci}", {{ autoAlpha: 1 }}, {a}).set("#cap{ci}", {{ autoAlpha: 0 }}, {b});'
                      f' tl.fromTo("#cap{ci}", {{ scale: 0.85 }}, {{ scale: 1, duration: 0.15, ease: "back.out(3)" }}, {a});')
        for k, w in enumerate(ch):
            CAP_JS.append(f'tl.set("#cw{ci}_{k}", {{ color: "#ffd400" }}, {T(w["s"])}).set("#cw{ci}_{k}", {{ color: "#ffffff" }}, {T(w["e"]) + 0.05});')

# ---------------- write ----------------
DUR = {"impact": 0.9, "pop": 0.12, "whoosh": 0.6, "tick": 0.06, "riser": 1.2, "ding": 1.2}
SFX_HTML = "\n".join(f'      <audio id="sfx{i:02d}" src="assets/sfx/{k}.wav" data-start="{max(0, round(t, 3))}" data-duration="{DUR[k]}" '
                     f'data-volume="{v}" data-track-index="{4 + i % 4}"></audio>'
                     for i, (k, t, v) in enumerate(sorted(SFX, key=lambda x: x[1])))
out = (ROOT / "index.tpl").read_text()
for k, v in dict(D=D, SCENES="\n".join(SC_HTML), GRAPHICS="\n\n".join(G_HTML), CAPS="\n".join(CAP_HTML), VO=VO, SFX=SFX_HTML,
                 BED_VOL=CFG.get("music_volume", 0.15), CUTS=json.dumps(starts[1:]), KB="\n      ".join(KB),
                 GJS="\n\n      ".join(G_JS), CAPJS="\n      ".join(CAP_JS)).items():
    out = out.replace("{{" + k + "}}", str(v))
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
(ROOT / "index.html").write_text(out)

print(f"index.html written — {D}s, {len(CUTS)} pauses tightened ({sum(b - a for a, b in CUTS):.2f}s saved)")
for s in scenes:
    a, b = SCENE_T[s["id"]]
    print(f"  {a:6.2f}-{b:6.2f}  {s['id']:10s} {s['src']}")
