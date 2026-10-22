"""Спортивное оборудование. Каждая функция строит одно изделие.

Параметры (x, y, rot): точка привязки (угол изделия) и поворот вокруг
вертикали (0/90/180/270°). Локальные оси: u — длина изделия,
v — глубина (направление «от стены в зал» для пристенного оборудования).
"""
from . import colors as C
from .frame import Frame


# ---------------------------------------------------------------- общие
def bench(sc, x, y, rot=0, length=3000):
    """Гимнастическая скамья 3000 x 240, высота 300."""
    f = Frame(sc, x, y, rot).item("Скамья гимнастическая")
    f.box(0, 0, 260, length, 240, 40, C.WOOD)
    for u in (150, length / 2 - 20, length - 190):
        f.box(u, 20, 0, 40, 200, 260, C.WOOD_DARK)
    f.box(150, 100, 60, length - 300, 40, 40, C.WOOD_DARK)  # нижний брус


def mat(sc, x, y, dx=2000, dy=1000, t=100, color=C.MAT_BLUE, name="Мат гимнастический"):
    sc.item(name)
    sc.box(x, y, 0, dx, dy, t, color)
    # ручки-ремни по торцам
    sc.box(x + dx / 2 - 100, y - 15, t * 0.4, 200, 15, 30, C.BLACK)
    sc.box(x + dx / 2 - 100, y + dy, t * 0.4, 200, 15, 30, C.BLACK)


def mat_stack(sc, x, y, n=4, dx=2000, dy=1000, t=100):
    cols = [C.MAT_BLUE, C.MAT_GREEN, C.MAT_RED, C.MAT_BLUE, C.MAT_GREEN]
    sc.item("Стопка матов")
    for i in range(n):
        sc.box(x, y, i * t, dx, dy, t - 2, cols[i % len(cols)])


