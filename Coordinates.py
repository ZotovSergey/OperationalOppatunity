import Packeges as pack
import math

EARTH_RADIUS = 6378.137

# Класс Coordinate объединяет широту, долготу и высоту некоторой точки в одну структуру
class GeoCoordinate:
    def __init__(self, long, lat, alt):                                                                                 # Конструктор класса Coordinate принимает широту (градусы), долготу long (градусы), высоту alt (километры)
        self.long = long                                                                                                # Присвоение полю long значения long
        self.lat = lat                                                                                                  # Присвоение полю lat значения lat
        self.alt = alt

    def __str__(self):
        return (str(self.lat) + '\t' + str(self.long) + '\t' + str(self.alt))

    def nulAlt(self):
        return GeoCoordinate(self.long, self.lat, 0)


class DecartCoordinate:
    def __init__(self, decCoord):
        self.decCoord = decCoord

def distBetweenDecCoord(decCoord1, decCoord2):
    lat1 = math.pi * decCoord1.lat / 180
    lat2 = math.pi * decCoord2.lat / 180
    deltaLong = math.pi * (decCoord1.long - decCoord2.long) / 180

    sinLat1 = math.sin(lat1)
    cosLat1 = math.cos(lat1)
    sinLat2 = math.sin(lat2)
    cosLat2 = math.cos(lat2)
    sinDelLong = math.sin(deltaLong)
    cosDelLong = math.cos(deltaLong)

    delAngle = math.atan((((cosLat2 * sinDelLong) ** 2 + (cosLat1 * sinLat2
            - sinLat1 * cosLat2 * cosDelLong) ** 2) ** 0.5)
            / (sinLat1 * sinLat2 + cosLat1 * cosLat2 * cosDelLong))

    if delAngle < 0:
        delAngle += math.pi

    return delAngle * EARTH_RADIUS


