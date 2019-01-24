import math
import statistics
import os
from datetime import timedelta
from calendar import isleap
from DateManagement import to_determine_date_by_days_number_in_not_leap_year, to_determine_days_number_in_not_leap_year
from TimeManagment import to_get_unit_in_seconds, seconds_to_unit, unit_in_symbol
import OutputDataMaker

DEFAULT_MAX_ZENITH_ANGLE = 360
DEFAULT_MAX_CLOUD_SCORE = math.inf
DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD = 1
DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD = 365
DEFAULT_MIN_PERCENT_FOR_SOLVE = 100
DAYS_IN_NOT_LEAP_YEAR = 365
DAYS_IN_LEAP_YEAR = 366


class Task:
    """
    @Описание:
        Класс задает условия выполнения некоторой задачи, обеспечивает взаимодействие объектов классов SatelliteGroup и
            PolygonGroup. Класс имитирует полёт спутников из группы, заданной объектом класса SatellitesGroup, вокруг
            эллипсоида Земли, заданного объектом класса EarthEllipsoid и сканирование территорий, заданных объектом
            класса PolygonsGroup, собирает данные о ходе выполнения задачи и о пролётах спутников над полигонами,
            выводит результаты в различных формах.

    @Поля:
        name - название задачи (String). Задается методом to_set_name. По умолчанию None.
        satellites_group - спутниковая группировка, с помощью которых решается задача (SatelliteGroup). Задается методом
            to_set_satellites_group. По умолчанию None.
        polygons_group - группа полигонов, которые должны быть просканированы, чтобы задача считалась решенной
            (PolygonsGroup). Задается методом to_set_polygons_group. По умолчанию None.
        max_zenith_angle - максимально допустимый зенитный угол Солнца, при котором производится космическая съемка
            (int, double). Задается методом to_set_max_zenith_angle. По умолчанию DEFAULT_MAX_ZENITH_ANGLE.
        max_cloud_score - максимально допустимое количество облаков при котором производится космическая съемка (int).
            Задается методом to_set_max_cloud_score. По умолчанию DEFAULT_MAX_CLOUD_SCORE.
        common_cloudiness_is_calculated - логическая величина. Если True, то значение облачности вычисляется для всех
            полигонов одновременно по распределению self.polygon_list.common_cloudiness_distr_table, а если False, то
            вычисляется для каждого полигона отдельно, в соответствии с собственным распределением (boolean). По
            умолчанию True. Задается методом self.common_cloudiness_is_calculated.
        to_consider_partial_cloudiness - вычислять статистически частичную облачность, если значение True и не
            вычислять, если False (boolean). Определяется с помощью метода
            self.to_set_considering_considering_partial_cloudiness. По умолчанию False.
        initial_annual_observation_period - номер первого дня в невисокосном году годового периода наблюдений (времени в
            году, когда допустима съемка) (int). Задается методом to_set_annual_observations_period. По умолчанию
            DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD.
        final_annual_observation_period - номер последнего дня в невисокосном году годового периода наблюдений (времени
            в году, когда допустима съемка) (int). Задается методом to_set_annual_observations_period. По умолчанию
            DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD.
        observation_period_inside_one_year - индикатор того, что self.final_annual_observation_period больше
            self.initial_annual_observation_period(boolean). Это означает, что что и начало и конец периода наблюдения
            находятся внутри одного года без перехода в следующий (если True, если False, то наоборот). Задается методом
            to_set_annual_observations_period. По умолчанию True.
        min_percent_for_solve - минимальный процент площади территорий полигнов self.satellite_group от общей площади,
            которые должны быть просканированы, чтобы задача считалась выполненной. Задается методом
            to_set_min_percent_for_solve. По умолчанию DEFAULT_MIN_PERCENT_FOR_SOLVE.
        initial_simulation_time - начальное модельное время (datetime), то есть время в формате UTC, в которое
            начинается выполнение задачи внутри модели. Задается методом to_set_border_of_simulation_time. По умолчанию
            None.
        final_simulation_time - конечное модельное время (datetime), то есть время в формате UTC, в которое
            заканчивается выполнение задачи (попытки сканирования полигонов self.polygonGroup) внутри модели. Задается
            методом to_set_border_of_simulation_time. По умолчанию None.
        step - шаг изменения модельного времени в секундах (int, double). Задается методом
            to_set_step_of_simulation_time. По умолчанию None.
        growth_of_information - список. В каждую ячейку записывается площадь, просканированной территории полигонов
            self.PolygonsGroup в кв. метрах (double) за шаг изменения модельного времени self.step. Каждой заполненной
            ячейке сответствует время из списка self.time_of_growth_of_information. При этом в список не записываются
            нулевые значения. Список заполняется при выполнении метода to_solve_task. По умолчанию пустой список [].
        time_of_growth_of_information - список. В каждую ячейку записывается время UTC (datetime), соответствующее
            времени сканиирования площади из соответствующего элемента списка self.growth_of_information. Список
            заполняется при выполнении метода to_solve_task. По умолчанию пустой список [].
        time_of_solutions - список. В каждом элементе записывается модельное время, в которое была выполнена задача
            (datetime). Список заполняется при выполнении метода to_solve_task. По умолчанию пустой список [].

    @Методы:
        to_solve_task - моделирует выполнение задачи, собирает данные, по которым определяются показатели периодичности
            решений задачи и пролетов спутников self.satellite_group над полигонами self.polygons_group. Также выводит
            отчеты о состоянии системы self.satellite_group, вычисляемых показателяй периодичности, о просканированной
            территории группы полигонов self.polygons_group
        to_set_name - задает название задачи. Записывает его в поле self.name.
        to_set_satellites_group - задаёт спутниковую группировку, которая будет выполнять задачу, в виде объекта
            SatelliteGroup. Записывает его в поле self.satelliteGroup.
        to_set_polygons_group - задаёт группу полигонов, для которой будет выполняться задача, в виде объекта
            PolygonsGroup. Записывает его в поле self.polygonsGroup.
        to_set_task_characteristics - задаёт основные параметры задачи, условия выполнения задачи, допустимые условия
            наблюдения.
        to_set_border_of_simulation_time - задаёт период модельного времени в течении которого будет проводиться
            моделирование
        to_set_step_of_simulation_time - задаёт шаг изменения модельного времени в секундах.
        to_set_max_zenith_angle - задаёт максимальный зенитный угол при котором ведётся наблюдение в градусах.
        to_set_max_cloud_score - задаёт максимальный балл облачности при котором ведётся наблюдение.
        to_set_annual_observations_period - задаёт годовой период наблюдения.
        to_set_min_percent_for_solve - задаёт минимальный процент площади заданных полигонов, который требуется
            просканировать, чтобы задача считалась решенной.
        to_clear_statistic_data - очищает все поля, в которых накапливаются данные в процессе моделирования выполнения
            задачи.
        to_output_report - выводит отчет о координатах спутников группы self.satellite_group, о решениях задачи, о
            пролетах спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
            некоторой заданной периодичностью модельного времени.
        to_make_report - составляет отчет о координатах спутников группы self.satellite_group, о решениях задачи, о
            пролетах спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
            некоторой заданной периодичностью модельного времени.
        to_get_information_about_output_data - возвращает строку, содержащую данные о выполненой задачи и о выходных
            данных. Эта строка вставляется в файлы, которые создает  сохраняет OutputDataMaker.
        to_prepare_data_to_output - возвращает объект OutputDataMaker, в который записаны данные о задаче, о времени
            выполнения задачи, о пролетах и о площади просканированной территории. С помощью этого объекта выводятся
            данные о выполнении задачи, о пролетах и др. в требуемом виде.
    """

    def __init__(self):
        self.name = None
        self.satellites_group = None
        self.polygons_group = None
        self.max_zenith_angle = DEFAULT_MAX_ZENITH_ANGLE
        self.max_cloud_score = DEFAULT_MAX_CLOUD_SCORE
        self.to_consider_partial_cloudiness = False
        self.initial_annual_observation_period = DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD
        self.final_annual_observation_period = DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD
        self.observation_period_inside_one_year = True
        self.min_percent_for_solve = DEFAULT_MIN_PERCENT_FOR_SOLVE
        self.initial_simulation_time = None
        self.final_simulation_time = None
        self.step = None
        self.growth_of_information = []
        self.time_of_growth_of_information = []
        self.time_of_solutions = []

    def to_solve_task(self, unit_report_time=None,
                      report_address=None,
                      report_time_from_initial_time=True,
                      report_data_about_satellites=True,
                      count_of_numerals_after_point_in_geo_coordinates=3,
                      count_of_numerals_after_point_in_altitude=1,
                      count_of_numerals_after_point_in_velocity=2,
                      report_main_data_about_solutions=True,
                      report_main_data_about_overflights=True,
                      time_unit_of_report='days',
                      numerals_count_after_point_in_solutions_and_overflights_report=2,
                      to_skip_time_out_of_observation_period=False,
                      report_data_about_scanned_area=True,
                      report_scanned_area_in_percents=True,
                      count_of_numbers_after_point_in_area_report=0):
        """
        @Описание:
            Метод имитирует полёт спутников из группы, заданной объектом класса SatellitesGroup, вокруг
                эллипсоида Земли, заданного объектом класса EarthEllipsoid и сканирование территорий, заданных объектом
                класса PolygonsGroup, собирает данные о ходе выполнения задачи. Также в процессе моделирования выводится
                в консоль, а также могут записываться в отдельный файл txt, отчеты о положении спутников, о собранных
                данных, с заданной периодичностью модельного времени.
        :param unit_report_time: единица измерения времени (см. TimeManagement) (String). Через одну единицу измерения
            будет подаваться отчет в консоль. Допустимо None. Если None, то отчет не подпетсся в принципе. По умолчанию
            None.
        :param report_address: адрес документа txt, в который будут записываться все отчеты (String). Допустимо None.
            Если None, то отчеты не записываются в файл. По умолчанию None.
        :param report_time_from_initial_time: писать в отчетах модельное время от начала моделирования в единицах
            измерения времени, unit_report_time (если True, если False, то не писать)(boolean). По умолчанию True.
        :param report_data_about_satellites: писать в отчетах данные о состоянии спутников (географическое координаты,
            высота, скорость), входящих в систему self.SatelliteGroup (если True, если False, то не писать)(boolean).
        :param count_of_numerals_after_point_in_geo_coordinates: количество знаков после точки при выводе географических
            координат (в градусах) спутников отчете о состоянии. По умолчанию 3.
        :param count_of_numerals_after_point_in_altitude: количество знаков после точки при выводе высоты (в метрах) над
            поверхностью Земли спутников в отчете о состоянии. По умолчанию 1.
        :param count_of_numerals_after_point_in_velocity: количество знаков после точки при выводе скорости (в метрах в
            секунду) спутников отчете о состоянии. По умолчанию 2.
        :param report_main_data_about_solutions: писать в отчетах данные о времени решения (среднее, медианное,
            максимальное, минимальное время, дисперсия, среднеквадратическое отклонение) на текущий момент модельного
            времени (если True, если False, то не писать)(boolean). По умолчанию True.
        :param report_main_data_about_overflights: писать в отчетах данные о времени между пролетами спутников из группы
            self.SatelliteGroup над полигонами self.PolygonsGroup (среднее, медианное, максимальное, минимальное время,
            дисперсия, среднеквадратическое отклонение) на текущий момент модельного времени (если True, если False, то
            не писать)(boolean). По умолчанию True.
        :param time_unit_of_report: единица измерения времени (см. TimeManagement) (String). В этих единицах измерения
            выводяться в отчет данные о времени решений и данные о времени между пролетами спутников из группы
            self.SatelliteGroup над полигонами self.PolygonsGroup на текущий момент модельного времени. По умолчанию
            'days'.
        :param numerals_count_after_point_in_solutions_and_overflights_report: количество цифр после запятой в числах, в
            которых выводятся данные о времени решений и данные о времени между пролетами спутников из группы
            self.SatelliteGroup над полигонами self.PolygonsGroup на текущий момент модельного времени (int). По
            умолчанию 2.
        :param to_skip_time_out_of_observation_period: для отчета о времени решений и данные о времени между пролетами
            спутников из группы self.SatelliteGroup над полигонами self.PolygonsGroup на текущий момент модельного
            времени считать только время в годовых периодах наблюдения (если True, если False, то не писать)(boolean).
            По умолчанию False.
        :param report_data_about_scanned_area: писать в отчете данные о площади сканированных территорий полигонов
            self.PolygonsGroup и количестве сканирований в процентах от общей территории или в кв. метрах (если True,
            если False, то не писать)(boolean). По умолчанию True.
        :param report_scanned_area_in_percents: писать в отчете данные о о площади сканированных территорий в процентах
            от суммарной площади территории полигонов self.PolygonsGroup (если True, если False, то в м^2)(boolean). По
            умолчанию True.
        :param count_of_numbers_after_point_in_area_report: количество цифр после запятой в числах, в которых выводятся
            данные о площади просканированной территории (int). По умолчанию 0.
        :return: заполняются списки:
            self.growth_of_information - площадями просканированной области в кв. метрах, которые были просканированны в
                модельное время, записанное в соответствующую ячейку списка self.time_of_growth_of_information (если это
                0, то не записывается) (double);
            self.time_of_growth_of_information - время, в которое сканировалась территория, площадь которой записана в
                self.growth_of_information с шагом self.step (datetime);
            self.time_of_solutions - время, когда была решена поставленная задача с точность self.step (datetime).
            Также в консоль и в файл report_address выводятся отчеты (вид отчета см. описание метода to_make_report).
        """
        #####
        file = open('D:\\results\\file.txt', 'w')
        # Задание в качестве модельного времени для спутниковой группировки self.SatelliteGroup начального модельного
        #   времени и вычисление координатспутников группировки в это время
        self.satellites_group.to_set_simulation_time(self.initial_simulation_time)
        # Создание файла, в который будут записываться отчеты, если адрес задан
        if report_address is not None:
            #   Получение адреса директории
            report_directory = report_address.rsplit('\\', 1)[0]
            #   Создание директории, если ее нет
            if not os.path.exists(report_directory):
                os.makedirs(report_directory)
            report_file = open(report_address, 'w')
        else:
            report_file = None
        # Проверяется, входет ли начальное время в допустимый период наблюдения. Если нет, то это время переносится на
        #   начало следующего периода наблюдений и именно оно считается начальным модельным временем и записывается в
        #   отчетах и выходных данных
        # Подсчет номера дня в невисокосном году начального модельного времени спутниковой группировки
        days_number_in_year = to_determine_days_number_in_not_leap_year(self.satellites_group.simulation_time)
        if (self.observation_period_inside_one_year ^
            ((days_number_in_year >= self.initial_annual_observation_period) and
             (days_number_in_year <= self.final_annual_observation_period))) or \
                (days_number_in_year == self.initial_annual_observation_period) or \
                (days_number_in_year == self.final_annual_observation_period):
            new_year = self.initial_simulation_time.year
            if (self.observation_period_inside_one_year and
                (days_number_in_year > self.final_annual_observation_period)) or not \
                    self.observation_period_inside_one_year:
                new_year += 1
            new_initial_simulation_time = to_determine_date_by_days_number_in_not_leap_year(
                self.initial_annual_observation_period, new_year)
            # Запись в отчет о смене начального времени
            if unit_report_time is not None:
                output_about_changing_of_initial_simulation_time = \
                    "".join(['Начальное модельное время ', str(self.initial_simulation_time),
                             ' не входит в годовой допустимый интервал наблюдения.\nПоэтому начальное модельное время'
                             'меняется на начало следующего периода - ', str(new_initial_simulation_time), '\n'])
                print(output_about_changing_of_initial_simulation_time)
                if report_file is not None:
                    report_file.write(output_about_changing_of_initial_simulation_time)
                self.initial_simulation_time = new_initial_simulation_time
        # Перевод времени между отчетами из единиц измерения времени в секунды, если это время задано
        if unit_report_time is not None:
            report_time_sec = to_get_unit_in_seconds(unit_report_time)
            # Отправка первого отчета в начальное модельное время
            self.to_output_report(report_file,
                                  report_time_from_initial_time,
                                  unit_report_time,
                                  report_data_about_satellites,
                                  count_of_numerals_after_point_in_geo_coordinates,
                                  count_of_numerals_after_point_in_altitude,
                                  count_of_numerals_after_point_in_velocity,
                                  report_main_data_about_solutions,
                                  report_main_data_about_overflights,
                                  time_unit_of_report,
                                  numerals_count_after_point_in_solutions_and_overflights_report,
                                  to_skip_time_out_of_observation_period,
                                  report_data_about_scanned_area,
                                  report_scanned_area_in_percents,
                                  count_of_numbers_after_point_in_area_report)
        else:
            # Если время между отчетами не задано, то оно приравнивается к бесконечносте
            report_time_sec = math.inf
        # Время от последнего отчета в секундах
        time_from_report_last = 0
        # В цикле проверяется, не вышло ли модельное время спутниковой группировки self.SatelliteGroup за пределы
        #   времени моделирования
        while self.satellites_group.simulation_time < self.final_simulation_time:
            # Подсчет номера дня в невисокосном году текущего модельного времени спутниковой группировки
            days_number_in_year = to_determine_days_number_in_not_leap_year(self.satellites_group.simulation_time)
            # Определение, входит ли текущее время моделирования спутников в годовой период наблюдений
            if not (self.observation_period_inside_one_year ^
                    ((days_number_in_year >= self.initial_annual_observation_period) and
                     (days_number_in_year <= self.final_annual_observation_period))) or \
                    (days_number_in_year == self.initial_annual_observation_period) or \
                    (days_number_in_year == self.final_annual_observation_period):
                # Если входит, то
                #   Определяется следущее модельное время для спутников self.SatelliteGroup через шаг времени self.step
                next_simulation_time = self.satellites_group.simulation_time + timedelta(seconds=self.step)
                #   Моделирование работы спутников из self.SatelliteGroup на следующие self.step секунд. Возвращается
                #       площадь (кв. м) просканированной площади self.PolygonsGroup, меняется текущее модельное время на
                #       next_simulation_time
                scanned_area = self.satellites_group.to_act(next_simulation_time, file)
                #   Изменение времени от последнего отчета
                time_from_report_last += self.step
                #   Если просканированная площадь не нулевая...
                if scanned_area > 0:
                    # То записываются в спискок площадей просконированной территории и список времени сканирования
                    #   просканированная площадь scanned_area площадь и текущее модельное время, соответственно
                    self.growth_of_information.append(scanned_area)
                    self.time_of_growth_of_information.append(self.satellites_group.simulation_time)
                    percentages_of_grabbed_areas_list = self.polygons_group.to_calc_percentages_of_grabbed_areas()
                    #  Проверка, выполнена ли задача
                    if len(self.time_of_solutions) < len(percentages_of_grabbed_areas_list) and \
                            percentages_of_grabbed_areas_list[len(self.time_of_solutions)] >= \
                            self.min_percent_for_solve:
                        # Если выполнена, то текущее модельное время - время выполнения записывается в список времени
                        #   решений self.time_of_solutions
                        self.time_of_solutions.append(self.satellites_group.simulation_time)
                # Определение, настало ли время для нового отчета
                if time_from_report_last >= report_time_sec:
                    # Если да, то подается новый отчет
                    self.to_output_report(report_file,
                                          report_time_from_initial_time,
                                          unit_report_time,
                                          report_data_about_satellites,
                                          count_of_numerals_after_point_in_geo_coordinates,
                                          count_of_numerals_after_point_in_altitude,
                                          count_of_numerals_after_point_in_velocity,
                                          report_main_data_about_solutions,
                                          report_main_data_about_overflights,
                                          time_unit_of_report,
                                          numerals_count_after_point_in_solutions_and_overflights_report,
                                          to_skip_time_out_of_observation_period,
                                          report_data_about_scanned_area,
                                          report_scanned_area_in_percents,
                                          count_of_numbers_after_point_in_area_report)
                    # Время от последнего отчета
                    time_from_report_last = 0
            else:
                # Если не входит, то модельное время сразу переносится на начало следующего годового периода наблюдения
                new_year = self.satellites_group.simulation_time.year
                if (self.observation_period_inside_one_year and
                    (days_number_in_year > self.final_annual_observation_period)) or not \
                        self.observation_period_inside_one_year:
                    new_year += 1
                new_simulation_time = to_determine_date_by_days_number_in_not_leap_year(
                    self.initial_annual_observation_period, new_year)
                # В отчете указывается, когда заканчивается и начинаются периоды наблюдения
                if unit_report_time is not None:
                    report_about_observation_period = "".join([str(self.satellites_group.simulation_time),
                                                               ': годовой период наблюдения заканчивается.\n'
                                                               'Новый период начинается в ',
                                                               str(new_simulation_time), '\n\n'])
                    print(report_about_observation_period)
                    if report_file is not None:
                        report_file.write(report_about_observation_period)
                    # Если во время вне периода наблюдения настовало время отчета, то отчет делается в начале нового
                    #   периода наблюдений
                    time_from_report_last += (new_simulation_time - self.satellites_group.simulation_time).\
                        total_seconds()
                    # Присвоение нового текущего модельного времени
                    self.satellites_group.simulation_time = new_simulation_time
