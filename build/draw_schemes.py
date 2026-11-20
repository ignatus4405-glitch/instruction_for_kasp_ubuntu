# -*- coding: utf-8 -*-
"""Генерация схем развёртывания (PNG) для PDF и DOCX."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F = lambda size, bold=False: ImageFont.truetype(
    os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

STEEL = "#1F3864"
BLUE = "#2E74B5"
LIGHT = "#EAF1F8"
WHITE = "#FFFFFF"
GREY = "#5A6373"
ACCENT = "#C0551A"

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def text_center(d, cx, y, txt, font, fill=STEEL):
    w = d.textlength(txt, font=font)
    d.text((cx - w / 2, y), txt, font=font, fill=fill)


def rbox(d, xy, radius=14, fill=WHITE, outline=BLUE, width=3):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow(d, start, end, color=BLUE):
    d.line([start, end], fill=color, width=3)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    L, W = 17, 8
    p1 = (end[0] - L * math.cos(ang) + W * math.sin(ang),
          end[1] - L * math.sin(ang) - W * math.cos(ang))
    p2 = (end[0] - L * math.cos(ang) - W * math.sin(ang),
          end[1] - L * math.sin(ang) + W * math.cos(ang))
    d.polygon([end, p1, p2], fill=color)


def label(d, x, y, txt, font=None, anchor="left", color=ACCENT):
    font = font or F(18)
    w = d.textlength(txt, font=font)
    pad = 5
    if anchor == "center":
        x0 = x - w / 2
    elif anchor == "right":
        x0 = x - w
    else:
        x0 = x
    d.rectangle([x0 - pad, y - pad + 3, x0 + w + pad, y + 21 + pad - 3], fill=WHITE)
    d.text((x0, y), txt, font=font, fill=color)


def scheme(path):
    W, H = 1800, 1060
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    srv = (600, 40, 1200, 940)
    rbox(d, srv, radius=18, fill=LIGHT, outline=STEEL, width=4)
    text_center(d, 900, 66, "Сервер KSC — ksc01.company.local", F(28, True), STEEL)
    text_center(d, 900, 106, "192.168.10.10 · Ubuntu Server 26.10", F(20), GREY)

    comps = [
        (["KSC Web Console"], ["Node.js · порт 8080 (HTTPS)"], 150),
        (["Сервер администрирования"], ["klserver · 13000/TLS, 13299, 14000 · kliam_srv"], 360),
        (["СУБД MariaDB 11.8"], ["БД kav, iamdb · порт 3306 · только 127.0.0.1"], 580),
        (["Агент администрирования", "(серверная часть)"], ["klnagent · 15000/UDP, 13000/TCP"], 790),
    ]
    boxes = []
    for titles, subs, y in comps:
        box = (650, y, 1150, y + 110)
        rbox(d, box, radius=12, fill=WHITE, outline=BLUE, width=3)
        if len(titles) == 1:
            text_center(d, 900, y + 22, titles[0], F(23, True))
            text_center(d, 900, y + 62, subs[0], F(19), GREY)
        else:
            text_center(d, 900, y + 14, titles[0], F(22, True))
            text_center(d, 900, y + 44, titles[1], F(22, True))
            text_center(d, 900, y + 78, subs[0], F(18), GREY)
        boxes.append(box)

    # внутренние связи
    arrow(d, (900, boxes[0][3]), (900, boxes[1][1]))
    label(d, 918, 296, "13299 + IAM 4444/9050", F(17), color=GREY)
    arrow(d, (900, boxes[1][3]), (900, boxes[2][1]))
    label(d, 918, 506, "SQL · 3306", F(17))

    # рабочие места администраторов
    wbox = (60, 120, 520, 270)
    rbox(d, wbox, radius=14, fill=WHITE, outline=BLUE, width=3)
    text_center(d, 290, 146, "Рабочие места", F(24, True))
    text_center(d, 290, 178, "администраторов", F(24, True))
    text_center(d, 290, 220, "браузер Chrome / Edge /", F(19), GREY)
    text_center(d, 290, 246, "Firefox ESR", F(19), GREY)
    arrow(d, (520, 195), (650, 195))
    label(d, 527, 160, "8080 + 4444", F(16))

    # управляемые устройства
    dbox = (1280, 340, 1740, 510)
    rbox(d, dbox, radius=14, fill=WHITE, outline=ACCENT, width=3)
    text_center(d, 1510, 366, "Управляемые устройства", F(23, True), ACCENT)
    for i, line in enumerate(["Windows · Linux · macOS",
                              "Агент администрирования",
                              "защитные приложения KES"]):
        text_center(d, 1510, 410 + i * 30, line, F(19), GREY)
    arrow(d, (1280, 415), (1160, 415))
    label(d, 1180, 378, "13000/TLS", F(17))

    # точки распространения
    pbox = (1280, 760, 1740, 920)
    rbox(d, pbox, radius=14, fill=WHITE, outline=BLUE, width=3)
    text_center(d, 1510, 786, "Точки распространения", F(23, True))
    text_center(d, 1510, 828, "Агент администрирования", F(19), GREY)
    text_center(d, 1510, 856, "в удалённых сегментах сети", F(19), GREY)
    arrow(d, (1280, 845), (1160, 845))
    label(d, 1180, 808, "13000/TCP", F(17))

    d.line([(60, 960), (520, 960)], fill=BLUE, width=4)
    d.text((60, 974), "Все компоненты — на одной виртуальной машине. Порты указаны по умолчанию.",
           font=F(18), fill=GREY)
    d.text((60, 1004), "Наружу: 8080 и 4444 (рабочие места администраторов), 13000 (агенты); 3306, 13299, 9050 — только 127.0.0.1.",
           font=F(18), fill=GREY)

    img.save(path, dpi=(200, 200))


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    scheme(os.path.join(OUT_DIR, "scheme.png"))
    print("schemes written")
