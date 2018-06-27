import math


def LatLongToMerc(lon, lat):
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5

    rLat = math.radians(lat)
    rLong = math.radians(lon)

    a = 6378137.0
    b = 6356752.3142
    f = (a - b) / a
    e = math.sqrt(2 * f - f ** 2)
    x = a * rLong
    y = a * math.log(
        math.tan(math.pi / 4 + rLat / 2) * ((1 - e * math.sin(rLat)) / (1 + e * math.sin(rLat))) ** (e / 2))
    return x, y


print(LatLongToMerc(103.380833, 51.6406 - 0.1182))
