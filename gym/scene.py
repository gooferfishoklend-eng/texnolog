"""Примитивы сцены. Все размеры в миллиметрах.

Система координат: X — вдоль длины зала, Y — вдоль ширины, Z — вверх.
Начало координат — внутренний угол зала на уровне чистого пола.
Все тела строятся только операциями на плоскостях, параллельных XOY
(выдавливание вверх и вращение вокруг горизонтальной оси), поэтому
их одинаково легко воспроизвести в КОМПАС-3D вручную или макросом.
"""
from dataclasses import dataclass, field


@dataclass
class Box:
    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float
    color: str
    item: str


@dataclass
class Cyl:
    """Вертикальный цилиндр (или труба, если r_in > 0)."""
    cx: float
    cy: float
    z: float
    r: float
    h: float
    color: str
    item: str
    r_in: float = 0.0


@dataclass
class HCyl:
    """Горизонтальный цилиндр вдоль оси X или Y (тело вращения).

    Ось проходит через точку (x, y, z) и идёт на length в положительную
    сторону оси axis.
    """
    axis: str
    x: float
    y: float
    z: float
    length: float
    r: float
    color: str
    item: str
    r_in: float = 0.0


@dataclass
class Scene:
    name: str
    title: str
    size: tuple  # внутренние размеры зала (L, W, H)
    prims: list = field(default_factory=list)
    _item: str = "Без названия"
    _counts: dict = field(default_factory=dict)

    def item(self, name):
        """Начать новый элемент спецификации (повторы получают номер)."""
        n = self._counts.get(name, 0) + 1
        self._counts[name] = n
        self._item = name if n == 1 else f"{name} ({n})"
        return self

    def box(self, x, y, z, dx, dy, dz, color):
        # нормализуем отрицательные размеры
        if dx < 0:
            x, dx = x + dx, -dx
        if dy < 0:
            y, dy = y + dy, -dy
        if dz < 0:
            z, dz = z + dz, -dz
        if dx > 0 and dy > 0 and dz > 0:
            self.prims.append(Box(x, y, z, dx, dy, dz, color, self._item))

    def cyl(self, cx, cy, z, r, h, color, r_in=0.0):
        self.prims.append(Cyl(cx, cy, z, r, h, color, self._item, r_in))

    def hcyl(self, axis, x, y, z, length, r, color, r_in=0.0):
        if length < 0:
            if axis == "x":
                x += length
            else:
                y += length
            length = -length
        self.prims.append(HCyl(axis, x, y, z, length, r, color, self._item, r_in))

    def items(self):
        """Спецификация: {элемент: [примитивы]} в порядке появления."""
        out = {}
        for p in self.prims:
            out.setdefault(p.item, []).append(p)
        return out
