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
        canon_ellipsoid - объект CanonicalEllipsoid из библиотеки AnalyticGeometry. Имеет те же большую и малую полуоси,
            что и earth_ellipsoid. С его помощью проводятся вычисления методами из AnalyticGeometry.
        satellites_list - список всех спутников, входящих в моделируемую группу (в виде объектов класса Satellite).
            При инициализации задается пустым списком, заполняется по одному при исполнении метода to_add_satellite.
        simulation_time - модельное время моделируемой спутниковой группировки. При инициализации - None. Значение
            задается методом объекта Task и обновляется при исполнении метода self.to_act.
        task - объект Task - задает задачу тематической обработки моделируемой группировке. При инициализации - None.
            Задается из вне методом объекта Task.
        time_of_scanning - время в секундах, которое дляится сканирование каким-либо спутником подряд (int, double).
            Должно вестись, чтобы не допускать одинаковой облачности слишком долгое время, чтобы сравнивать с
            self.polygons_group.TIME_OF_CLOUDINESS_CHANGING. По умолчанию 0. Обновляется привыполнении метода
            self.to_scan.

    @Методы:
        to_act(self, next_simulation_time) - моделирует работу спутниковой группировки, то есть всех спутников, входящих
            в нее, от текущего модельного времени группыдо времени, некоторого заданного времени. Возвращает площадь
            просканированных тестовых полигонов за время моделирования в кв. м. и список спутников, которые за время
            моделирования работы группировки производили съемку.
        to_add_satellite(self, sat_name, tle_address, angle_of_view) - создает объект Satellite и добавляет его в список
            спутникоа группировки, то есть добавляет новый спутник в группировку.
    """
    # Ускорение работы объектов класса
    #import pyximport; pyximport.install()

    def __init__(self, earth_ellipsoid):
        self.earth_ellipsoid = earth_ellipsoid
        a = earth_ellipsoid.semi_major_axis
        c = earth_ellipsoid.semi_minor_axis
        self.canon_ellipsoid = AnalyticGeometry.CanonicalEllipsoid(a, a, c)
        self.satellites_list = []
        self.simulation_time = None
        self.task = None
        self.time_of_scanning = 0

    def to_act(self, next_simulation_time):
        """
        @Описание:
            Метод моделирует работу спутниковой группировки, то есть всех спутников, входящих в нее, от текущего
                модельного времени группы self.simulation_time до времени, заданного аргументом next_simulation_time.
                Возвращает площадь просканированных тестовых полигонов за время моделирования в кв. м. и список
                спутников, которые за время моделирования работы группировки производили съемку.
        :param next_simulation_time: время, до которого проходит моделирование. Следует использовать время не далекое от
            модельного, так как спутники моделируемой группировки между двумя координатами, сответствующих начальному и
            конечному времени моделирования, будет двигаться прямолинейно.
        :return: площадь просканированных тестовых полигонов за время моделирования (кв. м) всеми спутниками, входящих в
            моделируемую спутниковую группировку.
            Список спутников, которые за время моделирования работы группировки производили съемку.
        """
        common_scanned_area = 0
        close_polygons_are_exist = False
        # Обход всех спутников группировки
        for satellite in self.satellites_list:
            # Сохранение координат выбранного спутника в текущее время моделирования
            current_coordinates_set = satellite.satellite_coordinates_set
            # Моделирование движения спутника до времени next_simulation_time
            satellite.to_move_to_time(next_simulation_time)
            next_coordinates_set = satellite.satellite_coordinates_set
            # Определение полигонов достаточно близких моделируемому спутнику, чтобы быть просканированными
            satellite.to_determine_close_polygons()
            if len(satellite.close_polygons) > 0:
                close_polygons_are_exist = True
                #   Моделирование полосы захвата (по прямой линии между точками на орбите)
                satellite.to_determine_scan_area(current_coordinates_set, next_coordinates_set)
        # Если есть полигоны, близкие к спутникам из группы
        if close_polygons_are_exist:
            # Если сканирование только начинается
            if self.time_of_scanning == 0:
                # Задается облачность
                self.task.polygons_group.to_calculate_cloudiness_above_group(self.simulation_time)
                # Если погода не меняется не слишком долго
                # Вычисляется шаг времени сканирования и прибавляется времени сеанса
                self.time_of_scanning += (next_simulation_time - self.simulation_time).total_seconds()
            else:
                if self.time_of_scanning < self.task.polygons_group.TIME_OF_CLOUDINESS_CHANGING:
                    # Вычисляется шаг времени сканирования и прибавляется времени сеанса
                    self.time_of_scanning += (next_simulation_time - self.simulation_time).total_seconds()
                # Если погода не меняется слишком долго, то время сеанса обнуляется, чтобы поменялась и облачность на
                #   следующей итерации
                else:
                    self.time_of_scanning = 0
            # Обход всех спутников группировки
            for satellite in self.satellites_list:
                # Проверка, есть ли вблизи тестовые полигоны
                if len(satellite.close_polygons) > 0:
                    # Если да, то
                    #   Моделируется сканирование близких полигонов и прибовляет их просканированную площадь к общей
                    #       просканированной площади группы
                    common_scanned_area += satellite.to_scan()
        # Если сканирование закончилось, то обнуляется время сеанса
        else:
            # Если нет то
            #   очищается поле просканированной территории для каждого спутника
            for satellite in self.satellites_list:
                if len(satellite.scanned_territory_for_last_step) > 0:
                    satellite.scanned_territory_for_last_step = []
            #   возвращается 0
            if self.time_of_scanning > 0:
                self.time_of_scanning = 0

        # Обновление модельного времени для группы
        self.simulation_time = next_simulation_time
        return common_scanned_area

    def to_add_satellite(self, sat_name, tle_address, angle_of_view):
        """
        @Описание:
            Метод создает объект Satellite и добавляет его в список self.satellites_list, то есть добавляет новый
                спутник в группировку. Новый спутник задается названием sat_name  в системе NORAD, данными TLE по
                адрессу tle_address (если tle_address - None, то TLE для спутника с заданным названием загружается с
                celestrak.com), с углом обзора angle_of_view (в градусах).
        :param sat_name: название спутника в системе NORAD.
        :param tle_address: адресс данных TLE (допускается None).
        :param angle_of_view: угол обзора бортового гиперспектрометра создаваемого спутника.
        :return: добавляет спутник в список спутников группы self.satellites_list
        """
        self.satellites_list.append(Satellite(sat_name, tle_address, angle_of_view, self))

    def to_set_simulation_time(self, simulation_time):
        """
        @Описание:
            Устанавливает модельное время для данной спутниковой группировки и вычисляет координаты в это модельное
                время для каждого спутника в этой группировки
        :param simulation_time: устанавливаемое модельное время (datetime)
        :return: записывает время simulation_time в поле self.simulation_time и вычисляет для поля
                 satellite_coordinates_set для каждого спутника из self.satellites_list вычисляет координаты в модельное
                 время simulation_time
        """
        # Установка модельного времени
        self.simulation_time = simulation_time
        # Вычисление координат каждого спутника в модельное время simulation_time
        for satellite in self.satellites_list:
            (pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z) = satellite.orbit.get_position(simulation_time,
                                                                                        normalize=False)
            satellite.satellite_coordinates_set = SatelliteCoordinateSet(Coordinates.CartesianCoordinates
                                                                         (pos_x, pos_y, pos_z),
                                                                         AnalyticGeometry.Vector(vel_x, vel_y, vel_z),
                                                                         simulation_time,
                                                                         self.earth_ellipsoid)

    def __str__(self):
        """
        :return: список названий NORAD спутников в группе в виде:
        "Название в системе NORAD первого спутника в списке"
        "Название в системе NORAD второго спутника в списке"
        "Название в системе NORAD третьего спутника в списке"
        ...
        """
        str_satellite_group = []
        for satellite in self.satellites_list:
            str_satellite_group.append("".join([str(satellite), '\n']))
        return "".join(str_satellite_group)


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
        angle_of_view - половина угла обзора гиперспектрометра в радианах, базирующегося на моделируемом спутнике.
            Задается аргументом angle_of_view разделенным пополам при инициализации в градусах и переводится в радианы
            (радианы).
        satellites_group - объект SatelliteGroup, обозначающий спутниковую группировку, в которую входит моделируемый
            спутник. Задается аргументом satellite_group при инициализации.
        scanned_territory_for_last_step - список географических координат (GeoCoordinates) - вершины прямоугольника -
            часть полосы захвата, просканированные за последний шаг модельного времени. По умолчанию - пустой список.
            Определяется методом to_determine_close_polygons(self) и может очищаться методом to_act.
        close_polygons - список полигонов, достаточно близких к моделируемому спутнику, чтобы был шанс быть
            просканированными. По умолчанию - пустой список. Задаются методом to_determine_close_polygons.

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
        to_scan(self, polygons_to_scan) - моделирует процесс съемки заданных тестовых полигонов за некоторое время.
            Производится проверка того, попадают ли сегменты близких полигонов в полосу захвата за некоторое время,
            допустимый ли в момент съемки зенитный угол Солнца, моделирует облачность или для всех полигонов, или для
            каждого отдельно, задает случайную облачность для каждого сегмента и проверяет, допустима ли облачность над
            полигоном для съемки и не закрыт ли сегмент облаками. Если все эти условия соблюдены, то сегмент считается
            просканированным и его площадь прибавляется к сумме, подаваемой на выход метода.
    """
    # Ускорение работы объектов класса
    #import pyximport; pyximport.install()

    def __init__(self, sat_name, tle_address, angle_of_view, satellites_group):
        self.sat_name = sat_name
        # Извлечение данных TLE из файла по адресу tle_address или загрузка с celestrak.com для спутника sat_name, если
        #   tle_address is None
        tle = tlefile.read(sat_name, tle_address)
        # Создание объекта Orbital из пакета pyorbital
        self.orbit = orbital.Orbital(self.sat_name, line1=tle.line1, line2=tle.line2)
        self.satellite_coordinates_set = None
        # Перевод в радианы
        self.half_angle_of_view = math.pi * angle_of_view / 360
        self.satellites_group = satellites_group
        self.scanned_territory_for_last_step = []
        self.close_polygons = []

    def to_act(self, next_simulation_time):
        """
        @Описание:
            Метод моделирует работу спутника от текущего модельного времени группы
                (self.satellite_group.simulation_time) до времени, заданного аргументом next_simulation_time. В процесс
                моделирования входит моделиросвание движения моделируемого спутника, его полосы захвата, процесса
                съемки. Возвращает площадь просканированных тестовых полигонов за время моделирования в кв. м.
        :param next_simulation_time: время, до которого проходит моделирование. Следует использовать время не далекое от
            модельного, так как спутник между двумя координатами, сответствующих начальному и конечному времени
            моделирования, будет двигаться прямолинейно.
        :return: площадь просканированных тестовых полигонов за время моделирования (кв. м).
        """
        # Сохранение координат моделируемого спутника в начальное время моделирования
        current_coordinates_set = self.satellite_coordinates_set
        # Моделирование движения спутника
        self.to_move_to_time(next_simulation_time)
        next_coordinates_set = self.satellite_coordinates_set
        # Определение полигонов достаточно близких моделируемому спутнику, чтобы быть просканированными
        self.to_determine_close_polygons()
        # Проверка, есть ли вблизи тестовые полигоны
        if len(self.close_polygons) > 0:
            # Если да, то
            #   Моделирование полосы захвата (по прямой линии между точками на орбите)
            self.to_determine_scan_area(current_coordinates_set, next_coordinates_set)
            #   Моделируется сканирование близких полигонов и возвращается площадь
            return self.to_scan()
        else:
            # Если нет то
            #   очищается поле просканированной территории
            if len(self.scanned_territory_for_last_step) > 0:
                self.scanned_territory_for_last_step = []
            #   возвращается 0
            return 0

    def to_move_to_time(self, next_time):
        """
        @Описание:
            Метод определяет координаты спутника во время next_time и присваивает их значения моделируемому спутнику.
        :param next_time: время в формате UTC в которое определяются координаты моделируемого спутника.
        :return: координаты в объекте класса SatelliteCoordinatesSet записываются в self.satellite_coordinates_set
        """
        (pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z) = self.orbit.get_position(next_time, normalize=False)
        self.satellite_coordinates_set = SatelliteCoordinateSet(Coordinates.CartesianCoordinates(pos_x, pos_y, pos_z),
                                                                AnalyticGeometry.Vector(vel_x, vel_y, vel_z),
                                                                next_time,
                                                                self.satellites_group.earth_ellipsoid)

    def to_determine_scan_area(self, current_coordinates, next_coordinates):
        """
        @Описание:
            Определяет полосу захвата моделируемого спутника при прямолинейном движении спутника между точками с
                координатами current_coordinates и next_coordinates. Результат записывается в поле
                self.scanned_territory_for_last_step в виде списка геосоординат (GeoCoordinates).
        :param current_coordinates: координаты моделируемого спутника в начальной точке (SatelliteCoordinatesSet).
        :param next_coordinates: координаты моделируемого спутника в конечной точке (SatelliteCoordinatesSet).
        :return: полоса захвата записывается в поле self.scanned_territory_for_last_step в виде объекта
        shapely.geometry.Polygon.
        """
        # Если на прошлом шагу не было сканирования
        if len(self.scanned_territory_for_last_step) == 0:
            # Вычисление вектора-надира для спутника с координатами current_coordinate
            #   Декартовые координаты спутника в экватериальной системе координат
            current_sat_x = current_coordinates.cartesian_coordinates.x
            current_sat_y = current_coordinates.cartesian_coordinates.y
            current_sat_z = current_coordinates.cartesian_coordinates.z
            # Радиус-вектор спутника
            current_sat_coordinates_vector = AnalyticGeometry.Vector(current_sat_x, current_sat_y, current_sat_z)
            #   Вычисление вектора, указывающего направление надира для спутника
            current_vector_to_ground_x = current_coordinates.subsatellite_cartesian_coordinates.x - current_sat_x
            current_vector_to_ground_y = current_coordinates.subsatellite_cartesian_coordinates.y - current_sat_y
            current_vector_to_ground_z = current_coordinates.subsatellite_cartesian_coordinates.z - current_sat_z
            current_nadir_vector = AnalyticGeometry.Vector(current_vector_to_ground_x,
                                                           current_vector_to_ground_y,
                                                           current_vector_to_ground_z)
            # Вычисление границ полосы захвата для текущего положения спутника
            left_current_swath_border = self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(
                current_sat_coordinates_vector, current_coordinates.velocity_vector, current_nadir_vector,
                self.half_angle_of_view)
            right_current_swath_border = self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(
                current_sat_coordinates_vector, current_coordinates.velocity_vector, current_nadir_vector,
                -self.half_angle_of_view)
        # Если было
        else:
            # Текущими границами полосы захвата становятся следующие границы на предыдущем шаге
            left_current_swath_border = self.scanned_territory_for_last_step[3]
            right_current_swath_border = self.scanned_territory_for_last_step[2]

        # Вычисление вектора-надира для спутника с координатами next_coordinates
        #   Декартовые координаты спутника в экватериальной системе координат
        next_sat_x = next_coordinates.cartesian_coordinates.x
        next_sat_y = next_coordinates.cartesian_coordinates.y
        next_sat_z = next_coordinates.cartesian_coordinates.z
        # Радиус-вектор спутника
        next_sat_coordinates_vector = AnalyticGeometry.Vector(next_sat_x, next_sat_y, next_sat_z)
        #   Вычисление вектора, указывающего направление надира для спутника
        next_vector_to_ground_x = next_coordinates.subsatellite_cartesian_coordinates.x - next_sat_x
        next_vector_to_ground_y = next_coordinates.subsatellite_cartesian_coordinates.y - next_sat_y
        next_vector_to_ground_z = next_coordinates.subsatellite_cartesian_coordinates.z - next_sat_z
        next_nadir_vector = AnalyticGeometry.Vector(next_vector_to_ground_x,
                                                    next_vector_to_ground_y,
                                                    next_vector_to_ground_z)
        # Вычисление границ полосы захвата для следующего положения спутника
        right_next_swath_border = self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(
            next_sat_coordinates_vector, next_coordinates.velocity_vector, next_nadir_vector, -self.half_angle_of_view)
        left_next_swath_border = self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view(
            next_sat_coordinates_vector, next_coordinates.velocity_vector, next_nadir_vector, self.half_angle_of_view)
        # Определение углов прямоугольной полосы захвата с помощью метода
        #   self.to_calculate_geo_coordinates_of_ground_point_in_field_of_view
        vertices = [left_current_swath_border, right_current_swath_border, right_next_swath_border,
                    left_next_swath_border]
        self.scanned_territory_for_last_step = vertices

    def to_calculate_geo_coordinates_of_ground_point_in_field_of_view(self, sat_vector, velocity_vector, nadir_vector,
                                                                      angle_of_rotation):
        """

        @Описание:
            Вычисление координаты точки на Земле, в которую направлен вектор повернутый от надира спутника в сторону от
            его движения параллельно эллипсоиду Земли на заданный угол.
        :param sat_vector: координаты спутника (Coordinates.CartesianCoordinates)
        :param velocity_vector: вектор скорости спутника (AnalyticGeometry.Vector)
        :param nadir_vector: вектор-надир для спутника (Vector)
        :param angle_of_rotation: угол поворота в градусах (int, double)
        :return: Широту и долготу искомой точки (int, double) (в скобках для того, чтобы записать в объект Polygon)
        """
        # Вычисление координат вектора - оси вращения, вокруг которой будет вращаться вектор-надир, чтобы найти вектор
        #   движения спутника параллельно плоскости эллипсоида Земли
        rot_axis = nadir_vector * velocity_vector
        # Вычисление координат вектора с помощью вращения движения спутника параллельно плоскости эллипсоида Земли
        parallel_mov_vector = nadir_vector.to_rotate_vector(rot_axis, 90)
        # Вычисление вектора, направленного в искомую точку с помощью вращения
        vector_to_searched_point = nadir_vector.to_rotate_vector(parallel_mov_vector, angle_of_rotation)
        # Вычисление координат искомой точки по пересечения vector_to_searched_point и
        #   self.satellites_group.canon_ellipsoid
        searched_point = AnalyticGeometry. \
            to_found_point_of_intersection_of_line_and_canonical_ellipsoid_nearest_to_stating_point_of_line(
                AnalyticGeometry.Line(sat_vector, vector_to_searched_point), self.satellites_group.canon_ellipsoid)
        # Перевод декартовых  координат в географческие и вывод в виде объекта geometry.Point
        geo_coordinates_of_search_point = Coordinates.CartesianCoordinates(searched_point.x,
                                                                           searched_point.y,
                                                                           searched_point.z). \
            to_geo_coordinates(self.satellites_group.simulation_time, self.satellites_group.earth_ellipsoid)
        return geo_coordinates_of_search_point

    def to_determine_close_polygons(self):
        """
        @Описание:
            Метод определяет, какие полигоны из заданных, то есть тех, которые должны быть просканированны для решения
                задачи (определенных в объекте класса Task, записанных в списке
                self.satellites_group.task.polygons_group), находятся достаточно близко к моделируемому спутнику, чтобы
                части их территории могли попасть в полосу захвата моделируемого спутника.
        :return: близкие к подспутниковой точке полигоны записываются в список близких к моделируемуму спутнику
                 полигонов.
        """
        # Создание пустого списка
        close_polygons = []
        # Обход всех заданных полигонов, проверка на "близость" к моделируемому спутнику
        for polygon in self.satellites_group.task.polygons_group.polygons_list:
            # Вычисление расстояния от подспутниковой точки до центра полигона и сравнение с суммой расстояния от
            #   подспутниковой точки до края полосы захвата с радиусом выбранного полигона, умноженная на 110% (критерий
            #   близости)
            if (self.satellites_group.earth_ellipsoid.dist_between_geo_coordinates(
                    polygon.center.geo_coordinates, self.satellite_coordinates_set.geo_coordinates) < 1.1 *
                    (polygon.radius + self.satellite_coordinates_set.geo_coordinates.alt *
                     math.tan(self.half_angle_of_view))):
                close_polygons.append(polygon)
        self.close_polygons = close_polygons

    def to_scan(self):
        """
        @Описание:
            Метод моделирует процесс съемки близких полигонов self.close_polygons) за некоторое время. Производится
                проверка того, попадают ли сегменты близких полигонов (объекты из списка segments_list объекта Polygon)
                в полосу захвата за некоторое время self.scanned_territory_for_last_step, допустимый ли в момент съемки
                self.satellites_group.simulation_time зенитный угол Солнца (меньше
                self.satellites_group.task.max_zenith_angle), моделирует облачность или для всех полигонов, или для
                каждого отдельно, задает случайную облачность для каждого сегмента и проверяет, допустима ли облачность
                над полигоном для съемки (меньше self.satellites_group.task.max_cloud_score) и не закрыт ли сегмент
                облаками. Если все эти условия соблюденыЮ, то сегмент считается просканированным и его площадь
                прибавляется к сумме, подаваемой на выход метода.
        :return: площадь просканированной территории (кв. м)
        """
        # Преобразование списка геокоординат self.scanned_territory_for_last_step в объект geometry.Polygon
        scanned_polygon = geometry.Polygon([
            (self.scanned_territory_for_last_step[0].long, self.scanned_territory_for_last_step[0].lat),
            (self.scanned_territory_for_last_step[1].long, self.scanned_territory_for_last_step[1].lat),
            (self.scanned_territory_for_last_step[2].long, self.scanned_territory_for_last_step[2].lat),
            (self.scanned_territory_for_last_step[3].long, self.scanned_territory_for_last_step[3].lat)])
        scanned_area = 0
        # Обход всех близких полигонов
        for polygon in self.close_polygons:
            # Проверка, допустима ли облачность для съемки
            if polygon.current_cloudiness_in_score <= self.satellites_group.task.max_cloud_score:
                # Обход всех сегментов полигона
                for segment in polygon.segments_list:
                    # Проверка всех условий для съемки
                    if (scanned_polygon.contains(segment.center_geo_coordinates.point)) and \
                            (astronomy.sun_zenith_angle(self.satellites_group.simulation_time,
                                                        self.satellite_coordinates_set.geo_coordinates.long,
                                                        self.satellite_coordinates_set.geo_coordinates.lat)
                             <= self.satellites_group.task.max_zenith_angle) and \
                            (not self.satellites_group.task.to_consider_partial_cloudiness
                             or not polygon.segment_is_hidden()):
                        # Сегмент считается, как просканированный еще один раз
                        segment.segment_grabbed()
                        # Площадь сегмента суммируется с общей суммой
                        scanned_area += segment.segments_area
        return scanned_area

    def __str__(self):
        """
        :return: название спутника в системе NORAD
        """
        return str(self.sat_name)


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

    # Ускорение работы объектов класса
    #import pyximport; pyximport.install()

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
        self.subsatellite_cartesian_coordinates = self.subsatellite_geo_coordinates. \
            to_cartesian_coordinates(utc_time, earth_ellipsoid)

    def to_str(self, count_of_numerals_after_point_in_geo_coordinates=3,
               count_of_numerals_after_point_in_altitude=1,
               count_of_numerals_after_point_in_velocity=2):
        """
        @Описание:
            Вывод основных координат спутника - географических координат (градусы), высоты над поверхностью Земли (м),
                скорости (м/с), времени UTC - в виде строки.
        :param count_of_numerals_after_point_in_geo_coordinates: количество знаков после точки при выводе географических
            координат (в градусах). По умолчанию 3.
        :param count_of_numerals_after_point_in_altitude: количество знаков после точки при выводе высоты (в метрах) над
            поверхностью Земли. По умолчанию 1.
        :param count_of_numerals_after_point_in_velocity: количество знаков после точки при выводе скорости (в метрах в
            секунду). По умолчанию 2.
        :return:  строку (String) в виде:
            ***.*** с. ш.(ю. ш.)   ***.*** з. д.(в. д.)  ****.* км  ****.** м/с
        """
        return "".join([self.geo_coordinates.to_str(count_of_numerals_after_point_in_geo_coordinates,
                                                    count_of_numerals_after_point_in_altitude), '\t',
                        str(round(abs(self.velocity_vector), count_of_numerals_after_point_in_velocity)), ' м/с\t',
                        str(self.utc_time)])
