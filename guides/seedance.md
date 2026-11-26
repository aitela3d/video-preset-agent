# Seedance 2.5 (ByteDance) — prompt guide

Version: Seedance 2.5 ("Dreamina Seedance 2.5"), plus a faster 2.5 flash. Released July 2026 (date unverified).
Up to 30 s per generation, 720p / 1080p, any aspect ratio from 0.4 to 2.5 (9:16, 1:1, 16:9, 21:9).
Native audio (dialogue, sound effects) in 10+ languages. References: 30 images, 10 videos, 10 audio clips.

## Strengths
- Realistic people: faces, skin, natural body motion, believable performance.
- Reference control: subject references (1-5 subjects), storyboards, keyframes, video edit and extension.
- Multi-shot with integer-second timestamps; dialogue with lip sync.

## Weaknesses
- Emotion words about the eyes can produce glowing eyes; style may drift compared with 2.0.
- Multi-subject scenes swap characters; text is misspelled; unrequested subtitles or BGM may appear.

## Prompt structure (order)
1. One-sentence summary: Subject + Location + Event + Genre/Style + Camera movement.
2. Detailed plot: shot sequence or timeline ("Shot 1 ...", or timestamps).
3. Additional notes: camera, environment, lighting, sound, atmosphere.
For a single 5-10 s shot, the summary sentence plus 2-3 short detail sentences is enough.
Timestamps: integer seconds, no gaps: "0-3 seconds: ...", "3-7 seconds: ...", or "At the 2-second mark, ...".
Dialogue: Name says: {line} (exact syntax unverified). Keep actions general, avoid idioms.
Negatives work only for subtitles and audio: "No subtitles.", "No BGM." Describe visuals positively instead.

## Ideal length
No official length. 40-90 words for a single shot works well (unverified).

## Camera vocabulary
Shot size: extreme wide, wide, medium, medium close-up, close-up.
Moves: push in, pull out, pan, track, follow, orbit, dive, tilt up, handheld shake, locked-off.
Angles: low angle, overhead, first-person. Techniques: long take, dolly zoom, aerial, FPV, bullet time,
speed ramp, rack focus (explain niche terms in plain words). Tie each camera move to an event.
Transitions: give time and method ("At the 5-second mark, hard cut to ...").

## What to avoid
- More than one main action, or fast repeated motions, in a short clip.
- Eye-focused emotion phrases ("eyes burning with anger"): describe the face and posture instead.
- Vague praise words (beautiful, epic, cinematic); exact on-screen text.
- Visual negatives ("no blur", "no distorted hands"): only subtitle and audio negatives are supported.

## Example prompts
1. A woman in her 30s with short curly hair and a grey wool coat stands at a rainy tram stop at dusk and
   slowly looks up at the sky. Medium close-up, the camera pushes in as she looks up. Cool blue streetlight
   with warm shop-window rim light, quiet reflective mood, realistic 35mm film look. Sound: rain on
   pavement, distant tram bell. No subtitles. No BGM.
2. An elderly fisherman with a white beard and a yellow oilskin coat coils a rope on a wooden pier at
   sunrise. 0-5 seconds: wide shot, locked-off camera. 5-10 seconds: close-up of his hands tying a knot,
   camera slowly orbits left. Golden low sun, sea mist, calm mood. Sound: gulls, creaking wood. No subtitles.

## From my testing
- Seedance: best for realistic people.
- My consistency approach: background first, then the character on that background, then video.

## What changed vs the previous guide
Same model version. The guide now follows ByteDance's official text instead of third-party summaries:
visual "Avoid:" lines are dropped (only subtitle/audio negatives work), timestamps must be whole seconds,
and the order starts with one summary sentence. Vs 2.0: timestamps now work, aspect ratio is free.

## Sources
- ByteDance, Dreamina Seedance 2.5 series prompt guide (BytePlus ModelArk): https://ai.byteplus.com/ark/region:ap-southeast-1/docs/seedance-2-5-prompt-guide
