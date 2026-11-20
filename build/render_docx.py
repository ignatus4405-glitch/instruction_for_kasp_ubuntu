# -*- coding: utf-8 -*-
"""Сборка DOCX-версии инструкции (python-docx)."""
import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Emu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import content_1, content_2, content_3, content_4  # noqa: E402
import meta  # noqa: E402
from textutil import parse_inline  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

STEEL = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x74, 0xB5)
GREY = RGBColor(0x5A, 0x63, 0x73)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
CODE_COLOR = RGBColor(0x8B, 0x2E, 0x00)

BODY_FONT = "Calibri"
MONO_FONT = "Consolas"


# ------------------------------------------------------------------ утилиты
def set_run_font(run, name=None, size=None, bold=None, italic=None, color=None):
    if name:
        run.font.name = name
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    return run


PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
             "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
             "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
             "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing",
             "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment",
             "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]

TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap",
              "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark", "headers",
              "cellIns", "cellDel", "cellMerge", "tcPrChange"]

TRPR_ORDER = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit",
              "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden", "ins", "del", "trPrChange"]

TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
               "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd",
               "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]


def _local(tag):
    return tag.split("}")[-1]


def insert_ordered(parent, element, order):
    """Вставляет элемент с соблюдением порядка дочерних узлов схемы OOXML."""
    name = _local(element.tag)
    idx = order.index(name)
    for child in list(parent):
        if _local(child.tag) in order[idx + 1:]:
            child.addprevious(element)
            return element
    parent.append(element)
    return element


def shade(element, hex_fill, order):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    insert_ordered(element, shd, order)


def shade_paragraph(paragraph, hex_fill):
    pPr = paragraph._p.get_or_add_pPr()
    shade(pPr, hex_fill, PPR_ORDER)


