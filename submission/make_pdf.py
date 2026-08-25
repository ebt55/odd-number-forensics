"""Render REPORT_SUBMISSION.md into the submission PDF.

    python submission/make_pdf.py

Reads REPORT_SUBMISSION.md (the condensed submission draft), emits
OddNumber_SPAR_TakeHome_EbinBabuThomas.pdf next to it, then verifies the result by
extracting the text back with pdfplumber.

The layout is deliberately plain - real paragraphs, real Table flowables, one
column, base-14 fonts - because the PDF is machine-converted to DOCX afterwards.
There is no title page: the title block is a compact header on page 1.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether,
                                PageTemplate, Paragraph, Preformatted, Spacer, Table,
                                TableStyle)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "REPORT_SUBMISSION.md"
FIGS = ROOT / "experiments" / "oddnum" / "results" / "figs"
OUT = HERE / "OddNumber_SPAR_TakeHome_EbinBabuThomas.pdf"

PAGE_W, PAGE_H = letter
MARGIN = 0.85 * inch
AVAIL_W = PAGE_W - 2 * MARGIN
MAX_PAGES = 8

FIGURE = "f1_ladder.png"
FIG_CAPTION = ("Figure 1 - o3 cue ladder: audited violation rate, one edit at a time "
               "(Wilson 95% CIs; n at bar ends).")
MAX_FIG_H = 5.5 * inch

TITLE_TEXT = "Why Do Models Output Odd Numbers When Asked for Even Ones?"

# --------------------------------------------------------------- sanitation

# Glyphs outside WinAnsi. Everything else in the report (em/en dash, curly quotes,
# middle dot, dagger, section sign, +/-, division sign) is WinAnsi-safe and stays.
REPLACEMENTS = {
    "→": "->",    # right arrow
    "≈": "~",     # almost equal
    "≤": "<=",
    "≥": ">=",
    "≪": "<<",
    "≫": ">>",
    "−": "-",     # minus sign
    "×": "x",     # multiplication sign
    "✓": "",      # check mark
    "✗": "",
}
SUPERSCRIPTS = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
                "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
                "⁻": "-", "⁺": "+"}
SUP_OPEN, SUP_CLOSE = "\x01", "\x02"     # markers that survive XML escaping


def sanitize(text: str) -> str:
    """Map non-WinAnsi glyphs to safe equivalents; mark superscript runs."""
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)

    def sup(match: re.Match) -> str:
        return SUP_OPEN + "".join(SUPERSCRIPTS[c] for c in match.group(0)) + SUP_CLOSE

    return re.sub("[" + "".join(SUPERSCRIPTS) + "]+", sup, text)


def assert_winansi(text: str, where: str) -> None:
    try:
        text.encode("cp1252")
    except UnicodeEncodeError as exc:
        raise SystemExit(f"non-WinAnsi glyph survived in {where}: {exc}")


# ------------------------------------------------------------ inline markup

CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\s)([^*]+?)(?<!\s)\*(?!\*)")


def inline(text: str, code_size: float = 8.6) -> str:
    """Markdown inline syntax -> reportlab intra-paragraph markup."""
    text = sanitize(text)
    slots: list[str] = []

    def stash(markup: str) -> str:
        slots.append(markup)
        return f"\x00{len(slots) - 1}\x00"

    def do_code(m: re.Match) -> str:
        return stash(f'<font face="Courier" size="{code_size}">'
                     f"{html.escape(m.group(1))}</font>")

    def do_link(m: re.Match) -> str:
        label, url = html.escape(m.group(1)), html.escape(m.group(2), quote=True)
        if url.startswith(("http://", "https://")):
            # Show the URL itself so the address survives conversion to DOCX.
            return stash(f'{label} (<link href="{url}" color="blue">{url}</link>)')
        return stash(f'<font face="Courier" size="{code_size}">{label}</font>')

    text = CODE_RE.sub(do_code, text)
    text = LINK_RE.sub(do_link, text)
    text = html.escape(text)
    text = BOLD_RE.sub(lambda m: f"<b>{m.group(1)}</b>", text)
    text = ITALIC_RE.sub(lambda m: f"<i>{m.group(1)}</i>", text)
    text = text.replace(SUP_OPEN, "<super>").replace(SUP_CLOSE, "</super>")
    for i, markup in enumerate(slots):
        text = text.replace(f"\x00{i}\x00", markup)
    assert_winansi(text, "inline text")
    return text


def plain(text: str) -> str:
    """Markdown stripped to bare text, for width heuristics."""
    text = CODE_RE.sub(r"\1", sanitize(text))
    text = LINK_RE.sub(r"\1", text)
    return (text.replace("**", "").replace("*", "")
            .replace(SUP_OPEN, "").replace(SUP_CLOSE, ""))


# ------------------------------------------------------------------ styles

GREY = colors.HexColor("#555555")
NAVY = colors.HexColor("#12314f")
RULE = colors.HexColor("#9aa5b1")


def build_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle("body", fontName="Times-Roman", fontSize=10, leading=12.5,
                          alignment=TA_JUSTIFY, spaceAfter=6)
    return {
        "body": body,
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                                leading=23.5, alignment=TA_CENTER, spaceAfter=5),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=13,
                                   leading=16, alignment=TA_CENTER, spaceAfter=7,
                                   textColor=NAVY),
        "attrib": ParagraphStyle("attrib", fontName="Times-Italic", fontSize=9,
                                 leading=11.6, alignment=TA_CENTER, spaceAfter=4,
                                 textColor=GREY),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=15.5,
                             spaceBefore=11, spaceAfter=5, textColor=NAVY),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=13.5,
                             spaceBefore=9, spaceAfter=4, textColor=NAVY),
        "list": ParagraphStyle("list", parent=body, leftIndent=15, bulletIndent=2,
                               spaceAfter=4),
        "quote": ParagraphStyle("quote", fontName="Times-Italic", fontSize=9.3,
                                leading=11.8, alignment=TA_JUSTIFY, spaceAfter=5,
                                textColor=colors.HexColor("#333333")),
        "cap": ParagraphStyle("cap", fontName="Times-Italic", fontSize=8.5, leading=10.6,
                              alignment=TA_CENTER, spaceBefore=4, spaceAfter=8),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8.4, leading=10.6,
                               leftIndent=12, spaceBefore=3, spaceAfter=7),
        "cell": ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.5, leading=10.6),
        "cellh": ParagraphStyle("cellh", fontName="Helvetica-Bold", fontSize=8.5,
                                leading=10.6),
    }


# ----------------------------------------------------------------- parsing

HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
BULLET = re.compile(r"^[-*]\s+(.*)$")
NUMBERED = re.compile(r"^(\d+)\.\s+(.*)$")
QUOTE = re.compile(r"^>\s?(.*)$")


def parse(md: str) -> list[dict]:
    blocks: list[dict] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("```"):
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append({"kind": "code", "lines": code})
            continue

        if set(line) <= {"-"} and len(line) >= 3:
            blocks.append({"kind": "hr"})
            i += 1
            continue

        m = HEADING.match(line)
        if m:
            blocks.append({"kind": "heading", "level": len(m.group(1)),
                           "text": m.group(2).strip()})
            i += 1
            continue

        if QUOTE.match(line):
            paras: list[str] = []
            cur: list[str] = []
            while i < len(lines) and QUOTE.match(lines[i].strip()):
                inner = QUOTE.match(lines[i].strip()).group(1).strip()
                if inner:
                    cur.append(inner)
                elif cur:
                    paras.append(" ".join(cur))
                    cur = []
                i += 1
            if cur:
                paras.append(" ".join(cur))
            blocks.append({"kind": "quote", "paras": paras})
            continue

        if line.startswith("|"):
            rows: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append({"kind": "table", "rows": rows})
            continue

        if BULLET.match(line) or NUMBERED.match(line):
            ordered = bool(NUMBERED.match(line))
            items: list[tuple[str, str]] = []
            while i < len(lines):
                cur_line = lines[i]
                stripped = cur_line.strip()
                if not stripped:
                    nxt = lines[i + 1] if i + 1 < len(lines) else ""
                    if not (nxt.startswith(("   ", "\t")) and nxt.strip()):
                        break
                    i += 1
                    continue
                mb, mn = BULLET.match(stripped), NUMBERED.match(stripped)
                if (mb or mn) and not cur_line.startswith(("    ", "\t")):
                    if bool(mn) != ordered:
                        break
                    marker = f"{mn.group(1)}." if mn else "•"
                    items.append((marker, mn.group(2) if mn else mb.group(1)))
                elif items and cur_line.startswith((" ", "\t")):
                    items[-1] = (items[-1][0], items[-1][1] + " " + stripped)
                else:
                    break
                i += 1
            blocks.append({"kind": "list", "items": items})
            continue

        para: list[str] = []
        while i < len(lines) and lines[i].strip():
            nxt = lines[i].strip()
            if (nxt.startswith(("|", "```", "#", ">")) or BULLET.match(nxt)
                    or NUMBERED.match(nxt) or (set(nxt) <= {"-"} and len(nxt) >= 3)):
                break
            # Footnote markers start a new paragraph even without a blank line.
            if para and nxt.startswith(("†", "‡")):
                break
            para.append(nxt)
            i += 1
        if para:
            blocks.append({"kind": "para", "text": " ".join(para)})
    return blocks


# ---------------------------------------------------------------- flowables

NUMERIC = re.compile(r"^[^A-Za-z]*\d[^A-Za-z]*$")
TABLE_FONT = 8.5


def split_row(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def make_table(rows: list[str], styles: dict) -> Table:
    header = split_row(rows[0])
    body = [split_row(r) for r in rows[2:]] if len(rows) > 2 else []
    ncols = len(header)
    body = [r + [""] * (ncols - len(r)) for r in body if any(c for c in r)]

    size = TABLE_FONT if ncols <= 5 else 7.9
    cell = ParagraphStyle("c", parent=styles["cell"], fontSize=size, leading=size * 1.25)
    cellh = ParagraphStyle("ch", parent=styles["cellh"], fontSize=size,
                           leading=size * 1.25)
    right = ParagraphStyle("cr", parent=cell, alignment=2)
    righth = ParagraphStyle("crh", parent=cellh, alignment=2)

    # A column is numeric when most of its body cells carry no letters.
    numeric = []
    for c in range(ncols):
        vals = [plain(r[c]) for r in body if plain(r[c]).strip()]
        hits = sum(1 for v in vals if NUMERIC.match(v))
        numeric.append(bool(vals) and hits / len(vals) >= 0.6 and c > 0)

    data = [[Paragraph(inline(h, size), righth if numeric[c] else cellh)
             for c, h in enumerate(header)]]
    for r in body:
        data.append([Paragraph(inline(v, size), right if numeric[c] else cell)
                     for c, v in enumerate(r)])

    weights = []
    for c in range(ncols):
        widest = max([len(plain(header[c]))] + [len(plain(r[c])) for r in body] or [1])
        # The floor keeps a short header from wrapping mid-word.
        weights.append(min(max(widest, 10), 46))
    total = sum(weights)
    widths = [AVAIL_W * w / total for w in weights]

    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def make_quote(paras: list[str], styles: dict) -> Table:
    """Indented italic block with a left rule."""
    flow = [Paragraph(inline(p), styles["quote"]) for p in paras]
    table = Table([[flow]], colWidths=[AVAIL_W - 22], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 1.6, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def make_figure(styles: dict) -> list:
    path = FIGS / FIGURE
    if not path.exists():
        print(f"  [warn] figure missing: {path}")
        return []
    iw, ih = ImageReader(str(path)).getSize()
    width = AVAIL_W
    height = width * ih / iw
    if height > MAX_FIG_H:
        height = MAX_FIG_H
        width = height * iw / ih
    img = Image(str(path), width=width, height=height)
    img.hAlign = "CENTER"
    caption = Paragraph(inline(FIG_CAPTION), styles["cap"])
    return [Spacer(1, 5), KeepTogether([img, caption])]


def build_story(blocks: list[dict], styles: dict) -> list:
    story: list = []
    section = ""
    in_header = True
    figure_done = False

    for block in blocks:
        kind = block["kind"]

        if kind == "heading":
            level, text = block["level"], block["text"]
            if in_header and level == 1:
                story.append(Paragraph(inline(text), styles["title"]))
                continue
            if in_header and level == 2:
                story.append(Paragraph(inline(text), styles["subtitle"]))
                continue
            if level == 3 or (level == 2 and re.match(r"^\d", text)):
                section = text
            story.append(Paragraph(inline(text),
                                   styles["h3" if level >= 3 else "h2"]))

        elif kind == "para":
            if in_header:
                story.append(Paragraph(inline(block["text"]), styles["attrib"]))
                continue
            story.append(Paragraph(inline(block["text"]), styles["body"]))
            if not figure_done and section.startswith("2.3") and "Figure 1" in block["text"]:
                story.extend(make_figure(styles))
                figure_done = True

        elif kind == "list":
            for marker, text in block["items"]:
                story.append(Paragraph(inline(text), styles["list"],
                                       bulletText=sanitize(marker)))
            story.append(Spacer(1, 3))

        elif kind == "quote":
            story.append(Spacer(1, 2))
            story.append(make_quote(block["paras"], styles))
            story.append(Spacer(1, 6))

        elif kind == "code":
            body = "\n".join(sanitize(l) for l in block["lines"])
            assert_winansi(body, "code block")
            story.append(Preformatted(body, styles["code"]))

        elif kind == "hr":
            if in_header:
                # The thin rule that closes the compact title block.
                story.append(Spacer(1, 2))
                story.append(HRFlowable(width="100%", thickness=0.7, color=RULE))
                story.append(Spacer(1, 7))
                in_header = False
            else:
                story.append(Spacer(1, 4))
                story.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
                story.append(Spacer(1, 6))

        elif kind == "table":
            story.append(Spacer(1, 2))
            story.append(make_table(block["rows"], styles))
            story.append(Spacer(1, 7))

    if not figure_done:
        print("  [warn] Figure 1 anchor not found; figure not placed")
    return story


def page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Times-Roman", 8.5)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W / 2.0, MARGIN * 0.5, str(canvas.getPageNumber()))
    canvas.restoreState()


def build() -> int:
    md = SOURCE.read_text(encoding="utf-8")
    styles = build_styles()
    blocks = parse(md)
    print(f"parsed {len(blocks)} blocks from {SOURCE.name}")

    doc = BaseDocTemplate(str(OUT), pagesize=letter,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title=TITLE_TEXT, author="Ebin Babu Thomas",
                          subject="SPAR model-organisms take-home")
    frame = Frame(MARGIN, MARGIN, AVAIL_W, PAGE_H - 2 * MARGIN, id="main")
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=page_footer)])
    doc.build(build_story(blocks, styles))
    print(f"wrote {OUT}  ({OUT.stat().st_size:,} bytes)")
    return 0


# ------------------------------------------------------------- verification

SENTINELS = [
    "76.7%", "Ebin Babu Thomas", "credibly applying", "86.7%", "harmonizer",
    "Claude Fable 5", "gemini-3.7-flash", "audit_decisions.jsonl",
    "task reinterpretation", "o3 x1.8", "36.7%", "0/30",
    "A Toy Environment For Exploring Reasoning About Reward",
    "Why Do Models Output Odd Numbers",
]


def _winansi(ch: str) -> bool:
    try:
        ch.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def verify() -> int:
    import pdfplumber

    with pdfplumber.open(str(OUT)) as pdf:
        pages = len(pdf.pages)
        text = "\n".join(p.extract_text() or "" for p in pdf.pages)

    print(f"\npages: {pages}")
    print(f"extracted characters: {len(text):,}")

    failures = 0
    ok = pages <= MAX_PAGES
    failures += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'} page count {pages} <= {MAX_PAGES}")

    for needle in SENTINELS:
        ok = needle in text
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} sentinel {needle!r}")

    boxes = sum(text.count(c) for c in ("■", "�", "❑"))
    print(f"  {'ok  ' if boxes == 0 else 'FAIL'} missing-glyph boxes: {boxes}")
    failures += 1 if boxes else 0

    stray = sorted({c for c in text if not _winansi(c)})
    print(f"  {'ok  ' if not stray else 'FAIL'} non-WinAnsi glyphs in output: "
          f"{[hex(ord(c)) for c in stray] or 'none'}")
    failures += 1 if stray else 0

    print("\nVERIFY PASS" if not failures else f"\nVERIFY FAILED ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    build()
    sys.exit(verify())
