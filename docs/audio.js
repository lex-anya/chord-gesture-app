// ── Audio (Tone.js) ───────────────────────────────────────
// Loaded after sketch.js. Patches onConfirm() and onStop().

const CHORD_INTERVALS = {
  "maj":  [0,4,7],  "min":  [0,3,7],  "dim":  [0,3,6],
  "aug":  [0,4,8],  "maj7": [0,4,7,11], "7":  [0,4,7,10],
  "min7": [0,3,7,10], "dim7": [0,3,6,9],
  "sus2": [0,2,7],  "sus4": [0,5,7],  "add9": [0,4,7,14],
  "minadd9": [0, 3, 7, 14],  "9": [0, 4, 7, 10, 14],  "min9": [0, 3, 7, 10, 14],
  "6": [0, 4, 7, 9],
};

let synth = null;       // PolySynth, created on first confirm
let sampler = null;
let audioReady = false;

// ── Build Tone.js note strings with correct octave ────────
// Mirrors music_theory.py get_chord_notes() inversion logic.
// Works on raw semitone intervals so add9 (14) gets placed
// in the right octave automatically.
function buildNoteStrings(root, chordType, inversion, baseOctave) {
  const intervals = [...(CHORD_INTERVALS[chordType] || [0,4,7])];

  // Rotate left by inversion count (same as Python)
  for (let i = 0; i < inversion; i++) {
    intervals.push(intervals.shift() + 12);
  }

  // Find root semitone
  const useFlats = root.includes("b") || root === "F";
  const noteList = useFlats
    ? ["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"]
    : ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
  const rootSemitone = noteList.indexOf(root);

  // Convert each interval to a Tone.js note string
  const notes = [];
  for (const interval of intervals) {
    const semitone = (rootSemitone + interval) % 12;
    const octaveBump = Math.floor((rootSemitone + interval) / 12);
    const noteName = noteList[semitone];
    notes.push(`${noteName}${baseOctave + octaveBump}`);
  }

  return notes;
}

// ── Init synth (call inside user gesture) ─────────────────
// async function initAudio() {
//   if (audioReady) return;
//   await Tone.start();

//   synth = new Tone.PolySynth(Tone.Synth, {
//     oscillator: { type: config.wave || "sine" },
//     envelope: {
//       attack:  0.05,
//       decay:   0.1,
//       sustain: 0.8,
//       release: 1.2,
//     },
//   }).toDestination();

//   synth.volume.value = Tone.gainToDb(state.volume ?? 0.7);
//   audioReady = true;
// }
    // document.getElementById("audio-unlock").addEventListener("click", async () => {
    // await Tone.start();
    // synth = new Tone.PolySynth(Tone.Synth, {
    //     oscillator: { type: config.wave || "sine" },
    //     envelope: { attack: 0.05, decay: 0.1, sustain: 0.8, release: 1.2 },
    // }).toDestination();
    // synth.volume.value = Tone.gainToDb(state.volume ?? 0.7);
    // audioReady = true;
    // document.getElementById("audio-unlock").remove();
    // });

  document.getElementById("audio-unlock").addEventListener("click", async () => {
    document.getElementById("audio-unlock").innerHTML = 
      `<div style="color:#A78BFA; font-family:'JetBrains Mono',monospace; font-size:16px;">Loading piano...</div>`;
    
    await Tone.start();

    sampler = new Tone.Sampler({
      urls: {
        "A0":  "A0.mp3",  "C1":  "C1.mp3",  "D#1": "Ds1.mp3", "F#1": "Fs1.mp3",
        "A1":  "A1.mp3",  "C2":  "C2.mp3",  "D#2": "Ds2.mp3", "F#2": "Fs2.mp3",
        "A2":  "A2.mp3",  "C3":  "C3.mp3",  "D#3": "Ds3.mp3", "F#3": "Fs3.mp3",
        "A3":  "A3.mp3",  "C4":  "C4.mp3",  "D#4": "Ds4.mp3", "F#4": "Fs4.mp3",
        "A4":  "A4.mp3",  "C5":  "C5.mp3",  "D#5": "Ds5.mp3", "F#5": "Fs5.mp3",
        "A5":  "A5.mp3",  "C6":  "C6.mp3",  "D#6": "Ds6.mp3", "F#6": "Fs6.mp3",
        "A6":  "A6.mp3",  "C7":  "C7.mp3",  "D#7": "Ds7.mp3", "F#7": "Fs7.mp3",
        "A7":  "A7.mp3",  "C8":  "C8.mp3",
      },
      baseUrl: "https://tonejs.github.io/audio/salamander/",
      onload: () => {
        audioReady = true;
        document.getElementById("audio-unlock").remove();
      },
    }).toDestination();

    sampler.volume.value = Tone.gainToDb(state.volume ?? 1.0);
    // 
});

async function initAudio() { /* no-op, unlock handled above */ }

// ── Play a chord slot ─────────────────────────────────────
async function playChord(slot) {
  await initAudio();
  if (!audioReady || !sampler) return;
  sampler.releaseAll();

  const notes = buildNoteStrings(
    slot.root,
    slot.chordType,
    slot.inversion,
    slot.octave ?? config.octave ?? 4
  );

  sampler.triggerAttack(notes, Tone.now() + 0.001);
}

// ── Stop all audio ────────────────────────────────────────
function stopAudio() {
  if (sampler) sampler.releaseAll(Tone.now() + 0.1);
}

// // ── Patch existing hooks ──────────────────────────────────
// window.addEventListener("load", () => {
//   const _originalConfirm = onConfirm;
//   window.onConfirm = function () {
//     _originalConfirm();
//     if (state.activeSlot === null) return;
//     const slot = state.slots[state.activeSlot];
//     if (!slot || !slot.root) return;
//     playChord(slot);
//   };

//   const _originalStop = onStop;
//   window.onStop = function () {
//     _originalStop();
//     stopAudio();
//   };
// });