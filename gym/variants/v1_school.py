"""Вариант 1. Универсальный школьный спортивный зал 24 x 12 x 6 м.

Баскетбольная/волейбольная площадка, гимнастические стенки по северной
стене, скамьи, маты, стеллаж с мячами, табло. Ленточные окна по обеим
длинным стенам, двустворчатые двери в торцах. Освещение — линейные
светильники в защитной решётке, приточная вентиляция по оси зала,
вытяжные решётки, радиаторы с деревянными экранами.
"""
from .. import colors as C
from .. import equipment as E
from ..room import Room, opening
from ..scene import Scene

# поворот пристенного оборудования, чтобы «лицо» смотрело в зал
FACE = {"S": 0, "E": 90, "N": 180, "W": 270}


def build():
    L, W, H = 24000, 12000, 6000
    sc = Scene("variant1_school", "Вариант 1 — Школьный спортивный зал", (L, W, H))
    r = Room(sc, L, W, H, t=510)
    r.floor(C.PARQUET, "Паркет спортивный")
    r.walls({
        "S": [opening("window", 1350 + k * 3900, 2700, 2000, sill=2400)
              for k in range(6)],
        "N": [opening("window", 1350 + k * 3900, 2700, 1500, sill=3300)
              for k in range(6)],
        "W": [opening("door", W / 2 - 900, 1800, 2400, leaves=2)],
        "E": [opening("door", 900, 1500, 2400, leaves=2)],
    })
    r.ceiling()

    # игровая площадка
    E.court_markings(sc, L, W)
    E.volleyball_posts(sc, L / 2, 300, W - 600)
    E.basketball_hoop(sc, 0, W / 2, rot=FACE["W"])
    E.basketball_hoop(sc, L, W / 2, rot=FACE["E"])

    # гимнастические стенки вдоль северной стены (под окнами)
    for k in range(5):
        E.wall_bars(sc, 6050 + k * 3900, W, rot=FACE["N"], sections=3)
    # скамьи вдоль южной стены
    for k in range(5):
        E.bench(sc, 1500 + k * 4500, 600)
    # маты: стопки у восточной стены и разложенные у западной
    E.mat_stack(sc, L - 1300, 3000, n=5, dx=1000, dy=2000)
    E.mat_stack(sc, L - 1300, 5300, n=4, dx=1000, dy=2000)
    for k in range(3):
        E.mat(sc, 1200, 2500 + k * 1050, color=(C.MAT_BLUE, C.MAT_GREEN)[k % 2])
    E.locker_shelf(sc, L, 8400, rot=FACE["E"], length=2400)

    # оснащение стен
    E.scoreboard(sc, L / 2 - 1200, 0, 4700, rot=FACE["S"])
    E.clock(sc, 0, 2600, 4600, rot=FACE["W"])
    E.first_aid(sc, 0, 1500, rot=FACE["W"])
    E.speaker(sc, 0, 2100 + 350, 4500, rot=FACE["W"])
    E.speaker(sc, L, 10500, 4500, rot=FACE["E"])

    # освещение, вентиляция, отопление
    r.lights_grid(6, 2, H - 900, kind="panel")
    r.vent_duct(W / 2, H - 700, n_diff=6, w=800, h=500, entry="W")
    r.exhaust_grilles("N", [4350 + k * 3900 for k in range(5)], z=H - 800)
    for k in range(6):
        r.radiator("S", 1350 + k * 3900 + 750, length=1200)
    return sc
