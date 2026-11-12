# Template: Property Tour (Reels / TikTok, 1080×1920)

Template video tour rumah yang disync dengan voiceover, dibina dengan [HyperFrames](https://hyperframes.heygen.com).
Contoh siap: `rumah-tour/` (Lombong Besi 2) → `rumah-tour/renders/lombong-besi-2_final.mp4`.

**Isi template:**

- Hook kuat di 0 saat.
- Graphic yang keluar tepat pada perkataan yang disebut dalam voiceover.
- Caption ikut perkataan (perkataan yang sedang disebut jadi kuning).
- Sound FX dan music bed (synthesize sendiri, tak perlu download).
- Pause panjang dalam voiceover dibuang automatik.

## Susunan block graphic

| Block | Apa yang keluar | Cue (perkataan pencetus) |
|---|---|---|
| `hook` | Tag + 2 baris besar + emoji | `tag`, `line` |
| `location` | Kad 📍 lokasi, kawasan, jenis rumah + chip | `chip` |
| `rooms` | Nombor bilik tidur besar + pill bilik air | `bed`, `bath` |
| `land` | Counter keluasan tanah 0 → N + unit + ukuran | `number`, `unit`, `dims` |
| `side` | Tajuk ruang tepi + "N KERETA" + kereta pop | `title`, `cars` |
| `uses` | Senarai kegunaan, satu-satu | `items` (list) |
| `ready` | ✅ pill + baris "boleh terus masuk" | `pill`, `line` |
| `price` | 0% DP, kad harga (SPA dipotong, harga bersih), bonus, CTA | `dp`, `card`, `price`, `bonus`, `cta`, `cta_pulse` |
| `text` | Headline bebas + pill (block tambahan) | `pill` |

Block yang tak perlu boleh dibuang dari `graphics`. Teks yang kosong (contohnya `bonus`, `price_old`, `location_chip`) tak akan dipaparkan.

## Cara guna (listing baru)

```bash
# 1. Cipta projek (music bed + SFX dijana automatik)
templates/property-tour/new_project.sh rumah-baru /path/voiceover.mp3

# 2. Sediakan klip: HDR→SDR, portrait 1080x1920, buang audio b-roll
templates/property-tour/tools/prep_clips.sh rumah-baru /path/klip*.mp4
SLOW=2 templates/property-tour/tools/prep_clips.sh rumah-baru /path/klip_tanah.mp4   # slow-mo bila footage pendek
#    Still untuk scene grafik:  ffmpeg -ss 1.0 -i rumah-baru/assets/clips/X.mp4 -frames:v 1 rumah-baru/assets/stills/X.jpg

# 3. Transcribe voiceover (perlukan pip install faster-whisper + akses huggingface.co)
HF_HUB_DISABLE_XET=1 python3 -I templates/property-tour/tools/transcribe.py rumah-baru rumah-baru/assets/vo/voiceover.m4a medium ms

# 4. Edit rumah-baru/config.json: text, scenes, graphics (cue ikut perkataan dalam transcript)
# 5. Build + check + preview
cd rumah-baru && python3 build.py && npx hyperframes check && npx hyperframes preview --background
# 6. Render (SDR!)
npx hyperframes render -q delivery --sdr -o renders/final.mp4
```

## Rujukan masa dalam `config.json`

| Tulis | Maksud |
|---|---|
| `0`, `2.5` | saat dalam video |
| `"w:tanah"` | bila perkataan pertama "tanah" mula disebut |
| `"w:rumah#3-0.65"` | 0.65s sebelum "rumah" yang ke-3 |
| `"s:hall.end+0.2"` | 0.2s selepas scene `hall` tamat (`.start` / `.end`) |
| `"end"` | hujung video |

- **Scene** bermula pada `from`, dan tamat bila scene seterusnya bermula.
- `kind`:
  - `video` (default)
  - `img` (still dengan Ken Burns)
  - `blur` (still yang dikaburkan, untuk background graphic)
- `kb: [mula, akhir]` ialah zoom Ken Burns.
- `media_start` ialah titik mula dalam klip (saat).
- `build.py` akan beritahu kalau klip terlalu pendek untuk scene, atau kalau perkataan cue tak jumpa dalam transcript (dia senaraikan semua perkataan yang ada).

## Tips

- **Pembetulan ejaan transcript:** `fix_words` (contoh `{"Syah": "Shah"}`).
- **Kawal pause:** `pause_max` / `pause_keep`. Pause lebih panjang dari `pause_max` dipendekkan ke `pause_keep`.
- **Render guna `--sdr`:** footage phone Samsung/iPhone selalu HDR (HLG), dan nampak pudar kalau keluar HDR di IG/TikTok.
- **Ubah gaya:** warna/font semua dalam `:root` dan CSS di `index.tpl`.
