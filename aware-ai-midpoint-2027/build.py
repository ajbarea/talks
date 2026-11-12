# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2"]
# ///
"""AJ's slides for the AWARE-AI Winter Symposium midpoint talks, built on the shared deck's own template.

The symposium deck is one Google Slides file for the whole cohort. Export it as .pptx (File > Download >
Microsoft PowerPoint) and pass it as TEMPLATE: this keeps AJ's name slide, drops every other slide, and adds
his talk slides on the deck's own layouts, so they import with its look. Figures are native shapes, so they
stay editable in Google Slides. Every number comes from the Federated Agents talk's generated readings.

    uv run aware-ai-midpoint-2027/build.py TEMPLATE.pptx OUT_DIR

Writes OUT_DIR/aware-ai-midpoint-2027.pptx and OUT_DIR/script.md (the script with its figures filled in),
and fails when the script's sections do not match the slides or the script runs past the time budget.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.packuri import PackURI
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = pathlib.Path(__file__).resolve().parent
READINGS = HERE.parent / "federated-agents" / "data" / "readings.js"
SCRIPT = HERE / "script.md"
NAME = "AJ Barea"
WPM = 140  # a presenter's pace, words a minute
BUDGET_MIN = 4.5  # the organizers cut at 5:00; this leaves headroom

# Colours. The deck's own text is black Arial on white; the one accent is the Federated Agents deck's
# label navy (federated-agents/deck.css --label), so the slides read as the same research.
INK = RGBColor(0x00, 0x00, 0x00)
MUTED = RGBColor(0x59, 0x59, 0x59)  # the template's dk2, 7:1 on white
ACCENT = RGBColor(0x0B, 0x3A, 0x66)
TINT = RGBColor(0xDB, 0xE7, 0xF1)  # federated-agents/deck.css --band
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FILL_LINE = RGBColor(0xC4, 0x16, 0x60)  # federated-agents/deck.css --risk: a box to fill in January
FILL_INK = RGBColor(0x7D, 0x0E, 0x45)  # --risk-ink
CODE_FONT = "Courier New"


def readings() -> dict:
    text = READINGS.read_text()
    start = text.index("{", text.index("readings:"))
    return json.JSONDecoder().raw_decode(text, start)[0]


def fill(text: str, r: dict) -> str:
    def one(m: re.Match) -> str:
        if m.group(1) not in r:
            raise SystemExit(f"script names readings.{m.group(1)}, which {READINGS.name} lacks")
        return str(r[m.group(1)])

    return re.sub(r"\{readings\.([a-z_]+)\}", one, text)


# Drawing helpers, in inches on the 10 x 5.625 in canvas.


def text_box(slide, x, y, w, h, runs, size=16, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=None):
    """A text box; `runs` is a string, or a list of paragraphs, each a list of (text, bold, colour) runs."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    write(box.text_frame, runs, size, color, align, anchor, font)
    return box


def write(tf, runs, size, color, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=None):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.06))
    paras = [[(runs, False, color)]] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for text, bold, colour in para:
            run = p.add_run()
            run.text = text
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = colour
            if font:
                run.font.name = font


def shape(slide, kind, x, y, w, h, fill=None, line=None, weight=1.25, dash=False):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(weight)
        if dash:
            s.line.dash_style = MSO_LINE.DASH
    return s


def label(s, runs, size=16, color=INK, align=PP_ALIGN.CENTER, font=None):
    write(s.text_frame, runs, size, color, align, MSO_ANCHOR.MIDDLE, font)


def arrow(slide, x1, y1, x2, y2, color=ACCENT, weight=1.75):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(weight)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return c


def fill_box(slide, x, y, w, h, text, size=15):
    """A dashed box for what is true only after today: AJ fills it in January and removes the box."""
    s = shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, line=FILL_LINE, weight=1.5, dash=True)
    label(s, [[("FILL: ", True, FILL_INK), (text, False, FILL_INK)]], size, align=PP_ALIGN.LEFT)
    return s


def title(slide, text):
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.34), Inches(0.22), Inches(9.32), Inches(1.0)
    write(t.text_frame, text, 24, INK, anchor=MSO_ANCHOR.TOP)


def notes(slide, bullets):
    slide.notes_slide.notes_text_frame.text = "\n".join(f"- {b}" for b in bullets)


# The slides.


def name_slide(slide):
    text_box(
        slide,
        0.34,
        3.25,
        9.32,
        1.35,
        [
            [
                (
                    "Does learned house style in code review belong to the project group, "
                    "the organization, or neither?",
                    False,
                    ACCENT,
                )
            ],
            [("PhD student, Computing and Information Sciences · AI Software track", False, MUTED)],
            [("Advisor: Dr. Leon Reznik", False, MUTED)],
        ],
        size=18,
        align=PP_ALIGN.CENTER,
    )


