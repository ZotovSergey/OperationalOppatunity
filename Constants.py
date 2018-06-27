import Packeges as pack

def EARTH_FREQUENCY():
    return 0.000072722052166430399038487115353692

def SECONDS_IN_DAY():
    return 86400

def ELLIPSOID_AXISES_WGS_84():
    A = 6378.137                                                                                                        # A, B, C - оси эллипсоида, использующегося в модели координат WGS-84
    B = 6378.137
    C = 6356.75231424518
    return pack.MyGeometry.CanonEllipsoid(A, B, C)