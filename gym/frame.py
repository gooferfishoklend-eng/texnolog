"""Локальная система координат оборудования (поворот кратен 90°)."""


class Frame:
    def __init__(self, sc, x0, y0, rot=0):
        assert rot % 90 == 0
        self.sc, self.x0, self.y0, self.rot = sc, x0, y0, rot % 360

    def pt(self, u, v):
        r = self.rot
        if r == 0:
            return self.x0 + u, self.y0 + v
        if r == 90:
            return self.x0 - v, self.y0 + u
        if r == 180:
            return self.x0 - u, self.y0 - v
        return self.x0 + v, self.y0 - u

    def item(self, name):
        self.sc.item(name)
        return self

    def box(self, u, v, z, du, dv, dz, color):
        x1, y1 = self.pt(u, v)
        x2, y2 = self.pt(u + du, v + dv)
        self.sc.box(min(x1, x2), min(y1, y2), z, abs(x2 - x1), abs(y2 - y1), dz,
                    color)

    def cyl(self, u, v, z, r, h, color, r_in=0.0):
        x, y = self.pt(u, v)
        self.sc.cyl(x, y, z, r, h, color, r_in)

    def hcyl(self, axis, u, v, z, length, r, color, r_in=0.0):
        """axis = 'u' | 'v' — горизонтальный цилиндр в локальных осях."""
        x, y = self.pt(u, v)
        ex, ey = self.pt(u + (length if axis == "u" else 0),
                         v + (length if axis == "v" else 0))
        if abs(ex - x) > 1e-9:
            self.sc.hcyl("x", x, y, z, ex - x, r, color, r_in)
        else:
            self.sc.hcyl("y", x, y, z, ey - y, r, color, r_in)
