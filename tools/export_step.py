"""Экспорт вариантов в STEP (AP214, с цветами) через CadQuery.

    python tools/export_step.py [номер варианта ...]

STEP открывается в КОМПАС-3D: «Файл → Открыть», тип «STEP (*.stp, *.step)».
Каждый элемент спецификации (стена, скамья, тренажёр...) становится
отдельным компонентом сборки со своим именем и цветом.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cadquery as cq  # noqa: E402

from gym.scene import Box, Cyl  # noqa: E402
from gym.variants import VARIANTS  # noqa: E402


def solid(p):
    if isinstance(p, Box):
        return (cq.Workplane("XY", origin=(0, 0, p.z))
                .center(p.x + p.dx / 2, p.y + p.dy / 2).rect(p.dx, p.dy)
                .extrude(p.dz))
    if isinstance(p, Cyl):
        wp = cq.Workplane("XY", origin=(p.cx, p.cy, p.z)).circle(p.r)
        if p.r_in:
            wp = wp.circle(p.r_in)
        return wp.extrude(p.h)
    # горизонтальный цилиндр: эскиз на плоскости, перпендикулярной оси
    if p.axis == "x":
        wp = cq.Workplane("YZ", origin=(p.x, p.y, p.z))
    else:
        wp = cq.Workplane("XZ", origin=(p.x, p.y, p.z))
    wp = wp.circle(p.r)
    if p.r_in:
        wp = wp.circle(p.r_in)
    # у плоскости XZ нормаль направлена в -Y
    return wp.extrude(p.length if p.axis == "x" else -p.length)


def hex_to_color(h):
    h = h.lstrip("#")
    return cq.Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)), 1.0)


def build_assembly(sc):
    asm = cq.Assembly(name=sc.name)
    for name, prims in sc.items().items():
        sub = cq.Assembly(name=name)
        by_color = {}
        for p in prims:
            by_color.setdefault(p.color, []).append(solid(p).val())
        for k, (col, solids) in enumerate(by_color.items()):
            shape = solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids)
            sub.add(shape, name=f"{name}-{k + 1}", color=hex_to_color(col))
        asm.add(sub)
    return asm


def main(nums):
    for n in nums:
        sc = VARIANTS[n]()
        out = os.path.join(os.path.dirname(__file__), "..", "out", sc.name)
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, f"{sc.name}.step")
        build_assembly(sc).export(path)
        print(sc.name, "->", path, f"{os.path.getsize(path) / 1e6:.1f} МБ")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or sorted(VARIANTS))
