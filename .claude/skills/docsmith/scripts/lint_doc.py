#!/usr/bin/env python3
"""Lint a docsmith document against the mechanical checks in references/structure.md
section 7. Standard library only, Python 3.8+.

Usage: python3 lint_doc.py DOC.md [MORE.md ...] [--type readme|guide|howto|runbook|onboarding]
                           [--repo-root DIR]
       python3 lint_doc.py --selftest
Exit 0 when clean (warnings allowed), 1 when any file has an error, 2 on usage error.

It checks shape, not meaning: heading vocabulary and order, the tagline and at-a-glance
block, empty sections, placeholders, fence tags, alert placement, anchors, relative links,
table widths and <details> blocks. Mermaid syntax is check_mermaid.py's job. The judgement
half of the checklist (traceable results, terminology, voice) is still read by eye.
"""
import os
import re
import sys

VOCAB = {  # slot -> allowed H2 headings, from structure.md sections 1 and 6
    2: ["Contents"],
    3: ["Overview", "Why this exists", "What this is"],
    4: ["How it works", "Architecture", "Under the hood", "Decision flow"],
    5: ["Prerequisites", "Installation", "Before you begin", "Access you need", "Accounts and access"],
    6: ["Quick start", "Walkthrough", "Steps", "Procedure", "Getting started"],
    7: ["Usage", "Examples"],
    8: ["Reference", "Configuration", "Commands", "Options", "API", "Escalation", "Who to ask"],
    9: ["Troubleshooting", "Common problems", "If something goes wrong"],
    10: ["Limitations", "Known issues", "When this does not apply", "Open items", "Roadmap", "Limitations & known issues"],
    11: ["FAQ"],
    12: ["Contributing", "Development", "How we work"],
    13: ["Related docs", "See also", "Further reading"],
    14: ["Sources & provenance"],
    15: ["Assumptions"],
    16: ["License"],
}
HEADING_SLOT = {h.lower(): slot for slot, hs in VOCAB.items() for h in hs}
RUNBOOK_ORDER = {4: 6.5}                      # How it works comes after Procedure in a runbook
ALERT = re.compile(r'^(\s*)> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]')
LIST_ITEM = re.compile(r'^\s*(\d+[.)]|[-*+])\s+')
FENCE = re.compile(r'^(\s*)(`{3,}|~{3,})\s*(\S*)')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
PLACEHOLDER = re.compile(r'\bTBD\b|\bFIXME\b|\bXXX\b|coming soon|lorem ipsum|\[insert\b|\[placeholder\]', re.I)
TODO = re.compile(r'\bTODO\b')
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
SHELL = ("bash", "sh", "shell", "zsh", "console")
BADGE = re.compile(r'^\s*(\[!\[|!\[|<(a|img|p|div|picture)\b)')   # badge, logo or centred-html lines
GENERIC_SUMMARY = re.compile(r'^(click to expand|expand|details|more|show more|see more)\.?$', re.I)
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿⭐⭕✅❌]')


