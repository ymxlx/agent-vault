# Gamp EMT Simulator — Patient Asset Generation Prompt Package

Image-generation prompt package for producing the complete patient asset set for the
Gamp-code-emt-simulator. Built for any modern image model (Midjourney, DALL·E,
Stable Diffusion / Flux, Imagen). Use the **Global Style Block** as the prefix of every
prompt so all assets stay visually consistent, then append the per-asset prompt.

> **Status note:** the `Gamp-code-emt-simulator` repository was not reachable from this
> session (private repo outside the session's access scope), so scenario, style, and
> format assumptions below are stated explicitly in §1 and are trivial to swap once the
> repo's real art direction is confirmed. Everything else is repo-independent.

---

## 1. Assumptions to confirm against the repo

| Parameter | Assumed value | Change if repo says otherwise |
|---|---|---|
| Platform | 2D web game (HTML/JS) | — |
| Patient view | Top-down, patient supine (lying on back), full body | Side view if the sim uses a bed/stretcher side camera |
| Art style | Semi-realistic medical-illustration style: clean vector-like linework, soft cel shading, muted clinical palette | Match existing UI art |
| Scenario | Motorcycle collision (blunt + penetrating multi-system trauma) — the richest single scenario for teaching DCAP-BTLS | Any repo-defined scenario |
| Patient identity | Adult male, early 30s, medium build, medium skin tone (generate skin-tone variants, §6) | — |
| Output | PNG with transparent background, 2048×2048 master, layered/overlay-friendly | — |

---

## 2. Global Style Block (prefix for EVERY prompt)

```
Professional medical-training illustration for an EMS education simulator.
Clean semi-realistic style: precise anatomical proportions, smooth vector-like
linework, soft cel shading, neutral diffuse lighting, muted clinical color
palette (desaturated reds, clinical blues #4A7B9D, gauze white #F4F1EC, skin
midtone #C68B59). Top-down orthographic view of an adult male patient, early
30s, short dark hair, medium build, lying supine with arms slightly away from
the torso. Educational and respectful tone: injuries are clinically accurate
and clearly readable but never gratuitous or gory. Flat transparent background,
no floor, no shadows cast outside the body silhouette, no text, no watermark,
no UI elements baked in. Consistent character across all images.
```

**Global negative prompt** (for models that accept one):

```
photorealistic gore, excessive blood pooling, horror aesthetic, anime style,
cartoon exaggeration, extra limbs, deformed hands, wrong finger count,
duplicated face, text, captions, labels, watermark, signature, background
scenery, dramatic lighting, sexualized framing, nudity
```

---

## 3. Scenario trauma map (motorcycle collision — what the injuries are and where)

Canonical injury set, chosen so every DCAP-BTLS finding type appears at least once and
each maps to a distinct treatable gameplay interaction:

| # | Region | Injury (clinical) | Visual description for the model | Gameplay treatment |
|---|---|---|---|---|
| T1 | Right forehead / temple | 4 cm laceration with minor active bleeding | Clean-edged diagonal cut above right eyebrow, thin trail of bright red blood toward the ear, slight swelling around the wound | Direct pressure → dressing |
| T2 | Right clavicle | Closed fracture with deformity | Visible asymmetric bump and bluish-purple bruising over the right collarbone, right shoulder slightly slumped | Sling / immobilize |
| T3 | Left chest wall | Blunt contusion, suspected rib fractures | Large irregular reddish-purple bruise over left ribs 6–9, slight paradoxical depression of the segment | O₂ + position, monitor |
| T4 | Abdomen | Seatbelt-pattern contusion | Faint diagonal red-purple band of bruising from right shoulder line across to the left hip | Assess, monitor for rigidity |
| T5 | Right forearm | Road rash (deep abrasion) | Wide patch of raw, pink-red abraded skin from elbow to wrist with embedded gray gravel specks, glistening but not dripping | Irrigate → dressing |
| T6 | Left mid-thigh | Open (compound) femur fracture | Deformed, angulated thigh; 3 cm of off-white bone tip visible through a torn wound; controlled dark-red bleeding around the opening; lower leg rotated outward | Tourniquet/pressure → traction splint |
| T7 | Lips / nail beds (state variant) | Cyanosis (hypoxia state) | Bluish-gray tint on lips and fingernails, pale waxy facial skin | O₂ administration reverses |
| T8 | Whole body (state variant) | Decompensated shock | Pale ashen skin overall, fine sweat sheen on forehead, slack facial muscles | Treat causes; failure state if ignored |

Severity color logic for readability at game scale: **bright red = active bleeding
(act now)**, **purple-blue = closed injury (assess)**, **pink-raw = abrasion (clean)**.
Keep these hues distinct and colorblind-checked (§7).

---

## 4. Asset prompts

Each prompt = Global Style Block + the text below.

### A1 — Base patient, clothed (scene-start state)
```
Full-body supine patient wearing a torn dark-gray motorcycle jacket (unzipped,
right sleeve shredded over the forearm) and black riding pants torn at the left
mid-thigh revealing the wound area, one boot missing. Eyes open, conscious,
tense pained expression, jaw clenched. Injuries visible through torn clothing:
forehead laceration with thin blood trail (T1), raw road-rash forearm through
the shredded sleeve (T5), deformed left thigh with visible bone tip through
torn pants (T6). Chest rises naturally; pose anatomically relaxed but guarded.
```

### A2 — Exposed assessment asset (professional clinical version)
The “Expose” step of the primary survey: clothing cut away by EMS, patient in plain
fitted dark briefs/compression shorts only. **Clinical, anatomically accurate,
respectful — a medical-textbook figure, not a stylized character.**
```
Same patient, clothing removed for trauma assessment: bare torso, arms and legs
exposed, wearing only plain black compression shorts. All injuries from the
trauma map clearly visible and clinically accurate: 4 cm forehead laceration
with minor bleeding; asymmetric right clavicle deformity with focal bruising;
large purple-red contusion over the left lower ribs; faint diagonal seatbelt
bruise across the torso; deep road-rash abrasion on the right forearm with
embedded gravel; open left femur fracture with 3 cm of exposed bone, angulated
thigh, controlled dark bleeding. Skin otherwise pale with light sweat sheen.
Neutral medical-illustration treatment of the body, textbook anatomy, no
dramatization. This is the master assessment image: every injury must be
individually distinguishable at 25% zoom.
```

### A3 — Injury overlay decals (one prompt per decal, transparent sprites)
Generate each injury as an isolated overlay so the engine can compose states:
```
Isolated injury decal on transparent background, matching the established
style and skin midtone, drawn on a small patch of skin that fades to full
transparency at the edges, top-down angle consistent with a supine patient:
[SWAP IN: T1 forehead laceration / T2 clavicle deformity bruise / T3 rib
contusion / T4 seatbelt bruise band / T5 forearm road rash / T6 open femur
fracture wound]. No body outline, no background, decal only.
```

### A4 — Consciousness / physiology state variants (heads + full body)
```
(a) Conscious-alert: eyes open, focused, pained grimace.
(b) Conscious-distressed: eyes half closed, mouth open as if groaning, brow knotted.
(c) Unresponsive: eyes closed, face fully slack, head rolled slightly to the side.
(d) Cyanotic (hypoxia): variant of (c) with bluish-gray lips and fingertips.
(e) Shock: variant of (b) with ashen pale skin overall and sweat sheen.
Generate as same-framing variants of the A2 exposed master so they can be
hot-swapped without sprite jumping.
```

### A5 — Treated / intervention states (the reward feedback layer)
```
Same exposed patient with interventions applied, each as a separate image or
overlay, equipment drawn accurately per current EMS practice:
(a) White roller-gauze head dressing covering the forehead wound, neat wrap.
(b) Rigid cervical collar, correctly sized, chin seated.
(c) Triangular-bandage sling immobilizing the right arm against the chest.
(d) Orange windlass tourniquet high on the left thigh, strap tensioned, time-tab blank.
(e) Traction splint applied to the left leg, leg straightened and aligned.
(f) Non-rebreather oxygen mask with inflated reservoir bag, elastic over ears.
(g) Sterile dressing taped over the forearm road rash.
(h) "Packaged" final state: all of the above plus an unfolded foil emergency
blanket covering torso to knees — the visual win state.
Clean professional application: treated states must read as calm and orderly
versus the chaos of untreated states.
```

### A6 — Face portrait set (dialogue / feedback UI)
```
Bust portrait of the same patient, slight high angle as if the responder leans
over him, transparent background, six expressions: alert-pained, anxious,
groggy, calm-relieved (post-treatment), unconscious, cyanotic-unconscious.
Identical framing and scale across all six.
```

### A7 — Body-map UI silhouette (injury tagging interface)
```
Flat minimalist front-view human body silhouette of the same proportions,
single clinical blue (#4A7B9D) on transparent background, limbs slightly
separated for tap-target clarity, no facial features, subtle thin-line joints
at neck, shoulders, elbows, wrists, hips, knees, ankles. Companion version
with the eight trauma-map zones as slightly darker filled regions.
```

---

## 5. Single consolidated "master prompt" (quick one-shot version)

For a fast all-in-one generation (e.g., concept board before asset production):

```
Professional medical-training illustration, semi-realistic vector style with
soft cel shading, muted clinical palette, transparent background, no text.
Asset sheet for an EMS training game: an adult male motorcycle-crash patient,
early 30s, lying supine, shown in three rows. Row 1: clothed in torn riding
gear, conscious and pained. Row 2: exposed for assessment in black compression
shorts, showing a 4 cm forehead laceration, deformed bruised right clavicle,
purple rib contusion, diagonal seatbelt bruise, gravel-flecked road rash on
the right forearm, and an open left femur fracture with visible bone —
clinically accurate, readable, never gory. Row 3: fully treated — head
dressing, cervical collar, arm sling, thigh tourniquet, traction splint,
non-rebreather oxygen mask, foil blanket. Consistent character, top-down
orthographic angle, textbook-respectful tone.
```

---

## 6. Technical & pipeline specs

- **Format:** PNG-32 with alpha; master renders at 2048×2048, export game sizes 1024 / 512 / 256.
- **Consistency:** lock a character reference (seed / reference-image / `--cref`) from the approved A2 master before generating variants; regenerate variants from it, never from scratch.
- **Layering:** body base + injury decals (A3) + intervention overlays (A5) compose every game state; avoid baking injuries into treated images where a decal can do it.
- **Registration:** all full-body assets share identical canvas framing so overlays align pixel-perfect; portraits (A6) share their own fixed framing.
- **Naming:** `patient_<state>_<region>_<variant>.png`, e.g. `patient_exposed_thigh_t6_untreated.png`, `patient_treated_full_packaged.png`.
- **Palette discipline:** blood `#A4282B` (active) vs bruise `#5E4B8B`–`#7B6FA0` vs abrasion `#D97B66`; reserve pure saturated red for "needs immediate action" only.

---

## 7. Gamification review checklist (clean, polished, correctly gamified patient)

**State machine coverage** — every gameplay state has a distinct visual:
- [ ] Untreated / assessed (highlighted) / being-treated / treated / deteriorated for each of T1–T6
- [ ] Physiology layers (conscious, distressed, unresponsive, cyanotic, shock) combinable with any treatment state
- [ ] Win state (packaged patient, A5-h) visually rewarding — calm, orderly, warm-toned vs. the cold chaos of the start state

**Readability at game scale:**
- [ ] Every injury identifiable at 25% zoom and distinguishable from its neighbors
- [ ] Severity color logic consistent (red = act now, purple = assess, pink = clean)
- [ ] Treated overlays visually "quiet" so attention flows to remaining untreated injuries

**Interaction design:**
- [ ] Each injury zone ≥ 44 px tap target at smallest supported resolution; hit zones match decal positions
- [ ] Body-map silhouette zones (A7) correspond 1:1 with trauma map T1–T8
- [ ] Hover/selected variants achievable by tint or outline (no extra renders needed)

**Educational integrity:**
- [ ] Injuries anatomically plausible for the stated mechanism of injury (motorcycle collision)
- [ ] Interventions drawn per current EMS practice (collar sizing, tourniquet placement high-and-tight, NRB reservoir inflated)
- [ ] Exposed asset reads as clinical/textbook — appropriate for classroom use, ESRB Teen-equivalent tone

**Accessibility & inclusivity:**
- [ ] Blood/bruise/abrasion hues pass deuteranopia and protanopia simulation checks
- [ ] Skin-tone variant set generated from the same master (light `#E8C39E`, medium `#C68B59`, deep `#7C4F2B`) — regenerate with the character reference, changing only skin tone
- [ ] Optional female and older-adult patient variants reuse the identical trauma map and overlay registration

**Polish pass:**
- [ ] No baked-in text, shadows, or background remnants in any export
- [ ] Edges anti-aliased against transparency (no white fringing)
- [ ] All variants framed identically — flip through the full state stack and confirm zero sprite jump
