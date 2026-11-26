# Kling 3.0 (Kuaishou) — prompt guide

Version: Kling VIDEO 3.0 / 3.0 Omni (O3) — current on kling.ai and major API platforms (2026).
Kling 4.0 (3-30 s, 720p/1080p/4K, 21:9 16:9 1:1 9:16) is described by Krea from Kling's Oct 2026 guide;
availability outside Krea is unverified. Rules below apply to both.

## Strengths
- Scenes, environments, products, vehicles, nature: strong physics, texture and lighting.
- Precise camera language; multi-shot within one prompt; native audio.
- Readable on-screen text if you give exact words, placement and surface.

## Weaknesses
- Abstract adjectives ("premium", "vintage") are ignored or misread.
- Vague spatial language causes morphing; hands in extreme close-up deform.
- Big state jumps (day -> night) in one clip fail; open-ended motion with no end state stalls.

## Prompt structure (order)
Subject + Action (subject movement) + Scene + Camera + Lighting + Mood (official Kling blog).
Multi-shot: "[Shot 1: Wide shot] ... [Shot 2: Medium shot] ..." — set the scene first, then shots in order.
Timed beats also work: "0-4s: ...", "4-10s: ..."; one action per beat, repeat the subject description.
Image-to-video: describe only motion and camera, never restate what the image shows.

## Ideal length
60-100 words for text-to-video (Atlas Cloud); 15-40 words for image-to-video (VEED).
API cap 2,500 characters per prompt and per negative prompt (unverified; Kling 4.0 allows more).

## Camera vocabulary
Shot size: extreme close-up, close-up, medium close-up, full body, wide / establishing.
Moves: push-in, pull back, pan, tilt, tracking (side / behind), orbit / 180-degree arc, crane, aerial,
rack focus, locked / static camera, long take with no cuts. Add pace: slow, steady, quick.
Angles: low angle, high angle, overhead. Avoid "cinematic movement" or "nice angle" — name the move.

## What to avoid
- More than 3 sequential actions in one clip; more than ~7 distinct elements.
- Negative phrasing inside the prompt (can backfire); use the negative field for blur, warped hands, flicker.
  Exceptions that work inline: "no subtitles", "no background music".
- Restating the start image (identity drift); mixing keyframes and Omni references in one task.
- Possible content-filter triggers ("shirtless", "touching") — unverified.

## Example prompts
1. A matte black wireless speaker rests on a wet slate rock beside a mountain stream at dawn. Water droplets
   bead on its fabric and slowly run down. Close-up, slow push-in, then rack focus from the droplets to the
   logo-free top grille. Soft blue morning light with warm rim light from the left. Calm, premium-quiet mood.
   Negative: blur, flicker, text.
2. [Shot 1: Wide shot] An empty desert highway at golden hour, heat haze over the asphalt, a red vintage
   convertible enters from the right. Locked camera. [Shot 2: Tracking shot] Camera tracks alongside the car
   at wheel level, dust trailing behind. Warm low sun, long shadows, quiet open mood.

## From my testing
- Kling: best for scenes without people in close-up.
- My consistency approach: background first, then the character on that background, then video.

## Sources
- Kling official blog, Kling AI Prompt Guide (Aug 2026): https://kling.ai/blog/kling-ai-prompt-guide
- Krea, Kling 4.0 prompt guide (Nov 2026): https://www.krea.ai/models/kling-4/prompt-guide
- Atlas Cloud, Kling AI Video Prompt Guide (Jul 2026): https://www.atlascloud.ai/blog/guides/kling-ai-video-prompt-guide
- VEED, Kling AI Prompts guide: https://www.veed.io/learn/kling-ai-prompting-guide