def anchor_of(text):
    """GitHub's heading -> anchor rule: strip formatting, lowercase, drop punctuation, spaces to hyphens."""
    t = re.sub(r'`([^`]*)`', r'\1', text)
    t = re.sub(r'\*\*?|__?', '', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = t.strip().lower()
    t = re.sub(r'[^\w\s-]', '', t)
    return re.sub(r'\s', '-', t)


def parse(text):
    """Return (lines, in_fence flags, fences) where fences = [(open_line, lang, [body lines])]."""
    lines = text.splitlines()
    in_fence = [False] * len(lines)
    fences, open_fence = [], None
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if open_fence is None:
            if m:
                open_fence = (i, m.group(2), m.group(3))
                fences.append([i, m.group(3), []])
                in_fence[i] = True
        else:
            in_fence[i] = True
            if m and m.group(2)[0] == open_fence[1][0] and len(m.group(2)) >= len(open_fence[1]) and not m.group(3):
                open_fence = None
            else:
                fences[-1][2].append(line)
    return lines, in_fence, fences


def lint_text(text, path="doc.md", doc_type=None, repo_root=None):
    errors, warnings = [], []
    err = lambda n, msg: errors.append("%s:%d: error: %s" % (path, n + 1, msg))
    warn = lambda n, msg: warnings.append("%s:%d: warn: %s" % (path, n + 1, msg))
    lines, in_fence, fences = parse(text)
    prose = [(i, l) for i, l in enumerate(lines) if not in_fence[i]]

    # 1. fences: language tags, $ prompts
    for open_line, lang, body in fences:
        if not lang:
            err(open_line, "code fence without a language tag")
        elif lang in ("bash", "sh", "shell", "zsh"):
            for j, b in enumerate(body):
                if re.match(r'^\s*\$\s', b):
                    err(open_line + 1 + j, "'$ ' prompt inside a %s fence; drop it so the command copies cleanly" % lang)

    # 2. headings
    headings = [(i, len(m.group(1)), m.group(2)) for i, l in prose for m in [HEADING.match(l)] if m]
    h1s = [h for h in headings if h[1] == 1]
    if len(h1s) != 1:
        err(h1s[1][0] if len(h1s) > 1 else 0, "expected exactly one H1, found %d" % len(h1s))
    for i, level, txt in headings:
        if level >= 5:
            err(i, "H%d is not allowed; restructure as a table or <details> block" % level)
        if EMOJI.search(txt):
            warn(i, "emoji in heading")

    # 3. tagline and at-a-glance block (between the H1 and the first H2)
    glance_h2 = [i for i, level, txt in headings if level == 2 and anchor_of(txt) == "at-a-glance"]
    for i in glance_h2:
        err(i, "at a glance has no heading; put the bullets directly under the tagline and drop this H2")
    if h1s:
        h1_line = h1s[0][0]
        first_h2 = next((h[0] for h in headings if h[1] == 2), len(lines))
        after = [(i, l) for i, l in prose if h1_line < i < first_h2 and l.strip() and not BADGE.match(l)]
        if not after or not re.match(r'^>\s*\S', after[0][1]) or ALERT.match(after[0][1]):
            err(h1_line, "the H1 must be followed by a one-sentence '> ' tagline blockquote (badges may sit on either side of it)")
        glance = [i for i, l in after if re.match(r'^\s*[-*]\s+\*\*[^*]+:\*\*', l) or re.match(r'^\s*[-*]\s+\*\*[^*]+\*\*:', l)]
        if not glance_h2 and not 3 <= len(glance) <= 6:
            err(after[0][0] if after else h1_line, "at-a-glance block needs 3-6 '- **Label:** value' bullets before the first H2, found %d" % len(glance))

    # 4. H2 vocabulary and skeleton order
    order_key = dict(RUNBOOK_ORDER) if doc_type == "runbook" else {}
    last_slot, extra = -1, []
    for i, level, txt in headings:
        if level != 2:
            continue
        slot = HEADING_SLOT.get(txt.strip().lower())
        if slot is None:
            extra.append((i, txt))
            continue
        key = order_key.get(slot, slot)
        if key < last_slot:
            err(i, "'%s' is out of skeleton order (came after a later slot)" % txt)
        last_slot = max(last_slot, key)
    if len(extra) > 1:
        for i, txt in extra[1:]:
            err(i, "'%s': only one H2 outside the heading vocabulary is allowed (this is #%d); fold it into a slot" % (txt, extra.index((i, txt)) + 1))
    elif extra:
        warn(extra[0][0], "'%s' is the one extra H2 allowed; make sure it is not Reference or Overview content" % extra[0][1])

    # 5. empty sections and missing orientation lines
    for idx, (i, level, txt) in enumerate(headings):
        nxt = headings[idx + 1] if idx + 1 < len(headings) else None
        end = nxt[0] if nxt else len(lines)
        body = [l for j, l in enumerate(lines) if i < j < end and l.strip()]
        if not body:
            if nxt and nxt[1] > level:
                err(i, "'%s' groups sub-headings but has no orientation line before the first one" % txt)
            else:
                err(i, "'%s' is an empty section; drop it or fill it" % txt)

    # 6. placeholders (TODOs are counted in the body only; the Assumptions block lists them again)
    assume_at = next((i for i, l in prose if re.search(r'<summary>\s*Assumptions', l)), len(lines))
    todo_count = 0
    for i, l in prose:
        if PLACEHOLDER.search(l):
            err(i, "placeholder text: %r" % l.strip()[:60])
        if re.match(r'^\s*(\.\.\.|…)\s*$', l):
            err(i, "a bare ellipsis standing in for content")
        if TODO.search(l) and i < assume_at:
            todo_count += 1
            if todo_count > 3:
                err(i, "more than three TODOs; drop sections instead of leaving placeholders")
    if 0 < todo_count <= 3:
        warnings.append("%s: warn: %d TODO marker(s); each must be listed in the Assumptions block" % (path, todo_count))

    # 7. alerts: consecutive, density, indentation inside lists
    alert_lines = [i for i, l in prose if ALERT.match(l)]
    for a, b in zip(alert_lines, alert_lines[1:]):
        between = [l for j, l in prose if a < j < b and l.strip() and not l.lstrip().startswith(">")]
        if not between:
            err(b, "two alerts in a row; keep at most one per idea")
    if len(prose) and len(alert_lines) > max(1, len(prose) // 40) + 1:
        warnings.append("%s: warn: %d alerts in %d lines; the contract allows about one per forty" % (path, len(alert_lines), len(prose)))
    prev_nonblank, in_list = None, False
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        if not in_fence[i] and ALERT.match(l) and ALERT.match(l).group(1) == "" and in_list:
            nxt = next((m for m in lines[i + 1:] if m.strip() and not m.lstrip().startswith(">")), "")
            if LIST_ITEM.match(nxt) and not HEADING.match(nxt):
                err(i, "alert at column 0 between list items ends the list; indent it to the item's content column")
        if in_fence[i]:
            in_list = in_list and bool(re.match(r'^\s{2,}', l)) or (in_list and FENCE.match(l) is not None and FENCE.match(l).group(1) != "")
            continue
        in_list = bool(LIST_ITEM.match(l)) or (in_list and bool(re.match(r'^\s{2,}', l)))
        prev_nonblank = l

    # 8. anchors and relative links
    seen, anchors = {}, set()
    for i, level, txt in headings:
        a = anchor_of(txt)
        n = seen.get(a, 0)
        seen[a] = n + 1
        anchors.add(a if n == 0 else "%s-%d" % (a, n))
    doc_dir = os.path.dirname(os.path.abspath(path))
    for i, l in prose:
        for target in LINK.findall(re.sub(r'`[^`]*`', '', l)):
            if target.startswith("#"):
                if target[1:] not in anchors:
                    err(i, "anchor %s does not resolve to any heading (GitHub rule: lowercase, drop punctuation, spaces to hyphens)" % target)
            elif re.match(r'^[a-z][a-z0-9+.-]*:', target) or target.startswith("//"):
                continue
            else:
                rel = target.split("#", 1)[0]
                if not rel:
                    continue
                if rel.startswith("/"):
                    err(i, "root-absolute link %s; GitHub resolves it from the repo root, the contract wants it relative to this document" % rel)
                    continue
                if os.path.exists(os.path.join(doc_dir, rel)):
                    continue
                if repo_root and os.path.exists(os.path.join(repo_root, rel)):
                    err(i, "relative link %s exists at the repo root but not relative to this document's directory; "
                           "GitHub resolves links from the document, so write it relative to %s" % (rel, os.path.relpath(doc_dir, repo_root) or "."))
                else:
                    err(i, "relative link target does not exist: %s" % rel)

    # 9. tables
    for idx, (i, l) in enumerate(prose):
        if idx + 1 < len(prose) and l.strip().startswith("|") and re.match(r'^\s*\|?\s*:?-+:?\s*(\||$)', prose[idx + 1][1]):
            cols = len([c for c in l.strip().strip("|").split("|")])
            if not 2 <= cols <= 5:
                err(i, "table has %d columns; the contract allows 2-5" % cols)
            j = idx + 2
            while j < len(prose) and prose[j][1].strip().startswith("|"):
                for cell in prose[j][1].strip().strip("|").split("|"):
                    if len(cell.strip()) > 220:
                        warn(prose[j][0], "table cell over 220 characters reads as a paragraph; move it to prose")
                j += 1

    # 10. <details> blocks
    for i, l in prose:
        if re.match(r'^\s*<details\b', re.sub(r'`[^`]*`', '', l)):   # a real opener, not prose mentioning `<details>`
            k = i
            summary_line = None
            while k < len(lines) and k < i + 3:
                if "<summary>" in lines[k]:
                    summary_line = k
                    break
                k += 1
            if summary_line is None:
                err(i, "<details> without a <summary> on the same or next line")
                continue
            m = re.search(r'<summary>(.*?)</summary>', lines[summary_line])
            if m and GENERIC_SUMMARY.match(m.group(1).strip()):
                err(summary_line, "generic <summary> text %r; name the contents" % m.group(1))
            if summary_line + 1 < len(lines) and lines[summary_line + 1].strip():
                err(summary_line, "blank line required after </summary> or GitHub will not render the Markdown inside")
        if l.strip() == "</details>" and i > 0 and lines[i - 1].strip():
            err(i, "blank line required before </details>")

    # 11. emoji in bullets and table rows; provenance presence
    for i, l in prose:
        if (LIST_ITEM.match(l) or l.strip().startswith("|")) and EMOJI.search(l):
            warn(i, "emoji in a bullet or table row")
    if not re.search(r'<!-- docsmith provenance|<summary>Sources|^## Sources', text, re.M):
        warnings.append("%s: warn: no Sources & provenance block found (HTML comment for a README, <details> block otherwise)" % path)
    has_contents = any(re.match(r'^##\s+Contents\s*$', l) for _, l in prose)
    if doc_type == "readme":
        if has_contents:
            warnings.append("%s: warn: a README has no Contents section; GitHub renders its own outline" % path)
        if re.search(r'<summary>\s*Sources', text):
            warnings.append("%s: warn: a README carries provenance as an HTML comment, not a <details> block" % path)
    elif doc_type:
        if "<!-- docsmith provenance" in text:
            warnings.append("%s: warn: only a README uses the HTML-comment provenance form; use a <details> block" % path)
        if doc_type in ("guide", "onboarding") and not has_contents:
            warnings.append("%s: warn: Contents is on for a %s" % (path, doc_type))
        if any(re.match(r'^##\s+License\s*$', l) for _, l in prose):
            warnings.append("%s: warn: License is a README-only slot" % path)
    mermaid = sum(1 for _, lang, _ in fences if lang == "mermaid")
    if mermaid:
        warnings.append("%s: info: %d mermaid block(s); run check_mermaid.py on this file" % (path, mermaid))
    return errors, warnings


def lint_file(path, doc_type, repo_root):
    with open(path, encoding="utf-8") as fh:
        return lint_text(fh.read(), path, doc_type, repo_root)


GOOD = '''# Rotate the confmgr API key

> Replace the API key confmgr uses to reach the remote, without losing local changes.

- **For:** Operators who already run confmgr 2.x on the affected machine.
- **Takes:** About five minutes. No downtime for other machines.
- **Needs:** Shell access to the machine and a new key from the remote's settings page.

## Overview

confmgr reads its key from `~/.confmgr/config.toml` and caches a session token for one hour. See [Steps](#steps).

## Steps

1. **Check for unsynced changes.**
   ```bash
   confmgr status
   ```
   You should see `Working tree clean` or a list of modified files.

2. **Invalidate the cached session token.**
   ```bash
   rm ~/.confmgr/session.json
   ```
   No output.

   > [!WARNING]
   > Do not run `confmgr reset` here. It discards local edits as well as the token.

<details><summary>Rotating on every machine at once with the fleet script</summary>

`scripts/rotate-all.sh` loops over the hosts in `fleet.txt`.

</details>

<details>
<summary>Sources &amp; provenance</summary>

- cmd/config.go (read 2026-09-18): config path, token TTL.

</details>

<details>
<summary>Assumptions made while drafting</summary>

- Audience assumed to be operators who already run confmgr; Prerequisites therefore omit installation.
- Unasked (headless run): should the fleet script get its own section?

Delete this block after review.

</details>
'''

BAD = [  # (document, substring expected in an error)
    ("# A\n# B\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nhi\n", "exactly one H1"),
    ("# A\n\nno tagline\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nhi\n", "tagline"),
    ("# A\n\n> t\n\n- **What:** x\n\n## Overview\n\nhi\n", "3-6"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n## Steps\n\nhi\n", "empty section"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Steps\n\nhi\n\n## Overview\n\nhi\n", "out of skeleton order"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nTBD\n", "placeholder"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n```\nls\n```\n", "without a language tag"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n```bash\n$ ls\n```\n", "prompt"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n##### deep\n\nhi\n", "H5"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n> [!NOTE]\n> a\n\n> [!TIP]\n> b\n", "two alerts in a row"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Steps\n\n1. **Do.**\n   run it\n\n> [!TIP]\n> indented?\n\n2. **Next.**\n   run more\n", "column 0"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nSee [x](#nowhere).\n", "does not resolve"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nSee [x](no/such/file.md).\n", "does not exist"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Reference\n\n| a | b | c | d | e | f |\n|---|---|---|---|---|---|\n| 1 | 2 | 3 | 4 | 5 | 6 |\n", "columns"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n<details><summary>Click to expand</summary>\n\nx\n\n</details>\n", "generic <summary>"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\n<details><summary>Full config</summary>\nx\n\n</details>\n", "blank line required after"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nhi\n\n## Extra one\n\nhi\n\n## Extra two\n\nhi\n", "only one H2 outside"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nTODO a\n\nTODO b\n\nTODO c\n\nTODO d\n", "more than three TODOs"),
    ("# A\n\n> t\n\n- **What:** x\n- **For:** y\n- **Needs:** z\n\n## Overview\n\nSee [x](/harness/x.sh).\n", "root-absolute"),
]


GOOD2 = GOOD.replace("No output.", "TODO: confirm the output on Windows. No output.").replace(
    "- Unasked (headless run): should the fleet script get its own section?",
    "- TODO (Steps): the Windows output is unconfirmed.\n- TODO (Overview): the token TTL was quoted from a chat; verify.\n- Unasked (headless run): should the fleet script get its own section?"
).replace("caches a session token for one hour.", "caches a session token for one hour. TODO: verify the TTL against the code.")


def selftest():
    problems = 0
    for name, doc in (("good.md", GOOD), ("good2.md", GOOD2)):
        errors, _ = lint_text(doc, name)
        if errors:
            problems += 1
            print("%s failed:\n  " % name + "\n  ".join(errors))
    for i, (doc, expect) in enumerate(BAD):
        errors, _ = lint_text(doc, "bad%d.md" % i)
        if not any(expect in e for e in errors):
            problems += 1
            print("BAD[%d] expected %r, got: %s" % (i, expect, errors))
    print("selftest: 1 good, %d bad fixtures, %d problem(s)" % (len(BAD), problems))
    return 1 if problems else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[1] == "--selftest":
        return selftest()
    doc_type, repo_root, paths = None, None, []
    it = iter(argv[1:])
    for a in it:
        if a == "--type":
            doc_type = next(it, None)
        elif a == "--repo-root":
            repo_root = next(it, None)
        else:
            paths.append(a)
    if not paths:
        print("no files given", file=sys.stderr)
        return 2
    failed = 0
    for p in paths:
        try:
            errors, warnings = lint_file(p, doc_type, repo_root)
        except OSError as exc:
            print("%s: cannot read (%s)" % (p, exc))
            return 2
        for w in warnings:
            print(w)
        for e in errors:
            print(e)
        print("%s: %d error(s), %d warning(s)" % (p, len(errors), len(warnings)))
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
