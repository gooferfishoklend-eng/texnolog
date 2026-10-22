"""План зала (вид сверху, разрез на отм. +2.800). Нужен matplotlib.

    python tools/render_plan.py [номер варианта ...]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

from gym.scene import Box, Cyl  # noqa: E402
from gym.variants import VARIANTS  # noqa: E402

HIDE = ("Перекрытие",)


def render_plan(sc, path):
    L, W, H = sc.size
    fig, ax = plt.subplots(figsize=(16, 16 * (W + 2000) / (L + 2000)), dpi=110)
    prims = [p for p in sc.prims if not p.item.startswith(HIDE)
             and p.z < 2800 and not p.item.startswith(("Светильник", "Воздуховод",
                                                         "Диффузор", "Подвесы"))]
    prims.sort(key=lambda p: p.z + (p.dz if isinstance(p, Box) else
                                    p.h if isinstance(p, Cyl) else p.r))
    for p in prims:
        if isinstance(p, Box):
            ax.add_patch(Rectangle((p.x, p.y), p.dx, p.dy, fc=p.color,
                                   ec=(0, 0, 0, 0.35), lw=0.3))
        elif isinstance(p, Cyl):
            if p.r_in:
                ax.add_patch(Circle((p.cx, p.cy), p.r, fc="none", ec=p.color,
                                    lw=max(0.6, (p.r - p.r_in) / 25)))
            else:
                ax.add_patch(Circle((p.cx, p.cy), p.r, fc=p.color,
                                    ec=(0, 0, 0, 0.35), lw=0.3))
        else:
            if p.axis == "x":
                ax.add_patch(Rectangle((p.x, p.y - p.r), p.length, 2 * p.r,
                                       fc=p.color, ec=(0, 0, 0, 0.35), lw=0.3))
            else:
                ax.add_patch(Rectangle((p.x - p.r, p.y), 2 * p.r, p.length,
                                       fc=p.color, ec=(0, 0, 0, 0.35), lw=0.3))
    # размеры
    ax.annotate("", (0, -1300), (L, -1300),
                arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(L / 2, -1500, f"{L:.0f}", ha="center", va="top", fontsize=11)
    ax.annotate("", (-1300, 0), (-1300, W),
                arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(-1500, W / 2, f"{W:.0f}", ha="right", va="center", rotation=90,
            fontsize=11)
    ax.set_xlim(-2500, L + 1000)
    ax.set_ylim(-2500, W + 1000)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(f"{sc.title}: план (разрез на отм. +2.800)", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main(nums):
    for n in nums:
        sc = VARIANTS[n]()
        out = os.path.join(os.path.dirname(__file__), "..", "out", sc.name)
        os.makedirs(out, exist_ok=True)
        render_plan(sc, os.path.join(out, "plan.png"))
        print(sc.name, len(sc.prims), "примитивов")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or sorted(VARIANTS))
