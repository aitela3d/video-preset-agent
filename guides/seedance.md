# Seedance 2.5 (ByteDance) — prompt guide

Version: Seedance 2.5, released July 2026 (Kapwing; date unverified). Also sold as "Dreamina Seedance 2.5".
Up to 30 s per generation, native synchronized audio, up to 50 references (30 img / 10 video / 10 audio).
Aspect ratios seen in examples: 16:9, 9:16 (full list and resolutions unverified).

## Strengths
- Realistic people: faces, skin, natural body motion, believable performance.
- Multi-shot continuity in one generation; native dialogue, SFX and ambience.
- Strong reference control when each reference has a stated role.

## Weaknesses
- Too many micro-events in a short window -> jitter, fragmented motion.
- Timing is not frame-accurate; on-screen text and subtitles are unreliable.
- Identity drifts after occlusion or re-entry unless the subject is re-anchored.

## Prompt structure (order)
Subject + Action + Scene/Environment + Visual style + Camera + Audio (official order, via Higgsfield).
Only subject and action are mandatory; everything else sharpens the result.
For clips > ~10 s use timed beats: "0-5s: ...", "5-10s: ..." (each beat one action, one camera move).
For a single 5-10 s shot: one paragraph, no timestamps.
Audio can be a separate line: "SFX: ...", "AMBIENCE: ...", "MUSIC: none".
No dedicated negative-prompt field (Kapwing, unverified): put a short "Avoid: ..." line at the end.

## Ideal length
40-90 words for a single shot (unverified; inferred from official examples).
Longer structured prompts only for multi-beat clips. Every word should be visible or audible.

## Camera vocabulary
Shot size: extreme wide, wide, medium, close-up, extreme close-up.
Moves: push in, pull out, pan, tilt up, lateral move, follow shot, orbit, dolly out, handheld, locked-off.
Angles: low angle, overhead, first-person. Special: one-take, dolly zoom, aerial, FPV, whip-pan.
Tie each move to an event ("pushes in as she looks up"). One move per beat.
Turn optical terms into visible changes ("focus shifts from the cup to her face").

## What to avoid
- Several actions in one short clip; describing only start and end state (model invents the middle).
- Vague adjectives ("beautiful", "epic") instead of concrete materials, light and motion.
- Exact text on screen; many dialogue lines in a short shot (they overlap).
- Contradictions between camera and action (e.g. "static camera" + "orbit").

## Example prompts
1. A woman in her 30s with short curly hair and a grey wool coat stands at a rainy tram stop at dusk,
   slowly lowers her umbrella and looks up at the sky. Medium close-up, camera pushes in slowly as she
   looks up. Cool blue streetlight with warm shop-window rim light, soft rain. Realistic, 35mm film look.
   AMBIENCE: rain on pavement, distant tram bell. Avoid: text, logos.
2. 0-5s: Wide shot, an elderly fisherman with a white beard and yellow oilskin coils a rope on a wooden pier
   at sunrise, locked-off camera. 5-10s: Close-up, he ties a knot and smiles, camera slowly orbits left.
   Golden low sun, sea mist. Documentary realism. SFX: gulls, creaking wood.

## From my testing
- Seedance: best for realistic people.
- My consistency approach: background first, then the character on that background, then video.

## Sources
- Higgsfield, Seedance 2.5 Prompt Guide (copy of ByteDance's official guide): https://higgsfield.ai/enterprise-help-center/platform/seedance-prompt-guides
- Kapwing, How to Prompt Seedance 2.5 (Aug 2026): https://www.kapwing.com/resources/how-to-prompt-seedance-2-5-a-guide-for-ai-video-creators/
- BytePlus ModelArk docs (older Seedance 1.0 guide): https://docs.byteplus.com/docs/ModelArk/1631633