#                    if time_from_report_last >= report_time_sec:
#                        self.to_output_report(report_file,
#                                              report_time_from_initial_time,
#                                              unit_report_time,
#                                              report_data_about_satellites,
#                                              count_of_numerals_after_point_in_geo_coordinates,
#                                              count_of_numerals_after_point_in_altitude,
#                                              count_of_numerals_after_point_in_velocity,
#                                              report_main_data_about_solutions,
#                                              report_main_data_about_overflights,
#                                              time_unit_of_report,
#                                              numerals_count_after_point_in_solutions_and_overflights_report,
#                                              to_skip_time_out_of_observation_period,
#                                              report_data_about_scanned_area,
#                                              report_scanned_area_in_percents,
#                                              count_of_numbers_after_point_in_area_report)
#                        time_from_report_last % report_time_sec
        # Делается последний отчет о моделирований, и файл с отчетами закрывается, если он был открыт
        if report_file is not None:
            self.to_output_report(report_file,
                                  report_time_from_initial_time,
                                  unit_report_time,
                                  report_data_about_satellites,
                                  count_of_numerals_after_point_in_geo_coordinates,
                                  count_of_numerals_after_point_in_altitude,
                                  count_of_numerals_after_point_in_velocity,
                                  report_main_data_about_solutions,
                                  report_main_data_about_overflights,
                                  time_unit_of_report,
                                  numerals_count_after_point_in_solutions_and_overflights_report,
                                  to_skip_time_out_of_observation_period,
                                  report_data_about_scanned_area,
                                  report_scanned_area_in_percents,
                                  count_of_numbers_after_point_in_area_report)
            report_file.close()
            #####
            file.close()

    def to_set_name(self, name):
        """
        @Описание:
            Задает название задачи. Записывает его в поле self.name. Также производится очистка собранных данных, чтобы
                выходная информация не отличалась от пааметров задачи.
        :param name: название задачи (String)
        :return: в поле self.name записывается name
        """
        self.name = name
        # Производится очистка собранных данных, чтобы выходная информация не отличалась от пааметров задачи
        self.to_clear_statistic_data()

    def to_set_satellites_group(self, satellites_group):
        """
        @Описание:
            Задаёт спутниковую группировку, которая будет выполнять задачу, в виде объекта SatelliteGroup. Записывает
                его в поле self.satelliteGroup. Также производится очистка собранных данных, чтобы выходная информация
                не отличалась от пааметров задачи.
        :param satellites_group: спутниковая группировка (SatelliteGroup)
        :return: в поле self.satelliteGroup записывается satellites_group
        """
        self.satellites_group = satellites_group
        # Назначение для группы спутников satellites_group этой задачи
        self.satellites_group.task = self
        # Производится очистка собранных данных, чтобы выходная информация не отличалась от параметров задачи
        self.to_clear_statistic_data()

    def to_set_polygons_group(self, polygons_group):
        """
        @Описание:
            Задаёт группу полигонов, для которой будет выполняться задача, в виде объекта PolygonsGroup. Записывает
                его в поле self.polygonsGroup. Также производится очистка собранных данных, чтобы выходная информация
                не отличалась от пааметров задачи.
        :param polygons_group: группа полигонов (PolygonsGroup)
        :return: в поле self.polygonsGroup записывается polygons_group
        """
        self.polygons_group = polygons_group
        # Производится очистка собранных данных, чтобы выходная информация не отличалась от пааметров задачи
        self.to_clear_statistic_data()

    def common_cloudiness_is_calculated(self, common_cloudiness_is_calculated=True):
        """
        @Описание:
            Устанавливает логическую величину common_cloudiness_is_calculated, то есть постановляет, вычислять ли
                облачность для всех полигонов вместе или для каждого отдельно.
        :param common_cloudiness_is_calculated: логическое значение, которое устанавливается (boolean)
        :return: устанавливается логическая величина self.common_cloudiness_is_calculated
        """
        self.common_cloudiness_is_calculated = common_cloudiness_is_calculated

    def to_set_task_characteristics(self, initial_simulation_time, final_simulation_time, step,
                                    max_zenith_angle, max_cloud_score, initial_annual_observation_period,
                                    final_annual_observation_period, min_percent_for_solve):
        """
        @Описание:
            Задаёт основные параметры задачи, условия выполнения задачи, допустимые условия наблюдения. Также
                производится очистка собранных данных, чтобы выходная информация не отличалась от пааметров задачи.
        :param initial_simulation_time: модельное время начала моделирования (datetime).
        :param final_simulation_time: модельное время конца моделирования (datetime).
        :param step: изменение модельного времени (секунды).
        :param max_zenith_angle: максимальный зенитный угол при котором ведётся наблюдение(градусы). Допустимо None.
        :param max_cloud_score: максимальный балл облачности, при котором ведётся наблюдение (баллы). Допустимо None.
        :param initial_annual_observation_period: первый день в невисокосном году годового периода наблюдения. Допустимо
               None.
        :param final_annual_observation_period: последний день в невисокосном году годового периода наблюдения.
               Допустимо None.
               initial_annual_observation_period может быть меньше, чем final_annual_observation_period. Это означает,
                   что период наблюдений не пересекает границу двух годов. Тогда поле
                   observation_period_inside_one_year=True. Если initial_annual_observation_period
                   больше, чем final_annual_observation_period, то - пересекает. Тогда поле
                   observation_period_inside_one_year=False.
        :param min_percent_for_solve: минимальный процент площади заданных полигонов, который требуется просканировать,
               чтобы зададача считалась решенной. Допустимо None.
        :return: в поле self.initial_simulation_time записывается initial_simulation_time;
                 в поле self.final_simulation_time записывается final_simulation_time;
                 в поле self.step записывается step;
                 в поле self.max_zenith_angle записывается max_zenith_angle, если max_zenith_angle не равен None, если
                    равен, то записывается константа DEFAULT_MAX_ZENITH_ANGLE;
                 в поле self.max_cloud_score записывается max_cloud_score, если max_cloud_score не равен None, если
                    равен, то записывается константа DEFAULT_MAX_CLOUD_SCORE;
                 в поле self.initial_annual_observation_period записывается initial_annual_observation_period, если
                    initial_annual_observation_period или final_annual_observation_period - None, то присваивается
                    константа DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD;
                 в поле self.final_annual_observation_period записывается final_annual_observation_period, если
                    initial_annual_observation_period или final_annual_observation_period - None, то присваивается
                    константа DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD;
                 в поле observation_period_inside_one_year записывается True или False в зависимости от;
                    self.initial_annual_observation_period и final_annual_observation_period;
                 в поле self.min_percent_for_solve записывается min_percent_for_solve, если min_percent_for_solve не
                 равен None, если равен, то записывается константа DEFAULT_MIN_PERCENT_FOR_SOLVE.
        """
        # Используются другие методы get класса
        self.to_set_border_of_simulation_time(initial_simulation_time, final_simulation_time)
        self.to_set_step_of_simulation_time(step)
        self.to_set_max_zenith_angle(max_zenith_angle)
        self.to_set_max_cloud_score(max_cloud_score)
        self.to_set_annual_observations_period(initial_annual_observation_period, final_annual_observation_period)
        self.to_set_min_percent_for_solve(min_percent_for_solve)
        # Производится очистка собранных данных, чтобы выходная информация не отличалась от пааметров задачи
        self.to_clear_statistic_data()

    def to_set_considering_considering_partial_cloudiness(self, to_consider_partial_cloudiness):
        """
        @Описание:
            Метод задаёт поле self.to_consider_partial_cloudiness, которое определяет, учитывать ли во время
            моделирования частичную облачность над полигонами.
        :param to_consider_partial_cloudiness: присваиваемое self.to_consider_partial_cloudiness значение (boolean)
        :return: полю self.to_consider_partial_cloudiness присваивается значение аргумента
                 to_consider_partial_cloudiness
        """
        self.to_consider_partial_cloudiness = to_consider_partial_cloudiness

    def to_set_border_of_simulation_time(self, initial_simulation_time, final_simulation_time):
        """
        @Описание:
            Задаёт период модельного времени в течении которого будет проводиться моделирование.
        :param initial_simulation_time: модельное время начала моделирования (datetime).
        :param final_simulation_time: модельное время конца моделирования (datetime).
        :return: в поле self.initial_simulation_time записывается initial_simulation_time;
                 в поле self.final_simulation_time записывается final_simulation_time.
        """
        self.initial_simulation_time = initial_simulation_time
        self.final_simulation_time = final_simulation_time

    def to_set_step_of_simulation_time(self, step):
        """
        @Описание:
            Задаёт шаг изменения модельного времени в секундах.
        :param step: шаг изменения модельного времени (секунды)
        :return: в поле self.step записывается step
        """
        self.step = step

    def to_set_max_zenith_angle(self, max_zenith_angle):
        """
        @Описание:
            Задаёт максимальный зенитный угол при котором ведётся наблюдение в градусах. Если задаётся значение None,
                то присваивается значение константы DEFAULT_MAX_ZENITH_ANGLE - 360, то есть значение, при котором
                ограничения по зенитному углу Солнца нет.
        :param max_zenith_angle: максимальный зенитный угол при котором ведётся наблюдение(градусы). Может быть None.
        :return: в поле self.max_zenith_angle записывается max_zenith_angle, если max_zenith_angle не равен None, если
                 равен, то записывается константа DEFAULT_MAX_ZENITH_ANGLE
        """
        if max_zenith_angle is not None:
            self.max_zenith_angle = max_zenith_angle
        else:
            self.max_zenith_angle = DEFAULT_MAX_ZENITH_ANGLE

    def to_set_max_cloud_score(self, max_cloud_score):
        """
        @Описание:
            Задаёт максимальный балл облачности при котором ведётся наблюдение. Если задаётся значение None, то
                присваивается значение константы DEFAULT_MAX_CLOUD_SCORE - бесконечность, то есть значение, при котором
                ограничения по облачности нет.
        :param max_cloud_score: максимальный балл облачности при котором ведётся наблюдение. Может быть None.
        :return: в поле self.max_cloud_score записывается max_cloud_score, если max_cloud_score не равен None, если
                 равен, то записывается константа DEFAULT_MAX_CLOUD_SCORE
        """
        if max_cloud_score:
            self.max_cloud_score = max_cloud_score
        else:
            self.max_cloud_score = DEFAULT_MAX_CLOUD_SCORE

    def to_set_annual_observations_period(self, initial_annual_observation_period, final_annual_observation_period):
        """
        @Описание:
            Задаёт годовой период наблюдения.
        :param initial_annual_observation_period: первый день в невисокосном году годового периода наблюдения.
               Допустимо None;
        :param final_annual_observation_period: последний день в невисокосном году годового периода наблюдения.
               Допустимо None;
               initial_annual_observation_period может быть меньше, чем final_annual_observation_period. Это означает,
                   что период наблюдений не пересекает границу двух годов. Тогда поле
                   observation_period_inside_one_year=True. Если initial_annual_observation_period
                   больше, чем final_annual_observation_period, то - пересекает. Тогда поле
                   observation_period_inside_one_year=False. Если задаётся значение initial_annual_observation_period
                   или initial_annual_observation_period - None, то присваивается значение константы
                   DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD - 0 и DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD - 365,
                   соответственно, то есть значения, при котором весь год входит в годовой период наблюдения.
        :return: в поле self.initial_annual_observation_period записывается initial_annual_observation_period, если
                    initial_annual_observation_period или final_annual_observation_period - None, то присваивается
                    константа DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD;
                 в поле self.final_annual_observation_period записывается final_annual_observation_period, если
                    initial_annual_observation_period или final_annual_observation_period - None, то присваивается
                    константа DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD;
                 в поле observation_period_inside_one_year записывается True или False в зависимости от
                    self.initial_annual_observation_period и final_annual_observation_period.
        """
        if initial_annual_observation_period is not None:
            self.initial_annual_observation_period = initial_annual_observation_period
        else:
            self.initial_annual_observation_period = DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD
        if final_annual_observation_period is not None:
            self.final_annual_observation_period = final_annual_observation_period
        else:
            self.final_annual_observation_period = DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD
        self.observation_period_inside_one_year = final_annual_observation_period > initial_annual_observation_period

    def to_set_min_percent_for_solve(self, min_percent_for_solve):
        """
        @Описание:
            Задаёт минимальный процент площади заданных полигонов, который требуется просканировать, чтобы задача
                считалась решенной. Если задаётся значение None, то присваивается значение константы
                DEFAULT_MIN_PERCENT_FOR_SOLVE - 100.
        :param min_percent_for_solve: минимальный процент площади заданных полигонов, который требуется просканировать,
               чтобы зададача считалась решенной. Допустимо None.
        :return: в поле self.min_percent_for_solve записывается min_percent_for_solve, если min_percent_for_solve н
                 равен None, если равен, то записывается константа DEFAULT_MIN_PERCENT_FOR_SOLVE
        """
        if min_percent_for_solve is not None:
            self.min_percent_for_solve = min_percent_for_solve
        else:
            self.min_percent_for_solve = DEFAULT_MIN_PERCENT_FOR_SOLVE

    def to_clear_statistic_data(self):
        """
        @Описание:
            Метод очищает все поля, в которых накапливаются данные в процессе моделирования выполнения задачи.
        :return: присваивает self.growth_of_information значение [];
                 присваивает self.collecting_satellites значение [];
                 присваивает self.time_of_growth_of_information значение [];
                 присваивает self.time_of_solutions значение [];
        """
        self.growth_of_information = []
        self.time_of_growth_of_information = []
        self.time_of_solutions = []

    def to_output_report(self, report_file=None,
                         time_from_initial_time=True,
                         time_unit_from_initial_time='days',
                         data_about_satellites=True,
                         count_of_numerals_after_point_in_geo_coordinates=3,
                         count_of_numerals_after_point_in_altitude=1,
                         count_of_numerals_after_point_in_velocity=2,
                         data_about_solutions=True,
                         data_about_overflights=True,
                         time_unit='days',
                         numerals_count_after_point_in_solutions_and_overflights_report=2,
                         to_skip_time_out_of_observation_period=False,
                         data_about_scanned_area=True,
                         scanned_area_in_percents=True,
                         count_of_numbers_after_point_in_area_report=2):
        """
        @Описание:
            Метод выводит отчет о координатах спутников группы self.satellite_group, о решениях задачи, о пролетах
                спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
                некоторой заданной периодичностью модельного времени. Отчёт выводится в консоль и в файл по заданному
                адресу, если он был задан.
        :param report_file: адрес файла txt, в который будут выводиться отчёты. Если задано None, запись
            отчётов в файл не производится (String, допустимо None).
        :param time_from_initial_time: написать в отчете время от начального модельного времени до текущего в единицах
            измерения времени time_unit_from_initial_time (boolean). По умолчанию True.
        :param time_unit_from_initial_time: единицы измерения времени, в которых будет выводиться врем от модельного
            времени начала наблюдения (предполагается, что будет соответствовать времени, через которое делается отчет).
        :param data_about_satellites: написать в отчете координаты каждого спутника в текущее модельное время (boolean).
            По умолчанию True.
        :param count_of_numerals_after_point_in_geo_coordinates: количество знаков после точки при выводе географических
            координат (в градусах) спутников отчете о состоянии. По умолчанию 3.
        :param count_of_numerals_after_point_in_altitude: количество знаков после точки при выводе высоты (в метрах) над
            поверхностью Земли спутников в отчете о состоянии. По умолчанию 1.
        :param count_of_numerals_after_point_in_velocity: количество знаков после точки при выводе скорости (в метрах в
            секунду) спутников отчете о состоянии. По умолчанию 2.
        :param data_about_solutions: написать в отчете данные о времени решений: среднее, максимальное, минимальное,
            среднеквадратическое отклонение, а также общее количество решений от начального модельного времени до
            текущего (boolean). По умолчанию True.
        :param data_about_overflights: написать в отчете данные о времени пролётов спутников self.satellite_group над
            полигонами self.polygons_group: среднее, максимальное, минимальное, среднеквадратическое отклонение, а также
            общее количество пролетов от начального модельного времени до текущего (boolean). По умолчанию True.
        :param time_unit: Единицы измерения времени (см. TimeManagement.py), в которых выводятся данные о решении и
            пролётах (String). По умолчанию 'days'
        :param numerals_count_after_point_in_solutions_and_overflights_report: количество знаков после запятой в отчете
            о времени решений и пролетов (int). По умолчанию 2.
        :param to_skip_time_out_of_observation_period: НЕ учитывать при подсчете времени решения и пролетов периодов,
            между годовыми периодами наблюдений (между днями в году с номерами self.final_annual_observation_period и
            self.initial_annual_observation_period) (boolean). По умолчанию False.
        :param data_about_scanned_area: написать в отчете какая площадь заданных полигонов self.polygon_group были
            просканированы, сколько раз (boolean). По умолчанию True.
        :param scanned_area_in_percents: выводить отчет о площпди просканированной территории self.polygon_group в
            процентах (boolean). Если False, то выводитсяв кв. м. По умолчанию True.
        :param count_of_numbers_after_point_in_area_report: количество знаков после запятой в отчете просканированных
            территориях (int). По умолчанию 2.
        :return: выводит в консоль и в файл txt по адресу report_file отчет, составляемый с помощью метода
            self.to_make_report
        """
        # Текст отчета составляется с помощью метода self.to_make_report
        report = self.to_make_report(time_from_initial_time,
                                     time_unit_from_initial_time,
                                     data_about_satellites,
                                     count_of_numerals_after_point_in_geo_coordinates,
                                     count_of_numerals_after_point_in_altitude,
                                     count_of_numerals_after_point_in_velocity,
                                     data_about_solutions,
                                     data_about_overflights,
                                     time_unit,
                                     numerals_count_after_point_in_solutions_and_overflights_report,
                                     to_skip_time_out_of_observation_period,
                                     data_about_scanned_area,
                                     scanned_area_in_percents,
                                     count_of_numbers_after_point_in_area_report)
        # Вывод отчета в консоль
        print(report)
        # Вывод отчета в файл txt по адресу report_file, если файл задан
        if report_file is not None:
            report_file.write(report)

    def to_make_report(self, time_from_initial_time=True,
                       time_unit_from_initial_time='days',
                       data_about_satellites=True,
                       count_of_numerals_after_point_in_geo_coordinates=3,
                       count_of_numerals_after_point_in_altitude=1,
                       count_of_numerals_after_point_in_velocity=2,
                       data_about_solutions=True,
                       data_about_overflights=True,
                       time_unit='days',
                       numerals_count_after_point_in_solutions_and_overflights_report=2,
                       to_skip_time_out_of_observation_period=False,
                       data_about_scanned_area=True,
                       scanned_area_in_percents=True,
                       count_of_numbers_after_point_in_area_report=2):
        """
        @Описание:
            Метод составляет отчет о координатах спутников группы self.satellite_group, о решениях задачи, о пролетах
                спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
                некоторой заданной периодичностью модельного времени.
        :param time_from_initial_time: написать в отчете время от начального модельного времени до текущего в единицах
            измерения времени time_unit_from_initial_time (boolean). По умолчанию True.
        :param time_unit_from_initial_time: единицы измерения времени, в которых будет выводиться врем от модельного
            времени начала наблюдения (предполагается, что будет соответствовать времени, через которое делается отчет).
        :param data_about_satellites: написать в отчете координаты каждого спутника в текущее модельное время (boolean).
            По умолчанию True.
        :param count_of_numerals_after_point_in_geo_coordinates: количество знаков после точки при выводе географических
            координат (в градусах) спутников отчете о состоянии. По умолчанию 3.
        :param count_of_numerals_after_point_in_altitude: количество знаков после точки при выводе высоты (в метрах) над
            поверхностью Земли спутников в отчете о состоянии. По умолчанию 1.
        :param count_of_numerals_after_point_in_velocity: количество знаков после точки при выводе скорости (в метрах в
            секунду) спутников отчете о состоянии. По умолчанию 2.
        :param data_about_solutions: написать в отчете данные о времени решений: среднее, максимальное, минимальное,
            среднеквадратическое отклонение, а также общее количество решений от начального модельного времени до
            текущего (boolean). По умолчанию True.
        :param data_about_overflights: написать в отчете данные о времени пролётов спутников self.satellite_group над
            полигонами self.polygons_group: среднее, максимальное, минимальное, среднеквадратическое отклонение, а также
            общее количество пролетов от начального модельного времени до текущего (boolean). По умолчанию True.
        :param time_unit: Единицы измерения времени (см. TimeManagement.py), в которых выводятся данные о решении и
            пролётах (String). По умолчанию 'days'
        :param numerals_count_after_point_in_solutions_and_overflights_report: количество знаков после запятой в отчете
            о времени решений и пролетов (int). По умолчанию 2.
        :param to_skip_time_out_of_observation_period: НЕ учитывать при подсчете времени решения и пролетов периодов,
            между годовыми периодами наблюдений (между днями в году с номерами self.final_annual_observation_period и
            self.initial_annual_observation_period) (boolean). По умолчанию False.
        :param data_about_scanned_area: написать в отчете какая площадь заданных полигонов self.polygon_group были
            просканированы, сколько раз (boolean). По умолчанию True.
        :param scanned_area_in_percents: выводить отчет о площпди просканированной территории self.polygon_group в
            процентах (boolean). Если False, то выводитсяв кв. м. По умолчанию True.
        :param count_of_numbers_after_point_in_area_report: количество знаков после запятой в отчете просканированных
            территориях (int). По умолчанию 2.
        :return: текст отчета (String) в виде (полный текст отчета):
            Время: 'yyyy-MM-dd hh:mm:ss' - 'ddd' дней начального времени
            Состояние спутников:
                'satellite_1':  ** с. ш.(ю. ш.)   ** з. д.(в. д.)  **** м  **** м/с
                'satellite_2':  ** с. ш.(ю. ш.)   ** з. д.(в. д.)  **** м  **** м/с
                'satellite_3':  ** с. ш.(ю. ш.)   ** з. д.(в. д.)  **** м  **** м/с
                ...
            Основные показатели периодичности решений на текущий момент:
                Средний период:         '**.**' 'u'
                Медианный период:       '**.**' 'u'
                Максимальный период:    '**.**' 'u'
                Минимальный период:     '**.**' 'u'
                Дисперсия:              '**.**' 'u'
                Среднее кв. отклонение:  '**.**' 'u'
                Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
            Основные показатели периодичности пролетов на текущий момент:
                Средний период:         '**.**' 'u'
                Медианный период:       '**.**' 'u'
                Максимальный период:    '**.**' 'u'
                Минимальный период:     '**.**' 'u'
                Дисперсия:              '**.**' 'u'
                Среднее кв. отклонение:  '**.**' 'u'
                Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
            Данные о ходе сканирования:
                1 раз просканированно ***% (м^2) исследуемой территории
                2 раз просканированно ***% (м^2) исследуемой территории
                3 раз просканированно ***% (м^2) исследуемой территории
                ...
        """
        # Записывается текущее время
        current_time = self.satellites_group.simulation_time
        # Строка текущего времени
        str_time_report = "".join(['Время: ', str(current_time)])
        # Время от начального модельного времени до текущего
        if time_from_initial_time:
            str_addition_time_report = "".join([' - ', str(round(
                seconds_to_unit((current_time - self.initial_simulation_time).total_seconds(),
                                time_unit_from_initial_time))), ' ', unit_in_symbol(time_unit_from_initial_time),
                                                ' от начального времени'])
        else:
            str_addition_time_report = ''
        # Отчет о состоянии спутников в группе self.satellite_group
        if data_about_satellites:
            str_satellites_data = ['Состояние спутников:\n']
            for satellite in self.satellites_group.satellites_list:
                str_satellites_data.append("".join(['\t', str(satellite.sat_name), ':\t',
                                                    satellite.satellite_coordinates_set.to_str(
                                                        count_of_numerals_after_point_in_geo_coordinates,
                                                        count_of_numerals_after_point_in_altitude,
                                                        count_of_numerals_after_point_in_velocity), '\n']))
            str_satellites_data = "".join(str_satellites_data)
        else:
            str_satellites_data = ''

        if data_about_solutions or data_about_overflights:
            # Вычисление времени от начального модельного времени до текущего в секундах
            current_time_of_simulation = (current_time - self.initial_simulation_time).total_seconds()
            # Отчет о решении задачи на текущий момент модельного времени
            if data_about_solutions:
                # Вычисление периодов между соседними решениями задачи (или от начального модельного времени)
                periods_of_solutions = to_identify_periods_sec(self.time_of_solutions,
                                                               self.initial_simulation_time,
                                                               self.initial_annual_observation_period,
                                                               self.final_annual_observation_period,
                                                               to_skip_time_out_of_observation_period)
                # Запись данных о решениях и о их времени
                str_solutions_report = \
                    "".join(['Основные показатели периодичности решений на текущий момент:\n',
                             to_get_main_data_about_periods(
                                 periods_of_solutions,
                                 time_unit,
                                 numerals_count_after_point_in_solutions_and_overflights_report,
                                 current_time_of_simulation),
                             '\n'])
            else:
                str_solutions_report = ''
            # Отчет о пролетах спутников из self.satellite_group над полигонами из self.polygon_group на текущий момент
            #   модельного времени
            if data_about_overflights:
                # Вычисление модельного времени пролетов (начала сеансов сканирования)
                time_of_overflights = to_define_initial_times_of_scan_session(self.time_of_growth_of_information,
                                                                              self.step)
                # Вычисление периодов между соседними пролетами (или от начального модельного времени)
                periods_of_overflight = to_identify_periods_sec(time_of_overflights,
                                                                self.initial_simulation_time,
                                                                self.initial_annual_observation_period,
                                                                self.final_annual_observation_period,
                                                                to_skip_time_out_of_observation_period)
                # Запись данных о пролетах и о их времени
                str_overflights_report = \
                    "".join(['Основные показатели периодичности пролетов на текущий момент:\n',
                             to_get_main_data_about_periods(
                                 periods_of_overflight,
                                 time_unit,
                                 numerals_count_after_point_in_solutions_and_overflights_report,
                                 current_time_of_simulation),
                             '\n'])
            else:
                str_overflights_report = ''
        else:
            str_solutions_report = ''
            str_overflights_report = ''
        # Отчет о площади просканированной территории полигонов self.polygon_group
        if data_about_scanned_area:
            str_scanned_area = ['Данные о ходе сканирования:\n']
            scanned_area_list = self.polygons_group.to_calc_percentages_of_grabbed_areas(scanned_area_in_percents)
            # Вывод процентах или кв. м.
            if scanned_area_in_percents:
                for i in range(0, len(scanned_area_list)):
                    str_scanned_area.append("".join(['\t', str(i + 1), ' раз просканированно ',
                                                     str(round(scanned_area_list[i],
                                                               count_of_numbers_after_point_in_area_report)),
                                                     '% исследуемой территории\n']))
                "".join(str_scanned_area)
            else:
                for i in range(0, len(scanned_area_list)):
                    str_scanned_area.append(
                        "".join(['\t', str(i + 1), ' раз просканированно ',
                                 str(round(scanned_area_list[i], count_of_numbers_after_point_in_area_report)),
                                 ' м^2 исследуемой территории\n']))
            str_scanned_area = "".join(str_scanned_area)
        else:
            str_scanned_area = ''
        # Сшивание частей отчета
        str_report = "".join([str_time_report, str_addition_time_report, '\n', str_satellites_data,
                              str_solutions_report, str_overflights_report, str_scanned_area, '\n'])
        return str_report

    def to_get_information_about_output_data(self):
        """
        @Описание:
            Метод возвращает строку, содержащую данные о выполненой задачи и о выходных данных. Эта строка вставляется в
                файлы, которые создает  сохраняет OutputDataMaker.
                Это следующие данные:
                    название задачи self.name;
                    начальное и конечное модельное время self.initial_annual_observation_period и
                        self.final_annual_observation_period;
                    шаг изменения модельного времени self.step;
                    список спутников, выполняющих задачу self.satellites_group.satellites_list;
                    список полигонов, которые должны быть просканированы для выполнения задачи;
                    границы допустимого периода наблюдения self.initial_annual_observation_period и
                        self.final_annual_observation_period, если он задан;
                    максимально допустимый зенитный угол Солнца self.max_zenith_angle;
                    максимально допустимый балл облачности self.max_cloud_score;
                    учитывается ли частичная облачность.

        :return: строка данных (String) в виде:
            Основные параметры задачи 'name'
                Модельное время:                                от 'yyyy-MM-dd hh:mm:ss' до 'yyyy-MM-dd hh:mm:ss'
                Шаг изменения модельного времени:               'step' с
                Спутники, выполняющие задачу:                   'satellite_1', 'satellite_2', 'satellite_3', ...
                Названия сканируеемых полигонов:                'polygon_1', 'polygon_2', 'polygon_3', ...
                Допустимый период наблюдения:                   от 'ddd' дня до 'ddd' дня (или 'не задан')
                Максимально допустимый зенитный угол Солнца:    'uu'°
                Максимально допустимый балл облачности:         'sss'
                Частичная облачность учитывается (не учитывается)
        """
        # Запись списка спутников self.satellites_group.satellites_list в строку
        str_satellites = []
        for satellite in self.satellites_group.satellites_list:
            str_satellites.append("".join([satellite.sat_name, ', ']))
        str_satellites = "".join(str_satellites)
        # Удаление запятой в конце строчного списка спутников
        str_satellites = str_satellites[:-2]
        # Запись списка полигонов self.polygons_group.polygons_list в строку
        str_polygons = []
        for polygon in self.polygons_group.polygons_list:
            str_polygons.append("".join([polygon.name, ', ']))
        str_polygons = "".join(str_polygons)
        # Удаление запятой в конце строчного списка спутников
        str_polygons = str_polygons[:-2]
        # Запись границ годового периода наблюдений в строку, если он задан и 'не задан', если не задан
        if self.initial_annual_observation_period == DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD and \
                self.final_annual_observation_period == DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD:
            str_annual_observation = 'не задан'
        else:
            str_annual_observation = "".join(['от ', str(self.initial_annual_observation_period), ' дня до ',
                                              str(self.final_annual_observation_period), ' дня'])
        if self.to_consider_partial_cloudiness:
            str_considering_of_partial_cloudiness = 'Частичная облачность учитывается'
        else:
            str_considering_of_partial_cloudiness = 'Частичная облачность не учитывается'
        # Запись информации в строку
        str_info = "".join([
            'Основные параметры задачи\t', str(self.name), ':\n',
            '\tМодельное время:\t\t\t\tот ', str(self.initial_simulation_time), ' до ',
            str(self.final_simulation_time),
            '\n',
            '\tШаг изменения модельного времени:\t\t', str(self.step), ' с\n',
            '\tСпутники, выполняющие задачу:\t\t\t', str_satellites, '\n',
            '\tНазвания сканируеемых полигонов:\t\t', str_polygons, '\n',
            '\tДопустимый период наблюдения:\t\t\t', str_annual_observation, '\n',
            '\tМаксимально допустимый зенитный угол Солнца:\t', str(self.max_zenith_angle), '°\n',
            '\tМаксимально допустимый балл облачности:\t\t', str(self.max_cloud_score), '\n',
            '\t', str_considering_of_partial_cloudiness, '\n\n'])
        return str_info

    def to_prepare_data_to_output(self):
        """
        @Описание:
            Метод возвращает объект OutputDataMaker, в который записаны данные о задаче, о времени выполнения задачи, о
                пролетах и о площади просканированной территории. С помощью этого объекта выводятся данные о выполнении
                задачи, о пролетах и др. в требуемом виде.
        :return: объект OutputDataMaker
        """
        return OutputDataMaker.OutputDataMaker(self.name, self.polygons_group.full_area, self.initial_simulation_time,
                                               self.final_simulation_time, self.step, self.growth_of_information,
                                               self.time_of_growth_of_information, self.time_of_solutions,
                                               self.initial_annual_observation_period,
                                               self.final_annual_observation_period,
                                               self.to_get_information_about_output_data())


