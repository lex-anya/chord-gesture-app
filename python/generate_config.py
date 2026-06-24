import json
import os
from music_theory import (
    SCALE_FORMULAS,
    CHORD_FORMULAS,
    get_diatonic_chords,
    get_chord_notes,
)

def generate_config():
    config = {
        "scale_types": list(SCALE_FORMULAS.keys()),
        "chord_types": list(CHORD_FORMULAS.keys()),
        "default_key": "C",
        "default_scale": "major",
        "default_octave": 4,
        "default_wave": "sine",
        "diatonic_chords": get_diatonic_chords("C", "major"),
    }
    
    # Write to web/config.json
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "web",
        "config.json"
    )
    
    print(output_path)
    print(output_path)
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Config written to {output_path}")

if __name__ == "__main__":
    generate_config()