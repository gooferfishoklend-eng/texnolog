# -*- coding: utf-8 -*-
"""Построение модели спортивного зала в КОМПАС-3D через API 5.

Запуск (Windows, установлен КОМПАС-3D v17 и новее):
    1) pip install pywin32
    2) python kompas_build.py 1        # номер варианта: 1, 2 или 3
   или в КОМПАС-3D: «Приложения → Python → Запустить скрипт»
   (тогда номер варианта берётся из переменной VARIANT ниже).

Скрипт создаёт новую деталь (*.m3d) и строит в ней весь зал:
стены с проёмами, окна, двери, пол, перекрытие, оборудование,
светильники, вентиляцию и отопление. Используются только две операции:
  * «Элемент выдавливания» эскиза на плоскости, параллельной XOY;
  * «Элемент вращения» эскиза вокруг осевой линии (для горизонтальных
    цилиндров: перекладин, штанг, гантелей).
Одинаковые по высоте и цвету непересекающиеся контуры объединяются в
один эскиз, чтобы дерево построения было компактнее.
Ось Z модели направлена вверх (пол лежит в плоскости XOY).
"""
import os
import sys

VARIANT = 1          # какой вариант строить при запуске без аргументов
SAVE = True          # сохранить деталь рядом со скриптом в out/<вариант>/

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym.scene import Box, HCyl  # noqa: E402
from gym.variants import VARIANTS  # noqa: E402


# --------------------------------------------------------------- КОМПАС
def connect():
    import pythoncom
    from win32com.client import Dispatch, gencache

    api5 = gencache.EnsureModule("{0422828C-F174-495E-AC5D-D31014DBBE87}", 0, 1, 0)
    c3d = gencache.EnsureModule("{2CAF168C-7961-4B90-9DA2-701419BEEFE3}", 0, 1,
                                0).constants
    app = Dispatch("Kompas.Application.5")
    kompas = api5.KompasObject(app._oleobj_.QueryInterface(
        api5.KompasObject.CLSID, pythoncom.IID_IDispatch))
    kompas.Visible = True
    return kompas, c3d


