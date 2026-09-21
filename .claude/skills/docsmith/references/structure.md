# Document structure and style contract

This file is the contract every docsmith output follows. Read it in full before the first heading is written; consult specific sections again while drafting. The point of a fixed contract is recognizability: a reader who has seen one docsmith document should be able to navigate the next one without thinking, even if it is a runbook for a different team on a different stack.

## Contents

1. [The core skeleton](#1-the-core-skeleton)
2. [Doc-type matrix](#2-doc-type-matrix)
3. [Style contract (GitHub-flavored Markdown)](#3-style-contract-github-flavored-markdown)
4. [Where diagrams and figures go](#4-where-diagrams-and-figures-go)
5. [Decisions the interview settles](#5-decisions-the-interview-settles)
6. [Adaptivity rules](#6-adaptivity-rules)
7. [Quality bar checklist](#7-quality-bar-checklist)
8. [Worked example: a How-to](#8-worked-example-a-how-to)

---

## 1. The core skeleton

Every document is built from the same ordered list of slots. A slot is **CORE** (always present) or **ADAPTIVE** (present only when its trigger, stated in the table, is met). One rule governs both: **a section is never emitted empty or padded.** No "TBD", no "Coming soon", no heading followed by nothing. A visible `TODO` is not padding when it says exactly what is missing; the interview's gap rule allows at most three, each listed in Assumptions. A CORE slot with no supporting material shrinks to one honest paragraph and gets an Assumptions entry; an ADAPTIVE slot with no material does not exist. The collapsed CORE form looks like this, and it is a legitimate finished section:

```markdown
## Quick start

Nothing runs yet. The observer exists as a design (see [How it works](#how-it-works)); the planned entry point is `harness/observer.sh "<action>"`. This section will grow steps once the script lands.
```

The order is fixed. Slots may be dropped, never reordered, with one exception noted in section 2 for Runbooks. Only headings in the vocabulary of section 6 are used.

| # | Slot | Class | Purpose | What goes in it, and the trigger for ADAPTIVE slots |
|---|------|-------|---------|------------------------------------------------------|
| 0 | **Title + tagline** | CORE | Name the thing, say what it does. | `# Name` then a `>` blockquote of one sentence (3.1). |
| 1 | **At a glance** | CORE | Ten-second skim. | **No heading.** 3–6 bold-labelled bullets directly under the tagline (and badges), before the first H2 (3.2). |
| 2 | **Contents** | ADAPTIVE | Navigation for long, linear docs. | `## Contents`, hand-built after the body is final (3.3). On for Guide and Onboarding; off for README (GitHub renders its own outline); otherwise on only past ~150 lines. |
| 3 | **Overview** | CORE | Problem, approach, boundaries. | The why, the what, and what it does *not* do. Design decisions mined from chats ("exit 2 means needs-human because…") live here or in How it works, never in FAQ. |
| 4 | **How it works** | ADAPTIVE | Mental model before mechanics. | Architecture, flow, lifecycle, decision logic. Home of diagrams (section 4). Trigger: the material describes a mechanism with more than two moving parts. |
| 5 | **Prerequisites** | ADAPTIVE | Stop the reader before they fail three steps in. | Tools, versions, accounts, permissions, secrets, prior state. Trigger: any step assumes something the reader must already have. When installing is the only prerequisite, this slot is renamed *Installation*. |
| 6 | **Getting going** | CORE | The reader does the thing. | Numbered steps (3.6), renamed per type: *Quick start*, *Walkthrough*, *Steps*, *Procedure*, *Getting started*. If the material describes something not yet built, use the collapsed form above and prefer README or Guide over How-to or Runbook. |
| 7 | **Usage** | ADAPTIVE | Representative invocations beyond first success. | *Usage* or *Examples*: the two-to-five calls or snippets a library or CLI reader copies most. Trigger: the material shows more than one representative invocation that is neither the first-success path nor a lookup table. |
| 8 | **Reference** | ADAPTIVE | Look-up material. | Config keys, flags, env vars, API surface, file layout; tables by default (3.7). Trigger: at least three look-up rows exist. |
| 9 | **Troubleshooting** | ADAPTIVE | Known failures to fast fixes. | Table of Symptom / Likely cause / Fix. Trigger: the material yields three or more rows; one or two become a `> [!TIP]` on the step they concern. Chat transcripts are rich in these; mine them. |
| 10 | **Limitations & known issues** | ADAPTIVE | Prevent misplaced trust. | One line each, link to a tracking issue when one exists. Work the material defers or plans ("leave it, come back to it", the next phase) also lives here, under the *Open items* or *Roadmap* rename. Trigger: the material names at least one. |
| 11 | **FAQ** | ADAPTIVE | Questions readers asked. | Only questions a *reader of this document* asked or would plausibly ask, taken near-verbatim from an issue, thread or chat. Questions the author asked while designing the thing are not FAQ. Trigger: three or more such questions. |
| 12 | **Contributing / Development** | ADAPTIVE | Lower the cost of the next PR. | Build, test, lint, submit. Trigger: the repo is open to contribution or the material documents a dev loop. |
| 13 | **Related docs** | ADAPTIVE | Link outward. | *See also* list of docs the reader needs next. Trigger: the material names at least two such docs (common in Guide and Onboarding). |
| 14 | **Sources & provenance** | CORE | Audit trail. | Every input consumed and what it contributed (3.9). An HTML comment for a README, a collapsed `<details>` block otherwise. |
| 15 | **Assumptions** | ADAPTIVE | Make silent defaults loud. | Trigger: a default was taken unconfirmed, or a CORE slot was filled by inference (3.10). Always a collapsed `<details>` block, after Sources. |
| 16 | **License** | ADAPTIVE | State the terms. | One line plus link. README only, and only when a license file or statement is in the material. Never guess. |

**Title rule.** The title is the name the reader will search for: the repo for a README, the task for a How-to, the system for a Runbook, the team for Onboarding. When repo name and artifact name differ (`Autonomous-AI-Harness` versus `observer.sh`), a README takes the repo name and mentions the artifact in the tagline.

**One extra H2** may be added between How it works and Getting going when the material has a substantial concept (ten or more lines of real content) that fits no slot: "Security model", "Data retention", "Pricing". Name it with a plain noun phrase. Wanting two is the signal that one of them is Reference or Overview content.

---

## 2. Doc-type matrix

Pick the type in the interview. Cues in the material: "readme" / repo root / "what is this" → README. "Learn", "understand", "from scratch", multi-session scope → Guide. "How do I", a single verb-object goal, "steps to" → How-to. "On-call", "incident", "if it breaks", "rollback", "page" → Runbook. "New hire", "first week", "getting up to speed", "the team" → Onboarding. **When cues conflict and nobody can be asked**, the destination decides: writing to a repo's `README.md` → README; no destination → README for a codebase, How-to for a single stated goal, Guide otherwise. Record the choice in Assumptions.

| Slot | README | Guide | How-to | Runbook | Onboarding |
|------|--------|-------|--------|---------|------------|
| 2 Contents | off | on | off unless >150 lines | off | on |
| 3 Overview | 1–3 paragraphs | may run long | 1 paragraph: goal + end state | 2 sentences: what breaks, blast radius | "what this team owns" |
| 4 How it works | on when diagrammable | on, primary home of diagrams | only if a step is unexplainable without it | on, **after Procedure** | on, system map |
| 5 Prerequisites | on if install needed (*Installation*) | on | on | *Access you need*, as a checklist | *Accounts and access* |
| 6 Getting going | *Quick start*: 3–7 steps to first success | *Walkthrough*: H3 per stage | *Steps*: the doc's spine | *Procedure*: see the Runbook paragraph below | *Getting started*: H3s *Day one*, *First week*, *First month* as the material supports |
| 7 Usage | on if >1 invocation shown | off (stages cover it) | off | off | off |
| 8 Reference | on if config/CLI exists | on, at the end | off unless a step needs a lookup | short, renamed *Escalation* when it holds contacts | *Who to ask* table |
| 9 Troubleshooting | on at 3+ rows | on at 3+ rows | on at 3+ rows | **merged into Procedure** as decision branches | on at 3+ rows |
| 10 Limitations | on if known | on if known | rarely | *When this does not apply* | off |
| 11 FAQ | on if asked | on if asked | off | off | on if asked |
| 12 Contributing | on if open to contribution | off | off | off | *How we work* |
| 13 Related docs | on if 2+ links | on | off | on if 2+ links | on |
| 14 Sources | HTML comment | `<details>` block | `<details>` block | `<details>` block | `<details>` block |
| 16 License | on if in material | off | off | off | off |
| **Tone** | Confident, welcoming, present tense | Patient, teaching, explains the why | Terse, imperative, zero theory | Calm, clipped, no adjectives | Warm, orienting, links outward |
| **Ceiling** | 250 lines | 500 lines | 200 lines | 200 lines | 400 lines |
| **Diagram default** | 1 topology or central flow; a request sequence only if the project has a central one | 2–4 across stages | 1 flow or sequence, only if it clarifies | 1 decision flowchart before step 1, plus a state diagram when the operated thing has named states | 1 system map, plus 1 ownership map if the material has it |

**Runbook order, stated once:** Overview, Access you need, Procedure, How it works, Escalation, Sources. This is the only permitted reorder; on-call readers need the procedure before the theory. Inside Procedure: every step that can fail says how to tell; steps whose outcome changes the next step carry a decision branch ("If the log shows `HUMAN`, go to step 6"); any irreversible step is followed by a `<details><summary>Rollback for step N</summary>` block; the last step is always **Verify and close**. At a glance carries *Severity* and *Impact*.

Ceilings force prioritization; they are not targets. A How-to that does its job in 45 lines is finished. When material exceeds the ceiling, move detail into `<details>` or Reference before cutting steps.

---

## 3. Style contract (GitHub-flavored Markdown)

### 3.1 Title and tagline

```markdown
# confmgr

> A single-binary CLI that keeps one config file in sync across every machine you own.
```

One H1 per document. The tagline is one sentence with no marketing adjectives ("blazing", "powerful"). It answers "what does it do" and, when it can, "for whom".

### 3.2 At-a-glance block

```markdown
- **What:** Config sync for dotfiles and app settings, over any Git remote.
- **For:** Developers with more than one machine.
- **Status:** Stable, v2.x. Breaking changes only on major versions.
- **Needs:** Go 1.22+ to build, or a release binary. Git 2.30+.
- **Start here:** [Quick start](#quick-start)
```

No heading; the bullets sit under the tagline (and badges) and before the first H2. Bold label, colon, one line. Labels, used only when the material supports them: **What, For, Status, Needs, Start here, Takes** (time; How-to and Runbook), **Severity, Impact** (Runbook), **Owner, On-call, Last verified** (internal docs). Three minimum, six maximum. A Status or version you cannot trace is omitted, not guessed.

### 3.3 Contents and anchors

Build the list last, from the final H2s (H3s only inside Reference and Walkthrough). GitHub builds anchors by lowercasing the heading, dropping every character that is not a letter, number, space, hyphen or underscore, then replacing spaces with hyphens. Punctuation is dropped, not converted, so `## Sources & provenance` becomes `#sources--provenance` (two hyphens: the ampersand vanished and left two spaces), and `## config_path` keeps its underscore. Duplicate headings get `-1`, `-2` suffixes. Check every link against this rule; a broken TOC link is the most visible defect a doc can have.

### 3.4 Heading depth

H1 once. H2 for slots. H3 for stages inside a slot. H4 only inside Reference for items that need their own anchor. Never H5; if you need it, a table or `<details>` block fixes the structure. An H2 that only groups H3 stages gets one orientation line before the first H3 ("Four stages, about twenty minutes:"), never nothing.

### 3.5 GitHub alerts

| Alert | Use when | Not for |
|-------|----------|---------|
| `> [!NOTE]` | Context that changes how the reader interprets the next paragraph. | General asides (plain prose). |
| `> [!TIP]` | A shortcut, an easier path, a way to verify success. | Anything the reader must do. |
| `> [!IMPORTANT]` | Required to succeed at all: a mandatory flag, an order dependency. | Damage warnings. |
| `> [!WARNING]` | Risk of data loss, downtime, or an irreversible action. | Emphasis. |
| `> [!CAUTION]` | Security exposure, or harm to people or to others' production. | Anything WARNING covers. |

At most one alert per roughly forty lines, never two in a row. Inside a numbered procedure an alert is indented to the content column of the step it concerns (three spaces under `1.`), never placed at column 0 between items, because an unindented block ends the list.

### 3.6 Numbered steps

Every step has a bold imperative one-liner, an action, and an expected result. The action is a fenced, language-tagged block when the reader types or pastes something, and a plain line when it is a UI action, a conversation or a read ("Open **Settings > API keys** and copy the new key."). Never fence prose.

````markdown
1. **Initialise the vault.**
   ```bash
   confmgr init --remote git@github.com:you/dotfiles.git
   ```
   You should see `Vault created at ~/.confmgr` and a new empty commit on the remote.
````

The expected-result line is what makes a procedure followable by a stranger, so it may only state what you can trace: an output string read in the code or a log, an exit code, a file that now exists, a state you can name. Do not run the scripts you are documenting to find out: most write a log, a file or a network call as a side effect (the ingest reference's `--help` rule is the only exception), and the printed strings are in the code anyway. When the output is unknown, say what is knowable ("exits 1 and appends a `BLOCK` line to `observer.log`") rather than quoting invented text. A command or flag you have only seen discussed in a chat never becomes a step; describe it in prose as planned and list it in Assumptions.

One action per step. Sub-steps are a nested ordered list indented under the parent (`   1.` under `1.`; GitHub renders them as i., ii.), used only when the parent is meaningless without them. A step that branches becomes two steps or a small table, not a paragraph of conditionals. Optional steps carry `*(optional)*` after the bold line. Anything that belongs to a step (fence, alert, diagram, expected-result line) is indented to the step's content column so the list is never broken.

### 3.7 Tables versus lists, and `<details>`

Use a table for reference-type content with three or more rows and two to five columns: flags, keys, env vars, error codes, symptom/cause/fix. Use a bulleted list for one column or fewer than three items. Never put a paragraph in a cell; if a cell needs more than a sentence, the content belongs in prose with a link from the table.

Wrap in `<details><summary>…</summary>` anything long (over ~30 lines), optional or off the main path: full example configs, raw logs, alternative-OS instructions, the "why" behind a runbook step, rollback procedures. The summary is a noun phrase naming the contents ("Full `config.toml` with every key"), never "Click to expand". Leave a blank line after `<summary>` and before `</details>`, or GitHub will not render the Markdown inside.

### 3.8 Code fences, voice, emoji, badges, links, terminology

**Code fences.** Always tag the language: `bash`, `sh`, `powershell`, `python`, `go`, `rust`, `ts`, `js`, `json`, `yaml`, `toml`, `ini`, `sql`, `diff`, `mermaid`, `text` (output, logs). Untagged fences are a defect. In `bash`/`sh` fences show no `$` prompt so the command copies cleanly; output goes on the expected-result line or in a `text` block. A `console` fence with `$` prompts is allowed only to interleave several commands with their output as an illustration, and it is then never the copyable command.

**Voice.** Second person, present tense, active: "You run the installer and it writes…". Contractions are fine. Name the tool; "we" only in Onboarding, where "we" is the team.

**Emoji.** None in headings, bullets or tables. A single status glyph in At a glance is tolerated only when the repo's existing docs already use that convention. Alerts already carry the visual signal emoji are reached for.

**Badges.** Only badges backed by something in the material: an actual workflow file, an actual published package, an actual license file. Maximum four, on one line under the tagline. When nothing is verifiable, no badges.

**Links.** Descriptive link text, never "here". Relative paths for files in the same repo, written from the document's own directory because that is how GitHub resolves them (`[observer.sh](../harness/observer.sh)` from a doc in `docs/`; `[observer.sh](harness/observer.sh)` only from the root README), so links survive forks; verify each path exists from where the document lives. External link text names the destination. Bare URLs only inside Sources & provenance.

**Terminology.** Spell the tool, commands, flags, file paths and exit-code names exactly as the material does, everywhere, including in diagram labels. Pick one form on first use (`observer.sh`, not "the Observer script" in one place and "observer" in another). Inconsistent naming is the most frequent visible defect after broken anchors.

### 3.9 Sources & provenance

Always produced, because it is what lets the user trust and regenerate the doc. Its form is an interview decision (section 5) with a default per type. For a **README** it is an **HTML comment block opening with `<!-- docsmith provenance`, at the end of the body** (before the Assumptions block and any License line): the README is the project's public face, a transcript list there is noise to strangers, and the comment is invisible on GitHub yet survives regeneration. For **every other type** it is a **collapsed `<details>` block at the end of the body**: readers of a guide or runbook do want to know where a claim came from, and the block costs nothing until clicked. The user can ask for a fully visible `## Sources & provenance` section instead (internal docs where freshness matters). All three forms hold the same lines:

```markdown
<details>
<summary>Sources &amp; provenance</summary>

- harness/observer.sh (read 2026-09-18): rule lists, exit codes, log format.
- Chat transcript (assistant and date not given; pasted): rationale for exit code 2, the needs-human flow.
- https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts: alert syntax.
- Interview answer: audience is contributors, not end users.
- README.md as it existed before this run (one line): project name only.

</details>
```

For a README, the same bullets sit between `<!-- docsmith provenance` and `-->`. Links the user supplied as citations (papers, upstream docs) are not provenance: they go into the Related docs slot under the heading *Further reading*, one line of description each, because the user placed them to be kept visible.

One line per input, in the order consumed. Label chats as chats; give assistant and date only when the material states them. An existing file you were asked to replace is a source: list it, and preserve any section of it the user did not ask to drop. When a chat describes *intended* rather than *verified* behaviour, mark it in the body ("planned, per design discussion") and here. When a transcript and the code disagree, the code wins and the transcript's position is not mentioned; when two transcript positions disagree and no code settles it, the later one wins and the change is noted in Assumptions. Never list a source you did not read.

### 3.10 Assumptions

Two triggers: (a) a structural or factual default was taken without the user confirming it, which is always the case in a non-interactive run and in an interactive run whenever the user said "go" or "skip" before a decision point; (b) a CORE slot was filled by inference rather than material. Assumptions are always reported to the user in chat as well. In the document they are a collapsed `<details>` block directly after Sources, for every doc type: collapsed so drafting metadata does not read as a section of a public README, visible on click so a reviewer who was not around for the interview can still find and answer them. Each bullet names the assumption, the reason, and how to change it in terms of the interview question, not a flag, because no flag syntax exists unless SKILL.md defines one. Questions a headless run would have asked go in as an "Unasked" bullet each:

```markdown
<details>
<summary>Assumptions made while drafting</summary>

- Treated as a **How-to** because the material centres on one goal ("rotate the key"). Re-run docsmith and answer *Guide* at the doc-type question for a teaching version.
- Audience assumed to be **operators who already run confmgr**; Prerequisites therefore omit installation.
- **Status** in At a glance is inferred from tags in the repo; no release notes were in the material.
- The `--force` behaviour is described from a chat transcript, not from code; verify before relying on it.
- Unasked (headless run): should the fleet script get its own section rather than a `<details>` block?

Delete this block after review.

</details>
```

The blank line before `</details>` is not optional (3.7); `scripts/lint_doc.py` rejects the block without it.

### 3.11 Figures (real images)

A Figure is either a generated Mermaid diagram (3.9's neighbor concept, detected and drawn per the diagrams reference) or a real image the user supplied — a screenshot, a photo, an existing architecture picture. Detection, worthiness-equivalent judgement and asset handling for a supplied image are the diagrams reference's job (section 9); this section fixes how one looks in the Markdown, which is identical for both kinds:

```markdown
The dashboard groups jobs into three columns by status:

![Job dashboard with three columns: Queued, Running, Failed, each showing a job count](images/job-dashboard.png)

*Figure: the job dashboard as captured 2026-09-20; column order matches the state machine in [How it works](#how-it-works).*
```

Alt text is required and descriptive, never `![image]` or `![screenshot]` — the same rule 3.8 gives links ("descriptive text, never 'here'") applies to what a reader sees when the image does not load. The italic caption line follows the same convention a diagram's caption does (section 4) and shares its figure-numbering sequence when the doc has more than one Figure of either kind. Placement, budget and the "never fabricate" boundary are section 4's and the diagrams reference's; only a Mermaid diagram is generated, so only a Mermaid diagram needs the anti-fabrication rules — a supplied image is embedded as-is or not at all.

---

## 4. Where diagrams and figures go

Detection and construction belong to the diagrams reference; this section fixes placement and framing so the two agree. Everything here applies equally to a Mermaid diagram and a supplied image embedded as a Figure (3.11) — both are visual material that sits next to the prose it illustrates.

- A diagram or figure sits **immediately before the prose that walks through it**, never after and never in an appendix.
- Lead in with one sentence ending in a colon ("The observer evaluates every action in three passes:"), then the `mermaid` fence or the `![alt](path)` image, then an italic caption line directly under it: `*Figure 1: Observer decision flow. Exit codes 0, 1 and 2 map to allow, block and needs-human.*` Number figures only when the doc has more than one and the prose refers to them by number; a diagram and a supplied image share one numbering sequence.
- The walk-through prose uses the diagram's node labels, or the figure caption's terms, **verbatim**. If the prose needs a term the diagram lacks, add it to the diagram or drop it from the prose.
- Natural homes: **How it works** for topology, lifecycle, state and data-model diagrams, and for a supplied architecture or screenshot image; a specific **step** in Getting going for a sequence diagram of what that step triggers, or a screenshot of what that step produces (lead-in, fence or image and caption indented to the step's content column); **Procedure** in a Runbook for the decision flowchart, before step 1.
- One diagram or figure per H2 unless the section genuinely describes two independent mechanisms. A diagram never replaces numbered steps; it explains them.
- When the diagrams reference reports "nothing diagrammable" and no supplied image earns a place, How it works is prose only, and that is correct. An invented "User → Tool → Output" drawing is worse than none, and an image dumped in with no prose that discusses it is worse than leaving it out.

---

## 5. Decisions the interview settles

These are the structural choices this contract leaves open. The grill-me phase asks about each one only when the material makes it a real question (the cue), and takes the default when the user says "go" or cannot be asked. Every interview question should map to one of these rows, which is what keeps the interview about structure rather than a generic questionnaire.

| Decision | Default | Ask when (cue in the material) |
|----------|---------|--------------------------------|
| Doc type | Section 2 tie-break | Cues for two or more types are present. |
| Primary reader and what they already have | Inferred from the material's own audience | The material addresses both end users and contributors, or never names a reader. Drives Prerequisites depth and Overview length. |
| Borderline ADAPTIVE slots | Include at the threshold, drop below it | A slot has exactly the threshold amount (three rows, two links, one limitation). |
| The one extra H2 and its name | None | A ten-line-plus concept fits no slot. |
| Rename choice | The first vocabulary entry for the type | Two vocabulary entries fit equally ("Architecture" versus "Decision flow"). |
| Which mechanism gets the diagram | The budget rule (diagrams reference, section 2) and its per-type table (section 3) | Several candidates and a one-diagram budget. |
| Which supplied images become figures, and where | Embed one per section that discusses it; skip an image no section discusses (diagrams reference, section 9) | A supplied image could plausibly go in more than one section, or its role (read for text vs. embedded figure) is unclear. |
| Sources form | Per 3.9: HTML comment for a README, `<details>` block otherwise | The user has said the doc is internal (visible section) or wants a README's provenance shown. |
| Badges and emoji opt-in | Off | The repo's existing docs use them. |
| Existing file handling | Trivial stub: replace and say so. Real content: write `<name>.new.md` beside it | A file with real content exists at the destination. Asked first, because it is the only irreversible decision. |
| Length versus ceiling | Move detail into `<details>` | The material exceeds the ceiling by more than a third. |

---

## 6. Adaptivity rules

The skeleton stays recognizable because only five operations are allowed, each with a trigger.

| Operation | Trigger | Constraint |
|-----------|---------|------------|
| **Drop** | The slot's trigger in section 1 is not met. | ADAPTIVE slots only. CORE slots collapse to one honest paragraph plus an Assumptions entry. |
| **Add** | A ten-line-plus concept fits no slot. | One extra H2, between How it works and Getting going. |
| **Merge** | The source slot would have fewer than three rows or lines. | Only these merges: Prerequisites → first step of Getting going; Limitations → last paragraph of Overview ("What it does not do"); Troubleshooting → Procedure as decision branches (Runbook); FAQ → Troubleshooting when every question is a failure; Related docs → a closing line of Overview. |
| **Rename** | The doc type or material has a more specific noun. | Only from the vocabulary below. |
| **Split** | Getting going exceeds ~12 steps. | Into H3 stages inside the same H2. Never into multiple H2s; the reader loses the spine. |

Heading vocabulary:

| Slot | Allowed headings |
|------|------------------|
| Overview | Overview · Why this exists · What this is |
| How it works | How it works · Architecture · Under the hood · Decision flow |
| Prerequisites | Prerequisites · Installation · Before you begin · Access you need · Accounts and access |
| Getting going | Quick start · Walkthrough · Steps · Procedure · Getting started |
| Usage | Usage · Examples |
| Reference | Reference · Configuration · Commands · Options · API · Escalation · Who to ask |
| Troubleshooting | Troubleshooting · Common problems · If something goes wrong |
| Limitations & known issues | Limitations · Known issues · Limitations & known issues · When this does not apply · Open items · Roadmap |
| Contributing / Development | Contributing · Development · How we work |
| Related docs | Related docs · See also · Further reading |

Every other heading is fixed. The vocabulary is short on purpose: a reader who learns these synonyms has learned the whole system.

---

## 7. Quality bar checklist

Run this over the finished draft. Fix, do not annotate. The first group is mechanical; if `scripts/lint_doc.py` exists in the skill, run it instead of checking by eye. The second group needs judgement.

**Mechanical**

1. Exactly one H1; the tagline blockquote follows it; At a glance has 3–6 labelled bullets and no heading.
2. Sections appear in skeleton order (Runbook order per section 2 is the only exception); headings come from the vocabulary.
3. No heading is followed by nothing or directly by another H2; an H2 grouping H3s has its orientation line.
4. No placeholder text: TBD, "coming soon", "lorem", "[insert]", a bare "…" standing in for content; at most three `TODO`s, each saying what is missing and listed in Assumptions.
5. Every code fence has a language tag; no `$` prompt inside `bash`/`sh` fences; no H5.
6. Alerts: none consecutive, none more often than once per ~40 lines, each indented into its step when inside a list.
7. Every `](#…)` link resolves under the anchor rule (3.3); every relative file path exists in the repo.
8. Tables have 2–5 columns and no paragraphs in cells; every `<details>` has a descriptive summary and blank lines inside.

**Judgement**

9. Every numbered step has a bold imperative line, an action (fenced only when typed), and an expected result that is traceable, not invented.
10. No invented output strings, commands, flags, badges, licenses, versions, dates or URLs. Everything either traces to a listed source or sits in Assumptions; chat-derived "planned" behaviour is marked in the body.
11. Every diagram has a lead-in, a caption and prose that reuses its node labels; no diagram exists that the diagrams reference did not find. Every embedded figure has descriptive alt text, a lead-in and a caption; no figure was redrawn as Mermaid, and no Mermaid diagram duplicates a figure already shown.
12. Terminology is consistent: one spelling per tool, command, path and code name across prose, tables and diagrams.
13. Voice is second person, present tense; no "we" outside Onboarding; no emoji in headings, bullets or tables.
14. Length is within the ceiling, and got there by moving detail into `<details>` or Reference, not by deleting steps.
15. Sources lists every input consumed, in the visibility the interview chose; Assumptions exists exactly when 3.10's triggers fired, and the user was told the assumptions in chat.
16. Read once as the intended reader: can they succeed without opening another file? If not, what is missing goes in, not in a footnote.

---

## 8. Worked example: a How-to

The subject is generic (a CLI with a config file) so that the style, not the content, is what you take from it. Notice the terse Overview, the step pattern with traceable results, the alert indented inside its step, the `<details>` for the optional path, and provenance as a collapsed block at the end because this is a How-to, not a README.

````markdown
# Rotate the confmgr API key

> Replace the API key confmgr uses to reach the remote, without losing local changes.

- **For:** Operators who already run confmgr 2.x on the affected machine.
- **Takes:** About five minutes. No downtime for other machines.
- **Needs:** Shell access to the machine and a new key from the remote's settings page.

## Overview

confmgr reads its key from `~/.confmgr/config.toml` and caches a session token for one hour. Rotating means writing the new key, invalidating the cached token, and confirming a sync succeeds. Unsynced local edits stay in the working tree throughout.

## Steps

1. **Check for unsynced changes.**
   ```bash
   confmgr status
   ```
   You should see `Working tree clean` or a list of modified files. Either is fine; the rotation does not touch them.

2. **Write the new key.**
   ```bash
   confmgr config set remote.api_key "$NEW_KEY"
   ```
   The command prints `Updated remote.api_key` and rewrites `config.toml` with mode `0600`.

3. **Invalidate the cached session token.**
   ```bash
   rm ~/.confmgr/session.json
   ```
   No output. The next sync logs in fresh with the new key.

   > [!WARNING]
   > Do not run `confmgr reset` here. It discards local edits as well as the token.

4. **Verify with a sync.**
   ```bash
   confmgr sync
   ```
   You should see `Authenticated as <you>` followed by `Up to date` or a push summary. An `HTTP 401` means the key was pasted with a trailing newline; repeat step 2 with the value quoted.

<details><summary>Rotating on every machine at once with the fleet script</summary>

`scripts/rotate-all.sh` loops over the hosts in `fleet.txt` and runs steps 2–4 over SSH. It stops at the first failure and prints the host name.

```bash
NEW_KEY=... scripts/rotate-all.sh fleet.txt
```

</details>

<details>
<summary>Sources &amp; provenance</summary>

- cmd/config.go, internal/session/cache.go (read 2026-09-18): config path, token TTL, file mode, printed strings.
- Chat transcript (assistant and date not given; pasted): the trailing-newline 401 gotcha.
- scripts/rotate-all.sh (read 2026-09-18): fleet loop behaviour.

</details>
````

What to notice: about forty lines, one alert, no theory beyond the two sentences the steps need, every result traceable to a file that was read, and a reader could hand this to a colleague who has never seen confmgr's source.