def to_identify_periods_sec(time_list, first_time=None,
                            initial_annual_observation_period=DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD,
                            final_annual_observation_period=DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD,
                            to_skip_time_out_of_observation_period=False):
    """
    @Описание:
        Метод определяет время от времени начала наблюдения до первого значения времени из заданного списка и между
            соседними значениями времени из заданного списка в секундлах. Возможно вычисление периодов только по
            допустимому годовому периоду наблюдения.
    :param time_list: список значений времени, по которому будут вычисляться (date_time).
    :param first_time: начальное время наблюдений, от которого будет отсчитываться первый период (datetime).
        Допустимо None. При этом сразу вычисляются периоды между значениями time_list. По умолчанию None.
    :param initial_annual_observation_period: номер первого дня в невисокосном году допустимого годового периода
        наблюдения (времени в году, когда допустима съемка) (int). Задается методом to_set_annual_observations_period.
        По умолчанию DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD.
    :param final_annual_observation_period: номер последнего дня в невисокосном году годового подустимого периода
        наблюдений (времени в году, когда допустима съемка) (int). Задается методом to_set_annual_observations_period.
        По умолчанию DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD.
    :param to_skip_time_out_of_observation_period: пропускать промежутки времени, не входящие в годовые периоды
           наблюдения (boolean). По умолчанию False.
    :return: список приодов в секундах (int, double)
    """
    # Если нету пары значений времени (начального времени first_time и одного значения из time_list или два значения
    #   из time_list), то возвращается [], а дальнейшие вычисления не производятся. Если есть, то задаётся первое
    #   значение времени, от которого будет вестись отсчет - previous_time.
    if first_time is not None:
        if len(time_list) > 0:
            previous_time = first_time
        else:
            return []
    else:
        if len(time_list > 1):
            previous_time = time_list[0]
            del time_list[0]
        else:
            return []
    # В список periods записываются периоды
    periods = []
    # Если не пропускается время между периодами наблюдения
    if not to_skip_time_out_of_observation_period:
        # Список periods заполняется значениями периодов
        for time in time_list:
            period = (time - previous_time).total_seconds()
            periods.append(period)
            previous_time = time
    # Если пропускается время между периодами наблюдения
    else:
        # Определение индикатора observation_period_inside_one_year, который показывает, что
        #   final_annual_observation_period больше initial_annual_observation_period. Это означает, что что и начало и
        #   конец периода наблюдения находятся внутри одного года без перехода в следующий (если True, если False, то
        #   наоборот).
        observation_period_inside_one_year = final_annual_observation_period > initial_annual_observation_period
        # Вычисление даты начала годового периода наблюдения
        current_year = time_list[0].year
        start_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
            initial_annual_observation_period, current_year)
        end_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
            final_annual_observation_period, current_year)
        # Если previous_time оказывается не в периоде наблюдения, оно перемещается на начало следующего периода
        if observation_period_inside_one_year:
            if start_of_current_observation_period > previous_time > end_of_current_observation_period:
                previous_time = start_of_current_observation_period
        else:
            if previous_time < start_of_current_observation_period:
                previous_time = start_of_current_observation_period
                if previous_time < end_of_current_observation_period:
                    if not isleap(current_year):
                        days_in_current_year = DAYS_IN_LEAP_YEAR
                    else:
                        days_in_current_year = DAYS_IN_NOT_LEAP_YEAR
                    previous_time += timedelta(days=days_in_current_year)
        # Если период наблюдений не пересекает границу соседних годов
        if observation_period_inside_one_year:
            for time in time_list:
                current_year = time.year
                year_of_previous_time = previous_time.year
                skipped_time = 0
                year_of_skipped_period = current_year
                # Вычисление времени, не входящего в период наблюдения
                while year_of_skipped_period > year_of_previous_time:
                    start_of_new_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                        initial_annual_observation_period, year_of_skipped_period)
                    end_of_old_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                        final_annual_observation_period, year_of_skipped_period - 1)
                    skipped_time += (
                            start_of_new_observation_period - end_of_old_observation_period).total_seconds()
                    year_of_skipped_period -= 1
                # Вычисление периода без времени, не входящего в период наблюдения
                period = (time - previous_time).total_seconds() - skipped_time
                periods.append(period)
                previous_time = time
        # Если период наблюдений пересекает границу соседних годов
        else:
            for time in time_list:
                day_of_time_in_year = to_determine_days_number_in_not_leap_year(previous_time)
                if day_of_time_in_year >= initial_annual_observation_period:
                    year_of_not_observing_period = previous_time.year + 1
                else:
                    year_of_not_observing_period = previous_time.year
                end_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                    final_annual_observation_period, year_of_not_observing_period)
                skipped_time = 0
                time_copy = time
                # Вычисление времени, не входящего в период наблюдения
                while time_copy >= end_of_current_observation_period:
                    day_of_time_copy_in_year = to_determine_days_number_in_not_leap_year(previous_time)
                    if day_of_time_copy_in_year >= initial_annual_observation_period:
                        year_of_skipped_period = previous_time.year
                    else:
                        year_of_skipped_period = previous_time.year - 1
                    start_of_new_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                        initial_annual_observation_period, year_of_skipped_period)
                    end_of_old_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                        final_annual_observation_period, year_of_skipped_period)
                    skipped_time += (start_of_new_observation_period - end_of_old_observation_period). \
                        total_seconds()
                    time_copy = to_determine_date_by_days_number_in_not_leap_year(
                        to_determine_days_number_in_not_leap_year(time_copy), time_copy.year - 1)
                # Вычисление периода без времени, не входящего в период наблюдения
                period = (time - previous_time).total_seconds() - skipped_time
                periods.append(period)
                previous_time = time
    return periods


