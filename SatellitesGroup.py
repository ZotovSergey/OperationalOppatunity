import math
import Coordinates
import AnalyticGeometry
from pyorbital import astronomy, tlefile, orbital
from shapely import geometry


class SatellitesGroup:
    """
    @Описание:
        Класс SatelliteGroup моделирует работу группировки спутников ДЗЗ. Группировка состоит из одного или более
            спутников ДЗЗ, моделируемых объектами Satellite. Предусматривается возможность моделирования работы всех
            спутников группировки.

    @Аргументы:
        earth_ellipsoid - объект EarthEllipsoid, задающий эллипсоид Земли, на орбите которой находятся все спутники
            спутниковой группировки.

    @Поля:
        earth_ellipsoid - объект EarthEllipsoid, задающий эллипсоид Земли, на орбите которой находятся все спутники
            спутниковой группировки. Задается аргументом earth_ellipsoid при инициализации.
        satellites_list - список всех спутников, входящих в моделируемую группу (в виде объектов класса Satellite).
            При инициализации задается пустым списком, заполняется по одному при исполнении метода to_add_satellite.
        simulation_time - модельное время моделируемой спутниковой группировки. При инициализации - None. Значение
            задается методом объекта Task и обновляется при исполнении метода self.to_act.
        task - объект Task - задает задачу тематической обработки моделируемой группировке. При инициализации - None.
            Задается из вне методом объекта Task.

    @Методы:
        to_act(self, next_simulation_time) - моделирует работу спутниковой группировки, то есть всех спутников, входящих
            в нее, от текущего модельного времени группыдо времени, некоторого заданного времени. Возвращает площадь
            просканированных тестовых полигонов за время моделирования в кв. м. и список спутников, которые за время
            моделирования работы группировки производили съемку.
        to_add_satellite(self, sat_name, tle_address, angle_of_view) - создает объект Satellite и добавляет его в список
            спутникоа группировки, то есть добавляет новый спутник в группировку.
    """
    def __init__(self, earth_ellipsoid):
        self.earth_ellipsoid = earth_ellipsoid
        self.satellites_list = []
        self.simulation_time = None
        self.task = None

    def to_act(self, next_simulation_time):
        """
        Метод моделирует работу спутниковой группировки, то есть всех спутников, входящих в нее, от текущего модельного
            времени группы self.simulation_time до времени, заданного аргументом next_simulation_time. Возвращает
            площадь просканированных тестовых полигонов за время моделирования в кв. м. и список спутников, которые за
            время моделирования работы группировки производили съемку.
        :param next_simulation_time: время, до которого проходит моделирование. Следует использовать время не далекое от
            модельного, так как спутники моделируемой группировки между двумя координатами, сответствующих начальному и
            конечному времени моделирования, будет двигаться прямолинейно.
        :return: площадь просканированных тестовых полигонов за время моделирования (кв. м) всеми спутниками, входящих в
            моделируемую спутниковую группировку.
            Список спутников, которые за время моделирования работы группировки производили съемку.
        """
        full_scanned_area = 0
        scanning_satellites = []
        # Обход всех спутников группировки
        for satellite in self.satellites_list:
            # Моделирование работы спутников
            scanned_area = satellite.to_act(next_simulation_time)
            # Если площадь, просканированая спутником, больше нуля, то съемка производилась за время моделирования
            #   работы спутника этим спутником
            if scanned_area > 0:
                full_scanned_area += scanned_area
                scanning_satellites.append(satellite)
        # Обновление модельного времени
        self.simulation_time = next_simulation_time
        return full_scanned_area, scanning_satellites

    def to_add_satellite(self, sat_name, tle_address, angle_of_view):
        """
        Метод создает объект Satellite и добавляет его в список self.satellites_list, то есть добавляет новый спутник в
            группировку. Новый спутник задается названием sat_name  в системе NORAD, данными TLE по адрессу tle_address
            (если tle_address - None, то TLE для спутника с заданным названием загружается с celestrak.com), с углом
            обзора angle_of_view (в градусах).
        :param sat_name: название спутника в системе NORAD.
        :param tle_address: адресс данных TLE (допускается None).
        :param angle_of_view: угол обзора бортового гиперспектрометра создаваемого спутника.
        :return: добавляет спутник в список спутников группы self.satellites_list
        """
        self.satellites_list.append(Satellite(sat_name, tle_address, angle_of_view, self))


