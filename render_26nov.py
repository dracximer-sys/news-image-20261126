#!/usr/bin/env python3
"""Render the 26 November 2026 front page for the make.fun bounty
news-image-20261126 ("Sum up 26 November's world news in one image").

Build-time only: renders a 1024x1024 newspaper front page to entry.png
using Pillow. No network calls. Deterministic output: no random values,
no timestamps, fixed text and fixed geometry.

Data: research/stories-20261126.md (32 verified stories, Thursday
26 November 2026). Facts (names, numbers, places, outcomes) are kept
identical to that file; only the wording of titles/summaries is mine.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24  # side margin
PAPER = (251, 248, 241)
INK = (17, 17, 17)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
SEA = (214, 228, 240)
LAND = (232, 224, 204)
GREY = (90, 90, 90)
LINE = (210, 205, 195)
BODY = (40, 40, 40)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)


def wrap(text, fnt, width):
    """Split text into lines that fit `width` pixels with font `fnt`."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, leading):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, text, fnt, fill):
    draw.text((cx - fnt.getlength(text) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- data
# Headline stories 1-3: (number, title, summary, illustration label)
TOP_STORIES = [
    (
        "1",
        "CAIRO TANKER FIRE KILLS 31",
        "A fuel tanker overturned on the Ring Road in Giza on Wednesday "
        "evening and burst into flames, spreading to 27 vehicles. At "
        "least 31 people were killed and 21 injured.",
        "GIZA",
    ),
    (
        "2",
        "KIM ORDERS WIDER NUCLEAR DEPLOYMENT",
        "Kim Jong Un inspects nuclear material production facilities and "
        "says North Korea should deploy tactical nuclear weapons "
        "'across multiple domains'.",
        "PYONGYANG",
    ),
    (
        "3",
        "WALL STREET'S WILD WEDNESDAY",
        "The Nasdaq plunged more than 4% before closing down 0.62%; the "
        "Dow rose 0.33% to 50,182.95. Markets are closed on Thursday "
        "for Thanksgiving.",
        "WALL STREET",
    ),
]

# Stories 4-32, region-ordered: (number, region, title)
GRID = [
    (4, "EUROPE", "Kyiv hit by Russian ballistic missiles late Wednesday night"),
    (5, "EUROPE", "Euro leaders meet to discuss Lagarde's successor"),
    (6, "EUROPE", "Ukraine strikes Savasleyka airbase, five planes hit"),
    (7, "MIDDLE EAST", "Houthis escalate: strikes on Jeddah and Jazan ports claimed"),
    (8, "MIDDLE EAST", "Winter rains threaten 1,000 Gaza shelter sites"),
    (9, "AMERICAS", "Macy's 100th Thanksgiving parade moved to Saturday over storm"),
    (10, "AMERICAS", "ICE officers smash car window, pepper-spray bystanders"),
    (11, "AMERICAS", "US probes Virginia schools after sexual abuse scandal"),
    (12, "AMERICAS", "Kilmar Abrego Garcia leaves the US for Spain"),
    (13, "AMERICAS", "Trump open to meeting Democrats over healthcare"),
    (14, "AMERICAS", "Thanksgiving travel week: 81.5 million Americans on the move"),
    (15, "AMERICAS", "Thanksgiving Day, in the 250th year of American independence"),
    (16, "AMERICAS", "Poland's Nawrocki meets Chile's President Kast in Santiago"),
    (17, "AMERICAS", "Elderly man rescued after 11 days lost in Amazon jungle"),
    (18, "ASIA", "Bank of Korea raises base rate to 3.25%; KOSPI rebounds"),
    (19, "ASIA", "India marks Constitution Day (Samvidhan Divas)"),
    (20, "ASIA", "Delhi court to hear 'cockroach' leader Saurav Das's plea"),
    (21, "ASIA", "'Baby Aliyah': senator addresses Australian Senate with infant"),
    (22, "AFRICA", "Zambia bans protest over bid to scrap term limits"),
    (23, "AFRICA", "Nigeria panel reports on 37 miners who suffocated in custody"),
    (24, "ECONOMY", "Oil rises again as Hormuz stays shut; Brent $94.69"),
    (25, "SPORT & CULTURE", "Champions League: Barcelona 4-1 Sabah, PSG 2-2 Roma, Utd 2-2"),
    (26, "SPORT & CULTURE", "World Chess Championship Game 3 in Geneva, Sindarov White"),
    (27, "SPORT & CULTURE", "Europa League Matchday 5: 18 fixtures across the continent"),
    (28, "SPORT & CULTURE", "Conference League, AFC Champions League Two also play tonight"),
    (29, "SPORT & CULTURE", "India A face Sri Lanka A in Rising Stars semi-final"),
    (30, "SPORT & CULTURE", "NFL Thanksgiving tripleheader: Bears-Lions, Eagles-Cowboys, Chiefs-Bills"),
    (31, "CLIMATE", "Peru ports still closed as El Nino swells batter the coast"),
    (32, "CLIMATE", "King tides and El Nino storms batter California's coast"),
]

REGION_ORDER = [
    "EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA", "AFRICA",
    "ECONOMY", "SPORT & CULTURE", "CLIMATE",
]

# The day in numbers: (big figure, label)
NUMBERS = [
    ("31", "people killed in the Cairo fuel tanker fire"),
    ("$94.69", "Brent crude, up 3.60% as Hormuz stays shut"),
    ("3.25%", "Bank of Korea base rate, third hike of 2026"),
    ("96", "Peru ports closed as El Nino swells hit"),
    ("100", "inflatables in Macy's 100th Thanksgiving parade"),
    ("81.5m", "Americans travelling for Thanksgiving week"),
]

# Map pins: (lat, lon, label for the key). Seoul is NOT pinned: its pin
# would sit almost on top of Pyongyang's (3 px apart). San Francisco
# (king tides) takes that slot instead.
PINS = [
    (30.01, 31.21, "Giza — tanker fire kills 31"),
    (39.02, 125.75, "Pyongyang — Kim's nuclear order"),
    (40.71, -74.01, "New York — wild Wall Street day"),
    (50.45, 30.52, "Kyiv — missiles strike"),
    (24.71, 46.68, "Riyadh — missiles intercepted"),
    (-12.05, -77.04, "Callao — Peru ports closed"),
    (37.77, -122.42, "San Francisco — king tides batter coast"),
    (46.20, 6.14, "Geneva — Chess Game 3"),
    (-33.45, -70.67, "Santiago — Nawrocki meets Kast"),
    (9.62, 6.54, "Minna — miners' deaths report"),
    (28.61, 77.21, "Delhi — Das plea hearing"),
]

DATE_CHECK_BODY = (
    "Not 26 November, so left out: Houthi drone hits the PIF Tower in "
    "Riyadh, wounding 11 (24 Nov) · Australia passes the Digital Duty "
    "of Care (25 Nov) · Bangladesh garment minimum wage rises 36% "
    "(25 Nov) · Trump Thanksgiving proclamation signed (24 Nov, "
    "published 25 Nov) · EU General Court 'End the Cage Age' ruling "
    "(25 Nov) · ESA Hera mission Dimorphos crater images (25 Nov) · "
    "Melania Trump reunites 9 more Ukrainian and Russian children "
    "(25 Nov) · US Army Iowa lead azide detonation (25 Nov)."
)

SOURCES = (
    "Sources: Reuters · AP · CNN · BBC · Al Jazeera · The Times · "
    "USA Today · Yonhap · UEFA · FIDE · ChessBase · AAA · Straits · "
    "QNC News · pollar.news · Bar and Bench · White House · USTR · "
    "The Hindu BusinessLine · Wall Street Journal · Devdiscourse · "
    "WiseVoter · Daily Guardian Europe · ShipUniverse · selfstudys · "
    "Cricinfo · africasoccer. "
    "All stories from Thursday 26 Nov 2026. Built by @drac-ximer."
)

# Continent outlines (lon, lat) — drawn as polygons, equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 14), (-95, 16), (-100, 20), (-105, 22),
     (-110, 28), (-115, 32), (-120, 34), (-125, 40), (-125, 48),
     (-135, 58), (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 64), (-30, 68), (-25, 70), (-30, 76),
     (-45, 76), (-58, 70), (-60, 64)],
    [(-80, 10), (-75, 12), (-70, 12), (-60, 8), (-50, 4), (-45, 0),
     (-40, -5), (-35, -8), (-40, -15), (-45, -22), (-50, -28), (-55, -35),
     (-60, -40), (-65, -45), (-70, -52), (-73, -45), (-75, -35),
     (-78, -25), (-80, -15), (-82, -5), (-80, 5)],
    [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
     (15, 32), (20, 32), (30, 31), (35, 28), (40, 20), (43, 12), (48, 10),
     (51, 12), (45, 5), (40, -2), (38, -10), (35, -18), (32, -25),
     (28, -32), (20, -35), (15, -30), (12, -18), (10, -5), (8, 4), (0, 5),
     (-8, 5), (-15, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 55),
     (10, 58), (12, 60), (18, 62), (20, 65), (25, 70), (30, 70), (40, 68),
     (50, 69), (60, 70), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 45),
     (142, 40), (140, 35), (135, 33), (130, 31), (127, 35), (122, 38),
     (120, 32), (115, 25), (110, 20), (108, 12), (105, 8), (100, 8),
     (98, 12), (95, 16), (92, 20), (88, 22), (85, 19), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 23), (65, 25), (60, 25), (57, 26), (54, 27),
     (52, 28), (50, 30), (48, 30), (46, 32), (44, 35), (42, 38), (40, 40),
     (38, 42), (35, 42), (33, 40), (30, 38), (28, 38), (26, 38), (23, 36),
     (20, 38), (18, 40), (15, 40), (12, 42), (10, 44), (8, 44), (5, 43),
     (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (141, 39),
     (141, 42), (143, 44), (145, 44), (142, 42), (140, 38), (138, 35),
     (136, 33), (133, 32)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (103, -5), (100, 0)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -4),
     (110, -2)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -4), (132, -2)],
    [(105, -6), (110, -7), (114, -7), (114, -8), (108, -8), (105, -7)],
    [(119, 0), (121, 1), (123, 0), (121, -2), (120, -4), (119, -2)],
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33),
     (130, -32), (135, -35), (138, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (175, -40), (172, -43), (168, -46)],
]


