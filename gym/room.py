"""Ограждающие конструкции и инженерные системы зала."""
from . import colors as C


def opening(kind, pos, width, height, sill=0.0, leaves=1):
    """Проём в стене: kind = 'window' | 'door'; pos — начало по стене."""
    return dict(kind=kind, pos=pos, width=width, height=height, sill=sill,
                leaves=leaves)


class Room:
    """Зал с внутренними размерами L x W x H и толщиной стен t.

    Стены: 'S' (y<0), 'N' (y>W), 'W' (x<0), 'E' (x>L).
    Координата вдоль стены: для S/N — X, для W/E — Y.
    """

    def __init__(self, sc, L, W, H, t=380, wall_color=C.WALL):
        self.sc, self.L, self.W, self.H, self.t = sc, L, W, H, t
        self.wall_color = wall_color

    # --- вспомогательное: прямоугольник в системе стены -------------
    def wbox(self, wall, a, z, da, dz, off0, off1, color):
        """a..a+da вдоль стены, z..z+dz по высоте,
        off0..off1 — глубина от внутренней грани стены наружу
        (отрицательная глубина — выступ внутрь зала)."""
        L, W = self.L, self.W
        if wall == "S":
            self.sc.box(a, -off1, z, da, off1 - off0, dz, color)
        elif wall == "N":
            self.sc.box(a, W + off0, z, da, off1 - off0, dz, color)
        elif wall == "W":
            self.sc.box(-off1, a, z, off1 - off0, da, dz, color)
        elif wall == "E":
            self.sc.box(L + off0, a, z, off1 - off0, da, dz, color)

    def wall_range(self, wall):
        t = self.t
        return (-t, self.L + t) if wall in "SN" else (0.0, self.W)

    # --- конструкции ------------------------------------------------
    def floor(self, finish_color, finish_name="Покрытие пола", slab=300,
              finish=10):
        t, L, W = self.t, self.L, self.W
        self.sc.item("Плита пола")
        self.sc.box(-t, -t, -slab - finish, L + 2 * t, W + 2 * t, slab, C.CONCRETE)
        self.sc.item(finish_name)
        self.sc.box(0, 0, -finish, L, W, finish, finish_color)

    def ceiling(self, thickness=250):
        t = self.t
        self.sc.item("Перекрытие")
        self.sc.box(-t, -t, self.H, self.L + 2 * t, self.W + 2 * t, thickness,
                    C.CEILING)

    def walls(self, openings):
        """openings: {'S': [opening(...), ...], ...}"""
        H, t = self.H, self.t
        for wall in "SNWE":
            names = {"S": "южная", "N": "северная", "W": "западная", "E": "восточная"}
            self.sc.item(f"Стена {names[wall]}")
            a0, a1 = self.wall_range(wall)
            ops = sorted(openings.get(wall, []), key=lambda o: o["pos"])
            cur = a0
            for o in ops:
                self.wbox(wall, cur, 0, o["pos"] - cur, H, 0, t, self.wall_color)
                top = o["sill"] + o["height"]
                self.wbox(wall, o["pos"], 0, o["width"], o["sill"], 0, t,
                          self.wall_color)
                self.wbox(wall, o["pos"], top, o["width"], H - top, 0, t,
                          self.wall_color)
                cur = o["pos"] + o["width"]
            self.wbox(wall, cur, 0, a1 - cur, H, 0, t, self.wall_color)
            for o in ops:
                if o["kind"] == "window":
                    self._window(wall, o)
                else:
                    self._door(wall, o)

    def _window(self, wall, o):
        sc, t = self.sc, self.t
        a, w, z, h = o["pos"], o["width"], o["sill"], o["height"]
        f = 70  # ширина профиля рамы
        mid0, mid1 = t / 2 - 40, t / 2 + 40
        sc.item("Окно")
        self.wbox(wall, a, z, w, f, mid0, mid1, C.FRAME)
        self.wbox(wall, a, z + h - f, w, f, mid0, mid1, C.FRAME)
        self.wbox(wall, a, z + f, f, h - 2 * f, mid0, mid1, C.FRAME)
        self.wbox(wall, a + w - f, z + f, f, h - 2 * f, mid0, mid1, C.FRAME)
        n = max(1, round(w / 1000))  # импосты
        step = (w - f) / n
        for i in range(1, n):
            self.wbox(wall, a + i * step, z + f, f, h - 2 * f, mid0, mid1, C.FRAME)
        self.wbox(wall, a + f, z + f, w - 2 * f, h - 2 * f,
                  t / 2 - 12, t / 2 + 12, C.GLASS)
        if z > 0:  # подоконник
            self.wbox(wall, a - 50, z - 40, w + 100, 40, -80, mid0, C.SILL)
        # защитная сетка в спортзале
        if z < 2500:
            sc.item("Защитная решётка окна")
            bars = int(w // 150)
            for i in range(1, bars):
                self.wbox(wall, a + i * w / bars - 6, z, 12, h, -140, -128, C.STEEL)
            for zz in (z + 40, z + h - 60):
                self.wbox(wall, a - 40, zz, w + 80, 20, -150, -120, C.STEEL)

    def _door(self, wall, o):
        a, w, h = o["pos"], o["width"], o["height"]
        f = 80
        self.sc.item("Дверь")
        self.wbox(wall, a, 0, f, h, -20, 120, C.FRAME)
        self.wbox(wall, a + w - f, 0, f, h, -20, 120, C.FRAME)
        self.wbox(wall, a, h - f, w, f, -20, 120, C.FRAME)
        n = o["leaves"]
        lw = (w - 2 * f - (n - 1) * 10) / n
        for i in range(n):
            la = a + f + i * (lw + 10)
            self.wbox(wall, la, 10, lw, h - f - 10, 30, 75, C.DOOR)
            # ручка-штанга «антипаника» со стороны зала
            hx = la + 100 if i % 2 else la + lw - 100 - min(600, lw - 250)
            self.wbox(wall, hx, 1000, min(600, lw - 250), 40, -40, 30, C.HANDLE)
        # табличка «Выход» над дверью
        self.sc.item("Указатель «Выход»")
        self.wbox(wall, a + w / 2 - 200, h + 150, 400, 150, -30, 0, C.MAT_GREEN)

    # --- инженерные системы -----------------------------------------
    def lights_grid(self, nx, ny, z_hang, kind="panel", margin=None):
        """Подвесные светильники: kind = 'panel' (линейные) | 'dome' (купольные)."""
        L, W, H = self.L, self.W, self.H
        for i in range(nx):
            for j in range(ny):
                cx = L * (i + 0.5) / nx
                cy = W * (j + 0.5) / ny
                self.sc.item("Светильник")
                if kind == "panel":
                    lx, ly = 1500, 320
                    self.sc.box(cx - lx / 2, cy - ly / 2, z_hang, lx, ly, 90,
                                C.LAMP_BODY)
                    self.sc.box(cx - lx / 2 + 30, cy - ly / 2 + 30, z_hang - 10,
                                lx - 60, ly - 60, 10, C.LAMP)
                    # защитная решётка спортивного исполнения
                    for k in range(1, 6):
                        self.sc.box(cx - lx / 2 + k * lx / 6 - 5, cy - ly / 2,
                                    z_hang - 30, 10, ly, 20, C.STEEL)
                    for dxs in (-lx / 2 + 150, lx / 2 - 150):
                        self.sc.cyl(cx + dxs, cy, z_hang + 90, 8,
                                    H - z_hang - 90, C.STEEL)
                else:
                    self.sc.cyl(cx, cy, z_hang, 260, 220, C.LAMP_BODY)
                    self.sc.cyl(cx, cy, z_hang - 10, 220, 10, C.LAMP)
                    self.sc.cyl(cx, cy, z_hang + 220, 60, 120, C.LAMP_BODY)
                    self.sc.cyl(cx, cy, z_hang + 340, 10, H - z_hang - 340,
                                C.STEEL)

    def vent_duct(self, y_axis, z_bottom, n_diff, w=600, h=400, entry="W"):
        """Приточный воздуховод вдоль зала с диффузорами и подвесами,
        ввод через стену entry ('W' или 'E')."""
        L, H, t = self.L, self.H, self.t
        sc = self.sc
        sc.item("Воздуховод приточный")
        x0, x1 = (-t - 200, L - 600) if entry == "W" else (600, L + t + 200)
        sc.box(x0, y_axis - w / 2, z_bottom, x1 - x0, w, h, C.DUCT)
        # фланцы через каждые 1250 мм
        x = x0 + 1250
        while x < x1 - 100:
            sc.box(x - 15, y_axis - w / 2 - 20, z_bottom - 20, 30, w + 40, h + 40,
                   C.STEEL)
            x += 1250
        for k in range(n_diff):
            cx = 1200 + (L - 2400) * (k + 0.5) / n_diff
            sc.item("Диффузор")
            sc.box(cx - 150, y_axis - 150, z_bottom - 120, 300, 300, 120, C.DUCT)
            sc.box(cx - 300, y_axis - 300, z_bottom - 160, 600, 600, 40, C.DIFFUSER)
        sc.item("Подвесы воздуховода")
        for k in range(int(L // 3000) + 1):
            cx = min(max(1500 + k * 3000, 300), L - 900)
            for sy in (-1, 1):
                sc.cyl(cx, y_axis + sy * (w / 2 + 40), z_bottom - 40, 8,
                       H - z_bottom + 40, C.STEEL)
            sc.box(cx - 25, y_axis - w / 2 - 60, z_bottom - 40, 50, w + 120, 40,
                   C.STEEL)

    def exhaust_grilles(self, wall, positions, z=None, size=(600, 400)):
        z = self.H - 900 if z is None else z
        for a in positions:
            self.sc.item("Вытяжная решётка")
            self.wbox(wall, a, z, size[0], size[1], -30, 0, C.DIFFUSER)
            for k in range(1, 6):
                self.wbox(wall, a + 20, z + k * size[1] / 6 - 6, size[0] - 40, 12,
                          -45, -30, C.STEEL)

    def radiator(self, wall, a, length=1200, z=150, height=550):
        self.sc.item("Радиатор отопления")
        sections = int(length // 100)
        for i in range(sections):
            self.wbox(wall, a + i * 100, z, 80, height, -160, -60, C.RADIATOR)
        self.wbox(wall, a, z + 40, length, 40, -140, -80, C.RADIATOR)
        self.wbox(wall, a, z + height - 80, length, 40, -140, -80, C.RADIATOR)
        # защитный экран из деревянных реек
        self.sc.item("Экран радиатора")
        for i in range(int((length + 120) // 80)):
            self.wbox(wall, a - 60 + i * 80, z - 100, 40, height + 200, -230, -200,
                      C.WOOD)
        self.wbox(wall, a - 80, z + height + 100, length + 160, 30, -250, -60,
                  C.WOOD)
