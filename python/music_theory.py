# The 7 letter names in order
LETTERS = ["C", "D", "E", "F", "G", "A", "B"]

# Semitone value of each natural note (no sharps or flats)
NATURAL_SEMITONES = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

# Scale interval formulas in semitones
SCALE_FORMULAS = {
    "major":          [2, 2, 1, 2, 2, 2, 1],
    "natural_minor":  [2, 1, 2, 2, 1, 2, 2],
    "harmonic_minor": [2, 1, 2, 2, 1, 3, 1],
    "pentatonic":     [2, 2, 3, 2, 3],
    "blues":          [3, 2, 1, 1, 3, 2],
}

# Chord type interval formulas in semitones from root
CHORD_FORMULAS = {
    "maj":  [0, 4, 7],
    "min":  [0, 3, 7],
    "dim":  [0, 3, 6],
    "aug":  [0, 4, 8],
    "maj7": [0, 4, 7, 11],
    "7":    [0, 4, 7, 10],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "add9": [0, 4, 7, 14],
    "minadd9": [0, 3, 7, 14],
    "9":       [0, 4, 7, 10, 14],
    "min9":    [0, 3, 7, 10, 14],
    "6":       [0, 4, 7, 9],   
}

INVALID_ROOTS = {"B#", "Cb", "E#", "Fb"}

ENHARMONIC_SUGGESTIONS = {
    "B#": "C",
    "Cb": "B", 
    "E#": "F",
    "Fb": "E",
}

def parse_root(root_input):
    """
    Takes user input like 'C', 'F#', 'Gb'
    Returns (letter, accidental, semitone) tuple
    e.g. 'F#' -> ('F', '#', 6)
    """
    # Clean the input
    root_input = root_input.strip().capitalize()

    # Validate not in invalid roots
    if root_input in INVALID_ROOTS:
        raise ValueError(f"{root_input} is theoretically valid but not supported. Try {ENHARMONIC_SUGGESTIONS[root_input]} instead.")
    
    # Extract letter and accidental
    letter = root_input[0]
    accidental = root_input[1:] if len(root_input) > 1 else ""
    
    # Validate letter
    if letter not in LETTERS:
        raise ValueError(f"Invalid note: {root_input}")
    
    # Validate accidental
    if accidental not in ("", "#", "b"):
        raise ValueError(f"Invalid accidental: {root_input}")
    
    # Calculate semitone value
    semitone = NATURAL_SEMITONES[letter]
    if accidental == "#":
        semitone += 1
    elif accidental == "b":
        semitone -= 1
    
    # Wrap around (e.g. Cb = B = 11, not -1)
    semitone = semitone % 12
    
    return (letter, accidental, semitone)

def get_scale_notes(root_input, scale_type):
    if scale_type not in SCALE_FORMULAS:
        raise ValueError(f"Unknown scale type: {scale_type}")
    
    letter, accidental, semitone = parse_root(root_input)
    letter_index = LETTERS.index(letter)
    
    # Root note is note 0
    root_name = letter + accidental
    notes = [(root_name, semitone)]
    
    current_semitone = semitone
    
    for i, interval in enumerate(SCALE_FORMULAS[scale_type]):
        current_semitone = (current_semitone + interval) % 12
        
        # Next letter in sequence
        current_letter = LETTERS[(letter_index + i + 1) % 7]
        
        natural_semitone = NATURAL_SEMITONES[current_letter]
        diff = (current_semitone - natural_semitone) % 12
        
        if diff == 0:
            note_name = current_letter
        elif diff == 1:
            note_name = current_letter + "#"
        elif diff == 11:
            note_name = current_letter + "b"
        
        notes.append((note_name, current_semitone))
    
    return notes[:-1]  # drop the octave root before returning

def get_diatonic_chord_type(scale_type, degree):
    """
    Returns the chord type for a given scale degree.
    degree is 0-indexed.
    e.g. major scale degree 0 -> "maj", degree 1 -> "min"
    """
    DIATONIC_CHORD_TYPES = {
        "major":          ["maj", "min", "min", "maj", "maj", "min", "dim"],
        "natural_minor":  ["min", "dim", "maj", "min", "min", "maj", "maj"],
        "harmonic_minor": ["min", "dim", "aug", "min", "maj", "maj", "dim"],
        "pentatonic":     ["maj", "min", "min", "maj", "min"],
        "blues":          ["7",   "min", "dim", "min", "maj", "min"],
    }

    if scale_type not in DIATONIC_CHORD_TYPES:
        raise ValueError(f"Unknown scale type: {scale_type}")

    return DIATONIC_CHORD_TYPES[scale_type][degree]

def get_diatonic_chords(root_input, scale_type):
    """
    Returns full chord list for a given key and scale.
    e.g. get_diatonic_chords("D", "major") ->
    [
        {"degree": 1, "root": "D", "semitone": 2, "chord_type": "maj", "display": "Dmaj"},
        {"degree": 2, "root": "E", "semitone": 4, "chord_type": "min", "display": "Emin"},
        ...
    ]
    """
    scale_notes = get_scale_notes(root_input, scale_type)
    chords = []

    for i, (note_name, semitone) in enumerate(scale_notes):
        chord_type = get_diatonic_chord_type(scale_type, i)
        chords.append({
            "degree": i + 1,
            "root": note_name,
            "semitone": semitone,
            "chord_type": chord_type,
            "display": f"{note_name}{chord_type}",
        })

    return chords

def get_chord_notes(root, chord_type, inversion=0, octave=4):
    """
    Returns list of MIDI note numbers to play.
    root is a note name string e.g. "F#"
    inversion: 0 = root position, 1 = first, 2 = second, 3 = third
    octave: base octave (middle C is octave 4)
    
    MIDI note number = (octave + 1) * 12 + semitone
    e.g. middle C = (4 + 1) * 12 + 0 = 60
    """
    _, _, root_semitone = parse_root(root)
    
    intervals = CHORD_FORMULAS[chord_type]
    
    # Build notes as MIDI numbers in root position first
    midi_notes = [(octave + 1) * 12 + root_semitone + interval 
                  for interval in intervals]
    
    # Apply inversion by rotating
    # # inversion=0: [C, E, G]
    # # inversion=1: [E, G, C] → E is lowest, C bumped up an octave
    # # inversion=2: [G, C, E] → G is lowest, C and E bumped up
    for i in range(inversion):
        midi_notes.append(midi_notes.pop(0) + 12)
        
    return midi_notes