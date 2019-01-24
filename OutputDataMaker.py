import os
import matplotlib.pyplot as plt
import Task
from datetime import datetime, timedelta
from DateManagement import to_determine_days_number_in_not_leap_year
import TimeManagment


def to_load_data(save_address):
    """
    @ Описание:
        Метод загружает ранее сохраненные данные о задаче, пролетах, выполнениии задач - считывает эти данные из
            заданного файла (файла сохранения) и создает на их основе объект класса OutputDataMaker, с помощью которого
            эти данные можно вывести в соответствующей форме.
    :param save_address: адресс файла сохранения, из которого читаются данные о задаче, пролетах, выполнениии задач
        (String)
    :return: объект класса OutputDataMaker, содержащий данные о задаче, пролетах, выполнениии задач прочитанные из файла
        по адресу save_address
    """
    # Открытие файла сохранения
    save_file = open(save_address, 'r')
    # Чтение название задачи
    task_name = save_file.readline().strip()
    # Чтение значения площади полигонов
    polygons_full_area = float(save_file.readline())
    # Чтение начального модельного времени выполнения задачи
    initial_simulation_time = datetime.strptime(save_file.readline(), "%Y-%m-%d %H:%M:%S\n")
    # Чтение конечного модельного времени выполнения задачи
    final_simulation_time = datetime.strptime(save_file.readline(), "%Y-%m-%d %H:%M:%S\n")
    # Чтение шага времени
    step = float(save_file.readline())
    # Чтение номера первого дня в невисосном году годового периода наблюдения
    initial_annual_observation_period = float(save_file.readline())
    # Чтение номера последнего дня в невисосном году годового периода наблюдения
    final_annual_observation_period = float(save_file.readline())
    # Чтение строк данных о задаче
    task_data = []
    # Чтение первой строчки данных о задаче
    current_str = save_file.readline()
    # Сравнение со строкой 'beginning of growth_of_information', которая обозначает, что начинаются данные о площади
    #   просканированных территориях в цикле
    while current_str != 'beginning of growth_of_information\n':
        # Добавление строки к прочитанным данным
        task_data.append(current_str)
        # Чтение следующей строчки данных
        current_str = save_file.readline()
    # Объединение всех прочитанных строк в одну
    task_data = "".join(task_data)
    # Чтение строк данных о сканируемых территориях
    growth_of_information = []
    # Чтение первой строчки данных о сканируемых территориях и преобразование в datetime
    current_str = save_file.readline()
    # Сравнение со строкой 'beginning of time_of_growth_of_information', которая обозначает, что начинаются данные о
    #   времени сканирования территории
    while current_str != 'beginning of time_of_growth_of_information\n':
        # Преобразование прочитонной строки данных в float и добавление значения времени к прочитанным данным о
        #   площади просканированной территории
        growth_of_information.append(float(current_str))
        # Чтение следующей строчки данных
        current_str = save_file.readline()
    # Чтение строк данных о времени сканирования территории
    time_of_growth_of_information = []
    # Чтение первой строчки данных о времени сканирования территории
    current_str = save_file.readline()
    # Сравнение со строкой 'beginning of time_of_growth_of_information', которая обозначает, что начинаются данные о
    #   времени сканирования территорий
    while current_str != 'beginning of time_of_solutions\n':
        # Преобразование прочитонной строки данных в datetime и добавление значения времени к прочитанным данным о
        #   времени сканирования территории
        time_of_growth_of_information.append(datetime.strptime(current_str, "%Y-%m-%d %H:%M:%S\n"))
        # Чтение следующей строчки данных о времени сканирования территории
        current_str = save_file.readline()
    # Чтение строк данных о времени выполнения задачи
    time_of_solutions = []
    # Чтение первой строчки данных о времени выполнения задачи
    current_str = save_file.readline()
    # Сравнение со строкой 'end of save file', которая обозначает, что файл сохранения закончился
    while current_str != 'end of save file':
        # Преобразование прочитонной строки данных в datetime и добавление значения времени к прочитанным данным о
        #   времени решения задачи
        time_of_solutions.append(datetime.strptime(current_str, "%Y-%m-%d %H:%M:%S\n"))
        # Чтение следующей строчки данных о времени решения задачи
        current_str = save_file.readline()
    return OutputDataMaker(task_name, polygons_full_area, initial_simulation_time, final_simulation_time, step,
                           growth_of_information, time_of_growth_of_information, time_of_solutions,
                           initial_annual_observation_period, final_annual_observation_period, task_data)


