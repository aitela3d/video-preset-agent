"""Video Preset Agent: idea -> model-specific video prompt + reusable template, with a self-critique loop.

Pattern: routing + evaluator-optimizer (Anthropic, "Building effective agents").
Planner -> Router -> Writer -> Critic -> (Writer revises -> Critic) ... -> Final
"""
import json, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime

# ---- Config -------------------------------------------------------------------------------
MODEL = "google/gemini-3.5-flash-lite"   # OpenRouter model ID (one place to change it)
PRICE_IN, PRICE_OUT = 0.30, 2.50          # USD per 1M tokens, for the cost estimate
MAX_ROUNDS = 3                            # max write+critique rounds (enforced by code)
PASS_SCORE = 8                            # average needed to pass
MIN_ITEM = 7                              # every rubric item needs at least this
TIMEOUT = 60                              # seconds per LLM call
API_URL = "https://openrouter.ai/api/v1/chat/completions"
ROOT = os.path.dirname(os.path.abspath(__file__))
TARGETS = {"seedance": "Seedance 2.5", "kling": "Kling 4.0", "wan": "Wan 3.0"}

RUBRIC = {
    "faithful_to_idea": "Keeps every beat of the user's idea; nothing dropped, nothing added that changes it",
    "one_action": "One clear motion arc: start and end state stated, counts explicit ('one backflip')",
    "shot_and_camera": "Explicit shot size and ONE simple camera move",
    "concrete_subject": "Concrete subject, no vague adjectives",
    "lighting_mood": "Lighting and mood stated",
    "follows_guide": "Follows the model guide (structure, length, syntax, things to avoid)",
    "no_contradictions": "No contradictions",
    "plausible_motion": "Motion physically plausible within the duration",
    "simple_and_clear": "Plain short sentences, no stacked effects; fewer demands when the motion is fast",
}
# Effect terms that pile up demands on the model; counted by code and shown to the critic
EFFECTS = ["handheld", "shake", "flare", "anamorphic", "film grain", "grain", "speed ramp", "bullet time",
           "dolly zoom", "whip pan", "motion blur", "slow motion", "high shutter", "rack focus", "fisheye"]
# Repeatable moves need a count; fast body motion needs a short prompt. Both are checked by code.
MOVES = r"\b\w*(?:flips?|somersaults?|spins?|cartwheels?|twirls?)\b"  # also kickflip, backflip, heelflip
FAST = (r"\w*flips?\b|\b(ollies?|jumps?|leaps?|sprints?|runs?|running|vaults?|kicks?|dives?|dunks?|punch(es)?|"
        r"somersaults?|cartwheels?|skates?|skateboard\w*|surf(s|ing|ers?|boards?)?|tackles?|parkour)\b")
# Empty praise words: every guide says to show these with materials and light instead. Checked by code.
VAGUE = ["luxury", "luxurious", "premium", "sleek", "elegant", "stunning", "beautiful", "gorgeous", "epic",
         "cinematic", "breathtaking", "amazing", "masterpiece", "high quality", "high-quality", "ultra detailed",
         "high-end", "sophisticated", "vibrant", "dramatic"]


class AgentError(Exception):
    pass


def api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    env_path = os.path.join(ROOT, ".env")
    if not key and os.path.exists(env_path):
        for line in open(env_path):
            if line.strip().startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        raise AgentError("No API key: set OPENROUTER_API_KEY or put it in .env")
    return key


def norm(text):
    return " ".join(text.lower().replace("\u2014", "-").replace("\u2019", "'").split())


def load_guide(target):
    with open(os.path.join(ROOT, "guides", target + ".md")) as f:
        return f.read()


