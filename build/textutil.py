# -*- coding: utf-8 -*-
"""Разбор встроенной разметки: `код`, **жирный**, *курсив*."""
import re

TOKEN = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)")
URL = re.compile(r"(https?://[^\s,;)]+)")


def _split_urls(text):
    """Выделяет URL из обычного текста: ('t'|'url', строка)."""
    parts = []
    pos = 0
    for m in URL.finditer(text):
        if m.start() > pos:
            parts.append(("t", text[pos:m.start()]))
        parts.append(("url", m.group(0)))
        pos = m.end()
    if pos < len(text):
        parts.append(("t", text[pos:]))
    return parts


def parse_inline(text):
    """Возвращает список кортежей (стиль, текст), стиль: t | b | i | c | url."""
    out = []
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append(("c", part[1:-1]))
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(("b", part[2:-2]))
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append(("i", part[1:-1]))
        else:
            out.extend(_split_urls(part))
    return out


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def to_rl_markup(text, code_color="#8B2E00"):
    """Преобразование в разметку reportlab Paragraph."""
    buf = []
    for kind, val in parse_inline(text):
        esc = xml_escape(val)
        if kind == "c":
            buf.append('<font face="MONO" size="8" color="%s">%s</font>'
                       % (code_color, esc))
        elif kind == "b":
            buf.append("<b>%s</b>" % esc)
        elif kind == "i":
            buf.append("<i>%s</i>" % esc)
        elif kind == "url":
            buf.append('<link href="%s" color="#1F5FA8">%s</link>' % (esc, esc))
        else:
            buf.append(esc)
    return "".join(buf)
