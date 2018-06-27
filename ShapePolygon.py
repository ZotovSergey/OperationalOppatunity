import Packeges as pack
import math

class ShapePolygonPack:

    def __init__(self):
        self.shapeList = []
        self.allSpace = 0
        self.fullSegmentList = []

    def toReadShapeFile(self, shpFileAddress):
        shpFile = pack.shapefile.Reader(shpFileAddress)
        shpFileList = list(shpFile.iterShapes())
        for shape in shpFileList:
            self.shapeList.append(self.ShapePolygon(shape))

    def toSplitPoligons(self, latFineness, longFineness, earth):
        self.allSpace = 0
        for shapePolygon in self.shapeList:
            shapePolygon.toSplitPolygon(latFineness, longFineness, earth)
            self.allSpace += shapePolygon.fullSpace
            self.fullSegmentList += shapePolygon.segmentsList

    def toCalcPercents(self):
        segmentList = self.fullSegmentList
        i = 1
        spaceList = []
        while len(segmentList) > 0:
            newList = []
            currentSpace = 0
            for segment in segmentList:
                if segment.gripsCount >= i:
                    if segment.gripsCount > i:
                        newList.append(segment)
                    currentSpace += segment.space
            spaceList.append(currentSpace / self.allSpace * 100)
            segmentList = newList
            i += 1
        return spaceList

    def toCalcPercentsWithSun(self):
        segmentList = self.fullSegmentList
        i = 1
        spaceList = []
        while len(segmentList) > 0:
            newList = []
            currentSpace = 0
            for segment in segmentList:
                if segment.gripsCountWithSun >= i:
                    if segment.gripsCountWithSun > i:
                        newList.append(segment)
                    currentSpace += segment.space
            spaceList.append(currentSpace / self.allSpace * 100)
            segmentList = newList
            i += 1
        return spaceList

    def toCalcPercentsWithCloud(self):
        segmentList = self.fullSegmentList
        i = 1
        spaceList = []
        while len(segmentList) > 0:
            newList = []
            currentSpace = 0
            for segment in segmentList:
                if segment.gripsCountWithCloud >= i:
                    if segment.gripsCountWithCloud > i:
                        newList.append(segment)
                    currentSpace += segment.space
            spaceList.append(currentSpace / self.allSpace * 100)
            segmentList = newList
            i += 1
        return spaceList

    def toCalcPercentsWithSunCloud(self):
        segmentList = self.fullSegmentList
        i = 1
        spaceList = []
        while len(segmentList) > 0:
            newList = []
            currentSpace = 0
            for segment in segmentList:
                if segment.gripsCountWithSunCloud >= i:
                    if segment.gripsCountWithSunCloud > i:
                        newList.append(segment)
                    currentSpace += segment.space
            spaceList.append(currentSpace / self.allSpace * 100)
            segmentList = newList
            i += 1
        return spaceList

    class ShapePolygon:

        def __init__(self, shape):
            self.shape = shape
            self.segmentsList = []
            [self.leftLongBorder, self.downLatBorder, self.rightLongBorder, self.upLatBorder] = shape.bbox
            self.center = pack.GeoCoordinate((self.leftLongBorder + self.rightLongBorder) / 2,
                                             (self.upLatBorder + self.downLatBorder) / 2, 0)
            self.radius = pack.distBetweenDecCoord(self.center, pack.GeoCoordinate(self.rightLongBorder,
                                                                                   self.downLatBorder, 0))
            self.fullSpace = 0
            self.cloudDistr = []
            self.intervals = []

        def toPutCloudDistr(self, cloudDistr, intervals):
            self.intervals = intervals
            scoreSum = pack.np.zeros(len(cloudDistr))
            for i in range(0, len(cloudDistr)):
                for score in cloudDistr[i]:
                    scoreSum += score
                for score in cloudDistr[i]:
                    score /= scoreSum
            self.cloudDistr = cloudDistr

        def toSplitPolygon(self, latFineness, longFineness, earth):
            f = open('D://pol.txt', 'w')

            self.fullSpace = 0

            latOfDownSigment = self.downLatBorder + latFineness / 2
            latOfUpSigment = self.upLatBorder - latFineness / 2
            longOfLeftSigment = self.rightLongBorder + longFineness / 2
            longOfRightSigment = self.leftLongBorder - longFineness / 2

            latOfPolygonsSigments = pack.np.arange(latOfDownSigment, latOfUpSigment, latFineness)
            longOfPolygonsSigments = pack.np.arange(longOfRightSigment, longOfLeftSigment, longFineness)

            latGrid = pack.np.arange(self.downLatBorder, self.upLatBorder, latFineness)

            latSpaceGrid = self.toCalculateSpaceGrid(latGrid, longFineness, earth)

            polygon = pack.Polygon(self.shape.points)

            i = 0
            for latSegment in latOfPolygonsSigments:
                for longSegment in longOfPolygonsSigments:

                    point = pack.Point(longSegment, latSegment)

                    if polygon.contains(point):
                        self.segmentsList.append(self.Segment(longSegment, latSegment, latSpaceGrid[i]))
                        self.fullSpace += latSpaceGrid[i]
                        f.write(str(self.Segment(longSegment, latSegment, latSpaceGrid[i])) + '\n')
                i += 1

        def toCalculateSpaceGrid(self, latOfPolygonsSigments, longFineness, earth):
            a = earth.ellipsoid.a
            b = earth.ellipsoid.c
            latSpaceGrid = []
            lowSpace = self.toCalculateSpaceFromEquator(a, b, latOfPolygonsSigments[0])
            for gridStr in latOfPolygonsSigments[1 :]:
                upSpace = self.toCalculateSpaceFromEquator(a, b, gridStr)
                latSpaceGrid.append((upSpace - lowSpace) * longFineness / 360)
                lowSpace = upSpace
            return latSpaceGrid

        def toCalculateSpaceFromEquator(self, a, b, angle):
            y = b * math.sin(angle * math.pi / 180)

            A = a * a - b * b
            B = A ** 0.5
            C = b ** 4
            D = (C + y * y * A) ** 0.5

            return 2 * math.pi / b * D * ((C * math.log(B * D + y * A)) / (B * D) + y)

        class Segment:
            def __init__(self, long, lat, space):
                self.point = pack.Point(long, lat)
                self.geoCoord = pack.GeoCoordinate(long, lat, 0)
                self.gripsCount = 0
                self.gripsCountWithSun = 0
                self.gripsCountWithCloud = 0
                self.gripsCountWithSunCloud = 0
                self.space = space

            def addGripsCount(self):
                self.gripsCount += 1
                #print(str(self.geoCoord.lat) + '\t' + str(self.geoCoord.long))


            def addGripsCountWithSun(self):
                self.gripsCountWithSun += 1

            def addGripsCountWithCloud(self):
                self.gripsCountWithCloud += 1

            def addGripsCountWithSunCloud(self):
                self.gripsCountWithSunCloud += 1

            def __str__(self):
                return str(self.geoCoord) + '\t' + str(self.space)