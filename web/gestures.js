// ── gestures.js ───────────────────────────────────────────
// Finger extension detection + gesture recognition
// All gesture logic lives here; sketch.js calls detectGestures(results)

// ── Finger indices ────────────────────────────────────────
const FINGER_TIPS  = { thumb: 4, index: 8, middle: 12, ring: 16, pinky: 20 };
const FINGER_PIPS  = { thumb: 3, index: 6, middle: 10, ring: 14, pinky: 18 };
const FINGER_MCPS  = { thumb: 2, index: 5, middle: 9,  ring: 13, pinky: 17 };

// ── Is finger extended? ───────────────────────────────────
// For index/middle/ring/pinky: tip y < pip y (tip is higher than knuckle)
// For thumb: tip x further from palm centre than mcp (horizontal extension)
function isExtended(landmarks, finger) {
  if (finger === "thumb") {
    const tip  = landmarks[FINGER_TIPS.thumb];
    const mcp  = landmarks[FINGER_MCPS.thumb];
    const wrist = landmarks[0];
    // Thumb extends horizontally — compare x distance from wrist
    return Math.abs(tip.x - wrist.x) > Math.abs(mcp.x - wrist.x);
  }
  const tip = landmarks[FINGER_TIPS[finger]];
  const pip = landmarks[FINGER_PIPS[finger]];
  return tip.y < pip.y - 0.02;  // small threshold to avoid noise
}

function getExtendedFingers(landmarks) {
  return {
    thumb:  isExtended(landmarks, "thumb"),
    index:  isExtended(landmarks, "index"),
    middle: isExtended(landmarks, "middle"),
    ring:   isExtended(landmarks, "ring"),
    pinky:  isExtended(landmarks, "pinky"),
  };
}

// ── Right hand: Chinese number gestures 1–10 ─────────────
function detectRightHandGesture(landmarks) {
  const f = getExtendedFingers(landmarks);

  // Slot 1  — index only
  if (f.index && !f.thumb && !f.middle && !f.ring && !f.pinky) return 1;
  // Slot 2  — index + middle
  if (f.index && f.middle && !f.thumb && !f.ring && !f.pinky) return 2;
  // Slot 3  — index + middle + ring
  if (f.index && f.middle && f.ring && !f.thumb && !f.pinky) return 3;
  // Slot 4  — index + middle + ring + pinky
  if (f.index && f.middle && f.ring && f.pinky && !f.thumb) return 4;
  // Slot 5  — all five
  if (f.thumb && f.index && f.middle && f.ring && f.pinky) return 5;
  // Slot 6  — thumb only
  if (f.thumb && !f.index && !f.middle && !f.ring && !f.pinky) return 6;
  // Slot 7  — thumb + index
  if (f.thumb && f.index && !f.middle && !f.ring && !f.pinky) return 7;
  // Slot 8  — thumb + pinky
  if (f.thumb && !f.index && !f.middle && !f.ring && f.pinky) return 8;
  // Slot 9  — index + pinky
  if (f.index && !f.thumb && !f.middle && !f.ring && f.pinky) return 9;
  // Slot 10 — pinky only
  if (f.pinky && !f.thumb && !f.index && !f.middle && !f.ring) return 10;

  return null;  // no gesture recognised
}

// ── Left hand: L gesture (confirm/play) ──────────────────
function detectLeftHandGesture(landmarks) {
  const f = getExtendedFingers(landmarks);

  // L shape — index up, thumb out, others curled
  if (f.index && f.thumb && !f.middle && !f.ring && !f.pinky) return "confirm";

  return null;
}

// ── Both hands: stop gesture ──────────────────────────────
function detectStopGesture(leftLandmarks, rightLandmarks) {
  if (!leftLandmarks || !rightLandmarks) return false;
  const lf = getExtendedFingers(leftLandmarks);
  const rf = getExtendedFingers(rightLandmarks);
  const leftOpen  = lf.thumb && lf.index && lf.middle && lf.ring && lf.pinky;
  const rightOpen = rf.thumb && rf.index && rf.middle && rf.ring && rf.pinky;
  return leftOpen && rightOpen;
}

// ── Dwell timer state ─────────────────────────────────────
const dwell = {
  right:     { gesture: null, startTime: null },
  left:      { gesture: null, startTime: null },
  stop:      { active: false, startTime: null },
};

const DWELL_MS = 150;

// ── Main entry point — called every frame from sketch.js ──
function detectGestures(results) {
  if (!results || !results.multiHandLandmarks) return {};

  let leftLandmarks  = null;
  let rightLandmarks = null;

  // MediaPipe labels are from the camera's perspective (mirrored)
  // so "Left" in results = user's right hand
  for (let i = 0; i < results.multiHandLandmarks.length; i++) {
    const label = results.multiHandedness[i].label;
    if (label === "Left")  rightLandmarks = results.multiHandLandmarks[i];
    if (label === "Right") leftLandmarks  = results.multiHandLandmarks[i];
  }

  const now = Date.now();
  const confirmed = {};

  // ── Stop gesture (both hands) ───────────────────────────
  const stopDetected = detectStopGesture(leftLandmarks, rightLandmarks);
  if (stopDetected) {
    if (!dwell.stop.active) {
      dwell.stop.active    = true;
      dwell.stop.startTime = now;
    } else if (now - dwell.stop.startTime >= DWELL_MS) {
      confirmed.stop = true;
    }
  } else {
    dwell.stop.active    = false;
    dwell.stop.startTime = null;
  }

  // ── Right hand: slot selection ──────────────────────────
  if (rightLandmarks) {
    const g = detectRightHandGesture(rightLandmarks);
    if (g !== null) {
      if (dwell.right.gesture !== g) {
        // New gesture — reset timer
        dwell.right.gesture   = g;
        dwell.right.startTime = now;
      } else if (now - dwell.right.startTime >= DWELL_MS) {
        confirmed.slotIndex = g - 1;  // 0-indexed
      }
    } else {
      dwell.right.gesture   = null;
      dwell.right.startTime = null;
    }
    confirmed.rawRightGesture = g;  // for highlighting before dwell completes
  } else {
    dwell.right.gesture   = null;
    dwell.right.startTime = null;
  }

  // ── Left hand: confirm/play ─────────────────────────────
  if (leftLandmarks) {
    const g = detectLeftHandGesture(leftLandmarks);
    if (g === "confirm") {
      if (dwell.left.gesture !== "confirm") {
        dwell.left.gesture   = "confirm";
        dwell.left.startTime = now;
      } else if (now - dwell.left.startTime >= DWELL_MS) {
        confirmed.confirm = true;
      }
    } else {
      dwell.left.gesture   = null;
      dwell.left.startTime = null;
    }
  } else {
    dwell.left.gesture   = null;
    dwell.left.startTime = null;
  }

  return confirmed;
}