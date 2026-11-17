# -*- coding: utf-8 -*-
"""Сборка PDF-версии инструкции (reportlab)."""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, Image,
                                KeepTogether, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import content_1, content_2, content_3, content_4  # noqa: E402
import meta  # noqa: E402
from textutil import to_rl_markup  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONTS = "/usr/share/fonts/truetype/dejavu"

pdfmetrics.registerFont(TTFont("DJV", os.path.join(FONTS, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DJV-B", os.path.join(FONTS, "DejaVuSans-Bold.ttf")))
# курсивные начертания DejaVu в системе отсутствуют — подставляем прямые
pdfmetrics.registerFont(TTFont("DJV-I", os.path.join(FONTS, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DJV-BI", os.path.join(FONTS, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("MONO", os.path.join(FONTS, "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("MONO-B", os.path.join(FONTS, "DejaVuSansMono-Bold.ttf")))
pdfmetrics.registerFontFamily("DJV", normal="DJV", bold="DJV-B", italic="DJV-I", boldItalic="DJV-BI")
pdfmetrics.registerFontFamily("MONO", normal="MONO", bold="MONO-B", italic="MONO", boldItalic="MONO-B")

STEEL = colors.HexColor("#1F3864")
BLUE = colors.HexColor("#2E74B5")
GREY = colors.HexColor("#5A6373")
LIGHTGREY = colors.HexColor("#D8DEE7")
CODE_BG = colors.HexColor("#F3F4F6")
CODE_BORDER = colors.HexColor("#D5D9E0")
ROW_ALT = colors.HexColor("#F6F8FB")
NOTE_BG = colors.HexColor("#EAF2FA")
WARN_BG = colors.HexColor("#FFF4E4")
WARN_BORDER = colors.HexColor("#C0551A")

PAGE_W, PAGE_H = A4
LM, RM, TM, BM = 21 * mm, 18 * mm, 20 * mm, 18 * mm
CONTENT_W = PAGE_W - LM - RM

ss = getSampleStyleSheet()

S = {}
S["body"] = ParagraphStyle("body", fontName="DJV", fontSize=9.4, leading=13.8,
                           alignment=TA_JUSTIFY, textColor=colors.HexColor("#1A1A1A"),
                           spaceAfter=4, allowWidows=0, allowOrphans=0)
S["h1"] = ParagraphStyle("h1", fontName="DJV-B", fontSize=16, leading=20, textColor=STEEL,
                         spaceBefore=9, spaceAfter=9, alignment=TA_LEFT)
S["h2"] = ParagraphStyle("h2", fontName="DJV-B", fontSize=12, leading=15.5, textColor=STEEL,
                         spaceBefore=13, spaceAfter=5, keepWithNext=1, alignment=TA_LEFT)
S["h3"] = ParagraphStyle("h3", fontName="DJV-B", fontSize=10.2, leading=13.5, textColor=BLUE,
                         spaceBefore=10, spaceAfter=4, keepWithNext=1, alignment=TA_LEFT)
S["code"] = ParagraphStyle("code", fontName="MONO", fontSize=7.6, leading=9.9,
                           textColor=colors.HexColor("#20242B"), alignment=TA_LEFT)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=11, bulletIndent=2,
                             spaceAfter=2.5, alignment=TA_LEFT)
S["num"] = ParagraphStyle("num", parent=S["body"], leftIndent=15, bulletIndent=0,
                          spaceAfter=2.5, alignment=TA_LEFT)
S["th"] = ParagraphStyle("th", fontName="DJV-B", fontSize=8.1, leading=10.4,
                         textColor=colors.white, alignment=TA_LEFT)
S["td"] = ParagraphStyle("td", fontName="DJV", fontSize=7.9, leading=10.2,
                         textColor=colors.HexColor("#1A1A1A"), alignment=TA_LEFT)
S["note"] = ParagraphStyle("note", parent=S["body"], fontSize=8.8, leading=12.4,
                           alignment=TA_LEFT, spaceAfter=0)
S["caption"] = ParagraphStyle("caption", fontName="DJV-I", fontSize=8, leading=10.6,
                              textColor=GREY, alignment=TA_CENTER, spaceBefore=3, spaceAfter=9)
S["toc1"] = ParagraphStyle("toc1", fontName="DJV-B", fontSize=9.2, leading=12.2, textColor=STEEL,
                           spaceBefore=2.0)
S["toc2"] = ParagraphStyle("toc2", fontName="DJV", fontSize=8.1, leading=10.6,
                           textColor=colors.HexColor("#242424"), leftIndent=13)


# ------------------------------------------------------------------ обложка
def cover(canv, doc):
    canv.saveState()
    canv.setFillColor(STEEL)
    canv.rect(0, PAGE_H - 78 * mm, PAGE_W, 78 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#2E74B5"))
    canv.rect(0, PAGE_H - 82 * mm, PAGE_W, 4 * mm, stroke=0, fill=1)

    canv.setFillColor(colors.white)
    canv.setFont("DJV-B", 10.5)
    canv.drawString(LM, PAGE_H - 30 * mm, "ИНСТРУКЦИЯ ПО РАЗВЁРТЫВАНИЮ")
    canv.setFont("DJV", 9)
    canv.drawString(LM, PAGE_H - 37 * mm, "Корпоративная система защиты информации")
    canv.setStrokeColor(colors.HexColor("#7FA6CE"))
    canv.setLineWidth(0.6)
    canv.line(LM, PAGE_H - 41 * mm, LM + 56 * mm, PAGE_H - 41 * mm)

    canv.setFont("DJV-B", 24)
    canv.setFillColor(colors.white)
    y = PAGE_H - 54 * mm
    for line in ["Установка Ubuntu Server 24.04 LTS", "и развёртывание",
                 "Kaspersky Security Center"]:
        canv.drawString(LM, y, line)
        y -= 10.5 * mm

    canv.setFillColor(colors.HexColor("#1A1A1A"))
    canv.setFont("DJV-B", 12.5)
    canv.drawString(LM, PAGE_H - 100 * mm, "Практическое руководство")
    canv.setFont("DJV", 10.5)
    canv.setFillColor(GREY)
    canv.drawString(LM, PAGE_H - 107 * mm,
                    "Kaspersky Security Center Linux 15.2 · MariaDB 10.11 · Web Console")

    # перечень содержания работ
    canv.setFillColor(STEEL)
    canv.setFont("DJV-B", 9.5)
    canv.drawString(LM, PAGE_H - 122 * mm, "В документе")
    yy = PAGE_H - 131 * mm
    canv.setFont("DJV", 9.6)
    for item in meta.COVER_ITEMS:
        canv.setFillColor(BLUE)
        canv.rect(LM + 0.6 * mm, yy + 1.1 * mm, 2.0 * mm, 2.0 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.HexColor("#2B2F36"))
        canv.drawString(LM + 6 * mm, yy, item)
        yy -= 7.4 * mm

    # рамка сведений
    box_y = 62 * mm
    canv.setStrokeColor(LIGHTGREY)
    canv.setLineWidth(0.8)
    canv.rect(LM, box_y, CONTENT_W, 52 * mm, stroke=1, fill=0)
    rows = [
        ("Код документа", meta.DOC_CODE),
        ("Версия документа", meta.DOC_VERSION),
        ("Дата выпуска", meta.DOC_DATE),
        ("Статус", meta.DOC_STATUS),
        ("Область применения", "Ubuntu Server 24.04 LTS, KSC Linux 15.2"),
        ("Разработал", meta.DOC_AUTHOR),
    ]
    canv.setFont("DJV", 9)
    yy = box_y + 44 * mm
    for k, v in rows:
        canv.setFillColor(GREY)
        canv.drawString(LM + 7 * mm, yy, k)
        canv.setFillColor(colors.HexColor("#1A1A1A"))
        canv.drawString(LM + 55 * mm, yy, v)
        yy -= 7.6 * mm

    canv.setFillColor(GREY)
    canv.setFont("DJV", 7.8)
    canv.drawString(LM, 45 * mm,
                    "Документ содержит пошаговые команды. Перед применением проверьте параметры "
                    "стенда (раздел 2.1).")
    canv.drawString(LM, 40 * mm,
                    "Kaspersky Security Center является товарным знаком АО «Лаборатория Касперского».")
    canv.restoreState()


# ------------------------------------------------------------------ колонтитулы
def body_page(canv, doc):
    canv.saveState()
    canv.setStrokeColor(LIGHTGREY)
    canv.setLineWidth(0.6)
    canv.line(LM, PAGE_H - 13 * mm, PAGE_W - RM, PAGE_H - 13 * mm)
    canv.setFont("DJV", 7.4)
    canv.setFillColor(GREY)
    canv.drawString(LM, PAGE_H - 11 * mm, "%s · %s" % (meta.DOC_CODE, meta.DOC_TITLE))
    canv.drawRightString(PAGE_W - RM, PAGE_H - 11 * mm, "Версия %s от %s" % (meta.DOC_VERSION, meta.DOC_DATE))
    canv.restoreState()


class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.setFont("DJV", 7.6)
                self.setFillColor(GREY)
                self.drawCentredString(PAGE_W / 2.0, 11 * mm,
                                       "Стр. %d из %d" % (self._pageNumber, total))
            super().showPage()
        super().save()


# ------------------------------------------------------------------ строители
def code_block(lines):
    txt = "<br/>".join(
        (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
         if line.strip() else "&nbsp;")
        for line in lines)
    p = Paragraph(txt, S["code"])
    t = Table([[p]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, CODE_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [t, Spacer(1, 6)]


def note_block(text, kind="note"):
    style = S["note"]
    p = Paragraph(to_rl_markup(text), style)
    bg = NOTE_BG if kind == "note" else WARN_BG
    bar = BLUE if kind == "note" else WARN_BORDER
    t = Table([[p]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, bar),
        ("BOX", (0, 0), (-1, -1), 0.4, bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 7)]


def data_table(head, rows, widths):
    total = sum(widths)
    cols = [CONTENT_W * w / total for w in widths]
    data = [[Paragraph(to_rl_markup(h), S["th"]) for h in head]]
    for r in rows:
        data.append([Paragraph(to_rl_markup(str(c)), S["td"]) for c in r])
    t = Table(data, colWidths=cols, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#C6CEDA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 8)]


def params_table(_):
    head = ["Параметр", "Значение для вашего стенда", "Пример"]
    rows = [[k, "", v] for k, v in meta.PARAMS]
    total = 26 + 40 + 34
    cols = [CONTENT_W * 26 / total, CONTENT_W * 40 / total, CONTENT_W * 34 / total]
    data = [[Paragraph(to_rl_markup(h), S["th"]) for h in head]]
    for k, blank, v in rows:
        data.append([Paragraph(to_rl_markup(k), S["td"]), "", Paragraph(to_rl_markup(v), S["td"])])
    t = Table(data, colWidths=cols, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#C6CEDA")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (1, 1), (1, -1), colors.HexColor("#FBFBFD")),
    ]
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 8)]


def figure_block(item):
    path = os.path.join(ROOT, item["path"])
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    width = item.get("width_mm", 160) * mm
    height = width * h / w
    img = Image(path, width=width, height=height)
    cap = Paragraph(item["caption"], S["caption"])
    return [KeepTogether([img, cap])]


class Doc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ("h1", "h2"):
                txt = flowable.getPlainText()
                key = "h-%d" % id(flowable)
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(txt, key, level=0 if style == "h1" else 1, closed=False)
                self.notify("TOCEntry", (0 if style == "h1" else 1, txt, self.page, key))


def build():
    all_blocks = (content_1.BLOCKS + content_2.BLOCKS
                  + content_3.BLOCKS + content_4.BLOCKS)

    out = os.path.join(ROOT, "docs", "Инструкция_Ubuntu_Server_и_Kaspersky_Security_Center.pdf")
    doc = Doc(out, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
              title="%s — %s" % (meta.DOC_TITLE, meta.DOC_SUBTITLE),
              author=meta.DOC_AUTHOR, subject=meta.DOC_SUBTITLE,
              creator="Arena.ai Agent Mode", keywords="Ubuntu, Kaspersky Security Center, KSC Linux")

    frame_cover = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="cover")
    frame_body = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="body",
                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[frame_cover], onPage=cover),
        PageTemplate(id="Body", frames=[frame_body], onPage=body_page),
    ])

    story = [NextPageTemplate("Body"), Spacer(1, 1), PageBreak()]

    # Оглавление
    toc = TableOfContents(tableStyle=TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    toc.levelStyles = [S["toc1"], S["toc2"]]
    toc.dotsMinLevel = 0
    story.append(Paragraph("Содержание", ParagraphStyle(
        "toctitle", fontName="DJV-B", fontSize=16, leading=20, textColor=STEEL, spaceAfter=12)))
    story.append(Spacer(1, 4))
    story.append(toc)

    conv_lines = "<br/>".join("•&nbsp;&nbsp;" + to_rl_markup(item) for item in meta.CONVENTIONS)
    conv = Paragraph(
        '<font name="DJV-B" size="9.6" color="#1F3864">Соглашения документа</font><br/><br/>'
        + conv_lines, S["note"])
    box = Table([[conv]], colWidths=[CONTENT_W])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, BLUE),
        ("BOX", (0, 0), (-1, -1), 0.4, NOTE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(Spacer(1, 14))
    story.append(box)
    story.append(PageBreak())

    for idx, block in enumerate(all_blocks):
        kind = block[0]
        payload = block[1] if len(block) > 1 else None

        if kind in ("h1", "h1nb"):
            if idx > 0 and kind == "h1":
                story.append(CondPageBreak(95 * mm))
            story.append(Paragraph(to_rl_markup(payload), S["h1"]))
            story.append(Table([[""]], colWidths=[CONTENT_W], rowHeights=[2]))
            story[-1].setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE),
                                           ("LINEBELOW", (0, 0), (-1, -1), 0, colors.white),
                                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            story.append(Spacer(1, 9))
        elif kind == "h2":
            if idx > 0:
                story.append(CondPageBreak(38 * mm))
            story.append(Paragraph(to_rl_markup(payload), S["h2"]))
        elif kind == "h3":
            story.append(CondPageBreak(32 * mm))
            story.append(Paragraph(to_rl_markup(payload), S["h3"]))
        elif kind == "p":
            story.append(Paragraph(to_rl_markup(payload), S["body"]))
        elif kind == "ul":
            for item in payload:
                story.append(Paragraph(to_rl_markup(item), S["bullet"], bulletText="•"))
            story.append(Spacer(1, 4))
        elif kind == "ol":
            for i, item in enumerate(payload, 1):
                story.append(Paragraph(to_rl_markup(item), S["num"], bulletText="%d." % i))
            story.append(Spacer(1, 4))
        elif kind == "code":
            story.extend(code_block(payload))
        elif kind == "table":
            story.extend(data_table(payload["head"], payload["rows"], payload["widths"]))
        elif kind == "params_table":
            story.extend(params_table(payload))
        elif kind == "checklist":
            story.extend(data_table(payload["head"], payload["rows"], payload["widths"]))
        elif kind == "note":
            story.extend(note_block(payload, "note"))
        elif kind == "warn":
            story.extend(note_block(payload, "warn"))
        elif kind == "figure":
            story.extend(figure_block(payload))
        elif kind == "pagebreak":
            story.append(PageBreak())

    while story and isinstance(story[-1], Spacer):
        story.pop()

    doc.multiBuild(story, canvasmaker=NumberedCanvas)
    print("PDF:", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    build()
