#!/usr/bin/env python3
"""Lint every ```mermaid fence in a Markdown file. Standard library only, Python 3.8+.

Usage: python3 check_mermaid.py DOC.md [MORE.md ...]
       python3 check_mermaid.py --selftest
Exit 0 when every block passes (warnings allowed), 1 when any block has an error,
2 on usage error.

Heuristic and GitHub-oriented: errors are the mistakes that make a diagram fail to
render or render the wrong thing; warnings are hygiene that still renders. Line
numbers in messages are document line numbers. What it checks and what it cannot see
is listed in references/diagrams.md section 8; keep that list and this file in sync.
The fixtures under --selftest were checked against Mermaid 11: every "good" one parses,
every "bad" one fails the parser or produces a wrong diagram.
"""
import re
import sys

ALLOWED = ("stateDiagram-v2", "sequenceDiagram", "classDiagram", "erDiagram",
           "flowchart", "timeline", "pie")            # the docsmith set
DISCOURAGED = ("stateDiagram", "graph", "gantt", "journey", "mindmap", "gitGraph",
               "quadrantChart", "requirementDiagram", "sankey-beta", "xychart-beta",
               "block-beta", "C4Context")               # render on github.com, warn only
KNOWN = sorted(ALLOWED + DISCOURAGED, key=len, reverse=True)   # longest prefix first
FLOW_TYPES = ("flowchart", "graph")
COLON_TEXT_TYPES = ("sequenceDiagram", "stateDiagram-v2", "stateDiagram", "timeline",
                    "journey", "gantt", "pie")          # free text after the first ':'
PAIRS = {"(": ")", "[": "]"}
ID = r'\w+(?:-\w+)*'
ER_REL = re.compile(r'^\s*(.+?)\s+([|o}{]{2}(?:--|\.\.)[|o}{]{2})\s+(.+?)\s*(:.*)?$')
FLOW_SKIP = re.compile(r'^(direction|style|classDef|class|click|linkStyle|accTitle|accDescr|title)\b')
FLOW_LABEL = re.compile(r'(' + ID + r')\s*(\(\(\(|\(\(|\(\[|\[\[|\[\(|\[/|\[\\|\{\{|[(\[{>])(.*?)(\)\)\)|\)\)|\]\)|\]\]|\)\]|/\]|\\\]|\}\}|[)\]}])')
EDGE_LABEL = re.compile(r'\|[^|]*\||--\s[^>]*?\s-->|--\s[^-]*?\s---+|-\.\s[^>]*?\s\.->|==\s[^>]*?\s==>')
ARROW = re.compile(r'(?:\s+[xo]|\s*<?)[-.=]{2,}[>ox]?\s*')
END_TOKEN = re.compile(r'(?<![\w-])end(?![\w-])')       # lowercase only: End/END are fine
SEQ_OPEN = re.compile(r'^(alt|opt|loop|par|critical|break|rect|box)\b')
SEQ_MSG = re.compile(r'^(.+?)(-{1,2}(?:>>|>|x|\))|<<-{1,2}>>)([+-]?)(.+?):')
SEQ_NOTE = re.compile(r'^note\s+(left of|right of|over)\b', re.I)
ACTIVATE = re.compile(r'^(de)?activate\s+(\S+)')
STATE_SKIP = re.compile(r'^(state\b|note\b|direction\b|\[\*\]\s*$|}|--)')
FENCE = re.compile(r'^(`{3,}|~{3,})\s*(\S*)')


def extract_blocks(text):
    """Return [(first_body_line_no, [lines])] for every top-level mermaid fence.

    A mermaid fence nested inside another fenced block (a ````markdown example) is
    documentation, not a diagram, and is skipped.
    """
    blocks, body, start, fence, other = [], None, 0, None, None
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        m = FENCE.match(s)
        if body is None:
            if other is not None:                       # inside a non-mermaid fence
                if m and m.group(1)[0] == other[0] and len(m.group(1)) >= other[1] and not m.group(2):
                    other = None
                continue
            if m and re.match(r'^mermaid\b', m.group(2)):
                body, start, fence = [], n + 1, (m.group(1)[0], len(m.group(1)))
            elif m:
                other = (m.group(1)[0], len(m.group(1)))
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2):
            blocks.append((start, body))
            body = None
        else:
            body.append(line)
    if body is not None:                                # unterminated fence still counts
        blocks.append((start, body))
    return blocks


