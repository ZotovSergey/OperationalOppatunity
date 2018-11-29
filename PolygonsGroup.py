from shapefile import Reader
from random import random
from numpy import arange, concatenate, zeros
from shapely import geometry
import math
import Coordinates
import DateManagement


class PolygonsGroup:
    """
    @Описание:
        Класс PolygonsGroup моделирует группу наземных тестовых полигонов, которые должны быть просканированны, для того
            чтобы поставленная задача была выполнена. Предусматривается возможность разбиение на мелкие сегменты всех
            полигонов в группе, подсчёта количества сканирований каждого сегмента в отдельности, подсчёта
            приблизительной площади всех полигонов, моделирования облачности над полигонами в общем или над каждым в
            отдельности.

    @Аргументы:
        earth_ellipsoid - объект класса EarthEllipsoid.

    @Поля:
        earth_ellipsoid - объект класса EarthEllipsoid, задающий параметры модели эллипсоида Земли, на котором
            расположена группа полигонов. При инициализации присваивается значение аргумента earth_ellipsoid
        polygons_list – список, состоящий из объектов класса Polygon, где каждый элемент обозначает тестовый полигон
            принадлежащий моделируемой группе полигонов. При инициализации - пустой список. Заполняется методом
            self.to_read_shape_file
        full_segments_list - список, содержащий все сегменты, на которые разделены все полигоны из моделируемой группы.
            При инициалиации задаётся пустым списком. Заполняется с помощью метода to_split_all_polygons
        full_area – общая площадь всех полигонов, входящих в моделируемую группу. Общая площадь вычисляется
            суммированием площадей всех полигонов, входящих в группу, то есть всех, перечисленных в списке (кв. м)
            self.polygons_list, а площадь каждого полигона – объекта класса Polygon записана в их поле polygons_area.
            При инициализации - 0. Вычисляется при применении метода self.to_split_all_polygons
        common_cloudiness_distr_table - двумерный список, содержащий распределения вероятности появления облачности
            некоторого балла в районе, где находится моделируемая группа полигонов для годовых периодов, границы которых
            записываются в self.common_cloudiness_distr_ranges. При инициалиации присваивается [[0]]. Обновляется
            методом self.to_randomize_common_cloudiness.
        common_cloudiness_distr_ranges - границы годовых периодов, для которых записаны в
            self.common_cloudiness_distr_table (дни от начала не високосного года). При инициалиации присваивается
            [1, 365]. Обновляется методом self.to_randomize_common_cloudiness.
        common_current_cloudiness_in_score - балл облачности над моделируемой группой полигонов. При инициалиации
            присваивается 0. Обновляется методом to_randomize_common_cloudiness объекта класса PolygonGroup.
    @Методы:
        to_read_shape_file(self, shape_file_address) – читает из shape-файла информацию о тестовых полигонах, полигоны
            добавляются в список self.polygons_list.
        to_set_polygons_names(self, polygons_names) - задает имена полигонам, входящим в моделируемую группу.
        to_split_all_polygons(self, lat_fineness, long_fineness, earth_ellipsoid) – разбивает каждый полигон в группе на
            сегменты с мелкостью разбиения lat_fineness по широте и long_fineness по долготе, вычисляет приблизительную
            общую площадь всех полигонов в моделируемой группе.
        to_calc_percentages_of_grabbed_areas(self) – определяет ход выполнения тематической задачи – сколько процентов
            площади тестовых полигонов попало в поле зрения ГСК, сколько раз.
        to_clear_count_of_grabs(self) - очищает все сегменты всех полигонов от "сканирований". То есть после применения
            считается, что полигоны не сканировались.
        to_add_common_cloudiness_distr(self, common_cloudiness_distr_table, common_cloudiness_distr_ranges) - добавляет
            распределения вероятности появления облачности некоторого балла в районе, где находится моделируемая группа
            полигонов для годовых периодов, границы которых также записываются.
        to_add_cloudiness_distr_to_each_polygon(self, cloudiness_distr_tables_list, cloudiness_distr_ranges_list) -
            добавляет распределения вероятности появления облачности некоторого балла для каждого полигона в
            моделируемой группе для годовых периодов, границы которых также записываются.
        to_normalize_distribution(distribution) - нормируетраспределение на единицу distribution.
        to_randomize_common_cloudiness(self, time) - случайно определяет текущий балл облачности для всей моделируемой
            группы полигонов в соответвии с распределением из self.common_cloudiness_distr_table для времени из
            аргумента time.
    """
    def __init__(self, earth_ellipsoid):
        self.earth_ellipsoid = earth_ellipsoid
        self.polygons_list = []
        self.full_segments_list = []
        self.full_area = 0
        self.common_cloudiness_distr_table = [[0]]
        self.common_cloudiness_distr_ranges = [1, 365]
        self.common_current_cloudiness_in_score = 0

    def to_read_shape_file(self, shape_file_address):
        """
        @Описание:
            Открывает для чтения shape-файл, в цикле обходится все геометрические объекты типа “Polygon” (в терминах из
                описания формата shape-файла), из записанных в открытый shape-файл. На каждом витке создаётся объект
                self.Polygon(shape, self.earth_ellipsoid), где shape - один из геометрических объектов типа “Polygon”,
                self.earth_ellipsoid - объект EarthEllipsoid, задающий параметры эллипсоида Земли, на котором находится
                полигон, и добавляется в self.polygonsList, задает стандартные имена.
        :param shape_file_address: адресс shape-файла, из которого читается информация о тестовых полигонах.
        """

        # Чтение информации о полигонах из файла по адресу shape_file_address
        shape_file = Reader(shape_file_address)
        shape_file_list = list(shape_file.iterShapes())
        # Создание объектов self.Polygon(shape, self.earth_ellipsoid), где shape - один из объектов из списка, объект
        # EarthEllipsoid, задающий параметры эллипсоида Земли, на котором находится создаваемый полигон shape_file_list
        # и запись в self.polygons_list в цикле
        for shape in shape_file_list:
            self.polygons_list.append(Polygon(shape, self.earth_ellipsoid))
        # Задание полигонам стандартных названий: "Полигон 1", "Полигон 2", "Полигон 3" ...
        self.to_set_polygons_names([])

    def to_set_polygons_names(self, polygons_names):
        """
        Метод задает имена из списка polygons_names полигонам, входящим в моделируемую группу (self.polygons_list).
            Полигонам из списка self.polygons_list сообщаются имена из списка polygons_names в соответствии их номерам
            в списках. Полигонам, которым название не задано (None) или не хватает имен (если длина списка
            self.polygons_list больше polygons_names), сообщается стандартное название "Полигон 1", "Полигон 2",
            "Полигон 3" ...
        :param polygons_names: список имен, присвиваемых полигонам из списка self.polygons_list (в списке допустимы
            значения None)
        :return:
        """
        number_of_unnamed_polygon = 1
        i = 0
        while i < len(polygons_names):
            if polygons_names[i] is not None:
                self.polygons_list[i].to_set_polygons_name(polygons_names[i])
            else:
                self.polygons_list[i].to_set_polygons_name('Полигон ' + str(number_of_unnamed_polygon))
                number_of_unnamed_polygon += 1
            i += 1
        while i < len(self.polygons_list):
            self.polygons_list[i].to_set_polygons_name('Полигон ' + str(number_of_unnamed_polygon))
            number_of_unnamed_polygon += 1
            i += 1

    def to_split_all_polygons(self, lat_fineness, long_fineness):
        """
        @Описание:
            Метод разбивает каждый полигон в группе (из списка polygons_list) на сегменты с мелкостью разбиения
                lat_fineness по широте и long_fineness по долготе, вычисляет приблизительную общую площадь всех
                полигонов в моделируемой группе
        :param lat_fineness: мелкость разбиения сегментов по широте (км)
        :param long_fineness: мелкость разбиения сегментов по долготе (км)
        """
        self.full_segments_list = []
        self.full_area = 0
        # В цикле к каждому полигону применяется метод to_split_polygon(lat_fineness, long_fineness)
        for polygon in self.polygons_list:
            polygon.to_split_polygon(lat_fineness, long_fineness)
            # Сегменты, на которые разделился полигон из группы включаются в список всех сегментов моделируемой группы
            #   self.full_segments_list
            self.full_segments_list += polygon.segments_list
            # Площадь полигона из группы прибавляется к общей площади полигонов из моделируемой группы
            self.full_area += polygon.area

    def to_calc_percentages_of_grabbed_areas(self, result_in_percents=True):
        """
        @Описание:
            Метод определяет ход выполнения тематической задачи – какая площадь иили сколько процентов площади тестовых
                полигонов попало в поле зрения ГСК, сколько раз
        :param result_in_percents: если result_in_percents=True, то результат возвращается в процентах, если
            result_in_percents=False, то результат возвращается в м^2
        :return: список, в каждом элементе которого содержится процент площади группы полигонов, захваченных в ПЗ ГСК n
            раз, где n равняется номеру элемента списка плюс один
        """
        segments_list = self.full_segments_list
        percentages_of_grabbed_areas_list = []
        i = 1
        # Цикл продолжает работу пока из списка segments_list не дудут исключены все сегменты
        while len(segments_list) > 0:
            new_list_of_grabbed_segments = []
            current_area = 0
            # В цикле перебираются все сегменты из списка segments_list и проверяется, сколько раз он был просканирован:
            #   если i раз (i - счетчик), то площадь сегмента прибавляется к площади, просканированной i раз, если
            #   меньше, то сегмент исключается из списка segments_list
            for segment in segments_list:
                if segment.count_of_grabs >= i:
                    if segment.count_of_grabs > i:
                        new_list_of_grabbed_segments.append(segment)
                    current_area += segment.space
            # Вычисляется в м^2
            percentages_of_grabbed_areas_list.append(current_area)
            if result_in_percents:
                # м^2 переводится в проценты
                percentages_of_grabbed_areas_list[-1] /= self.full_area * 100
            segments_list = new_list_of_grabbed_segments
            i += 1
        return percentages_of_grabbed_areas_list

    def to_clear_count_of_grabs(self):
        """
        @Описание:
            Очищает все сегменты всех полигонов от "сканирований". То есть после применения считается, что полигоны не
                сканировались.
        :return: count_of_grabs каждого сегмента, каждого полигона в группе приравнивается к нулю.
        """
        for polygon in self.polygons_list:
            for segment in polygon.segments_list:
                segment.count_of_grabs = 0

    def to_add_common_cloudiness_distr(self, common_cloudiness_distr_table, common_cloudiness_distr_ranges):
        """
        @Описание:
            Метод добавляет распределения вероятности появления облачности некоторого балла в районе, где находится
                моделируемая группа полигонов для годовых периодов, границы которых также записываются
        :param common_cloudiness_distr_table: двумерный список, содержащий распределения вероятности появления
            облачности некоторого балла в районе, где находится моделируемая группа полигонов для годовых периодов,
            границы которых записываются в common_cloudiness_distr_ranges
        :param common_cloudiness_distr_ranges: границы годовых периодов, для которых известны распределения вероятности
            появления облачности некоторого балла в районе, где находится моделируемая группа полигонов (дни от начала
            не високосного года)
        """
        self.common_cloudiness_distr_ranges = common_cloudiness_distr_ranges
        # Распределения вероятностей нормируются на единицу
        self.common_cloudiness_distr_table = self.to_normalize_distribution(common_cloudiness_distr_table)

    def to_add_cloudiness_distr_to_each_polygon(self, cloudiness_distr_tables_list, cloudiness_distr_ranges_list):
        """
        @Описание:
            Метод добавляет распределения вероятности появления облачности некоторого балла для каждого полигона в
                моделируемой группе для годовых периодов, границы которых также записываются
        :param cloudiness_distr_tables_list: трехмерный список, содержащий распределения вероятности появления
            облачности некоторого балла для каждого полигона из моделируемой группы для годовых периодов, границы
            которых записываются в common_cloudiness_distr_ranges
        :param cloudiness_distr_ranges_list: границы годовых периодов, для которых известны распределения вероятности
            появления облачности некоторого балла в районе, где находится моделируемая группа полигонов (дни от начала
            не високосного года)
        """
        for i in range(0, len(self.polygons_list)):
            self.polygons_list[i].cloudiness_distr_ranges = cloudiness_distr_ranges_list[i]
            # Распределения вероятностей нормируются на единицу
            self.polygons_list[i].cloudiness_distr_table =\
                self.to_normalize_distribution(cloudiness_distr_tables_list[i])

    @staticmethod
    def to_normalize_distribution(distribution):
        """
        @Описание:
            Метод нормируетраспределение на единицу distribution.
        :param distribution: нормируемое распределение.
        :return: нормированное на единицу распределение.
        """
        elements_sum = zeros(len(distribution))
        for i in range(0, len(distribution)):
            for element in distribution[i]:
                elements_sum += element
            for element in distribution[i]:
                element /= elements_sum
        return distribution

    def to_randomize_common_cloudiness(self, time):
        """
        @Описание:
            Метод случайно определяет текущий балл облачности для всей моделируемой группы полигонов в соответвии с
                распределением из self.common_cloudiness_distr_table для времени из аргумента time
        :param time: объект datetime - время в формате UTC
        """
        self.common_current_cloudiness_in_score = to_randomize_cloudiness(time, self.common_cloudiness_distr_table,
                                                                          self.common_cloudiness_distr_ranges)


