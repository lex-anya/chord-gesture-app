// ── music_theory.js ──────────────────────────────────────
// Port of music_theory.py — runs entirely in browser

const SCALE_FORMULAS = {
  major:          [2,2,1,2,2,2,1],
  natural_minor:  [2,1,2,2,1,2,2],
  harmonic_minor: [2,1,2,2,1,3,1],
  pentatonic:     [2,2,3,2,3],
  blues:          [3,2,1,1,3,2],
};

const CHORD_FORMULAS_MT = {
  maj:  [0,4,7],  min:  [0,3,7],  dim:  [0,3,6],
  aug:  [0,4,8],  maj7: [0,4,7,11], "7": [0,4,7,10],
  min7: [0,3,7,10], dim7: [0,3,6,9],
  sus2: [0,2,7],  sus4: [0,5,7],  add9: [0,4,7,14],
};

const DIATONIC_CHORD_TYPES = {
  major:          ["maj","min","min","maj","maj","min","dim"],
  natural_minor:  ["min","dim","maj","min","min","maj","maj"],
  harmonic_minor: ["min","dim","aug","min","maj","maj","dim"],
  pentatonic:     ["maj","min","min","maj","min"],
  blues:          ["7","min","dim","min","maj","min"],
};

const LETTERS = ["C","D","E","F","G","A","B"];
const NATURAL_SEMITONES = {C:0,D:2,E:4,F:5,G:7,A:9,B:11};
const INVALID_ROOTS = new Set(["B#","Cb","E#","Fb"]);

function parseRoot(root) {
  root = root.trim()[0].toUpperCase() + root.trim().slice(1).toLowerCase();
  if (INVALID_ROOTS.has(root)) throw new Error(`${root} not supported.`);
  const letter = root[0];
  const accidental = root.slice(1);
  if (!LETTERS.includes(letter)) throw new Error(`Invalid note: ${root}`);
  if (!["","#","b"].includes(accidental)) throw new Error(`Invalid accidental: ${root}`);
  let semitone = NATURAL_SEMITONES[letter];
  if (accidental === "#") semitone += 1;
  if (accidental === "b") semitone -= 1;
  semitone = ((semitone % 12) + 12) % 12;
  return { letter, accidental, semitone };
}

function getScaleNotes(rootInput, scaleType) {
  if (!SCALE_FORMULAS[scaleType]) throw new Error(`Unknown scale: ${scaleType}`);
  const { letter, accidental, semitone } = parseRoot(rootInput);
  const letterIndex = LETTERS.indexOf(letter);
  const rootName = letter + accidental;
  const notes = [{ name: rootName, semitone }];
  let currentSemitone = semitone;

  SCALE_FORMULAS[scaleType].forEach((interval, i) => {
    currentSemitone = (currentSemitone + interval) % 12;
    const currentLetter = LETTERS[(letterIndex + i + 1) % 7];
    const naturalSemitone = NATURAL_SEMITONES[currentLetter];
    const diff = ((currentSemitone - naturalSemitone) % 12 + 12) % 12;
    let noteName;
    if (diff === 0)  noteName = currentLetter;
    else if (diff === 1)  noteName = currentLetter + "#";
    else if (diff === 11) noteName = currentLetter + "b";
    notes.push({ name: noteName, semitone: currentSemitone });
  });

  return notes.slice(0, -1);
}

function getDiatonicChords(rootInput, scaleType) {
  const scaleNotes = getScaleNotes(rootInput, scaleType);
  const chordTypes = DIATONIC_CHORD_TYPES[scaleType];
  return scaleNotes.map((note, i) => ({
    degree: i + 1,
    root: note.name,
    semitone: note.semitone,
    chord_type: chordTypes[i],
    display: `${note.name}${chordTypes[i]}`,
    inversion: 0,
    octave: 4,
  }));
}