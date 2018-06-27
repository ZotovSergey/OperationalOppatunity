import Packeges as pack


class Earth:
    def __init__(self, a, b, c):
        self.ellipsoid = pack.MyGeometry.CanonEllipsoid(a, b, c)