class Polygon:
    """
    @Описание:
        Класс Polygon моделирует наземный полигон, который входит в группу полигонов, моделируемых PolygonsGroup, и
            должен быть просканирован для решени задачи. Предусматривается возможность разбиения полигона на мелкие
            сегменты, учёта количества сканирования каждого сегмента в отдельности, подсчёта приблизительной площади
            полигона, моделирования облачности над полигоном и каждым сегментом отдельно.

    @Аргументы
        shape - содержит геометрический объект типа “Polygon” (в терминах из описания shape-формата), прочитанный из
            shape-файла. Записанный геометрический объект определяет границы тестового полигона
        polygons_group - объект PolygonGroup - группа полигонов, к которой относится создаваемы объект

    @Поля:
        shape – содержит геометрический объект типа “Polygon” (в терминах из описания shape-формата), прочитанный из
            shape-файла. Записанный геометрический объект определяет границы тестового полигона. При инициализации
            объект в поле записывается значение аргумента shape.
        polygons_name - название полигона. При инициализации присваивается None. Задается методом to_set_polygons_name.
        segments_list – список, состоящий из объектов класса Segment, где каждый элемент обозначает один из сегментов на
            которые разбит моделируемый полигон. Заполняется при применении метода to_split_polygon.
        polygons_area – площадь моделируемого полигона с некоторой точностью, равна общей площади всех сегментов, на
            которые разбит тестовый полигон, то есть сумма полей segments_area объектов Segment, входящих в список
            self.segmentsList. При инициализации объекта приравнивается к нулю, значение обновляется при применении
            метода to_split_polygon.
        own_group - содержит объект PolygonsGroup - группу полигонов, к которой относится моделируемый полигон. В
            own_group содержится поле. Присваивается аргумент polygons_group при инициализации объекта.
            earth_ellipsoid, используещееся в вычислениях для моделируемого полигона.
        top_border_lat – широта самой северной точки на границе тестового полигона. Вычисляется при инициализации
        bot_border_lat – широта самой южной точки на границе тестового полигона. Вычисляется при инициализации
        left_border_long – долгота самой западной точки на границе тестового полигона. Вычисляется при инициализации
        right_border_long – долгота самой восточной точки на границе тестового полигона. Вычисляется при инициализации
        center – объект Coordinates.GeoCoordinatesAndPointSet, содержащий координаты точки на поверхности Земли. (высота
            над поверхностью Земли всегда 0) - центра полигона. Вычисляется при инициализации
        radius – расстояние от центра тестового полигона до самой дальней от него точки на границы
            полигона. Определяется при инициализации
        cloudiness_distr_table - таблица (двумерный список), содержащая распределения вероятности появления облачности
            некоторого балла (балл соответствует номеру элемента одномерного списка, содержащего распределение, включая
            ноль, вероятность для этого балла записана в значение этого элемента, полная вероятность нормирована на
            единицу) над моделируемым полигоном для каждого периода времени в не високосном году, границы которых
            записаны в список cloudiness_distr_ranges в днях от начала года. При инициалиации присваивается список
        [[0]].
            Устанавливается методом to_add_cloudiness_distr_to_each_polygon объекта класса PolygonGroup.
        cloudiness_distr_ranges - список, содержащий границы годовых периодов, для которых определены распределения
            вероятности появления над моделируемым полигоном балла облачности, в днях от начала не високосного года. При
            инициализации присваивается список [0, 365]. Устанавливается методом to_add_cloudiness_distr_to_each_polygon
            объекта класса PolygonGroup.
        current_cloudiness_in_score - балл облачности над моделируемым полигоном. При инициалиации присваивается 0.
            Обновляется методом to_randomize_cloudiness_to_each_polygon объекта класса PolygonGroup.


    @Методы
        to_set_polygons_name(self, polygons_name) - задает название полигона.
        to_split_polygon(self, lat_fineness, long_fineness) - разделяет моделируемый полигон на сегменты с мелкостью
            разбиения по широте lat_fineness и по долготе long_fineness
        to_calculate_segments_area(self, lat_of_grids_nodes, longFineness) - метод вычисляет площади сегментов,
            на которые делится полигон в зависимости от широты их верхних и нижних границ lat_of_grids_nodes и мелкости
            разбиения по долготе long_fineness
        to_calculate_space_from_equator_to_lat(self, lat) - вычисляет площадь поверхности эллипсоида Земли
            self.own_group.earth_ellipsoid от экватора до заданной аргументом lat широты
        segment_is_hidden(self) – случайным образом определяет закрыт ли некоторый сегмент моделируемого полигона
            облаком или тенью от облака. Вероятность зависит от текущего балла облачности над полигоном
            self.current_cloudiness_in_score
        to_randomize_cloudiness_to_polygon(self, time) - добавляет распределения вероятности появления облачности
            некоторого балла моделируемого полигона для годовых периодов, границы которых также
            записываются
    """
    def __init__(self, shape, polygon_group):
        self.shape = shape
        self.polygons_name = None
        self.segments_list = []
        self.area = 0
        self.own_group = polygon_group
        [self.left_long_border, self.bot_lat_border, self.right_long_border, self.top_lat_border] = shape.bbox
        self.center = Coordinates.GeoCoordinatesAndPointSet((self.left_long_border + self.right_long_border) / 2,
                                                            (self.top_lat_border + self.bot_lat_border) / 2, 0)
        border_points = shape.points
        max_distance = 0
        for point in border_points:
            geo_coordinates_of_point = Coordinates.GeoCoordinates(point.x, point.y, 0)
            distance_to_point = self.own_group.earth_ellipsoid.dist_between_geo_coordinates(self.center,
                                                                                            geo_coordinates_of_point)
            if distance_to_point > max_distance:
                max_distance = distance_to_point
        self.radius = max_distance
        self.cloudiness_distr_table = [[0]]
        self.cloudiness_distr_ranges = [1, 365]
        self.current_cloudiness_in_score = 0

    def to_set_polygons_name(self, polygons_name):
        """
        Метод задает название полигона polygons_name.
        :param polygons_name: Название полигона.
        :return: поле self.polygons_name приравнивается к значению аргумента polygons_name.
        """
        self.polygons_name = polygons_name

    def to_split_polygon(self, lat_fineness, long_fineness):
        """
        @Описание:
            Разделяет моделируемый полигон на сегменты с мелкостью разбиения по широте lat_fineness и по долготе
                long_fineness
        :param lat_fineness: мелкость разбиения сегментов по широте (км)
        :param long_fineness: мелкость разбиения сегментов по долготе (км)
        """
        self.area = 0
        # Координаты центрального сегмента будет совпадать с центром полигона
        coordinates_of_central_segment = Coordinates.GeoCoordinates(self.center.geo_coordinates.long,
                                                                    self.center.geo_coordinates.lat, 0)
        # Определение координат центров сегментов в виде сетки -двумерного списка
        lat_of_segments = concatenate([arange(coordinates_of_central_segment.lat - lat_fineness, self.bot_lat_border,
                                              -lat_fineness), arange(coordinates_of_central_segment.lat,
                                                                     self.top_lat_border, lat_fineness)])
        long_of_segments = concatenate([arange(coordinates_of_central_segment.long - long_fineness,
                                               self.right_long_border, -long_fineness),
                                        arange(coordinates_of_central_segment.long, self.left_long_border,
                                               long_fineness)])
        # Определение широт границ сегментов с юга на север
        lat_of_grids_nodes = arange(self.bot_lat_border - lat_fineness, self.top_lat_border + lat_fineness,
                                    lat_fineness)
        # Вычисление площадей сегментов в зависимости от их широты
        area_of_segments_of_lat = self.to_calculate_segments_area(lat_of_grids_nodes, long_fineness)
        # Представление моделируемого объекта в виде прямоугольника на плоскости
        polygon = geometry.Polygon(self.shape.points)
        # В двойном цикле производится проверка того, принадлежат ли сегменты, координаты которых записаны в
        #   lat_of_segments и long_of_segments моделируемому полигону
        for i in range(0, len(lat_of_segments)):
            for segment_long in long_of_segments:
                # Проверка того, находится ли центр сегмента внутри многоугольника
                point = geometry.Point(segment_long, lat_of_segments[i])
                if polygon.contains(point):
                    # Если центр сегмента находится внутри многоугольника, то он добавляется в список сегментов, на
                    #   которые разделён моделируемый полигон self.segments_list
                    self.segments_list.append(Segment(segment_long, lat_of_segments[i], area_of_segments_of_lat[i]))
                    # Также площадь сегмента (определяемая из списка area_of_segments_of_lat) прибавляется к общей
                    #   площади полигона self.area
                    self.area += area_of_segments_of_lat[i]

    def to_calculate_segments_area(self, lat_of_grids_nodes, long_fineness):
        """
        @Описание:
            Метод вычисляет площади сегментов, на которые делится полигон в зависимости от широты их верхних и нижних
                границ lat_of_grids_nodes и мелкости разбиения по долготе long_fineness
        :param lat_of_grids_nodes: список границ сегментов полигона по широте (градусы)
        :param long_fineness: мелкость разбиения моделируемого полигона на сегменты по долготе (градусы)
        :return: список длиной в (len(lat_of_grids_nodes) - 1), содержащий площади сегментов (кв. км), на которые
            делится моделируемый полигон. В элементе с номером i содержит площадь сегмента, расположенного между
            широтами lat_of_grids_nodes[i] и lat_of_grids_nodes[i + 1]
        """
        # Создание пустого массива, в который будут записываться результаты
        area_of_segments_of_lat = []
        # Вычисление площадь эллипсоида self.own_group.earth_ellipsoid от экватора до нижней границы самого южного
        #   сегмента
        area_from_equator_to_segments_bot_border = self.to_calculate_space_from_equator_to_lat(lat_of_grids_nodes[0])
        # В цикле вычислеяются площади сегментов от широты и добавляется в area_of_segments_of_lat
        for lat_of_node in lat_of_grids_nodes[1:]:
            # Вычисление площадь эллипсоида self.own_group.earth_ellipsoid от экватора до верхней границы некоторого
            #   сегмента
            area_from_equator_to_segments_top_border = self.to_calculate_space_from_equator_to_lat(lat_of_node)
            # Вычисляется площадь некоторого сегмента и добавляется в список результатов
            area_of_segments_of_lat.append((area_from_equator_to_segments_top_border -
                                            area_from_equator_to_segments_bot_border) * long_fineness / 360)
            area_from_equator_to_segments_bot_border = area_from_equator_to_segments_top_border
        return area_of_segments_of_lat

    def to_calculate_space_from_equator_to_lat(self, lat):
        """
        @Описание:
            Метод вычисляет площадь поверхности эллипсоида Земле self.own_group.earth_ellipsoid от экватора до заданной
                аргументом lat широты. Вычисление происходит методом интегрирования части эллипсоида по поверхности
        :param lat: широта, до которой вычесляется площадь (градусы)
        :return: площадь поверхности на эллипсоиде Земли self.own_group.earth_ellipsoid от экватора эллипсоида до
            заданной широты lat (кв. км)
        """
        semi_major_axle = self.own_group.earth_ellipsoid.semi_major_axle
        semi_minor_axle = self.own_group.earth_ellipsoid.semi_minor_axle
        y = semi_minor_axle * math.sin(lat * math.pi / 180)
        a = semi_major_axle * semi_major_axle - semi_minor_axle * semi_minor_axle
        b = a ** 0.5
        c = semi_minor_axle ** 4
        d = (c + y * y * a) ** 0.5
        return 2 * math.pi / semi_minor_axle * d * ((c * math.log(b * d + y * a)) / (b * d) + y)

    def segment_is_hidden(self):
        """
        @Описание:
            Метод случайным образом определяет закрыт ли некоторый сегмент моделируемого полигона облаком или тенью от
                облака. Вероятность зависит от текущего балла облачности над полигоном self.current_cloudiness_in_score
        :return: возвращается логическая величина. Если возвращается False – это означает, что данный сегмент не скрыт
            облаками или тенью от облаков, если True - скрыт. Вероятность возврата “правды” или “лжи” зависит от
            значения self.current_cloudiness_in_score
        """
        # Вычисление доли неба, закрытого облаками по баллу облачности
        current_cloudiness_in_proportion = self.current_cloudiness_in_score / (len(self.cloudiness_distr_table[0]) - 1)
        # Определяется случайне число от 0 до 1
        rand = random()
        # rand сравнивается с вероятности скрытия некоторого сегмента облаками или тенью от облаков
        return rand >= current_cloudiness_in_proportion * (2 - current_cloudiness_in_proportion)

    def to_randomize_cloudiness_to_polygon(self, time):
        """
        @Описание:
            Метод случайно определяет текущий балл облачности моделируемого полигона в соответвии с распределением для
                полигона, для времени из аргумента time
        :param time: объект datetime - время в формате UTC
        """
        self.current_cloudiness_in_score = to_randomize_cloudiness(time, self.cloudiness_distr_table,
                                                                   self.cloudiness_distr_ranges)


