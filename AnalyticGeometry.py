import math
import numpy


class Vector:
    """
    @Описание:
        Класс моделирует вектор в трехмерном пространстве, заданный декартовыми координатами (x, y, z).
            Предусматривается возможность вычисления длины вектора, суммирования, вычитание векторов, вычисление
            отрицательного вектора, векторное и скалярное умножение на вектор, смешанное произведение с векторами,
            вычисление нормированного вектора, вычисление повернутого вектора

    @Аргументы:
        x - координата x вектора
        y - координата y вектора
        z - координата z вектора

    @Поля класса:
        x - координата x вектора. Берется из аргумента x при инициализации
        y - координата y вектора. Берется из аргумента y при инициализации
        z - координата z вектора. Берется из аргумента z при инициализации

    @Методы класса
        scalar_product(self, other) - вычисляет скалярное произведение моделируемого вектора на другой вектор
        triple_product(self, other1, other2) - вычисляет смешанное произведение моделируемого вектора с двумя другими
            векторами other1 и other2
        get_normalized_vector(self) - вычисляет вектор, равный нормированному моделируемому вектору
        to_rotate_vector(self, axis_of_rotation, angle_of_rotation) - вычисляет вектор, равный повернотому моделируемому
            вектору вокруг оси axis_of_rotation (заданной вектором) на угол angle_of_rotation
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __len__(self):
        """
        @Описание
            Вычисление длины моделируемого вектора
        :return: длина моделируемого вектора
        """
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __add__(self, other):
        """
        @Описание
            Сложение моделируемого вектора с другим
        :param other: вектор, который прибавляется моделируемому вектору
        :return: вектор-сумма
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        @Описание
            Вычитание из моделируемого вектора другого
        :param other: вектор, который вычитается из моделируемого вектора
        :return: вектор-разность
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        """
        @Описание
            Вычсление вектора отрицательного моделируемому
        :return: вектор отрицательный моделируемому
        """
        return Vector(-self.x, -self.y, -self.z)

    def __mul__(self, other):
        """
        @Описание
            Векторное умножение моделируемого вектора на другой
        :param other: вектор, на который векторно умножается моделируемый вектор
        :return: вектор, получившийся при векторном умножении моделируемого вектора на другой
        """
        return Vector(self.y * other.z - other.y * self.z,
                      other.x * self.z - self.x * other.z,
                      self.x * other.y - other.x * self.y)

    def scalar_product(self, other):
        """
        @Описание
            Скалярное умножение моделируемого вектора на другой
        :param other: вектор, на который скалярно умножается моделируемый вектор
        :return: результат скалярного умножении моделируемого вектора на другой
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def triple_product(self, other1, other2):
        """
        @Описание
            Вычисление смешанного произведения моделируемого вектора с двумя другими
        :param other1: первый из двух векторов, с которыми вычисляется смешанное произведение моделируемого
        :param other2: второй из двух векторов, с которыми вычисляется смешанное произведение моделируемого
        :return: значение смешанного произведения моделирумого вектора с двумя другими заданными
        """
        return self.x * (other1.y * other2.z - other1.z * other2.y) -\
            self.y * (other1.x * other2.z - other1.z * other2.x) +\
            self.z * (other1.x * other2.y - other1.y * other2.x)

    def get_normalized_vector(self):
        """
            Вычисления нормированного на единицу вектора
        :return: моделируемый вектор, нормированный на единицу
        """
        length = len(self)
        return Vector(self.x / length, self.y / length, self.z / length)

    def to_rotate_vector(self, axis_of_rotation, angle_of_rotation):
        """
        @Описание
            Вычисляет вектор, равный моделируемому вектору, повернутому вокруг оси, заданной некоторым вектором на
                заданный угол
        :param axis_of_rotation: ось, вокруг которой вращается моделируемый вектор, заданная вектором (объектом Vector)
        :param angle_of_rotation: угол, на который поворачивается моделируемый вектор (градусы)
        :return: вектор (объект Vector), равный моделируемому вектору, повернутому вокруг оси, заданной вектором
            axis_of_rotation, на угол angle_of_rotation
        """
        # Создание матрицы поворота вокруг вектора rotating_vector на угол angle_of_rotation
        rotation_matrix = RotationMatrix(axis_of_rotation, angle_of_rotation)
        # Вычисление координат повернутого вектора
        rotated_vector_x = rotation_matrix.rotation_matrix[0][0] * self.x +\
            rotation_matrix.rotation_matrix[0][1] * self.y +\
            rotation_matrix.rotation_matrix[0][2] * self.z
        rotated_vector_y = rotation_matrix.rotation_matrix[1][0] * self.x +\
            rotation_matrix.rotation_matrix[1][1] * self.y +\
            rotation_matrix.rotation_matrix[1][2] * self.z
        rotated_vector_z = rotation_matrix.rotation_matrix[2][0] * self.x +\
            rotation_matrix.rotation_matrix[2][1] * self.y +\
            rotation_matrix.rotation_matrix[2][2] * self.z
        return Vector(rotated_vector_x, rotated_vector_y, rotated_vector_z)


class Line:
    """
    @Описание:
        Класс моделирует прямую в трехмерном пространстве, заданную точкой на прямой (которая, в свою очередь, задана
            радииус-вектором - объектом Vector) и направляющим вектором (объектом Vector)

    @Аргументы:
        point_on_line - точка, заданная радиус-вектором - объектом Vector
        directing_vector - направляющий вектор, заданный объектом Vector

    @Поля класса:
        point_on_line - точка, заданная радиус-вектором - объектом Vector. Берется из аргумента point_on_line при
            инициализации
        directing_vector - направляющий вектор, заданный объектом Vector. Берется из аргумента directing_vector при
            инициализации

    @Методы класса
        get_point_on_line(self, coef) - вычисляет точку, заданную радиус-вектором (объектом Vector) на моделируемой
            прямой, расположенную от известной точки на прямой (self.point_on_line) на расстояние, равное длине
            направляющего вектора умноженной на заданный аргументом коэффициент coef
        to_make_line_by_planes - статический метод. Определяет прямую на пересечении двух заданных в аргументах
            плоскостей plane1 и plane2, отдаёт на выход объект Line, моделирующий получившуюся прямую
    """
    def __init__(self, point_on_line, directing_vector):
        self.point_on_line = point_on_line
        self.directing_vector = directing_vector

    def get_point_on_line(self, coef):
        """
        @Описание
            Вычисляет точку, заданную радиус-вектором (объектом Vector) на моделируемой прямой, расположенную от
                известной точки на прямой (self.point_on_line) на расстояние, равное длине направляющего вектора
                умноженной на заданный аргументом коэффициент coef
        :param coef: коэффициент, на который умножается направляющий вектор прямой line для вычисления точки на ней
        :return: искомая точка на прямой line, заданная радиус-вектором (объектом Vector)
        """
        x = self.point_on_line.x + coef * self.directing_vector.x
        y = self.point_on_line.y + coef * self.directing_vector.y
        z = self.point_on_line.z + coef * self.directing_vector.z
        return Vector(x, y, z)

    @staticmethod
    def to_make_line_by_planes(plane1, plane2):
        """
        @Описание
            Метод определяет прямую на пересечении двух заданных плоскостей plane1 и plane2, создает объект Line,
                моделирующий получившуюся прямую
        :param plane1: первая плоскость из двух, на пересечении которых находится искомая прямая
        :param plane2: вторая плоскость из двух, на пересечении которых находится искомая прямая
        :return: объект Line, моделирующий прямую на пересечении двух заданный плоскостей
        """
        # Определение коэффициентов уравнения первой плоскости plane1
        a1 = plane1.normal.x
        b1 = plane1.normal.y
        d1 = plane1.coef_d
        # Определение коэффициентов уравнения второй плоскости plane2
        a2 = plane2.normal.x
        b2 = plane2.normal.y
        d2 = plane2.coef_d
        # Вычисление некоторой точки общей для плоскостей plane1 и plane2
        point_on_line_z = 0
        point_on_line_y = (a2 * d1 - a1 * d2) / (a1 * b2 - a2 * b1)
        point_on_line_x = -(d1 + b1 * point_on_line_y) / a1
        point_on_line = Vector(point_on_line_x, point_on_line_y, point_on_line_z)
        # Вычисление направляющего вектора для прямой - пересечения плоскостей plane1 и plane2
        directing_vector = plane1.normal * plane2.normal

        return Line(point_on_line, directing_vector)


class Plane:
    """
    @Описание:
        Класс моделирует плоскость в трехмерном пространстве, заданную вектором-нормалью (объектом Vector) и
            коэффициентом D из уравнения плоскости вида Ax + By + Cz + D = 0

    @Аргументы:
        normal - вектор-нормаль, заданный объектом Vector
        coef_d - коэффициент D из уравнения плоскости вида Ax + By + Cz + D = 0

    @Поля класса:
        normal - вектор-нормаль, заданный объектом Vector. Берется из аргумента normal при инициализации
        coef_d - коэффициент D из уравнения плоскости вида Ax + By + Cz + D = 0. Берется из аргумента coef_d при
            инициализации

    @Методы класса
        to_make_plane_by_points(point1, point2, point3) - статический метод. Создает объект Plane, моделирующий
            плоскость, проходящую через три точки, заданных радиус-векторами (объектами Vector) - point1, point2, point3

    """
    def __init__(self, normal, coef_d):
        self.normal = normal
        self.coef_d = coef_d

    @staticmethod
    def to_make_plane_by_points(point1, point2, point3):
        """
        @Описание
            Метод вычисляет уравнение плоскости по трем заданным радиус-векторами точкам, принадлежащим этой плоскости и
                создает объект Plane, соответствующий вычисленной плоскости
        :param point1: первая точка, заданная радиус-вектором (объектом Vector), принадлежащая искомой плоскости
        :param point2: вторая точка, заданная радиус-вектором (объектом Vector), принадлежащая искомой плоскости
        :param point3: третья точка, заданная радиус-вектором (объектом Vector), принадлежащая искомой плоскости
        :return: объект Plane, моделирущий найденную плоскость
        """
        x1 = point1.x
        y1 = point1.y
        z1 = point1.z

        x2 = point2.x
        y2 = point2.y
        z2 = point2.z

        x3 = point3.x
        y3 = point3.y
        z3 = point3.z

        m21 = x2 - x1
        m22 = y2 - y1
        m23 = z2 - z1
        m31 = x3 - x1
        m32 = y3 - y1
        m33 = z3 - z1

        normal_x = m22 * m33 - m23 * m32
        normal_y = -(m21 * m33 - m23 * m31)
        normal_z = m21 * m32 - m22 * m31
        normal = Vector(normal_x, normal_y, normal_z)

        d = -x1 * (m22 * m33 - m23 * m32) + y1 * (m21 * m33 - m23 * m31) - z1 * (m21 * m32 - m22 * m31)

        return Plane(normal, d)

    @staticmethod
    def to_make_plane_by_lines(line1, line2):
        """
        @Описание
            Метод вычисляет уравнение плоскости по двум не секущимся прямым, принадлежащим этой плоскости и создает
                объект Plane, соответствующий вычисленной плоскости. Если прямые секущии, то возвращается None
        :param line1: первая прямая, принадлежащая искомой плоскости (объект Line)
        :param line2: вторая прямая, принадлежащая искомой плоскости (объект Line)
        :return:
        """
        if line1.directing_vector.triple_product(line2.directing_vector,
                                                 line1.point_on_line - line2.point_on_line) == 0:
            point1 = line1.point
            point2 = line1.get_point_on_line(1)
            point3 = line2.point
            return Plane.to_make_plane_by_points(point1, point2, point3)
        else:
            return None


class CanonicalEllipsoid:
    """
    @Описание:
        Класс моделирует канонический эллипсоид в трехмерном пространстве, заданный тремя длинами полуосей a, b и c,
            расположеными, соответственно, параллельно осям x, y, z

    @Аргументы:
        axis_a - полуось эллипсоида, расположенная параллельно оси x
        axis_b - полуось эллипсоида, расположенная параллельно оси y
        axis_c - полуось эллипсоида, расположенная параллельно оси z

    @Поля класса:
        axis_a - полуось эллипсоида, расположенная параллельно оси x. Берется из аргумента axis_a при инициализации
        axis_b - полуось эллипсоида, расположенная параллельно оси y. Берется из аргумента axis_b при инициализации
        axis_c - полуось эллипсоида, расположенная параллельно оси z. Берется из аргумента axis_c при инициализации
    """
    def __init__(self, axis_a, axis_b, axis_c):
        self.axis_a = axis_a
        self.axis_b = axis_b
        self.axis_c = axis_c


class RotationMatrix:
    """
    @Описание:
        Класс моделирует матрицу поворота вокруг заданной оси на заданный угол в трехмерном пространстве

    @Аргументы:
        axis_of_rotation - ось вращения, заданная направляющим вектором (объектом Vector)
        angle_of_rotation - угол вращения (градусы)

    @Поля класса:
        rotation_matrix - матрица 3x3 (numpy) - матрица поворота в трехмерном пространстве вокруг оси, заданной вектором
            axis_of_rotation на угол angle_of_rotation. Коэффициенты матрицы вычисляются при инициализации
    """
    def __init__(self, axis_of_rotation, angle_of_rotation):
        angle_of_rotation_in_rad = numpy.deg2rad(angle_of_rotation)
        sin_of_angle = math.sin(angle_of_rotation_in_rad)
        cos_of_angle = math.cos(angle_of_rotation_in_rad)

        matrix_coef11 = cos_of_angle + (1 - cos_of_angle) * axis_of_rotation.x * axis_of_rotation.x
        matrix_coef12 = (1 - cos_of_angle) * axis_of_rotation.x * axis_of_rotation.y - sin_of_angle * axis_of_rotation.z
        matrix_coef13 = (1 - cos_of_angle) * axis_of_rotation.x * axis_of_rotation.z + sin_of_angle * axis_of_rotation.y

        matrix_coef21 = (1 - cos_of_angle) * axis_of_rotation.x * axis_of_rotation.y + sin_of_angle * axis_of_rotation.z
        matrix_coef22 = cos_of_angle + (1 - cos_of_angle) * axis_of_rotation.y * axis_of_rotation.y
        matrix_coef23 = (1 - cos_of_angle) * axis_of_rotation.y * axis_of_rotation.z - sin_of_angle * axis_of_rotation.x

        matrix_coef31 = (1 - cos_of_angle) * axis_of_rotation.x * axis_of_rotation.z - sin_of_angle * axis_of_rotation.y
        matrix_coef32 = (1 - cos_of_angle) * axis_of_rotation.y * axis_of_rotation.z + sin_of_angle * axis_of_rotation.x
        matrix_coef33 = cos_of_angle + (1 - cos_of_angle) * axis_of_rotation.z * axis_of_rotation.z

        self.rotation_matrix = numpy.array([[matrix_coef11, matrix_coef12, matrix_coef13],
                                            [matrix_coef21, matrix_coef22, matrix_coef23],
                                            [matrix_coef31, matrix_coef32, matrix_coef33]])


def solution_of_quadratic_equation(a, b, c):
    """
    @Описание
        Метод возвращает два решения квадратного уравнения вида ax ** 2 + bx + c = 0
    :param a: коэффициент a в квадратном уравнении вида ax ** 2 + bx + c = 0
    :param b: коэффициент b в квадратном уравнении вида ax ** 2 + bx + c = 0
    :param c: коэффициент c в квадратном уравнении вида ax ** 2 + bx + c = 0
    :return: два решения квадратного уравнения с заданными коэффициентами. Если заданное уравнение имеет одно решение,
        оба возвращаемых решения x1 и x2 равны между собой
    """
    discriminant = b ** 2 - 4 * a * c
    x1 = (-b + math.sqrt(discriminant)) / (2 * a)
    x2 = (-b - math.sqrt(discriminant)) / (2 * a)
    return x1, x2


def point_of_intersection_of_line_and_plane(line, plane):
    """
    @Описание
        Метод возвращает точку пересечения заданных в аргументах прямой и площади, заданную радиус-вектором (объектом
            Vector), в том случае, если прямая и плоскость не параллельны. Если параллельны, то возвращает None
    :param line: прямая, заданная объектом Line, точка пересечения которой с плоскостью plane вычисляется
    :param plane: плоскость, заданная объектом Plane, точка пересечения которой с прямой line вычисляется
    :return: если прямая line и плоскость plane не параллельны, точка пересечения прямой line и плоскасти plane,
        заданную радиус-вектором (объект Vector), если параллельны, то None
    """
    scalar_product_of_line_and_plane_normal = line.directing_vector.scalar_product(plane.normal)
    # Проверка того, что line и plane не параллельны
    if scalar_product_of_line_and_plane_normal != 0:
        coef_of_direct_vect_to_intersection = -(plane.normal.x * line.point_on_line.x +
                                                plane.normal.y * line.point_on_line.y +
                                                plane.normal.z * line.point_on_line.z + plane.d_coef) /\
                                              scalar_product_of_line_and_plane_normal
        return line.get_point_on_line(coef_of_direct_vect_to_intersection)
    else:
        return None


def projection_of_line_on_plane(projected_line, plane):
    """
    @Описание
        Метод возвращает прямую - проекцию заданной прямой на заданную плоскость (объект Line)
    :param projected_line: проектируемая на плоскость plane прямая (объект line)
    :param plane: плоскость, на которую проектируется прямая projected_line (объект plane)
    :return: прямая (объект line) - проекция прямой projected_line на плоскость plane
    """
    point_of_intersection = point_of_intersection_of_line_and_plane(projected_line, plane)
    # Проверка того, пересекается ли прямая projected_line и плоскость plane
    if point_of_intersection is not None:
        perpendicular_plane_to_plane_with_projected_line =\
            Plane.to_make_plane_by_lines(projected_line, Line(point_of_intersection, plane.normal))
    else:
        perpendicular_plane_to_plane_with_projected_line =\
            Plane.to_make_plane_by_lines(projected_line, Line(projected_line.point_on_line, plane.normal))

    return Line.to_make_line_by_planes(plane, perpendicular_plane_to_plane_with_projected_line)


def points_of_intersections_of_line_and_canonical_ellipsoid(line, ellipsoid):
    """
    @Описание
        Метод возвращает точки пересечения заданных в аргументах прямой и канонического эллипсоида, заданную
            радиус-векторами (объектами Vector)
    :param line: прямая, заданная объектом Line, точки пересечения которой с эллипсоидом ellipsoid
    :param ellipsoid: эллипсоид, заданный объектом CanonicalEllipsoid, точки пересечения которого с прямой line
    :return: две точки пересечения прямой line и эллипсоида ellipsoid, заданные радиус-векторами (объектами Vector)
    """
    # Вычисление коэффициентов для квадратного уравнения
    a_coef = (line.directing_vector.x / ellipsoid.axis_a) ** 2 + (line.directing_vector.y / ellipsoid.axis_b) ** 2 \
        + (line.directing_vector.z / ellipsoid.axis_c) ** 2
    b_coef = 2 * (line.point_on_line.x * line.directing_vector.x / (ellipsoid.axis_a * ellipsoid.axis_a) +
                  line.point_on_line.y * line.directing_vector.y / (ellipsoid.axis_b * ellipsoid.axis_b) +
                  line.point_on_line.z * line.directing_vector.z / (ellipsoid.axis_c * ellipsoid.axis_c))
    c_coef = (line.point_on_line.x / ellipsoid.axis_a) ** 2 + (line.point_on_line.y / ellipsoid.axis_b) ** 2 \
        + (line.point_on_line.z / ellipsoid.axis_c) ** 2 - 1
    coef_of_direct_vect_to_intersection1, coef_of_direct_vect_to_intersection2 =\
        solution_of_quadratic_equation(a_coef, b_coef, c_coef)

    return line.get_point_on_line(coef_of_direct_vect_to_intersection1),\
        line.get_point_on_line(coef_of_direct_vect_to_intersection2)


def to_found_point_of_intersection_of_line_and_canonical_ellipsoid_nearest_to_stating_point_of_line(line, ellipsoid):
    """
    @Описание
        Метод возвращает ближайшую к точке отсчета line.point_on_line точку из двух точек пересечения заданных в
            аргументах прямой и канонического эллипсоида, заданную радиус-векторам (объектом Vector)
    :param line: прямая, заданная объектом Line, точки пересечения которой с эллипсоидом ellipsoid
    :param ellipsoid: эллипсоид, заданный объектом CanonicalEllipsoid, точки пересечения которого с прямой line
    :return: ближайшая к line.point_on_line точка из двух точек пересечения прямой line и эллипсоида ellipsoid, заданная
        радиус-вектором (объект Vector)
    """
    # Вычисление двух точек пересечения line и ellipsoid
    point_of_intersection1, point_of_intersection2 = points_of_intersections_of_line_and_canonical_ellipsoid(line,
                                                                                                             ellipsoid)
    # Вычисление расстояний от точек пересечения до line.point_on_line
    dist1 = len(Vector(line.point_on_line.x - point_of_intersection1.x, line.point_on_line.y - point_of_intersection1.y,
                       line.point_on_line.z - point_of_intersection1.z))
    dist2 = len(Vector(line.point_on_line.x - point_of_intersection2.x, line.point_on_line.y - point_of_intersection2.y,
                       line.point_on_line.z - point_of_intersection2.z))
    if dist2 >= dist1:
        return point_of_intersection1
    else:
        return point_of_intersection2


def plane_touched_canonical_ellipsoid(point, ellipsoid):
    """
    @Описание
        Возращает плоскость (объект Plane) касающуюся заданного эллипсоида в заданной точке
    :param point: точка, заданная радиус-вектором (объектом Vector), касательная плоскость эллипсоиду ellipsoid в
        которой вычисляется уравнение искомой плоскости
    :param ellipsoid: эллипсоид (объект CanonicalEllipsoid), уравнение касательной плоскости к которому в точке point
        вычисляется
    :return: плоскость (объект Plane) касающуюся эллипсоида ellipsoid в точке point
    """
    normal = Vector(point.x / (ellipsoid.axis_a * ellipsoid.axis_a), point.y / (ellipsoid.axis_b * ellipsoid.axis_b),
                    point.z / (ellipsoid.axis_c * ellipsoid.axis_c))
    d = -((point.x * point.x) / (ellipsoid.axis_a * ellipsoid.axis_a) +
          (point.y * point.y) / (ellipsoid.axis_b * ellipsoid.axis_b) +
          (point.z * point.z) / (ellipsoid.axis_c * ellipsoid.axis_c))
    return Plane(normal, d)
