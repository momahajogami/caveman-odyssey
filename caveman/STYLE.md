# Homer Very Small — Style Guide

*For authors, collaborators, and anyone adding episodes.*

---

## What This Is

A retelling of Homer's Odyssey in extremely minimal English — for puppet shows, young children, and families. Each episode has a **read version** (web page) and a **print version** (puppet script, letter paper, Ctrl+P ready).

The language is the constraint. Every word must earn its place. When in doubt, cut.

---

## The Caveman Voice

### Core rules

- **Subject before verb. Verb before object.** No inversions, no subordinate clauses, no relative pronouns.
- **Present tense throughout.** Not "Telemakos walked" — "Telemakos walks."
- **Cut articles hard.** Not "the boat" — "boat." Not "a god" — "god." Only keep an article when removing it makes the line genuinely unclear.
- **No conjunctions except "and" and "but."** No "although," "however," "therefore," "because."
- **Repetition is good.** "Nestor old. Nestor wrong. Nestor sit down." The repetition is rhythm.
- **Proper names instead of pronouns when possible.** "Telemakos go. Telemakos not stop." Not "he goes, he doesn't stop."
- **Emphasis by sentence fragment.** "Very bad." "First time." "Just gone."
- **Greek spellings for all names.** Telemakos, Athena, Kalypso, Olympos, Ithaka, Aigisthos, Aithiopians. When in doubt, use the Greek form.

### The speeches are the structure

Homer is a series of speeches with almost no description in between. That structure is sacred here. Every speech in Homer gets a speech here — simplified, but present. Do not combine two characters' speeches into one. Do not cut a speech to a stage direction. The number of speeches and their sequence must be preserved.

What gets simplified is the language inside each speech, not the architecture of the scene.

### Emotions

Do not soften the weight of the story. Lean into the drama. Feel things deeply even with simple language. The Orestes story — father killed, son avenges him — is in there directly. That is right. Children can feel the weight of real things. Earn buy-in from intelligent adults. This is scaffold for real art.

Emotions show in the speaking, not in description. Athena's anger at Zeus's indifference is in what she says and how she says it — the repetition, the accusation, the contrast. Not in a stage direction that reads "angrily."

### What the voice is *not*

Not baby talk. Not silly. Not condescending. The grammar is stripped but the feelings are real and the stakes are real. Nestor's lesson about Orestes lands hard in caveman — maybe harder than in a fuller telling, because nothing cushions it.

### Good test

Read a line aloud. If it sounds like a telegram, it's probably right. If it sounds like a sentence, cut it down.

---

## Episode Structure

### Naming

Files follow the pattern `book-NN-slug.html` and `book-NN-slug-print.html`.

Slugs are short, plain English — what happens in the scene, not a literary title:

- `book-02-wakeup` — boy wakes up
- `book-02-council` — the island council
- `book-02-boat` — boy loads the boat

Episode titles on the index page can be more evocative: *Boy Wake Up*, *The Island Council*, *Old King Nestor*.

### Length

A read episode should take 3–6 minutes to read aloud. A print script should fit on two letter pages. If it runs longer, split it.

### Natural break points

Each episode needs one strong ending image — a moment that lands and closes. Examples so far:

- *He does not look back.* (boat departure)
- *Stranger is gone. Just gone.* (Athena departs)
- *Nestor watches from the shore for a long time.* (end of Book III)

Don't end on dialogue if you can end on a stage direction.

---

## The Read Page

### Structure

```
← back link          puppet script link →
h1 (chipsquirt, amber family)
.book-note (italic, gray — one line orienting the reader)
[scenes]
.footer
```

### Scene anatomy

```html
<div class="scene">
  <div class="speaker">NAME <span class="role">brief description</span></div>
  <div class="speech">
    <p>dialogue</p>
  </div>
</div>

<div class="stage">Stage direction in italics.</div>
```

### Stage directions