# ------------------------------------------------------- illustrations
# All three are drawn with code — original art, no photos.

def ill_cairo(draw, x0, y0, w, h):
    """Fuel tanker on fire on the Giza Ring Road at dusk."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(52, 32, 24))
    # dusk glow band across the sky
    draw.rectangle([x0, y0 + 10, x0 + w, y0 + 20], fill=(120, 62, 30))
    # road band at the bottom with a dashed centre line
    draw.rectangle([x0, y0 + h - 12, x0 + w, y0 + h], fill=(32, 32, 32))
    for dx in range(8, w - 10, 28):
        draw.line([x0 + dx, y0 + h - 6, x0 + dx + 14, y0 + h - 6],
                  fill=(200, 200, 200), width=2)
    # smoke column above the tanker
    for cx, cy, r in ((150, 8, 10), (162, 6, 8), (138, 9, 8),
                      (172, 8, 7), (128, 11, 6)):
        draw.ellipse([x0 + cx - r, y0 + cy - r, x0 + cx + r, y0 + cy + r],
                     fill=(60, 60, 60))
    # flames licking up from the tanker
    for fx, fy, fs in ((140, 22, 10), (155, 18, 13), (170, 22, 10),
                       (185, 24, 8), (128, 25, 7)):
        draw.polygon([(x0 + fx - fs, y0 + fy + 8), (x0 + fx, y0 + fy - 8),
                      (x0 + fx + fs, y0 + fy + 8)], fill=(255, 140, 0))
    for fx, fy, fs in ((150, 24, 6), (162, 21, 7), (140, 26, 5)):
        draw.polygon([(x0 + fx - fs, y0 + fy + 6), (x0 + fx, y0 + fy - 6),
                      (x0 + fx + fs, y0 + fy + 6)], fill=(255, 220, 80))
    # overturned tanker: cylindrical tank lying on its side, wheels up
    draw.rectangle([x0 + 70, y0 + 30, x0 + 230, y0 + 42], fill=(200, 200, 200))
    draw.ellipse([x0 + 66, y0 + 30, x0 + 78, y0 + 42], fill=(180, 180, 180))
    draw.rectangle([x0 + 70, y0 + 34, x0 + 230, y0 + 38], fill=(180, 40, 30))
    # cab, tipped over at the front
    draw.rectangle([x0 + 232, y0 + 26, x0 + 258, y0 + 42], fill=(140, 40, 30))
    draw.rectangle([x0 + 240, y0 + 29, x0 + 254, y0 + 35], fill=(30, 60, 100))
    # wheels pointing up
    for wx in (95, 150, 205):
        draw.ellipse([x0 + wx - 6, y0 + 22, x0 + wx + 6, y0 + 30],
                     fill=(20, 20, 20))
    # a second burning car, small, on the right
    draw.rectangle([x0 + 272, y0 + 34, x0 + 300, y0 + 42], fill=(25, 25, 25))
    draw.polygon([(x0 + 280, y0 + 34), (x0 + 286, y0 + 26),
                  (x0 + 292, y0 + 34)], fill=(255, 140, 0))
    draw.text((x0 + 6, y0 + 3), "GIZA",
              font=SANS_B(10), fill=(255, 255, 255))


def ill_kim(draw, x0, y0, w, h):
    """Nuclear facility hall with centrifuge cylinders and a missile."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(12, 20, 45))
    # stars at fixed positions
    for sx, sy in ((18, 8), (48, 14), (90, 6), (210, 10), (280, 8),
                   (60, 22), (120, 10), (200, 20), (300, 16), (30, 30)):
        draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2],
                     fill=(255, 255, 255))
    # red star, top right of the label
    sx, sy = x0 + 100, y0 + 8
    draw.polygon([(sx, sy - 6), (sx + 2, sy - 1), (sx + 7, sy - 1),
                  (sx + 3, sy + 2), (sx + 4, sy + 7), (sx, sy + 4),
                  (sx - 4, sy + 7), (sx - 3, sy + 2), (sx - 7, sy - 1),
                  (sx - 2, sy - 1)], fill=(200, 40, 40))
    # facility hall: dark block with a lighter roof line
    draw.rectangle([x0 + 24, y0 + 22, x0 + 216, y0 + h - 4],
                   fill=(45, 50, 62))
    draw.rectangle([x0 + 24, y0 + 22, x0 + 216, y0 + 26], fill=(90, 98, 112))
    # centrifuge cylinders in a row inside the hall
    for cx in (44, 84, 124, 164):
        draw.rectangle([x0 + cx, y0 + 28, x0 + cx + 16, y0 + h - 6],
                       fill=(180, 190, 200))
        draw.rectangle([x0 + cx, y0 + 28, x0 + cx + 16, y0 + 32],
                       fill=(120, 130, 140))
        draw.line([x0 + cx, y0 + 40, x0 + cx + 16, y0 + 40],
                  fill=(120, 130, 140), width=1)
    # missile silhouette standing at the right
    mx = x0 + 252
    draw.polygon([(mx - 8, y0 + 10), (mx + 8, y0 + 10), (mx, y0 + 3)],
                 fill=(200, 40, 40))
    draw.rectangle([mx - 8, y0 + 10, mx + 8, y0 + h - 8], fill=(60, 64, 72))
    draw.rectangle([mx - 8, y0 + 26, mx + 8, y0 + 30], fill=(200, 40, 40))
    draw.polygon([(mx - 8, y0 + h - 14), (mx - 14, y0 + h - 4),
                  (mx - 8, y0 + h - 4)], fill=(40, 44, 50))
    draw.polygon([(mx + 8, y0 + h - 14), (mx + 14, y0 + h - 4),
                  (mx + 8, y0 + h - 4)], fill=(40, 44, 50))
    draw.text((x0 + 6, y0 + 3), "PYONGYANG",
              font=SANS_B(10), fill=(255, 255, 255))