class Satellite:
    """
    @Описание:
        Класс Satellite моделирует работу спутника ДЗЗ. Предусматривается возможность двигаться по заданной орбите,
            вычислять полосу захвата, какая часть заданных тестовых полигонов попала в полосу захвата при соответствии
            внешних условий заданным.

    @Аргументы:
        sat_name - название спутника.
        tle_address - адресс текстового файла, содержащего данные TLE для спутниа с названием sat_name. Допустимо
            значение None
        angle_of_view - угол обзора гиперспектрометра, базирующегося на спутнике с названием sat_name (градусы).
        satellites_group - объект SatelliteGroup - группа спутников, в который входит моделируемый спутник.
            Предполагается, что создаваемый объект Satellite инициируется методом именно этого объекта.

    @Поля:
        sat_name - название спутника. Название должно совпадать с названием спутниа в системе NORAD. Присваивается
            значение аргумента sat_name при инициализации.
        orbit - объект Orbital, с помощью которого вычисляется положение моделируемого спутника на орбите Земли,
            заданной данными TLE, расположенных по адрессу из аргумента tle_address для спутника под названием sat_name
            в системе NORAD. Если значение аргумента sat_name - None, то данные TLE загружаются с веб-сайта
            celestrak.com для спутника под названием из аргумента sat_name. Если аргумент sat_name не задан или задан
            неправильно, то определение объекта Orbital невозможно. Создается при инициализации.
        satellite_coordinate_set - объект SatelliteCoordinateSet, содержащий важнейшие координаты моделируемого
            спутника. При инициалиции - None. Обновляется методом to_move_to_time.
        angle_of_view - угол обзора гиперспектрометра, базирующегося на моделируемом спутнике. Задается аргументом
            angle_of_view при инициализации (градусы).
        satellites_group - объект SatelliteGroup, обозначающий спутниковую группировку, в которую входит моделируемый
            спутник. Задается аргументом satellite_group при инициализации.
        scanned_territory_for_last_step - объект shapely.geometry.Polygon, представляет из себя прямоугольник с
            врешинами, заданными географическими координатами в градусах.
        close_polygons - список полигонов (объектов Polygon) находящихся достаточно близко к моделируемому спутнику,
            чтобы акая-либо его чатсь могла попасть в полосу захвата моделируемого спутника. при инициализации - пустой
            список, заполняется при использовании метода to_determine_close_polygon

    @Методы:
        to_act(self, next_simulation_time) - моделирует работу спутника от текущего модельного времени спутниковой
            группы до времени, заданного аргументом. Возвращает площадь просканированных тестовых полигонов за время
            моделирования.
        to_move_to_time(self, next_time) - определяет координаты спутника в заданное время и присваивает их значения
            моделируемому спутнику.
        to_determine_scan_area(self, previous_coordinate, current_coordinate) - вычисление точки пересечения эллипсоида
            Земли и прямой повернутой вокруг оси движения спутника (касательной к поверхности Земли в подспутниковой
            точке) с заданными координатами (параллельной Земле) на заданный угол.
        to_calculate_geo_coordinates_of_ground_point_in_field_of_view(self, satellite_coordinates_set,
                                                                      angle_of_rotation) - вычисляет точку пересечения
            эллипсоида Земли и прямой повернутой вокруг оси движения спутника (проекция вектора скорости спутника на
            касательную плоскость к поверхности Земли в подспутниковой точке) с координатами спутника на заданный угол.
        to_determine_close_polygons(self) - определяет, какие полигоны из заданных, то есть тех, которые должны быть
            просканированны для решения задачи, находятся достаточно близко к моделируемому спутнику, чтобы части их
            территории могли попасть в полосу захвата моделируемого спутника.
        to_scan(self) - моделирует процесс съемки близких тестовых полигонов за некоторое время. Производится проверка
            того, попадают ли сегменты близких полигонов в полосу захвата за некоторое время, допустимый ли в момент
            съемки зенитный угол Солнца, моделирует облачность или для всех полигонов, или для каждого отдельно, задает
            случайную облачность для каждого сегмента и проверяет, допустима ли облачность над полигоном для съемки
            и не закрыт ли сегмент облаками. Если все эти условия соблюдены, то сегмент считается просканированным и его
            площадь прибавляется к сумме, подаваемой на выход метода.
    """
    def __init__(self, sat_name, tle_address, angle_of_view, satellites_group):
        self.sat_name = sat_name
        # Извлечение данных TLE из файла по адресу tle_address или загрузка с celestrak.com для спутника sat_name, если
        #   tle_address is None
        tle = tlefile.read(sat_name, tle_address)
        # Создание объекта Orbital из пакета pyorbital
        self.orbit = orbital.Orbital(self.sat_name, line1=tle.line1, line2=tle.line2)
        self.satellite_coordinates_set = None
        self.angle_of_view = angle_of_view
        self.satellites_group = satellites_group
        self.scanned_territory_for_last_step = None
        self.close_polygons = []

    def to_act(self, next_simulation_time):
        """
        Метод моделирует работу спутника от текущего модельного времени группы (self.satellite_group.simulation_time) до
            времени, заданного аргументом next_simulation_time. В процесс моделирования входит моделиросвание движения
                моделируемого спутника, его полосы захвата, процесса съемки. Возвращает площадь просканированных
                тестовых полигонов за время моделирования в кв. м.
        :param next_simulation_time: время, до которого проходит моделирование. Следует использовать время не далекое от
            модельного, так как спутник между двумя координатами, сответствующих начальному и конечному времени
            моделирования, будет двигаться прямолинейно.
        :return: площадь просканированных тестовых полигонов за время моделирования (кв. м).
        """
        # Сохранение координат моделируемого спутника в начальное время моделирования
        current_coordinates_set = self.satellite_coordinates_set
        # Моделирование движения спутника
        self.to_move_to_time(next_simulation_time)
        # Моделироване полосы захвата (по прямой линии между точками на орбите)
        self.to_determine_scan_area(current_coordinates_set, self.satellite_coordinates_set)
        # Определение полигонов достаточно близких моделируемому спутнику, чтобы быть просканированными
        self.to_determine_close_polygons()
        # Проверка, есть ли вблизи тестовые полигоны
        if self.close_polygons:
            # Если да, то моделируется сканирование близких полигонов и возвращается площадь
            return self.to_scan()
        else:
            # Если нет, то возвращается 0
            return 0

    def to_move_to_time(self, next_time):
        """
        Метод определяет координаты спутника во время next_time и присваивает их значения моделируемому спутнику.
        :param next_time: время в формате UTC в которое определяются координаты моделируемого спутника.
        :return: координаты в объекте класса SatelliteCoordinatesSet записываются в self.satellite_coordinates_set
        """
        (pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z) = self.orbit.get_position(next_time, normalize=False)
        self.satellite_coordinates_set = SatelliteCoordinateSet(Coordinates.CartesianCoordinates(pos_x, pos_y, pos_z),
                                                                AnalyticGeometry.Vector(vel_x, vel_y, vel_z),
                                                                self.satellites_group.simulation_time,
                                                                self.satellites_group.earth_ellipsoid)

    def to_determine_scan_area(self, previous_coordinate, current_coordinate):
        """
        Определяет полосу захвата моделируемого спутника при прямолинейном движении спутника между точками с
            координатами previous_coordinate и current_coordinate. Результат записывается в поле
            self.scanned_territory_for_last_step в виде объекта shapely.geometry.Polygon.
        :param previous_coordinate: координаты моделируемого спутника в начальной точке (SatelliteCoordinatesSet).
        :param current_coordinate: координаты моделируемого спутника в конечной точке (SatelliteCoordinatesSet).
        :return: полоса захвата записывается в поле self.scanned_territory_for_last_step в виде объекта
        shapely.geometry.Polygon.
        """
        # Определение углов прямоугольной полосы захвата с помощью метода
        #   self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view
        vertices = [self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(current_coordinate,
                                                                                       self.angle_of_view),
                    self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(current_coordinate,
                                                                                       -self.angle_of_view),
                    self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(previous_coordinate,
                                                                                       -self.angle_of_view),
                    self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(previous_coordinate,
                                                                                       self.angle_of_view)]
        self.scanned_territory_for_last_step = geometry.Polygon(vertices)

    def to_calculate_geo_coordinates_of_ground_point_in_field_of_view(self, satellite_coordinates_set,
                                                                      angle_of_rotation):
        """
        Вычисление точки пересечения эллипсоида Земли и прямой повернутой вокруг оси движения спутника (проекция вектора
            скорости спутника на касательную плоскость к поверхности Земли в подспутниковой точке) с координатами
            satellite_coordinates_set на угол angle_of_rotation.
        :param satellite_coordinates_set: координаты SatelliteCoordinatesSet спутника.
        :param angle_of_rotation: угол поворота вокруг оси.
        :return: географические координаты искомой точки в объекте shapely.geometry.Point.
        """
        # Декартовые координаты спутника в экватериальной системе координат
        sat_x = satellite_coordinates_set.cartesian_coordinates.x
        sat_y = satellite_coordinates_set.cartesian_coordinates.y
        sat_z = satellite_coordinates_set.cartesian_coordinates.z
        # Вычисление вектора, указывающего направление надира для спутника
        vector_to_ground_x = satellite_coordinates_set.subsatellite_cartesian_coordinates.x - sat_x
        vector_to_ground_y = satellite_coordinates_set.subsatellite_cartesian_coordinates.y - sat_y
        vector_to_ground_z = satellite_coordinates_set.subsatellite_cartesian_coordinates.z - sat_z
        vector_to_subsatellite_point = AnalyticGeometry.Vector(vector_to_ground_x,
                                                               vector_to_ground_y,
                                                               vector_to_ground_z)
        # Создание объекта AnalyticGeometry.CanonicalEllipsoid по заданному эллипсоиду Земли
        a = self.satellites_group.earth_ellipsoid.semi_major_axis
        c = self.satellites_group.earth_ellipsoid.semi_minor_axis
        ellipsoid_obj = AnalyticGeometry.CanonicalEllipsoid(a, a, c)
        # Вычисления касательной к поверхности Земли (vector_of_movement) через проектирования вектора скорости спутника
        #    на плоскость касающуюся Земли в подспутниковой точке
        flat_earth_plane = AnalyticGeometry.plane_touched_canonical_ellipsoid(vector_to_subsatellite_point,
                                                                              ellipsoid_obj)
        scalar_product_of_line_and_plane_normal = vector_to_subsatellite_point.scalar_product(flat_earth_plane.normal)
        if scalar_product_of_line_and_plane_normal != 0:
            line_to_earth = AnalyticGeometry.Line(AnalyticGeometry.Vector(sat_x, sat_y, sat_z),
                                                  vector_to_subsatellite_point)
            vector_of_movement = AnalyticGeometry.projection_of_line_on_plane(line_to_earth, flat_earth_plane).\
                directing_vector
        else:
            vector_of_movement = satellite_coordinates_set.velocity_vector
        # Вычисление вектора к искомой точке
        vector_to_search_point = vector_to_subsatellite_point.to_rotate_vector(vector_of_movement, angle_of_rotation)
        # Вычисление искомой точки (точки пересечения)
        line_to_search_point = AnalyticGeometry.Line(AnalyticGeometry.Vector(sat_x, sat_y, sat_z),
                                                     vector_to_search_point)
        search_point = AnalyticGeometry.\
            to_found_point_of_intersection_of_line_and_canonical_ellipsoid_nearest_to_stating_point_of_line(
                line_to_search_point, ellipsoid_obj)
        geo_coordinates_of_search_point = Coordinates.CartesianCoordinates(search_point.x,
                                                                           search_point.y,
                                                                           search_point.z).\
            to_geo_coordinates(self.satellites_group.simulation_time, self.satellites_group.earth_ellipsoid)
        return geometry.Point(geo_coordinates_of_search_point.long, geo_coordinates_of_search_point.lat)

    def to_determine_close_polygons(self):
        """
        Метод определяет, какие полигоны из заданных, то есть тех, которые должны быть просканированны для решения
            задачи (определенных в объекте класса Task, записанных в списке self.satellites_group.task.polygons_group),
            находятся достаточно близко к моделируемому спутнику, чтобы части их территории могли попасть в полосу
            захвата моделируемого спутника.
        :return: близкие полигоны записываются в спикок self.close_polygons.
        """
        # Очистка списка
        self.close_polygons = []
        # Обход всех заданных полигонов, проверка на "близость" к моделируемому спутнику
        for polygon in self.satellites_group.task.polygons_group:
            # Вычисление расстояния от подспутниковой точки до центра полигона и сравнение с суммой расстояния от
            #   подспутниковой точки до края полосы захвата с радиусом выбранного полигона, умноженная на 110% (критерий
            #   близости)
            if self.satellites_group.earth_ellipsoid.dist_between_geo_coordinates(
                    polygon.center, self.satellite_coordinates_set.geo_coordinates) < 1.1 * \
                    (polygon.radius + self.satellite_coordinates_set.geo_coordinates.alt *
                     math.tan(self.angle_of_view)):
                self.close_polygons.append(polygon)

    def to_scan(self):
        """
        Метод моделирует процесс съемки близких тестовых полигонов (записанных в self.close_polygons) за некоторое
            время. Производится проверка того, попадают ли сегменты близких полигонов (объекты из списка segments_list
            объекта Polygon) в полосу захвата за некоторое время self.scanned_territory_for_last_step, допустимый ли в
            момент съемки self.satellites_group.simulation_time зенитный угол Солнца (меньше
            self.satellites_group.task.max_zenith_angle), моделирует облачность или для всех полигонов, или для каждого
            отдельно, задает случайную облачность для каждого сегмента и проверяет, допустима ли облачность над
            полигоном для съемки (меньше self.satellites_group.task.max_cloud_score) и не закрыт ли сегмент облаками.
            Если все эти условия соблюденыЮ, то сегмент считается просканированным и его площадь прибавляется к сумме,
            подаваемой на выход метода.
        :return: площадь просканированной территории (кв. м)
        """
        # Вычисление случайной облачности либо для всех близких полинов сразу, либо отдельно
        if self.satellites_group.task.common_cloudiness_boolean:
            common_cloudiness = self.close_polygons[0].own_group.to_randomize_common_cloudiness(
                self.satellites_group.simulation_time)
            for polygon in self.close_polygons:
                polygon.current_cloudiness_in_score = common_cloudiness
        else:
            for polygon in self.close_polygons:
                polygon.to_randomize_cloudiness_to_polygon(self.satellites_group.simulation_time)

        scanned_area = 0
        # Обход всех близких полигонов
        for polygon in self.close_polygons:
            # Проверка, допустима ли облачность для съемки
            if polygon.current_cloudiness_in_score <= self.satellites_group.task.max_cloud_score:
                # Обход всех сегментов полигона
                for segment in polygon.segments_list:
                    # Проверка всех условий для съемки
                    if (self.scanned_territory_for_last_step.contains(segment.center_geo_coordinates.point)) and\
                            (astronomy.sun_zenith_angle(self.satellites_group.simulation_time,
                                                        self.satellite_coordinates_set.geo_coordinates.long,
                                                        self.satellite_coordinates_set.geo_coordinates.lat)
                             <= self.satellites_group.task.max_zenith_angle) and (polygon.segment_is_hidden()):
                        # Сегмент считается, как просканированный еще один раз
                        segment.segment_grabbed()
                        # Площадь сегмента суммируется с общей суммой
                        scanned_area += segment.segments_area
        return scanned_area