def wall_bars(sc, x, y, rot=0, sections=4, height=3000, width=900):
    """Шведская стенка. Привязка — угол у стены, v — от стены в зал."""
    f = Frame(sc, x, y, rot)
    for s in range(sections):
        f.item("Гимнастическая стенка")
        u0 = s * (width + 50)
        # кронштейны к стене
        for z in (300, height - 300):
            f.box(u0 + 40, 0, z, width - 80, 40, 60, C.STEEL)
        for u in (u0, u0 + width - 40):
            f.box(u, 0, 0, 40, 150, height, C.WOOD_DARK)
        n = int((height - 150) // 250)
        for k in range(n):
            z = 150 + k * 250
            v = 75 if k < n - 2 else 140  # верхние перекладины выносные
            f.hcyl("u", u0 + 40, v, z, width - 80, 17, C.WOOD)


def scoreboard(sc, x, y, z, rot=0):
    f = Frame(sc, x, y, rot).item("Табло электронное")
    f.box(0, 0, z, 2400, 120, 1000, C.SCREEN)
    for k, col in enumerate((C.LINE_RED, C.YELLOW, C.LINE_RED)):
        f.box(250 + k * 700, 120, z + 350, 500, 10, 300, col)


def clock(sc, x, y, z, rot=0):
    f = Frame(sc, x, y, rot).item("Часы настенные")
    f.box(0, 0, z, 600, 60, 300, C.SCREEN)
    f.box(60, 60, z + 80, 480, 5, 140, C.LINE_RED)


def speaker(sc, x, y, z, rot=0):
    f = Frame(sc, x, y, rot).item("Акустическая колонка")
    f.box(0, 0, z, 350, 300, 550, C.BLACK)
    f.box(30, 300, z + 60, 290, 5, 290, C.STEEL_DARK)


def first_aid(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Аптечка")
    f.box(0, 0, 1400, 400, 150, 400, C.LINE_WHITE)
    f.box(170, 150, 1500, 60, 5, 200, C.LINE_RED)
    f.box(100, 150, 1570, 200, 5, 60, C.LINE_RED)


def coach_desk(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Стол тренера")
    f.box(0, 0, 720, 1400, 700, 30, C.WOOD)
    for u in (0, 1360):
        f.box(u, 0, 0, 40, 700, 720, C.STEEL_DARK)
    f.item("Стул")
    f.box(500, 750, 450, 450, 450, 40, C.UPHOLSTERY)
    f.box(500, 1160, 490, 450, 40, 450, C.UPHOLSTERY)
    for du, dv in ((0, 0), (410, 0), (0, 410), (410, 410)):
        f.box(500 + du, 750 + dv, 0, 40, 40, 450, C.STEEL_DARK)


def locker_shelf(sc, x, y, rot=0, length=2400):
    """Стеллаж для инвентаря с мячами."""
    f = Frame(sc, x, y, rot).item("Стеллаж для инвентаря")
    for u in (0, length - 40):
        f.box(u, 0, 0, 40, 500, 1800, C.STEEL_DARK)
    for z in (100, 700, 1300, 1760):
        f.box(0, 0, z, length, 500, 30, C.STEEL)
    f.item("Мячи")
    cols = [C.ORANGE, C.LINE_WHITE, C.MAT_BLUE, C.YELLOW]
    for k in range(int((length - 200) // 260)):
        for lvl, z in enumerate((130, 730, 1330)):
            f.cyl(180 + k * 260, 250, z, 115, 230, cols[(k + lvl) % 4])


# ----------------------------------------------------- игровые виды спорта
def basketball_hoop(sc, x, y, rot=0):
    """Щит с кольцом, крепление к стене. Привязка — середина у стены."""
    f = Frame(sc, x, y, rot).item("Баскетбольный щит")
    # ферма крепления
    for u in (-700, 640):
        f.box(u, 0, 2700, 60, 1200, 60, C.STEEL_DARK)
        f.box(u, 0, 3900, 60, 1200, 60, C.STEEL_DARK)
        f.box(u, 1140, 2700, 60, 60, 1260, C.STEEL_DARK)
    f.box(-900, 1200, 2900, 1800, 30, 1050, C.LINE_WHITE)
    f.box(-295, 1230, 3050, 590, 5, 450, C.LINE_RED)
    f.box(-245, 1230, 3100, 490, 6, 350, C.LINE_WHITE)
    f.item("Баскетбольное кольцо")
    f.box(-120, 1230, 3030, 240, 150, 20, C.ORANGE)
    f.cyl(0, 1230 + 151 + 225, 3050, 242, 20, C.ORANGE, r_in=225)


def volleyball_posts(sc, x, y, length):
    """Волейбольные стойки с сеткой вдоль оси Y."""
    sc.item("Волейбольная стойка")
    sc.cyl(x, y, 0, 50, 2550, C.STEEL)
    sc.cyl(x, y, 0, 200, 20, C.STEEL_DARK)
    sc.item("Волейбольная стойка")
    sc.cyl(x, y + length, 0, 50, 2550, C.STEEL)
    sc.cyl(x, y + length, 0, 200, 20, C.STEEL_DARK)
    sc.item("Волейбольная сетка")
    sc.box(x - 3, y + 500, 1430, 6, length - 1000, 1000, C.LINE_WHITE)
    sc.box(x - 8, y + 50, 2380, 16, length - 100, 50, C.BLACK)
    sc.box(x - 8, y + 50, 1430, 16, length - 100, 20, C.BLACK)
    sc.item("Антенны сетки")
    for yy in (y + 500, y + length - 500):
        sc.cyl(x, yy, 1430, 5, 1800, C.LINE_RED)


def court_markings(sc, L, W, color=C.LINE_WHITE):
    """Разметка баскетбольной площадки 28x15 (масштабируется под зал)."""
    lw, t = 50, 2
    m = 1000
    cx, cy = L / 2, W / 2
    sc.item("Разметка площадки")
    sc.box(m, m, 0, L - 2 * m, lw, t, color)
    sc.box(m, W - m - lw, 0, L - 2 * m, lw, t, color)
    sc.box(m, m, 0, lw, W - 2 * m, t, color)
    sc.box(L - m - lw, m, 0, lw, W - 2 * m, t, color)
    sc.box(cx - lw / 2, m, 0, lw, W - 2 * m, t, color)
    sc.cyl(cx, cy, 0, 1800, t, color, r_in=1750)
    for side in (0, 1):
        x0 = m if side == 0 else L - m - 5800
        sc.box(x0, cy - 2450, 0, 5800, lw, t, color)
        sc.box(x0, cy + 2400, 0, 5800, lw, t, color)
        xf = x0 + 5800 - lw if side == 0 else x0
        sc.box(xf, cy - 2450, 0, lw, 4900, t, color)
        fx = m + 5800 if side == 0 else L - m - 5800
        sc.cyl(fx, cy, 0, 1800, t, color, r_in=1750)
        # «краска» в зоне
        sc.box(x0 + (0 if side == 0 else lw), cy - 2400, 0, 5800 - lw, 4800, 1,
               C.LINE_BLUE)


# --------------------------------------------------------- тренажёрный зал
def treadmill(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Беговая дорожка")
    f.box(0, 0, 0, 2000, 850, 220, C.STEEL_DARK)
    f.box(150, 125, 220, 1650, 600, 15, C.BLACK)
    f.hcyl("v", 120, 0, 140, 850, 60, C.STEEL)
    for v in (40, 730):
        f.box(1750, v, 220, 80, 80, 1150, C.STEEL_DARK)
        f.box(1300, v + 15, 1100, 520, 50, 50, C.BLACK)  # поручни
    f.box(1700, 40, 1370, 200, 770, 350, C.STEEL_DARK)
    f.box(1690, 120, 1420, 10, 610, 250, C.SCREEN)


def exercise_bike(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Велотренажёр")
    f.box(0, 150, 0, 1200, 300, 60, C.STEEL_DARK)
    f.box(0, 0, 0, 80, 600, 60, C.STEEL_DARK)
    f.box(1120, 0, 0, 80, 600, 60, C.STEEL_DARK)
    f.hcyl("v", 850, 270, 450, 60, 260, C.STEEL)  # маховик
    f.box(250, 260, 60, 80, 80, 900, C.STEEL_DARK)
    f.box(150, 200, 960, 300, 200, 80, C.UPHOLSTERY)  # седло
    f.box(950, 260, 60, 80, 80, 1100, C.STEEL_DARK)
    f.box(950, 100, 1150, 200, 400, 40, C.BLACK)  # руль
    f.box(1050, 220, 1160, 60, 160, 160, C.SCREEN)


def press_bench(sc, x, y, rot=0):
    """Скамья для жима со стойками и штангой."""
    f = Frame(sc, x, y, rot).item("Скамья для жима")
    f.box(0, 0, 0, 1600, 80, 60, C.STEEL_DARK)
    f.box(0, 920, 0, 1600, 80, 60, C.STEEL_DARK)
    f.box(1100, 0, 0, 80, 1000, 60, C.STEEL_DARK)
    f.box(150, 0, 0, 80, 1000, 60, C.STEEL_DARK)
    f.box(150, 380, 60, 1100, 240, 360, C.STEEL_DARK)
    f.box(100, 370, 420, 1200, 260, 60, C.LEATHER)
    for v in (60, 860):
        f.box(1100, v, 60, 80, 80, 1150, C.STEEL)
        f.box(1060, v, 1100, 120, 80, 40, C.STEEL_DARK)
    f.item("Штанга олимпийская")
    f.hcyl("v", 1120, -600, 1170, 2200, 15, C.STEEL)
    for v0 in (-450, 1530):
        f.hcyl("v", 1120, v0, 1170, 70, 225, C.BLACK, r_in=26)
        f.hcyl("v", 1120, v0 + (70 if v0 < 0 else -40), 1170, 40, 30, C.STEEL)


def power_rack(sc, x, y, rot=0):
    """Силовая рама 1400 x 1400 x 2300 с турником."""
    f = Frame(sc, x, y, rot).item("Силовая рама")
    s, h = 1400, 2300
    for u in (0, s - 80):
        for v in (0, s - 80):
            f.box(u, v, 0, 80, 80, h, C.STEEL_DARK)
    for v in (0, s - 80):
        f.box(0, v, h - 80, s, 80, 80, C.STEEL_DARK)
        f.box(0, v, 0, s, 80, 60, C.STEEL_DARK)
    f.box(0, 0, h - 80, 80, s, 80, C.STEEL_DARK)
    f.hcyl("v", s - 40, -80, h + 40, s + 160, 16, C.STEEL)  # турник
    for v in (0, s - 80):
        f.box(80, v, 900, s - 160, 80, 40, C.STEEL)  # страховочные упоры
    f.item("Платформа")
    f.box(-300, -300, 0, s + 600, s + 600, 20, C.WOOD)


def dumbbell_rack(sc, x, y, rot=0, n=8):
    """Стойка с гантелями (n пар), длина около 2000."""
    f = Frame(sc, x, y, rot).item("Стойка для гантелей")
    length = n * 250 + 100
    for u in (0, length / 2 - 40, length - 80):
        f.box(u, 0, 0, 80, 600, 750, C.STEEL_DARK)
    f.box(0, 0, 450, length, 280, 30, C.STEEL)
    f.box(0, 300, 750, length, 300, 30, C.STEEL)
    for k in range(n):
        r = 55 + 4 * k
        u = 80 + k * 250
        for v, z in ((20, 480), (320, 780)):
            f.item("Гантель")
            f.hcyl("v", u + 80, v, z + r, 70, r, C.BLACK)
            f.hcyl("v", u + 80, v + 70, z + r, 120, 17, C.STEEL)
            f.hcyl("v", u + 80, v + 190, z + r, 70, r, C.BLACK)


def plate_tree(sc, x, y):
    """Вертикальная стойка для блинов (блины лежат стопкой на штыре)."""
    sc.item("Стойка для блинов")
    sc.box(x - 400, y - 400, 0, 800, 800, 40, C.STEEL_DARK)
    sc.cyl(x, y, 40, 25, 700, C.STEEL)
    zz = 40
    for r, h in ((225, 50), (225, 50), (200, 40), (180, 35), (160, 30),
                 (135, 25), (110, 20)):
        sc.item("Блин")
        sc.cyl(x, y, zz, r, h, C.BLACK, r_in=26)
        zz += h + 2


def kettlebells(sc, x, y, n=6):
    for k in range(n):
        sc.item("Гиря")
        r = 90 + 8 * k
        cx = x + sum(2 * (90 + 8 * i) + 80 for i in range(k)) + r
        sc.cyl(cx, y, 0, r, 1.6 * r, C.BLACK)
        sc.cyl(cx, y, 1.6 * r, 0.75 * r, 0.25 * r, C.BLACK)
        sc.hcyl("x", cx - 0.6 * r, y, 1.85 * r + 70, 1.2 * r, 15, C.STEEL_DARK)
        sc.cyl(cx - 0.6 * r, y, 1.85 * r, 15, 70, C.STEEL_DARK)
        sc.cyl(cx + 0.6 * r - 1, y, 1.85 * r, 15, 70, C.STEEL_DARK)


def cable_crossover(sc, x, y, rot=0):
    """Кроссовер: две колонны с грузовыми блоками и перемычкой."""
    f = Frame(sc, x, y, rot).item("Кроссовер")
    span = 3200
    for u in (0, span - 600):
        f.box(u, 0, 0, 600, 600, 60, C.STEEL_DARK)
        f.box(u + 50, 50, 60, 80, 80, 2300, C.STEEL_DARK)
        f.box(u + 470, 50, 60, 80, 80, 2300, C.STEEL_DARK)
        f.box(u + 160, 200, 60, 280, 150, 900, C.BLACK)  # грузовой блок
        f.cyl(u + 300, 275, 960, 10, 1400, C.STEEL)
        f.box(u + 50, 50, 2360, 500, 80, 80, C.STEEL_DARK)
        f.box(u + 50, 50, 2360, 80, 500, 80, C.STEEL_DARK)
        f.box(u + 470, 50, 2360, 80, 500, 80, C.STEEL_DARK)
    f.box(0, 50, 2360, span, 80, 80, C.STEEL_DARK)
    f.hcyl("u", 400, 300, 2300, span - 800, 16, C.STEEL)


def adjustable_bench(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Скамья регулируемая")
    f.box(0, 150, 0, 1300, 100, 80, C.STEEL_DARK)
    f.box(0, 0, 0, 80, 400, 60, C.STEEL_DARK)
    f.box(1220, 0, 0, 80, 400, 60, C.STEEL_DARK)
    f.box(300, 170, 80, 60, 60, 320, C.STEEL_DARK)
    f.box(900, 170, 80, 60, 60, 320, C.STEEL_DARK)
    f.box(0, 70, 400, 1300, 260, 60, C.LEATHER)


def mirror_wall(sc, x, y, rot=0, length=6000):
    f = Frame(sc, x, y, rot).item("Зеркала")
    n = int(length // 1500)
    for k in range(n):
        f.box(k * 1500 + 5, 0, 300, 1490, 10, 2000, C.MIRROR)
    f.box(0, 0, 200, n * 1500, 30, 100, C.STEEL)


def floor_mats_grid(sc, x, y, nx, ny, size=1000, t=20, color=C.RUBBER,
                    name="Резиновое покрытие"):
    sc.item(name)
    for i in range(nx):
        for j in range(ny):
            sc.box(x + i * size + 2, y + j * size + 2, 0, size - 4, size - 4, t,
                   color)


# ----------------------------------------------- гимнастика и единоборства
def tatami(sc, x, y, nx, ny, t=40):
    """Татами 1000 x 2000: центр — один цвет, периметр — другой."""
    sc.item("Татами")
    for i in range(nx):
        for j in range(ny):
            edge = i in (0, nx - 1) or j in (0, ny - 1)
            sc.box(x + i * 2000 + 2, y + j * 1000 + 2, 0, 1996, 996, t,
                   C.TATAMI_2 if edge else C.TATAMI_1)


def rings(sc, x, y, h_ceiling):
    """Гимнастические кольца на тросах."""
    sc.item("Гимнастические кольца")
    for dy in (-250, 250):
        sc.cyl(x, y + dy, 2600, 6, h_ceiling - 2600, C.STEEL)
        sc.hcyl("y", x, y + dy - 14, 2470, 28, 120, C.WOOD, r_in=95)


def climbing_rope(sc, x, y, h_ceiling):
    sc.item("Канат для лазания")
    sc.cyl(x, y, 300, 20, h_ceiling - 300, C.WOOD)
    sc.cyl(x, y, h_ceiling - 200, 60, 200, C.STEEL_DARK)


def horizontal_bar(sc, x, y, rot=0, span=2400):
    f = Frame(sc, x, y, rot).item("Перекладина гимнастическая")
    for u in (0, span):
        f.cyl(u, 0, 0, 50, 2600, C.STEEL)
        f.cyl(u, 0, 0, 250, 30, C.STEEL_DARK)
    f.hcyl("u", 0, 0, 2550, span, 14, C.STEEL)
    f.item("Растяжки перекладины")
    for u in (0, span):
        for v in (-1500, 1500):
            f.box(u - 10, min(0, v), 0, 20, abs(v), 15, C.STEEL_DARK)


def parallel_bars(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Брусья параллельные")
    f.box(0, 0, 0, 2500, 600, 100, C.STEEL_DARK)
    for v in (50, 470):
        for u in (550, 1870):
            f.box(u, v, 100, 80, 80, 1500, C.STEEL)
        f.hcyl("u", 0, v + 40, 1650, 2500, 25, C.WOOD)


def balance_beam(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Бревно гимнастическое")
    f.box(0, 0, 1150, 5000, 100, 160, C.WOOD)
    f.box(0, 0, 1145, 5000, 100, 5, C.LEATHER)
    for u in (700, 4200):
        f.box(u, -500, 0, 100, 1100, 60, C.STEEL_DARK)
        f.box(u, 20, 60, 100, 60, 1085, C.STEEL_DARK)


def vault_horse(sc, x, y, rot=0):
    f = Frame(sc, x, y, rot).item("Козёл гимнастический")
    f.box(0, 0, 900, 600, 350, 250, C.LEATHER)
    for du in (50, 490):
        for dv in (30, 260):
            f.box(du, dv, 0, 60, 60, 900, C.WOOD_DARK)
    f.item("Мостик гимнастический")
    f.box(-1500, 0, 0, 1200, 600, 60, C.WOOD)
    f.box(-700, 0, 60, 400, 600, 140, C.WOOD)


def punching_bag(sc, x, y, h_ceiling):
    sc.item("Боксёрский мешок")
    sc.cyl(x, y, 600, 170, 1100, C.LEATHER)
    sc.cyl(x, y, 1700, 30, 200, C.STEEL)
    sc.cyl(x, y, 1900, 6, h_ceiling - 1900, C.STEEL)


def gym_ball(sc, x, y, r=325, color=C.MAT_RED):
    sc.item("Фитбол")
    # шар аппроксимируем тремя цилиндрами
    sc.cyl(x, y, 0, r * 0.6, r * 0.2, color)
    sc.cyl(x, y, r * 0.2, r * 0.9, r * 0.4, color)
    sc.cyl(x, y, r * 0.6, r, r * 0.8, color)
    sc.cyl(x, y, r * 1.4, r * 0.9, r * 0.4, color)
    sc.cyl(x, y, r * 1.8, r * 0.6, r * 0.2, color)


def bench_lockers(sc, x, y, rot=0, length=3000):
    """Скамья с вешалкой (раздевалочная)."""
    f = Frame(sc, x, y, rot).item("Скамья с вешалкой")
    f.box(0, 100, 420, length, 350, 40, C.WOOD)
    for u in (100, length - 140):
        f.box(u, 100, 0, 40, 350, 420, C.STEEL_DARK)
        f.box(u, 0, 0, 40, 60, 1900, C.STEEL_DARK)
    f.box(0, 0, 1700, length, 30, 120, C.WOOD)
    for k in range(int(length // 300)):
        f.box(150 + k * 300, 30, 1750, 20, 80, 20, C.STEEL)
