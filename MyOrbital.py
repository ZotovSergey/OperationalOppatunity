from math import sin, cos, sqrt
from numpy import rad2deg, all, arctan2
import numpy as np
from pyorbital.orbital import Orbital
from pyorbital import astronomy                                                                                 # Импорт класса Point для работы с точками на плоскости из пакета shapely
import Packeges as pack

XKMPER = 6378.135

F = 1 / 298.257223563  # Earth flattening WGS-84
A = 6378.137  # WGS84 Equatorial radius

class MyOrbital(Orbital):
    def get_dec_and_vel(self, utc_time):
        """Calculate sublon, sublat and altitude of satellite.
        http://celestrak.com/columns/v02n03/
        """
        (pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z) = self.get_position(
            utc_time, normalize=False)

        decCoord = pack.DecartCoordinate(pack.MyGeometry.Point(pos_x, pos_y, pos_z))
        velVect = pack.MyGeometry.Vector(vel_x, vel_y, vel_z)

        return decCoord, velVect

def decardToGeoCoordinates(decCoord, utc_time, alt):
    pos_x = decCoord.decCoord.radVect.x
    pos_y = decCoord.decCoord.radVect.y
    pos_z = decCoord.decCoord.radVect.z

    lon = ((np.arctan2(pos_y, pos_x) - astronomy.gmst(utc_time))
           % (2 * np.pi))

    lon = np.where(lon > np.pi, lon - np.pi * 2, lon)
    lon = np.where(lon <= -np.pi, lon + np.pi * 2, lon)

    r = sqrt(pos_x * pos_x + pos_y * pos_y)
    lat = arctan2(pos_z, r)
    e2 = F * (2 - F)
    while True:
        lat2 = lat
        c = 1 / (np.sqrt(1 - e2 * (sin(lat2) ** 2)))
        lat = arctan2(pos_z + c * e2 * sin(lat2), r)
        if all(abs(lat - lat2) < 1e-10):
            break
    geoCoord = pack.GeoCoordinate(rad2deg(lon), rad2deg(lat), alt)
    return geoCoord
