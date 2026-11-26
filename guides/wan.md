# Wan 2.2 (Alibaba, open weights) — prompt guide

Version: Wan 2.2 (Jul 2025, Apache 2.0) — the latest open-weight flagship, on most video platforms and ComfyUI.
Models: T2V-A14B, I2V-A14B (480p/720p), TI2V-5B (720p @ 24 fps, runs on a 24 GB GPU). Typical clip ~5 s.
Newer Wan 2.5 / 2.6 / 2.7 / 3.0 (3.0 since Aug 2026, up to 30 s, 1080p) are closed, API-only.
The prompt formula below is Alibaba's official one and works for all versions.

## Strengths
- Cheap: open weights, run locally or very low price per second on hosted platforms.
- Good motion and camera following for short single shots; strong stylized looks (anime, 3D, painterly).
- Fine-tunable (LoRA), large community workflows.

## Weaknesses
- Lower detail and realism than Seedance/Kling; faces and hands degrade, especially at 480p.
- No native audio in 2.2. Short clips only; long choreographed action breaks.
- Exact on-screen text and lip sync are unreliable.

## Prompt structure (order)
Basic: Entity + Scene + Motion.
Advanced (recommended): Entity + Scene + Motion + Aesthetic control (light, shot size, angle, lens,
camera move) + Stylization. Cover all five.
Image-to-video: Motion + Camera movement only (the image already gives entity, scene, style).
For one shot on Wan 2.7+, add "Generate single shot."
Open model accepts a negative prompt (artifacts, blur, extra limbs, text) — exact default list unverified.

## Ideal length
50-100 words (unverified; official examples range from one sentence to ~80 words).
Short prompts are often auto-expanded by an LLM ("prompt extend") — write the full version yourself.

## Camera vocabulary
Shot size: close-up, medium close-up, medium shot, full shot, extreme full shot, wide-angle.
Angle: eye-level, low-angle, high-angle, top-down, over-the-shoulder, aerial.
Lens: long-focus, medium focal length, ultra-wide fisheye.
Moves: push in, pull out, pan, tilt up, tracking/follow, orbit, drone shot, fixed camera.
Light: soft, side, rim, backlight, daylight, overcast, firelight. Composition: center, symmetrical.

## What to avoid
- Rapid scene changes or more than one main action in a clip.
- Large orbits (keep arc small; "<45 degrees" is unverified advice).
- Real people by name, exact text on screen, lip sync to exact words.
- Photoreal human close-ups as the hero shot (quality limit) — prefer medium/wide or stylized.

## Example prompts
1. A small orange fox with a fluffy tail trots through a snowy birch forest at dawn, stops and sniffs the air.
   Soft side light, pale pink sky, medium shot at eye level, slow tracking shot following the fox from the side.
   Cold, quiet mood, storybook 3D animation style. Negative: blur, extra legs, text.
2. A steaming bowl of ramen on a dark wooden counter, chopsticks lift noodles slowly out of the broth.
   Warm firelight from the left, close-up, fixed camera, shallow depth of field, steam rising.
   Cozy late-night mood, realistic food photography style.

## From my testing
- Wan: cheap open-source option, weaker quality.
- My consistency approach: background first, then the character on that background, then video.

## Sources
- Wan 2.2 GitHub README: https://github.com/Wan-Video/Wan2.2
- Alibaba Cloud Model Studio, text-to-video prompt guide (Oct 2026): https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt
- Alibaba Cloud blog, Wan 2.6 (Dec 2025): https://www.alibabacloud.com/blog/602742
- eWeek, Wan 3.0 launch (Aug 2026): https://eweek.com/news/alibaba-wan3-ai-video-documents-apac-china/
- Atlas Cloud, Is Wan 3.0 open source? (Aug 2026): https://www.atlascloud.ai/sv/blog/tips/is-wan-3.0-open-source