def ill_wallstreet(draw, x0, y0, w, h):
    """Wall Street: skyscrapers and a market line that plunges, then recovers."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 18, 40))
    # skyscraper silhouettes along the bottom, with lit windows
    for bx, bw, bh in ((8, 34, 22), (48, 26, 30), (80, 40, 18),
                       (126, 30, 26), (162, 24, 34), (192, 36, 20),
                       (234, 28, 28), (268, 34, 16)):
        draw.rectangle([x0 + bx, y0 + h - bh, x0 + bx + bw, y0 + h],
                       fill=(30, 38, 55))
        for wy in range(y0 + h - bh + 4, y0 + h - 2, 7):
            for wx in range(x0 + bx + 5, x0 + bx + bw - 3, 9):
                draw.ellipse([wx, wy, wx + 2, wy + 2], fill=(255, 220, 120))
    # market line: jagged plunge from the top left, then a recovery
    pts = [(x0 + 6, y0 + 14), (x0 + 40, y0 + 20), (x0 + 70, y0 + 16),
           (x0 + 100, y0 + 26), (x0 + 130, y0 + 22), (x0 + 160, y0 + 34),
           (x0 + 190, y0 + 30), (x0 + 215, y0 + 40), (x0 + 240, y0 + 36)]
    draw.line(pts, fill=(220, 60, 60), width=3)
    # recovery segment in green, climbing to the top right
    rec = [(x0 + 240, y0 + 36), (x0 + 268, y0 + 28), (x0 + 296, y0 + 20),
           (x0 + 309, y0 + 16)]
    draw.line(rec, fill=(60, 180, 80), width=3)
    draw.ellipse([x0 + 303, y0 + 10, x0 + 313, y0 + 20],
                 outline=(60, 180, 80), width=2)
    draw.text((x0 + 6, y0 + 3), "WALL STREET",
              font=SANS_B(10), fill=(255, 255, 255))


ILLUSTRATIONS = [ill_cairo, ill_kim, ill_wallstreet]


# ------------------------------------------------------------ sections

def draw_masthead(draw):
    centred(draw, W // 2, 10, "THE WORLD TODAY", SERIF_B(54), INK)
    draw.line([(M, 76), (W - M, 76)], fill=INK, width=2)
    draw.text((M, 82), "THURSDAY, 26 NOVEMBER 2026",
              font=SANS_B(13), fill=INK)
    right = "32 STORIES  ·  8 REGIONS  ·  ONE DAY"
    draw.text((W - M - SANS_B(13).getlength(right), 82), right,
              font=SANS_B(13), fill=INK)
    # red date band
    draw.rectangle([M, 100, W - M, 128], fill=RED)
    centred(draw, W // 2, 107,
            "THE DAY IN WORLD NEWS  —  THURSDAY 26 NOVEMBER 2026",
            SANS_B(15), (255, 255, 255))
    # region counts, counted from the data
    counts = {}
    for _, region, _ in GRID:
        counts[region] = counts.get(region, 0) + 1
    counts["MIDDLE EAST"] += 1  # headline 1, Cairo
    counts["ASIA"] += 1  # headline 2, Kim
    counts["ECONOMY"] += 1  # headline 3, Wall Street
    parts = ["%s %d" % (r, counts[r]) for r in REGION_ORDER if counts.get(r)]
    centred(draw, W // 2, 136, "   ·   ".join(parts), SANS_B(12), INK)


def draw_numbers(draw):
    draw.text((M, 160), "THE DAY IN NUMBERS", font=SANS_B(14), fill=RED)
    box_w = (976 - 5 * 8) // 6
    y0, y1 = 182, 232
    for i, (big, label) in enumerate(NUMBERS):
        bx = M + i * (box_w + 8)
        draw.rectangle([bx, y0, bx + box_w, y1], outline=INK, width=1)
        draw.text((bx + 8, y0 + 4), big, font=SANS_B(18), fill=INK)
        draw_wrapped(draw, bx + 8, y0 + 27, label, SANS(9), box_w - 14,
                     GREY, 10)


def draw_top_stories(draw):
    draw.text((M, 242), "TOP STORIES", font=SANS_B(14), fill=RED)
    card_w = (976 - 24) // 3
    card_y, card_h = 260, 160
    for i, (num, title, summary, _label) in enumerate(TOP_STORIES):
        cx = M + i * (card_w + 12)
        draw.rectangle([cx, card_y, cx + card_w, card_y + card_h],
                       outline=INK, width=1)
        ILLUSTRATIONS[i](draw, cx + 1, card_y + 1, card_w - 2, 56)
        draw.text((cx + 8, card_y + 62), num, font=SERIF_B(20), fill=RED)
        title_lines = wrap(title, SERIF_B(17), card_w - 38)
        ty = card_y + 62
        for line in title_lines:
            draw.text((cx + 30, ty), line, font=SERIF_B(17), fill=INK)
            ty += 20
        draw_wrapped(draw, cx + 8, ty + 4, summary, SANS(11), card_w - 16,
                     BODY, 14)
    return card_y + card_h


def draw_map(draw, y0):
    """World map, height 140, equirectangular, with 11 numbered pins."""
    draw.text((M, y0), "WHERE IT HAPPENED", font=SANS_B(14), fill=RED)
    map_y0, map_y1 = y0 + 18, y0 + 158
    draw.rectangle([M, map_y0, W - M, map_y1], fill=SEA, outline=INK, width=1)

    def px(lon):
        return M + (lon + 180) / 360.0 * 976

    def py(lat):
        return map_y0 + (85 - lat) / 145.0 * 140

    # graticule every 30 degrees
    for lon in range(-180, 181, 30):
        x = px(lon)
        draw.line([(x, map_y0), (x, map_y1)], fill=(190, 205, 220), width=1)
    for lat in range(-60, 86, 30):
        y = py(lat)
        draw.line([(M, y), (W - M, y)], fill=(190, 205, 220), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [(px(lon), py(lat)) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(120, 110, 90))
    # pins
    for i, (lat, lon, _label) in enumerate(PINS, start=1):
        x, y = px(lon), py(lat)
        draw.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED,
                     outline=(255, 255, 255), width=1)
        num = str(i)
        nf = SANS_B(10 if len(num) == 1 else 9)
        draw.text((x - nf.getlength(num) / 2, y - 6), num, font=nf,
                  fill=(255, 255, 255))
    # pin key, two lines
    key1 = "  ·  ".join("%d. %s" % (i + 1, PINS[i][2]) for i in range(6))
    key2 = "  ·  ".join("%d. %s" % (i + 1, PINS[i][2]) for i in range(6, 11))
    draw.text((M, map_y1 + 4), key1, font=SANS(9), fill=GREY)
    draw.text((M, map_y1 + 15), key2, font=SANS(9), fill=GREY)
    return map_y1 + 26


def draw_also(draw, y0):
    """Stories 4-32, region-ordered, split in half across two columns."""
    draw.text((M, y0), "ALSO ON THURSDAY 26 NOVEMBER",
              font=SANS_B(14), fill=RED)
    col_w = (976 - 20) // 2
    half = (len(GRID) + 1) // 2
    columns = [GRID[:half], GRID[half:]]
    bottom = y0
    for ci, stories in enumerate(columns):
        cx = M + ci * (col_w + 20)
        y = y0 + 18
        last_region = None
        for num, region, title in stories:
            if region != last_region:
                draw.text((cx, y), region, font=SANS_B(10), fill=RED)
                y += 22
                last_region = region
            text = "%d. %s" % (num, title)
            y = draw_wrapped(draw, cx + 12, y, text, SANS(10),
                             col_w - 12, INK, 11)
        bottom = max(bottom, y)
    return bottom


def draw_date_check(draw, y0):
    draw.rectangle([M, y0, W - M, y0 + 54], outline=RED, width=2)
    draw.text((M + 8, y0 + 5), "DATE CHECK — LEFT OUT ON PURPOSE",
              font=SANS_B(11), fill=RED)
    draw_wrapped(draw, M + 8, y0 + 19, DATE_CHECK_BODY, SANS(10),
                 976 - 16, INK, 12)
    return y0 + 54


def draw_footer(draw, y0):
    draw.line([(M, y0), (W - M, y0)], fill=INK, width=1)
    return draw_wrapped(draw, M, y0 + 4, SOURCES, SANS(8), 976, GREY, 11)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_numbers(draw)
    cards_bottom = draw_top_stories(draw)
    map_bottom = draw_map(draw, cards_bottom + 8)
    also_bottom = draw_also(draw, map_bottom + 8)
    dc_bottom = draw_date_check(draw, also_bottom + 8)
    end = draw_footer(draw, dc_bottom + 6)
    assert end <= H, "page overflow: footer ends at y=%d" % end
    return img


def main():
    out = os.environ.get("RENDER_OUT") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG")
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
