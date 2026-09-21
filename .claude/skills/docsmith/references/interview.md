# The structuring interview

This is the "grill me" step of docsmith. It runs after the digest and before the first
line of the doc. Its only job is to resolve how the document is *structured*: type,
sections, diagrams, scope, destination. It is not a content review and not a survey. A
grill asks one pointed, evidence-backed question at a time and digs on the answer until
nothing structural is ambiguous; a questionnaire asks the same ten things of every doc.

Contents

1. [Inputs: what you hold before the first question](#1-inputs)
2. [The opening move: outline, then question, same turn](#2-the-opening-move)
3. [How a question earns a turn](#3-how-a-question-earns-a-turn)
4. [The decision branches, in order](#4-the-decision-branches-in-order)
5. [Defaults per branch](#5-defaults-per-branch)
6. [Follow-ups inside a branch](#6-follow-ups-inside-a-branch)
7. [Mechanics: turns, the tool, deferrals, corrections](#7-mechanics)
8. [The ledger lives in the transcript](#8-the-ledger-lives-in-the-transcript)
9. [Stopping rule and cap](#9-stopping-rule-and-cap)
10. [Escapes](#10-escapes)
11. [Headless runs](#11-headless-runs)
12. [The Assumptions block](#12-the-assumptions-block)
13. [Sample transcript](#13-sample-transcript)

---

## 1. Inputs

Questions asked without these are generic, and generic questions are the failure mode
this file exists to prevent. Moves 1 and 2 of SKILL.md (ingest, then outline) produce all
of them; check each is in hand before the first question.

**The material inventory** (`references/ingest.md`, section 4), with a source id on every
item:

| Bucket | Holds | Used for |
|---|---|---|
| Directives | The user's own instructions from the invocation | `User` ledger rows before the first question; never asked |
| Facts | Versions, ports, names, exit codes, owners | Anchors; never asked about |
| Procedures | Ordered steps (install, deploy, rollback); `[unverified]` when only a chat states a step | Action sections; unverified steps are gap questions |
| Diagrammables | Candidate diagrams, each with a suggested Mermaid type (`references/diagrams.md`) | Diagram branch decides scope and placement, not detection |
| Figures | Candidate images to embed, real files the user supplied (`references/diagrams.md`, section 9) | Same branch as Diagrammables: decides which are embedded and where, not detection |
| Decisions | Choices the material records with their why, and rejected branches with a stated reason | Overview and How it works material; not contradictions |
| Terms | Canonical name -> aliases seen | Naming branch |
| Contradictions | Two sources disagree and the precedence in 4.6 cannot settle it | One question each |
| Gaps | What the doc type needs and the material lacks, including work the chat deferred ("leave it, come back to it") | Ask, TODO, or omit (4.7); deferred work is a candidate "Open items" section |
| Reader signals | Who the material says will read the doc, at what level | Audience branch |
| Sources | Source id, kind, date, contribution; redactions made | A `Material` ledger row per redaction (a live token pasted in a chat); never a question |

**The coverage map** (`references/ingest.md`, section 4): each skeleton section for the
doc type -> the inventory ids that feed it, or `none`. Sections at `none` and sections
with far more material than the rest are where section-level questions come from.

**The skeleton for the doc type.** Read the slot table and the doc-type matrix in
`references/structure.md` (sections 1 and 2) and start from them. The user asked for "the
same core structure, changed where necessary"; the interview honours that only if the
outline is expressed as deviations from the standard shape, so every question targets a
deviation.

**The draft outline hypothesis.** Type, title, ordered sections (one line each saying
what fills it and from where), the diagram set (flow, Mermaid type, position), and the
destination. Prefix deviations from the skeleton: `+` added, `-` dropped, `~` renamed or
merged. Mark each open decision inline with its specific uncertainty: `(? with or
without log-write nodes)`, `(? merge into 4)`, not a bare `(?)`.

**The destination check.** Resolve the path (the invocation's, else the skeleton's
default for the type) and check whether it exists and how big it is, with `ls`/Read.
Put the result in the outline header. This is the only irreversible decision in the
interview, and it cannot be asked or defaulted correctly without looking.

**Invocation instructions are ledger rows before the first question.** "Make this a
runbook, no diagrams, write to docs/" is three `User` rows. Challenge one only when the
material plainly contradicts it, and say why in the question.

## 2. The opening move

In one turn: the outline as text, then the first question immediately after it
(AskUserQuestion call, or a lettered question in plain chat). Do not end the turn on the
outline alone; that costs a round trip and stalls a headless run.

Show the outline before asking because people cannot answer "who is the audience?" in a
vacuum but react instantly to a concrete proposal that is slightly wrong. One correction
("this is a runbook, drop Architecture") pre-empts several questions. The `?` marks and
the `+/-/~` prefixes keep a good default from becoming silent anchoring; attack the most
consequential `?` first, not the easiest.

Keep it under ~25 lines:

```
Draft outline — Guide (Guide skeleton). Destination docs/observer-guide.md: does not exist.
  1. Overview          pre-execution guardrail; one action string in, exit 0/1/2 out
  2. How it works      flowchart: deny → protected path → confirm → allow (? with or without log-write nodes)
  3. Prerequisites     a caller that passes one action string (observer.sh usage line)
  4. Walkthrough       H3 Install and smoke-test · H3 Add a rule · H3 Read the log
  5. Reference         three rule tables, one per array in observer.sh; the log line format
- 6. Troubleshooting   dropped: no errors recorded anywhere in the material
~ 7. Open items        Limitations slot: log rotation; settings.json hook wiring, proposed in chat and never built, so prose only (? include, or omit from a current-behaviour doc)
  Resolved from material: README.md is not protected (chat reverses it, later wins); token in chat redacted.
+ added  - dropped  ~ merged/renamed, relative to the Guide skeleton. (? ...) = open.
One question at a time. Say "go" whenever you want the defaults shown here.
```

## 3. How a question earns a turn

A question earns a turn when the answer would change the outline (sections, order, type,
destination), the diagram set (which flows are drawn, with which Mermaid type), a
diagram's scope (which nodes, participants or states are in it), or which supplied
images are embedded as figures and where. Use this exact test in
section 9 as the stopping rule; nothing else qualifies, and a question that only changes
wording is fixed faster in review.

Every question is derived the same way: *observation* (what you saw, where; quote it
when short) → *tension* (why the material alone cannot settle it) → *question* with
options → *consequence* (what each option does to the outline).

- Bad: "Who is the audience for this doc?"
- Good: "The Slack thread addresses 'whoever is on-call'; the ticket says 'onboarding
  material for new hires'. Which reader? On-call: Prerequisites shrinks to a link and the
  decision flow leads. New hires: Prerequisites explains what a guardrail is and the flow
  moves after the concepts."

The bad version fits any doc. The good one fits only this doc and takes three words to
answer. Never ask what the material already answers: if the script header says
`Exit 0 = allow, 1 = block, 2 = needs human`, the exit codes are a `Material` row.

## 4. The decision branches, in order

Each branch constrains the next: audience decides type, type decides scope, scope
decides sections, sections decide diagrams; contradictions, gaps and naming come after.
Destination is the exception: if the target exists with real content, ask the overwrite
question first, because it is the only irreversible one. Skip any branch the invocation,
the material or an earlier answer settled, and record why in the ledger rather than ask
filler.

### 4.1 Audience and prior knowledge

- "The README draft says 'assumes familiarity with Terraform'; the chat spends four
  messages explaining what a state file is. Terraform-literate reader, or the one from
  the chat? That decides whether section 2 is a link or a page."
- No signal at all (common for a design chat plus a script): ground in the outline
  instead. "Nothing in the material names a reader. The outline assumes someone wiring
  the observer into their own agent loop. If it is for whoever maintains the script,
  the Walkthrough shrinks to a smoke test and How it works leads with the design
  rationale."

### 4.2 Doc type

The canonical type list, the cues for each type and the per-type skeleton live in
`references/structure.md`, section 2. Settle the type before touching sections, because
it fixes the skeleton. A type the invocation names is already a `User` row; challenge it
only when the material cannot fill that type's action spine (a How-to with no procedure,
a Runbook with no symptom→action content).

- "The material is 80% one procedure (deploy) and 20% architecture. That is a How-to
  with a short 'How it works' preamble, not a Guide. Agree, or should architecture lead?"
- "You asked for a README but the material covers only incident response, no install or
  usage. Runbook skeleton, or README with a runbook section?"

### 4.3 Scope boundary

What is deliberately out, and what is parked. A doc that does not say what it excludes
gets extended into a wiki.

- "The chat drifts into the billing service in the last third. Out, with one line under
  'Not covered', or in?"
- "The chat parks log rotation and hook wiring for later. Short 'Open items' section
  listing them (Recommended: readers ask about missing pieces), or leave them out of a
  doc that describes current behaviour?"

### 4.4 Section-level structure

Merge, split, drop, rename, always against the outline already shown and within the five
operations `references/structure.md` section 6 allows: merges only into their whitelisted
targets, renames only from the vocabulary, never a reorder.

- "Limitations would hold one line ('does not catch `rm -fr`'). Fold it into Overview's
  closing 'what it does not do' paragraph (Recommended), or keep a one-line section?"
- "The chat's design rationale (why exit 2 exists, why bash and not Python) fills six
  lines. In Overview, or in How it works next to the flowchart?"

### 4.5 Diagrams and figures: scope and placement

Detection and type selection are done (`references/diagrams.md`). When the material
clearly contains a flow, do not ask whether to draw it; ask about scope or placement.
Ask about inclusion only for a marginal candidate, and prefer skipping over guessing.

- "The decision flow has three ordered checks and three exits, and every exit writes a
  log line. One flowchart with the checks as diamonds. Fold the log write into the exit
  labels ('Log BLOCK, exit 1', 4 nodes, Recommended) or give each write its own node
  (7 nodes)?"
- "The chat mentions a retry loop in the uploader but no states or limits. I would
  rather skip a state diagram than draw one from guesses. Skip, or do you know the states?"

Supplied images (the `Figures` bucket) follow the same branch: which are embedded and
where, never whether one *could* be reconstructed as Mermaid instead (`references/diagrams.md`,
section 9 already settled that a real image always wins over a redraw). Ask when a
supplied image could plausibly sit in more than one section, or when its role — read for
its text versus embedded as a figure — is not obvious from the material.

- "You attached `dashboard.png`. It could illustrate How it works (what the dashboard
  looks like) or the first Walkthrough step (what you see after setup). Which, or both?"
- "`error-dialog.png` both shows a specific error worth seeing and contains a stack trace
  worth quoting. Embed it as a figure in Troubleshooting *and* quote the stack trace in
  prose (Recommended), or one or the other?"

### 4.6 Contradictions

Apply this precedence before asking: (1) the artifact in the repo (code, config, script
header); (2) an explicit "we changed / decided X" statement in chat; (3) within one
transcript, the later statement (exports often lack timestamps, so position is the
signal); (4) memory and notes. A settled contradiction is a `Material` row and one line
in the outline ("timeout: 45 s per config.yaml, newer than chat") that the user can veto
for free; it is not a confirm question. A chat proposal the artifact never implemented
is not a contradiction: file it under Gaps as discussed-only work (`references/ingest.md`
section 3), or under Decisions only when a reason for rejecting it was stated, and raise
it at most once, in the scope branch.

- Reversal, resolved without asking: "add README.md to protected paths" then "hmm no
  scratch that" → `Material: README.md not protected (later statement in transcript)`.
- Ask only when precedence fails: "Two people in the same thread, same day, give the
  rollback steps in opposite orders and the script has no rollback. Which is current? I
  will not write both."

### 4.7 Gaps

Three tiers, so the doc is not a field of placeholders:

- The doc type requires it (README: how to run it; How-to: every step): ask if the user
  plausibly knows it offhand, else one visible `TODO` saying what is missing.
- The doc type could merely use it (Troubleshooting with no recorded fixes): omit the
  section; do not TODO it.
- A doc carries at most three TODOs (`scripts/lint_doc.py` errors above that); if it would
  carry more, drop sections. Only TODOs that survive are listed in the Assumptions block.
  Never fabricate.

- "Nothing says how to run the tests, and a README without that is incomplete. Do you
  know the command, or leave a marked TODO?"

### 4.8 Naming

- "Script comment says 'observer', chat says 'guardrail', ticket says 'gate'. Headings
  use 'observer' (the artifact's name), others mentioned once. Object?"
- "'Job', 'task' and 'run' are interchangeable in the transcript. One term, or three things?"

### 4.9 Destination and overwrite

Default: never replace or edit an existing file that has real content without a `User`
row. A trivial existing file (a title-only stub, a template placeholder, fewer than ~10
non-blank lines with no fact the material lacks) is replaced without a question, and the
delivery message says so; nothing is lost. Otherwise write to a sibling `<name>.new.md`
(`README.new.md` next to `README.md`; `docs/<slug>.new.md` next to a colliding
`docs/<slug>.md`) and say so in the output and the Assumptions block. Silent overwrite of a README with content is the mistake the
user notices first.

- "`README.md` exists with 120 lines, including a Roadmap section nothing in the material
  covers. Write `README.new.md` beside it for you to merge (Recommended), merge my
  sections into it and keep Roadmap, or replace it?"
- "`docs/deploy.md` exists with its own Prerequisites. Write `docs/deploy.new.md`
  (Recommended), or merge my Prerequisites into it and keep the rest?"

## 5. Defaults per branch

The cap, an escape and a headless run all apply the same defaults, so the outcome is
deterministic rather than invented on the spot. Each unanswered branch becomes a
`Default` row using this table.

| Branch | Default |
|---|---|
| Audience | The reader named in the material; else the reader the type presumes (README: about to use it; How-to: doing the task; Runbook: on-call; Guide: learning it; Onboarding: joining the team) |
| Doc type | The invocation's; else from the mix: one procedure → How-to; symptom→action → Runbook; concepts plus procedures → Guide; otherwise README |
| Scope | Everything about the named subject; digressions get one line under "Not covered"; deferred work gets a short "Open items" section |
| Sections | The skeleton; drop a section with nothing to fill; merge two whose content overlaps by more than half |
| Diagrams | Every clear flow, at the granularity the material supports, with shared side steps (logging, metrics) folded into the terminal labels as the canonical shapes do; marginal candidates skipped |
| Figures | Every supplied image with a section that discusses it, embedded there; an image with no discussing section, or only described and never attached, left out |
| Contradictions | The precedence in 4.6 |
| Gaps | The tiers in 4.7 |
| Naming | The name the artifact uses; alternatives mentioned once |
| Destination | The path asked for; a trivial stub there is replaced; a file with real content gets a sibling `<name>.new.md`, never a replacement |

## 6. Follow-ups inside a branch

This is what makes it a grill. Two cases earn a follow-up before advancing:

- The answer conflicts with the material or an earlier ledger row. Name the conflict:
  "You said on-call engineers, but the material has no symptom→action content. What
  would on-call do with this doc, or is it really for whoever integrates it?"
- The answer opens a sub-decision: "new hires" → "Do they know what a PreToolUse hook is?
  If not, section 3 needs a paragraph the material does not have; TODO or you dictate it?"

Cap follow-ups at two per branch. A follow-up counts toward the question cap.

## 7. Mechanics

**One question per turn by default.** Each answer can change the next question; a batch
asked before the first answer is half wasted. Batch up to three only when the answers
are independent and in the same branch (three naming choices; three contradictions from
the same source pair). A batch counts as one question toward the cap. Never batch across
branches.

**AskUserQuestion, when available.** Match its schema or the first question burns a retry:

- `header`: a short branch label of at most 12 characters: "Audience", "Doc type",
  "Scope", "Sections", "Diagram", "Conflict" (the contradictions branch), "Gaps",
  "Naming", "Overwrite". Never the prose branch name; "Contradictions" is too long.
- `question`: the observation, the tension and the anchor. This is where the evidence goes.
- `options`, 2–4: `label` is the choice in 1–5 words, recommended one first with
  "(Recommended)" in the label; `description` is the one-line consequence for the
  outline. If you have no recommendation, go back to the material.
- Do not add an "Other" option; the tool supplies free text itself. Inspect that free
  text for deferrals and escapes (below), not just for answers.
- One call may carry up to four questions; docsmith puts at most three in it (the batch
  rule above).

**Plain chat fallback.** Same content: lettered options, recommended first and marked,
"reply with a letter or a correction."

**Per-question deferral versus whole-interview escape.** "You decide", "either", "skip",
"next", "whatever" in reply to one question mean: apply that question's recommended
option, log a `Default` row, continue. Do not end the interview on a shrug. Whole-interview
escapes are covered in section 10. "Skip" alone is per-question unless it is the whole
reply to the outline or comes with "the rest" or "the interview".

**Corrections that are not answers.** "Actually this should be two docs" or "drop the
diagram" is a structural decision: record it, re-plan, resume from the branch it affects.

**New material mid-interview.** A pasted file or a second chat is not an answer to the
pending question. Digest it, update the inventory and the `?` marks, note the change in
one line, and resume from the earliest branch it affects.

## 8. The ledger lives in the transcript

There are no hidden working notes; anything not in the transcript is lost by the next
turn. So the acknowledgment of each answer *is* the ledger row, printed on one line
before the next question:

```
#4 Diagram scope, decision flow → logging folded into exit labels (User: "keep it to the checks")
#5 Timeout → 45 s (Material: config.yaml newer than chat)
#6 Test command → TODO (Default: not in material, user unsure)
```

The third field is the provenance: `User`, `Material` (resolved without asking, with the
evidence), or `Default` (assumed). The full table is assembled from these lines once,
when writing the Assumptions block; `Default` rows are exactly its content.

**Deltas and re-shows.** When an answer changes the outline materially (section added,
removed, merged, split, reordered; diagram added, removed, retyped, or rescoped; type or
destination changed), append the delta to the ledger line with `+`, `-`, `~`:

```
#3 Scope → migration tool out (User)   - section 8; + "Not covered" line
```

Show the full outline again only once, at the end of the interview, and only if any
delta was recorded since it was last shown; otherwise print "Outline unchanged.
Writing." Re-showing after every answer buries the questions and trains the user to skim.

## 9. Stopping rule and cap

Stop when no open item would change the outline, the diagram set or a diagram's scope
(the section 3 test). Walk the branches once more; if each is answered, resolved by
material, or would only produce a `Default` row that changes wording, you are done.

Cap at 10 questions (8 for a short How-to, 12 for a multi-flow Guide), batches and
follow-ups included. The first three questions settle most of the structure; the value
of each further question falls fast and an uncapped interview makes users answer
carelessly. At the cap, list what is open with the default from section 5 for each, and
proceed:

```
Cap reached. Applying defaults:
- Retry loop diagram → skipped (no states in material)
- Term for job/task/run → "job" (the script's name)
Both go in the Assumptions block.
```

## 10. Escapes

The rule is intent, not a word list: any statement that the user cannot or will not
answer, wants defaults, or is in a hurry ends the interview. Illustrations: "go", "just
write it", "use defaults", "stop asking", "skip the rest", "skip the interview", "nobody
is around to answer questions", "I can't answer questions, just do it", `--no-grill`.
Such a statement in the invocation itself skips the interview before the first question.
Both escapes and deferrals can arrive through the tool's free-text field.

On escape: stop, without one last question. Apply the section 5 default to every
unresolved branch and log each as a `Default` row. If the outline was never shown, show
it once (no questions) before writing, so the structure is visible before the full doc.
Then write, with the Assumptions block.

## 11. Headless runs

Decide before the first question, from signals you can see now. Treat the run as
headless when any holds:

- The system prompt or launching context says you are a subagent, worker, CI job,
  routine, orchestrated step, or in print/non-interactive mode.
- The invocation says nobody can answer or asks for no questions (section 10 phrasing).
- AskUserQuestion is absent and there is no sign a human turn will follow: the invocation
  arrived as a complete work order (material, destination, "write it") with no
  conversation around it.

A plain human chat without AskUserQuestion is still interactive when the user has been
conversing across turns or asked for the interview; ask with lettered options there.
When the tool is absent and you are unsure, do not end the turn on a question. Write the
doc with defaults in the same turn and put the questions you would have asked as a
checklist inside the Assumptions block, so a human can answer them in a second pass. A
headless run must never end on an unanswered question.

Headless runs ask nothing but still do everything else: show the outline in the output
before the doc, log `Material` and `Default` rows, apply section 5, write, append the
Assumptions block.

## 12. The Assumptions block

Drafting metadata should not sit as a top-level heading in a README that may be public.
Append it at the end of the doc as a block GitHub collapses natively (blank line after
the summary is required for the Markdown inside to render):

```
<details>
<summary>Assumptions made while drafting</summary>

- Audience: assumed engineers integrating the observer; if for maintainers, lead with How it works.
- Destination: README.md existed with real content, so this was written to README.new.md; merge and swap it in when reviewed.
- Open items section included (log rotation, hook wiring); delete if the doc should describe current behaviour only.
- Unasked (headless run): should each log write be its own node instead of part of the exit label?

Delete this block after review.

</details>
```

Keep the blank line before `</details>`; `scripts/lint_doc.py` rejects the block without it.

One bullet per `Default` row: the decision, what was assumed, what would change it. The
same treatment suits a Sources section meant for the author rather than the reader.

## 13. Sample transcript

The user pasted a Slack thread, `deploy.sh` and a Notion page about a service called
"ingest" and asked for "a guide". Abbreviated; option descriptions shown inline.

```
docsmith: Draft outline — Guide (Guide skeleton). Destination docs/ingest.md: does not exist.
    1. Overview          what ingest does (Notion, para 1)
    2. How it works      sequence: webhook → queue → worker → warehouse (? with or without the retry loop)
    3. Prerequisites     AWS creds, kubectl (deploy.sh header) (? overlaps 5)
    4. Walkthrough       H3 Deploying: the 9 steps in deploy.sh · H3 Rolling back: Slack 2026-07-14, msgs 31–38
  ~ 5. Configuration     Reference slot: env vars from deploy.sh
  - 6. Troubleshooting   dropped: three errors named, fixes for two (? keep with a TODO)
  Resolved from material: REGION=eu-west-1 (deploy.sh, newer than the Notion page).
  One question at a time. "go" for the defaults shown.

Q1 [Audience] Notion opens "for the platform team"; the Slack thread is product
   engineers asking how to deploy. Which reader?
   a) Product engineers (Recommended) — Prerequisites stays, section 2 stays short
   b) Platform team — Prerequisites drops, section 2 grows, add "Internals"
user: a
  #1 Audience → product engineers (User)

Q2 [Doc type] Material is mostly one procedure. Guide as drafted, or How-to "Deploy
   ingest" with Overview as preamble?
   a) Guide (Recommended) — Rolling back stays its own Walkthrough stage
   b) How-to — Rolling back becomes step 10 of Steps, Troubleshooting appended
user: guide
  #2 Doc type → Guide (User)

Q3 [Scope] Slack msgs 40–55 discuss the new schema migration tool. In scope?
   a) Out (Recommended) — one "Not covered" line at the end of Overview; nothing explains it
   b) In, as the one extra section — mostly TODO
user: out
  #3 Scope → migration tool out (User)   + "Not covered" line in Overview

Q4 [Diagram] Request path has four hops and one retry (Slack msg 22: "worker retries
   the warehouse write 3x"). Draw the retry?
   a) With retry (Recommended) — one `loop` block; it is what the thread asks about
   b) Without — simpler
user: with
  #4 Diagram scope → retry loop drawn (User)   ~ sequence diagram rescoped

Q5 [Gaps] Troubleshooting: three errors, fixes for two; "QueueDepthExceeded" has none.
   a) Keep the section, that error as a TODO (Recommended) — reader sees it is known
   b) Drop the section — only solved errors
user: keep it, and add "page the platform team" as the interim step
  #5 Troubleshooting → kept, TODO + interim action (User)   + section 6 restored

Q6 [Sections] Prerequisites (3) and Configuration (5) share 5 of 8 env vars. Where does
   the table live?
   a) Configuration holds all 8; Prerequisites lists only the 3 required (Recommended) — one lookup table
   b) Both list all 8 — each section stands alone, at the cost of duplication
user: a
  #6 Sections → Prerequisites required-only, Configuration all 8 (User)   ~ 3 and 5 rescoped

Q7 [Naming] Slack says "ingestor", Notion "ingest service", deploy.sh "ingest".
   a) "ingest" (Recommended)   b) "ingest service"   c) "ingestor"
user: go
  Stopping on "go".
  #7 Naming → "ingest" (Default: the artifact's name)
  #8 Destination → docs/ingest.md (Default: path free)

  Outline changed (Q3, Q4, Q5, Q6):
    1. Overview           + "Not covered: schema migration tool" line
    2. How it works       ~ sequence diagram with retry loop
    3. Prerequisites      ~ required env vars only
    4. Walkthrough        H3 Deploying · H3 Rolling back
  ~ 5. Configuration      ~ full variable table
  + 6. Troubleshooting    QueueDepthExceeded: TODO + interim action
  Writing.
```

Seven questions, one escape, nine ledger rows (six `User`, two `Default`, one
`Material` for the region, resolved without asking), and an outline the user saw twice.
That is the whole interview.