def to_get_main_data_about_periods(periods, unit_of_output_time, numerals_count_after_point, overall_time_of_modeling):
    """
    @Описание:
        Метод возвращает некоторые основные показатели периодчности по заданным периодам времени в заданых
            едидниицах измерения времени. Среди выходных параметров: среднее, медианное, максимальное, минимальное
            значение, дисперсия и среднеквадратическое отклонение, а также общее количество значений за заданное
            время наблюдения в заданных единицах измерения времени.
    :param periods: списов периодов в секундах, по которым производится вычисление (int, double).
    :param unit_of_output_time: единицы измерения времени (см. файл TimeManagement), в которых будут выводиться
           данные (String).
    :param numerals_count_after_point: количество знаков после запятой, в выходных значениях значениях (int).
    :param overall_time_of_modeling: общее время вычисления предоставленных значений в секундах (int, double).
    :return: "основные показатели" строкой в общем виде:
        Средний период:         '**.**' 'u'
        Медианный период:       '**.**' 'u'
        Максимальный период:    '**.**' 'u'
        Минимальный период:     '**.**' 'u'
        Дисперсия:              '**.**' 'u'
        Среднее кв. отклонение:  '**.**' 'u'
        Всего за время моделирования - '**.**' 'u' - было сделано измерений: '**'
    """
    # Символ - обозначение единицы измерения времени unit_of_output_time
    unit_symbol = unit_in_symbol(unit_of_output_time)
    # Если список значений periods не пустой, вычисляются "основные" параметры
    if periods is not []:
        # Вычисление выходных параметров  с помощью метода to_determine_median_average_max_min_dispersion_standard
        average_period_value, median_period_value, max_period_value, min_period_value, dispersion_period_value,\
            standard_deviation_period_value = to_determine_median_average_max_min_dispersion_standard(periods)
        # Перевод всех "основных" параметров из секунд в единицы измерения времени unit_of_output_time и округление
        #   до numerals_count_after_point знаков после запятой
        average_period_value = round(seconds_to_unit(average_period_value, unit_of_output_time),
                                     numerals_count_after_point)
        median_period_value = round(seconds_to_unit(median_period_value, unit_of_output_time),
                                    numerals_count_after_point)
        max_period_value = round(seconds_to_unit(max_period_value, unit_of_output_time),
                                 numerals_count_after_point)
        min_period_value = round(seconds_to_unit(min_period_value, unit_of_output_time),
                                 numerals_count_after_point)
        dispersion_period_value = round(seconds_to_unit(dispersion_period_value, unit_of_output_time),
                                        numerals_count_after_point)
        standard_deviation_period_value = round(seconds_to_unit(standard_deviation_period_value,
                                                                unit_of_output_time),
                                                numerals_count_after_point)
    # Если список значений periods пустой, "основные" параметры приравниваются к нулю
    else:
        average_period_value = 0
        median_period_value = 0
        max_period_value = 0
        min_period_value = 0
        dispersion_period_value = 0
        standard_deviation_period_value = 0
    # В любом случае время вычислений переводится в unit_of_output_time и округляется до numerals_count_after_point
    #   знаков
    overall_time_of_modeling = round(seconds_to_unit(overall_time_of_modeling, unit_of_output_time),
                                     numerals_count_after_point)
    # Запись вычесленных данных в строку
    str_data_about_periods = "".join([
        '\tСредний период:\t\t', str(average_period_value), ' ', unit_symbol, '\n',
        '\tМедианный период:\t', str(median_period_value), ' ', unit_symbol, '\n',
        '\tМаксимальный период:\t', str(max_period_value), ' ', unit_symbol, '\n',
        '\tМинимальный период:\t', str(min_period_value), ' ', unit_symbol, '\n',
        '\tДисперсия:\t\t', str(dispersion_period_value), ' ', unit_symbol, '\n',
        '\tСреднее кв. отклонение:\t', str(standard_deviation_period_value), ' ', unit_symbol, '\n',
        '\tВсего за время моделирования - ', str(overall_time_of_modeling), ' ', unit_symbol,
        ' - было сделано измерений: ', str(len(periods))])
    return str_data_about_periods


