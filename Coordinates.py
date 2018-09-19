from shapely.geometry import Point
from pyorbital import astronomy
import numpy
import math


class GeoCoordinates:
    """
    @Описание:
        Структура, содержащая географические координаты: географическую долготу, географическую широту и высоту над
            поверхностью Земли. Предусматривается возможность перевода кординат из географической системы координат в
            геоцентрическую прямоугольную экваториальную систему координат учетом формы Земли и времени

    @Аргументы:
        long - георграфическая долгота (градусы)
        lat - географическая широта (градусы)
        alt - высота над поверхностью Земли (м)

    @Поля:
        long - географическая долгота (градусы). При инициализации присваивается значение аргумента long
        lat - географическая широта (градусы). При инициализации присваивается значение аргумента lat
        alt - высота над поверхностью Земли (м). При инициализации присваивается значение аргумента alt
    """

    def __init__(self, long, lat, alt):
        self.long = long
        self.lat = lat
        self.alt = alt

    def __str__(self):
        """
        :return: ** с. ш.(ю. ш.)   ** з. д.(в. д.)  **** м
        """
        if self.long >= 0:
            long_str = str(self.long) + ' в. д.'
        else:
            long_str = str(abs(self.long)) + ' з. д.'

        if self.lat >= 0:
            lat_str = str(self.lat) + ' с. ш.'
        else:
            lat_str = str(abs(self.lat)) + ' ю. ш.'
        return lat_str + '\t' + long_str + '\t' + str(self.alt) + ' м'

    def to_cartesian_coordinates(self, utc_time, earth_ellipsoid):
        """
        Метод переводит кординаты из географической системы координат (self.long, self.lat, self.alt) в
            геоцентрическую прямоугольную экваториальную систему с учетом эллипсоида Земли ellipsoid и времени в формате
            UTC utc_time. Формула взята из лекций http://lnfm1.sai.msu.ru/grav/russian/lecture/tfe/node3.html
        :param utc_time: время в формате UTC, показывающее, как повернута Земля в данный момент. Если его значение None,
            то вращение Земли не учитывается
        :param earth_ellipsoid: эллипсоид Земли. Его форма учитывается при переводе
        :return: объект CartesianCoordinates - координаты (self.long, self.lat, self.alt), переведенные в географическую
            систему координат
        """
        # a - большая полуось данного эллипсоид (в плоскости экватора)
        a = earth_ellipsoid.semi_major_axis
        # b - малая полуось данного эллипсоид (вдоль оси z)
        b = earth_ellipsoid.semi_minor_axle
        # Проверка того, задано ли время
        if utc_time is not None:
            # Если время задано, то определяется угол поворота Земли в данный момент времени
            earth_turn = astronomy.gmst(utc_time)
        else:
            earth_turn = 0
        # Перевод долготы и широты из градусов в радианы и из подвижной системы в неподвижную
        long = numpy.deg2rad(self.long) + earth_turn
        lat = numpy.deg2rad(self.lat)
        alt = self.alt
        # p вычисляется для удобства вычислений
        p = a ** 2 / math.sqrt(a ** 2 * math.cos(lat) ** 2 + b ** 2 * math.sin(lat) ** 2)
        # Вычисление прямоугольных координат
        x = (p + alt) * math.cos(lat) * math.cos(long)
        y = (p + alt) * math.cos(lat) * math.sin(long)
        z = ((b ** 2 / a ** 2) * p + alt) * math.sin(lat)
        # Возвращает объет CartesianCoordinates с переведенными координатами
        return CartesianCoordinates(x, y, z)


