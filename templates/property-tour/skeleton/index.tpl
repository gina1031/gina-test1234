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
