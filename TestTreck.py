import Packeges as pack


# Объекты класса Satellite моделируют поведение спутника дистанционного зондирования и его полосы захвата
class Satellite:

    # Метод coordPredict принимает объект time класса datetime, который содержит дату и время в формате utc. Метод coordPredict прогнозирует координаты спутника в момент времени time по строкам tle, используя алгоритм для предсказания координат низкоорбитальных спутников (период обращения менее 225 минут) и возвращает координаты в формате Coordinate
    def geoCoordPredict(self):
        lon, lat, alt = self.orbit.get_lonlatalt(self.utc_time)                                                         ## Прогнозирование широты lat (градусы), долготы long (градусы), высоты над уровнем моря alt (километры) с помощью метода get_lonlatalt, примененного на объекте orbit по времени time
        self.geoCoord = Coordinate(lon, lat, alt)

    def swathCoords(self, treck):
        for satCoords in treck:
            satGroundMovDir = self.satGroundMovementDirect(satCoords.decCoords, satCoords.velVect)

            leftSwathDir = geometry.toRotVect(-satCoords.decCoords.radVect, satGroundMovDir, self.swathAng / 2)
            rightSwathDir = geometry.toRotVect(-satCoords.decCoords.radVect, satGroundMovDir, -self.swathAng / 2)

            decLeftSwathCoord = self.nearestEllipsoidIntersection(geometry.Straight(satCoords.decCoords, leftSwathDir))
            decRightSwathCoord = self.nearestEllipsoidIntersection(geometry.Straight(satCoords.decCoords, rightSwathDir))

            self.leftSwathCoordList.append(self.orbit.decardToGeoCoordinates(decLeftSwathCoord, satCoords.utc_time))
            self.rightSwathCoordList.append(self.orbit.decardToGeoCoordinates(decRightSwathCoord, satCoords.utc_time))

    ## Метод coordPredict принимает объект time класса datetime, который содержит дату и время в формате utc. Метод coordPredict прогнозирует координаты спутника в момент времени time по строкам tle, используя алгоритм для предсказания координат низкоорбитальных спутников (период обращения менее 225 минут) и возвращает координаты в формате Coordinate
    def coordsPredict(self):
        self.coords = self.orbit.get_all_coords(self.utc_time)

    #def toMakeAreaOfObs(self):
    #    self.leftSwathCoordList
    #    self.areaOfObs = Polygon()

    def satGroundMovementDirect(self, decCoords, velVect):
        satMovStraight = geometry.Straight(decCoords, velVect)
        straightToCenter = geometry.Straight(decCoords, decCoords.radVect)
        groundCord = self.nearestEllipsoidIntersection(straightToCenter)
        groundPlane = geometry.planeTouchedCanonEllipsoid(groundCord, self.ellipsoid)
        straightProj = geometry.projStraightOnPlane(satMovStraight, groundPlane)
        return geometry.normVect(straightProj.vector)



    def treckTest(self):
        f = open('D://treck.txt', 'w')
        fl  = open('D://left.txt', 'w')
        fr = open('D://right.txt', 'w')
        for point1 in self.satTrack:
            f.write(str(point1.geoCoord) + '\n')
        for point1 in self.leftSwathCoordList:
            fl.write(str(point1.geoCoord) + '\n')
        for point1 in self.rightSwathCoordList:
            fr.write(str(point1.geoCoord) + '\n')


class ShapePolygon:

    class Segment:
        def __init__(self, lat, long):
            self.lat = lat
            self.long = long
            self.gripsCount = 0

    def __init__(self, shpFileAddress):
        self.shpFile = shapefile.Reader(shpFileAddress)
        self.segmentsList = []

    def splitPolygon(self, latFineness, longFineness):
        shpFileList = list(self.shpFile.iterShapes())

        for shape in shpFileList:

            [leftLongBorder, downLatBorder, rightLongBorder, upLatBorder] = shape.bbox

            latOfDownSigment = downLatBorder + latFineness / 2
            latOfUpSigment = upLatBorder - latFineness / 2
            longOfLeftSigment = rightLongBorder + longFineness / 2
            longOfRightSigment = leftLongBorder - longFineness / 2

            latOfPolygonsSigments = numpy.arange(latOfDownSigment, latOfUpSigment, latFineness)
            longOfPolygonsSigments = numpy.arange(longOfRightSigment, longOfLeftSigment, longFineness)

            polygon = Polygon(shape.points)

            for latSegment in latOfPolygonsSigments:
                for longSegment in longOfPolygonsSigments:

                    point = Point(longSegment, latSegment)

                    if polygon.contains(point):
                        self.segmentsList.append(ShapePolygon.Segment(latSegment, longSegment))

if __name__ == '__main__':
    utc_time1 = datetime(2018, 6, 15, 0, 0, 0)
    utc_time2 = datetime(2018, 6, 17, 0, 0, 0)

    startTime = datetime.now()
    sat = Satellite('ISS (ZARYA)', None, 3.5)
    print(datetime.now() - startTime)

    startTime = datetime.now()
    sat.predictTreck(utc_time1, utc_time2, 1, None)
    print(len(sat.satTrack))
    print(datetime.now() - startTime)
    #polygon = ShapePolygon("D:/Shapefiles/Utrish")
    #polygon.splitPolygon(0.01, 0.01)