def problem(slide):
    for x, head in ((0.45, "An AI assistant writes"), (3.65, "A reviewer replies"), (6.85, "The fix the team wants")):
        text_box(slide, x, 1.45, 2.7, 0.4, head, 16, MUTED, PP_ALIGN.CENTER)
    a = shape(slide, MSO_SHAPE.RECTANGLE, 0.45, 1.9, 2.7, 1.2, fill=TINT)
    label(a, "db = connect(URL)", 16, font=CODE_FONT)
    b = shape(slide, MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, 3.65, 1.9, 2.7, 1.2, fill=WHITE, line=ACCENT, weight=2)
    label(b, "Please use our team_db() helper here.", 16)
    c = shape(slide, MSO_SHAPE.RECTANGLE, 6.85, 1.9, 2.7, 1.2, fill=TINT, line=ACCENT, weight=2)
    label(c, "db = team_db()", 16, font=CODE_FONT)
    arrow(slide, 3.18, 2.5, 3.6, 2.5)
    arrow(slide, 6.38, 2.5, 6.8, 2.5)
    text_box(
        slide,
        0.45,
        3.55,
        9.1,
        0.9,
        [
            [
                ("Teams enforce rules like this in code review, one comment at a time, and ", False, INK),
                ("rarely write them down.", True, ACCENT),
            ]
        ],
        20,
    )
    text_box(slide, 0.45, 4.9, 9.1, 0.4, "Illustrative example.", 16, MUTED)


def study(slide):
    org = shape(slide, MSO_SHAPE.RECTANGLE, 0.4, 1.35, 3.0, 2.15, line=ACCENT, weight=1.25)
    org.text_frame.text = ""
    text_box(
        slide,
        0.45,
        1.38,
        2.9,
        0.55,
        [[("One organization", True, INK)], [("OpenStack, Wikimedia or Qt", False, MUTED)]],
        15,
    )
    for y, name in ((1.95, "Half A of projects"), (2.7, "Half B of projects")):
        label(shape(slide, MSO_SHAPE.RECTANGLE, 0.55, y, 2.7, 0.6, fill=TINT), name, 16)
    label(
        shape(slide, MSO_SHAPE.RECTANGLE, 0.4, 3.7, 3.0, 0.6, line=MUTED),
        "Chromium: another organization, used for Qt",
        15,
    )
    chips = ((2.25, "Own add-on"), (3.0, "Sibling add-on"), (4.0, "Foreign add-on"))
    for cy, name in chips:
        label(
            shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 3.95, cy - 0.275, 1.85, 0.55, fill=ACCENT),
            [[(name, True, WHITE)]],
        )
    arrow(slide, 3.27, 2.25, 3.93, 2.25)
    arrow(slide, 3.27, 3.0, 3.93, 3.0)
    arrow(slide, 3.42, 4.0, 3.93, 4.0)
    target = shape(slide, MSO_SHAPE.RECTANGLE, 6.45, 2.35, 3.1, 1.25, fill=WHITE, line=ACCENT, weight=2)
    label(
        target,
        [
            [("Unseen reviews from Half A", True, INK)],
            [("Score: the probability each gives the developer's real fix", False, MUTED)],
        ],
        16,
    )
    for cy, ty in ((2.25, 2.65), (3.0, 2.97), (4.0, 3.3)):
        arrow(slide, 5.82, cy, 6.43, ty)
    for x, lead, rest in (
        (0.4, "Own beats sibling: ", "style stays with its projects"),
        (5.1, "Sibling beats foreign: ", "Qt has a style beyond its projects"),
    ):
        card = shape(slide, MSO_SHAPE.RECTANGLE, x, 4.55, 4.45, 0.7, fill=TINT)
        label(card, [[(lead, True, ACCENT), (rest, False, INK)]], 16)


