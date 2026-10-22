"""Вариант 2. Тренажёрный (фитнес) зал 18 x 10 x 3,6 м.

Зонирование: кардиозона у окон (беговые дорожки, велотренажёры),
зона свободных весов (силовая рама, жим лёжа, гантели, блины, гири,
кроссовер) на резиновом покрытии, зона растяжки (коврики, фитболы,
шведская стенка). Зеркала по восточной стене, стойка тренера у входа.
Окна — по южной стене, две двери (вход и в раздевалку) — по северной.
"""
from .. import colors as C
from .. import equipment as E
from ..room import Room, opening
from ..scene import Scene

FACE = {"S": 0, "E": 90, "N": 180, "W": 270}


def build():
    L, W, H = 18000, 10000, 3600
    sc = Scene("variant2_fitness", "Вариант 2 — Тренажёрный зал", (L, W, H))
    r = Room(sc, L, W, H, t=400, wall_color=C.WALL_ACCENT)
    r.floor("#cfcfcf", "Наливной пол")
    r.walls({
        "S": [opening("window", 1200 + k * 3400, 2000, 1800, sill=900)
              for k in range(5)],
        "N": [opening("door", 2000, 1100, 2100),
              opening("door", 7000, 1000, 2100)],
    })
    r.ceiling()

    # --- кардиозона (лицом к окнам)
    for k in range(4):
        E.treadmill(sc, 1200 + k * 1300, 3400, rot=270)
    for k in range(3):
        E.exercise_bike(sc, 6600 + k * 900, 3000, rot=270)

    # --- зона свободных весов на резиновом покрытии
    E.floor_mats_grid(sc, 9500, 300, 8, 9)
    E.mirror_wall(sc, L, 300, rot=FACE["E"], length=9000)
    E.dumbbell_rack(sc, L, 1500, rot=FACE["E"], n=8)
    E.adjustable_bench(sc, L - 2300, 1800, rot=90)
    E.adjustable_bench(sc, L - 2300, 3500, rot=90)
    E.power_rack(sc, 13000, 5300)
    E.press_bench(sc, 10300, 4300)
    E.plate_tree(sc, 16300, 6600)
    E.cable_crossover(sc, 13600, W, rot=FACE["N"])
    E.kettlebells(sc, 15000, 8700, n=5)

    # --- зона растяжки
    E.wall_bars(sc, 0, 9600, rot=FACE["W"], sections=2, height=2700)
    for k in range(4):
        E.mat(sc, 1200, 4800 + k * 850, dx=1800, dy=600, t=10,
              color=(C.MAT_GREEN, C.MAT_BLUE, C.MAT_RED, C.MAT_GREEN)[k],
              name="Коврик для фитнеса")
    E.gym_ball(sc, 3800, 5300, color=C.MAT_BLUE)
    E.gym_ball(sc, 3800, 6200, color=C.MAT_RED)
    E.gym_ball(sc, 4600, 5700, color=C.MAT_GREEN)
    E.bench(sc, 500, 1200, rot=90, length=2000)

    # --- рецепция и оснащение
    E.coach_desk(sc, 4000, 8100)
    E.first_aid(sc, 5800, W, rot=FACE["N"])
    E.clock(sc, 9300, W, 2400, rot=FACE["N"])
    E.speaker(sc, 0, 1200 + 2000 + 350, 2600, rot=FACE["W"])
    E.speaker(sc, L, 9500, 2600, rot=FACE["E"])

    # --- инженерные системы
    r.lights_grid(6, 3, H - 400, kind="panel")
    r.vent_duct(3300, H - 450, n_diff=5, w=500, h=300, entry="W")
    r.exhaust_grilles("N", [4200, 11000, 16000], z=H - 650, size=(500, 300))
    for k in range(5):
        r.radiator("S", 1200 + k * 3400 + 400, length=1200)
    return sc
