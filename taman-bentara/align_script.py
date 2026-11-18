"""Replace whisper's words with the known script (correct spelling), keeping whisper's timings.
Usage: python3 align_script.py <display_script.txt>   (rewrites transcript.json)"""
import difflib, json, re, sys
disp = open(sys.argv[1]).read().split()
tx = json.load(open("transcript.json"))
flat = []
for si, seg in enumerate(tx):
    for w in seg["words"]:
        t = w["w"].strip()
        if flat and (re.match(r"^[,.]\d", t) or re.match(r"^-\w", t)):
            flat[-1]["w"] += t; flat[-1]["e"] = w["e"]
        else:
            flat.append({"w": t, "s": w["s"], "e": w["e"], "seg": si})
n = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
sm = difflib.SequenceMatcher(None, [n(w["w"]) for w in flat], [n(x) for x in disp], autojunk=False)
out = []
for op, a0, a1, b0, b1 in sm.get_opcodes():
    if op == "delete":
        continue
    if a1 - a0 == b1 - b0:   # equal / same-length replace: keep each word's own timing
        for j in range(a1 - a0):
            w = flat[a0 + j]
            out.append({"w": " " + disp[b0 + j], "s": w["s"], "e": w["e"], "seg": w["seg"]})
        continue
    src = flat[a0:a1] if a1 > a0 else [flat[max(0, a0 - 1)]]
    s, e, seg = src[0]["s"], src[-1]["e"], src[0]["seg"]
    k = b1 - b0
    for j in range(k):   # spread the script words over the matched whisper span
        out.append({"w": " " + disp[b0 + j], "s": round(s + (e - s) * j / k, 3), "e": round(s + (e - s) * (j + 1) / k, 3), "seg": seg})
segs = []
for w in out:
    if not segs or segs[-1]["_i"] != w["seg"]:
        segs.append({"_i": w["seg"], "file": tx[0]["file"], "words": []})
    segs[-1]["words"].append({"w": w["w"], "s": w["s"], "e": w["e"]})
for sg in segs:
    sg["start"], sg["end"] = sg["words"][0]["s"], sg["words"][-1]["e"]
    sg["text"] = "".join(w["w"] for w in sg["words"]); del sg["_i"]
json.dump(segs, open("transcript.json", "w"), ensure_ascii=False, indent=1)
for sg in segs: print(f'[{sg["start"]:6.2f}]{sg["text"]}')
