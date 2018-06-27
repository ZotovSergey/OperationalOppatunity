import math
import numpy as np

class Point:
    def __init__(self, x, y, z):
        self.radVect = Vector(x, y, z)

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def lenght(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

class Straight:
    def __init__(self, point, vector):
        self.point = point
        self.vector = vector

class Plane:
    def __init__(self, normal, d):
        self.normal = normal
        self.d = d

class CanonEllipsoid:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

class RotationMatrix:
    def __init__(self, rotAxis, angle):
        sinA = math.sin(angle)
        cosA = math.cos(angle)

        rotMatrix11 = cosA + (1 - cosA) * rotAxis.x * rotAxis.x
        rotMatrix12 = (1 - cosA) * rotAxis.x * rotAxis.y - sinA * rotAxis.z
        rotMatrix13 = (1 - cosA) * rotAxis.x * rotAxis.z + sinA * rotAxis.y

        rotMatrix21 = (1 - cosA) * rotAxis.x * rotAxis.y + sinA * rotAxis.z
        rotMatrix22 = cosA + (1 - cosA) * rotAxis.y * rotAxis.y
        rotMatrix23 = (1 - cosA) * rotAxis.y * rotAxis.z - sinA * rotAxis.x

        rotMatrix31 = (1 - cosA) * rotAxis.x * rotAxis.z - sinA * rotAxis.y
        rotMatrix32 = (1 - cosA) * rotAxis.y * rotAxis.z + sinA * rotAxis.x
        rotMatrix33 = cosA + (1 - cosA) * rotAxis.z * rotAxis.z

        #normVector = normVect(rotAxis)
        #lam0 = math.cos(angle / 2)
        #lam1 = normVector.x * math.sin(angle / 2)
        #lam2 = normVector.y * math.sin(angle / 2)
        #lam3 = normVector.z * math.sin(angle / 2)

        #rotMatrix11 = 1 - 2 * (lam2 * lam2 + lam3 * lam3)
        #rotMatrix12 = 2 * (lam1 * lam2 - lam0 * lam3)
        #rotMatrix13 = 2 * (lam1 * lam3 + lam0 * lam2)

        #rotMatrix21 = 2 * (lam1 * lam2 + lam0 * lam3)
        #rotMatrix22 = 1 - 2 * (lam1 * lam1 + lam3 * lam3)
        #rotMatrix23 = 2 * (lam2 * lam3 - lam0 * lam1)

        #rotMatrix31 = 2 * (lam1 * lam3 - lam0 * lam2)
        #rotMatrix32 = 2 * (lam2 * lam3 + lam0 * lam1)
        #rotMatrix33 = 1 - 2 * (lam1 * lam1 + lam2 * lam2)

        self.rotMatrix = np.array([[rotMatrix11, rotMatrix12, rotMatrix13], [rotMatrix21, rotMatrix22, rotMatrix23],
                                [rotMatrix31, rotMatrix32, rotMatrix33]])

def quadrEquationSol(a, b, c):
    D = b ** 2 - 4 * a * c
    x1 = (-b + math.sqrt(D)) / (2 * a)
    x2 = (-b - math.sqrt(D)) / (2 * a)
    return x1, x2

def pointOnStraight(straight, coef):
    x = straight.point.radVect.x + coef * straight.vector.x
    y = straight.point.radVect.y + coef * straight.vector.y
    z = straight.point.radVect.z + coef * straight.vector.z
    return Point(x, y, z)

def scalMult(vect1, vect2):
    return vect1.x * vect2.x + vect1.y * vect2.y + vect1.z * vect2.z

def vectMult(vect1, vect2):
    return Vector(vect1.y * vect2.z - vect2.y * vect1.z,
                       vect2.x * vect1.z - vect1.x * vect2.z,
                        vect1.x * vect2.y - vect2.x * vect1.y)

def normVect(vect):
    long = math.sqrt(vect.x * vect.x + vect.y * vect.y + vect.z * vect.z)
    return Vector(vect.x / long, vect.y / long, vect.z / long)

def toMultMatrixOnjVect3D(matrix, vect):
    x_new = matrix[0][0] * vect.x + matrix[0][1] * vect.y + matrix[0][2] * vect.z
    y_new = matrix[1][0] * vect.x + matrix[1][1] * vect.y + matrix[1][2] * vect.z
    z_new = matrix[2][0] * vect.x + matrix[2][1] * vect.y + matrix[2][2] * vect.z
    return Vector(x_new, y_new, z_new)

def toRotVect(vect, axis, rotAngle):
    rotMatrix = RotationMatrix(axis, rotAngle)
    return toMultMatrixOnjVect3D(rotMatrix.rotMatrix, vect)

def planeByPoints(point1, point2, point3):
    x1 = point1.radVect.x
    y1 = point1.radVect.y
    z1 = point1.radVect.z

    x2 = point2.radVect.x
    y2 = point2.radVect.y
    z2 = point2.radVect.z

    x3 = point3.radVect.x
    y3 = point3.radVect.y
    z3 = point3.radVect.z

    m21 = x2 - x1
    m22 = y2 - y1
    m23 = z2 - z1
    m31 = x3 - x1
    m32 = y3 - y1
    m33 = z3 - z1

    norm_x = m22 * m33 - m32 * m23
    norm_y = m31 * m23 - m21 * m33
    norm_z = m21 * m32 - m31 * m22
    normal = Vector(norm_x, norm_y, norm_z)

    d = x1 * m32 * m23 + m21 * y1 * m33 + m31 * m22 * z1 - x1 * m22 * m33 - m21 * m32 * z1 - m31 * y1 * m23

    return Plane(normal, d)

def planeByStraights(straight1, straight2):
    point1 = straight1.point
    point2 = pointOnStraight(straight1, 1)
    point3 = straight2.point
    return planeByPoints(point1, point2, point3)

def straightByPlanes(plane1, plane2):
    a1 = plane1.normal.x
    b1 = plane1.normal.y
    #c1 = plane1.normal.z
    d1 = plane1.d

    a2 = plane2.normal.x
    b2 = plane2.normal.y
    #c2 = plane2.normal.z
    d2 = plane2.d

    startPoint_z = 0
    startPoint_y = (a2 * d1 - a1 * d2) / (a1 * b2 - a2 * b1)
    startPoint_x = -(d1 + b1 * startPoint_y) / a1
    startPoint = Point(startPoint_x, startPoint_y, startPoint_z)

    dirVect = vectMult(plane1.normal, plane2.normal)

    return Straight(startPoint, dirVect)

def straightPlaneIntersectionOrProj(straight, plane, retProjIfParall):
    if scalMult(straight.vector, plane.normal) != 0:
        intersectPointCoef = -(plane.normal.x * straight.point.radVect.x + plane.normal.y * straight.point.radVect.y
              + plane.normal.z * straight.point.radVect.z + plane.d) / (plane.normal.x * straight.vector.x
                + plane.normal.y * straight.vector.y + plane.normal.z * straight.vector.z)
        return pointOnStraight(straight, intersectPointCoef)
    else:
        if retProjIfParall:
            newStraight = Straight(straight.point, plane.normal)
            return straightPlaneIntersectionOrProj(newStraight, plane, False)
        else:
            return 0

def projStraightOnPlane(straight, plane):
    interPoint = straightPlaneIntersectionOrProj(straight, plane, True)
    perpPlane = planeByStraights(straight, Straight(interPoint, plane.normal))
    return straightByPlanes(plane, perpPlane)

def nearestEllipsoidIntersection(straight, ellipsoid):
    inter1, inter2 = straightCanonEllipsoidIntersection(straight, ellipsoid)
    dist1 = Vector(straight.point.radVect.x - inter1.radVect.x,
                            straight.point.radVect.y - inter1.radVect.y,
                            straight.point.radVect.z - inter1.radVect.z).lenght()
    dist2 = Vector(straight.point.radVect.x - inter2.radVect.x,
                            straight.point.radVect.y - inter2.radVect.y,
                            straight.point.radVect.z - inter2.radVect.z).lenght()
    if dist2 > dist1:
        return inter1
    else:
        return inter2

def straightCanonEllipsoidIntersection(straight, ellipsoid):
    a = (straight.vector.x / ellipsoid.a) ** 2 + (straight.vector.y / ellipsoid.b) ** 2 \
        + (straight.vector.z / ellipsoid.c) ** 2
    b = 2 * (straight.point.radVect.x * straight.vector.x / (ellipsoid.a * ellipsoid.a)
             + straight.point.radVect.y * straight.vector.y / (ellipsoid.b * ellipsoid.b)
             + straight.point.radVect.z * straight.vector.z / (ellipsoid.c * ellipsoid.c))
    c = (straight.point.radVect.x / ellipsoid.a) ** 2 + (straight.point.radVect.y / ellipsoid.b) ** 2 \
        + (straight.point.radVect.z / ellipsoid.c) ** 2 - 1
    intersectCoef1, intersectCoef2 = quadrEquationSol(a, b, c)

    return pointOnStraight(straight, intersectCoef1), pointOnStraight(straight, intersectCoef2)

def planeTouchedCanonEllipsoid(point, ellipsoid):
    normal = Vector(point.radVect.x / (ellipsoid.a * ellipsoid.a), point.radVect.y / (ellipsoid.b * ellipsoid.b),
                    point.radVect.z / (ellipsoid.c * ellipsoid.c))
    d = -((point.radVect.x * point.radVect.x) / (ellipsoid.a * ellipsoid.a)
          + (point.radVect.y * point.radVect.y) / (ellipsoid.b * ellipsoid.b)
          + (point.radVect.z * point.radVect.z) / (ellipsoid.c * ellipsoid.c))
    return Plane(normal, d)