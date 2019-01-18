from OutputDataMaker import to_load_data

if __name__ == '__main__':
    output_data_maker = to_load_data('D:\\results\\data_save.txt')
    # Параметры выходных данных
    #   Название файлов с выходными данными
    data_name = 'Test'
    #   Директория, в которую будут записываться выходные данные
    directory_address = 'D://results//Last Version'
    #   Единицы измерения времени, в которых будут выводиться ресультаты
    unit_of_output_time = 'days'
    #   Количество цифр после запятой в показателях периодичности решений и периодичности пролетов
    numerals_count_after_point = 2
    #   Выводить показатели периодчности решений
    to_get_main_data_about_solutions = False
    #   Выводить показатели периодчности пролетов
    to_get_main_data_about_overflights = False
    #   Выводить зависимость сканированной площади за шаг модельного времени от времени в документах txt, pdf, jpg
    to_get_graph_information_collection_rate_txt = False
    to_get_graph_information_collection_rate_pdf = False
    to_get_graph_information_collection_rate_png = True
    #   Размеры выводимых графиков зависимости сканированной площади за шаг модельного времени от времени по x и y
    graph_information_collection_rate_x_size = 20
    graph_information_collection_rate_y_size = 15
    #   Размеры шрифтов заголовков, подписей засечек на осях, подписей осей в графиках зависимости сканированной площади
    #       за шаг модельного времени от времени
    graph_information_collection_rate_title_font = 24
    graph_information_collection_rate_ticks_label_font = 18
    graph_information_collection_rate_axis_titles_font = 24
    #   Количество пикселей на дюйм в изображении графика зависимости площади просканированной территории за текущий шаг
    #       времени от времени
    graph_information_collection_rate_dpi = 95
    #   Выводить зависимость полной сканированной площади от времени в документах txt, pdf, jpg
    to_get_graph_information_volume_txt = False
    to_get_graph_information_volume_pdf = False
    to_get_graph_information_volume_png = True
    #   Размеры выводимых графиков зависимости полной сканированной площади от времени по x и y
    graph_information_volume_x_size = 20
    graph_information_volume_y_size = 15
    #   Размеры шрифтов заголовков, подписей засечек на осях, подписей осей в графиках зависимости полной сканированной
    #       площади от времени
    graph_information_volume_title_font = 24
    graph_information_volume_ticks_label_font = 18
    graph_information_volume_axis_titles_font = 24
    #   Количество пикселей на дюйм в изображении графика зависимости площади просканированной территории от времени
    graph_information_volume_dpi = 95
    #   Выводить гистограмму периодов решений задачи в документах txt, pdf, jpg
    to_get_histogram_of_solving_period_txt = True
    to_get_histogram_of_solving_period_pdf = False
    to_get_histogram_of_solving_period_png = True
    #   Размеры выводимых гистограмм периодов решений задачи по x и y
    histogram_of_solving_period_x_size = 20
    histogram_of_solving_period_y_size = 15
    #   Размеры шрифтов заголовков, подписей засечек на осях, подписей осей в гистограмм периодов решений задачи
    histogram_of_solving_period_title_font = 24
    histogram_of_solving_period_label_font = 18
    histogram_of_solving_period_axis_titles_font = 24
    #   Количество пикселей на дюйм в изображении гистограммы времени выполнения задачи
    histogram_of_solving_period_dpi = 95
    #   Выводить гистограмму периодов пролетов в документах txt, pdf, jpg
    to_get_histogram_of_overflight_period_txt = True
    to_get_histogram_of_overflight_period_pdf = False
    to_get_histogram_of_overflight_period_png = True
    #   Размеры выводимых гистограмм периодов пролетов по x и y
    histogram_of_overflight_period_x_size = 20
    histogram_of_overflight_period_y_size = 15
    #   Размеры шрифтов заголовков, подписей засечек на осях, подписей осей в гистограмм периодов пролетов
    histogram_of_overflight_period_title_font = 24
    histogram_of_overflight_period_label_font = 18
    histogram_of_overflight_period_axis_titles_font = 24
    #   Количество пикселей на дюйм в изображении гистограммы времени между пролетами спутников над полигонами.
    histogram_of_overflight_period_dpi = 95

    #   Пропускать периоды, в которые нет наблюдений, для периодов решений и пролетов
    to_skip_time_out_of_observation_period_in_periods = False
    #   Пропускать периоды, в которые нет наблюдений, для графиков сканированной площади
    to_skip_time_out_of_observation_period_in_information_value = True
    #   Представлять значения на осях времени на графиках просканированной площади в виде единиц измерения времени
    #       unit_of_output_time
    time_axis_in_units = False
    #   Представлять значения на осях площади на графиках просканированной площади в виде процентов от общей площади
    #       всех полигонов
    scanned_area_in_percents = False
    # Вывод результатов
    output_data_maker.to_output_data(data_name, directory_address, unit_of_output_time, numerals_count_after_point,
                                     to_get_main_data_about_solutions,
                                     to_get_main_data_about_overflights,
                                     to_get_graph_information_collection_rate_txt,
                                     to_get_graph_information_collection_rate_pdf,
                                     to_get_graph_information_collection_rate_png,
                                     graph_information_collection_rate_x_size,
                                     graph_information_collection_rate_y_size,
                                     graph_information_collection_rate_title_font,
                                     graph_information_collection_rate_ticks_label_font,
                                     graph_information_collection_rate_axis_titles_font,
                                     graph_information_volume_dpi,
                                     to_get_graph_information_volume_txt,
                                     to_get_graph_information_volume_pdf,
                                     to_get_graph_information_volume_png,
                                     graph_information_volume_x_size,
                                     graph_information_volume_y_size,
                                     graph_information_volume_title_font,
                                     graph_information_volume_ticks_label_font,
                                     graph_information_volume_axis_titles_font,
                                     graph_information_volume_dpi,
                                     to_get_histogram_of_solving_period_txt,
                                     to_get_histogram_of_solving_period_pdf,
                                     to_get_histogram_of_solving_period_png,
                                     histogram_of_solving_period_x_size,
                                     histogram_of_solving_period_y_size,
                                     histogram_of_solving_period_title_font,
                                     histogram_of_solving_period_label_font,
                                     histogram_of_solving_period_axis_titles_font,
                                     histogram_of_solving_period_dpi,
                                     to_get_histogram_of_overflight_period_txt,
                                     to_get_histogram_of_overflight_period_pdf,
                                     to_get_histogram_of_overflight_period_png,
                                     histogram_of_overflight_period_x_size,
                                     histogram_of_overflight_period_y_size,
                                     histogram_of_overflight_period_title_font,
                                     histogram_of_overflight_period_label_font,
                                     histogram_of_overflight_period_axis_titles_font,
                                     histogram_of_overflight_period_dpi,
                                     to_skip_time_out_of_observation_period_in_periods,
                                     to_skip_time_out_of_observation_period_in_information_value,
                                     time_axis_in_units,
                                     scanned_area_in_percents)