def shade_cell(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shade(tcPr, hex_fill, TCPR_ORDER)


def paragraph_border(paragraph, side="left", color="2E74B5", size=18, space=6):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        insert_ordered(pPr, pBdr, PPR_ORDER)
    el = OxmlElement("w:%s" % side)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    pBdr.append(el)


def cell_margins(cell, top=60, bottom=60, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:%s" % side)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    insert_ordered(tcPr, mar, TCPR_ORDER)


def add_field(paragraph, instr, placeholder=""):
    parts = []
    r1 = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    r1._r.append(fld_begin)
    parts.append(r1)

    r2 = paragraph.add_run()
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    r2._r.append(instr_el)
    parts.append(r2)

    r3 = paragraph.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    r3._r.append(fld_sep)
    parts.append(r3)

    r4 = paragraph.add_run(placeholder)
    parts.append(r4)

    r5 = paragraph.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    r5._r.append(fld_end)
    parts.append(r5)
    return parts


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    insert_ordered(trPr, tblHeader, TRPR_ORDER)


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    insert_ordered(trPr, el, TRPR_ORDER)


def set_table_fixed(table):
    """python-docx сам выставляет w:tblLayout=fixed при autofit=False."""
    table.autofit = False


def add_hyperlink(paragraph, url, text, size):
    part = paragraph.part
    r_id = part.relate_to(url,
                          "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                          is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "1F5FA8")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(c)
    rPr.append(u)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def write_inline(paragraph, text, size=10.5, color=DARK, bold_all=False):
    for kind, val in parse_inline(text):
        if kind == "url":
            add_hyperlink(paragraph, val, val, size)
        elif kind == "c":
            run = paragraph.add_run(val)
            set_run_font(run, MONO_FONT, size - 1.2, color=CODE_COLOR)
        elif kind == "b":
            run = paragraph.add_run(val)
            set_run_font(run, BODY_FONT, size, bold=True, color=color)
        elif kind == "i":
            run = paragraph.add_run(val)
            set_run_font(run, BODY_FONT, size, italic=True, color=color)
        else:
            run = paragraph.add_run(val)
            set_run_font(run, BODY_FONT, size, bold=bold_all or None, color=color)


# ------------------------------------------------------------------ документ
class Builder:
    def __init__(self):
        self.doc = Document()
        self._setup_page()
        self._setup_styles()

    # -------------------------------------------------- страница и стили
    def _setup_page(self):
        section = self.doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2.1)
        section.right_margin = Cm(1.8)
        section.header_distance = Cm(1.1)
        section.footer_distance = Cm(0.9)
        self.section = section

    def _setup_styles(self):
        st = self.doc.styles
        normal = st["Normal"]
        normal.font.name = BODY_FONT
        normal.font.size = Pt(10.5)
        normal.font.color.rgb = DARK
        rpr = normal.element.get_or_add_rPr()
        rFonts = rpr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rpr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), BODY_FONT)
        pf = normal.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(4)
        pf.line_spacing = 1.12

        specs = {
            "Heading 1": (16, True, STEEL, 14, 8),
            "Heading 2": (12.5, True, STEEL, 13, 5),
            "Heading 3": (11, True, BLUE, 10, 4),
        }
        for name, (size, bold, color, before, after) in specs.items():
            style = st[name]
            style.font.name = BODY_FONT
            style.font.size = Pt(size)
            style.font.bold = bold
            style.font.color.rgb = color
            style.paragraph_format.space_before = Pt(before)
            style.paragraph_format.space_after = Pt(after)
            style.paragraph_format.keep_with_next = True
            style.paragraph_format.line_spacing = 1.0

    # -------------------------------------------------- обложка
    def cover(self):
        doc = self.doc

        # верхняя плашка
        tbl = doc.add_table(rows=1, cols=1)
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Cm(17.1)
        shade_cell(cell, "1F3864")
        cell_margins(cell, top=340, bottom=340, left=340, right=340)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        set_run_font(p.add_run("ИНСТРУКЦИЯ ПО РАЗВЁРТЫВАНИЮ"), BODY_FONT, 10, bold=True,
                     color=RGBColor(0xFF, 0xFF, 0xFF))
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(18)
        set_run_font(p2.add_run("Корпоративная система защиты информации"), BODY_FONT, 9,
                     color=RGBColor(0xDD, 0xE6, 0xF2))
        for line in ["Установка Ubuntu Server 26.10", "и развёртывание",
                     "Kaspersky Security Center"]:
            ph = cell.add_paragraph()
            ph.paragraph_format.space_after = Pt(0)
            set_run_font(ph.add_run(line), BODY_FONT, 22, bold=True,
                         color=RGBColor(0xFF, 0xFF, 0xFF))

        doc.add_paragraph()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(26)
        p.paragraph_format.space_after = Pt(2)
        set_run_font(p.add_run("Практическое руководство — пошагово, с указанием клавиш"), BODY_FONT, 13, bold=True, color=STEEL)
        p = doc.add_paragraph()
        set_run_font(p.add_run("Kaspersky Security Center Linux 17 · MariaDB 11.8 · Web Console 17"),
                     BODY_FONT, 10.5, color=GREY)

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(26)
        p.paragraph_format.space_after = Pt(6)
        set_run_font(p.add_run("В документе"), BODY_FONT, 10, bold=True, color=STEEL)
        for item in meta.COVER_ITEMS:
            pi = doc.add_paragraph()
            pf = pi.paragraph_format
            pf.left_indent = Cm(0.6)
            pf.first_line_indent = Cm(-0.6)
            pf.space_after = Pt(4)
            set_run_font(pi.add_run("▪  "), BODY_FONT, 10, color=BLUE)
            set_run_font(pi.add_run(item), BODY_FONT, 10.5, color=RGBColor(0x2B, 0x2F, 0x36))

        for _ in range(2):
            doc.add_paragraph()

        rows = [
            ("Код документа", meta.DOC_CODE),
            ("Версия документа", meta.DOC_VERSION),
            ("Дата выпуска", meta.DOC_DATE),
            ("Статус", meta.DOC_STATUS),
            ("Область применения", "Ubuntu Server 26.10, KSC Linux 17"),
            ("Разработал", meta.DOC_AUTHOR),
        ]
        t = doc.add_table(rows=len(rows), cols=2)
        t.autofit = False
        set_table_fixed(t)
        for i, (k, v) in enumerate(rows):
            row = t.rows[i]
            cant_split(row)
            c0, c1 = row.cells
            c0.width = Cm(5.4)
            c1.width = Cm(11.7)
            for c in (c0, c1):
                cell_margins(c, top=70, bottom=70, left=140, right=140)
            p0 = c0.paragraphs[0]
            set_run_font(p0.add_run(k), BODY_FONT, 9.5, color=GREY)
            p1 = c1.paragraphs[0]
            set_run_font(p1.add_run(v), BODY_FONT, 9.5, color=DARK)
        self._table_borders(t, color="D8DEE7", inner=False)

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        set_run_font(p.add_run("Документ содержит пошаговые команды. Перед применением проверьте "
                               "параметры стенда (раздел 2.1)."), BODY_FONT, 8, color=GREY)
        p = doc.add_paragraph()
        set_run_font(p.add_run("Kaspersky Security Center является товарным знаком "
                               "АО «Лаборатория Касперского»."), BODY_FONT, 8, color=GREY)
        doc.add_page_break()

    def _table_borders(self, table, color="C6CEDA", size=6, inner=True):
        tbl = table._tbl
        tblPr = tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement("w:%s" % side)
            if side.startswith("inside") and not inner:
                el.set(qn("w:val"), "nil")
            else:
                el.set(qn("w:val"), "single")
                el.set(qn("w:sz"), str(size))
                el.set(qn("w:space"), "0")
                el.set(qn("w:color"), color)
            borders.append(el)
        insert_ordered(tblPr, borders, TBLPR_ORDER)

    # -------------------------------------------------- колонтитулы
    def header_footer(self):
        section = self.section
        header = section.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.text = ""
        hp.paragraph_format.tab_stops.add_tab_stop(Cm(17.1), WD_TAB_ALIGNMENT.RIGHT)
        set_run_font(hp.add_run("%s · %s" % (meta.DOC_CODE, meta.DOC_TITLE)), BODY_FONT, 7.5, color=GREY)
        hp.add_run("\t")
        set_run_font(hp.add_run("Версия %s от %s" % (meta.DOC_VERSION, meta.DOC_DATE)),
                     BODY_FONT, 7.5, color=GREY)
        paragraph_border(hp, "bottom", color="D8DEE7", size=6, space=4)

        footer = section.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.text = ""
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("Стр. ")
        set_run_font(r, BODY_FONT, 7.5, color=GREY)
        add_field(fp, " PAGE ", "1")
        r = fp.add_run(" из ")
        set_run_font(r, BODY_FONT, 7.5, color=GREY)
        add_field(fp, " NUMPAGES ", "1")
        for run in fp.runs:
            set_run_font(run, BODY_FONT, 7.5, color=GREY)

    # -------------------------------------------------- оглавление
    def toc(self):
        doc = self.doc
        h = doc.add_paragraph()
        h.paragraph_format.space_after = Pt(10)
        set_run_font(h.add_run("Содержание"), BODY_FONT, 16, bold=True, color=STEEL)

        p = doc.add_paragraph()
        add_field(p, r' TOC \o "1-2" \h \z \u ',
                  "Оглавление формируется автоматически: выделите его и нажмите F9.")
        p = doc.add_paragraph()
        set_run_font(p.add_run("Оглавление собирается автоматически при открытии документа; строки — "
                               "ссылки, щелчок открывает соответствующий раздел. Если оглавление "
                               "осталось пустым, щёлкните по нему правой кнопкой мыши и выберите "
                               "«Обновить поле» (или нажмите F9)."), BODY_FONT, 8, italic=True, color=GREY)

        doc.add_paragraph()
        t = doc.add_table(rows=1, cols=1)
        t.autofit = False
        set_table_fixed(t)
        cell = t.cell(0, 0)
        cell.width = Cm(17.1)
        shade_cell(cell, "EAF2FA")
        cell_margins(cell, top=160, bottom=160, left=170, right=170)
        head = cell.paragraphs[0]
        head.paragraph_format.space_after = Pt(8)
        set_run_font(head.add_run("Соглашения документа"), BODY_FONT, 10, bold=True, color=STEEL)
        for item in meta.CONVENTIONS:
            pi = cell.add_paragraph()
            pf = pi.paragraph_format
            pf.left_indent = Cm(0.55)
            pf.first_line_indent = Cm(-0.55)
            pf.space_after = Pt(5)
            set_run_font(pi.add_run("•  "), BODY_FONT, 9.3, color=BLUE)
            write_inline(pi, item, size=9.3)
        tblPr = t._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "bottom", "right"):
            el = OxmlElement("w:%s" % side)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "EAF2FA")
            borders.append(el)
        el = OxmlElement("w:left")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "18")
        el.set(qn("w:color"), "2E74B5")
        borders.append(el)
        insert_ordered(tblPr, borders, TBLPR_ORDER)
        doc.add_page_break()

    # -------------------------------------------------- блоки
    def h1(self, text, first=False):
        p = self.doc.add_paragraph(style="Heading 1")
        self._heading_runs(p, text, 16)
        if not first:
            p.paragraph_format.page_break_before = True
        paragraph_border(p, "bottom", color="2E74B5", size=12, space=4)

    def _heading_runs(self, paragraph, text, size):
        for kind, val in parse_inline(text):
            run = paragraph.add_run(val)
            set_run_font(run, BODY_FONT, size, bold=True,
                         color=STEEL if size >= 12 else BLUE)

    def h2(self, text):
        p = self.doc.add_paragraph(style="Heading 2")
        self._heading_runs(p, text, 12.5)

    def h3(self, text):
        p = self.doc.add_paragraph(style="Heading 3")
        self._heading_runs(p, text, 11)

    def para(self, text):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        write_inline(p, text)

    def bullets(self, items):
        for item in items:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pf = p.paragraph_format
            pf.left_indent = Cm(0.75)
            pf.first_line_indent = Cm(-0.35)
            pf.space_after = Pt(2.5)
            set_run_font(p.add_run("•\t"), BODY_FONT, 10.5, color=BLUE)
            write_inline(p, item)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)

    def numbers(self, items):
        for i, item in enumerate(items, 1):
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pf = p.paragraph_format
            pf.left_indent = Cm(0.85)
            pf.first_line_indent = Cm(-0.85)
            pf.space_after = Pt(2.5)
            set_run_font(p.add_run("%d.\t" % i), BODY_FONT, 10.5, bold=True, color=STEEL)
            write_inline(p, item)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)

    def code(self, lines):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(3)
        pf.space_after = Pt(7)
        pf.left_indent = Cm(0.15)
        pf.line_spacing = 1.0
        pf.keep_together = True
        shade_paragraph(p, "F3F4F6")
        paragraph_border(p, "left", color="2E74B5", size=18, space=6)
        paragraph_border(p, "top", color="D5D9E0", size=4, space=4)
        paragraph_border(p, "bottom", color="D5D9E0", size=4, space=4)
        paragraph_border(p, "right", color="D5D9E0", size=4, space=4)
        for i, line in enumerate(lines):
            run = p.add_run(line if line.strip() else " ")
            set_run_font(run, MONO_FONT, 7.8, color=RGBColor(0x20, 0x24, 0x2B))
            if i < len(lines) - 1:
                run.add_break(WD_BREAK.LINE)

    def note(self, text, kind="note"):
        fill = "EAF2FA" if kind == "note" else "FFF4E4"
        bar = "2E74B5" if kind == "note" else "C0551A"
        t = self.doc.add_table(rows=1, cols=1)
        t.autofit = False
        set_table_fixed(t)
        cell = t.cell(0, 0)
        cell.width = Cm(17.1)
        shade_cell(cell, fill)
        cell_margins(cell, top=110, bottom=110, left=150, right=150)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        write_inline(p, text, size=9.3)
        tblPr = t._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "bottom", "right"):
            el = OxmlElement("w:%s" % side)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), fill)
            borders.append(el)
        el = OxmlElement("w:left")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "18")
        el.set(qn("w:color"), bar)
        borders.append(el)
        insert_ordered(tblPr, borders, TBLPR_ORDER)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)

    def table(self, head, rows, widths):
        ncols = len(head)
        t = self.doc.add_table(rows=1, cols=ncols)
        t.autofit = False
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        set_table_fixed(t)
        total = sum(widths)
        widths_cm = [Cm(17.1 * w / total) for w in widths]

        hdr = t.rows[0]
        repeat_header(hdr)
        cant_split(hdr)
        for i, h in enumerate(head):
            cell = hdr.cells[i]
            cell.width = widths_cm[i]
            shade_cell(cell, "1F3864")
            cell_margins(cell)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            set_run_font(p.add_run(h), BODY_FONT, 8.6, bold=True,
                         color=RGBColor(0xFF, 0xFF, 0xFF))

        for r_idx, row in enumerate(rows):
            cells = t.add_row().cells
            cant_split(t.rows[-1])
            for i, val in enumerate(row):
                cell = cells[i]
                cell.width = widths_cm[i]
                cell_margins(cell)
                if r_idx % 2 == 1:
                    shade_cell(cell, "F6F8FB")
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                write_inline(p, str(val), size=8.6)
        self._table_borders(t)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)

    def params_table(self, _):
        head = ["Параметр", "Значение для вашего стенда", "Пример"]
        rows = [[k, "", v] for k, v in meta.PARAMS]
        self.table(head, rows, [26, 40, 34])

    def figure(self, item):
        path = os.path.join(ROOT, item["path"])
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run()
        run.add_picture(path, width=Cm(item.get("width_mm", 160) / 10.0))
        cap = self.doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(9)
        set_run_font(cap.add_run(item["caption"]), BODY_FONT, 8, italic=True, color=GREY)

    # -------------------------------------------------- сборка
    def build(self):
        self.cover()
        self.header_footer()
        self.toc()

        blocks = (content_1.BLOCKS + content_2.BLOCKS
                  + content_3.BLOCKS + content_4.BLOCKS)
        first_h1 = True
        for block in blocks:
            kind = block[0]
            payload = block[1] if len(block) > 1 else None
            if kind in ("h1", "h1nb"):
                self.h1(payload, first=(first_h1 or kind == "h1nb"))
                first_h1 = False
            elif kind == "h2":
                self.h2(payload)
            elif kind == "h3":
                self.h3(payload)
            elif kind == "p":
                self.para(payload)
            elif kind == "ul":
                self.bullets(payload)
            elif kind == "ol":
                self.numbers(payload)
            elif kind == "code":
                self.code(payload)
            elif kind in ("table", "checklist"):
                self.table(payload["head"], payload["rows"], payload["widths"])
            elif kind == "params_table":
                self.params_table(payload)
            elif kind == "note":
                self.note(payload, "note")
            elif kind == "warn":
                self.note(payload, "warn")
            elif kind == "figure":
                self.figure(payload)
            elif kind == "pagebreak":
                self.doc.add_page_break()

        # автообновление полей при открытии: оглавление собирается само и становится
        # кликабельным (w:updateFields должен стоять до w:compat — порядок элементов схемы)
        settings = self.doc.settings.element
        if settings.find(qn("w:updateFields")) is None:
            update = OxmlElement("w:updateFields")
            update.set(qn("w:val"), "true")
            compat = settings.find(qn("w:compat"))
            if compat is not None:
                compat.addprevious(update)
            else:
                settings.append(update)

        out = os.path.join(ROOT, "docs", "Инструкция_Ubuntu_Server_и_Kaspersky_Security_Center.docx")
        self.doc.save(out)
        print("DOCX:", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    Builder().build()