Italicized, set apart. Use as few as possible. Homer uses almost none — the speeches carry everything. A stage direction is justified only when something must happen that cannot be spoken: a transformation, an entrance, a departure, a silence. One sentence maximum. Cut the rest.

### Section breaks

`<div class="section-break">* * *</div>` — use sparingly. Only when there's a genuine scene change (time passing, location shift). Not between every exchange.

---

## The Print Page (Puppet Script)

### Structure

1. **Title block** — title, subtitle (`Book N — a puppet script — after Homer`)
2. **Cast list** — every puppet needed, one line each with a character note
3. **Scenes** — headed with `<div class="scene-head">`
4. **Dialogue** — two-column: name right-aligned in a fixed-width left column, speech in the right
5. **Puppet tips** — boxed section at the bottom, 4–6 practical tips

### Cast notes

One line per character. Tell the puppeteer what they need to *play*, not just who the character is.

- Good: `NESTOR — very old king, slow, enormous white beard, tells long stories`
- Bad: `NESTOR — king of Pylos`

### Puppet tips

These are the most useful part of the print script. Be specific and practical:

- Which moment is the laugh line, and how to play it
- Where to pause and why
- How to handle costume/prop swaps (same puppet, different hat)
- Where the emotional center of the scene is
- What the last image should feel like

---

## Color — Chipsquirt

All episode titles and h1 headers use **Chipsquirt** in **orbit mode** — per-letter color cycling through HSV space via golden-ratio Lissajous. The effect reads as a single color at a glance but rewards inspection.

### Current assignment

All episode h1 headers use the **amber** family (hue center 36°). This gives the whole project warmth and consistency.

The index page cycles all six families across episode titles in this order:
`amber → violet → forest → teal → magenta → slate`

### Color families

| Family  | Hue  | Character            |
|---------|------|----------------------|
| amber   | 36°  | Ancient, candlelit   |
| violet  | 268° | Nocturnal, mathematical |
| forest  | 140° | Earthy, patient      |
| teal    | 172° | Cool, oceanic        |
| magenta | 312° | Warm, pressured      |
| slate   | 215° | Formal, lapidary     |

### To tune a story's color

In each episode's `<script>` block, find `var fam = {...}` and replace with your chosen family's values. The color should feel right for the emotional register of that episode. Amber is the default and works for most scenes. Violet suits the divine/uncanny moments (Athena revealing herself, the eagle). Teal suits the sea.

---

## Visual Design (Warm Folio)

The design language is **Warm Folio**: a well-made book that happens to be on a screen.

| Property    | Value                            |
|-------------|----------------------------------|
| Background  | `#fdfaf5` — warm off-white, never pure white |
| Body type   | Georgia, 18px base               |
| Line height | 1.75 (read pages), 1.55 (print)  |
| Max width   | 680px (episodes), 720px (index)  |
| Rule color  | `#e0d8cc` — warm gray            |
| Body text   | `#1a1a1a`                        |
| Secondary   | `#888`, `#aaa`, `#bbb`           |

Prose stays plain. Color is reserved for structure — headers, navigation, Chipsquirt. Nothing competes with the text.

---

## Adding an Episode

1. Copy `episodes/book-02-council.html` → `episodes/book-NN-slug.html`
2. Copy `episodes/book-02-council-print.html` → `episodes/book-NN-slug-print.html`
3. Update title, `.book-note`, scenes, cast, puppet tips
4. Add a `<li>` block to `index.html` under the correct book heading
5. Commit and push — deploys automatically

---

## What We're Telling

The Odyssey is about someone trying to get home, and everyone who loves them trying to hold on until he does. The caveman voice strips it to that. Every episode should feel that stakes are real — even when the moment is funny (and many are), the longing underneath is genuine.

Telemakos's arc across Books I–III is the model: he begins passive and sad, and episode by episode — gets dressed, speaks at the assembly, argues with his nurse, sails away in the dark — he becomes someone. The voice stays simple throughout. The transformation is visible in the actions, not the words.

That's the template for every book to come.
