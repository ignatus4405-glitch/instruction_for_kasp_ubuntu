# -*- coding: utf-8 -*-
"""Иллюстрации для инструкции: маршрут, порты, экраны установщика, Web Console,
разметка диска, резервное копирование. Все рисунки — схемы, а не снимки экрана."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

from draw_schemes import (F, ACCENT, BLUE, GREY, LIGHT, OUT_DIR, STEEL, WHITE,
                          arrow, label, rbox, text_center)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
MONO = lambda size: ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSansMono.ttf"), size)
MONO_B = lambda size: ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf"), size)

PALE = "#F4F6FA"
BORDER = "#C6CEDA"
SOFT = "#E8EDF5"
DARK = "#0F1419"
TERM_BG = "#12171D"
TERM_LINE = "#2A3546"
TERM_TXT = "#DCE3EC"
TERM_DIM = "#8B97A8"
TERM_SEL = "#1F3864"
GREEN = "#2E7D32"
ORANGE = "#C0551A"
YELLOW = "#F2C24B"


def wrap(d, txt, font, max_w):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if d.textlength(probe, font=font) <= max_w or not cur:
            cur = probe
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def dashed_rbox(d, xy, radius=14, outline=BLUE, width=3, dash=12, gap=8):
    """Пунктирная рамка (приблизительно) — рисуем по сторонам."""
    x0, y0, x1, y1 = xy
    for x in range(x0 + radius, x1 - radius, dash + gap):
        d.line([(x, y0), (min(x + dash, x1 - radius), y0)], fill=outline, width=width)
        d.line([(x, y1), (min(x + dash, x1 - radius), y1)], fill=outline, width=width)
    for y in range(y0 + radius, y1 - radius, dash + gap):
        d.line([(x0, y), (x0, min(y + dash, y1 - radius))], fill=outline, width=width)
        d.line([(x1, y), (x1, min(y + dash, y1 - radius))], fill=outline, width=width)


# ------------------------------------------------------------------ 1. маршрут
def roadmap(path):
    W, H = 1700, 300
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    steps = [
        ("Подготовка", "раздел 2"),
        ("Ubuntu Server\n24.04 LTS", "раздел 3"),
        ("СУБД MariaDB", "раздел 4"),
        ("Сервер\nадминистрирования", "раздел 5"),
        ("Web Console", "раздел 6"),
        ("Первичная\nнастройка", "раздел 7"),
        ("Эксплуатация", "раздел 8"),
    ]
    n = len(steps)
    margin = 40
    col = (W - 2 * margin) / n
    cy = 70
    r = 30

    d.line([(margin + col / 2, cy), (W - margin - col / 2, cy)], fill=BLUE, width=5)

    for i, (title, ref) in enumerate(steps):
        cx = margin + col * (i + 0.5)
        if i < n - 1:
            arrow(d, (cx + r + 10, cy), (cx + col - r - 14, cy), color=BLUE)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=STEEL, outline=WHITE, width=5)
        text_center(d, cx, cy - 15, str(i + 1), F(26, True), WHITE)

        lines = title.split("\n")
        y = cy + 52 + (2 - len(lines)) * 15
        for line in lines:
            text_center(d, cx, y, line, F(21, True), STEEL)
            y += 28
        text_center(d, cx, cy + 52 + 2 * 28 + 8, ref, F(18), GREY)

    img.save(path, dpi=(200, 200))


# ------------------------------------------------------------------ 2. порты
def ports(path):
    W, H = 1700, 640
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # клиенты
    def client(xy, title, sub, accent=BLUE):
        rbox(d, xy, radius=14, fill=WHITE, outline=accent, width=3)
        x0, y0, x1, y1 = xy
        cx = (x0 + x1) / 2
        ty = y0 + 22
        for line in title.split("\n"):
            text_center(d, cx, ty, line, F(21, True), accent if accent == ACCENT else STEEL)
            ty += 29
        ty += 6
        for line in sub.split("\n"):
            text_center(d, cx, ty, line, F(17), GREY)
            ty += 24

    client((40, 70, 340, 210), "Рабочие места", "браузер Chrome / Edge /\nFirefox ESR")
    client((40, 400, 340, 540), "Управляемые\nустройства", "Агент администрирования\nWindows · Linux · macOS", ACCENT)

    # сервер
    rbox(d, (400, 30, 1660, 545), radius=18, fill=LIGHT, outline=STEEL, width=4)
    d.text((432, 52), "Сервер KSC — ksc01.company.local · 192.168.10.10 · Ubuntu Server 24.04 LTS",
           font=F(23, True), fill=STEEL)

    # Web Console
    rbox(d, (440, 120, 760, 300), radius=12, fill=WHITE, outline=BLUE, width=3)
    text_center(d, 600, 140, "KSC Web Console", F(22, True), STEEL)
    text_center(d, 600, 176, "Node.js", F(18), GREY)
    text_center(d, 600, 216, "8080/TCP (HTTPS)", F(23, True), ACCENT)
    text_center(d, 600, 248, "/var/opt/kaspersky/", F(15), GREY)
    text_center(d, 600, 270, "ksc-web-console", F(15), GREY)

    # службы
    rbox(d, (870, 120, 1620, 300), radius=12, fill=WHITE, outline=BLUE, width=3)
    text_center(d, 1245, 134, "Службы Kaspersky Security Center (klserver)", F(21, True), STEEL)
    rows = [("kladminserver_srv", "14000/TCP — внутренний порт"),
            ("klactprx_srv", "13299/TCP+TLS — Web Console, OpenAPI"),
            ("klwebsrv_srv", "внутренний веб-сервер"),
            ("Агенты администрирования", "13000/TCP+TLS · 15000/UDP")]
    y = 166
    for name, note in rows:
        d.text((896, y), name, font=F(18, True), fill=STEEL)
        d.text((1250, y + 2), note, font=MONO(15), fill=GREY)
        y += 33

    # СУБД
    rbox(d, (870, 370, 1240, 500), radius=12, fill=WHITE, outline=BLUE, width=3)
    text_center(d, 1055, 388, "СУБД MariaDB 10.11 · БД kav", F(20, True), STEEL)
    text_center(d, 1055, 424, "3306/TCP", F(24, True), ACCENT)
    text_center(d, 1055, 462, "только 127.0.0.1", F(17), GREY)

    # вариант Б
    rbox(d, (1300, 370, 1620, 500), radius=12, fill=WHITE, outline=ACCENT, width=3)
    text_center(d, 1460, 386, "Web Console", F(20, True), ACCENT)
    text_center(d, 1460, 414, "(вариант Б)", F(18), GREY)
    text_center(d, 1460, 446, "kws01 · 192.168.10.11", F(17), GREY)
    text_center(d, 1460, 472, "8080/TCP", F(17), GREY)

    # связи
    arrow(d, (340, 140), (440, 140))
    label(d, 344, 100, "8080/TLS", F(17))

    arrow(d, (760, 170), (870, 170))
    label(d, 764, 138, "13299/TLS", F(16))

    arrow(d, (1055, 300), (1055, 370))
    label(d, 1072, 318, "SQL · 3306", F(17))

    arrow(d, (1460, 370), (1460, 300))
    label(d, 1476, 330, "13299/TLS", F(16))

    # устройства — к службам (ломаная)
    d.line([(340, 470), (815, 470)], fill=BLUE, width=3)
    d.line([(815, 470), (815, 250)], fill=BLUE, width=3)
    arrow(d, (815, 250), (870, 250))
    d.text((352, 424), "13000/TCP+TLS", font=F(17), fill=ACCENT)
    d.text((352, 448), "15000/UDP", font=F(17), fill=ACCENT)

    d.text((40, 580), "Порты указаны по умолчанию; изменяются в файле ответов (PORT_SRV, PORT_SRV_SSL, PORT_KLOAPI, PORT_GUI).",
           font=F(17), fill=GREY)
    d.text((40, 606), "Полная таблица портов — приложение А.", font=F(17), fill=GREY)

    img.save(path, dpi=(200, 200))


# ------------------------------------------------------------------ 3. экран: сеть
def _terminal(d, box, title, subtitle=""):
    rbox(d, box, radius=10, fill=TERM_BG, outline=TERM_LINE, width=3)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 + 3, y0 + 3, x1 - 3, y0 + 62], radius=8, fill=STEEL)
    d.text((x0 + 26, y0 + 18), title, font=F(24, True), fill=WHITE)
    if subtitle:
        tw = d.textlength(subtitle, font=F(19))
        d.text((x1 - 26 - tw, y0 + 22), subtitle, font=F(19), fill="#BFD0E4")


def installer_network(path):
    W, H = 1500, 900
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    box = (30, 20, W - 30, H - 20)
    _terminal(d, box, "Network configuration", "Ubuntu Server 24.04 LTS — Subiquity")

    # список интерфейсов
    d.text((70, 104), "Интерфейс", font=MONO_B(19), fill=TERM_DIM)
    d.text((380, 104), "Адрес", font=MONO_B(19), fill=TERM_DIM)
    d.text((840, 104), "Метод", font=MONO_B(19), fill=TERM_DIM)
    d.text((1080, 104), "Состояние", font=MONO_B(19), fill=TERM_DIM)
    d.line([(70, 136), (W - 70, 136)], fill=TERM_LINE, width=2)

    d.rectangle([62, 150, W - 62, 200], fill=TERM_SEL)
    d.text((70, 160), "ens18", font=MONO_B(21), fill=WHITE)
    d.text((380, 160), "192.168.10.10/24", font=MONO(21), fill=WHITE)
    d.text((840, 160), "static", font=MONO(21), fill=WHITE)
    d.text((1080, 160), "UP", font=MONO(21), fill=WHITE)
    d.text((70, 218), "ens19 (не подключён)", font=MONO(20), fill=TERM_DIM)

    d.line([(70, 262), (W - 70, 262)], fill=TERM_LINE, width=2)
    d.text((70, 282), "Edit IPv4 configuration  —  manual", font=F(22, True), fill=WHITE)

    fields = [("Subnet", "192.168.10.0/24"),
              ("Address", "192.168.10.10"),
              ("Gateway", "192.168.10.1"),
              ("Name servers", "192.168.10.2,192.168.10.3"),
              ("Search domains", "company.local")]
    y = 340
    for name, val in fields:
        d.text((90, y), name, font=MONO(20), fill=TERM_TXT)
        d.rectangle([470, y - 6, 1290, y + 32], outline=TERM_LINE, width=2, fill="#1A222C")
        d.text((490, y), val, font=MONO_B(20), fill=YELLOW)
        y += 74

    # кнопки
    d.rounded_rectangle([90, 740, 300, 792], radius=6, fill=TERM_SEL, outline=BLUE, width=3)
    d.text((140, 754), "Save", font=F(22, True), fill=WHITE)
    d.rounded_rectangle([330, 740, 520, 792], radius=6, fill="#1A222C", outline=TERM_LINE, width=2)
    d.text((372, 754), "Cancel", font=F(22), fill=TERM_TXT)
    d.text((560, 756), "Tab — переход по полям, Enter — подтверждение", font=F(18), fill=TERM_DIM)

    d.text((90, 820), "После выбора интерфейса: Edit IPv4 → Manual. Значения соответствуют таблице раздела 3.4.",
           font=F(18), fill=TERM_DIM)

    img.save(path, dpi=(200, 200))


# ------------------------------------------------------------------ 4. разметка диска
def storage(path):
    W, H = 1700, 556
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    left, right = 60, W - 60
    total_w = right - left
    EFI_COL = "#9FB0C6"
    VAR_COL = "#5D93C8"

    def bar(y, parts, height=88):
        """parts: (name, size, fill, txt_col, frac, min_w)"""
        fracs = [p[4] for p in parts]
        widths = [total_w * f / sum(fracs) for f in fracs]
        for i, p in enumerate(parts):
            min_w = p[5] if len(p) > 5 else 0
            if widths[i] < min_w:
                deficit = min_w - widths[i]
                widths[i] = min_w
                j = widths.index(max(widths))
                widths[j] -= deficit
        x = left
        for p, w in zip(parts, widths):
            name, size, fill, txt_col = p[0], p[1], p[2], p[3]
            d.rectangle([x, y, x + w, y + height], fill=fill, outline=WHITE, width=4)
            if w >= 190:
                text_center(d, x + w / 2, y + 16, name, F(21, True), txt_col)
                text_center(d, x + w / 2, y + 48, size, F(19), txt_col)
            elif w >= 100:
                text_center(d, x + w / 2, y + 20, name, F(16, True), txt_col)
                text_center(d, x + w / 2, y + 50, size, F(15), txt_col)
            elif w >= 58:
                text_center(d, x + w / 2, y + 30, size, F(15), txt_col)
            x += w

    d.text((left, 34), "Диск /dev/sda — 120 ГБ (GPT, UEFI)", font=F(23, True), fill=STEEL)
    bar(74, [("/boot/efi", "1 ГБ", EFI_COL, STEEL, 1, 95),
             ("LVM: группа ubuntu-vg", "119 ГБ", STEEL, WHITE, 119, 0)])

    d.text((left, 196), "Группа томов ubuntu-vg — логические тома", font=F(23, True), fill=STEEL)
    bar(236, [("ubuntu-lv  /", "60 ГБ · ext4", BLUE, WHITE, 60, 0),
              ("var-lv  /var", "40 ГБ · ext4", VAR_COL, WHITE, 40, 0),
              ("swap", "12 ГБ", ACCENT, WHITE, 12, 0),
              ("свободно", "7 ГБ", SOFT, GREY, 7, 0)])

    items = [
        (EFI_COL, "/boot/efi", "1 ГБ, FAT32 — обязателен при загрузке UEFI (для Legacy BIOS не создаётся)"),
        (BLUE, "/ (ubuntu-lv)", "60 ГБ — ОС, пакеты KSC (/opt/kaspersky/ksc64), журналы, обновления"),
        (VAR_COL, "/var (var-lv)", "40 ГБ — БД и данные: /var/lib/mysql, /var/opt/kaspersky/klnagent_srv"),
        (ACCENT, "swap", "12 ГБ — не менее 1,5 × объёма ОЗУ (при 8 ГБ ОЗУ)"),
        (SOFT, "свободно", "7 ГБ — резерв для роста БД и обновлений; размеры не в масштабе"),
    ]
    y = 366
    for col, name, note in items:
        d.rectangle([left, y + 8, left + 18, y + 26], fill=col, outline=BORDER)
        d.text((left + 32, y), name, font=F(21, True), fill=STEEL)
        d.text((left + 262, y), note, font=F(20), fill=GREY)
        y += 38

    img.save(path, dpi=(200, 200))


# ------------------------------------------------------------------ 5. Web Console
def webconsole(path):
    W, H = 1600, 700
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # окно браузера
    rbox(d, (20, 20, W - 20, H - 20), radius=14, fill=WHITE, outline=BORDER, width=3)
    d.rounded_rectangle([23, 23, W - 23, 92], radius=12, fill="#E3E7EC")
    d.rectangle([23, 74, W - 23, 92], fill="#E3E7EC")
    for i, c in enumerate(["#E56B6F", "#E3B24B", "#7FB069"]):
        d.ellipse([48 + i * 34, 44, 70 + i * 34, 66], fill=c)
    d.rounded_rectangle([170, 38, 1180, 78], radius=18, fill=WHITE, outline=BORDER, width=2)
    d.text((196, 46), "https://ksc01.company.local:8080", font=MONO(19), fill="#3A4453")
    d.text((1200, 46), "Защищено · самоподписанный сертификат", font=F(16), fill=GREEN)

    # боковое меню
    d.rectangle([23, 92, 350, H - 23], fill=STEEL)
    d.text((56, 118), "Kaspersky", font=F(24, True), fill=WHITE)
    d.text((56, 150), "Security Center", font=F(24, True), fill=WHITE)
    d.line([(56, 196), (320, 196)], fill="#3B5580", width=2)
    menu = ["Мониторинг", "Устройства", "Пользователи и роли", "Инсталляционные пакеты",
            "Ключи", "Политики", "Задачи", "Отчёты", "События", "Параметры"]
    y = 218
    for i, item in enumerate(menu):
        if i == 0:
            d.rectangle([40, y - 6, 334, y + 34], fill="#2E4F80")
        d.text((56, y), item, font=F(19), fill=WHITE if i == 0 else "#C7D3E4")
        y += 46

    # заголовок раздела
    d.text((390, 116), "Мониторинг", font=F(28, True), fill=STEEL)
    d.text((390, 156), "ksc01.company.local · Сервер администрирования 15.2 · лицензия активна",
           font=F(17), fill=GREY)

    # карточки
    cards = [("Устройства", "128", "защищено 124", STEEL),
             ("Критические события", "0", "за 24 часа", GREEN),
             ("Обновление баз", "сегодня", "02:15 · актуально", STEEL),
             ("Задачи", "12", "выполнено 12", STEEL)]
    x = 390
    cw = (W - 60 - 390 - 3 * 24) / 4
    for title, big, sub, col in cards:
        rbox(d, (x, 200, x + cw, 350), radius=12, fill=PALE, outline=BORDER, width=2)
        d.text((x + 20, 212), title, font=F(18), fill=GREY)
        d.text((x + 20, 250), big, font=F(34, True), fill=col)
        d.text((x + 20, 306), sub, font=F(17), fill=GREY)
        x += cw + 24

    # таблица устройств
    d.text((390, 392), "Устройства с критическими событиями", font=F(20, True), fill=STEEL)
    d.rectangle([390, 432, W - 60, 478], fill=SOFT)
    d.text((410, 444), "Устройство", font=F(17, True), fill=STEEL)
    d.text((700, 444), "Группа", font=F(17, True), fill=STEEL)
    d.text((960, 444), "Состояние", font=F(17, True), fill=STEEL)
    rows = [("pc-01", "Рабочие станции", "защищено, событий нет"),
            ("srv-db-01", "Серверы", "защищено, событий нет")]
    for i, r in enumerate(rows):
        y = 478 + i * 56
        d.rectangle([390, y, W - 60, y + 56], outline=BORDER, width=1)
        d.text((410, y + 18), r[0], font=MONO(17), fill=STEEL)
        d.text((700, y + 18), r[1], font=F(17), fill=GREY)
        d.text((960, y + 18), r[2], font=F(17), fill=GREEN)

    d.text((390, 616), "Состав разделов меню слева может отличаться в зависимости от роли и прав пользователя.",
           font=F(18), fill=GREY)

    img.save(path, dpi=(200, 200))


# ------------------------------------------------------------------ 6. резервное копирование
def backup(path):
    W, H = 1700, 540
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    def box(xy, title, sub, accent=BLUE, fill=WHITE):
        rbox(d, xy, radius=12, fill=fill, outline=accent, width=3)
        x0, y0, x1, y1 = xy
        cx = (x0 + x1) / 2
        ty = y0 + 26
        for line in title.split("\n"):
            text_center(d, cx, ty, line, F(23, True), STEEL)
            ty += 30
        ty += 6
        for line in sub.split("\n"):
            text_center(d, cx, ty, line, F(19), GREY)
            ty += 26

    box((40, 50, 470, 185), "СУБД MariaDB", "БД kav · /var/lib/mysql")
    box((1000, 50, 1430, 185), "/backup/mariadb", "kav_ГГГГ-ММ-ДД.sql.gz\nхранение 14 дней", ACCENT)
    arrow(d, (470, 118), (1000, 118))
    label(d, 560, 78, "mariadb-dump, cron 02:30", F(19))

    box((40, 265, 470, 400), "Сервер администрирования", "/var/opt/kaspersky/ksc64")
    box((1000, 265, 1430, 400), "/backup/ksc", "klbackup -savepwd\nне менее 10 копий", ACCENT)
    arrow(d, (470, 333), (1000, 333))
    label(d, 620, 292, "klbackup, cron 02:40", F(19))

    box((1490, 160, 1660, 290), "Внешний\nноситель", "", STEEL, LIGHT)
    arrow(d, (1430, 118), (1490, 190))
    arrow(d, (1430, 333), (1490, 262))
    d.text((1470, 300), "вывоз копий", font=F(17), fill=GREY)
    d.text((1470, 322), "на отдельный", font=F(17), fill=GREY)
    d.text((1470, 344), "сервер хранения", font=F(17), fill=GREY)

    d.text((40, 440), "Резервная копия = дамп БД + копия klbackup. Оба каталога не должны находиться на том же",
           font=F(19), fill=GREY)
    d.text((40, 470), "физическом носителе, что и данные. Восстановление проверяется не реже раза в квартал.",
           font=F(19), fill=GREY)

    img.save(path, dpi=(200, 200))


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    roadmap(os.path.join(OUT_DIR, "fig_roadmap.png"))
    ports(os.path.join(OUT_DIR, "fig_ports.png"))
    installer_network(os.path.join(OUT_DIR, "fig_installer_net.png"))
    storage(os.path.join(OUT_DIR, "fig_storage.png"))
    webconsole(os.path.join(OUT_DIR, "fig_webconsole.png"))
    backup(os.path.join(OUT_DIR, "fig_backup.png"))
    print("figures written")
