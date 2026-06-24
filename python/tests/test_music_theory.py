import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_theory import get_scale_notes
from music_theory import get_diatonic_chords
from music_theory import get_chord_notes

def test_d_major():
    notes = get_scale_notes("D", "major")
    names = [n[0] for n in notes]
    assert names == ["D", "E", "F#", "G", "A", "B", "C#"]

def test_f_major():
    notes = get_scale_notes("F", "major")
    names = [n[0] for n in notes]
    assert names == ["F", "G", "A", "Bb", "C", "D", "E"]

def test_bb_major():
    notes = get_scale_notes("Bb", "major")
    names = [n[0] for n in notes]
    assert names == ["Bb", "C", "D", "Eb", "F", "G", "A"]

def test_a_natural_minor():
    notes = get_scale_notes("A", "natural_minor")
    names = [n[0] for n in notes]
    assert names == ["A", "B", "C", "D", "E", "F", "G"]

def test_c_major_chords():
    chords = get_diatonic_chords("C", "major")
    displays = [c["display"] for c in chords]
    assert displays == ["Cmaj", "Dmin", "Emin", "Fmaj", "Gmaj", "Amin", "Bdim"]   

def test_c_major_first_inversion():
    # E4 G4 C5 = MIDI 64 67 72
    notes = get_chord_notes("C", "maj", inversion=1, octave=4)
    assert notes == [64, 67, 72]

def test_c_major_second_inversion():
    # G4 C5 E5 = MIDI 67 72 76
    notes = get_chord_notes("C", "maj", inversion=2, octave=4)
    assert notes == [67, 72, 76]