def to_determine_median_average_max_min_dispersion_standard(numbers):
    """
    @Описание:
        По списку чисел вычисляет их среднее, медианное, максимальное, минимальное значение, их дисперсию и
            среднеквадратическое отклонение.
    :param numbers: список чисел, для которых проводится вычисления.
    :return:
        average_value: среднее значение по списку numbers (double)
        median_value: медианное значение по списку numbers (double)
        max_value: максимальное значение по списку numbers (double)
        min_value: минимальное значение по списку numbers (double)
        dispersion: дисперсия по списку numbers (double)
        standard_deviation: среднеквадратическое отклонение по списку numbers (double)
    """
    if len(numbers) > 0:
        average_value = statistics.mean(numbers)
        median_value = statistics.median(numbers)
        max_value = max(numbers)
        min_value = min(numbers)
        if len(numbers) > 1:
            dispersion = statistics.variance(numbers)
            standard_deviation = statistics.stdev(numbers)
        else:
            dispersion = 0
            standard_deviation = 0
    else:
        average_value = 0
        median_value = 0
        max_value = 0
        min_value = 0
        dispersion = 0
        standard_deviation = 0
    return average_value, median_value, max_value, min_value, dispersion, standard_deviation


def to_define_initial_times_of_scan_session(time_of_growth_of_information, step):
    """
    @Описание:
        Метод определяет время всех начала пролётов на данный момент (начала сессии скаирования).
    :param time_of_growth_of_information: список времени (datetime) сканирования.
    :param step: шаг времени в секундах (int, double) - точность, с которой определяется начало пролета.
    :return: список объектов datetime - времени всех пролётов на данный момент (начала сессии скаирования)
    """
    time_of_growth_of_information = time_of_growth_of_information
    # Массив модельного времени пролетов
    time_of_overflights = []
    if len(time_of_growth_of_information) > 0:
        # Начальное время первого пролёта
        initial_time_of_overflight = time_of_growth_of_information[0]
        # Вычисление времен начала пролетов. Началом пролета считается то время, когда сбор данных только начался,
        #   а до этого был нулевым
        for i in range(1, len(time_of_growth_of_information)):
            if (time_of_growth_of_information[i] - time_of_growth_of_information[i - 1]).total_seconds() > step:
                time_of_overflights.append(initial_time_of_overflight)
                initial_time_of_overflight = time_of_growth_of_information[i]
        time_of_overflights.append(initial_time_of_overflight)
    return time_of_overflights
