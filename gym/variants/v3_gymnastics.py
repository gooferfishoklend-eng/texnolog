"""Вариант 3. Зал гимнастики и единоборств 18 x 12 x 5 м.

Западная половина — гимнастическая зона (перекладина, брусья, бревно,
козёл с мостиком, кольца, канаты, гимнастические стенки, маты);
восточная — зона единоборств на татами 8 x 8 м с боксёрскими мешками.
Окна по южной стене (с защитными решётками) и верхний ряд по северной,
двери в торцах. Купольные светильники, приточный воздуховод.
"""
from .. import colors as C
from .. import equipment as E
from ..room import Room, opening
from ..scene import Scene

FACE = {"S": 0, "E": 90, "N": 180, "W": 270}


def build():
    L, W, H = 18000, 12000, 5000
    sc = Scene("variant3_gymnastics", "Вариант 3 — Зал гимнастики и единоборств",
               (L, W, H))
    r = Room(sc, L, W, H, t=510)
    r.floor(C.PARQUET, "Паркет спортивный")
    r.walls({
        "S": [opening("window", 1500 + k * 3300, 2100, 2200, sill=1200)
              for k in range(5)],
        "N": [opening("window", 1500 + k * 3300, 2100, 1300, sill=3200)
              for k in range(5)],
        "W": [opening("door", W / 2 - 900, 1800, 2400, leaves=2)],
        "E": [opening("door", W - 2400, 1000, 2100)],
    })
    r.ceiling()

    # --- гимнастическая зона
    for k in range(4):
        E.wall_bars(sc, 2400 + k * 1900, W, rot=FACE["N"], sections=2)
    E.horizontal_bar(sc, 2000, 3200)
    for k in range(2):
        E.mat(sc, 2200, 2200 + k * 1000, color=C.MAT_BLUE)
    E.parallel_bars(sc, 1500, 7400)
    E.balance_beam(sc, 2500, 10000 - 300 - 500)
    E.mat(sc, 2500, 8000, dx=2000, dy=1000, color=C.MAT_GREEN)
    E.mat(sc, 4500, 8000, dx=2000, dy=1000, color=C.MAT_GREEN)
    E.vault_horse(sc, 6800, 3000)
    E.mat(sc, 7500, 2600, dx=2000, dy=1200, color=C.MAT_RED)
    E.rings(sc, 6300, 6800, H)
    E.mat(sc, 5300, 6300, dx=2000, dy=1000, color=C.MAT_BLUE)
    E.climbing_rope(sc, 7800, 6300, H)
    E.climbing_rope(sc, 7800, 7300, H)
    E.mat(sc, 7300, 6200, dx=1000, dy=2000, color=C.MAT_RED)
    E.mat_stack(sc, 600, 600, n=5)

    # --- зона единоборств
    E.tatami(sc, 9500, 2000, 4, 8)
    for k in range(3):
        E.punching_bag(sc, 11000 + k * 2500, 900, H)
    E.bench_lockers(sc, L - 500, W, rot=FACE["N"], length=3200)
    E.bench(sc, L, 2200, rot=FACE["E"], length=3000)
    E.mirror_wall(sc, L, 4800, rot=FACE["E"], length=4500)

    # --- оснащение
    E.coach_desk(sc, 9600, 10400)
    E.scoreboard(sc, 12000, W, 3500, rot=FACE["N"])
    E.clock(sc, 0, 3000, 3600, rot=FACE["W"])
    E.first_aid(sc, 0, 1500, rot=FACE["W"])
    E.speaker(sc, 0, 9500, 3800, rot=FACE["W"])
    E.speaker(sc, L, 1500, 3800, rot=FACE["E"])

    # --- инженерные системы
    r.lights_grid(5, 3, H - 800, kind="dome")
    r.vent_duct(4000, H - 600, n_diff=5, w=600, h=400, entry="E")
    r.exhaust_grilles("W", [1500, 9000], z=H - 900)
    for k in range(5):
        r.radiator("S", 1500 + k * 3300 + 450, length=1200, z=150, height=500)
    return sc
