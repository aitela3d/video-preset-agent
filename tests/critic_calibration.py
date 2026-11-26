"""Critic calibration: known-bad prompts must fail, known-good prompts must pass.

Run: python3 tests/critic_calibration.py
Bad prompt passes the check if one of its target rubric items scores < 7 (so the loop forces a revision).
Good prompt passes the check if the average is >= 8 and every item is >= 7 (verdict pass).
The "overloaded action" case is a real prompt that scored 10/10 earlier but produced a double flip and
artifacts on Seedance 2.5 flash, while the plain idea gave a clean single flip (author's test, 27 Nov 2026).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import critic  # noqa: E402

PLAN = {"duration": 5, "aspect_ratio": "16:9"}
PARKOUR = "a parkour runner jumps between rooftops at sunset, flips and lands"
CASES = [  # (kind, name, model, target items, user idea, prompt)
    ("bad", "vague words", "kling", ["concrete_subject"], "a luxury watch close-up",
     "A stunning, beautiful, epic luxury watch in an amazing cinematic scene. Close-up, slow push-in. "
     "Gorgeous high-quality lighting, breathtaking premium mood, masterpiece, ultra detailed."),
    ("bad", "two actions", "seedance", ["one_action"], "a woman in a red raincoat on a rainy street",
     "A young woman in a red raincoat runs across a busy street, then stops to buy flowers at a market stall, "
     "and finally opens her umbrella as rain starts. Medium shot, camera tracks her from the side. Overcast "
     "daylight, soft grey light, calm mood. Realistic, 35mm film look."),
    ("bad", "camera contradiction", "kling", ["no_contradictions", "shot_and_camera"],
     "a red convertible on a desert highway",
     "A red vintage convertible is parked on an empty desert highway at golden hour, heat haze rising from the "
     "asphalt. Wide shot, locked static camera that slowly orbits 360 degrees around the car while craning "
     "up. Warm low sun from the right, long shadows, quiet open mood."),
    ("bad", "overloaded action (real)", "seedance", ["faithful_to_idea", "simple_and_clear", "one_action"], PARKOUR,
     "An athletic parkour runner wearing a sleek black compression suit and neon orange sneakers performs a "
     "mid-air backflip while leaping across a gap between two concrete apartment rooftops at dusk. Medium long "
     "shot, the camera performs a tracking shot following the subject's trajectory through the air. Golden hour "
     "sunset light from behind creates a strong rim light and long shadows, handheld camera shake, 35mm film "
     "grain, anamorphic lens flare, energetic mood. Sound: wind rushing, distant city ambience. No subtitles. "
     "No BGM."),
    ("good", "person close-up", "seedance", None, "a woman at a rainy tram stop looks up at the sky",
     "A woman in her 30s with short curly hair and a grey wool coat stands under a clear umbrella at a rainy "
     "tram stop at dusk and slowly looks up at the sky. Medium close-up, the camera pushes in slowly as she "
     "looks up. Cool blue streetlight with warm shop-window rim light, soft rain. Quiet, reflective mood. "
     "Realistic, 35mm film look. Sound: rain on pavement, distant tram bell. No subtitles."),
    ("good", "product shot", "kling", None, "steam rising from a coffee mug by a rainy window",
     "A matte black ceramic coffee mug sits on a weathered oak table beside a rain-streaked window. A thin curl "
     "of steam rises from the coffee and drifts to the left. One continuous shot, no cuts: close-up, slow "
     "push-in toward the rim of the mug. Soft grey daylight from the window on the left, warm reflection on "
     "the glaze. Calm, quiet morning mood, muted brown and grey palette, shallow depth of field."),
    ("good", "simple action", "seedance", None, PARKOUR,
     "A young man in a black t-shirt and grey joggers jumps off the edge of a flat concrete rooftop at sunset, "
     "does one backflip over the gap and lands on both feet on the next roof. Medium wide shot, the camera "
     "tracks sideways at a steady pace. Warm low sun from behind, long shadows, energetic mood. No subtitles."),
]

if __name__ == "__main__":
    usage, ok_count = {"in": 0, "out": 0}, 0
    print("%-5s %-25s %-9s %-18s %5s %6s %-7s %s" % ("kind", "case", "model", "target item", "item", "total",
                                                    "verdict", "result"))
    for kind, name, model, items, idea, prompt in CASES:
        r = critic(prompt, idea, PLAN, model, usage)
        s = r["scores"]
        if kind == "bad":
            item = min(items, key=lambda k: s[k])  # the weakest of the target items
            ok = s[item] < 7
        else:
            item = None
            ok = r["total"] >= 8 and min(s.values()) >= 7
        ok_count += ok
        print("%-5s %-25s %-9s %-18s %5s %6.1f %-7s %s" % (kind, name, model, item or "(all >= 7)",
              s[item] if item else min(s.values()), r["total"], r["verdict"], "OK" if ok else "FAIL"))
        for i in r["issues"]:
            print("        - [%s%s] %s" % (i["item"], ", guide rule" if i.get("breaks_guide_rule") else "",
                                         i["problem"]))
    print("\n%d/%d cases OK. Tokens in/out: %d/%d" % (ok_count, len(CASES), usage["in"], usage["out"]))
    sys.exit(0 if ok_count == len(CASES) else 1)
