# Video Preset Agent — project rules

Answer me (the user) in Russian. Code, UI text, prompts and README: English.

## Goal
Portfolio demo: a small agent that writes model-specific video prompts and critiques them. Must be clear in 60 seconds and honest about its limits.
Do not use any company name in the repo name, UI or branding.

## Hard constraints
- Python 3 standard library only (http.server, urllib, json, threading). No pip installs. If something is truly impossible without a dependency, stop and ask me first.
- One command to run: `python3 app.py`, then open http://localhost:8000.
- Code budget: about 700 lines total (Python + HTML/CSS/JS), excluding guides/, runs/ and README. Hard cap 1000. Simple over clever.
- LLM access only via OpenRouter. Key from env var OPENROUTER_API_KEY or a local .env file (in .gitignore). Never print, log or commit the key.
- Model ID in one config constant. Pick a cheap, fast model with reliable JSON output: check current models and prices on OpenRouter before choosing and tell me why. Budget for all development and testing: $1.5. Show estimated cost per run.
- Every LLM call: max_tokens cap, timeout, one retry, JSON validation, clear error message if it still fails.

## Agent design (keep these names)
Pattern: routing + evaluator-optimizer loop (Anthropic, "Building effective agents").
1. Planner: parse the idea into preset fields: subject, action (one motion arc from start to end state, with counts; keep every beat of the idea), shot size, camera motion (one simple move), environment, lighting (+ mood), style (one short look), duration, aspect ratio.
2. Router: choose the target model from guides/ (Seedance / Kling / Wan) with a one-sentence reason. Quality is close, so it decides by features the idea needs (dialogue, 4K, 21:9, references, cost), with a soft default when nothing decides. The user can override (Auto or a specific model).
3. Writer: write the final prompt following the chosen model's guide, plus a reusable template with a {subject} slot (the "one-click preset" version). Write simply: plain short sentences, full motion arc first, one camera move, no stacked effects; fast body motion under 60 words.
4. Critic: separate call, temperature 0. Sees only the user's idea, the prompt, the guide and the rubric, not the writer's reasoning. Code also gives it the word count and the effect terms found. Returns JSON: score 1-10 per rubric item, issues (rubric item, problem, concrete fix, breaks a guide rule yes/no). Code computes total (average) and verdict. From round 2 the critic also gets its previous round's issues and answers resolved yes/no for each. Caps enforced by code: a guide-rule violation or an unresolved previous issue = that item at most 6.
5. Loop: code decides from the scores. Revise if any item < 7 or average < 8. Max 3 rounds. Stop early if the average did not improve vs the previous round. The final result is the best-scoring version, not the last one.
6. Critic calibration: tests/critic_calibration.py runs 4 known-bad prompts (vague words; two actions; camera contradiction; a real overloaded prompt that failed on a real generation) and 3 good ones. Bad must score < 7 on a target item, good must pass (average >= 8, all items >= 7).

Critic rubric: faithful to the idea (no beat dropped); one clear motion arc with start and end state; explicit shot size and one simple camera move; concrete subject (no vague adjectives); lighting and mood stated; follows the model guide (length, syntax, things to avoid); no contradictions; motion physically plausible within the duration; simple and clear (no stacked effects, fewer demands for fast motion).
Lesson from a real generation test: a 10/10 critic score is not video quality. Scores must be checked against real generations.

## Model guides (guides/seedance.md, kling.md, wan.md)
- Use the current model versions available on popular video platforms; check on the web.
- Current versions (updated 27 Nov 2026): Seedance 2.5, Kling 4.0, Wan 3.0.
- Each file 60 lines max: strengths, weaknesses, prompt structure, ideal length, camera vocabulary, what to avoid, 2 example prompts.
- Research current official prompting guides first (web search). Sources with links at the bottom. Mark anything uncertain as "unverified".
- Each guide has a section "From my testing" with these rules from me. Do not change them without asking me (last updated together on 27 Nov 2026):
  - Seedance 2.5: good for realistic people, on par with Kling 4.0 and Wan 3.0 prime; 2.5 flash is a bit weaker.
  - Kling 4.0: as good as Seedance for people, also strong for scenes, products and nature; 4.0 Flash is a bit weaker.
  - Wan 3.0 prime: as good as Seedance and Kling for people, usually the cheapest; lighter versions are a bit weaker. (API-only; open weights end at Wan 2.2.)
  - On these models a plain one-line idea often works as well as an engineered prompt for simple single shots.
  - My consistency approach: background first, then the character on that background, then video.

## UI (single static/index.html, no frameworks, no external CDNs)
- Input: idea (one line) + model selector (Auto / Seedance / Kling / Wan) + Run button.
- Live step timeline streamed from the server (SSE): Planner -> Router (model + reason) -> Writer -> Critic (score + top issues) -> Revise ... -> Final.
- Final card: target model, final prompt (copy button), reusable template (copy button), first score vs final score, rounds, time, cost.
- "Raw idea vs final prompt" side by side.
- Every run saved to runs/<timestamp>.json. A "Replay" dropdown plays saved runs step by step without calling the API, so the demo works even offline.
- Clean, minimal, dark theme, large readable text for screen sharing.

## Workflow
- Stages: 1) research and write guides/ -> 2) agent core + CLI test (`python3 agent.py "idea"`) on 3 different ideas -> 3) server + UI -> 4) README + 5 saved demo runs.
- Stop for my check after stage 1 and after stage 2 (show me the 3 outputs with scores). Stages 3-4 without stopping.
- Demo runs in stage 4: a person close-up, a product shot, a landscape without people, an action scene, food. At least one must show the critic forcing a revision.
- Run the code yourself after each change. Never say "done" before a real end-to-end run worked.
- Do not rewrite working files without a reason. Keep your messages short.
- At the end: git init, .gitignore (.env), first commit. I push to GitHub myself.

## README.md (English, for GitHub)
What it does (2 sentences); placeholder for a 60-second demo video; architecture diagram (mermaid); how to run; one example (raw idea -> final prompt -> scores); cost and latency per run; limitations (LLM-as-judge bias, guides can go stale, scores are not ground truth); next steps (keyframe image step, vision QA of generated frames, A/B tests with real generations).
Honest framing: a prototype built in a day to learn agent design. No claims of production use.