class CartesianCoordinates:
    """
    @Описание:
        Структура, содержащая декартовые координаты в геоцентрической прямоугольной экваториальной системе координат.
            Предусматривается возможность перевода кординат из геоцентрической прямоугольной экваториальной системы в
            географическую с учетом формы Земли и времени

    @Аргументы:
        x - координата x в геоцентрической прямоугольной экваториальной системе координат (м)
        y - координата y в геоцентрической прямоугольной экваториальной системе координат (м)
        z - координата z в геоцентрической прямоугольной экваториальной системе координат (м)

    @Поля:
        x - координата x в геоцентрической прямоугольной экваториальной системе координат (м). При инициализации
            присваивается значение аргумента x
        y - координата y в геоцентрической прямоугольной экваториальной системе координат (м). При инициализации
            присваивается значение аргумента y
        z - координата z в геоцентрической прямоугольной экваториальной системе координат (м). При инициализации
            присваивается значение аргумента z

    @Методы:
        to_geo_coordinates(self, utc_time, earth_ellipsoid) - переводит кординаты из геоцентрической прямоугольной
            экваториальной системы, записаные в этом объекте, в географическую с учетом формы Земли и времени
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_geo_coordinates(self, utc_time, earth_ellipsoid):
        """
        Метод переводит кординаты из геоцентрической прямоугольной экваториальной системы (self.x, self.y, self.z) в
            географическую с учетом эллипсоида Земли earth_ellipsoid и времени в формате UTC utc_time. Формула взята из
            библиотеки pyorbital (https://github.com/pytroll/pyorbital/blob/master/pyorbital/orbital.py)
        :param utc_time: время в формате UTC, показывающее, как повернута Земля в данный момент. Если его значение None,
            то вращение Земли не учитывается
        :param earth_ellipsoid: эллипсоид Земли. Его форма учитывается при переводе
        :return: объект GeoCoordinates - координаты (self.x, self.y, self.z), переведенные в географическую систему
            координат
        """
        f = earth_ellipsoid.f
        a = earth_ellipsoid.semi_major_axis
        # Проверка того, задано ли время
        if utc_time is not None:
            # Если время задано, то определяется угол поворота Земли в данный момент времени
            earth_turn = astronomy.gmst(utc_time)
        else:
            earth_turn = 0
        # Вычисление долготы (в радианах) с учетом поворота Земли (в подвижной системе координат)
        long = ((numpy.arctan2(self.y, self.x) - earth_turn) % (2 * numpy.pi))
        # Проверка того, не выходит ли долгота за пределы диапазона (-pi, pi]
        long = numpy.where(long > math.pi, long - math.pi * 2, long)
        long = numpy.where(long <= -math.pi, long + math.pi * 2, long)
        # Расстояние до координат из начала отсчета в плоскости экватора
        r = math.sqrt(self.x ** 2 + self.y ** 2)
        # Вычисление широты в сферической системе
        lat = numpy.arctan2(self.z, r)
        # Вычисление эксцентриситета эллипсоида Земли в квадрате
        e2 = f * (2 - f)
        # Вычисление долготы (в радианах) в геодезической системе координат (нормальная проекция координаты на заданный
        #   эллипсоид) с точностью до 1e-10 км
        while True:
            lat_in_last_iter = lat
            sin_lat_in_last_iter = math.sin(lat_in_last_iter)
            c = 1 / (math.sqrt(1 - e2 * (sin_lat_in_last_iter ** 2)))
            lat = numpy.arctan2(self.z / a + c * e2 * sin_lat_in_last_iter, r / a)
            if numpy.all(abs(lat - lat_in_last_iter) < 1e-10):
                break
        # Вычисление наименьшенго расстояния до поверхности заданного эллипсоида Земли
        alt = r / math.cos(lat) - c * a
        # Возвращает объет GeoCoordinate с переведенными координатами, долгота и широта при этом переводится в градусы
        return GeoCoordinates(numpy.rad2deg(long), numpy.rad2deg(lat), alt)


class GeoCoordinatesAndPointSet:
    """
    @Описание:
        Структура, содержащая объект GeoCoordinates и объект shapely.geometry.Point

    @Аргументы:
        long - георграфическая долгота
        lat - географическая широта
        alt - высота над поверхностью Земли

    @Поля:
        geo_coordinates - содержит объект GeoCoordinates, который создаётся при инициализации с аргументами
            long, lat, alt
        point - содержит объект shapely.geometry.Point, который создаётся при инициализации с аргументами long, lat
    """
    def __init__(self, long, lat, alt):
        self.geo_coordinates = GeoCoordinates(long, lat, alt)
        self.point = Point(long, lat)