class SatelliteCoordinateSet:
    """
    @Описание:
        Класс содержит основные координаты некоторого спутника: координаты спутника в прямоугольной экватериальной
            системе координат и в географической системе координат, вектор скорости в прямоугольной экватериальной
            системе координат, время в формате UTC, координаты подспутниковой точки в прямоугольной экватериальной
            системе координат и в географической системе координат.

    @Аргументы:
        cartesian_coordinates - декартовые координаты спутника в прямоугольной экватериальной системе координат в
            объекте Coordinates.CartesianCoordinates.
        velocity_vector - вектор скорости в прямоугольной экватериальной системе координат в объекте
            AnalyticGeometry.Vector в м/с.
        utc_time - время в формате UTC, в котором находится спутник (datetime.datetime).
        earth_ellipsoid - объект EarthEllipsoid, моделирующий эллипсоид Земли, по орбите которой движется спутник.

    @Поля:
        cartesian_coordinates - декартовые координаты спутника в прямоугольной экватериальной системе координат (объект
            Coordinates.CartesianCoordinates). Задается аргументом cartesian_coordinates при инициализации.
        geo_coordinates - координаты спутника в географической системе координат. Вычисляется по аргументу
            cartesian_coordinates при инициализации.
        velocity_vector - вектор скорости в прямоугольной экватериальной системе координат. Задается аргументом
            velocity_vector.
        utc_time - время в формате UTC, в котором находится спутник. Задается аргументом utc_time.
        subsatellite_geo_coordinates - координаты подспутниковой точки в географической системе координат. Вычисляется
            при инициализации по полю geo_coordinates.
        subsatellite_cartesian_coordinates - координаты подспутниковой точки в прямоугольной экватериальной системе
            координат. Вычисляется при инициализации по полю subsatellite_geo_coordinates.

    """
    def __init__(self, cartesian_coordinates, velocity_vector, utc_time, earth_ellipsoid):
        self.cartesian_coordinates = cartesian_coordinates
        # Вычисление координат спутника в географической системе координат путем перевода координат
        #   cartesian_coordinates из прямоугольной экватериальной системы координат в географическую
        self.geo_coordinates = cartesian_coordinates.to_geo_coordinates(utc_time, earth_ellipsoid)
        self.velocity_vector = velocity_vector
        self.utc_time = utc_time
        # Вычисление координат подспутниковой точки в географической системе координат путем обнуления высоты для поля
        #   self.geo_coordinates
        self.subsatellite_geo_coordinates = Coordinates.GeoCoordinates(self.geo_coordinates.long,
                                                                       self.geo_coordinates.lat, 0)
        # Вычисление координат подспутниковой точки в прямоугольной экватериальной системе координат путем перевода
        #   координат self.subsatellite_geo_coordinates из географической системы координат в прямоугольную
        #   экватериальную
        self.subsatellite_cartesian_coordinates = self.subsatellite_geo_coordinates.\
            to_cartesian_coordinates(utc_time, earth_ellipsoid)

    def __str__(self):
        """
        :return: ** с. ш.(ю. ш.)   ** з. д.(в. д.)  **** м  **** м/с
        """
        return str(self.geo_coordinates) + '\t' + str(len(self.velocity_vector)) + ' м/с'
