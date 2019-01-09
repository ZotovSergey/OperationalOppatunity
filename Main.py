from Task import Task
from SatellitesGroup import SatellitesGroup
from PolygonsGroup import PolygonsGroup
from EarthEllipsoid import EarthEllipsoid
from datetime import datetime

if __name__ == '__main__':
    # Создание объекта - эллипсоида Земли по умолчанию. Эллипсоид по умолчанию - это эллипсоид из WGS-84.
    earth_ellipsoid = EarthEllipsoid()
    print("".join(["Эллипсоид Земли\n", earth_ellipsoid.to_str()]))

    # Входные данные для спутников
    #   ISS №1:
    #       Название в базе NORAD
    ISS_name = 'ISS (ZARYA)'
    #       Адрес файла с данными TLE
    ISS_tle = 'D://TLE//tle.txt'
    #       Угол обзора бортового прибора (градусы)
    ISS_angle_of_view = 3.5

    # Создание объекта - спутниковой группировки, с помощью которой будет выполняться задача. Спутники satellite_group
    #   вращаются вокруг эллипсоида Земли earth_ellipsoid
    satellite_group = SatellitesGroup(earth_ellipsoid)
    # Добавление спутника №1 (ISS) в группу
    satellite_group.to_add_satellite(ISS_name, ISS_tle, ISS_angle_of_view)
    print("".join(["\nСпутники в группе:\n", str(satellite_group)]))

    # Входные данные для полигонов
    #   Мелкость разбиения по широте и долготе в градусах широты и долготы
    lat_fineness = 0.005
    long_fineness = 0.005
    #   Таблица распределений количества облаков по месяцам
    common_cloudiness_distr_table = \
        [[0.03977273, 0.05397727, 0.07954545, 0.10795455, 0.11647727, 0.12215909, 0.13068182, 0.10795455, 0.10511364,
          0.07954545, 0.05681818],
         [0.01880878, 0.10658307, 0.10031348, 0.12225705, 0.13479624, 0.14106583, 0.12539185, 0.06583072, 0.10031348,
          0.06583072, 0.01880878],
         [0.03977273, 0.06818182, 0.13920455, 0.13636364, 0.14488636, 0.09943182, 0.14488636, 0.08806818, 0.06818182,
          0.04261364, 0.02840909],
         [0.01466276, 0.05571848, 0.10557185, 0.12609971, 0.15542522, 0.15835777, 0.18181818, 0.1026393, 0.07038123,
          0.02932551, 0],
         [0.00852273, 0.05965909, 0.13920455, 0.09943182, 0.15056818, 0.16761364, 0.17897727, 0.13068182, 0.05681818,
          0.00852273, 0],
         [0, 0.06534091, 0.15625, 0.13068182, 0.16477273, 0.15625, 0.11647727, 0.11079545, 0.09090909, 0.00852273, 0],
         [0.0058651, 0.1026393, 0.13782991, 0.14369501, 0.13489736, 0.14076246, 0.14956012, 0.1026393, 0.07624633,
          0.0058651, 0],
         [0.00568182, 0.16477273, 0.17613636, 0.15340909, 0.17045455, 0.11079545, 0.10511364, 0.05681818, 0.04261364,
          0.01420455, 0],
         [0.01173021, 0.09677419, 0.17888563, 0.14662757, 0.13782991, 0.10557185, 0.1143695, 0.08797654, 0.05571848,
          0.03225806, 0.03225806],
         [0.00568182, 0.09090909, 0.17613636, 0.12215909, 0.15625, 0.09090909, 0.13352273, 0.09090909, 0.06534091,
          0.05965909, 0.00852273],
         [0.00879765, 0.11730205, 0.15249267, 0.12316716, 0.08211144, 0.09090909, 0.16129032, 0.1202346, 0.07038123,
          0.06744868, 0.0058651],
         [0.00577346, 0.07826246, 0.10428886, 0.13104839, 0.1308651, 0.1308651, 0.10483871, 0.11574413, 0.0789956,
          0.09897361, 0.02034457]]
    #   Границы периодов (в днях в невисокосном году), для которых задано распределение количества облаков (в данном
    #       случае по месяцам)
    common_cloudiness_distr_ranges = [0, 31, 59, 90, 120, 151, 182, 212, 243, 273, 304, 334, 365]

    # Создание объекта - группы полигонов, которые должны быть просканированы для того, чтобы задача считалась
    #   выполненной. Полигоны расположены на поверхности эллипсоида Земли earth_ellipsoid
    polygons_group = PolygonsGroup(earth_ellipsoid)
    #   Загрузка полигонов из файла
    polygons_group.to_read_shape_file(
        "D:/Карты/Валуйки/Важные объединенные участки леса валуйского лесничества (shape).shp")
    #   Разбиение полигонов
    polygons_group.to_split_all_polygons(lat_fineness, long_fineness)
    #   Установка параметров облачности
    polygons_group.to_add_common_cloudiness_distr(common_cloudiness_distr_table, common_cloudiness_distr_ranges)
    print("".join(["\nПолигоны:\n", polygons_group.to_str()]))
    print()

    # Параметры задачи
    #   Название задачи
    name = 'Test'
    #   Начальное и конечное время моделирования
    initial_simulation_time = datetime(2017, 6, 17, 12, 0, 0)
    final_simulation_time = datetime(2017, 7, 17, 0, 0, 0)
    #   Шаг изменения модельного времени в секундах
    step = 1
    #   Максимальный зенитный угол Солнца (градусы)
    max_zenith_angle = 90
    #   Максимальный балл облачности
    max_cloud_score = None
    # Началао и конец годового периода наблюдений
    initial_annual_observation_period = 121
    final_annual_observation_period = 274
    # Минимальный процент сканирования для решения
    min_percent_for_solve = 50

    # Флажок, определяющий, учитывать ли во время моделирования выполнения задачи частичную облачность
    to_consider_partial_cloudiness = False

    # Параметры отчетности
    #   Периоды отчетов
    unit_report_time = 'weeks'
    #   Адрес файла с отчетами
    report_address = 'D://results//Last Version//test_report.txt'
    #   Писать в отчете время от начала моделирования
    report_time_from_initial_time_in_days = True
    #   Писать в отчете данные о спутниках
    report_data_about_satellites = True
    #   Точность в выводе отчетов о состоянии спутников
    count_of_numerals_after_point_in_geo_coordinates = 3
    count_of_numerals_after_point_in_altitude = 1
    count_of_numerals_after_point_in_velocity = 2
    #   Писать в отчете промежуточные данные о решениях
    report_main_data_about_solutions = True
    #   Писать в отчете промежуточные данные о пролетах
    report_main_data_about_overflights = True
    #   Единицы измерения времени для отчетов
    time_unit_of_report = 'days'
    #   Точность в знаках после запятой, для отчетов о решениях и пролетах
    numerals_count_after_point_in_solutions_and_overflights_report = 2
    #   Пропускать период ненаблюдения при подсчете показателей
    to_skip_time_out_of_observation_period = True
    #   Писать в данные о сканированной территории
    report_data_about_scanned_area = True
    #   Писать данные о сканированной территории в процентах
    report_scanned_area_in_percents = True
    #   Точность в знаках после запятой, для отчетов о просканированных территориях
    count_of_numbers_after_point_in_area_report = 2

    # Создание объекта - задачи
    task = Task()
    # Задается название задачи
    task.to_set_name(name)
    # Задается спутниковая группировка
    task.to_set_satellites_group(satellite_group)
    # Задается группа полигонов
    task.to_set_polygons_group(polygons_group)
    # Задаются параметры
    task.to_set_task_characteristics(initial_simulation_time,
                                     final_simulation_time,
                                     step,
                                     max_zenith_angle,
                                     max_cloud_score,
                                     initial_annual_observation_period,
                                     final_annual_observation_period,
                                     min_percent_for_solve)

    # Задается, флажок, определяющий, учитывать ли во время моделирования выполнения задачи частичную облачность
    task.to_set_considering_considering_partial_cloudiness(to_consider_partial_cloudiness)


    # Моделирование
    task.to_solve_task(unit_report_time,
                       report_address,
                       report_time_from_initial_time_in_days,
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

    # Параметры выходных данных
    #   Директория, в которую будут записываться выходные данные
    directory_address = 'D://results//Last Version'
    #   Единицы измерения времени, в которых будут выводиться ресультаты
    unit_of_output_time = 'days'
    #   Количество цифр после запятой в показателях периодичности решений и периодичности пролетов
    numerals_count_after_point = 2
    #   Выводить показатели периодчности решений
    to_get_main_data_about_solutions = True
    #   Выводить показатели периодчности пролетов
    to_get_main_data_about_overflights = True
    #   Выводить зависимость сканированной площади за шаг модельного времени от времени в документах txt, pdf, jpg
    to_get_graph_information_collection_rate_txt = True
    to_get_graph_information_collection_rate_pdf = True
    to_get_graph_information_collection_rate_jpg = True
    #   Выводить зависимость полной сканированной площади от времени в документах txt, pdf, jpg
    to_get_graph_information_volume_txt = True
    to_get_graph_information_volume_pdf = True
    to_get_graph_information_volume_jpg = True
    #   Выводить гистограмму периодов решений задачи в документах txt, pdf, jpg
    to_get_histogram_of_solving_period_txt = True
    to_get_histogram_of_solving_period_pdf = True
    to_get_histogram_of_solving_period_jpg = True
    #   Выводить гистограмму периодов пролетов задачи в документах txt, pdf, jpg
    to_get_histogram_of_overflight_period_txt = True
    to_get_histogram_of_overflight_period_pdf = True
    to_get_histogram_of_overflight_period_jpg = True
    #   Пропускать периоды, в которые нет наблюдений, для периодов решений и пролетов
    to_skip_time_out_of_observation_period_in_periods = True
    #   Пропускать периоды, в которые нет наблюдений, для графиков сканированной площади
    to_skip_time_out_of_observation_period_in_information_value = True
    #   Представлять значения на осях времени на графиках просканированной площади в виде единиц измерения времени
    #       unit_of_output_time
    time_axis_in_units = True
    #   Представлять значения на осях площади на графиках просканированной площади в виде процентов от общей площади
    #       всех полигонов
    scanned_area_in_percents = True
    # Вывод результатов
    task.to_output_data(directory_address, unit_of_output_time, numerals_count_after_point,
                        to_get_main_data_about_solutions,
                        to_get_main_data_about_overflights,
                        to_get_graph_information_collection_rate_txt,
                        to_get_graph_information_collection_rate_pdf,
                        to_get_graph_information_collection_rate_jpg,
                        to_get_graph_information_volume_txt,
                        to_get_graph_information_volume_pdf,
                        to_get_graph_information_volume_jpg,
                        to_get_histogram_of_solving_period_txt,
                        to_get_histogram_of_solving_period_pdf,
                        to_get_histogram_of_solving_period_jpg,
                        to_get_histogram_of_overflight_period_txt,
                        to_get_histogram_of_overflight_period_pdf,
                        to_get_histogram_of_overflight_period_jpg,
                        to_skip_time_out_of_observation_period_in_periods,
                        to_skip_time_out_of_observation_period_in_information_value,
                        time_axis_in_units,
                        scanned_area_in_percents)
