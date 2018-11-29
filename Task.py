import math
import statistics
import matplotlib.pyplot as plt
from DateManagement import to_determine_date_by_days_number_in_not_leap_year, to_determine_days_number_in_not_leap_year
from TimeManagment import to_get_unit_in_seconds, seconds_to_unit, unit_in_symbol
from datetime import timedelta
from calendar import isleap

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
            времени сканиирования площади из соответствующего элемента списка growth_of_information. Список заполняется
            при выполнении метода to_solve_task. По умолчанию пустой список [].
        time_of_solutions - Список. В каждом элементе записывается модельное время, в которое была выполнена задача
            (double). Список заполняется при выполнении метода to_solve_task. По умолчанию пустой список [].

    @Методы:
        to_solve_task - моделирует выполнение задачи, собирает данные, по которым определяются показатели периодичности
            решений задачи и пролетов спутников self.satellite_group над полигонами self.polygons_group. Также выводит
            отчеты о состоянии системы self.satellite_group, вычисляемых показателяй периодичности, о просканированной
            территории группы полигонов self.polygons_group
        to_output_data - преобразует данные, собранные методом to_solve_task в:
                среднее, медианное, максимальное, минимальное значениее времени выполнения задачи, дисперсию и
                среднеквадратическое отклонение (далее основные оказатели) и выводит в виде докумена txt;
                гистограмму распределения времении выполнения задачи и выводит в текстовом виде в документе txt, в
                    графичечском виде в документе pdf, jpg;
                основные показатели периодичности пролётов спутников над полигонами и выводит в виде докумена txt;
                гистограмму распределения периода пролётов спутников над полигонами и выводит в текстовом виде в
                    документе txt, в графичечском видиде в документе pdf, jpg;
                график прироста просканированной территории (в м^2 или в %) за выбранный период времени и выводит в
                    текстовом виде в документе txt, в графичечском виде в документе pdf, jpg;
                график просканированной территории (в м^2 или в %)  и выводит в текстовом виде в документе txt, в
                    графичечском виде в документе pdf, jpg.
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
        to_define_initial_times_of_scan_session - определяет модельное время всех пролётов на данный момент (начала
        сессии скаирования).
        to_get_main_data_about_periods - возвращает некоторые основные показатели периодчности по заданным периодам
            времени в заданых едидниицах измерения времени. Среди выходных параметров: среднее, медианное, максимальное,
            минимальное значение, дисперсия и среднеквадратическое отклонение, а также общее количество значений за
            заданное время наблюдения в заданных единицах измерения времени.
        to_determine_median_average_max_min_dispersion_standard - по списку чисел вычисляет их среднее, медианное,
            максимальное, минимальное значение, их дисперсию и среднеквадратическое отклонение.
        to_get_information_about_task - возвращает некоторые данные о выполняемой задаче - о объекте self - в виде
            строки.
        to_identify_periods_sec - определяет время от времени начала наблюдения до первого значения времени из заданного
            списка и между соседними значениями времени из заданного списка в секундлах.
        to_make_axis - принимает список чисел и список соответствующих им значений времени. Числа группируются по
            времени с шагом в одну заданную единицу измерения времени и суммируются. На выход подается список сумм чисел
            и список значений времени, соответсвующих суммам (началу отсчета времени для группы) или отсчеты заданных
            единиц измерения времени от первого - нулевого значения.
        to_sum_values_on_axis - суммирование каждого значения заданного списка со всеми прдыдущими (интегрирование).
        to_make_histogram - создает гистограмму из списка значений с шагом в одну заданную единицу измерения времени.
    """

    def __init__(self):
        self.name = None
        self.satellites_group = None
        self.polygons_group = None
        self.max_zenith_angle = DEFAULT_MAX_ZENITH_ANGLE
        self.max_cloud_score = DEFAULT_MAX_CLOUD_SCORE
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
                      report_time_from_initial_time_in_days=True,
                      report_data_about_satellites=True,
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
        :param report_time_from_initial_time_in_days: писать в отчетах модельное время от начала моделирования в днях
            (если True, если False, то не писать)(boolean). По умолчанию True.
        :param report_data_about_satellites: писать в отчетах данные о состоянии спутников (географическое координаты,
            высота, скорость), входящих в систему self.SatelliteGroup (если True, если False, то не писать)(boolean).
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
        # Создание файла, в который будут записываться отчеты, если адрес задан
        if report_address is not None:
            report_file = open(report_address, 'w')
        else:
            report_file = None
        # Перевод времени между отчетами из единиц измерения времени в секунды, если это время задано
        if unit_report_time is not None:
            report_time_sec = to_get_unit_in_seconds(unit_report_time)
            # Отправка первого отчета в начальное модельное время
            self.to_output_report(report_file,
                                  report_time_from_initial_time_in_days,
                                  report_data_about_satellites,
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
        # Задание в качестве модельного времени для спутниковой группировки self.SatelliteGroup начального модельного
        #   времени
        self.satellites_group.simulation_time = self.initial_simulation_time
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
                scanned_area = self.satellites_group.to_act(next_simulation_time)
                #   Если просканированная площадь не нулевая...
                if scanned_area > 0:
                    # То записываются в спискок площадей просконированной территории и список времени сканирования
                    #   просканированная площадь scanned_area площадь и текущее модельное время, соответственно
                    self.growth_of_information.append(scanned_area)
                    self.time_of_growth_of_information.append(self.satellites_group.simulation_time)
                    percentages_of_grabbed_areas_list = self.polygons_group.to_calc_percentages_of_grabbed_areas()
                    #  Проверка, выполнена ли задача
                    if percentages_of_grabbed_areas_list[len(self.time_of_solutions) + 1] >= self.min_percent_for_solve:
                        # Если выполнена, то текущее модельное время - время выполнения записывается в список времени
                        #   решений self.time_of_solutions
                        self.time_of_solutions.append(self.satellites_group.simulation_time)
                # Определение, настало ли время для нового отчета
                if time_from_report_last >= report_time_sec:
                    # Если да, то подается новый отчет
                    self.to_output_report(report_file,
                                          report_time_from_initial_time_in_days,
                                          report_data_about_satellites,
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
                # Если не входит, то модельно время сразу переносится на начало следующего годового периода наблюдения
                new_year = self.satellites_group.simulation_time.year
                if self.observation_period_inside_one_year:
                    new_year += 1
                new_simulation_time = to_determine_date_by_days_number_in_not_leap_year(days_number_in_year, new_year)
                # Если делаются отчеты
                if unit_report_time is not None:
                    # В отчете указывается, когда заканчивается и начинаются периоды наблюдения
                    report_about_observation_period = "".join([str(self.satellites_group.simulation_time),
                                                               ': годовой период наблюдения заканчивается.'
                                                               'Новый период начинается в ',
                                                               str(new_simulation_time), '\n\n'])
                    print(report_about_observation_period)
                    report_file.write(report_about_observation_period)
                    # Если во время вне периода наблюдения настовало время отчета, то отчет делается в начале нового
                    #   периода наблюдений
                    time_from_report_last += (new_simulation_time - self.satellites_group.simulation_time).seconds
                    if time_from_report_last >= report_time_sec:
                        self.to_output_report(report_file,
                                              report_time_from_initial_time_in_days,
                                              report_data_about_satellites,
                                              report_main_data_about_solutions,
                                              report_main_data_about_overflights,
                                              time_unit_of_report,
                                              numerals_count_after_point_in_solutions_and_overflights_report,
                                              to_skip_time_out_of_observation_period,
                                              report_data_about_scanned_area,
                                              report_scanned_area_in_percents,
                                              count_of_numbers_after_point_in_area_report)
                        time_from_report_last % report_time_sec
                # Присвоение нового текущего модельного времени
                self.satellites_group.simulation_time = new_simulation_time
        # Файл с отчетами закрывается, если был открыт
        if report_address is not None:
            report_file.close()

    def to_output_data(self, directory_address, unit_of_output_time, numerals_count_after_point,
                       to_get_main_data_about_solutions=False,
                       to_get_main_data_about_overflights=False,
                       to_get_graph_information_collection_rate_txt=False,
                       to_get_graph_information_collection_rate_pdf=False,
                       to_get_graph_information_collection_rate_jpg=False,
                       to_get_graph_information_volume_txt=False,
                       to_get_graph_information_volume_pdf=False,
                       to_get_graph_information_volume_jpg=False,
                       to_get_histogram_of_solving_period_txt=False,
                       to_get_histogram_of_solving_period_pdf=False,
                       to_get_histogram_of_solving_period_jpg=False,
                       to_get_histogram_of_overflight_period_txt=False,
                       to_get_histogram_of_overflight_period_pdf=False,
                       to_get_histogram_of_overflight_period_jpg=False,
                       to_skip_time_out_of_observation_period_in_periods=False,
                       to_skip_time_out_of_observation_period_in_information_value=False,
                       time_axis_in_units=False,
                       scanned_area_in_percents=False):
        """
        @Описание:
            Метод преобразует данные, собранные методом to_solve_task в:
                среднее, медианное, максимальное, минимальное значениее времени выполнения задачи, дисперсию и
                среднеквадратическое отклонение (далее основные оказатели) и выводит в виде докумена txt;
                гистограмму распределения времении выполнения задачи и выводит в текстовом виде в документе txt, в
                    графичечском виде в документе pdf, jpg;
                основные показатели периодичности пролётов спутников над полигонами и выводит в виде докумена txt;
                гистограмму распределения периода пролётов спутников над полигонами и выводит в текстовом виде в
                    документе txt, в графичечском видиде в документе pdf, jpg;
                график прироста просканированной территории (в м^2 или в %) за выбранный период времени и выводит в
                    текстовом виде в документе txt, в графичечском виде в документе pdf, jpg;
                график просканированной территории (в м^2 или в %)  и выводит в текстовом виде в документе txt, в
                    графичечском виде в документе pdf, jpg.
        :param directory_address: адрес директории, в которую сохраняются выходные данные
        :param unit_of_output_time: единицы измерения времени (см. TimeManagement), в которых будут выводиться выходные,
            связанные со временем.
        :param numerals_count_after_point: количество символов после запятой  для выводимых данных о времени решений
            задачи и периодах между пролетами.
        :param to_get_main_data_about_solutions: вывести осноные данные о времени решений в единицах измерения
            unit_of_output_time, с точностью до numerals_count_after_point знаков после запятой в файл txt (если True,
            если False, то не выводить). По умолчанию False.
        :param to_get_main_data_about_overflights: вывести осноные данные о периоде пролетов спутников из
            self.SatelliteGroup над полигонами self.PolygonsGroup в единицах измерения unit_of_output_time, с точностью
            до numerals_count_after_point знаков после запятой в файл txt (если True, если False, то не выводить). По
            умолчанию False.
        :param to_get_graph_information_collection_rate_txt: вывести зависимость площади просканированной территории за
            текущий шаг времени от времени в виде таблицы в файл txt (если True, если False, то не выводить). По
            умолчанию False.
        :param to_get_graph_information_collection_rate_pdf: вывести зависимость площади просканированной территории за
            текущий шаг времени от времени в виде графика в файл pdf (если True, если False, то не выводить). По
            умолчанию False.
        :param to_get_graph_information_collection_rate_jpg: вывести зависимость площади просканированной территории за
            текущий шаг времени от времени в виде графика в файл jpg (если True, если False, то не выводить). По
            умолчанию False.
        :param to_get_graph_information_volume_txt: вывести зависимость площади просканированной территории от времени в
            виде таблицы в файл txt (если True, если False, то не выводить). По умолчанию False.
        :param to_get_graph_information_volume_pdf: вывести зависимость площади просканированной территории от времени в
            виде графика в файл pdf (если True, если False, то не выводить). По умолчанию False.
        :param to_get_graph_information_volume_jpg: вывести зависимость площади просканированной территории от времени в
            виде графика в файл jpg (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_solving_period_txt: вывести время выполнения задачи в виде гистограммы в файл txt
            (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_solving_period_pdf: вывести время выполнения задачи в виде гистограммы в файл pdf
            (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_solving_period_jpg: вывести время выполнения задачи в виде гистограммы в файл jpg
            (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_overflight_period_txt: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл txt (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_overflight_period_pdf: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл pdf (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_overflight_period_jpg: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл jpg (если True, если False, то не выводить). По умолчанию False.
        :param to_skip_time_out_of_observation_period_in_periods: не учитывать во времени выполнения задачи и времени
            между пролетами спутников периоды, в которые не проводится наблюдение (время вне периода годового
            наблюдения) (если True, если False, то учитывать). По умолчанию False.
        :param to_skip_time_out_of_observation_period_in_information_value: пропускать в данных о просканированной
            площади полигонов периоды, в которые не проводится наблюдение (время вне периода годового наблюдения) (если
            True, если False, то не пропускать). По умолчанию False.
        :param time_axis_in_units: выводить графики площадей просканированной территории от времени с осями времени в
            единицах измерения времени unit_of_output_time и с отсчетом от нуля, где ноль - налальное модельное время
            (self.initial_simulation_time) (если True, если False, то ось в модельном времени UTC). По умолчанию False.
        :param scanned_area_in_percents: выводить графики площадей просканированной территории от времени с осями
            площадей в процентах площади просканированной территории от полной площади полигонов self.PolygonsGroup
            (если True, если False, то ось кв. метрах). По умолчанию False.
        :return: сохраняет в директрию directory_address ... - см. описание
        """
        # Будет ли выводиться зависимость просканированной площади за шаг времени от времени в каком-либо виде
        if to_get_graph_information_collection_rate_txt or \
                to_get_graph_information_collection_rate_pdf or \
                to_get_graph_information_collection_rate_jpg:
            to_get_graph_information_collection_rate = True
        else:
            to_get_graph_information_collection_rate = False
        # Будет ли выводиться зависимость просканированной площади от времени в каком-либо виде
        if to_get_graph_information_volume_txt or \
                to_get_graph_information_volume_pdf or \
                to_get_graph_information_volume_jpg:
            to_get_graph_information_volume = True
        else:
            to_get_graph_information_volume = False
        # Будет ли выводиться гистограмма времени между решениями в каком-либо виде
        if to_get_histogram_of_solving_period_txt or \
                to_get_histogram_of_solving_period_pdf or \
                to_get_histogram_of_solving_period_jpg:
            to_get_histogram_of_solving_period = True
        else:
            to_get_histogram_of_solving_period = False
        # Будет ли выводиться гистограмма времени между пролетами спутников над полигонами в каком-либо виде
        if to_get_histogram_of_overflight_period_txt or \
                to_get_histogram_of_overflight_period_pdf or \
                to_get_histogram_of_overflight_period_jpg:
            to_get_histogram_of_overflight_period = True
        else:
            to_get_histogram_of_overflight_period = False
        # Если на осях времени в графиках отображаются единицы измерения времени, в которых будет выводиться информация
        #   о времени, то задается символ единицы измеерения, если нет, то вместо символа - обозначение формата времени
        #   "yyyy-MM-dd hh:mm:ss"
        if time_axis_in_units:
            unit_symbol = unit_in_symbol(unit_of_output_time)
        else:
            unit_symbol = "yyyy-MM-dd hh:mm:ss"
        # Вычисление периодов между решениями задачи по списку времени выполнения self.time_of_solutions
        periods_of_solutions = []
        if to_get_main_data_about_solutions or to_get_histogram_of_solving_period:
            periods_of_solutions = self.to_identify_periods_sec(self.time_of_solutions, self.initial_simulation_time,
                                                                to_skip_time_out_of_observation_period_in_periods)
        # Вычисление периодов между пролетами спутников над исследуемыми полигонами по списку времени сканирования
        #   self.time_of_growth_of_information
        periods_of_overflight = []
        if (to_get_main_data_about_overflights or to_get_histogram_of_overflight_period) and \
                self.time_of_growth_of_information is not []:
            time_of_growth_of_information = self.time_of_growth_of_information
            time_of_overflights = []
            # Вычисление времен появления спутников над полигонами и начала сканирования и запись этого времени в список
            #   time_of_overflights
            initial_time_of_overflight = time_of_growth_of_information[0]
            for i in range(1, len(time_of_growth_of_information)):
                if (time_of_growth_of_information[i] - time_of_growth_of_information[i - 1]).total_seconds() > \
                        self.step:
                    time_of_overflights.append(initial_time_of_overflight)
                    initial_time_of_overflight = time_of_growth_of_information[i]
            time_of_overflights.append(initial_time_of_overflight)
            # Вычсление периодов
            periods_of_overflight = self.to_identify_periods_sec(time_of_overflights, self.initial_simulation_time,
                                                                 to_skip_time_out_of_observation_period_in_periods)
        # Если выводятся основные показатели периодичности решений или пролетов...
        if to_get_main_data_about_solutions or to_get_main_data_about_overflights:
            # Вычисление полного модельного времени (времени моделирования)
            overall_time_of_simulation_sec = seconds_to_unit((self.final_simulation_time -
                                                              self.initial_simulation_time).total_seconds(),
                                                             unit_of_output_time)
            # Вывод основный данных о времени между решениями в файл txt, если это требуется, в виде:
            #   Основные показатели периодичности выполнения задачи 'название задачи'
            #       Средний период:         '**.**' 'u'
            #       Медианный период:       '**.**' 'u'
            #       Максимальный период:    '**.**' 'u'
            #       Минимальный период:     '**.**' 'u'
            #       Дисперсия:              '**.**' 'u'
            #       Среднее кв. отклнение:  '**.**' 'u'
            #       Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
            if to_get_main_data_about_solutions:
                main_data_solutions_file = open("".join([directory_address, '/', self.name,
                                                         ' - основные показатели периодичности выполнения задачи (',
                                                         unit_symbol, ').txt']), 'w')
                main_data_solutions_file.write("".join(['Основные показатели периодичности выполнения задачи ',
                                                        str(self.name), '\n', self.to_get_information_about_task(),
                                                        self.to_get_main_data_about_periods
                                                        (periods_of_solutions, unit_of_output_time,
                                                         numerals_count_after_point, overall_time_of_simulation_sec)]))
                main_data_solutions_file.close()
            # Вывод основный данных о времени между пролетами в файл txt, если это требуется, в виде:
            #   Основные показатели периодичности пролетов спутника 'название задачи'
            #       Средний период:         '**.**' 'u'
            #       Медианный период:       '**.**' 'u'
            #       Максимальный период:    '**.**' 'u'
            #       Минимальный период:     '**.**' 'u'
            #       Дисперсия:              '**.**' 'u'
            #       Среднее кв. отклнение:  '**.**' 'u'
            #       Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
            if to_get_main_data_about_overflights:
                main_data_overflights_file = open("".join([directory_address, '/', self.name,
                                                           ' - основные показатели периодичности пролетов спутников (',
                                                           unit_symbol, ').txt']), 'w')
                main_data_overflights_file.write("".join(['Основные показатели периодичности пролетов спутника ',
                                                          str(self.name), '\n\n', self.to_get_information_about_task(),
                                                          self.to_get_main_data_about_periods
                                                          (periods_of_overflight,
                                                           unit_of_output_time,
                                                           numerals_count_after_point,
                                                           overall_time_of_simulation_sec)]))
                main_data_overflights_file.close()
        # Если выводится график площади за шаг от времени или график просканированной площади за все время от времени...
        if to_get_graph_information_collection_rate or to_get_graph_information_volume:
            # Если площадь выводится в процентах от общей площади исследуеммых полигонов, то список
            #   self.growth_of_information переводится в проценты, а символом в представлениях данных становится '% '
            if scanned_area_in_percents:
                symbol_of_units_of_information = '%'
                growth_of_information = []
                for value in self.growth_of_information:
                    growth_of_information.append(value / self.polygons_group.full_area)
            else:
                # Если нет, то символом становится 'кв. м'
                symbol_of_units_of_information = 'кв. м'
                growth_of_information = self.growth_of_information
            # Составление осей графика площади за шаг от времени
            information_collection_rate_axis, time_axis = self.to_make_axis(
                growth_of_information,
                self.time_of_growth_of_information,
                to_skip_time_out_of_observation_period_in_information_value,
                unit_of_output_time,
                time_axis_in_units)
            # Если зависимость выводится в каком-либо виде...
            if to_get_graph_information_collection_rate:
                # Подготовка заголовков
                graph_title = "".join(['График притока информации (', symbol_of_units_of_information, ') от времени (',
                                       unit_symbol, ')'])
                graph_address = "".join([directory_address, '/', self.name, ' - график притока информации (',
                                         symbol_of_units_of_information, ') от времени (', unit_symbol, ')'])
                # Вывод зависимости в виде таблицы в файле txt, если требуется
                if to_get_graph_information_collection_rate_txt:
                    table_information_volume_file = open("".join([graph_address, '.txt']), 'w')

                    table_information_volume_file.write("".join([graph_title, '\n\n',
                                                                 self.to_get_information_about_task(), unit_symbol,
                                                                 '\t\t', symbol_of_units_of_information, '\n']))
                    for i in range(0, len(information_collection_rate_axis)):
                        table_information_volume_file.write("".join([str(time_axis[i]), '\t\t',
                                                                     str(information_collection_rate_axis[i]), '\n']))
                # Если предполагается вывод зависимости в виде графиков, то график строится с заголовком и названием
                #   осей
                if to_get_graph_information_collection_rate_jpg or to_get_graph_information_collection_rate_pdf:
                    graph_information_collection_rate = plt.figure()
                    plt.plot(time_axis, information_collection_rate_axis, color='blue')
                    plt.axis([time_axis[0], time_axis[-1], information_collection_rate_axis[0],
                              information_collection_rate_axis[-1]])

                    plt.title(graph_title)
                    plt.ylabel("".join(['Информация (', symbol_of_units_of_information, ')']))
                    plt.xlabel("".join(['Время (', unit_symbol, ')']))
                    plt.grid(True)
                    # Вывод зависимости в виде графика в файле jpg, если требуется
                    if to_get_graph_information_collection_rate_jpg:
                        graph_information_collection_rate.savefig("".join([graph_address, '.jpg']))
                    # Вывод зависимости в виде графика в файле pdf, если требуется
                    if to_get_graph_information_collection_rate_pdf:
                        graph_information_collection_rate.savefig("".join([graph_address, '.pdf']))
                    plt.close()
            # Если зависимость площади сканированной территории выводится в каком-либо виде
            if to_get_graph_information_volume:
                # Интегрируются значение зависимости просканированной площади за шаг от времени и получается зависимость
                #    общей площади от того же времени
                information_volume_axis = self.to_sum_values_on_axis(information_collection_rate_axis)
                # Подготовка заголовков
                graph_title = "".join(['График собранной информации (', symbol_of_units_of_information,
                                       ') от времени (', unit_symbol, ')'])
                graph_address = "".join([directory_address, '/', self.name, ' - график собранной информации (',
                                         symbol_of_units_of_information, ') от времени (', unit_symbol, ')'])
                # Вывод зависимости в виде таблицы в файле txt, если требуется
                if to_get_graph_information_collection_rate_txt:
                    table_information_volume_file = open("".join([graph_address, '.txt']), 'w')

                    table_information_volume_file.write("".join([graph_title, '\n\n',
                                                                 self.to_get_information_about_task(), unit_symbol,
                                                                 '\t\t', symbol_of_units_of_information, '\n']))
                    for i in range(0, len(information_volume_axis)):
                        table_information_volume_file.write("".join([str(time_axis[i]), '\t\t',
                                                                     str(information_volume_axis[i]), '\n']))
                # Если предполагается вывод зависимости в виде графиков, то график строится с заголовком и названием
                #   осей
                if to_get_graph_information_collection_rate_jpg or to_get_graph_information_collection_rate_pdf:
                    graph_information_collection_rate = plt.figure()
                    plt.plot(time_axis, information_volume_axis, color='purple')
                    plt.axis([time_axis[0], time_axis[-1], information_volume_axis[0],
                              information_volume_axis[-1]])

                    plt.title(graph_title)
                    plt.ylabel("".join(['Информация (', symbol_of_units_of_information, ')']))
                    plt.xlabel("".join(['Время (', unit_symbol, ')']))
                    plt.grid(True)
                    # Вывод зависимости в виде графика в файле jpg, если требуется
                    if to_get_graph_information_collection_rate_jpg:
                        graph_information_collection_rate.savefig("".join([graph_address, '.jpg']))
                    # Вывод зависимости в виде графика в файле pdf, если требуется
                    if to_get_graph_information_collection_rate_pdf:
                        graph_information_collection_rate.savefig("".join([graph_address, '.pdf']))
                    plt.close()
        # Если выводится гистограмма периодов решений задачи в каком-либо виде
        if to_get_histogram_of_solving_period:
            # Построение гистограммы периодов решений
            histogram_of_solving_periods = self.to_make_histogram(periods_of_solutions, unit_of_output_time)
            # Подготовка заголовков и подписей осей
            histogram_title = "".join(['Гистограмма распределения решений (', unit_symbol, ')'])
            histogram_address = "".join([directory_address, '/', self.name, ' - гистограмма распределения решений (',
                                         unit_symbol, ')'])
            x_label = "".join(['Период выполнения задачи (', unit_symbol, ')'])
            y_label = 'Количество решений'
            # Вывод гистограммы в файле txt, если требуется
            if to_get_histogram_of_solving_period_txt:
                histogram_of_solutions_file = open("".join([histogram_address, '.txt']), 'w')

                histogram_of_solutions_file.write("".join([histogram_title, '\n\n',
                                                           self.to_get_information_about_task(), x_label, '\t\t\t\t',
                                                           y_label, '\n']))
                for i in range(0, len(histogram_of_solving_periods)):
                    histogram_of_solutions_file.write("".join([str(i), '\t\t\t\t', str(histogram_of_solving_periods[i]),
                                                               '\n']))
                histogram_of_solutions_file.close()
            # Если гистограмма выводится в графическом виде
            if to_get_histogram_of_solving_period_jpg or to_get_histogram_of_solving_period_pdf:
                # Построение гистограммы в графическом виде
                hist_of_solving_periods = plt.figure()
                plt.hist(histogram_of_solving_periods, color='red')
                plt.axis([0, len(histogram_of_solving_periods), 0, max(histogram_of_solving_periods)])
                plt.title(histogram_title)
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                # Вывод гистограммы в файле jpg, если требуется
                if to_get_histogram_of_solving_period_jpg:
                    hist_of_solving_periods.savefig("".join([histogram_address, '.jpg']))
                # Вывод гистограммы в файле pdf, если требуется
                if to_get_histogram_of_solving_period_pdf:
                    hist_of_solving_periods.savefig("".join([histogram_address, '.pdf']))
                plt.close()
        # Если выводится гистограмма периодов пролетов спутников над полигонами в каком-либо виде
        if to_get_histogram_of_overflight_period:
            # Построение гистограммы периодов решений
            histogram_of_overflight_periods = self.to_make_histogram(periods_of_overflight, unit_of_output_time)
            # Подготовка заголовков и подписей осей
            histogram_title = "".join(['Гистограмма распределения пролетов (', unit_symbol, ')'])
            histogram_address = "".join([directory_address, '/', self.name, ' - гистограмма распределения пролетов (',
                                         unit_symbol, ')'])
            x_label = "".join(['Период пролетов (', unit_symbol, ')'])
            y_label = 'Количество пролетов'
            # Вывод гистограммы в файле txt, если требуется
            if to_get_histogram_of_overflight_period_txt:
                histogram_of_overflight_file = open("".join([histogram_address, '.txt']), 'w')

                histogram_of_overflight_file.write("".join([histogram_title, '\n\n',
                                                            self.to_get_information_about_task(), x_label, '\t\t\t\t',
                                                            y_label, '\n']))

                for i in range(0, len(histogram_of_overflight_periods)):
                    histogram_of_overflight_file.write("".join([str(i), '\t\t\t\t',
                                                                str(histogram_of_overflight_periods[i]), '\n']))

                histogram_of_overflight_file.close()
            # Если гистограмма выводится в графическом виде
            if to_get_histogram_of_overflight_period_jpg or to_get_histogram_of_overflight_period_pdf:
                hist_of_overflight_periods = plt.figure()
                plt.hist(histogram_of_overflight_periods, color='green')
                plt.axis([0, len(histogram_of_overflight_periods), 0, max(histogram_of_overflight_periods)])

                plt.title(histogram_title)
                plt.xlabel("".join(['Период пролетов (', unit_symbol, ')']))
                plt.ylabel('Количество пролетов')
                # Вывод гистограммы в файле jpg, если требуется
                if to_get_histogram_of_solving_period_jpg:
                    hist_of_overflight_periods.savefig("".join([histogram_address, '.jpg']))
                # Вывод гистограммы в файле pdf, если требуется
                if to_get_histogram_of_solving_period_pdf:
                    hist_of_overflight_periods.savefig("".join([histogram_address, '.pdf']))
                plt.close()

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
        # Производится очистка собранных данных, чтобы выходная информация не отличалась от пааметров задачи
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
        self.collecting_satellites = []
        self.time_of_growth_of_information = []
        self.time_of_solutions = []

    def to_output_report(self, report_file=None,
                         time_from_initial_time_in_days=True,
                         data_about_satellites=True,
                         data_about_solutions=True,
                         data_about_overflights=True,
                         time_unit='days',
                         numerals_count_after_point_in_solutions_and_overflights_report=2,
                         to_skip_time_out_of_observation_period=False,
                         data_about_scanned_area=True,
                         scanned_area_in_percents=True,
                         count_of_numbers_after_point_in_area_report=0):
        """
        @Описание:
            Метод выводит отчет о координатах спутников группы self.satellite_group, о решениях задачи, о пролетах
                спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
                некоторой заданной периодичностью модельного времени. Отчёт выводится в консоль и в файл по заданному
                адресу, если он был задан.
        :param report_file: адрес файла txt, в который будут выводиться отчёты. Если задано None, запись
            отчётов в файл не производится (String, допустимо None).
        :param time_from_initial_time_in_days: написать в отчете время от начального модельного времени до текущего в
            днях (boolean). По умолчанию True.
        :param data_about_satellites: написать в отчете координаты каждого спутника в текущее модельное время (boolean).
            По умолчанию True.
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
            территориях (int). По умолчанию 0.
        :return: выводит в консоль и в файл txt по адресу report_file отчет, составляемый с помощью метода
            self.to_make_report
        """
        # Текст отчета составляется с помощью метода self.to_make_report
        report = self.to_make_report(time_from_initial_time_in_days,
                                     data_about_satellites,
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

    def to_make_report(self, time_from_initial_time_in_days=True,
                       data_about_satellites=True,
                       data_about_solutions=True,
                       data_about_overflights=True,
                       time_unit='days',
                       numerals_count_after_point_in_solutions_and_overflights_report=2,
                       to_skip_time_out_of_observation_period=False,
                       data_about_scanned_area=True,
                       scanned_area_in_percents=True,
                       count_of_numbers_after_point_in_area_report=0):
        """
        @Описание:
            Метод составляет отчет о координатах спутников группы self.satellite_group, о решениях задачи, о пролетах
                спутников над полигонами self.polygons_group, о площади просканированнной территории полигонов с
                некоторой заданной периодичностью модельного времени.
        :param time_from_initial_time_in_days: написать в отчете время от начального модельного времени до текущего в
            днях (boolean). По умолчанию True.
        :param data_about_satellites: написать в отчете координаты каждого спутника в текущее модельное время (boolean).
            По умолчанию True.
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
            территориях (int). По умолчанию 0.
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
                Среднее кв. отклнение:  '**.**' 'u'
                Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
            Основные показатели периодичности пролетов на текущий момент:
                Средний период:         '**.**' 'u'
                Медианный период:       '**.**' 'u'
                Максимальный период:    '**.**' 'u'
                Минимальный период:     '**.**' 'u'
                Дисперсия:              '**.**' 'u'
                Среднее кв. отклнение:  '**.**' 'u'
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
        # Время от начального модельного времени до текущего в днях
        if time_from_initial_time_in_days:
            str_addition_time_report = "".join([' - ', str(round((current_time - self.initial_simulation_time).
                                                                 total_days())), 'дней от начального времени'])
        else:
            str_addition_time_report = ''
        # Отчет о состоянии спутников в группе self.satellite_group
        if data_about_satellites:
            str_satellites_data = ['Состояние спутников:\n']
            for satellite in self.satellites_group.satillites_list:
                str_satellites_data.append("".join(['\t', str(satellite.name), ':\t',
                                                    str(satellite.satellite_coordinates_set), '\n']))
            "".join(str_satellites_data)
        else:
            str_satellites_data = ''

        if data_about_solutions or data_about_overflights:
            # Вычисление времени от начального модельного времени до текущего в секундах
            current_time_of_simulation = (current_time - self.initial_simulation_time).total_seconds()
            # Отчет о решении задачи на текущий момент модельного времени
            if data_about_solutions:
                # Вычисление периодов между соседними решениями задачи (или от начального модельного времени)
                periods_of_solutions = self.to_identify_periods_sec(self.time_of_solutions,
                                                                    self.initial_simulation_time,
                                                                    to_skip_time_out_of_observation_period)
                # Запись данных о решениях и о их времени
                str_solutions_report = \
                    "".join(['Основные показатели периодичности решений на текущий момент:\n',
                             self.to_get_main_data_about_periods(
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
                time_of_overflights = self.to_define_initial_times_of_scan_session()
                # Вычисление периодов между соседними пролетами (или от начального модельного времени)
                periods_of_overflight = self.to_identify_periods_sec(time_of_overflights,
                                                                     self.initial_simulation_time,
                                                                     to_skip_time_out_of_observation_period)
                # Запись данных о пролетах и о их времени
                str_overflights_report = \
                    "".join(['Основные показатели периодичности пролетов на текущий момент:\n',
                             self.to_get_main_data_about_periods(
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
            scanned_area_list = \
                round(self.polygons_group.to_calc_percentages_of_grabbed_areas(scanned_area_in_percents),
                      count_of_numbers_after_point_in_area_report)
            # Вывод процентах или кв. м.
            if scanned_area_in_percents:
                for i in range(0, len(scanned_area_list)):
                    str_scanned_area.append("".join(['\t', str(i + 1), ' раз просканированно ',
                                                     str(scanned_area_list[i]), '% исследуемой территории\n']))
                "".join(str_scanned_area)
            else:
                for i in range(0, len(scanned_area_list)):
                    str_scanned_area.append("".join(['\t', str(i + 1), ' раз просканированно ',
                                                     str(scanned_area_list[i]), ' м^2 исследуемой территории\n']))
                "".join(str_scanned_area)
        else:
            str_scanned_area = ''
        # Сшивание частей отчета
        str_report = [str_time_report, str_addition_time_report, '\n', str_satellites_data, str_solutions_report,
                      str_overflights_report, str_scanned_area, '\n']
        return str_report

    def to_define_initial_times_of_scan_session(self):
        """
        @Описание:
            Метод определяет модельное время всех пролётов на данный момент (начала сессии скаирования).
        :return: список объектов datetime - модельного времени всех пролётов на данный момент (начала сессии
            скаирования)
        """
        time_of_growth_of_information = self.time_of_growth_of_information
        # Массив модельного времени пролетов
        time_of_overflights = []
        # Начальное время первого пролёта
        initial_time_of_overflight = time_of_growth_of_information[0]
        # Вычисление времен начала пролетов. Началом пролета считается то время, когда сбор данных только начался, а до
        #   этого был нулевым
        for i in range(1, len(time_of_growth_of_information)):
            if (time_of_growth_of_information[i] - time_of_growth_of_information[i - 1]).total_seconds() > \
                    self.step:
                time_of_overflights.append(initial_time_of_overflight)
                initial_time_of_overflight = time_of_growth_of_information[i]
        time_of_overflights.append(initial_time_of_overflight)
        return time_of_overflights

    def to_get_main_data_about_periods(self, periods, unit_of_output_time, numerals_count_after_point,
                                       overall_time_of_modeling):
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
            Среднее кв. отклнение:  '**.**' 'u'
            Всего за время моделирования - '**.**' 'u' - было сделано '**' измерений
        """
        # Символ - обозначение единицы измерения времени unit_of_output_time
        unit_symbol = unit_in_symbol(unit_of_output_time)
        # Если список значений periods не пустой, вычисляются "основные" параметры
        if periods is not []:
            # Вычисление выходных параметров  с помощью метода to_determine_median_average_max_min_dispersion_standard
            average_period_value, median_period_value, max_period_value, min_period_value, dispersion_period_value,\
                standard_deviation_period_value = self.to_determine_median_average_max_min_dispersion_standard(periods)
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
            '\tСредний период:\t\t\t', str(average_period_value), unit_symbol, '\n',
            '\tМедианный период:\t\t', str(median_period_value), unit_symbol, '\n',
            '\tМаксимальный период:\t', str(max_period_value), unit_symbol, '\n',
            '\tМинимальный период:\t\t', str(min_period_value), unit_symbol, '\n',
            '\tДисперсия:\t\t\t\t', str(dispersion_period_value), unit_symbol, '\n',
            '\tСреднее кв. отклнение:', str(standard_deviation_period_value), unit_symbol, '\n',
            '\tВсего за время моделирования - ', str(overall_time_of_modeling), ' ', unit_symbol,
            ' - было сделано ', str(len(periods)), ' измерений'])
        return str_data_about_periods

    @staticmethod
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
        average_value = statistics.mean(numbers)
        median_value = statistics.median(numbers)
        max_value = max(numbers)
        min_value = min(numbers)
        dispersion = statistics.pvariance(numbers)
        standard_deviation = statistics.pstdev(numbers)
        return average_value, median_value, max_value, min_value, dispersion, standard_deviation

    def to_get_information_about_task(self):
        """
        @Описание:
            Метод возвращает некоторые данные о выполняемой задаче - о объекте self - в виде строки.
                Это следующие данные:
                    название задачи self.name;
                    начальное и конечное модельное время self.initial_annual_observation_period и
                        self.final_annual_observation_period;
                    шаг изменения модельного времени self.step;
                    список спутников, выполняющих задачу self.satellites_group.satellites_list;
                    границы допустимого периода наблюдения self.initial_annual_observation_period и
                        self.final_annual_observation_period, если он задан;
                    максимально допустимый зенитный угол Солнца self.max_zenith_angle;
                    максимально допустимый балл облачности self.max_cloud_score.

        :return: строка данных (String) в виде:
            Основные параметры задачи 'name'
                Модельное время:                                от 'yyyy-MM-dd hh:mm:ss' до 'yyyy-MM-dd hh:mm:ss'
                Шаг изменения модельного времени:               'step' с
                Спутники, выполняющие задачу:                   'satellite_1', 'satellite_2', 'satellite_3', ...
                Допустимый период наблюдения:                   от 'ddd' дня до 'ddd' дня (или 'не задан')
                Максимально допустимый зенитный угол Солнца:    'uu'°
                Максимально допустимый балл облачности:         'sss'
        """
        # Запись списка спутников self.satellites_group.satellites_list в строку
        str_satellites = []
        for satellite in self.satellites_group.satellites_list:
            str_satellites.append("".join([satellite.name, ', ']))
        "".join(str_satellites)
        # Удаление запятой в конце строчного списка спутников
        str_satellites = str_satellites[:-2]
        # Запись границ годового периода наблюдений в строку, если он задан и 'не задан', если не задан
        if self.initial_annual_observation_period == DEFAULT_INITIAL_ANNUAL_OBSERVATION_PERIOD and \
                self.final_annual_observation_period == DEFAULT_FINAL_ANNUAL_OBSERVATION_PERIOD:
            str_annual_observation = 'не задан'
        else:
            str_annual_observation = "".join(['от ', str(self.initial_annual_observation_period), ' дня до ',
                                              str(self.final_annual_observation_period), ' дня'])
        # Запись информации в строку
        str_info = "".join([
            'Основные параметры задачи\t\t\t\t\t', str(self.name), '\n',
            '\tМодельное время:\tот ', str(self.initial_simulation_time), ' до ', str(self.final_simulation_time), '\n',
            '\tШаг изменения модельного времени:\t\t\t\t', str(self.step), ' с\n',
            '\tСпутники, выполняющие задачу:\t\t\t\t\t', str_satellites, '\n',
            '\tДопустимый период наблюдения:\t\t\t\t\t', str_annual_observation, '\n',
            '\tМаксимально допустимый зенитный угол Солнца\t: ', str(self.max_zenith_angle), '°\n',
            '\tМаксимально допустимый балл облачности:\t\t\t', str(self.max_cloud_score), '\n\n'])
        return str_info

    def to_identify_periods_sec(self, time_list, first_time=None, to_skip_time_out_of_observation_period=False):
        """
        @Описание:
            Метод определяет время от времени начала наблюдения до первого значения времени из заданного списка и между
                соседними значениями времени из заданного списка в секундлах. Возможно вычисление периодов только по
                допустимому времени наблюдения.
        :param time_list: список значений времени, по которому будут вычисляться (date_time).
        :param first_time: начальное время наблюдений, от которого будет отсчитываться первый период (datetime).
               Допустимо None. При этом сразу вычисляются периоды между значениями time_list. По умолчанию None.
        :param to_skip_time_out_of_observation_period: пропускать промежутки времени, не входящие в годовые периоды
               наблюдения (boolean). По умолчанию False.
        :return: список приодов в секундах (int, double)
        """
        # Если нету пары значений времени (начального времени first_time и одного значения из time_list или два значения
        #   из time_list), то возвращается 0, а дальнейшие вычисления не производятся. Если есть, то задаётся первое
        #   значение времени, от которого будет вестись отсчет - previous_time.
        if first_time is not None:
            if len(time_list > 0):
                previous_time = first_time
            else:
                return [0]
        else:
            if len(time_list > 1):
                previous_time = time_list[0]
                del time_list[0]
            else:
                return [0]
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
            # Вычисление даты начала годового периода наблюдения
            current_year = time_list[0].year
            start_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                self.initial_annual_observation_period, current_year)
            end_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                self.final_annual_observation_period, current_year)
            # Если previous_time оказывается не в периоде наблюдения, оно перемещается на начало следующего периода
            if self.observation_period_inside_one_year:
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
            if self.observation_period_inside_one_year:
                for time in time_list:
                    current_year = time.year
                    year_of_previous_time = previous_time.year
                    skipped_time = 0
                    year_of_skipped_period = current_year
                    # Вычисление времени, не входящего в период наблюдения
                    while year_of_skipped_period > year_of_previous_time:
                        start_of_new_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                            self.initial_annual_observation_period, year_of_skipped_period)
                        end_of_old_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                            self.final_annual_observation_period, year_of_skipped_period - 1)
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
                    if day_of_time_in_year >= self.initial_annual_observation_period:
                        year_of_not_observing_period = previous_time.year + 1
                    else:
                        year_of_not_observing_period = previous_time.year
                    end_of_current_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                        self.final_annual_observation_period, year_of_not_observing_period)
                    skipped_time = 0
                    time_copy = time
                    # Вычисление времени, не входящего в период наблюдения
                    while time_copy >= end_of_current_observation_period:
                        day_of_time_copy_in_year = to_determine_days_number_in_not_leap_year(previous_time)
                        if day_of_time_copy_in_year >= self.initial_annual_observation_period:
                            year_of_skipped_period = previous_time.year
                        else:
                            year_of_skipped_period = previous_time.year - 1
                        start_of_new_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                            self.initial_annual_observation_period, year_of_skipped_period)
                        end_of_old_observation_period = to_determine_date_by_days_number_in_not_leap_year(
                            self.final_annual_observation_period, year_of_skipped_period)
                        skipped_time += (start_of_new_observation_period - end_of_old_observation_period). \
                            total_seconds()
                        time_copy = to_determine_date_by_days_number_in_not_leap_year(
                            to_determine_days_number_in_not_leap_year(time_copy), time_copy.year - 1)
                    # Вычисление периода без времени, не входящего в период наблюдения
                    period = (time - previous_time).total_seconds() - skipped_time
                    periods.append(period)
                    previous_time = time
        return periods

    def to_make_axis(self, values, times, unit_of_time, to_skip_time_out_of_observation_period=False,
                     time_axis_in_units=False):
        """
        @Описание:
            Метод принимает список чисел и список соответствующих им значений времени. Числа группируются по времени с
                шагом в одну заданную единицу измерения времени и суммируются. На выход подается список сумм чисел и
                список значений времени, соответсвующих суммам (началу отсчета времени для группы) или отсчеты заданных
                единиц измерения времени от первого - нулевого значения.
        :param values: список начений (int, double)
        :param times: список значений времени (datetime)
        :param unit_of_time: единицы измерения времен (см. файл TimeManagement) (String)
        :param to_skip_time_out_of_observation_period: пропускать промежутки времени, не входящие в годовые периоды
               наблюдения (boolean). По умолчанию False.
        :param time_axis_in_units: выводить список времени для просуммированных значений в виде отсчетов единиц
               измерения unit_of_time времени от первого - нулевого значения (boolean). Иначе выводить в виде значений
               времени datetime.  По умолчанию False.
        :return:
            value_axis: список чисел - сумм чисел из values по времени times с шагом в один unit_of_time (int, double).
            time_axis: список времени с шагом в один unit_of_time, соответствует value_axis (datetime или int).
        """
        # Начальное и конечное время вычислений
        initial_time = self.initial_simulation_time
        final_time = self.final_simulation_time
        # Вычисление шага времени, по которому будет суммирование в секундах
        step = to_get_unit_in_seconds(unit_of_time)
        # Добавление в times начального времени моделирования, а в values нуля, если это время отсуттствует
        if initial_time < times[0]:
            values.insert(0, 0)
            times.insert(0, initial_time)
        # Добавление в times конечного времени моделирования, а в values нуля, если это время отсуттствует
        if final_time > times[-1]:
            values.append(0)
            times.append(final_time)
        # Новые списки
        value_axis = []
        time_axis = []
        # previous_time - начальное время периода, по которому будет производиться суммрование
        previous_time = times[0]
        # current_time - конечное время периода, по которому будет производиться суммрование
        current_time = previous_time + timedelta(seconds=step)
        # Суммирование в цикле
        i = 0
        while current_time <= times[-1]:
            sum_for_unit = 0
            while (times[i] >= previous_time) and (times[i] < current_time):
                sum_for_unit += values[i]
                i += 1
            # Запись суммы и времени
            value_axis.append(sum_for_unit)
            time_axis.append(current_time)
            # Переход к следующему периоду
            previous_time = current_time
            current_time += timedelta(seconds=step)
        # Убирает значения, соответствующие времени вне периода наблюдения
        if to_skip_time_out_of_observation_period:
            i = 0
            # Начало и конец периодов наблюдения (в днях в невисокосном году)
            initial_annual_observation_period = self.initial_annual_observation_period
            final_annual_observation_period = self.final_annual_observation_period
            # Цикл по всему time_axis
            while i < len(time_axis):
                day_number = to_determine_days_number_in_not_leap_year(times[i])
                current_day_between_borders_of_annual_observation_period =\
                    initial_annual_observation_period < day_number < final_annual_observation_period
                current_day_in_observation_period = (not self.observation_period_inside_one_year or
                                                     current_day_between_borders_of_annual_observation_period) and \
                                                    (self.observation_period_inside_one_year or
                                                     not current_day_between_borders_of_annual_observation_period) or \
                    day_number == initial_annual_observation_period or \
                    day_number == final_annual_observation_period

                if not current_day_in_observation_period:
                    i = i + 1
                else:
                    # Удаление лишних значений
                    del values[i]
                    del times[i]
        # Перевод времени datetime в единицы измерения времени unit_of_time
        if time_axis_in_units:
            initial_time = times[0]
            for i in range(0, len(times)):
                times[i] = (times[i] - initial_time).total_seconds() / step

        return value_axis, time_axis

    @staticmethod
    def to_sum_values_on_axis(axis):
        """
        @Описание:
            Суммирование каждого значения заданного списка со всеми прдыдущими (интегрирование)
        :param axis: список значений, по которым проводится суммирование (int, double)
        :return: проинтегрированный список (int, double)
        """
        summed_axis = [axis[0]]
        for i in range(1, len(axis)):
            summed_axis.append(axis(i) + summed_axis[i - 1])
        return summed_axis

    @staticmethod
    def to_make_histogram(values, unit_of_time):
        """
        @Описание:
            Метод создает гистограмму из списка значений с шагом в одну заданную единицу измерения времени.
        :param values: список значений, по которым составляется гистограмма
        :param unit_of_time: единица измерения времени (см. файл TimeManagement), в которых будит измеряться время в
            гистограмме и по которой будет определяться шаг времени
        :return: список, соответствующей вычисленной гистограмме
        """
        # Перевод единиц измерения unit_of_time в секунды
        step = to_get_unit_in_seconds(unit_of_time)
        # Определение максимума гистограммы по времени в секундах
        max_value = (max(values) // step) * step + step
        # Перевод максимума гистограммы по времени из секунд в unit_of_time
        histogram_len = int(max_value // step)
        # Составление гистограммы
        histogram = [0] * histogram_len
        for value in values:
            index = int(value // step)
            histogram[index] += 1
        return histogram