class Segment:
    """
    @Описание
        Класс моделирует один из сегментов, на которые разделен некоторый наземный полигон, моделируемый объектом
            Polygon. Предусматривается возможность подсчёта, сколько раз был просканирован моделируемый сегмент

    @Аргументы
        long - долгогта географического центра сегмента
        lat - широта географического центра сегмента
        segments_area - площадь сегмента в кв. километрах

    @Поля
        center_geo_coordinates – объект Coordinates.GeoCoordinatesAndPointSet(long, lat, 0) содержащий географические
            координаты географического центра сегмента на поверхности Земли. Задается при инициализации, long и lat -
            аргументы объекта
        segments_area – площадь сегмента. При инициализации задается значением аргумента segments_area
        count_of_grabs – число захватов сегмента в ПЗ любого из ГСК, участвующего в выполнении задачи, за все время
            моделирования. При инициализации задается значние 0

    @Методы:
        segment_grabbed(self) – прибавляет единицу к значению поля self.countOfGrabs, то есть обозначает, что этот
        сегмент попал в ПЗ ГСК
    """
    def __init__(self, long, lat, segments_area):
        self.center_geo_coordinates = Coordinates.GeoCoordinatesAndPointSet(long, lat, 0)
        self.segments_area = segments_area
        self.count_of_grabs = 0

    def segment_grabbed(self):
        """
        @Описание:
            Метод прибавляет единицу к значению поля self.countOfGrabs, то есть обозначает, что этот сегмент попал в ПЗ
                ГСК
        """
        self.count_of_grabs += 1


