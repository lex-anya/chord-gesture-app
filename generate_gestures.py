import os

OUT_DIR = "docs/assets/gestures"
os.makedirs(OUT_DIR, exist_ok=True)

FINGER_BASES = {
    "thumb":  (30, 92),
    "index":  (40, 76),
    "middle": (54, 72),
    "ring":   (68, 74),
    "pinky":  (80, 78),
}

EXTENDED_TIPS = {
    "thumb":  (14, 70),
    "index":  (38, 34),
    "middle": (52, 28),
    "ring":   (66, 32),
    "pinky":  (79, 38),
}

CURLED_TIPS = {
    "thumb":  (38, 88),
    "index":  (46, 90),
    "middle": (56, 92),
    "ring":   (67, 91),
    "pinky":  (76, 89),
}

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]

def colors(hand):
    if hand == "right":
        return {"joint": "#A78BFA", "connection": "#6D28D9"}
    else:
        return {"joint": "#60A5FA", "connection": "#1D4ED8"}

def pip(base, tip):
    return ((base[0]+tip[0])/2 - 2, (base[1]+tip[1])/2)

def finger_svg(finger, extended, c):
    base = FINGER_BASES[finger]
    tip  = EXTENDED_TIPS[finger] if extended else CURLED_TIPS[finger]
    mid  = pip(base, tip)
    lines = [
        f'<polyline points="{base[0]},{base[1]} {mid[0]:.1f},{mid[1]:.1f} {tip[0]},{tip[1]}" fill="none" stroke="{c["connection"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    for (jx, jy) in [base, mid, tip]:
        lines.append(f'<circle cx="{jx:.1f}" cy="{jy:.1f}" r="3" fill="{c["joint"]}"/>')
    return "\n  ".join(lines)

def palm_connections(c):
    lines = [
        f'<polyline points="40,76 54,72 68,74 80,78" fill="none" stroke="{c["connection"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<line x1="30" y1="92" x2="40" y2="76" stroke="{c["connection"]}" stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="40" y1="76" x2="42" y2="128" stroke="{c["connection"]}" stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="54" y1="72" x2="60" y2="128" stroke="{c["connection"]}" stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="80" y1="78" x2="78" y2="128" stroke="{c["connection"]}" stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="38" y1="128" x2="82" y2="128" stroke="{c["connection"]}" stroke-width="2.5" stroke-linecap="round"/>',
        f'<circle cx="38" cy="128" r="3" fill="{c["joint"]}"/>',
        f'<circle cx="82" cy="128" r="3" fill="{c["joint"]}"/>',
        f'<circle cx="60" cy="128" r="3" fill="{c["joint"]}"/>',
    ]
    return "\n  ".join(lines)

def make_svg(extended_fingers, hand="right", label=""):
    c = colors(hand)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 160" width="120" height="160">',
        '  <rect width="120" height="160" fill="#000000" rx="8"/>',
        f'  {palm_connections(c)}',
    ]
    if hand == "left":
        parts.append('  <g transform="translate(120,0) scale(-1,1)">')
    parts.append(f'  {palm_connections(c)}')
    for finger in FINGERS:
        parts.append(f'  {finger_svg(finger, finger in extended_fingers, c)}')
    if hand == "left":
        parts.append('  </g>')
    if label:
        parts.append(f'  <text x="60" y="150" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" fill="{c["joint"]}">{label}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def make_stop_svg():
    cr = colors("right")
    cl = colors("left")

    def hand_group(ox, c, mirror=False):
        lines = [f'<g transform="translate({ox},0)">']
        if mirror:
            lines.append('  <g transform="translate(120,0) scale(-1,1)">')
        lines.append(f'  {palm_connections(c)}')
        for finger in FINGERS:
            lines.append(f'  {finger_svg(finger, True, c)}')
        if mirror:
            lines.append('  </g>')
        lines.append('</g>')
        return "\n".join(lines)

    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160" width="240" height="160">',
        '  <rect width="240" height="160" fill="#000000" rx="8"/>',
        hand_group(0, cl, mirror=True),   # left hand, mirrored so thumb faces right (inward)
        hand_group(120, cr, mirror=False),  # right hand, no mirror, thumb already faces left (inward)
        '  <text x="120" y="150" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" fill="#6B7280">stop</text>',
        '</svg>',
    ])

GESTURES = {
    "gesture_1":    (["index"],                                "right", "1"),
    "gesture_2":    (["index","middle"],                       "right", "2"),
    "gesture_3":    (["index","middle","ring"],                 "right", "3"),
    "gesture_4":    (["index","middle","ring","pinky"],         "right", "4"),
    "gesture_5":    (["thumb","index","middle","ring","pinky"], "right", "5"),
    "gesture_6":    (["thumb"],                                "right", "6"),
    "gesture_7":    (["thumb","index"],                        "right", "7"),
    "gesture_8":    (["thumb","pinky"],                        "right", "8"),
    "gesture_9":    (["index","pinky"],                        "right", "9"),
    "gesture_10":   (["pinky"],                                "right", "10"),
    "gesture_play": (["thumb","index"],                        "left",  "play"),
}

for name, (extended, hand, label) in GESTURES.items():
    path = os.path.join(OUT_DIR, f"{name}.svg")
    with open(path, "w") as f:
        f.write(make_svg(extended, hand=hand, label=label))
    print(f"✓ {name}.svg")

path = os.path.join(OUT_DIR, "gesture_stop.svg")
with open(path, "w") as f:
    f.write(make_stop_svg())
print("✓ gesture_stop.svg")
print(f"\nAll 12 SVGs written to {OUT_DIR}/")