# ---- LLM call: max_tokens cap, timeout, one retry, JSON validation ---------------------------
def call_llm(system, user, required, temperature=0.7, max_tokens=900, usage=None, reasoning=None):
    body = json.dumps({
        "model": MODEL, "temperature": temperature, "max_tokens": max_tokens,
        "reasoning": {"effort": reasoning or "minimal"},  # this model cannot turn reasoning off
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    headers = {"Authorization": "Bearer " + api_key(), "Content-Type": "application/json",
               "X-Title": "Video Preset Agent"}
    last_error = ""
    for attempt in range(2):  # first try + one retry
        try:
            req = urllib.request.Request(API_URL, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read())
            if usage is not None and data.get("usage"):
                usage["in"] += data["usage"].get("prompt_tokens", 0)
                usage["out"] += data["usage"].get("completion_tokens", 0)
            text = data["choices"][0]["message"]["content"].strip()
            if text.startswith("```"):  # tolerate markdown fences around JSON
                text = text.strip("`").removeprefix("json").strip()
            result = json.loads(text)
            missing = [k for k in required if k not in result]
            if missing:
                raise ValueError("JSON is missing keys: " + ", ".join(missing))
            return result
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise AgentError("OpenRouter rejected the API key (HTTP %s). Check OPENROUTER_API_KEY." % e.code)
            last_error = "HTTP %s: %s" % (e.code, e.read().decode(errors="ignore")[:200])
        except Exception as e:  # timeout, network, bad JSON, missing keys
            last_error = "%s: %s" % (type(e).__name__, e)
    raise AgentError("LLM call failed after retry (" + last_error + ")")


# ---- Agent steps ---------------------------------------------------------------------------
PLAN_FIELDS = ["subject", "action", "shot_size", "camera_motion", "environment",
               "lighting", "style", "duration", "aspect_ratio"]


def planner(idea, usage):
    system = (
        "You are the Planner of a video prompt agent. Parse a one-line video idea into preset fields. "
        "Return JSON with keys: " + ", ".join(PLAN_FIELDS) + ". Rules: subject = concrete and visual "
        "(who/what, age, materials, colors); action = ONE motion arc in plain words from start to a clear "
        "end state, with explicit counts (e.g. 'runs to the edge, jumps the gap, does one backflip, lands "
        "on both feet'). Keep EVERY beat the idea mentions, add none; if the beats need more time, raise "
        "the duration instead of dropping them. shot_size = a film term; camera_motion = ONE simple move "
        "(for fast body motion: locked camera or a steady tracking shot); fill missing details with "
        "sensible choices that serve the idea; lighting = light source, direction and color plus the mood "
        "(e.g. 'soft window light from the left, calm mood'); style = ONE short look (e.g. 'realistic, "
        "natural colors'), no stacked lens or film effects; never vague words like cinematic, epic; "
        "duration = integer seconds (default 5, max 10); "
        "aspect_ratio = '16:9' unless the idea implies vertical (9:16) or square (1:1). All values are strings "
        "except duration.")
    return call_llm(system, "Idea: " + idea, PLAN_FIELDS, temperature=0.4, max_tokens=800, usage=usage)


def router(idea, plan, usage):
    guides = "\n\n".join("=== %s (%s) ===\n%s" % (k, v, load_guide(k)) for k, v in TARGETS.items())
    system = (
        "You are the Router of a video prompt agent. Choose the target video model for this shot. The "
        "author's real tests ('From my testing') show all three give similar quality for people and scenes, "
        "so decide by what the idea needs, using the guides: readable on-screen text, 4K or 21:9 -> kling; "
        "spoken dialogue with lip sync -> seedance; a cheap or budget option -> wan. If no need decides, use "
        "the soft default: a person as the subject -> seedance, no people -> kling. The reason is one plain "
        "sentence for the user that names the need that decided, e.g. 'The idea needs readable text on a "
        "sign, which Kling renders best.' or 'Nothing special is needed, so the default for people applies.' "
        'Return JSON: {"model": "seedance" | "kling" | "wan", "reason": "<one sentence>"}.')
    out = call_llm(system, "Guides:\n" + guides + "\n\nUser's idea: " + idea + "\n\nShot plan:\n" +
                   json.dumps(plan, indent=1),
                   ["model", "reason"], temperature=0, max_tokens=400, usage=usage)
    if out["model"] not in TARGETS:
        raise AgentError("Router returned unknown model: %s" % out["model"])
    return out


def writer(idea, plan, target, usage, previous=None, issues=None, keep_fixed=()):
    system = (
        "You are the Writer of a video prompt agent. Write the final text-to-video prompt for %s, following "
        "the model guide below (structure order, ideal length, camera vocabulary, things to avoid). "
        "Write simply, like directions to a camera crew: plain words, short sentences. Start with who does "
        "what: the full motion from start to a visible ending, with counts ('does one backflip and lands on both "
        "feet'); describe the ending itself, never write the words 'end state'. Every beat of the user's idea must be in the prompt, and add no new beats (no extra run-up, roll, turn or "
        "pose). Then where, ONE simple camera move with "
        "the shot size, light and a mood word, then only the lines the guide requires. Add no effects "
        "(handheld shake, lens flare, film grain, speed ramp, slow motion) unless the idea asks for them; at "
        "most one style term. Fast or complex body motion: under 60 words and a locked or steady tracking "
        "camera, because every extra demand raises the risk of artifacts. Never use praise words (luxury, "
        "premium, sleek, elegant, stunning, cinematic, vibrant, dramatic): show them with materials, shapes "
        "and light instead (a luxury watch -> a polished steel watch with a sapphire crystal). "
        "Do not mention the model name, duration or aspect ratio unless the guide's syntax needs it. "
        "Also write a reusable template: the same prompt with the main subject's whole noun phrase (including "
        "its article, e.g. 'A barista in a dark apron') replaced by the slot {subject}; later mentions become "
        "'they/their' for people or animals and 'it/its' for things. The template must read naturally when "
        "{subject} is a similar noun phrase ('a skateboarder', 'a red sports car', 'thick sea mist'). Also "
        "return subject_phrase: the main subject's noun phrase exactly as written in the prompt. "
        'Return JSON: {"prompt": "...", "template": "...", "subject_phrase": "..."}.\n\nMODEL GUIDE:\n%s'
    ) % (TARGETS[target], load_guide(target))
    user = "User's idea: " + idea + "\n\nShot plan:\n" + json.dumps(plan, indent=1)
    if previous:
        user += ("\n\nYour previous prompt:\n" + previous + "\n\nThe critic found these problems. Fix EVERY one "
                 "(simplify the shot plan if needed), keep what already works, and never drop the lighting "
                 "or the mood word. If a fix conflicts with the shot plan, the fix wins, but never drop a beat of the "
                 "user's idea (make it simpler instead):\n" +
                 "\n".join("- %s -> FIX: %s" % (i["problem"], i["fix"]) for i in issues))
        if keep_fixed:
            user += "\n\nAlready fixed earlier, do NOT bring these back:\n" + "\n".join("- " + p for p in keep_fixed)
    out = call_llm(system, user, ["prompt", "template", "subject_phrase"], temperature=0.7, max_tokens=1200,
                   usage=usage)
    if "{subject}" not in str(out["template"]):  # code fallback: put the slot where the subject phrase is
        phrase = str(out["subject_phrase"]).strip()
        hit = re.search(re.escape(phrase), out["prompt"], flags=re.I) if len(phrase) > 2 else None
        out["template"] = (out["prompt"][:hit.start()] + "{subject}" + out["prompt"][hit.end():] if hit
                           else "{subject}: " + out["prompt"])
    t = re.sub(r"\{(?!subject\})(\w+)\}", r"\1", out["template"])  # only one kind of slot: {subject}
    phrase = str(out["subject_phrase"]).strip()
    if len(phrase) > 2:  # a subject mention the writer left in the template becomes the slot too
        t = re.sub(re.escape(phrase), "{subject}", t, flags=re.I)
    t = re.sub(r"\{subject\},\s+(?=[a-z])", "{subject} ", t)  # "{subject}, sits" -> "{subject} sits"
    out["template"] = re.sub(r"\b(?:its|it)/(their|they)\b|\b(their|they)/(?:its|it)\b",
                             lambda m: m.group(1) or m.group(2), t)
    # {subject} carries its own article ("a skateboarder"), so drop any article written before the slot
    out["template"] = re.sub(r"\b(the|a|an)\s+\{subject\}", "{subject}", out["template"], flags=re.I)
    return out


def critic(prompt, idea, plan, target, usage, previous_issues=()):
    """Separate call, temperature 0. Sees only the user's idea, the prompt (+ duration/aspect), the guide,
    the rubric and, from round 2, its own earlier issues. Never sees the writer's reasoning."""
    rubric = "\n".join("- %s: %s" % kv for kv in RUBRIC.items())
    system = (
        "You are a strict Critic of text-to-video prompts for %s. Score the prompt 1-10 on each rubric item. "
        "Scale: 10 = nothing to improve; 8 = only cosmetic polish left; 6 = a real risk of a visibly worse "
        "video; 4 = likely failure. Every issue you list must lower the score of its rubric item. "
        "First audit, then score. Audit the prompt against each rubric item and the guide line by line: "
        "word count vs the guide's ideal length, structure order, vague words (cinematic, beautiful, "
        "high-definition, stunning, epic...), things the guide says to avoid, the weaknesses listed in THIS "
        "guide (only those; a strength of the model is never a risk), whether the action and camera move fit "
        "the duration. Faithfulness: list every action verb of the user's idea and check each one is in the "
        "prompt with the same meaning (smiling is not laughing, holding is not reading); a lost or weakened "
        "action is a real problem (<= 6). The motion has a stated end state and counts, otherwise the model invents the rest (double "
        "flips, teleporting). Simplicity: more demands = more artifacts, so stacked effects (handheld shake, "
        "lens flare, film grain...) or long camera instructions on fast body motion are a real risk (<= 6). "
        "Vague words = empty praise/quality words with no visible meaning (cinematic, beautiful, stunning, "
        "premium, high quality, masterpiece). Mood words (calm, tense, quiet, reflective) are REQUIRED by the "
        "rubric and are not vague. One action = one motion arc: a movement with its natural start and end "
        "(takes off, does one flip, lands) is ONE action, and stating the end is GOOD, never a risk. A "
        "simultaneous expression or ambient motion (steam, hair in the wind) is not a second action; separate "
        "activities in a row are ('runs, then buys flowers, then opens an umbrella'). A fast-motion prompt "
        "under 60 words meets the length rule. "
        "Be honest, not generous; list only real problems (never one you call "
        "acceptable); if nothing is wrong, return no issues.\n"
        "RUBRIC:\n%s\n\nMODEL GUIDE:\n%s\n\n"
        'Return JSON in this key order: {"previous": [{"id": <n>, "resolved": "yes" | "no"}] (one entry per '
        'previous issue, empty if none given), "issues": [{"item": <rubric key>, "problem": "<short>", '
        '"fix": "<concrete edit>", "guide_rule": "<exact words copied from the guide>" or ""}] (up to 4 real '
        'problems; guide_rule only if the prompt violates a rule written in the guide), '
        '"scores": {<rubric key>: int}}.'
    ) % (TARGETS[target], rubric, load_guide(target))
    effects = [e for e in EFFECTS if e in prompt.lower() and not (e == "grain" and "film grain" in prompt.lower())]
    user = ("USER'S IDEA: %s\nClip duration: %ss. Aspect ratio: %s. Word count (counted by code): %d. "
            "Effect terms (found by code): %s.\nPROMPT:\n%s") % (
        idea, plan["duration"], plan["aspect_ratio"], len(prompt.split()), ", ".join(effects) or "none", prompt)
    if previous_issues:
        user += ("\n\nIssues you found in EARLIER versions. For each, check the new prompt: is it really "
                 "resolved (the problem is gone, not just reworded, and has not come back)?\n" +
                 "\n".join("%d. [%s] %s" % (n, i["item"], i["problem"]) for n, i in enumerate(previous_issues, 1)))
    out = call_llm(system, user, ["previous", "issues", "scores"], temperature=0, max_tokens=3000,
                   usage=usage, reasoning="low")
    scores = {k: int(out["scores"].get(k, 0)) for k in RUBRIC}
    if not all(1 <= v <= 10 for v in scores.values()):
        raise AgentError("Critic returned invalid scores: %s" % out["scores"])
    issues = [i for i in out["issues"] if isinstance(i, dict) and i.get("item") in RUBRIC and i.get("problem")]
    # Caps enforced by code, not left to the LLM: a guide violation or an unresolved old issue -> item <= 6
    guide = norm(load_guide(target))
    for i in issues:
        i.setdefault("fix", "")
        quote = norm(str(i.get("guide_rule") or "")).strip(' ."')
        i["breaks_guide_rule"] = len(quote) >= 8 and quote in guide  # the quoted rule must really be in the guide
        if i["breaks_guide_rule"]:
            scores[i["item"]] = min(scores[i["item"]], 6)
    answers = {int(p.get("id", 0)): p.get("resolved") == "yes" for p in out["previous"] if isinstance(p, dict)}
    resolved = []
    for n, old in enumerate(previous_issues, 1):
        ok = answers.get(n, False)  # missing answer counts as unresolved
        resolved.append({"problem": old["problem"], "item": old["item"], "resolved": ok})
        if not ok:
            scores[old["item"]] = min(scores[old["item"]], 6)
    vague = [w for w in VAGUE if re.search(r"\b%s\b" % re.escape(w), prompt.lower())]
    if vague:  # deterministic check, like the word count: praise words cap concrete_subject at 6
        issues.append({"item": "concrete_subject", "problem": "Vague praise words (found by code): " +
                       ", ".join(vague), "fix": "Replace them with visible materials, shapes and light.",
                       "breaks_guide_rule": True})
        scores["concrete_subject"] = min(scores["concrete_subject"], 6)
    low = prompt.lower()  # repeatable moves need a count ("one backflip"), or the model may repeat them
    uncounted = [m.group() for m in re.finditer(MOVES, low)
                 if not re.search(r"\b(one|single|two|three|double|triple)\b", low[max(0, m.start() - 25):m.start()])
                 and not re.search(r"\b(once|twice)\b", low[m.end():m.end() + 10])]
    if uncounted:
        issues.append({"item": "one_action", "problem": "Move without a count (found by code): " +
                       ", ".join(uncounted), "fix": "Say how many, e.g. 'does one backflip and lands'.",
                       "breaks_guide_rule": True})
        scores["one_action"] = min(scores["one_action"], 6)
    words = len(prompt.split())  # fast body motion needs a short prompt (guides: under 60 words)
    if words > 60 and re.search(FAST, low):
        issues.append({"item": "simple_and_clear", "problem": "Fast body motion in %d words (found by code; "
                       "limit 60)" % words, "fix": "Cut to under 60 words: keep the action, one camera "
                       "move, light and mood, the required lines.", "breaks_guide_rule": True})
        scores["simple_and_clear"] = min(scores["simple_and_clear"], 6)
    total = round(sum(scores.values()) / len(scores), 1)  # computed in code, not trusted from LLM
    verdict = "pass" if total >= PASS_SCORE and min(scores.values()) >= MIN_ITEM else "revise"
    return {"scores": scores, "total": total, "issues": issues, "resolved": resolved, "verdict": verdict}


# ---- Orchestration -------------------------------------------------------------------------
def run_agent(idea, choice="auto", emit=lambda step, data: None):
    """Runs the full pipeline. emit(step, data) streams each step (used by CLI and SSE)."""
    start, usage, events = time.time(), {"in": 0, "out": 0}, []

    def step(name, data):
        data = dict(data, t=round(time.time() - start, 1))
        events.append({"step": name, "data": data})
        emit(name, data)

    plan = planner(idea, usage)
    step("planner", {"plan": plan})

    if choice in TARGETS:
        route = {"model": choice, "reason": "Chosen manually by the user (override)."}
    else:
        route = router(idea, plan, usage)
    target = route["model"]
    step("router", {"model": target, "name": TARGETS[target], "reason": route["reason"]})

    # Evaluator-optimizer loop. Code decides from the scores; the best version wins, not the last one.
    draft = writer(idea, plan, target, usage)
    step("writer", {"round": 1, "prompt": draft["prompt"]})
    history, previous_issues = [], []
    for rnd in range(1, MAX_ROUNDS + 1):
        review = critic(draft["prompt"], idea, plan, target, usage, previous_issues)
        history.append((review["total"], rnd, draft, review["verdict"] == "pass"))
        step("critic", dict(review, round=rnd))
        if review["verdict"] == "pass":
            stop = "passed (all items >= %d, average >= %d)" % (MIN_ITEM, PASS_SCORE)
            break
        if rnd > 1 and review["total"] <= history[-2][0]:
            stop = "stopped: score did not improve"
            break
        if rnd == MAX_ROUNDS:
            stop = "stopped: max %d rounds" % MAX_ROUNDS
            break
        # Next round re-checks ALL issues found so far (catches regressions), writer fixes open ones
        unresolved = [r for r in review["resolved"] if not r["resolved"]]
        todo = review["issues"] + [dict(r, fix="Still unresolved: really fix it.") for r in unresolved]
        previous_issues = previous_issues + review["issues"]
        fixed = [r["problem"] for r in review["resolved"] if r["resolved"]]
        draft = writer(idea, plan, target, usage, previous=draft["prompt"], issues=todo, keep_fixed=fixed)
        step("revise", {"round": rnd + 1, "fixes": [i["fix"] for i in todo], "prompt": draft["prompt"]})

    best_total, best_round, best, best_passed = max(history, key=lambda h: (h[0], -h[1]))  # tie -> earlier
    cost = usage["in"] * PRICE_IN / 1e6 + usage["out"] * PRICE_OUT / 1e6
    final = {"idea": idea, "model": target, "name": TARGETS[target], "prompt": best["prompt"],
             "template": best["template"], "first_score": history[0][0], "final_score": best_total,
             "best_round": best_round, "passed": best_passed, "rounds": len(history), "stop": stop,
             "seconds": round(time.time() - start, 1), "tokens": usage, "cost_usd": round(cost, 4), "llm": MODEL}
    step("final", final)
    return {"idea": idea, "choice": choice, "created": datetime.now().isoformat(timespec="seconds"),
            "events": events, "final": final}


def save_run(run):
    os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
    name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    with open(os.path.join(ROOT, "runs", name), "w") as f:
        json.dump(run, f, indent=2, ensure_ascii=False)
    return name


def print_step(step, d):
    if step == "planner":
        print("\n[Planner]", json.dumps(d["plan"], ensure_ascii=False))
    elif step == "router":
        print("\n[Router] %s - %s" % (d["name"], d["reason"]))
    elif step in ("writer", "revise"):
        print("\n[%s round %d]\n%s" % (step.title(), d["round"], d["prompt"]))
    elif step == "critic":
        print("\n[Critic round %d] total %.1f -> %s | %s" % (d["round"], d["total"], d["verdict"], d["scores"]))
        for r in d["resolved"]:
            print("  %s previous: %s" % ("[resolved]" if r["resolved"] else "[NOT resolved]", r["problem"]))
        for i in d["issues"]:
            print("  - [%s%s] %s" % (i["item"], ", guide rule" if i.get("breaks_guide_rule") else "", i["problem"]))
    elif step == "final":
        print("\n[Final] %s | score %.1f -> %.1f (best = round %d, %s) | rounds %d, %s | %.1fs | ~$%.4f" % (
            d["name"], d["first_score"], d["final_score"], d["best_round"], "passed" if d["passed"] else
            "did NOT pass", d["rounds"], d["stop"], d["seconds"],
            d["cost_usd"]))
        print("Prompt: %s\nTemplate: %s" % (d["prompt"], d["template"]))


if __name__ == "__main__":
    args = sys.argv[1:]
    choice = "auto"
    if "--model" in args:
        i = args.index("--model")
        choice = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit('Usage: python3 agent.py "your idea" [--model auto|seedance|kling|wan]')
    try:
        run = run_agent(" ".join(args), choice, print_step)
        print("\nSaved: runs/" + save_run(run))
    except AgentError as e:
        sys.exit("Error: %s" % e)
