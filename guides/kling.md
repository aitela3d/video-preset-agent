# Kling 4.0 (Kuaishou) — prompt guide

Version: Kling 4.0 (global launch Oct 2026) and 4.0 Flash (3-20 s, 720p). Stereo audio, lip sync.
3-30 s (default 10 s), 720p / 1080p / 4K, 21:9, 16:9, 1:1, 9:16, Auto; up to 15 references, 10 keyframes.

## Strengths
- Scenes, environments, products, vehicles, nature: physics, texture, lighting.
- Stable large-scale motion and complex camera moves; text stays readable through camera moves.
- Multi-shot and timed beats; edits keep everything you ask it to preserve.

## Weaknesses
- Abstract words ("premium look", "vintage feel") are ignored: describe light, materials, composition.
- Short prompts are auto-expanded with invented story and camera moves: be specific to stay in control.
- Hands in extreme close-up and day -> night jumps in one clip fail (3.0 sources, unverified for 4.0).

## Prompt structure (order)
Start with one sentence: subject, scene, action, emotion. Then add only details that matter:
camera, timing, lighting, audio. Core order: Subject + Action + Scene + Camera + Lighting + Mood.
Multi-shot is on by default (the model cuts on its own): for one clip write "one continuous shot, no cuts".
Timed beats: "0-3 seconds: ...", "Shot 1 (5s): ...", "Cut to ...". Full template for complex clips:
[Asset roles] -> [Overall settings: scene, texture, visual style, camera tone] -> [Timed events] -> [Audio].
Dialogue in quotes, with the speaker's tone and speed. Negatives: no separate field, they raise errors;
only two are needed: "no subtitles", "no background music".

## Ideal length
Max 8,000 tokens, but longer is not better. 50-100 words for a single shot (unverified).

## Camera vocabulary
Shot size: extreme close-up, close-up, medium close-up, full body, wide / establishing.
Moves: push-in, pull-out, pull back, pan, tilt up, tracking shot, orbit / arc, whip pan, handheld,
static / locked camera. Pace: slow, steady, quick. Lens: "24mm wide", "85mm". Never "cinematic movement".

## What to avoid
- More than one main action per beat; vague spatial language (causes morphing).
- Lists of visual negatives ("no blur, no flicker"): describe the wanted result instead.
- Abstract quality words; restating the start image in image-to-video (identity drift).

## Example prompts
1. A matte black wireless speaker rests on a wet slate rock beside a mountain stream at dawn; water droplets
   bead on its fabric and slowly run down. One continuous shot, no cuts: close-up, slow push-in, then rack
   focus from the droplets to the top grille. Soft blue morning light with warm rim light from the left,
   calm mood. Sound: running water, light birdsong. No background music.
2. An empty desert highway at golden hour, heat haze over the asphalt. 0-4 seconds: wide shot, locked
   camera, a red vintage convertible enters from the right. 4-8 seconds: tracking shot alongside the car at
   wheel level, dust trailing behind. Warm low sun, long shadows, quiet open mood. No subtitles.

## From my testing
- Kling: best for scenes without people in close-up.
- My consistency approach: background first, then the character on that background, then video.

## What changed vs Kling 3.0
Same core formula (subject, action, scene, camera, light, mood). New: clips up to 30 s, 8,000-token input,
multi-shot on by default (say "one continuous shot" for a single clip), stereo dialogue in quotes.
Main change: no "Negative:" line any more; the official guide says negatives raise errors, except
"no subtitles" and "no background music".

## Sources
- Kling, Kling 4.0 User Guide (Nov 2026): https://kling.ai/quickstart/kling-4-model-user-guide
- Krea, Kling 4.0 prompt guide: https://www.krea.ai/models/kling-4/prompt-guide
- Kling blog, Kling AI Prompt Guide (3.0 era): https://kling.ai/blog/kling-ai-prompt-guide