def code_lines(start, lines):
    """Yield (doc_line_no, line) for non-blank, non-comment lines, frontmatter skipped.

    A line with an odd number of double quotes opens a multi-line quoted label (the
    markdown-string form); following lines are joined onto it until the quotes balance,
    and the joined text is reported at the first line's number.
    """
    in_front, pending = False, None
    for i, raw in enumerate(lines):
        s = raw.strip()
        if pending is not None:
            text = pending[1] + " " + s
            pending = None if text.count('"') % 2 == 0 else (pending[0], text)
            if pending is None:
                yield start + i - text.count("\n"), text
            continue
        if i == 0 and s == "---":
            in_front = True
            continue
        if in_front:
            in_front = s != "---"
            continue
        if not s or s.startswith("%%"):                 # comments live on their own line
            continue
        if s.count('"') % 2:
            pending = (start + i, raw.rstrip())
            continue
        yield start + i, raw.rstrip()
    if pending is not None:                             # never balanced: reported as odd quotes
        yield pending


def unquote(s):
    return re.sub(r'"[^"]*"', '""', s)


def check_balance(start, lines, dtype):
    """() and [] balance per line (Mermaid is line-oriented); {} may span lines."""
    errors, depth = [], 0
    for n, line in code_lines(start, lines):
        if line.count('"') % 2:
            errors.append('line %d: odd number of double quotes: %r' % (n, line.strip()))
            continue
        clean = unquote(line)
        if dtype in COLON_TEXT_TYPES:
            clean = clean.split(":", 1)[0]
        if dtype == "erDiagram":
            clean = re.sub(r'[|o}{]{2}(?:--|\.\.)[|o}{]{2}', '', clean)
        if dtype in FLOW_TYPES:
            clean = re.sub(r'\w+>[^\]]*\]', 'X', clean)  # asymmetric shape id>text]
        stack = []
        for ch in clean:
            if ch in PAIRS:
                stack.append(ch)
            elif ch in PAIRS.values():
                if not stack or PAIRS[stack.pop()] != ch:
                    errors.append('line %d: unbalanced %r: %r' % (n, ch, line.strip()))
                    break
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    errors.append('line %d: unmatched "}": %r' % (n, line.strip()))
                    depth = 0
        else:
            if stack:
                errors.append('line %d: unclosed %r: %r' % (n, stack[-1], line.strip()))
    if depth:
        errors.append('block: %d unclosed "{"' % depth)
    return errors


def check_flowchart(start, lines):
    errors, depth = [], 0
    for n, line in list(code_lines(start, lines))[1:]:     # skip the type line
        s = line.strip()
        if s == "end":
            depth -= 1
            if depth < 0:
                errors.append('line %d: "end" without an open subgraph' % n)
                depth = 0
            continue
        if FLOW_SKIP.match(s):
            continue
        clean = unquote(s)                                 # quoted labels become ""
        if s.startswith("subgraph"):
            depth += 1
            if END_TOKEN.search(s.split("[", 1)[0]):
                errors.append('line %d: lowercase "end" in a bracket-less subgraph title swallows the next '
                              'line; write subgraph id [Title]: %r' % (n, s))
            continue
        for m in FLOW_LABEL.finditer(clean):
            label = m.group(3)
            if label != '""' and re.search(r'[()\[\]{}|]', label):
                errors.append('line %d: unquoted label containing ( ) [ ] { } or | -> wrap it '
                              'in double quotes: %r' % (n, label))
            if '"' in label and label != '""':
                errors.append('line %d: a double quote inside an unquoted label is a parse error; quote '
                              'the whole label and drop the inner quotes: %r' % (n, m.group(0)))
        rest = EDGE_LABEL.sub(' --> ', FLOW_LABEL.sub(r'\1', clean))   # ids and arrows only
        if END_TOKEN.search(rest):
            errors.append('line %d: lowercase "end" as a node id breaks flowcharts; rename the id '
                          '(End, END and end inside a bracketed label are fine): %r' % (n, s))
        for statement in rest.split(";"):                  # a bare ; separates statements
            for frag in ARROW.split(statement):
                for node in frag.split("&"):
                    node = node.strip()
                    if node and not re.match(r'^' + ID + r'(:::\w+)?$', node):
                        errors.append('line %d: node id with spaces or punctuation %r; use id[Label] '
                                      'with a plain id' % (n, node))
    if depth:
        errors.append('block: %d subgraph(s) not closed with "end"' % depth)
    return errors


