# Wan 3.0 (Alibaba) — prompt guide

Version: Wan 3.0 (API: wan3.0-video, wan3.0-video-prime), public beta Aug 2026, docs updated Nov 2026.
Hosted API only, weights not published (unverified); the last open-weight flagship is Wan 2.2.
2-30 s (default 5 s), 480p-1080p, 30 fps, 21:9 to 9:16. Native audio on by default; up to 20 references.

## Strengths
- Low price per second, especially at 480p/720p (exact pricing unverified).
- Multi-reference transfer, editing, extension; follows an explicit timed shot list closely.

## Weaknesses
- Little independent testing of quality yet; hands and limbs can deform in motion.
- Fast repeated motions are not controllable; speech or music may be added if you do not say otherwise.

## Prompt structure (official order)
1. Overall description (for one clip, first line: "Generate single shot.")
2. Reference citation: Image N / Video N / Audio N (only with uploads)
3. Shot N [start-end s]: Subject + Scene + Motion + Aesthetic control (light, shot size, angle, lens, camera move)
4. Dialogue: Name says: "..." (write "No dialogue." if there is none)
5. Sound effect / background music ("No background music." to turn it off)
6. Style / Mood (at the start or the end)
7. Negative prompt list: only unwanted items, do not repeat positives
Multi-shot: "Shot 1 [0-3s]: ...", "Shot 2 [3-6s]: ...", no gaps or overlaps, 2-6 s per shot (pages differ).

## Ideal length
No official length; max 20,000 characters. 50-100 words for a single shot (unverified).

## Camera vocabulary
Shot size: close-up, medium close-up, medium shot, full shot, wide shot.
Moves: static / fixed camera, push in, pull back, slow zoom out, orbit, tilt down, handheld follow,
whip pan, FPV. Angles: low, extreme low, overhead. Speed: slow motion, high-speed (1000 fps).
Lens: 24mm wide-angle, 85mm telephoto, shallow or deep focus.

## What to avoid
- Fast repeated motions ("shakes head 3 times per second"); more than one main action per shot.
- Leaving audio unspecified when you want silence: say "No dialogue." / "No background music."
- Photoreal human close-ups as the hero shot (quality limit, see below).

## Example prompts
1. Generate single shot. A small orange fox with a fluffy tail trots through a snowy birch forest at dawn,
   stops and sniffs the air. Medium shot at eye level, slow tracking shot from the side. Soft side light,
   pale pink sky. Sound: crunching snow, light wind. No dialogue. No background music. Style: storybook
   3D animation, cold quiet mood. Negative prompt: extra legs, text.
2. Generate single shot. A steaming bowl of ramen on a dark wooden counter; chopsticks lift noodles slowly
   out of the broth. Close-up, fixed camera, 85mm, shallow focus, steam rising. Warm side light from the left.
   Sound: soft slurp, quiet kitchen hum. No dialogue. Style: realistic food photography, cozy late-night mood.

## From my testing
- Wan: cheap option, weaker quality. (Wan 3.0 is API-only; open weights end at Wan 2.2.)
- My consistency approach: background first, then the character on that background, then video.

## What changed vs Wan 2.2
Big change. The old formula Entity + Scene + Motion + Aesthetic + Style still sits inside each shot, but
3.0 adds a shot list with timestamps, a "Generate single shot." line, native audio that must be specified
(or turned off), and an ordered negative list at the end. Clips grow from ~5 s to 30 s. 3.0 is API-only.

## Sources
- Alibaba Cloud Model Studio, wan3.0 video generation prompt guide: https://help.aliyun.com/en/model-studio/wan3-video-generation-prompt-guide
- Alibaba Cloud Model Studio, wan3.0 video generation guide (Nov 2026): https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-guide
- eWeek, Wan 3.0 launch (Aug 2026): https://eweek.com/news/alibaba-wan3-ai-video-documents-apac-china/
