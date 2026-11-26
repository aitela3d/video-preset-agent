# Video Preset Agent — project rules

Answer me (the user) in Russian. Code, UI text, prompts and README: English.

## Goal
A small, reliable demo for a Prompt Engineer job interview at a generative video company.
The agent turns a one-line idea into a model-specific, reusable video preset and critiques its own output.
Audience: a non-technical recruiter (must be clear in 60 seconds) and later a technical interviewer (must be explainable and honest).
Do not use any company name in the repo name, UI or branding.

## Hard constraints
- Python 3 standard library only (http.server, urllib, json, threading). No pip installs. If something is truly impossible without a dependency, stop and ask me first.
- One command to run: `python3 app.py`, then open http://localhost:8000.
- Code budget: about 700 lines total (Python + HTML/CSS/JS), excluding guides/, runs/ and README. Hard cap 1000. Simple over clever.
- LLM access only via OpenRouter. Key from env var OPENROUTER_API_KEY or a local .env file (in .gitignore). Never print, log or commit the key.
- Model ID in one config constant. Pick a cheap, fast model with reliable JSON output: check current models and prices on OpenRouter before choosing and tell me why. Budget for all development and testing: $1.5. Show estimated cost per run.
- Every LLM call: max_tokens cap, timeout, one retry, JSON validation, clear error message if it still fails.

## Agent design (keep these names, I must explain them in the interview)
Pattern: routing + evaluator-optimizer loop (Anthropic, "Building effective agents").
1. Planner: parse the idea into preset fields: subject, action (exactly one main action), shot size, camera motion, environment, lighting, style, duration, aspect ratio.
2. Router: choose the target model from guides/ (Seedance / Kling / Wan) with a one-sentence reason. The user can override (Auto or a specific model).
3. Writer: write the final prompt following the chosen model's guide, plus a reusable template with a {subject} slot (the "one-click preset" version).
4. Critic: separate call, temperature 0. Sees only the prompt, the guide and the rubric, not the writer's reasoning. Returns JSON: score 1-10 per rubric item, issues (rubric item, problem, concrete fix, breaks a guide rule yes/no). Code computes total (average) and verdict. From round 2 the critic also gets its previous round's issues and answers resolved yes/no for each. Caps enforced by code: a guide-rule violation or an unresolved previous issue = that item at most 6.
5. Loop: code decides from the scores. Revise if any item < 7 or average < 8. Max 3 rounds. Stop early if the average did not improve vs the previous round. The final result is the best-scoring version, not the last one.
6. Critic calibration: tests/critic_calibration.py runs 3 known-bad prompts (vague words; two actions; camera contradiction) and 2 good ones. Bad must score < 7 (on the relevant item or average), good >= 8.

Critic rubric: one clear action per clip; explicit shot size and camera motion; concrete subject (no vague adjectives); lighting and mood stated; follows the model guide (length, syntax, things to avoid); no contradictions; motion physically plausible within the duration.

## Model guides (guides/seedance.md, kling.md, wan.md)
- Use the current model versions available on popular video platforms; check on the web.
- Each file 60 lines max: strengths, weaknesses, prompt structure, ideal length, camera vocabulary, what to avoid, 2 example prompts.
- Research current official prompting guides first (web search). Sources with links at the bottom. Mark anything uncertain as "unverified".
- Each guide has a section "From my testing" with these rules from me. Do not change them:
  - Seedance: best for realistic people.
  - Kling: best for scenes without people in close-up.
  - Wan: cheap open-source option, weaker quality.
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