SEQ_BRANCH = {"else": "alt", "and": "par", "option": "critical"}   # branch keyword -> block it needs


def check_sequence(start, lines):
    errors, warnings, stack, active = [], [], [], {}
    for n, line in list(code_lines(start, lines))[1:]:
        s = line.strip()
        m = SEQ_OPEN.match(s)
        if m:
            stack.append(m.group(1))
        elif s == "end":
            if not stack:
                errors.append('line %d: "end" without an open alt/opt/loop/par/critical/break/rect/box' % n)
            else:
                stack.pop()
        branch = re.match(r'^(else|and|option)\b', s)
        if branch and (not stack or stack[-1] != SEQ_BRANCH[branch.group(1)]):
            errors.append('line %d: "%s" is only valid inside an open %s block: %r'
                          % (n, branch.group(1), SEQ_BRANCH[branch.group(1)], s))
        if SEQ_NOTE.match(s) and ":" not in s:
            errors.append('line %d: a Note needs ": text" after the participant(s): %r' % (n, s))
        if (SEQ_MSG.match(s) or SEQ_NOTE.match(s)) and "#" in s.split(":", 1)[-1]:
            warnings.append('line %d: "#" in message text is read as an entity code at render time and the rest '
                            'of the text disappears; write the word instead: %r' % (n, s))
        m = ACTIVATE.match(s)
        if m:
            active[m.group(2)] = active.get(m.group(2), 0) + (-1 if m.group(1) else 1)
        m = SEQ_MSG.match(s)
        if m and m.group(3) == "+":                     # A->>+B activates the receiver
            active[m.group(4).strip()] = active.get(m.group(4).strip(), 0) + 1
        elif m and m.group(3) == "-":                   # B-->>-A deactivates the sender
            active[m.group(1).strip()] = active.get(m.group(1).strip(), 0) - 1
        for who, count in list(active.items()):
            if count < 0:
                errors.append('line %d: deactivating %s, which was never activated' % (n, who))
                active[who] = 0
    if stack:
        errors.append('block: %d alt/opt/loop/par/critical/break/rect/box block(s) not closed with "end"' % len(stack))
    for who, count in active.items():
        if count:
            warnings.append('participant %s activated %d time(s) without deactivate; the bar runs to '
                            'the end of the diagram' % (who, count))
    return errors, warnings


def check_state(start, lines):
    errors, warnings = [], []
    for n, line in list(code_lines(start, lines))[1:]:
        s = unquote(line.strip()).split(":", 1)[0]
        arrows = ARROW.findall(s)
        if STATE_SKIP.match(s) or not arrows:
            continue
        if len(arrows) > 1:
            errors.append('line %d: one transition per line; "A --> B --> C" is a parse error: %r' % (n, s))
            continue
        if any(a.strip() != "-->" for a in arrows):
            errors.append('line %d: only --> is a valid transition in stateDiagram-v2 (no dashed '
                          'arrows; mark inferred transitions in the label instead): %r' % (n, s))
        for side in ARROW.split(s):
            side = side.strip()
            if side != "[*]" and not re.match(r'^\w+$', side):
                errors.append('line %d: state name %r must be a single word; declare '
                              'state "Long name" as ShortId and use ShortId' % (n, side))
            if side in ("start", "end"):
                warnings.append('line %d: %r becomes an ordinary state named %s; use [*] for the '
                                'start and end pseudo-states' % (n, side, side))
    return errors, warnings


