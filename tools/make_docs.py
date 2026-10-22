"""Спецификация оборудования (Markdown) для каждого варианта.

    python tools/make_docs.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gym.scene import Box, Cyl  # noqa: E402
from gym.variants import VARIANTS  # noqa: E402

STRUCTURE = ("Плита пола", "Перекрытие", "Стена", "Паркет", "Наливной пол",
             "Покрытие", "Окно", "Дверь", "Защитная решётка", "Указатель")
ENGINEERING = ("Светильник", "Воздуховод", "Диффузор", "Подвесы", "Вытяжная",
               "Радиатор", "Экран радиатора")


def bbox(prims):
    xs0, ys0, zs0, xs1, ys1, zs1 = [], [], [], [], [], []
    for p in prims:
        if isinstance(p, Box):
            a = (p.x, p.y, p.z, p.x + p.dx, p.y + p.dy, p.z + p.dz)
        elif isinstance(p, Cyl):
            a = (p.cx - p.r, p.cy - p.r, p.z, p.cx + p.r, p.cy + p.r, p.z + p.h)
        else:
            lx = p.length if p.axis == "x" else 0
            ly = p.length if p.axis == "y" else 0
            a = (p.x - (0 if lx else p.r), p.y - (0 if ly else p.r), p.z - p.r,
                 p.x + (lx or p.r), p.y + (ly or p.r), p.z + p.r)
        for lst, v in zip((xs0, ys0, zs0, xs1, ys1, zs1), a):
            lst.append(v)
    return max(xs1) - min(xs0), max(ys1) - min(ys0), max(zs1) - min(zs0)


def spec(sc):
    rows = {}
    for name, prims in sc.items().items():
        base = re.sub(r" \(\d+\)$", "", name)
        r = rows.setdefault(base, dict(n=0, size=None))
        r["n"] += 1
        if r["size"] is None:
            r["size"] = bbox(prims)
    return rows


def section(rows, pred):
    out = ["| № | Наименование | Кол-во | Габариты Д×Ш×В, мм |",
           "|---|---|---|---|"]
    i = 0
    for name, r in rows.items():
        if not pred(name):
            continue
        i += 1
        d, w, h = (round(v) for v in r["size"])
        out.append(f"| {i} | {name} | {r['n']} | {d}×{w}×{h} |")
    return "\n".join(out)


def main():
    for n, fn in sorted(VARIANTS.items()):
        sc = fn()
        mod = sys.modules[fn.__module__]
        L, W, H = sc.size
        rows = spec(sc)
        is_struct = lambda s: s.startswith(STRUCTURE)  # noqa: E731
        is_eng = lambda s: s.startswith(ENGINEERING)  # noqa: E731
        text = f"""# {sc.title}

{mod.__doc__.split(chr(10), 1)[1].strip()}

**Внутренние размеры:** {L/1000:g} × {W/1000:g} м, высота {H/1000:g} м, площадь {L*W/1e6:g} м².

![3D-вид](preview_3d.png)

![План](plan.png)

## Файлы

| Файл | Что это |
|---|---|
| `{sc.name}.step` | Модель для КОМПАС-3D: «Файл → Открыть» → тип STEP. Откроется сборкой, где каждый объект — отдельный компонент |
| `viewer.html` | Интерактивный 3D-просмотр в браузере (вращение мышью, подписи объектов) |
| `preview_3d.png`, `plan.png` | Картинки для отчёта/презентации |

Построить модель «родными» операциями КОМПАС: `python kompas_build.py {n}` (см. корневой README).

## Строительные конструкции

{section(rows, is_struct)}

## Спортивное оборудование и оснащение

{section(rows, lambda s: not is_struct(s) and not is_eng(s))}

## Освещение, вентиляция, отопление

{section(rows, is_eng)}
"""
        out = os.path.join(os.path.dirname(__file__), "..", "out", sc.name)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "README.md"), "w", encoding="utf-8") as f:
            f.write(text)
        print(sc.name, len(rows), "позиций")


if __name__ == "__main__":
    main()