def built(slide, r):
    stats = (
        (
            1.4,
            f"{r['corpus_examples_openstack']} + {r['corpus_examples_wikimedia']}",
            "review lessons built from OpenStack and Wikimedia",
        ),
        (
            2.85,
            f"+{r['tuned_exact_gain']} in 100",
            "more fixes exactly right than the untuned model, after tuning on a community's own reviews",
        ),
    )
    for y, big, small in stats:
        text_box(slide, 0.45, y, 4.2, 0.75, [[(big, True, ACCENT)]], 40)
        text_box(slide, 0.45, y + 0.75, 4.2, 0.65, small, 16)
    runs, found = r["planted_runs"], r["planted_found"]
    text_box(
        slide,
        5.0,
        1.4,
        4.6,
        0.85,
        f"A fake house rule, planted in training, was found in {found} of {runs} splits",
        18,
    )
    cols, d, gap = 10, 0.3, 0.135
    for i in range(runs):
        x = 5.05 + (i % cols) * (d + gap)
        y = 2.45 + (i // cols) * (d + gap)
        shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=ACCENT if i < found else None, line=ACCENT, weight=1.5)
    ky = 2.45 + ((runs - 1) // cols + 1) * (d + gap) + 0.15
    shape(slide, MSO_SHAPE.OVAL, 5.05, ky + 0.05, 0.2, 0.2, fill=ACCENT, line=ACCENT)
    text_box(slide, 5.3, ky - 0.04, 1.2, 0.38, "found", 16, MUTED)
    shape(slide, MSO_SHAPE.OVAL, 6.5, ky + 0.05, 0.2, 0.2, line=ACCENT, weight=1.5)
    text_box(slide, 6.75, ky - 0.04, 1.2, 0.38, "missed", 16, MUTED)
    text_box(
        slide,
        0.45,
        4.65,
        9.1,
        0.7,
        f"Tuning gain and planted rule: development months only ({r['window_dev']}); the test months stay sealed.",
        16,
        MUTED,
    )


def beyond(slide):
    columns = (
        (
            0.45,
            "AWARE-AI",
            (
                "BONSAI lab rotation (Prof. Lange): 4 pull requests to shared lab code",
                "Hackathons: Best AI Model (spring), Best Presentation (fall)",
                "Talk to the AI Software track on makesense",
            ),
            "trainee council, AFRL visit, TA work, outreach",
        ),
        (
            5.1,
            "Dissemination",
            (
                "IAAI-27: makesense accepted as an oral (Montréal, Feb 2027)",
                "SCADS 2026 Technical Report: two chapters",
                "Co-author: IEEE Intelligent Systems journal; IJCNN 2026",
                "Talks: Rochester Security Summit; Federated Agents at RIT",
            ),
            "CISC-810 and LDQIS lab talks (Nov), anything new",
        ),
    )
    for x, head, items, todo in columns:
        text_box(slide, x, 1.15, 4.4, 0.45, [[(head, True, ACCENT)]], 20)
        for i, item in enumerate(items):
            y = 1.7 + i * 0.7
            shape(slide, MSO_SHAPE.OVAL, x + 0.05, y + 0.14, 0.16, 0.16, fill=ACCENT)
            text_box(slide, x + 0.3, y, 4.1, 0.72, item, 17)
        fill_box(slide, x, 4.62, 4.45, 0.68, todo)


def timeline(slide):
    # Every dot is hollow until AJ confirms the date in January; fill a dot (True) once it has happened.
    events = (
        ("Nov 20", "Plan submitted to MSR 2027", False),
        ("Dec 23", "Reviews returned", False),
        ("Jan 15", "Response and revision", False),
        ("Feb 4", "Decision", False),
        ("Apr 26-27", "MSR 2027 in Dublin, if accepted", False),
        ("Sep 30", "Full paper to the journal", False),
    )
    xs = (0.9, 2.4, 4.4, 5.9, 7.4, 8.9)
    line_y = 2.3
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.5), Inches(line_y), Inches(9.5), Inches(line_y))
    c.line.color.rgb = ACCENT
    c.line.width = Pt(2.5)
    for x, (date, what, past) in zip(xs, events, strict=True):
        text_box(slide, x - 0.7, 1.7, 1.4, 0.45, [[(date, True, ACCENT)]], 18, align=PP_ALIGN.CENTER)
        shape(
            slide,
            MSO_SHAPE.OVAL,
            x - 0.12,
            line_y - 0.12,
            0.24,
            0.24,
            fill=ACCENT if past else WHITE,
            line=ACCENT,
            weight=2,
        )
        text_box(slide, x - 0.72, 2.55, 1.44, 1.0, what, 16, align=PP_ALIGN.CENTER)
    today = 3.4
    t = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(today), Inches(1.7), Inches(today), Inches(2.9))
    t.line.color.rgb = INK
    t.line.width = Pt(1.5)
    t.line.dash_style = MSO_LINE.DASH
    text_box(slide, today - 0.6, 1.25, 1.2, 0.42, [[("Today", True, INK)]], 16, align=PP_ALIGN.CENTER)
    fill_box(slide, 0.45, 3.85, 9.1, 0.5, "did the plan go in on Nov 20, and what did the Dec 23 reviews say?")
    text_box(
        slide,
        0.45,
        4.5,
        9.1,
        0.85,
        [
            [
                ("Registered report: ", True, ACCENT),
                (
                    "the method is judged before any result exists. Once accepted in principle, the journal paper is "
                    "likely published whatever the answer, if I follow the plan.",
                    False,
                    INK,
                ),
            ]
        ],
        16,
    )


