from flask import Flask, request, jsonify, send_from_directory
import sys
import os

# Make sure we can import from the python/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from music_theory import get_diatonic_chords, SCALE_FORMULAS, CHORD_FORMULAS
import json

app = Flask(__name__, static_folder="web", static_url_path="")

# ── Serve web files ───────────────────────────────────────
@app.route("/")
def setup():
    return send_from_directory("web", "setup.html")

@app.route("/app")
def player():
    return send_from_directory("web", "index.html")

# ── Generate config ───────────────────────────────────────
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    key        = data.get("key", "C")
    scale_type = data.get("scale_type", "major")
    octave     = int(data.get("octave", 4))
    # wave       = data.get("wave", "sine")
    slots      = data.get("slots", [])  # user's custom slot configurations

    print(f"Received slots: {slots}")

    # Generate diatonic chords for selected key/scale
    diatonic = get_diatonic_chords(key, scale_type)

    # Build final 10 slots
    # If user sent custom slots, use those; otherwise use diatonic defaults
    final_slots = []
    for i in range(10):
        if i < len(slots) and slots[i] and slots[i].get("root"):
            # User customised this slot
            final_slots.append({
                "degree":     i + 1,
                "root":       slots[i]["root"],
                "chord_type": slots[i]["chordType"],
                "inversion":  slots[i].get("inversion", 0),
                "octave":     slots[i].get("octave", octave),
                "display":    f"{slots[i]['root']}{slots[i]['chordType']}",
            })
        elif i < len(slots) and slots[i] is None:
            # User explicitly cleared this slot
            final_slots.append(None)
        elif i < len(diatonic):
            # Use diatonic default
            d = diatonic[i].copy()
            d["octave"] = octave
            final_slots.append(d)
        else:
            # Empty slot
            final_slots.append(None)

    config = {
        "key":            key,
        "scale_type":     scale_type,
        "octave":         octave,
        # "wave":           wave,
        "scale_types":    list(SCALE_FORMULAS.keys()),
        "chord_types":    list(CHORD_FORMULAS.keys()),
        "slots":          final_slots,
    }

    # Write config.json
    config_path = os.path.join(os.path.dirname(__file__), "web", "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return jsonify({"status": "ok", "config": config})

# Serve config fresh (no browser cache)
@app.route("/config")
def get_config():
    config_path = os.path.join(os.path.dirname(__file__), "web", "config.json")
    with open(config_path) as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    app.run(debug=True, port=5000)