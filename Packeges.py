from datetime import datetime, timedelta                                                                                # Импорт классов datetime, работающего с датой и временем; timedelta, для определения интервала времени из пакета datetime
from pyorbital import tlefile                                                                                           # Импорт класса tlefile, работающего со строками tle и скачивающий их из the Internet из пакетоа pyorbital                                                                            # Импорт класса Orbital для прогнозирования координат спутника по строкам tle из пакета pyorbital
import shapefile                                                                                                        # Импорт пакеты shapefile для работы с shape-файлами
import numpy as np                                                                                                      # Импорт пакета numpy для работы с массивами
from shapely.geometry import Point                                                                                      # Импорт класса Point для работы с точками на плоскости из пакета shapely
from shapely.geometry.polygon import Polygon                                                                            # Импорт класса Polygon для работы с многоугольниками на плоскости из пакета shapely
from pyorbital.astronomy import sun_zenith_angle
from SatelliteGroup import *
from Coordinates2 import *
from MyOrbital import *
import MyGeometry
from AdditionalFunctions import *
from Earth import *
from Constants import *
from ShapePolygon import *