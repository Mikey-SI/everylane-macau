# -*- coding: utf-8 -*-
"""Shared docx styling helpers for the competition documents."""
from docx import Document
import os

from docx.shared import Pt, RGBColor, Inches, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TERRA = RGBColor(0xBE, 0x4A, 0x3A)
AZUL = RGBColor(0x2C, 0x5E, 0x86)
INK = RGBColor(0x2B, 0x21, 0x18)
GOLD = RGBColor(0x9C, 0x6E, 0x1E)
GREY = RGBColor(0x6B, 0x60, 0x55)
CENTER = WD_ALIGN_PARAGRAPH.CENTER

BODY_FONT = "Microsoft JhengHei"
SERIF_FONT = "Microsoft JhengHei"
MONO = "Consolas"


def new_doc():
    doc = Document()
    # A4 with slightly wider printable area. This keeps tables from wrapping
    # awkwardly and gives screenshots enough width to look crisp.
    for sec in doc.sections:
        sec.page_width = Mm(210)
        sec.page_height = Mm(297)
        sec.top_margin = Inches(0.62)
        sec.bottom_margin = Inches(0.62)
        sec.left_margin = Inches(0.68)
        sec.right_margin = Inches(0.68)
    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(10.5)
    st.font.color.rgb = INK
    st._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    st.paragraph_format.space_after = Pt(5)
    st.paragraph_format.line_spacing = 1.3
    return doc


def cjk(run, font=BODY_FONT):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    rf.set(qn("w:eastAsia"), font); rf.set(qn("w:ascii"), font); rf.set(qn("w:hAnsi"), font)


def para(doc, text="", size=10.5, color=INK, bold=False, align=None, before=0, after=5, italic=False, font=BODY_FONT):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if text:
        r = p.add_run(text)
        r.bold = bold; r.italic = italic; r.font.size = Pt(size); r.font.color.rgb = color
        cjk(r, font)
    return p


def runs(doc, parts, after=5, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    for text, o in parts:
        r = p.add_run(text)
        r.bold = o.get("bold", False); r.italic = o.get("italic", False)
        r.font.size = Pt(o.get("size", 10.5)); r.font.color.rgb = o.get("color", INK)
        cjk(r, o.get("font", BODY_FONT))
    return p


def h1(doc, no, text):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"{no}　{text}" if no else text)
    r.bold = True; r.font.size = Pt(15); r.font.color.rgb = TERRA; cjk(r, SERIF_FONT)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr"); bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "2"); bottom.set(qn("w:color"), "E0CBA8")
    pbdr.append(bottom); pPr.append(pbdr)
    return p


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
    r = p.add_run("▎" + text)
    r.bold = True; r.font.size = Pt(11.8); r.font.color.rgb = AZUL; cjk(r, SERIF_FONT)
    return p


def bullet(doc, text, head=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.26); p.paragraph_format.space_after = Pt(3)
    dot = p.add_run("· "); dot.font.color.rgb = GOLD; dot.bold = True; cjk(dot)
    if head:
        r = p.add_run(head); r.bold = True; r.font.size = Pt(10.5); cjk(r)
    r2 = p.add_run(text); r2.font.size = Pt(10.5); r2.font.color.rgb = INK; cjk(r2)
    return p


def _shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def _cell_margin(cell, top=70, start=90, bottom=70, end=90):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def _no_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:cantSplit")) is None:
        trPr.append(OxmlElement("w:cantSplit"))


def _set(cell, text, bold=False, color=INK, size=10, white=False, mono=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.keep_together = True
    r = p.add_run(text); r.bold = bold; r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if white else color
    cjk(r, MONO if mono else BODY_FONT)


def table(doc, rows, widths=None, header=True, head_fill="2C5E86", firstcol=False):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    t.autofit = False
    for ri, row in enumerate(rows):
        _no_row_split(t.rows[ri])
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci)
            _cell_margin(cell)
            if header and ri == 0:
                _shade(cell, head_fill); _set(cell, val, bold=True, white=True)
            elif (firstcol or not header) and ci == 0:
                _shade(cell, "F4EAD8"); _set(cell, val, bold=True)
            else:
                _set(cell, val)
    if widths:
        for ci, w in enumerate(widths):
            for r in t.rows:
                r.cells[ci].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def page_break(doc):
    doc.add_page_break()


def image(doc, filename, caption, width=6.35, before=4, after=8):
    """Add a centred image with a compact caption if the file exists."""
    if not os.path.exists(filename):
        return None
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_together = True
    p.paragraph_format.keep_with_next = True
    r = p.add_run()
    r.add_picture(filename, width=Inches(width))
    cap = para(doc, "圖：" + caption, size=8.8, color=GREY, italic=True, align=CENTER, after=after)
    cap.paragraph_format.keep_together = True
    return p