SLIDES = (
    (
        NAME,
        None,
        [
            "Name, PhD in Computing and Information Sciences, AI Software track, Dr. Reznik",
            "One question: does learned house style belong to a project group, the organization, or neither?",
            "Roadmap: problem, study, the rest of the year, where it stands",
        ],
    ),
    (
        "AI coding assistants rarely see an organization's unwritten house style",
        problem,
        [
            "Assistant connects directly; reviewer: use our helper",
            "Rules live in review, comment by comment, rarely written down",
            "Why care: an assistant on your team should follow your team's rules",
        ],
    ),
    (
        "I test where a learned house style transfers: within projects, or across an organization",
        study,
        [
            "Split an organization's projects in half, many times; small add-on per half on a frozen open model",
            "Score on unseen reviews: the probability each add-on gives the developer's real fix",
            "Own > sibling: stays with projects. Sibling > foreign (Qt vs Chromium): organization style",
        ],
    ),
    (
        "On development data, the test finds a house rule when one is planted",
        built,
        [
            "Open-source tool: comment + code + the developer's next code = one lesson",
            "Tuning on a community's own reviews: more fixes exactly right than the untuned model",
            "Planted fake rule found in every split; test months still sealed",
        ],
    ),
    (
        "Alongside the study: a lab rotation, an oral paper, and talks",
        beyond,
        [
            "BONSAI rotation with Prof. Lange: 4 PRs (CI, memory fix, weight-copy bug, template)",
            "Hackathons: Best AI Model, Best Presentation",
            "IAAI-27 oral in Montréal next month; SCADS 2026 report; talks",
        ],
    ),
    (
        "Next, reviewers judge the plan; then the sealed months answer where house style belongs",
        timeline,
        [
            "MSR 2027 registered report: response Jan 15, decision Feb 4",
            "Accepted: open sealed months, paper to EMSE by Sep 30",
            "Then the goal: agents that share what organizations have in common, without leaking the rest",
        ],
    ),
)


def script_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^## \d+\. (.+)$", text, flags=re.M)
    return [
        (parts[i].strip(), re.sub(r"<!--.*?-->", "", parts[i + 1], flags=re.S).strip()) for i in range(1, len(parts), 2)
    ]


def check_script(text: str) -> list[tuple[str, int]]:
    sections = script_sections(text)
    titles = [s[0] for s in SLIDES]
    if [t for t, _ in sections] != titles:
        raise SystemExit(f"script.md sections {[t for t, _ in sections]} do not match the slides {titles}")
    counts = [(t, len(body.split())) for t, body in sections]
    minutes = sum(n for _, n in counts) / WPM
    if minutes > BUDGET_MIN:
        raise SystemExit(f"script runs {minutes:.2f} min at {WPM} wpm, over the {BUDGET_MIN} min budget")
    return counts


def build(template: pathlib.Path, out: pathlib.Path) -> None:
    r = readings()
    script = fill(SCRIPT.read_text(), r)
    counts = check_script(script)

    prs = Presentation(str(template))
    ids = prs.slides._sldIdLst
    keep = [
        sid
        for sid, slide in zip(list(ids), prs.slides, strict=True)
        if slide.shapes.title is not None and slide.shapes.title.text_frame.text.strip() == NAME
    ]
    if len(keep) != 1:
        raise SystemExit(f"expected one slide titled {NAME!r} in {template}, found {len(keep)}")
    for sid in list(ids):
        if sid is not keep[0]:
            prs.part.drop_rel(sid.rId)
            ids.remove(sid)

    # The kept slide keeps its old part name (slide2.xml, say); add_slide numbers new parts by count, so free it.
    prs.slides[0].part.partname = PackURI("/ppt/slides/slide1.xml")
    layout = next(lay for lay in prs.slide_layouts if lay.name == "TITLE_ONLY")
    name, _, name_notes = SLIDES[0]
    first = prs.slides[0]
    name_slide(first)
    notes(first, name_notes)
    for heading, draw, bullets in SLIDES[1:]:
        slide = prs.slides.add_slide(layout)
        title(slide, heading)
        draw(slide, r) if draw is built else draw(slide)
        notes(slide, bullets)

    out.mkdir(parents=True, exist_ok=True)
    prs.save(str(out / "aware-ai-midpoint-2027.pptx"))
    (out / "script.md").write_text(script)
    total = sum(n for _, n in counts)
    for t, n in counts:
        print(f"{n:4d} words  {n / WPM * 60:5.0f} s  {t}")
    print(f"{total:4d} words  {total / WPM:.2f} min at {WPM} wpm (budget {BUDGET_MIN} min)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    build(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
