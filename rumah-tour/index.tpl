<!doctype html>
<!-- Source template (index.tpl): edit it, then run `python3 build.py` to regenerate index.html -->
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); font-weight: 800; }
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); font-weight: 900; }
      @font-face { font-family: "Emoji"; src: url("assets/fonts/noto-color-emoji-emoji-400-normal.woff2") format("woff2"); }
      :root { --ground: #0d0d0d; --ink: #ffffff; --accent: #ffd400; --green: #0f8a4c; --red: #e0242b; --deep: #10233f; --font-display: "Mont", "Emoji", sans-serif; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: var(--font-display); color: var(--ink); }
      .clip { position: absolute; inset: 0; }
      video.clip, img.clip { width: 1080px; height: 1920px; object-fit: cover; }
      .bg-blur { filter: blur(18px) brightness(0.55); }
      .shade-top { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 40%); }
      .shade-bot { position: absolute; inset: 0; background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 30%); }
      .t-stroke { text-shadow: 0 6px 0 rgba(0,0,0,.35), 0 0 24px rgba(0,0,0,.55); -webkit-text-stroke: 3px #000; paint-order: stroke fill; }
      .cx { position: absolute; left: 40px; right: 40px; text-align: center; }
      .y { color: var(--accent); }
      .pill { display: inline-block; background: #000; color: #fff; padding: 18px 34px; border-radius: 22px; font-weight: 900; font-size: 58px; white-space: nowrap; }
      .pill.y { background: var(--accent); color: #000; }
      .pill.g { background: var(--green); color: #fff; }
      .tag { display: inline-block; padding: 14px 30px; border-radius: 999px; font-weight: 900; font-size: 44px; white-space: nowrap; }

      /* captions */
      #captions { pointer-events: none; }
      .cap { position: absolute; left: 50px; right: 50px; top: 1560px; text-align: center; font-weight: 900; font-size: 64px; line-height: 1.15; visibility: hidden;
             text-shadow: 0 5px 0 rgba(0,0,0,.45), 0 0 18px rgba(0,0,0,.6); -webkit-text-stroke: 3px #000; paint-order: stroke fill; }
      .cw { color: #fff; }

      /* hook */
      #hook-a { top: 330px; font-weight: 900; font-size: 80px; }
      #hook-a .tag { background: var(--accent); color: #000; font-size: 76px; padding: 16px 40px; }
      #hook-b { top: 500px; font-weight: 900; font-size: 116px; line-height: 1.02; }

      /* location */
      #loc { position: absolute; left: 60px; right: 60px; top: 1120px; }
      #loc .card { background: rgba(255,255,255,.96); color: #111; border-radius: 34px; padding: 30px 40px; box-shadow: 0 20px 50px rgba(0,0,0,.35); }
      #loc .l1 { font-weight: 900; font-size: 70px; }
      #loc .l2 { font-weight: 800; font-size: 44px; color: #333; margin-top: 4px; }
      #loc .l3 { font-weight: 600; font-size: 34px; color: #555; margin-top: 6px; }
      #loc-chip { margin-top: 20px; }
      #loc-chip .tag { background: var(--green); color: #fff; }

      /* rooms */
      #bilik-num { top: 300px; font-weight: 900; font-size: 280px; line-height: 1; }
      #bilik-word { top: 590px; font-weight: 900; font-size: 92px; }
      #bilikair { top: 760px; }

      /* land size */
      #best { top: 300px; }
      #luas-num { top: 520px; font-weight: 900; font-size: 230px; line-height: 1; letter-spacing: -0.04em; }
      #luas-unit { top: 770px; font-weight: 900; font-size: 84px; }
      #luas-dim { top: 920px; }

      /* side */
      #side-a { top: 300px; font-weight: 900; font-size: 92px; line-height: 1.05; }
      #side-b { top: 560px; font-weight: 900; font-size: 140px; }
      #cars-row { position: absolute; top: 760px; left: 0; right: 0; display: flex; justify-content: center; gap: 26px; }
      #cars-row span { font-size: 130px; display: inline-block; }

      /* game changer list */
      #gc-title { top: 300px; font-weight: 900; font-size: 84px; line-height: 1.08; }
      #gc-list { position: absolute; top: 620px; left: 110px; right: 110px; display: flex; flex-direction: column; gap: 36px; }
      .item { background: rgba(255,255,255,.95); color: #111; border-radius: 28px; padding: 30px 36px; font-weight: 800; font-size: 60px; display: flex; align-items: center; gap: 24px; white-space: nowrap; }
      .item .e { font-size: 68px; }

      /* ready */
      #ready-a { top: 330px; }
      #ready-b { top: 470px; font-weight: 900; font-size: 84px; }

      /* price */
      #dp { top: 220px; font-weight: 900; font-size: 120px; line-height: 1; }
      #dp-sub { top: 360px; font-weight: 900; font-size: 64px; }
      #price-card { position: absolute; top: 560px; left: 70px; right: 70px; background: #fff; color: #111; border-radius: 40px; padding: 46px 50px 40px; text-align: center; box-shadow: 0 30px 70px rgba(0,0,0,.45); }
      #spa { white-space: nowrap; font-weight: 800; font-size: 54px; color: #666; position: relative; display: inline-block; }
      #spa-strike { position: absolute; left: -10px; right: -10px; top: 50%; height: 8px; background: var(--red); transform-origin: left center; border-radius: 4px; }
      #net-label { margin-top: 24px; font-weight: 900; font-size: 46px; letter-spacing: .1em; color: var(--deep); }
      #net { white-space: nowrap; font-weight: 900; font-size: 132px; line-height: 1; color: var(--red); letter-spacing: -0.04em; }
      #fine { margin-top: 22px; font-weight: 600; font-size: 30px; color: #555; }
      #bonus { top: 1060px; }
      #bonus .tag { background: var(--green); color: #fff; font-size: 42px; }
      #cta { top: 1250px; }
      #cta .pill { font-size: 48px; background: #0f8a4c; color: #fff; }
      #flash { background: #fff; opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{D}}" data-width="1080" data-height="1920">

      <!-- ===== VIDEO TRACK (timed from voiceover words) ===== -->
{{SCENES}}

      <!-- ===== GRAPHICS ===== -->
      <div id="g-hook" class="clip" {{HOOK}} data-track-index="1">
        <div class="shade-top"></div>
        <div id="hook-a" class="cx"><span class="tag">RUMAH CORNER LOT</span></div>
        <div id="hook-b" class="cx t-stroke">TANAH TEPI<br /><span class="y">LUAS GILER</span> 🤯</div>
      </div>

      <div id="g-loc" class="clip" {{LOC}} data-track-index="1">
        <div id="loc">
          <div class="card">
            <div class="l1">📍 Lombong Besi 2</div>
            <div class="l2">Seksyen 29, Shah Alam</div>
            <div class="l3">Single Storey Terrace • Corner No.1</div>
          </div>
          <div id="loc-chip"><span class="tag">🌳 Tanah Rezab Melayu</span></div>
        </div>
      </div>

      <div id="g-bed" class="clip" {{BED}} data-track-index="1">
        <div class="shade-top"></div>
        <div id="bilik-num" class="cx t-stroke y">3</div>
        <div id="bilik-word" class="cx t-stroke">BILIK TIDUR 🛏️</div>
        <div id="bilikair" class="cx"><span class="pill y">+ 2 BILIK AIR 🚿</span></div>
      </div>

      <div id="g-land" class="clip" {{LAND}} data-track-index="1">
        <div class="shade-top"></div>
        <div id="best" class="cx"><span class="pill">YANG PALING BEST 🔥</span></div>
        <div id="luas-num" class="cx t-stroke y">0</div>
        <div id="luas-unit" class="cx t-stroke">KAKI PERSEGI</div>
        <div id="luas-dim" class="cx"><span class="tag" style="background:#fff;color:#111">43' ~ 64' x 68'</span></div>
      </div>

      <div id="g-side" class="clip" {{SIDE}} data-track-index="1">
        <div class="shade-top"></div>
        <div id="side-a" class="cx t-stroke">Bahagian tepi<br /><span class="y">MEMANG LUAS</span></div>
        <div id="side-b" class="cx t-stroke">4 KERETA</div>
        <div id="cars-row"><span>🚗</span><span>🚙</span><span>🚗</span><span>🚙</span></div>
      </div>

      <div id="g-gc" class="clip" {{GC}} data-track-index="1">
        <div id="gc-title" class="cx t-stroke">Ruang tepi ni<br /><span class="y">BOLEH JADI…</span></div>
        <div id="gc-list">
          <div class="item"><span class="e">🌳</span>Mini garden</div>
          <div class="item"><span class="e">🚲</span>Tempat anak bermain</div>
          <div class="item"><span class="e">☕️</span>Ruang santai</div>
        </div>
      </div>

      <div id="g-ready" class="clip" {{READY}} data-track-index="1">
        <div class="shade-top"></div>
        <div id="ready-a" class="cx"><span class="pill g">✅ RUMAH DAH SIAP</span></div>
        <div id="ready-b" class="cx t-stroke">Boleh terus <span class="y">MASUK!</span></div>
      </div>

      <div id="g-price" class="clip" {{PRICE}} data-track-index="1">
        <div id="dp" class="cx t-stroke y">0%</div>
        <div id="dp-sub" class="cx t-stroke">DOWNPAYMENT</div>
        <div id="price-card">
          <div id="spa">Harga SPA: RM 665,431<div id="spa-strike"></div></div>
          <div id="net-label">HARGA BERSIH</div>
          <div id="net">RM 598,888</div>
          <div id="fine">*Loan Agreement to be borne by purchaser</div>
        </div>
        <div id="bonus" class="cx"><span class="tag">🎁 FREE SPA Legal Fees &amp; MOT</span></div>
        <div id="cta" class="cx"><span class="pill">📲 WhatsApp Gina untuk viewing!</span></div>
      </div>

      <!-- ===== CAPTIONS (word-synced to voiceover) ===== -->
      <div id="captions" class="clip" data-start="0" data-duration="{{D}}" data-track-index="2">
{{CAPS}}
      </div>

      <div id="flash" class="clip" data-start="0" data-duration="{{D}}" data-track-index="2"></div>

      <!-- ===== VOICEOVER (pauses tightened) ===== -->
{{VO}}

      <!-- ===== MUSIC BED ===== -->
      <audio id="bed" src="assets/sfx/bed.m4a" data-start="0" data-duration="{{D}}" data-media-start="0" data-volume="0.15" data-fade-out="1.2" data-track-index="3"></audio>

      <!-- ===== SFX ===== -->
{{SFX}}
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const back = "back.out(2.2)";
      const K = {{K}};
      tl.set("#flash", { opacity: 0 }, 0);
      {{CUTS}}.forEach((t) => {
        tl.to("#flash", { opacity: 0.5, duration: 0.05, ease: "none" }, t - 0.05).to("#flash", { opacity: 0, duration: 0.18, ease: "power2.out" }, t);
      });
      const kb = (sel, a, b, s0, s1) => tl.fromTo(sel, { scale: s0 }, { scale: s1, duration: b - a, ease: "none" }, a);
      const span = (sel) => { const el = document.querySelector(sel); const a = +el.dataset.start; return [a, a + +el.dataset.duration]; };

      // Ken Burns on every shot
      kb("#v-hook", ...span("#v-hook"), 1.25, 1.05);
      kb("#v-front", ...span("#v-front"), 1.12, 1.0);
      kb("#v-hall", ...span("#v-hall"), 1.0, 1.12);
      kb("#v-bed", ...span("#v-bed"), 1.0, 1.1);
      kb("#v-room", ...span("#v-room"), 1.08, 1.0);
      kb("#v-bath", ...span("#v-bath"), 1.12, 1.0);
      kb("#i-land", ...span("#i-land"), 1.0, 1.15);
      kb("#v-side", ...span("#v-side"), 1.0, 1.12);
      kb("#i-gc", ...span("#i-gc"), 1.12, 1.22);
      kb("#v-ready", ...span("#v-ready"), 1.1, 1.0);
      kb("#i-price", ...span("#i-price"), 1.12, 1.3);

      // HOOK — synced to "corner lot" / "tanah tepi"
      tl.fromTo("#hook-a", { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: back }, K.corner);
      tl.fromTo("#hook-b", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: back }, K.tanah);
      tl.to("#hook-b", { scale: 1.05, duration: 0.15, yoyo: true, repeat: 3, ease: "sine.inOut" }, K.tanah + 0.4);

      // LOCATION — "Lombong Besi 2, seksyen 29 Shah Alam"
      tl.fromTo("#loc .card", { x: -1100 }, { x: 0, duration: 0.45, ease: "power4.out" }, K.lombong - 0.2);
      tl.fromTo("#loc-chip", { scale: 0, opacity: 0, transformOrigin: "left center" }, { scale: 1, opacity: 1, duration: 0.35, ease: back }, K.seksyen);

      // ROOMS — "3 bilik tidur dan 2 bilik air"
      tl.fromTo("#bilik-num", { scale: 3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.out" }, K.tiga);
      tl.fromTo("#bilik-word", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: back }, K.tiga + 0.25);
      tl.fromTo("#bilikair", { x: 900, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "power4.out" }, K.dua);

      // LAND SIZE — counter lands on "4,102", unit on "kaki persegi"
      tl.fromTo("#best", { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: back }, K.best);
      const n = { v: 0 }, numEl = document.querySelector("#luas-num");
      tl.fromTo("#luas-num", { opacity: 0 }, { opacity: 1, duration: 0.15 }, K.best + 0.8);
      tl.fromTo(n, { v: 0 }, { v: 4102, duration: K.luas_n - (K.best + 0.8), ease: "power2.out",
        onUpdate: () => { numEl.textContent = Math.round(n.v).toLocaleString("en-US"); } }, K.best + 0.8);
      tl.to("#luas-num", { scale: 1.12, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }, K.luas_n);
      tl.fromTo("#luas-unit", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: back }, K.kaki);
      tl.fromTo("#luas-dim", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: back }, K.luas_n + 0.3);

      // SIDE — "Bahagian tepi ... memang luas. Nak parking 4 kereta"
      tl.fromTo("#side-a", { y: -80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: back }, K.bahagian);
      tl.fromTo("#side-b", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.out" }, K.empat);
      gsap.utils.toArray("#cars-row span").forEach((el, i) => {
        tl.fromTo(el, { scale: 0, rotation: -25 }, { scale: 1, rotation: 0, duration: 0.25, ease: back }, K.empat + i * 0.2);
      });

      // USES — each item on its spoken word
      tl.fromTo("#gc-title", { scale: 1.8, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }, span("#g-gc")[0]);
      [K.mini, K.tempat, K.ruang].forEach((t, i) => {
        tl.fromTo(`#gc-list .item:nth-child(${i + 1})`, { x: i % 2 ? 900 : -900, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }, t - 0.1);
      });

      // READY — "Rumah dah siap, boleh terus masuk"
      tl.fromTo("#ready-a", { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: back }, K.siap + 0.05);
      tl.fromTo("#ready-b", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: back }, K.siap + 0.4);

      // PRICE — "Downpayment 0%, harga bersih hanya RM598,888"
      tl.fromTo("#dp", { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "power4.out" }, K.dp);
      tl.fromTo("#dp-sub", { y: 50, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: back }, K.dp + 0.2);
      tl.fromTo("#price-card", { y: 1100 }, { y: 0, duration: 0.45, ease: "power4.out" }, K.harga - 0.1);
      tl.fromTo("#spa-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, K.harga + 0.4);
      tl.fromTo("#net", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }, K.rm);
      tl.to("#net", { scale: 1.06, duration: 0.45, yoyo: true, repeat: 5, ease: "sine.inOut" }, K.rm + 0.4);
      tl.fromTo("#bonus", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: back }, K.rm + 1.2);
      tl.fromTo("#cta", { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: back }, K.berminat);
      tl.to("#cta", { scale: 1.06, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut" }, K.whatsapp);

      // CAPTIONS
      gsap.set(".cap", { autoAlpha: 0 });
      {{CAPJS}}

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