class OutputDataMaker:
    """
    @Описание:
        Объекты этого класса содержат информацию о некоторой задаче, пролетах над заданными полигонами, которые должны
            быть просканированы для того чтобы задача считалась решенной и решениях задачи. Эти данные содержатся в
            полях класса. С помощью методов этого класса можно выводить данные о пролетах спутников над заданными
            полигонами и о решениях поставленной задачи в виде файлов, имеющих заданный вид. Подробнее о выходных данных
            в описании метода to_output_data.
    @Поля:
        task_name - название задачи, для которой записываются данные (String). Задается при инициализации.
        polygons_group_area - общая площадь всех полигонов, на территории которых решается задача в кв. метрах (double).
            Задается при инициализации.
        initial_simulation_time - начальное модельное время (datetime), то есть время в формате UTC, в которое
            начинается выполнение задачи внутри модели. Задается при инициализации.
        final_simulation_time - конечное модельное время (datetime), то есть время в формате UTC, в которое
            заканчивается выполнение задачи (попытки сканирования полигонов) внутри модели. Задается при инициализации.
        step - шаг изменения модельного времени в секундах (int, double). Задается при инициализации.
        growth_of_information - список. В каждую ячейку записывается площадь, просканированной территории полигонов
            в кв. метрах (double) за шаг изменения модельного времени self.step. Каждой заполненной ячейке сответствует
            время из списка self.time_of_growth_of_information. При этом в список не записываются нулевые значения.
            Задается при инициализации.
        time_of_growth_of_information - список. В каждую ячейку записывается время UTC (datetime), соответствующее
            времени сканиирования площади из соответствующего элемента списка self.growth_of_information. Список
            заполняется при выполнении метода to_solve_task. Задается при инициализации.
        time_of_solutions - список. В каждом элементе записывается модельное время, в которое была выполнена задача
            (datetime). Задается при инициализации.
        initial_annual_observation_period - номер первого дня в невисокосном году годового периода наблюдений (времени в
            году, когда допустима съемка) (int). Задается при инициализации.
        final_annual_observation_period - номер последнего дня в невисокосном году годового периода наблюдений (времени
            в году, когда допустима съемка) (int). Задается при инициализации.
        observation_period_inside_one_year - индикатор того, что self.final_annual_observation_period больше
            self.initial_annual_observation_period(boolean). Это означает, что что и начало и конец периода наблюдения
            находятся внутри одного года без перехода в следующий (если True, если False, то наоборот). Вычисляется при
            инициализации.
        str_information_about_output_data - строка (String), содержащая данные о выполненой задачи и о выходных данных.
            Эта строка вставляется в файлы, которые создает сохраняет объект данного класса.
                Это следующие данные:
                    название задачи;
                    начальное и конечное модельное время;
                    шаг изменения модельного времени;
                    список спутников, выполняющих задачу;
                    список полигонов, которые должны быть просканированы для выполнения задачи;
                    границы допустимого периода наблюдения, если он задан;
                    максимально допустимый зенитный угол Солнца;
                    максимально допустимый балл облачности;
                    учитывается ли частичная облачность.
            Имеет общий вид:
                Основные параметры задачи 'name'
                    Модельное время:                                от 'yyyy-MM-dd hh:mm:ss' до 'yyyy-MM-dd hh:mm:ss'
                    Шаг изменения модельного времени:               'step' с
                    Спутники, выполняющие задачу:                   'satellite_1', 'satellite_2', 'satellite_3', ...
                    Названия сканируеемых полигонов:                'polygon_1', 'polygon_2', 'polygon_3', ...
                    Допустимый период наблюдения:                   от 'ddd' дня до 'ddd' дня (или 'не задан')
                    Максимально допустимый зенитный угол Солнца:    'uu'°
                    Максимально допустимый балл облачности:         'sss'
                    Частичная облачность учитывается (не учитывается)
            Задается при инициализации.
    @Методы:
        to_output_data - преобразует данные, собранные методом to_solve_task в:
            среднее, медианное, максимальное, минимальное значениее времени выполнения задачи, дисперсию и
            среднеквадратическое отклонение (далее основные оказатели) и выводит в виде докумена txt;
            гистограмму распределения времении выполнения задачи и выводит в текстовом виде в документе txt, в
                графичечском виде в документе pdf, png;
            основные показатели периодичности пролётов спутников над полигонами и выводит в виде докумена txt;
            гистограмму распределения периода пролётов спутников над полигонами и выводит в текстовом виде в
                документе txt, в графичечском видиде в документе pdf, png;
            график прироста просканированной территории (в м^2 или в %) за выбранный период времени и выводит в
                текстовом виде в документе txt, в графичечском виде в документе pdf, png;
            график просканированной территории (в м^2 или в %)  и выводит в текстовом виде в документе txt, в
                графичечском виде в документе pdf, png.
        to_make_axis - принимает список чисел и список соответствующих им значений времени. Числа группируются по
            времени с шагом в одну заданную единицу измерения времени и суммируются. На выход подается список сумм чисел
            и список значений времени, соответсвующих суммам (началу отсчета времени для группы) или отсчеты заданных
            единиц измерения времени от первого - нулевого значения.
        to_sum_values_on_axis - суммирование каждого значения заданного списка со всеми прдыдущими (интегрирование).
        to_make_histogram - создает гистограмму из списка значений с шагом в одну заданную единицу измерения времени.
        to_make_and_output_graph - принимает данные о зависимости и строит по ним графическое представление.
            Также для метода задаются параметры графического представления построенного графика: высота, ширина,
            количество пикселей на дюйм, размеры шрифтов подписей обозначений на осях, заголовка и осей, а также
            сами заголовок и названия осей. После постраения график сохраняется по выбранному адресу в png, pdf или
            обоих форматах.
        to_make_and_output_hist - принимает данные о гистограме и строит по ним графическое представление. Также для
            метода, задаются параметры графического представления построенной гистограммы: высота, ширина, количество
            пикселей на дюйм, размеры шрифтов подписей обозначений на осях, заголовка и осей, а также сами заголовок и
            названия осей. После постраения гистограмма сохраняется по выбранному адресу в png, pdf или обоих форматах.
        to_save_data - сохраняет данные из полей объекта в виде файла сохранения с заданным именем в заданной
            директории. Эти данные могут быть прочитаны, а на их основе может быть создан новый объект данного класса с
            помощью метода to_load_data.
    """
    def __init__(self, task_name, polygons_group_area, initial_simulation_time, final_simulation_time, step,
                 growth_of_information, time_of_growth_of_information, time_of_solutions,
                 initial_annual_observation_period, final_annual_observation_period, str_information_about_output_data):
        self.task_name = task_name
        self.polygons_group_area = polygons_group_area
        self.initial_simulation_time = initial_simulation_time
        self.final_simulation_time = final_simulation_time
        self.step = step
        self.growth_of_information = growth_of_information
        self.time_of_growth_of_information = time_of_growth_of_information
        self.time_of_solutions = time_of_solutions
        self.initial_annual_observation_period = initial_annual_observation_period
        self.final_annual_observation_period = final_annual_observation_period
        self.observation_period_inside_one_year = final_annual_observation_period > initial_annual_observation_period
        self.str_information_about_output_data = str_information_about_output_data

    def to_output_data(self, data_name, directory_address, unit_of_output_time, numerals_count_after_point,
                       to_get_main_data_about_solutions=False,
                       to_get_main_data_about_overflights=False,
                       to_get_graph_information_collection_rate_txt=False,
                       to_get_graph_information_collection_rate_pdf=False,
                       to_get_graph_information_collection_rate_png=False,
                       graph_information_collection_rate_x_size=20,
                       graph_information_collection_rate_y_size=15,
                       graph_information_collection_rate_title_font=24,
                       graph_information_collection_rate_ticks_label_font=18,
                       graph_information_collection_rate_axis_titles_font=24,
                       graph_information_collection_rate_dpi=95,
                       to_get_graph_information_volume_txt=False,
                       to_get_graph_information_volume_pdf=False,
                       to_get_graph_information_volume_png=False,
                       graph_information_volume_x_size=20,
                       graph_information_volume_y_size=15,
                       graph_information_volume_title_font=24,
                       graph_information_volume_ticks_label_font=18,
                       graph_information_volume_axis_titles_font=24,
                       graph_information_volume_dpi=95,
                       to_get_histogram_of_solving_period_txt=False,
                       to_get_histogram_of_solving_period_pdf=False,
                       to_get_histogram_of_solving_period_png=False,
                       histogram_of_solving_period_x_size=20,
                       histogram_of_solving_period_y_size=15,
                       histogram_of_solving_period_title_font=24,
                       histogram_of_solving_period_label_font=18,
                       histogram_of_solving_period_axis_titles_font=24,
                       histogram_of_solving_period_dpi=95,
                       to_get_histogram_of_overflight_period_txt=False,
                       to_get_histogram_of_overflight_period_pdf=False,
                       to_get_histogram_of_overflight_period_png=False,
                       histogram_of_overflight_period_x_size=20,
                       histogram_of_overflight_period_y_size=15,
                       histogram_of_overflight_period_title_font=24,
                       histogram_of_overflight_period_label_font=18,
                       histogram_of_overflight_period_axis_titles_font=24,
                       histogram_of_overflight_period_dpi=95,
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
                    графичечском виде в документе pdf, png;
                основные показатели периодичности пролётов спутников над полигонами и выводит в виде докумена txt;
                гистограмму распределения периода пролётов спутников над полигонами и выводит в текстовом виде в
                    документе txt, в графичечском видиде в документе pdf, png;
                график прироста просканированной территории (в м^2 или в %) за выбранный период времени и выводит в
                    текстовом виде в документе txt, в графичечском виде в документе pdf, png;
                график просканированной территории (в м^2 или в %)  и выводит в текстовом виде в документе txt, в
                    графичечском виде в документе pdf, png.
        :param data_name: название файлов с выходными данными, которым они все будут подписываться перед пояснением типа
            данных
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
        :param to_get_graph_information_collection_rate_png: вывести зависимость площади просканированной территории за
            текущий шаг времени от времени в виде графика в файл png (если True, если False, то не выводить). По
            умолчанию False.
        :param graph_information_collection_rate_x_size: размер графика зависимости площади просканированной территории
            за текущий шаг времени от времени по оси x в дюймах (int, float). По умолчанию 20.
        :param graph_information_collection_rate_y_size: размер графика зависимости площади просканированной территории
            за текущий шаг времени от времени по оси y в дюймах (int, float). По умолчанию 15.
        :param graph_information_collection_rate_title_font: размер шрифта заголовка графика зависимости площади
            просканированной территории за текущий шаг времени от времени. По умолчанию 24.
        :param graph_information_collection_rate_ticks_label_font: размер шрифта подписей засечек осей графика
            зависимости площади просканированной территории за текущий шаг времени от времени. По умолчанию 18.
        :param graph_information_collection_rate_axis_titles_font: размер шрифта заголовков осей графика зависимости
            площади просканированной территории за текущий шаг времени от времени. По умолчанию 24.
        :param graph_information_collection_rate_dpi: количество пикселей на дюйм в изображении графика зависимости
            площади просканированной территории за текущий шаг времени от времени. По умолчанию 95.
        :param to_get_graph_information_volume_txt: вывести зависимость площади просканированной территории от времени в
            виде таблицы в файл txt (если True, если False, то не выводить). По умолчанию False.
        :param to_get_graph_information_volume_pdf: вывести зависимость площади просканированной территории от времени в
            виде графика в файл pdf (если True, если False, то не выводить). По умолчанию False.
        :param to_get_graph_information_volume_png: вывести зависимость площади просканированной территории от времени в
            виде графика в файл png (если True, если False, то не выводить). По умолчанию False.
        :param graph_information_volume_x_size: размер графика зависимости площади просканированной территории от
            времени по оси x в дюймах (int, float). По умолчанию 20.
        :param graph_information_volume_y_size: размер графика площади просканированной территории от времени по
            оси y в дюймах (int, float). По умолчанию 15.
        :param graph_information_volume_title_font: размер шрифта заголовка графика площади просканированной
            территории от времени. По умолчанию 24.
        :param graph_information_volume_ticks_label_font: размер шрифта подписей засечек осей графика
            площади просканированной территории от времени. По умолчанию 18.
        :param graph_information_volume_axis_titles_font: размер шрифта заголовков осей графика площади
            просканированной территории от времени. По умолчанию 24.
        :param graph_information_volume_dpi: количество пикселей на дюйм в изображении графика зависимости площади
            просканированной территории от времени. По умолчанию 95.
        :param to_get_histogram_of_solving_period_txt: вывести время выполнения задачи в виде гистограммы в файл txt
            (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_solving_period_pdf: вывести время выполнения задачи в виде гистограммы в файл pdf
            (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_solving_period_png: вывести время выполнения задачи в виде гистограммы в файл png
            (если True, если False, то не выводить). По умолчанию False.
        :param histogram_of_solving_period_dpi: количество пикселей на дюйм в изображении графика зависимости площади
            просканированной территории от времени. По умолчанию 95.
        :param histogram_of_solving_period_x_size: размер гистограммы времени выполнения задачи по оси x в дюймах (int,
            float). По умолчанию 20.
        :param histogram_of_solving_period_y_size: размер гистограммы времени выполнения задачи по оси y в дюймах (int,
            float). По умолчанию 15.
        :param histogram_of_solving_period_title_font: размер шрифта заголовка гистограммы времени выполнения задачи. По
            умолчанию 24.
        :param histogram_of_solving_period_label_font: размер шрифта подписей засечек осей гистограммы времени
            выполнения задачи. По умолчанию 18.
        :param histogram_of_solving_period_axis_titles_font: размер шрифта заголовков осей гистограммы времени
            выполнения задачи. По умолчанию 24.
        :param histogram_of_solving_period_dpi: количество пикселей на дюйм в изображении гистограммы времени выполнения
            задачи. По умолчанию 95.
        :param to_get_histogram_of_overflight_period_txt: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл txt (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_overflight_period_pdf: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл pdf (если True, если False, то не выводить). По умолчанию False.
        :param to_get_histogram_of_overflight_period_png: вывести время между пролетамми спутников над полигонами в виде
            гистограммы в файл png (если True, если False, то не выводить). По умолчанию False.
        :param histogram_of_overflight_period_x_size: размер гистограммы времени между пролетамми спутников над
            полигонами по оси x в дюймах (int, float). По умолчанию 20.
        :param histogram_of_overflight_period_y_size: размер гистограммы времени между пролетамми спутников над
            полигонами по оси y в дюймах (int, float). По умолчанию 15.
        :param histogram_of_overflight_period_title_font: размер шрифта заголовка гистограммы между пролетамми спутников
            над полигонами задачи. По умолчанию 24.
        :param histogram_of_overflight_period_label_font: размер шрифта подписей засечек осей гистограммы времени
            между пролетамми спутников над полигонами. По умолчанию 18.
        :param histogram_of_overflight_period_axis_titles_font: размер шрифта заголовков осей гистограммы времени
            между пролетамми спутников над полигонами. По умолчанию 24.
        :param histogram_of_overflight_period_dpi: количество пикселей на дюйм в изображении гистограммы времени между
            пролетамми спутников над полигонами. По умолчанию 95.
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
        #   Создание директории, в которую записываются выходные данные, если ее нет
        if not os.path.exists(directory_address):
            os.makedirs(directory_address)
        # Будет ли выводиться зависимость просканированной площади за шаг времени от времени в каком-либо виде
        if to_get_graph_information_collection_rate_txt or \
                to_get_graph_information_collection_rate_pdf or \
                to_get_graph_information_collection_rate_png:
            to_get_graph_information_collection_rate = True
        else:
            to_get_graph_information_collection_rate = False
        # Будет ли выводиться зависимость просканированной площади от времени в каком-либо виде
        if to_get_graph_information_volume_txt or \
                to_get_graph_information_volume_pdf or \
                to_get_graph_information_volume_png:
            to_get_graph_information_volume = True
        else:
            to_get_graph_information_volume = False
        # Будет ли выводиться гистограмма времени между решениями в каком-либо виде
        if to_get_histogram_of_solving_period_txt or \
                to_get_histogram_of_solving_period_pdf or \
                to_get_histogram_of_solving_period_png:
            to_get_histogram_of_solving_period = True
        else:
            to_get_histogram_of_solving_period = False
        # Будет ли выводиться гистограмма времени между пролетами спутников над полигонами в каком-либо виде
        if to_get_histogram_of_overflight_period_txt or \
                to_get_histogram_of_overflight_period_pdf or \
                to_get_histogram_of_overflight_period_png:
            to_get_histogram_of_overflight_period = True
        else:
            to_get_histogram_of_overflight_period = False
        # unit_symbol - символ единиц измерения времени для всех выходных данных, кроме графиков, который будет писаться
        #   в заголовки файлов, в название файлов, на осях гистограмм
        unit_symbol = TimeManagment.unit_in_symbol(unit_of_output_time)
        # Если на осях времени в графиках отображаются единицы измерения времени, в которых будет выводиться информация
        #   о времени, то задается символ единицы измерения такой же, как unit_symbol, если нет, то время на осях
        #   графиков будет обозначаться в формате времени UTC - "yyyy-MM-dd hh:mm:ss" - вместо символа единиц измерения
        #   времени - обозначение "date, time"
        if time_axis_in_units:
            graph_unit_symbol = unit_symbol
        else:
            graph_unit_symbol = "date, time"
        # Вычисление периодов между решениями задачи по списку времени выполнения self.time_of_solutions
        periods_of_solutions = []
        if to_get_main_data_about_solutions or to_get_histogram_of_solving_period:
            periods_of_solutions = Task.to_identify_periods_sec(self.time_of_solutions, self.initial_simulation_time,
                                                                self.initial_annual_observation_period,
                                                                self.final_annual_observation_period,
                                                                to_skip_time_out_of_observation_period_in_periods)
        # Вычисление периодов между пролетами спутников над исследуемыми полигонами по списку времени сканирования
        #   self.time_of_growth_of_information
        periods_of_overflight = []
        if (to_get_main_data_about_overflights or to_get_histogram_of_overflight_period) and \
                self.time_of_growth_of_information is not []:
            time_of_growth_of_information = self.time_of_growth_of_information
            # Вычисление времен появления спутников над полигонами и начала сканирования и запись этого времени в список
            #   time_of_overflights
            time_of_overflights = Task.to_define_initial_times_of_scan_session(time_of_growth_of_information, self.step)
            # Вычсление периодов пролетов
            periods_of_overflight = Task.to_identify_periods_sec(time_of_overflights, self.initial_simulation_time,
                                                                 self.initial_annual_observation_period,
                                                                 self.final_annual_observation_period,
                                                                 to_skip_time_out_of_observation_period_in_periods)
        # Если выводятся основные показатели периодичности решений или пролетов...
        if to_get_main_data_about_solutions or to_get_main_data_about_overflights:
            # Вычисление полного модельного времени (времени моделирования) в секундах
            overall_time_of_simulation_sec = (self.final_simulation_time - self.initial_simulation_time).total_seconds()
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
                main_data_solutions_file = open("".join([directory_address, '\\', data_name,
                                                         ' - основные показатели периодичности выполнения задачи (',
                                                         unit_symbol, ').txt']), 'w')
                main_data_solutions_file.write("".join(['Основные показатели периодичности выполнения задачи ',
                                                        str(self.task_name), '\n',
                                                        self.str_information_about_output_data,
                                                        Task.to_get_main_data_about_periods
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
                main_data_overflights_file = open("".join([directory_address, '/', data_name,
                                                           ' - основные показатели периодичности пролетов спутников (',
                                                           unit_symbol, ').txt']), 'w')
                main_data_overflights_file.write("".join(['Основные показатели периодичности пролетов спутника ',
                                                          str(self.task_name), '\n\n',
                                                          self.str_information_about_output_data,
                                                          Task.to_get_main_data_about_periods
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
                    growth_of_information.append(value / self.polygons_group_area)
            else:
                # Если нет, то символом становится 'кв. м'
                symbol_of_units_of_information = 'кв. м'
                growth_of_information = self.growth_of_information
            # Составление осей графика площади за шаг от времени
            information_collection_rate_axis, time_axis = self.to_make_axis(
                growth_of_information,
                self.time_of_growth_of_information,
                unit_of_output_time,
                to_skip_time_out_of_observation_period_in_information_value,
                time_axis_in_units)
            # Если зависимость выводится в каком-либо виде...
            if to_get_graph_information_collection_rate:
                # Подготовка заголовков
                graph_title = "".join(['График скорости сканирования площади (', symbol_of_units_of_information, '/',
                                       unit_symbol, ') от времени (', graph_unit_symbol, ')'])
                graph_address = "".join([directory_address, '/', data_name, ' - график скорости сканирования'
                                                                            ' площади (',
                                         symbol_of_units_of_information, ' в ', unit_symbol, ') от времени (',
                                         graph_unit_symbol, ')'])
                # Подписи осей графика
                y_label = "".join(['Скорость сканирования площади (', symbol_of_units_of_information, '/',
                                   unit_symbol, ')'])
                x_label = "".join(['Время (', graph_unit_symbol, ')'])
                # Вывод зависимости в виде таблицы в файле txt, если требуется
                if to_get_graph_information_collection_rate_txt:
                    table_information_volume_file = open("".join([graph_address, '.txt']), 'w')

                    table_information_volume_file.write("".join([graph_title, '\n\n',
                                                                 self.str_information_about_output_data,
                                                                 x_label, '\t\t', y_label, '\n']))
                    for i in range(0, len(information_collection_rate_axis)):
                        table_information_volume_file.write("".join([str(time_axis[i]), '\t\t\t',
                                                                     str(information_collection_rate_axis[i]), '\n']))
                # Если предполагается вывод зависимости в виде графиков, то график строится с заголовком и названием
                #   осей
                if to_get_graph_information_collection_rate_png or to_get_graph_information_collection_rate_pdf:
                    # Создание графика и охранение по graph_address в форматах png и (или) pdf
                    self.to_make_and_output_graph(graph_address, graph_title, time_axis,
                                                  information_collection_rate_axis,
                                                  graph_information_collection_rate_x_size,
                                                  graph_information_collection_rate_y_size,
                                                  graph_information_collection_rate_dpi, unit_of_output_time,
                                                  x_label, y_label,
                                                  graph_information_collection_rate_ticks_label_font,
                                                  graph_information_collection_rate_title_font,
                                                  graph_information_collection_rate_axis_titles_font,
                                                  'blue',
                                                  to_get_graph_information_collection_rate_png,
                                                  to_get_graph_information_collection_rate_pdf)
            # Если зависимость площади сканированной территории выводится в каком-либо виде
            if to_get_graph_information_volume:
                # Интегрируются значение зависимости просканированной площади за шаг от времени и получается зависимость
                #    общей площади от того же времени
                information_volume_axis = self.to_sum_values_on_axis(information_collection_rate_axis)
                # Подготовка заголовков
                graph_title = "".join(['График собранной информации (', symbol_of_units_of_information,
                                       ') от времени (', graph_unit_symbol, ')'])
                graph_address = "".join([directory_address, '/', data_name, ' - график собранной информации (',
                                         symbol_of_units_of_information, ') от времени (', graph_unit_symbol, ')'])
                # Подписи осей графика
                y_label = "".join(['Площадь (', symbol_of_units_of_information, ')'])
                x_label = "".join(['Время (', graph_unit_symbol, ')'])
                # Вывод зависимости в виде таблицы в файле txt, если требуется
                if to_get_graph_information_volume_txt:
                    table_information_volume_file = open("".join([graph_address, '.txt']), 'w')

                    table_information_volume_file.write("".join([graph_title, '\n\n',
                                                                 self.str_information_about_output_data,
                                                                 x_label, '\t\t', y_label, '\n']))
                    for i in range(0, len(information_volume_axis)):
                        table_information_volume_file.write("".join([str(time_axis[i]), '\t\t\t',
                                                                     str(information_volume_axis[i]), '\n']))
                # Если предполагается вывод зависимости в виде графиков, то график строится с заголовком и названием
                #   осей
                if to_get_graph_information_volume_png or to_get_graph_information_volume_pdf:
                    # Создание графика и охранение по graph_address в форматах png и (или) pdf
                    self.to_make_and_output_graph(graph_address, graph_title, time_axis,
                                                  information_volume_axis,
                                                  graph_information_volume_x_size,
                                                  graph_information_volume_y_size,
                                                  graph_information_volume_dpi, unit_of_output_time,
                                                  x_label, y_label,
                                                  graph_information_volume_ticks_label_font,
                                                  graph_information_volume_title_font,
                                                  graph_information_volume_axis_titles_font,
                                                  'purple',
                                                  to_get_graph_information_volume_png,
                                                  to_get_graph_information_volume_pdf)
        # Если выводится гистограмма периодов решений задачи в каком-либо виде
        if to_get_histogram_of_solving_period:
            # Построение гистограммы периодов решений
            histogram_of_solving_periods = self.to_make_histogram(periods_of_solutions, unit_of_output_time)
            # Подготовка заголовков и подписей осей
            histogram_title = "".join(['Гистограмма распределения решений (', unit_symbol, ')'])
            histogram_address = "".join([directory_address, '/', data_name,
                                         ' - гистограмма распределения решений (', unit_symbol, ')'])
            x_label = "".join(['Период выполнения задачи (', unit_symbol, ')'])
            y_label = 'Количество решений'
            # Вывод гистограммы в файле txt, если требуется
            if to_get_histogram_of_solving_period_txt:
                histogram_of_solutions_file = open("".join([histogram_address, '.txt']), 'w')

                histogram_of_solutions_file.write("".join([histogram_title, '\n\n',
                                                           self.str_information_about_output_data, x_label, '\t',
                                                           y_label, '\n']))
                for i in range(0, len(histogram_of_solving_periods)):
                    histogram_of_solutions_file.write("".join([str(i), '\t\t\t\t', str(histogram_of_solving_periods[i]),
                                                               '\n']))
                histogram_of_solutions_file.close()
            # Если гистограмма выводится в графическом виде
            if to_get_histogram_of_solving_period_png or to_get_histogram_of_solving_period_pdf:
                # Построение гистограммы в графическом виде
                self.to_make_and_output_hist(histogram_address, histogram_title, histogram_of_solving_periods,
                                             histogram_of_solving_period_x_size, histogram_of_solving_period_y_size,
                                             histogram_of_solving_period_dpi, x_label, y_label,
                                             histogram_of_solving_period_label_font,
                                             histogram_of_solving_period_title_font,
                                             histogram_of_solving_period_axis_titles_font, 'red',
                                             to_get_histogram_of_solving_period_png,
                                             to_get_histogram_of_solving_period_pdf)
        # Если выводится гистограмма периодов пролетов спутников над полигонами в каком-либо виде
        if to_get_histogram_of_overflight_period:
            # Построение гистограммы периодов решений
            histogram_of_overflight_periods = self.to_make_histogram(periods_of_overflight, unit_of_output_time)
            # Подготовка заголовков и подписей осей
            histogram_title = "".join(['Гистограмма распределения пролетов (', unit_symbol, ')'])
            histogram_address = "".join([directory_address, '/', data_name,
                                         ' - гистограмма распределения пролетов (', unit_symbol, ')'])
            x_label = "".join(['Период пролетов (', unit_symbol, ')'])
            y_label = 'Количество пролетов'
            # Вывод гистограммы в файле txt, если требуется
            if to_get_histogram_of_overflight_period_txt:
                histogram_of_overflight_file = open("".join([histogram_address, '.txt']), 'w')

                histogram_of_overflight_file.write("".join([histogram_title, '\n\n',
                                                            self.str_information_about_output_data, x_label, '\t\t',
                                                            y_label, '\n']))

                for i in range(0, len(histogram_of_overflight_periods)):
                    histogram_of_overflight_file.write("".join([str(i), '\t\t\t\t',
                                                                str(histogram_of_overflight_periods[i]), '\n']))

                histogram_of_overflight_file.close()
            # Если гистограмма выводится в графическом виде
            if to_get_histogram_of_overflight_period_png or to_get_histogram_of_overflight_period_pdf:
                self.to_make_and_output_hist(histogram_address, histogram_title, histogram_of_overflight_periods,
                                             histogram_of_overflight_period_x_size,
                                             histogram_of_overflight_period_y_size,
                                             histogram_of_overflight_period_dpi, x_label, y_label,
                                             histogram_of_overflight_period_label_font,
                                             histogram_of_overflight_period_title_font,
                                             histogram_of_overflight_period_axis_titles_font, 'green',
                                             to_get_histogram_of_overflight_period_png,
                                             to_get_histogram_of_overflight_period_pdf)

    def to_make_axis(self, values_original, times_original, unit_of_time, to_skip_time_out_of_observation_period=False,
                     time_axis_in_units=False):
        """
        @Описание:
            Метод принимает список чисел и список соответствующих им значений времени. Числа группируются по времени с
                шагом в одну заданную единицу измерения времени и суммируются. На выход подается список сумм чисел и
                список значений времени, соответсвующих суммам (началу отсчета времени для группы) или отсчеты заданных
                единиц измерения времени от первого - нулевого значения.
        :param values_original: список начений (int, double)
        :param times_original: список значений времени (datetime)
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
        # Дублирование списков данных во избежание изменения данных
        values = values_original.copy()
        times = times_original.copy()
        # Начальное и конечное время вычислений
        initial_time = self.initial_simulation_time
        final_time = self.final_simulation_time
        # Вычисление шага времени, по которому будет суммирование в секундах
        step = TimeManagment.to_get_unit_in_seconds(unit_of_time)
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
                day_number = to_determine_days_number_in_not_leap_year(time_axis[i])
                current_day_between_borders_of_annual_observation_period =\
                    initial_annual_observation_period < day_number < final_annual_observation_period
                current_day_in_observation_period = (not self.observation_period_inside_one_year or
                                                     current_day_between_borders_of_annual_observation_period) and \
                                                    (self.observation_period_inside_one_year or
                                                     not current_day_between_borders_of_annual_observation_period) or \
                    day_number == initial_annual_observation_period or \
                    day_number == final_annual_observation_period

                if current_day_in_observation_period:
                    i = i + 1
                else:
                    # Удаление лишних значений
                    del value_axis[i]
                    del time_axis[i]
        # Перевод времени datetime в единицы измерения времени unit_of_time
        if time_axis_in_units:
            time_axis = list(range(0, len(time_axis)))
            ###initial_time = time_axis[0]
            ###for i in range(0, len(time_axis)):
            ###    time_axis[i] = (time_axis[i] - initial_time).total_seconds() / step
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
            summed_axis.append(axis[i] + summed_axis[i - 1])
        return summed_axis

    @staticmethod
    def to_make_and_output_graph(graph_address, graph_title, time_axis_original, value_axis_original, x_size, y_size,
                                 dpi, unit_of_output_time, x_label, y_label, ticks_label_font, title_font,
                                 axis_title_font, color_ind, output_in_png=True, output_in_pdf=False):
        """
        @Описание:
            Метод принимает данные о зависимости и строит по ним график с помощью пакета matplotlib. Также для метода
                задаются параметры графического представления построенного графика: высота, ширина, количество пикселей
                на дюйм, размеры шрифтов подписей обозначений на осях, заголовка и осей, а также сами заголовок и
                названия осей. После постраения график сохраняется по выбранному адресу в png, pdf или обоих форматах.
        :param graph_address: адрес по которому сохраняется график (с названием, но без формата) (String)
        :param graph_title: название графика, которым он будет подписан в графическом представлении (String)
        :param time_axis_original: данные по времени по оси x - в некоторых единицах измерения времени или в datetime
            (int, datetime)
        :param value_axis_original: значение по оси y (int, float)
        :param x_size: размер графического представления графика по оси x (в ширину) в дюймах (int, float)
        :param y_size: размер графического представления графика по оси y (в высоту) в дюймах (int, float)
        :param dpi: количество пикселей на дюм в графическом представлении графика (int)
        :param unit_of_output_time: разница между соседними значениями времени по оси x в одной единице измерения
            времени, записаной в этом аргументе (String). Используется только, если время представляется в datetime
        :param x_label: название оси x, которым будет подписываться эта ось на графическом представлении (String)
        :param y_label: название оси y, которым будет подписываться эта ось на графическом представлении (String)
        :param ticks_label_font: размер шрифта названия графика graph_title, которым он подписывается на графическом
            представлении (int)
        :param title_font: размер шрифта названия графика осей x_label, y_label на графическом представлении (int)
        :param axis_title_font: размер шрифта, обозначений засечек на осях x и y в графическом представлении (int)
        :param color_ind: текстовое обозначение цвета графика (String)
        :param output_in_png: если True, то выводить график в формате png (boolean). По умолчанию False
        :param output_in_pdf: если True, то выводить график в формате pdf (boolean). По умолчанию True
        :return: сохраняет по адресу graph_address графическое представление графика в форматах png, pdf или обоих
            одновременно, построенный по зависимости graph_title, time_axis_original с размерами x_size, y_size,
                разрешениеь dpi на дюйм, с подписью графика graph_title, подписями осей x_label, y_label, с рамерами
                шрифтов названия, подписей осей и подписей осей ticks_label_font, title_font, axis_title_font,
                соответственно, цветом графика color.
        """
        # Копирование осей, чтобы не изменять оригиналы
        time_axis = time_axis_original.copy()
        value_axis = value_axis_original.copy()
        # Индикатор того, что на оси x (оси времени) обозначается время в datetime
        time_axis_is_datetime = time_axis[0].__class__ is datetime
        graph = plt.figure(figsize=(x_size, y_size), dpi=dpi)
        ax = graph.add_subplot(111)
        # Добавление последнего значения к значаениям, выводимым на графике, чтобы ступенчатый график
        #   выглядел понятнее
        value_axis.append(value_axis[-1])
        if time_axis_is_datetime:
            time_axis.append(time_axis[-1] + timedelta(seconds=TimeManagment.to_get_unit_in_seconds(
                unit_of_output_time)))
        else:
            time_axis.append(time_axis[-1] + 1)
        plt.step(time_axis, value_axis, where='post', color=color_ind)
        # Изменение размера шрифта подписей оси x
        for label in ax.xaxis.get_ticklabels():
            label.set_fontsize(ticks_label_font)
        # Изменение размера шрифта подписей оси y
        for label in ax.yaxis.get_ticklabels():
            label.set_fontsize(ticks_label_font)
        plt.title(graph_title, fontsize=title_font)
        plt.ylabel(y_label, fontsize=axis_title_font)
        plt.xlabel(x_label, fontsize=axis_title_font)
        plt.grid(True)
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.family'] = 'Calibri'
        # Позиции засечек на графике минимальных, чтобы весь график был виден для обеих осей
        y_ticks = ax.get_yticks()
        max_y_value = max(value_axis)
        i = -1
        while ~(y_ticks[i] >= max_y_value > y_ticks[i - 1]):
            i = i - 1
        min_suitable_y_tick = y_ticks[i]
        x_ticks = ax.get_xticks()
        if time_axis_is_datetime:
            for label in ax.xaxis.get_ticklabels():
                # Наклонение подписей засечек на оси x на 45 градусов, чтобы они не перекрывали друг друга
                label.set_rotation(-45)
            plt.axis([x_ticks[0], x_ticks[-1], 0, min_suitable_y_tick])
            plt.xticks(x_ticks)
        else:
            max_x_value = max(time_axis)
            i = -1
            while ~(x_ticks[i] >= max_x_value > x_ticks[i - 1]):
                i = i - 1
            min_suitable_x_tick = x_ticks[i]
            # Границы окна графика
            plt.axis([0, min_suitable_x_tick, 0, min_suitable_y_tick])
        # Вывод зависимости в виде графика в файле png, если требуется
        if output_in_png:
            graph.savefig("".join([graph_address, '.png']))
        # Вывод зависимости в виде графика в файле pdf, если требуется
        if output_in_pdf:
            graph.savefig("".join([graph_address, '.pdf']))
        plt.close()

    @staticmethod
    def to_make_and_output_hist(hist_address, hist_title, hist_values, x_size, y_size, dpi, x_label, y_label,
                                ticks_label_font, title_font, axis_title_font, color_ind, output_in_png=True,
                                output_in_pdf=False):
        """
        @Описание:
            Метод принимает данные о гистограме и строит по ним графическое представление с помощью пакета matplotlib.
                Также для метода, задаются параметры графического представления построенной гистограммы: высота, ширина,
                количество пикселей на дюйм, размеры шрифтов подписей обозначений на осях, заголовка и осей, а также
                сами заголовок и названия осей. После постраения гистограмма сохраняется по выбранному адресу в png, pdf
                или обоих форматах.
        :param hist_address: адрес по которому сохраняется гистограмма (с названием, но без формата) (String)
        :param hist_title: название гистограммы, которым он будет подписан в графическом представлении (String)
        :param hist_values: данные о гистограмме (значения каждого столбца в списке) (int)
        :param x_size: размер графического представления графика по оси x (в ширину) в дюймах (int, float)
        :param y_size: размер графического представления графика по оси y (в высоту) в дюймах (int, float)
        :param dpi: количество пикселей на дюм в графическом представлении графика (int)
        :param x_label: название оси x, которым будет подписываться эта ось на графическом представлении (String)
        :param y_label: название оси y, которым будет подписываться эта ось на графическом представлении (String)
        :param ticks_label_font: размер шрифта названия графика graph_title, которым он подписывается на графическом
            представлении (int)
        :param title_font: размер шрифта названия графика осей x_label, y_label на графическом представлении (int)
        :param axis_title_font: размер шрифта, обозначений засечек на осях x и y в графическом представлении (int)
        :param color_ind: текстовое обозначение цвета графика (String)
        :param output_in_png: если True, то выводить график в формате png (boolean). По умолчанию False
        :param output_in_pdf: если True, то выводить график в формате pdf (boolean). По умолчанию True
        :return: сохраняет по адресу hist_address графическое представление гистограммы в форматах png, pdf или обоих
            одновременно, построенный по зависимости hist_title, time_axis_original с размерами x_size, y_size,
            разрешениеь dpi на дюйм, с подписью графика graph_title, подписями осей x_label, y_label, с рамерами
            шрифтов названия, подписей осей и подписей осей ticks_label_font, title_font, axis_title_font,
            соответственно, цветом графика color.
        """
        hist = plt.figure(figsize=(x_size, y_size), dpi=dpi)
        ax = hist.add_subplot(111)

        plt.bar(range(0, len(hist_values)), hist_values, width=1, color=color_ind)
        # Изменение размера шрифта подписей оси x
        for label in ax.xaxis.get_ticklabels():
            label.set_fontsize(ticks_label_font)
        # Изменение размера шрифта подписей оси y
        for label in ax.yaxis.get_ticklabels():
            label.set_fontsize(ticks_label_font)
        plt.title(hist_title, fontsize=title_font)
        plt.ylabel(y_label, fontsize=axis_title_font)
        plt.xlabel(x_label, fontsize=axis_title_font)
        plt.grid(True)
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.family'] = 'Calibri'
        # Позиции засечек на графике минимальных, чтобы весь график был виден для обеих осей
        y_ticks = ax.get_yticks()
        max_y_value = max(hist_values)
        i = -1
        while ~(y_ticks[i] >= max_y_value > y_ticks[i - 1]):
            i = i - 1
        min_suitable_y_tick = y_ticks[i]
        x_ticks = ax.get_xticks()
        max_x_value = len(hist_values)
        i = -1
        while ~(x_ticks[i] >= max_x_value > x_ticks[i - 1]):
            i = i - 1
        min_suitable_x_tick = x_ticks[i]
        plt.axis([0, min_suitable_x_tick, 0, min_suitable_y_tick])
        # Вывод зависимости в виде графика в файле png, если требуется
        if output_in_png:
            hist.savefig("".join([hist_address, '.png']))
        # Вывод зависимости в виде графика в файле pdf, если требуется
        if output_in_pdf:
            hist.savefig("".join([hist_address, '.pdf']))
        plt.close()

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
        step = TimeManagment.to_get_unit_in_seconds(unit_of_time)
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

    def to_save_data(self, save_name, save_directory):
        """
        @Описание:
            Метод сохраняет данные из полей объекта в виде файла сохранения с заданным именем в заданной директории. Эти
                данные могут быть прочитаны, а на их основе может быть создан новый объект данного класса с помощью
                метода to_load_data.
        :param save_name: название создаваемого файла сохранения (String)
        :param save_directory: адрес директории, в которую сохраняется файл сохранение (String)
        :return: файл сохранение, содержащий данные, содержащиеся в полях объекта этого класса, по которым можно создать
            объект OutputDataMaker с помощью метода to_load_data, с названием save_name по в директории по адресу
            save_directory
        """
        # Составление адреса файла сохранения
        save_address = "".join([save_directory, '\\', save_name, '.txt'])
        # Создание или открытие файла сохранения
        save_file = open(save_address, 'w')
        # Запись данных о задачи в файл сохранения
        save_file.write("".join([
            self.task_name, '\n',
            str(self.polygons_group_area), '\n',
            str(self.initial_simulation_time), '\n',
            str(self.final_simulation_time), '\n',
            str(self.step), '\n',
            str(self.initial_annual_observation_period), '\n',
            str(self.final_annual_observation_period), '\n',
            self.str_information_about_output_data,
            'beginning of growth_of_information', '\n']))
        # Заполнение строки данных данными из self.growth_of_information
        for data_string in self.growth_of_information:
            save_file.write("".join([str(data_string), '\n']))
        save_file.write("".join(['beginning of time_of_growth_of_information', '\n']))
        # Заполнение строки данных данными из self.time_of_growth_of_information
        for data_string in self.time_of_growth_of_information:
            save_file.write("".join([str(data_string), '\n']))
        save_file.write("".join(['beginning of time_of_solutions', '\n']))
        # Заполнение строки данных данными из self.time_of_solutions
        for data_string in self.time_of_solutions:
            save_file.write("".join([str(data_string), '\n']))
        # Запись строки "end of save file", обозначающий, что файл закончился
        save_file.write("end of save file")
        # Закрытие файла сохранения
        save_file.close()