def to_randomize_cloudiness(time, distribution_of_year_range, borders_of_ranges):
    """
    @Описание:
        Метод случайно определяет балл облачности в соответвии с распределением из distribution_of_year_range для
            времени из аргумента time
    :param time: объект datetime - время в формате UTC
    :param distribution_of_year_range: двумерный массив, содержащий распределения вероятности выпадения некоторого
        балла облачности для годовых периодов, границы которых записаны в аргументе borders_of_ranges
    :param borders_of_ranges: границы годовых периодов, для которых в аргументе distribution_of_year_range
        определены распределения вероятности выпадения некоторого балла облачности
    :return: случайный балл облачности
    """
    # Определение дня от начала года в невисокосном году
    days_number_in_year = DateManagement.to_determine_days_number_in_not_leap_year(time)
    # Проверяется, входит ли заданный день в заданные годовые периоды, для которых заданы распределения облачности.
    #   Если нет, то возвращается 0.
    if (days_number_in_year < distribution_of_year_range[0]) or (days_number_in_year >
                                                                 distribution_of_year_range[-1]):
        return 0
    # Определяется, в какой период входит время time
    i = 0
    while days_number_in_year <= borders_of_ranges[i]:
        i += 1
    distribution = distribution_of_year_range[i]
    # Вычисление случайного балла облачности в соответствии с распределением для определенного выше годового периода
    rand = random()
    j = 0
    sum_proportion = distribution[0]
    while rand >= sum_proportion:
        j += 1
        sum_proportion += distribution[j]
    return j