def rgb(hex_color):
    """'#rrggbb' -> целое КОМПАС (0x00BBGGRR)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return r | (g << 8) | (b << 16)


class Builder:
    def __init__(self, kompas, c3d):
        self.k, self.c = kompas, c3d
        self.doc = kompas.Document3D()
        self.doc.Create(False, True)  # видимый документ, деталь
        self.part = self.doc.GetPart(c3d.pTop_Part)
        self.base = self.part.GetDefaultEntity(c3d.o3d_planeXOY)
        self.planes = {}
        self.ok = self.fail = 0

    def plane(self, z):
        z = round(z, 2)
        if abs(z) < 1e-6:
            return self.base
        if z not in self.planes:
            pl = self.part.NewEntity(self.c.o3d_planeOffset)
            d = pl.GetDefinition()
            d.direction = z > 0
            d.offset = abs(z)
            d.SetPlane(self.base)
            pl.hidden = True
            pl.Create()
            self.planes[z] = pl
        return self.planes[z]

    def sketch(self, z, draw):
        sk = self.part.NewEntity(self.c.o3d_sketch)
        d = sk.GetDefinition()
        d.SetPlane(self.plane(z))
        sk.Create()
        doc2d = d.BeginEdit()
        draw(doc2d)
        d.EndEdit()
        return sk

    def _finish(self, ent, color, name):
        ent.name = name[:120]
        try:
            cp = ent.ColorParam()
            cp.color = rgb(color)
            cp.ambient, cp.diffuse, cp.specularity, cp.shininess = 0.5, 0.6, 0.4, 0.5
            cp.transparency = 0.5 if color.lower() in ("#9fd3f0", "#dbeafe") else 1.0
            cp.emission = 0.0
        except Exception:
            pass
        if ent.Create():
            self.ok += 1
            try:
                ent.Update()
            except Exception:
                pass
        else:
            self.fail += 1
            print("  не удалось построить:", name)

    def extrude(self, z, h, draw, color, name):
        sk = self.sketch(z, draw)
        ent = self.part.NewEntity(self.c.o3d_bossExtrusion)
        d = ent.GetDefinition()
        d.directionType = self.c.dtNormal
        d.SetSideParam(True, self.c.etBlind, h, 0, False)
        d.SetThinParam(False, 0, 0, 0)
        d.SetSketch(sk)
        self._finish(ent, color, name)

    def revolve(self, z, draw, color, name):
        sk = self.sketch(z, draw)
        ent = self.part.NewEntity(self.c.o3d_bossRotated)
        d = ent.GetDefinition()
        d.directionType = self.c.dtNormal
        d.toroidShellFlag = False
        d.SetSideParam(True, 360)
        d.SetThinParam(False, 0, 0, 0)
        d.SetSketch(sk)
        self._finish(ent, color, name)


# ------------------------------------------------- группировка эскизов
def footprint(p):
    if isinstance(p, Box):
        return (p.x, p.y, p.x + p.dx, p.y + p.dy)
    return (p.cx - p.r, p.cy - p.r, p.cx + p.r, p.cy + p.r)


def overlaps(a, b, gap=1.0):
    return not (a[2] + gap < b[0] or b[2] + gap < a[0]
                or a[3] + gap < b[1] or b[3] + gap < a[1])


def group_vertical(prims):
    """Box и Cyl -> группы (z, h, color, [prims]) без пересечений в плане."""
    groups = {}
    out = []
    for p in prims:
        h = p.dz if isinstance(p, Box) else p.h
        key = (round(p.z, 2), round(h, 2), p.color)
        fp = footprint(p)
        for g in groups.setdefault(key, []):
            if not any(overlaps(fp, footprint(q)) for q in g):
                g.append(p)
                break
        else:
            g = [p]
            groups[key].append(g)
            out.append((key, g))
    return out


def group_horizontal(prims):
    """HCyl на одной оси (одна прямая) с непересекающимися отрезками."""
    groups = {}
    out = []
    for p in prims:
        across = p.y if p.axis == "x" else p.x
        key = (p.axis, round(p.z, 2), round(across, 2), p.color)
        a0 = p.x if p.axis == "x" else p.y
        seg = (a0, a0 + p.length)
        for g in groups.setdefault(key, []):
            if all(seg[1] + 1 < s0 or e + 1 < seg[0] for s0, e, _ in g):
                g.append((*seg, p))
                break
        else:
            g = [(*seg, p)]
            groups[key].append(g)
            out.append((key, g))
    return out


def build(variant):
    sc = VARIANTS[variant]()
    print(f"{sc.title}: {len(sc.prims)} примитивов")
    kompas, c3d = connect()
    b = Builder(kompas, c3d)
    b.doc.author = "Проект спортивного зала"
    b.doc.comment = sc.title

    vertical = [p for p in sc.prims if not isinstance(p, HCyl)]
    horizontal = [p for p in sc.prims if isinstance(p, HCyl)]
    vgroups = group_vertical(vertical)
    hgroups = group_horizontal(horizontal)
    total = len(vgroups) + len(hgroups)
    print(f"операций: {total}")

    n = 0
    for (z, h, color), g in vgroups:
        def draw(d2, g=g):
            for p in g:
                if isinstance(p, Box):
                    x0, y0, x1, y1 = footprint(p)
                    d2.ksLineSeg(x0, y0, x1, y0, 1)
                    d2.ksLineSeg(x1, y0, x1, y1, 1)
                    d2.ksLineSeg(x1, y1, x0, y1, 1)
                    d2.ksLineSeg(x0, y1, x0, y0, 1)
                else:
                    d2.ksCircle(p.cx, p.cy, p.r, 1)
                    if p.r_in:
                        d2.ksCircle(p.cx, p.cy, p.r_in, 1)
        b.extrude(z, h, draw, color, g[0].item)
        n += 1
        if n % 25 == 0:
            print(f"  {n}/{total}")

    for (axis, z, across, color), g in hgroups:
        a_min = min(s for s, _, _ in g)
        a_max = max(e for _, e, _ in g)

        def draw(d2, g=g, axis=axis, across=across, a_min=a_min, a_max=a_max):
            # осевая линия (стиль 3) и прямоугольные профили по одну сторону
            if axis == "x":
                d2.ksLineSeg(a_min - 10, across, a_max + 10, across, 3)
            else:
                d2.ksLineSeg(across, a_min - 10, across, a_max + 10, 3)
            for s, e, p in g:
                r0, r1 = across + p.r_in, across + p.r
                pts = [(s, r0), (e, r0), (e, r1), (s, r1)]
                if axis == "y":
                    pts = [(v, u) for u, v in pts]
                for i in range(4):
                    (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 4]
                    d2.ksLineSeg(x0, y0, x1, y1, 1)
        b.revolve(z, draw, color, g[0][2].item)
        n += 1
        if n % 25 == 0:
            print(f"  {n}/{total}")

    print(f"готово: построено {b.ok}, ошибок {b.fail}")
    if SAVE:
        out = os.path.join(HERE, "out", sc.name)
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, sc.name + ".m3d")
        b.doc.SaveAs(path)
        print("сохранено:", path)


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else VARIANT)