def check_pie(start, lines):
    errors = []
    for n, line in list(code_lines(start, lines))[1:]:
        s = line.strip()
        if s.startswith("title") or s.startswith("accTitle") or s.startswith("accDescr"):
            continue
        if not re.match(r'^"[^"]*"\s*:\s*\d+(\.\d+)?$', s):
            errors.append('line %d: pie data is "label" : number, one per line: %r' % (n, s))
    return errors


def check_er(start, lines):
    errors, in_attrs = [], False
    for n, line in list(code_lines(start, lines))[1:]:
        s = line.strip()
        if in_attrs:
            in_attrs = s != "}"
            continue
        if s.endswith("{"):
            in_attrs = True
            continue
        if "--" in s or ".." in s:
            m = ER_REL.match(unquote(s))
            if not m:
                errors.append('line %d: malformed relationship; expected A ||--o{ B : label '
                              '(tokens |o || }o }| on each side): %r' % (n, s))
                continue
            if not m.group(4) or not m.group(4)[1:].strip():
                errors.append('line %d: relationship needs a label after ":": %r' % (n, s))
            for ent in (m.group(1), m.group(3)):
                if not re.match(r'^\w+$', ent) and ent != '""':
                    errors.append('line %d: entity name %r must be a single word' % (n, ent))
    return errors


def lint_block(start, lines):
    errors, warnings = [], []
    body = list(code_lines(start, lines))
    if not body:
        return "(empty)", ["empty mermaid block"], warnings
    header = body[0][1].strip()
    dtype = next((t for t in KNOWN if re.match(re.escape(t) + r'(?![\w-])', header)), None)
    if dtype is None:
        errors.append('unrecognized diagram type on first line: %r (allowed: %s)'
                      % (header, ", ".join(ALLOWED)))
        return header.split()[0], errors, warnings
    if dtype in DISCOURAGED:
        hint = {"graph": "write flowchart (newer parser)",
                "stateDiagram": "write stateDiagram-v2"}.get(dtype, "prefer a flowchart or a list")
        warnings.append('%s is outside the docsmith allowed set; %s' % (dtype, hint))
    if any(l.strip().startswith("%%{") for l in lines):
        warnings.append("%%{init}%% directive found; GitHub applies its own theme, remove it")
    if any(re.match(r'^\s*(style|classDef|linkStyle)\b', l) for l in lines):
        warnings.append("style/classDef/linkStyle found; GitHub theming differs in dark mode, remove it")
    errors += check_balance(start, lines, dtype)
    if dtype in FLOW_TYPES:
        errors += check_flowchart(start, lines)
    elif dtype == "sequenceDiagram":
        e, w = check_sequence(start, lines)
        errors += e
        warnings += w
    elif dtype.startswith("stateDiagram"):
        e, w = check_state(start, lines)
        errors += e
        warnings += w
    elif dtype == "erDiagram":
        errors += check_er(start, lines)
    elif dtype == "pie":
        errors += check_pie(start, lines)
    return dtype, errors, warnings


