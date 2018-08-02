from shapely.geometry import Point


class GeoCoordinates:
    """
    @Описание:
        Структура, содержащая географические координаты: географическую долготу, географическую широту и высоту над
            поверхностью Земли

    @Аргументы:
        long - георграфическая долгота
        lat - географическая широта
        alt - высота над поверхностью Земли в километрах

    @Поля:
        long - георграфическая долгота. При инициализации присваивается значение аргумента long
        lat - географическая широта. При инициализации присваивается значение аргумента lat
        alt - высота над поверхностью Земли. При инициализации присваивается значение аргумента alt
    """

    def __init__(self, long, lat, alt):
        self.long = long
        self.lat = lat
        self.alt = alt


class GeoCoordinatesAndPoint:
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
