<!doctype html>
<!-- Property-tour template. Edit config.json (and styles here), then run `python3 build.py` to regenerate index.html -->
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); font-weight: 800; }
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); font-weight: 900; }
      @font-face { font-family: "Mont"; src: url("assets/fonts/montserrat-latin-700-normal.woff2") format("woff2"); font-weight: 700; }
      @font-face { font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "Play"; src: url("assets/fonts/playfair-display-latin-600-italic.woff2") format("woff2"); font-style: italic; font-weight: 600; }
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
      /* cta block (no price) */
      #cta-title { top: 300px; font-weight: 900; font-size: 84px; line-height: 1.08; }
      #cta-list { position: absolute; top: 560px; left: 70px; right: 70px; }
      .check { white-space: nowrap; font-weight: 900; font-size: 54px; margin-bottom: 40px; background: rgba(0,0,0,.55); padding: 26px 30px; border-radius: 28px; display: flex; gap: 20px; align-items: center; }
      .check .bx { background: var(--green); width: 74px; height: 74px; border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 50px; flex: none; }
      #flash { background: #fff; opacity: 0; }

      /* ===== titlecard block (any theme) ===== */
      #tc-top { top: 660px; font-weight: 700; font-size: 54px; text-shadow: 0 3px 10px rgba(0,0,0,.7); }
      #tc-big { top: 740px; font-family: "Anton", sans-serif; font-size: 250px; line-height: 0.95; color: #ffd60a; text-transform: uppercase;
                -webkit-text-stroke: 5px #111; paint-order: stroke fill; text-shadow: 0 10px 0 rgba(0,0,0,.35), 0 0 40px rgba(0,0,0,.35); }
      #tc-pill { top: 1230px; }
      #tc-pill span { display: inline-block; background: #fff; color: #111; font-weight: 700; font-size: 52px; padding: 10px 34px; border-radius: 14px; }
      #tc-script { top: 1335px; font-family: "Play", serif; font-style: italic; font-weight: 600; font-size: 74px; text-shadow: 0 3px 12px rgba(0,0,0,.75); }
      #tc-corner { position: absolute; top: 380px; right: 70px; font-family: "Play", serif; font-style: italic; font-size: 52px; text-shadow: 0 2px 8px rgba(0,0,0,.6); }

      /* ===== phone number (config "phone") ===== */
      #phone-mark { pointer-events: none; }
      #phone { position: absolute; top: 205px; right: 60px; font-family: "Play", serif; font-style: italic; font-weight: 600; font-size: 50px;
               color: #fff; letter-spacing: 0.02em; text-shadow: 0 2px 4px rgba(0,0,0,.95), 0 0 14px rgba(0,0,0,.8), 0 0 28px rgba(0,0,0,.5); }
      #cta-phone { top: 1370px; font-weight: 800; font-size: 56px; text-shadow: 0 3px 10px rgba(0,0,0,.8); }

      /* ===== theme add-on: luxe (use "theme": "clean luxe") — dark, serif italic, gold ===== */
      .theme-luxe .t-stroke, .theme-luxe #tc-big { font-family: "Play", serif !important; font-style: italic; font-weight: 600; text-transform: none;
                               letter-spacing: 0; -webkit-text-stroke: 0; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,.7); }
      .theme-luxe #tc-big { color: #f3d27a !important; line-height: 1.02; }
      .theme-luxe .y { color: #f3d27a; }
      .theme-luxe .pill, .theme-luxe .pill.y, .theme-luxe .pill.g, .theme-luxe .tag, .theme-luxe #tc-pill span {
               background: rgba(12,16,28,.72) !important; color: #f3d27a !important; border: 2px solid #d4af37; border-radius: 999px; font-weight: 700; }
      .theme-luxe #cta .pill { background: #d4af37 !important; color: #0c101c !important; }
      .theme-luxe .check, .theme-luxe .nb-row, .theme-luxe .item { background: rgba(12,16,28,.8) !important; color: #fff !important; border: 1.5px solid rgba(212,175,55,.6); }
      .theme-luxe .check .bx { background: #d4af37 !important; color: #0c101c !important; }
      .theme-luxe .nb-t { background: #d4af37; color: #0c101c; }
      .theme-luxe .shade-top { background: linear-gradient(180deg, rgba(5,8,16,.65) 0%, rgba(5,8,16,0) 45%); }
      .theme-luxe #flash { background: #f3d27a; }

      /* ===== theme add-on: promo (use "theme": "clean promo") — red/yellow sale style ===== */
      .theme-promo .t-stroke { display: inline-block; left: 50%; right: auto; transform-origin: center; translate: -50% 0; background: #e11d2e; color: #fff;
                               padding: 6px 30px; border-radius: 10px; -webkit-text-stroke: 0; text-shadow: none; box-shadow: 0 8px 0 #8f0f1b; }
      .theme-promo #bilik-num, .theme-promo #luas-num { background: none; box-shadow: none; color: #ffd60a; -webkit-text-stroke: 6px #e11d2e; }
      .theme-promo #tc-big { color: #ffd60a; -webkit-text-stroke: 7px #e11d2e; text-shadow: 0 12px 0 #8f0f1b; }
      .theme-promo .pill, .theme-promo .pill.y, .theme-promo .pill.g, .theme-promo .tag, .theme-promo #tc-pill span {
               background: #ffd60a !important; color: #111 !important; border: 4px solid #111; border-radius: 12px; font-weight: 900; rotate: -3deg; display: inline-block; }
      .theme-promo #cta .pill { background: #e11d2e !important; color: #fff !important; border-color: #fff; }
      .theme-promo .cap-in { background: #ffd60a; color: #111; padding: 2px 14px; border-radius: 6px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
      .theme-promo .cap .cw { color: #111; }
      .theme-promo .cap { -webkit-text-stroke: 0; text-shadow: none; line-height: 1.35; }
      .theme-promo #captions { background: none; }
      .theme-promo .check .bx, .theme-promo .nb-t { background: #e11d2e !important; color: #fff !important; }

      /* ===== theme add-on: card (use "theme": "clean card") — modern boxed labels, green accent ===== */
      .theme-card .t-stroke { display: inline-block; left: 50%; right: auto; translate: -50% 0; background: rgba(17,17,17,.78); color: #fff;
                              font-family: "Mont", "Emoji", sans-serif; font-weight: 800; text-transform: none; letter-spacing: -0.01em;
                              padding: 12px 34px; border-radius: 26px; -webkit-text-stroke: 0; text-shadow: none; }
      .theme-card #bilik-num, .theme-card #luas-num { color: #22c55e; }
      .theme-card .y { color: #4ade80; }
      .theme-card #tc-big { font-family: "Mont", sans-serif; font-weight: 900; color: #fff; -webkit-text-stroke: 0; text-transform: none;
                            letter-spacing: -0.04em; text-shadow: 0 6px 24px rgba(0,0,0,.6); }
      .theme-card .pill, .theme-card .pill.y, .theme-card .pill.g, .theme-card .tag, .theme-card #tc-pill span {
               background: #22c55e !important; color: #fff !important; border-radius: 999px; font-weight: 800; }
      .theme-card .cap { -webkit-text-stroke: 0; text-shadow: none; }
      .theme-card .cap-in { background: #fff; color: #111; padding: 4px 16px; border-radius: 10px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
      .theme-card .cap .cw { color: #111; }
      .theme-card #captions { background: none; }
      .theme-card .check .bx, .theme-card .nb-t { background: #22c55e !important; color: #fff !important; }

      /* ===== nearby block ===== */
      #nb-title { top: 300px; font-weight: 900; font-size: 84px; }
      #nb-list { position: absolute; top: 470px; left: 70px; right: 70px; display: flex; flex-direction: column; gap: 26px; }
      .nb-row { display: flex; align-items: center; gap: 22px; background: rgba(255,255,255,.95); color: #111; border-radius: 22px; padding: 22px 30px; }
      .nb-e { font-size: 56px; }
      .nb-p { flex: 1; font-weight: 800; font-size: 46px; line-height: 1.1; }
      .nb-t { font-weight: 900; font-size: 40px; background: #111; color: #ffd60a; border-radius: 12px; padding: 8px 16px; white-space: nowrap; }

      /* ===== theme: clean (TikTok-style: plain white captions, Anton headings, white pills) ===== */
      .theme-clean .cap { top: 1500px; font-weight: 700; font-size: 54px; -webkit-text-stroke: 2px rgba(0,0,0,.55); paint-order: stroke fill;
                          text-shadow: 0 2px 4px rgba(0,0,0,.9), 0 0 18px rgba(0,0,0,.7); }
      .theme-clean #captions { background: linear-gradient(0deg, rgba(0,0,0,0) 6%, rgba(0,0,0,.42) 14%, rgba(0,0,0,.42) 20%, rgba(0,0,0,0) 26%); }
      .theme-clean #luas-num { font-size: 260px; }
      .theme-clean #luas-unit { top: 830px; }
      .theme-clean #luas-dim { top: 960px; }
      .theme-clean #bilik-num { font-size: 260px; }
      .theme-clean #bilik-word { top: 620px; }
      .theme-clean #bilikair { top: 770px; }
      .theme-clean #cta .pill { background: #ffd60a; color: #111; }
      .theme-clean .t-stroke { font-family: "Anton", "Emoji", sans-serif; font-weight: 400; letter-spacing: 0.01em; text-transform: uppercase;
                               -webkit-text-stroke: 4px #111; text-shadow: 0 8px 0 rgba(0,0,0,.3), 0 0 30px rgba(0,0,0,.35); }
      .theme-clean .y { color: #ffd60a; }
      .theme-clean .pill, .theme-clean .pill.y, .theme-clean .pill.g { background: #fff; color: #111; font-weight: 700; border-radius: 14px; }
      .theme-clean .tag { background: #fff !important; color: #111 !important; border-radius: 14px; font-weight: 700; }
      .theme-clean .shade-top { background: linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 35%); }
      .theme-clean .check { background: rgba(255,255,255,.95); color: #111; }
      .theme-clean .check .bx { background: #111; color: #ffd60a; }
    </style>
  </head>
  <body>
    <div id="root" class="{{THEME}}" data-composition-id="main" data-start="0" data-duration="{{D}}" data-width="1080" data-height="1920">

      <!-- ===== SCENES (cut on voiceover words) ===== -->
{{SCENES}}

      <!-- ===== GRAPHICS ===== -->
{{GRAPHICS}}

      <!-- ===== CAPTIONS (word-synced) ===== -->
      <div id="captions" class="clip" data-start="0" data-duration="{{D}}" data-track-index="2">
{{CAPS}}
      </div>

      <div id="flash" class="clip" data-start="0" data-duration="{{D}}" data-track-index="2"></div>

      <!-- ===== VOICEOVER (long pauses tightened) ===== -->
{{VO}}

      <!-- ===== MUSIC BED ===== -->
      <audio id="bed" src="assets/sfx/bed.m4a" data-start="0" data-duration="{{D}}" data-media-start="0" data-volume="{{BED_VOL}}" data-fade-out="1.2" data-track-index="3"></audio>

      <!-- ===== SFX ===== -->
{{SFX}}
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      tl.set("#flash", { opacity: 0 }, 0);
      {{CUTS}}.forEach((t) => {
        tl.to("#flash", { opacity: 0.5, duration: 0.05, ease: "none" }, t - 0.05).to("#flash", { opacity: 0, duration: 0.18, ease: "power2.out" }, t);
      });

      // Ken Burns on every shot
      {{KB}}

      {{GJS}}

      // captions
      gsap.set(".cap", { autoAlpha: 0 });
      {{CAPJS}}

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