def lint_file(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    blocks = extract_blocks(text)
    failed = 0
    for start, lines in blocks:
        dtype, errors, warnings = lint_block(start, lines)
        print("%s:%d: %s [%s]" % (path, start - 1, dtype, "FAIL" if errors else "ok"))
        for w in warnings:
            print("    warn: " + w)
        for e in errors:
            print("    error: " + e)
        failed += bool(errors)
    return len(blocks), failed


GOOD = [  # every canonical example and every "right" line from the reference must pass
    'flowchart LR\n    action([Action string]) --> deny{Matches deny list?}\n    deny -- yes --> block(["Log BLOCK, exit 1"])\n    deny -- no --> prot{Touches protected path?}\n    prot -- yes --> block\n    prot -- no --> conf{Matches confirm list?}\n    conf -- yes --> human(["Log HUMAN, exit 2"])\n    conf -- no --> allow(["Log ALLOW, exit 0"])',
    'flowchart TB\n    subgraph client [Client]\n        ui[Web UI]\n    end\n    subgraph backend [Backend services]\n        api[API server]\n        worker[Worker]\n    end\n    ui --> api\n    api -->|enqueue| worker\n    worker -.->|status callback| api',
    'flowchart LR\n    a["Read config (yaml)"] --> b["Exit 1: failure"]\n    a-->c["Retry [max 3]"]\n    c-->|exit 1|d[Done]\n    d --> e[End] & f[END]\n    e --> g[Exit 1: failure]\n    g --> h[Log 100% done]:::hot',
    'flowchart LR\n    a[Start] --> b[The end]\n    subgraph be [Back end]\n        c[C]\n    end\n    a -->|at the end| c\n    d{Is it the end?} --> e[Yes]\n    b -- "the end of it" --> e',
    'flowchart LR\n    a("`The **cat**\n    in the hat`") -- "edge label" --> b{{"`The **dog** in the hog`"}}',
    'flowchart LR\n    a[A] -- some text --- b[B]\n    c[C] o--o d[D]\n    pre-flight[x] --> b\n    asym>Asymmetric] --> d\n    a --> b & c\n    e[One]; f[Two]\n    e --x f\n    g[Fine] --o h[Circle]\n    i[First] <--> j[Bi]',
    '---\ntitle: Titled flow\n---\nflowchart LR\n    accTitle: Titled flow\n    accDescr: three steps\n    s1[One] --> s2[Two] --> s3[Three]',
    'sequenceDiagram\n    participant U as User\n    participant A as API\n    participant D as Database\n    U->>+A: POST /orders\n    A->>D: INSERT order\n    alt insert failed\n        D-->>A: error\n        A-->>-U: 500\n    else ok\n        D-->>A: id\n        A-->>U: 201 Created\n    end\n    Note over A,D: reply arrows are stated in the API docs\n    Note left of U: returns 200 :)',
    'sequenceDiagram\n    participant A\n    participant B\n    par one\n        A->>B: x\n    and two\n        A->>B: y\n    end\n    critical open (TLS)\n        A->>B: hello\n    option timeout\n        B-->>A: bye\n    end',
    'stateDiagram-v2\n    state "Waiting for human" as Waiting\n    [*] --> Pending\n    Pending --> Running : worker picks up\n    Running --> Done : success\n    Running --> Failed : error (timeout)\n    Failed --> Pending : retry (max 3)\n    Failed --> Waiting : retries exhausted\n    Done --> [*]',
    'stateDiagram-v2\n    [*] --> Active\n    state Active {\n        [*] --> Idle\n        Idle --> Busy : job\n        Busy --> Idle : done\n    }\n    Active --> [*]',
    'erDiagram\n    USER ||--o{ ORDER : places\n    ORDER ||--|{ LINE_ITEM : contains\n    PRODUCT ||--o{ LINE_ITEM : "appears in"\n    USER {\n        int id PK\n        string email\n    }',
    'classDiagram\n    class PaymentProvider {\n        +String name\n        +charge(amount) Receipt\n    }\n    class StripeProvider\n    class PaypalProvider\n    PaymentProvider <|-- StripeProvider\n    PaypalProvider --|> PaymentProvider\n    Checkout "1" --> "*" PaymentProvider : selects',
    'classDiagram\n    namespace Shapes {\n        class Square {\n            +List~int~ sides\n        }\n    }\n    class Registry~T~ {\n        +add(T item)\n    }\n    Registry~T~ o-- Square : holds',
    'timeline\n    title Release history\n    2024 : Prototype\n    2025 : v1.0 : First external users\n    2026 : v2.0 : Observer added',
    'pie title Requests by outcome\n    "allow" : 70\n    "block" : 20\n    "human" : 10',
]
BAD = [  # (block, substring expected in an error)
    ('flowchart LR\n    A[Read config (yaml)] --> B', 'unquoted label'),
    ('flowchart LR\n    A --> end[Finish]', '"end"'),
    ('flowchart LR\n    end --> B[Next]', '"end"'),
    ('flowchart LR\n    a[Prints "done"] --> b', 'double quote inside'),
    ('flowchart LR\n    subgraph Back end\n      A\n    end', '"end"'),
    ('flowchart LR\n    API Server --> Job Queue', 'node id with spaces'),
    ('flowchart LR\n    A["oops] --> B', 'double quotes'),
    ('flowchart LR\n    A[Log [BLOCK]] --> B', 'unquoted label'),
    ('flowchart LR\n    subgraph grp [Group]\n        a[A] --> b[B]', 'not closed'),
    ('flowchart LR\n    a[A] --> b[B]\n    end', 'without an open subgraph'),
    ('sequenceDiagram\n    alt ok\n        A-->>B: 200\n    else\n        A-->>B: 500', 'not closed'),
    ('sequenceDiagram\n    A->>B: hi\n    end', 'without an open'),
    ('sequenceDiagram\n    A->>B: hi\n    deactivate B', 'never activated'),
    ('sequenceDiagram\n    A->>B: hi\n    Note over A,B', 'Note needs'),
    ('sequenceDiagram\n    A->>B: hi\n    and other\n    B-->>A: yo', 'only valid inside'),
    ('pie title Outcomes\n    "allow" : 70\n    "block" 20', 'pie data'),
    ('stateDiagram-v2\n    [*] --> Waiting for human', 'single word'),
    ('stateDiagram-v2\n    [*] -.-> Pending', 'only -->'),
    ('stateDiagram-v2\n    [*] --> Idle --> Busy', 'one transition per line'),
    ('erDiagram\n    USER 1--* ORDER', 'malformed relationship'),
    ('erDiagram\n    USER ||--o{ ORDER', 'label after'),
    ('erDiagram\n    USER ACCOUNT ||--o{ ORDER : has', 'single word'),
    ('classDiagram\n    class A {\n        +int x', 'unclosed "{"'),
    ('mermaid\n    A --> B', 'unrecognized diagram type'),
    ('statediagram\n    A --> B', 'unrecognized diagram type'),
    ('', 'empty'),
]
WARN = [  # (block, substring expected in a warning, and no error)
    ('sequenceDiagram\n    A->>+B: hi\n    B-->>A: bye', 'without deactivate'),
    ('stateDiagram-v2\n    start --> Pending\n    Pending --> end', 'use [*]'),
    ('graph LR\n    a[A] --> b[B]', 'write flowchart'),
    ('sequenceDiagram\n    A->>B: ledger line #3 then next', 'entity code'),
]


def selftest():
    bad = 0
    for i, block in enumerate(GOOD):
        dtype, errors, _ = lint_block(1, block.splitlines())
        if errors:
            bad += 1
            print("GOOD[%d] (%s) failed: %s" % (i, dtype, errors))
    for i, (block, expect) in enumerate(BAD):
        dtype, errors, _ = lint_block(1, block.splitlines())
        if not any(expect in e for e in errors):
            bad += 1
            print("BAD[%d] (%s) expected %r, got: %s" % (i, dtype, expect, errors))
    for i, (block, expect) in enumerate(WARN):
        dtype, errors, warnings = lint_block(1, block.splitlines())
        if errors or not any(expect in w for w in warnings):
            bad += 1
            print("WARN[%d] (%s) expected warning %r, got errors %s warnings %s" % (i, dtype, expect, errors, warnings))
    print("selftest: %d good, %d bad, %d warn fixtures, %d problem(s)" % (len(GOOD), len(BAD), len(WARN), bad))
    return 1 if bad else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[1] == "--selftest":
        return selftest()
    total = failed = 0
    for path in argv[1:]:
        try:
            n, f = lint_file(path)
        except OSError as exc:
            print("%s: cannot read (%s)" % (path, exc))
            return 2
        total += n
        failed += f
    print("%d mermaid block(s), %d with errors" % (total, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
