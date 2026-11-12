#!/usr/bin/env bash
# Synthesize the SFX kit + a soft music bed into <project>/assets/sfx (no downloads needed).
# Usage: tools/make_sfx.sh <project-dir> [bed-seconds=60]
set -euo pipefail
OUT="$1/assets/sfx"; BED="${2:-60}"; mkdir -p "$OUT"; cd "$OUT"
A="-hide_banner -loglevel error -y"
ffmpeg $A -f lavfi -i "anoisesrc=d=0.6:c=pink:a=0.9" -af "highpass=f=300,lowpass=f=4000,volume='sin(PI*t/0.6)^2':eval=frame,afade=t=out:st=0.45:d=0.15,aecho=0.6:0.4:30:0.3,volume=19dB" -ar 48000 -ac 2 whoosh.wav
ffmpeg $A -f lavfi -i "aevalsrc='0.8*sin(2*PI*(900-6000*t)*t)*exp(-38*t)':d=0.12:s=48000" -ac 2 pop.wav
ffmpeg $A -f lavfi -i "aevalsrc='0.9*sin(2*PI*(120-150*t)*t)*exp(-6*t)+0.25*(random(0)-0.5)*exp(-30*t)':d=0.9:s=48000" -af "lowpass=f=1800" -ac 2 impact.wav
ffmpeg $A -f lavfi -i "aevalsrc='0.45*sin(2*PI*1568*t)*exp(-4*t)+0.3*sin(2*PI*2349*t)*exp(-6*t)+0.15*sin(2*PI*3136*t)*exp(-9*t)':d=1.2:s=48000" -ac 2 ding.wav
ffmpeg $A -f lavfi -i "aevalsrc='(0.35*sin(2*PI*(200*t+300*t*t))+0.2*(random(0)-0.5))*(t/1.2)^2':d=1.2:s=48000" -af "highpass=f=150" -ac 2 riser.wav
ffmpeg $A -f lavfi -i "aevalsrc='0.6*sin(2*PI*2200*t)*exp(-90*t)':d=0.06:s=48000" -ac 2 tick.wav
C='if(lt(mod(t,9.6),2.4),A,if(lt(mod(t,9.6),4.8),B,if(lt(mod(t,9.6),7.2),C,D)))'
n() { local s=${C/A/$1}; s=${s/B/$2}; s=${s/C/$3}; s=${s/D/$4}; echo "$s"; }
ffmpeg $A -f lavfi -i "aevalsrc='0.06*(sin(2*PI*$(n 261.6 220 174.6 196)*t)+sin(2*PI*$(n 329.6 261.6 220 246.9)*t)+sin(2*PI*$(n 392 329.6 261.6 293.7)*t)+0.7*sin(2*PI*$(n 493.9 392 329.6 349.2)*t))+0.35*sin(2*PI*(55-40*mod(t,0.6))*mod(t,0.6))*exp(-14*mod(t,0.6))+0.04*(random(0)-0.5)*exp(-40*mod(t+0.3,0.6))':d=$BED:s=48000" \
  -af "lowpass=f=3000,aecho=0.7:0.5:300:0.25,afade=t=in:d=0.5,volume=8dB" -ac 2 -c:a aac -b:a 128k bed.m4a
ls "$OUT"
