import Packeges as pack
import math
import matplotlib.pyplot as plt
import scipy.fftpack
import random
import matplotlib.pylab as pylab


class SatelliteGroup:

    def __init__(self, earth, polygons, resultAddress):
        self.satList = []
        self.earth = earth
        self.polygons = polygons
        self.file = open(resultAddress, 'w')

    def toCreatSatellite(self, satName, tleAdress, swathAng, address):
        self.satList.append(self.Satellite(satName, tleAdress, swathAng, self.earth, self.polygons, address))

    class Satellite:

        def __init__(self, satName, tleAdress, swathAng, earth, polygons, address):                                     # Конструктор класса Satellite принимает название спутника в системе NORAD satName; адрес файла, содержащего строки tle (допустимо значение None) и угол поля зрения прибора на борту swathAng
            self.satName = satName                                                                                      # Присвоение полю satName значения satName
            self.tle = pack.tlefile.read(satName, tleAdress)                                                            # Присвоение полю tle строк tle из файла по адресу tleAdress или, если tleAdress=None, скаченного с сайта www.celestrak.com
            self.swathAng = swathAng / 2                                                                                # Присвоение полю swathAng значения swathAng
            self.radSwathAng = math.pi * self.swathAng / 180
            self.earth = earth
            self.coord = self.SatelliteCoordinates(pack.DecartCoordinate(pack.MyGeometry.Point(1, 1, 1)),
                                                   pack.MyGeometry.Vector(1, 1, 1), pack.datetime.now(), self.earth)
            self.satTracks = []                                                                                         # Объявление списка satTrack, в который будут добавляться объекты Coordinate, опредедяяющие трэк движения спутника
            #self.satTrack = []
            self.swathCoordList = []                                                                                    # Объявление списка leftSwathPointsList, в который будут добавляться объекты класса Coordinate - координаты левой границы полосы захвата
            self.leftSwathCoordList = []
            self.rightSwathCoordList = []
            self.areaOfObs = pack.Polygon()                                                                             # Объявление поля areaOfObs для класса Polygon, обозначающего полосу захвата на плоскости
            self.orbit = pack.MyOrbital(self.satName, line1=self.tle.line1, line2=self.tle.line2)                       # Создание объекта orbit класса Orbital, который принимает имя спутника satName в системе NORAD, первую и вторую строки tle line1 и line2 из объекта tle
            self.polygons = polygons
            self.file = open(address + 'Ход выполнения задачи.txt', 'w')
            self.file_sun = open(address + '(Солнце) Ход выполнения задачи.txt', 'w')
            self.file_cloud = open(address + '(Облака) Ход выполнения задачи.txt', 'w')
            self.file_suncloud = open(address + '(Солнце и облака) Ход выполнения задачи.txt', 'w')
            self.value_vel_axis = [[], []]
            self.value_vel_axis_sun = [[], []]
            self.value_vel_axis_cloud = [[], []]
            self.value_vel_axis_suncloud = [[], []]
            self.solving = []
            self.solving_sun = []
            self.solving_cloud = []
            self.solving_suncloud = []
            self.address = address
            #self.f = open('D://results//2//track.txt', 'w')
            self.firstDate = pack.datetime(2000, 1, 1, 0, 0, 0)
            self.lastDate = pack.datetime(2000, 1, 1, 0, 0, 0)


        # Метод predictTreck принимает объекты startTime и endTime класса datetime, которые содержат дату и время в формате utc и число step. Метод predictTreck прогнозирует трек спутника в интервал времени между startTime и endTime, при этом трэк записывается в виде списка объектов класса Coordinate, вычисляемых для моментов времени в выбранный интервал времени сшагом step (секунды)
        def predictTrack(self, startTime, endTime, startDay, endDay, step, oneCicle, minZenitAngle, address, solvePercent, maxCloudLevel):
            f = open('D://track.txt', 'w')
            self.address = address
            self.file = open(address + 'Ход выполнения задачи.txt', 'w')
            self.file_sun = open(address + '(Солнце) Ход выполнения задачи.txt', 'w')
            self.file_cloud = open(address + '(Облака) Ход выполнения задачи.txt', 'w')
            self.file_suncloud = open(address + '(Солнце и облака) Ход выполнения задачи.txt', 'w')
            if oneCicle is None:
                oneCicle = pack.SECONDS_IN_DAY() / self.tle.mean_motion

            self.utc_time = startTime

            self.firstDate = pack.datetime(self.utc_time.year, 1, 1, 0, 0, 0)
            self.firstDate += pack.timedelta(days=startDay - 1)
            if (endDay >= startDay):
                self.lastDate = pack.datetime(self.utc_time.year, 1, 1, 0, 0, 0)
                self.lastDate += pack.timedelta(days=endDay - 1)
            else:
                self.lastDate = pack.datetime(self.utc_time.year + 1, 1, 1, 0, 0, 0)
                self.lastDate += pack.timedelta(days=endDay - 1)
            if self.utc_time < self.firstDate:
                self.utc_time = self.firstDate
            else:
                if self.utc_time > self.lastDate:
                    self.utc_time = self.firstDate
                    self.utc_time += pack.timedelta(days=365)
                                                                               # time - объект класса datetime, опеределяет момент времени, для которого прогнозируются координаты спутника. Сначала time присваивается startTime
            itIsNearStep = False
            while self.utc_time <= endTime:                                                                             # Начало цикла while. Цикл работает, пока time меньше endTime, то есть пока time не выйдет за пределы исследуемого интервала времени startTime, endTime
                if (self.utc_time >= self.firstDate) and (self.utc_time <= self.lastDate):
                    itIsNearStep = self.iteration(itIsNearStep, step)
                    if (len(self.satTracks) > 0) and not itIsNearStep:
                        for i in range(0, len(self.satTracks)):
                            #startTime = self.satTracks[i][0].utc_time - pack.timedelta(seconds=step)
                            lastTime = self.satTracks[i][-1].utc_time + pack.timedelta(seconds=step)

                            #decCoord, velVect = self.orbit.get_dec_and_vel(startTime)
                            #self.satTracks[i].insert(0, self.SatelliteCoordinates(decCoord, velVect, startTime, self.earth))

                            decCoord, velVect = self.orbit.get_dec_and_vel(lastTime)
                            self.satTracks[i].append(self.SatelliteCoordinates(decCoord, velVect, lastTime, self.earth))
                            for p in self.satTracks[i]:
                                f.write(str(p.geoCoord.long) + '\t' + str(p.geoCoord.lat) + '\n')
                            f.close()
                        self.swathCoords(self.satTracks)
                        self.satTracks = []
                        areas = self.toMakeAreasOfVidion()
                        self.toGrip(areas, minZenitAngle, step, solvePercent, startTime, maxCloudLevel)
                    self.utc_time += pack.timedelta(seconds=step)
                else:
                    self.firstDate = pack.datetime(self.firstDate.year + 1, self.firstDate.month, self.firstDate.day, 0, 0, 0)
                    self.lastDate = pack.datetime(self.lastDate.year + 1, self.lastDate.month, self.lastDate.day, 0, 0, 0)
                    self.utc_time = pack.datetime(self.firstDate.year, self.firstDate.month, self.firstDate.day, 0, 0, 0)
                    #if (endDay >= startDay):
                    #    self.firstDate = pack.datetime(self.firstDate.year + 1, self.firstDate.month, self.firstDate.day, 0, 0, 0)
                    #    self.lastDate = pack.datetime(self.lastDate.year + 1, self.lastDate.month, self.lastDate.day, 0, 0, 0)
                    #    self.utc_time = pack.datetime(self.firstDate.year, self.firstDate.month, self.firstDate.day, 0, 0, 0)
                    #else:
                    #    self.utc_time = pack.datetime(self.firstDate.year, self.firstDate.month, self.firstDate.day, 0, 0, 0)
                    #    self.lastDate = pack.datetime(self.utc_time.year, 1, 1, 0, 0, 0)
                    #    self.lastDate += pack.timedelta(days=endDay)


            #    self.treckTest()

        def iteration(self, itIsNearStep, step):
            self.coordPredict()
            #self.satTrack.append(self.coord)

            for pol in self.polygons.shapeList:
                if pack.distBetweenDecCoord(pol.center, self.coord.geoCoord) < 1.1 * (pol.radius
                    + self.coord.geoCoord.alt * math.tan(self.radSwathAng)):
                    if not itIsNearStep:
                        self.satTracks.append([])
                    self.satTracks[-1].append(self.coord)
                    #self.f.write(str(self.coord.geoCoord) + '\n')
                    return True
                else:
                    return False
                #if itIsNearStep:
                    #self.satTracks[-1].append(self.coord)  # Прогнозирование координат спутника в момент времени time с помощью метода coordAzimuthPredict и добавление полученного объекта Coordinate - координаты трэка к списку satTrack
                    #return True
                #else:
                    #self.satTracks.append([])
                    #self.satTracks[-1].append(self.coord)
                    #return True



        def coordPredict(self):
            decCoord, velVect = self.orbit.get_dec_and_vel(self.utc_time)
            self.coord = self.SatelliteCoordinates(decCoord, velVect, self.utc_time, self.earth)

        def swathCoords(self, tracks):
            self.swathCoordList = []
            f = open('D://swath.txt', 'w')
            for track in tracks:
                self.swathCoordList.append([])
                for satCoord in track:
                    satGroundMovDir = self.satGroundMovementDirect(satCoord)
                    if pack.MyGeometry.scalMult(satGroundMovDir, satCoord.velVect) < 0:
                        satGroundMovDir = -satGroundMovDir

                    leftSwathDir = pack.MyGeometry.toRotVect(satCoord.decCoord.decCoord.radVect, satGroundMovDir,
                                              self.radSwathAng)
                    rightSwathDir = pack.MyGeometry.toRotVect(satCoord.decCoord.decCoord.radVect, satGroundMovDir,
                                               -self.radSwathAng)

                    pointLeftSwathCoord = pack.MyGeometry.nearestEllipsoidIntersection(pack.MyGeometry.Straight
                                                    (satCoord.decCoord.decCoord, leftSwathDir), self.earth.ellipsoid)
                    pointRightSwathCoord = pack.MyGeometry.nearestEllipsoidIntersection(pack.MyGeometry.Straight
                                                    (satCoord.decCoord.decCoord, rightSwathDir), self.earth.ellipsoid)

                    leftPoints = pack.decardToGeoCoordinates(pack.DecartCoordinate(pointLeftSwathCoord),
                                                               satCoord.utc_time, 0)
                    rightPoints = pack.decardToGeoCoordinates(pack.DecartCoordinate(pointRightSwathCoord),
                                                               satCoord.utc_time, 0)

                    swathCoord = self.SwathCoordinate(leftPoints, rightPoints, satCoord.utc_time)
                    f.write(str(leftPoints.long) + '\t' + str(leftPoints.lat) + '\n')
                    f.write(str(rightPoints.long) + '\t' + str(rightPoints.lat) + '\n')

                    self.swathCoordList[-1].append(swathCoord)

                    #self.rightSwathCoordList.append(pack.decardToGeoCoordinates
                    #                                (pack.DecartCoordinate(pointLeftSwathCoord), satCoord.utc_time, 0))
                    #self.leftSwathCoordList.append(pack.decardToGeoCoordinates
                    #                               (pack.DecartCoordinate(pointRightSwathCoord), satCoord.utc_time, 0))

        def toGrip(self, areas, minZenitAngle, step, solvePercent, start_time, maxCloudLevel):
            gripedPercent = 0
            gripedPercentWithSun = 0
            gripedPercentWithCloud = 0
            gripedPercentWithSunCloud = 0
            origin = areas[0].start_time
            print(str(self.satName) + ' приближается к испытательному полигону. Время: ' + str(origin))
            self.file.write(str(self.satName) + ' приближается к испытательному полигону. Время: ' + str(origin) + '\n')
            self.file_sun.write(str(self.satName) + ' приближается к испытательному полигону. Время: ' + str(origin) + '\n')
            self.file_cloud.write(str(self.satName) + ' приближается к испытательному полигону. Время: ' + str(origin) + '\n')
            self.file_suncloud.write(str(self.satName) + ' приближается к испытательному полигону. Время: ' + str(origin) + '\n')

            cloudLevels = []
            cloudLevelsGrad = []
            for polygon in self.polygons.shapeList:
                daysFromYear = (areas[0].start_time - pack.datetime(areas[0].start_time.year, 1, 1, 0, 0, 0)).days
                i = 0
                while(daysFromYear < polygon.intervals[i]) or (daysFromYear > polygon.intervals[i + 1]):
                    i += 1

                prob = polygon.cloudDistr[i]
                roundCloud = random.random()
                i = 0
                sumProb = prob[0]
                while roundCloud > sumProb:
                    i += 1
                    sumProb += prob[i]
                cloudLevels.append(i)
                cloudLevelsGrad.append(1 / len(prob))


            for area in areas:
                gripedPercentInPass = 0
                gripedPercentInPassWithSun = 0
                gripedPercentInPassWithCloud = 0
                gripedPercentInPassWithSunCloud = 0

                polygons = self.polygons.shapeList
                for i in range(0, len(self.polygons.shapeList)):
                    for segment in polygons[i].segmentsList:
                        cloudLevel = cloudLevels[i]
                        cloudLevelGrad = cloudLevelsGrad[i]
                        sunZenithAngle = pack.sun_zenith_angle(area.middle_time, segment.geoCoord.long, segment.geoCoord.lat)
                        roundCloudUnderSeg = random.random()

                        if (area.areaPolygon.contains(segment.point)):
                            segment.addGripsCount()
                            gripedPercentInPass += segment.space / self.polygons.allSpace * 100
                            if sunZenithAngle <= minZenitAngle:
                                segment.addGripsCountWithSun()
                                gripedPercentInPassWithSun += segment.space / self.polygons.allSpace * 100
                            if cloudLevel <= maxCloudLevel:
                                cloudPercent = cloudLevel * cloudLevelGrad
                                if roundCloudUnderSeg >= cloudPercent * (2 - cloudPercent):
                                    segment.addGripsCountWithCloud()
                                    gripedPercentInPassWithCloud += segment.space / self.polygons.allSpace * 100
                            if (cloudLevel <= maxCloudLevel) and (sunZenithAngle <= minZenitAngle):
                                cloudPercent = cloudLevel * cloudLevelGrad
                                if (roundCloudUnderSeg >= cloudPercent * (2 - cloudPercent)):
                                    segment.addGripsCountWithSunCloud()
                                    gripedPercentInPassWithSunCloud += segment.space / self.polygons.allSpace * 100
                gripedPercent += gripedPercentInPass
                gripedPercentWithSun += gripedPercentInPassWithSun
                gripedPercentWithCloud += gripedPercentInPassWithCloud
                gripedPercentWithSunCloud += gripedPercentInPassWithSunCloud
                self.value_vel_axis[0].append(gripedPercentInPass)
                self.value_vel_axis[1].append(area.end_time)
                self.value_vel_axis_sun[0].append(gripedPercentInPassWithSun)
                self.value_vel_axis_sun[1].append(area.end_time)
                self.value_vel_axis_cloud[0].append(gripedPercentInPassWithCloud)
                self.value_vel_axis_cloud[1].append(area.end_time)
                self.value_vel_axis_suncloud[0].append(gripedPercentInPassWithSunCloud)
                self.value_vel_axis_suncloud[1].append(area.end_time)

                if gripedPercent > 0:
                    print(str(round(gripedPercent, 3)) + '%\tтерритории захвачено через время: ' + str(area.end_time - origin))
                    self.file.write(str(round(gripedPercent, 3)) + '%\tтерритории захвачено через время: ' + str(area.end_time - origin) + '\n')
                if gripedPercentWithSun > 0:
                    self.file_sun.write(str(round(gripedPercentWithSun, 3)) + '%\tтерритории захвачено через время: ' + str(area.end_time - origin) + '\n')
                if gripedPercentWithCloud > 0:
                    self.file_cloud.write(str(round(gripedPercentWithCloud, 3)) + '%\tтерритории захвачено через время: ' + str(area.end_time - origin) + '\n')
                if gripedPercentWithSunCloud > 0:
                    self.file_suncloud.write(str(round(gripedPercentWithSunCloud, 3)) + '%\tтерритории захвачено через время: ' + str(area.end_time - origin) + '\n')
            print(str(self.satName) + ' удаляется от испытательного полигона. Время: ' + str(areas[-1].end_time))
            self.file.write(str(self.satName) + ' удаляется от испытательного полигона. Время: ' + str(areas[-1].end_time) + '\n')
            self.file_sun.write(str(self.satName) + ' удаляется от испытательного полигона. Время: ' + str(areas[-1].end_time) + '\n')
            self.file_cloud.write(str(self.satName) + ' удаляется от испытательного полигона. Время: ' + str(areas[-1].end_time) + '\n')
            self.file_suncloud.write(str(self.satName) + ' удаляется от испытательного полигона. Время: ' + str(areas[-1].end_time) + '\n')
            print(str(round(gripedPercent, 3)) + '% территории было захвачено за время приближение к полигону\n')
            self.file.write(str(round(gripedPercent, 3)) + '% территории было захвачено за время приближение к полигону\n' + '\n')
            self.file_sun.write(str(round(gripedPercentWithSun, 3)) + '% территории было захвачено за время приближение к полигону\n' + '\n')
            self.file_cloud.write(str(round(gripedPercentWithCloud, 3)) + '% территории было захвачено за время приближение к полигону\n' + '\n')
            self.file_suncloud.write(str(round(gripedPercentWithSunCloud, 3)) + '% территории было захвачено за время приближение к полигону\n' + '\n')
            print('На момент времени ' + str(areas[-1].end_time) + ' захвачено:')
            self.file.write('На момент времени ' + str(areas[-1].end_time) + ' захвачено:' + '\n')
            self.toPrintPercents(solvePercent, areas[-1].end_time)
            self.file_sun.write('На момент времени ' + str(areas[-1].end_time) + ' захвачено:' + '\n')
            self.toPrintPercentsWithSun(solvePercent, areas[-1].end_time)
            self.file_cloud.write('На момент времени ' + str(areas[-1].end_time) + ' захвачено:' + '\n')
            self.toPrintPercentsWithCloud(solvePercent, areas[-1].end_time)
            self.file_suncloud.write('На момент времени ' + str(areas[-1].end_time) + ' захвачено:' + '\n')
            self.toPrintPercentsWithSunCloud(solvePercent, areas[-1].end_time)
            print()
            self.file.write('\n')
            self.file_sun.write('\n')
            self.file_cloud.write('\n')
            self.file_suncloud.write('\n')

        def toPrintPercents(self, solvePercent, time):
            solvePercents = self.polygons.toCalcPercents()
            if len(self.solving) < len(solvePercents):
                if solvePercents[len(self.solving)] >= solvePercent:
                    self.solving.append(time)
            i = 1
            for solve in solvePercents:
                print(str(i) + ' раз захвачено ' + str(round(solve, 3)) + '% территории')
                self.file.write(str(i) + ' раз захвачено ' + str(round(solve, 3)) + '% территории' + '\n')
                i += 1

        def toPrintPercentsWithSun(self, solvePercent, time):
            solvePercents = self.polygons.toCalcPercentsWithSun()
            if len(self.solving_sun) < len(solvePercents):
                if solvePercents[len(self.solving_sun)] >= solvePercent:
                    self.solving_sun.append(time)
            i = 1
            for solve in solvePercents:
                self.file_sun.write(str(i) + ' раз захвачено ' + str(round(solve, 3)) + '% территории' + '\n')
                i += 1

        def toPrintPercentsWithCloud(self, solvePercent, time):
            solvePercents = self.polygons.toCalcPercentsWithCloud()
            if len(self.solving_cloud) < len(solvePercents):
                if solvePercents[len(self.solving_cloud)] >= solvePercent:
                    self.solving_cloud.append(time)
            i = 1
            for solve in solvePercents:
                self.file_cloud.write(str(i) + ' раз захвачено ' + str(round(solve, 3)) + '% территории' + '\n')
                i += 1

        def toPrintPercentsWithSunCloud(self, solvePercent, time):
            solvePercents = self.polygons.toCalcPercentsWithSunCloud()
            if len(self.solving_suncloud) < len(solvePercents):
                if solvePercents[len(self.solving_suncloud)] >= solvePercent:
                    self.solving_suncloud.append(time)
            i = 1
            for solve in solvePercents:
                self.file_suncloud.write(str(i) + ' раз захвачено ' + str(round(solve, 3)) + '% территории' + '\n')
                i += 1

        def toMakeAreasOfVidion(self):
            #f = open('D://swath.txt', 'w')
            areas = []
            for swath in self.swathCoordList:
                swathLen = len(swath)
                if len(swath) > 1:
                    for i in range(swathLen - 1):
                        points = []
                        points.append((swath[i].leftGeoCoord.long, swath[i].leftGeoCoord.lat))
                        points.append((swath[i + 1].leftGeoCoord.long, swath[i + 1].leftGeoCoord.lat))
                        points.append((swath[i + 1].rightGeoCoord.long, swath[i + 1].rightGeoCoord.lat))
                        points.append((swath[i].rightGeoCoord.long, swath[i].rightGeoCoord.lat))
                        areas.append(self.Area(pack.Polygon(points), swath[i].utc_time, swath[i + 1].utc_time))
                #points = []
                #for leftCoord in swath[0]:
                #    points.append((leftCoord.long, leftCoord.lat))
                    #f.write(str(leftCoord) + '\n')
                #for rightCoord in reversed(swath[1]):
                #    points.append((rightCoord.long, rightCoord.lat))
                    #f.write(str(rightCoord) + '\n')
                #areas.append(pack.Polygon(points))
            return areas

        def satGroundMovementDirect(self, coord):
            satMovStraight = pack.MyGeometry.Straight(coord.decCoord.decCoord, coord.velVect)
            groundPlane = pack.MyGeometry.planeTouchedCanonEllipsoid(coord.groundCoord, self.earth.ellipsoid)
            straightProj = pack.MyGeometry.projStraightOnPlane(satMovStraight, groundPlane)
            #velProj = self.toAddVel(straightProj.vector, coord.geoCoord.lat, groundPlane)
            return pack.MyGeometry.normVect(straightProj.vector)

        def toAddVel(self, vect, lat, plane):
            earthVel = self.earth.ellipsoid.a * self.earth.ellipsoid.c / math.sqrt(self.earth.ellipsoid.c
                        * self.earth.ellipsoid.c + self.earth.ellipsoid.a * self.earth.ellipsoid.a
                        * (math.tan(lat) ** 2)) * pack.EARTH_FREQUENCY()
            transMat = [[plane.normal.z, plane.normal.y, -plane.normal.x],
                        [plane.normal.x, -plane.normal.z, plane.normal.y],
                        [plane.normal.x, plane.normal.y, plane.normal.z]]
            newVect = pack.MyGeometry.toMultMatrixOnjVect3D(transMat, vect)
            #newVect.y -= earthVel
            return pack.MyGeometry.toMultMatrixOnjVect3D(pack.np.linalg.inv(transMat), newVect)

        #def treckTest(self):
            #f = open('D://treck.txt', 'w')
            #for track in self.satTracks:
            #    for point in track:
            #        f.write(str(point) + '\n')
            #fl = open('D://left.txt', 'w')
            #fr = open('D://right.txt', 'w')
            #for point1 in self.satTrack:
                #f.write(str(point1) + '\n')
            #for point1 in self.leftSwathCoordList:
            #    fl.write(str(point1) + '\n')
            #for point1 in self.rightSwathCoordList:
            #    fr.write(str(point1) + '\n')
            #for point1 in self.leftSwathCoordList:
            #    fl.write(str(point1) + '\n')

            #f = open('D://fullTrack.txt', 'w')
            #for point1 in self.satTrack:
            #    f.write(str(point1) + '\n')

            #for swath in self.swathCoordList:
            #    for point in swath:
            #        fl.write(str(point.leftGeoCoord) + '\n')
            #        fr.write(str(point.rightGeoCoord) + '\n')

        #def graphs(self):
        #    for i in range(1, len(self.value_vel_axis)):
        #        self.value_axis[i] = self.value_vel_axis[i] + self.value_axis[i - 1]
        #        self.value_axis_sun[i] = self.value_vel_axis_sun[i] + self.value_axis_sun[i - 1]
        #    fig = plt.figure()
        #    value_graph = fig.add_subplot(111)
        #    value_graph.plot(self.sec_axis, self.value_axis)
        #    #value_graph.title('value_graph')
        #    fig.savefig('D://value_graph')

        #    fig = plt.figure()
        #    value_vel_graph = fig.add_subplot(111)
        #    value_vel_graph.plot(self.sec_axis, self.value_vel_axis)
        #    #value_graph.title('value_vel_graph')
        #    fig.savefig('D://value_vel_graph')

        #    fig = plt.figure()
        #    value_sun_graph = fig.add_subplot(111)
        #    value_sun_graph.plot(self.sec_axis, self.value_axis_sun)
        #    #value_graph.title('value_sun_graph')
        #    fig.savefig('D://value_sun_graph')

        #    fig = plt.figure()
        #    value_vel_sun_graph = fig.add_subplot(111)
        #    value_vel_sun_graph.plot(self.sec_axis, self.value_vel_axis_sun)
            #value_graph.title('value_vel_sun_graph')
        #    fig.savefig('D://value_vel_sun_graph')

        #    fig = plt.figure()
        #    value_vel_graph = fig.add_subplot(111)
        #    yf = scipy.fftpack.fft(self.value_vel_axis)
        #    value_vel_graph.plot(self.sec_axis, abs(yf))
        #    # value_graph.title('value_vel_graph')
        #    fig.savefig('D://value_vel_graph_fur')

        #    fig = plt.figure()
        #    value_vel_graph = fig.add_subplot(111)
        #    yf = scipy.fftpack.fft(self.value_vel_axis_sun)
        #    value_vel_graph.plot(self.sec_axis, abs(yf))
        #    # value_graph.title('value_vel_graph')
        #    fig.savefig('D://value_vel_sun_graph_fur')

        def graphs(self, startTime, endTime, firstDay, lastDay, step):
            if len(self.value_vel_axis) > 0:
                val_vel = self.value_vel_axis[0]
                time = self.value_vel_axis[1]
                sum_delta_time = 0
                length = len(val_vel)
                i = 0
                while i < length:
                    if val_vel[i] == 0:
                        del val_vel[i]
                        del time[i]
                        length -= 1
                    else:
                        i += 1
                if len(val_vel) > 1:
                    start_time = []
                    prev_start_time = time[0]
                    for j in range(1, len(val_vel)):
                        if (time[j] - time[j - 1]).total_seconds() > step:
                            start_time.append(prev_start_time)
                            prev_start_time = time[j]
                    start_time.append(prev_start_time)
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(start_time, firstDay, lastDay)
                    print('Средний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file.write('Средний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600) + '\n')

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + 'Гистограмма плотности распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + 'Гистограмма плотности распределения пролетов')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + 'Гистограмма функции распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + 'Гистограмма функции распределения пролетов')
                    file.close()
                    plt.close()


                if len(self.solving) > 2:
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(self.solving, firstDay, lastDay)
                    print('\nРешение задачи:\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file.write('\nРешение задачи:\nСредний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600) + '\n\n')
                    self.file.close()

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + 'Гистограмма плотности распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + 'Гистограмма плотности распределения решений')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + 'Гистограмма функции распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + 'Гистограмма функции распределения решений')
                    file.close()
                    plt.close()

                    full_val_vel, full_time = self.toFullGraph(val_vel, time, startTime, endTime, step)

                    file = open(self.address + 'График притока информации.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val_vel)
                    #value_graph.title('value_graph')
                    fig.savefig(self.address + 'График притока информации')
                    plt.close()

                    file = open(self.address + 'Данные о притоке информации.txt', 'w')
                    for i in range(0, len(val_vel)):
                        file.write(time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((time[i] - startTime).total_seconds()) + '\t' + str(val_vel[i]) + '\n')
                    file.close()

                    #yf = abs(scipy.fftpack.fft(full_val_vel))

                    #fig = plt.figure()
                    #value_graph = fig.add_subplot(111)
                    #value_graph.plot(full_time, yf)
                    # value_graph.title('value_graph')
                    #fig.savefig('D://furye_graph')

                    #file = open('D://furye_file.txt', 'w')
                    #for i in range(0, len(val_vel)):
                    #    file.write(time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str(
                    #        (time[i] - startTime).total_seconds()) + '\t' + str(val_vel[i]) + '\n')
                    #file.close()

                    full_val = []
                    full_val.append(full_val_vel[0])
                    for i in range(1, len(full_val_vel)):
                        full_val.append(full_val_vel[i] + full_val[i - 1])

                    file = open(self.address + 'График данных от времени.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val)
                    # value_graph.title('value_graph')
                    fig.savefig(self.address + 'График данных от времени')
                    plt.close()
                else:
                    self.file.close()



            if len(self.value_vel_axis_sun) > 0:
                val_vel = self.value_vel_axis_sun[0]
                time = self.value_vel_axis_sun[1]
                sum_delta_time = 0
                length = len(val_vel)
                i = 0
                while i < length:
                    if val_vel[i] == 0:
                        del val_vel[i]
                        del time[i]
                        length -= 1
                    else:
                        i += 1
                if len(val_vel) > 1:
                    start_time = []
                    prev_start_time = time[0]
                    for j in range(1, len(val_vel)):
                        if (time[j] - time[j - 1]).total_seconds() > step:
                            start_time.append(prev_start_time)
                            prev_start_time = time[j]
                    start_time.append(prev_start_time)
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(start_time, firstDay, lastDay)
                    print('\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file_sun.write('Средний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600) + '\n')

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Солнце) Гистограмма плотности распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце) Гистограмма плотности распределения пролетов')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Солнце) Гистограмма функции распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце) Гистограмма функции распределения пролетов')
                    file.close()
                    plt.close()

                if len(self.solving_sun) > 2:
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(self.solving_sun, firstDay, lastDay)
                    print('\nРешение задачи:\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file_sun.write('\nРешение задачи:\nСредний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600))
                    self.file_sun.close()

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Солнце) Гистограмма плотности распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце) Гистограмма плотности распределения решений')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Солнце) Гистограмма функции распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце) Гистограмма функции распределения решений')
                    file.close()
                    plt.close()

                    full_val_vel, full_time = self.toFullGraph(val_vel, time, startTime, endTime, step)

                    file = open(self.address + '(Солнце) Данные о притоке информации.txt', 'w')
                    for i in range(0, len(val_vel)):
                        file.write(time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((time[i] - startTime).total_seconds()) + '\t' + str(val_vel[i]) + '\n')
                    file.close()

                    file = open(self.address + '(Солнце) График притока информации.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    yf = abs(scipy.fftpack.fft(full_val_vel))

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val_vel)
                    #value_graph.title('value_graph')
                    fig.savefig(self.address + '(Солнце) График притока информации')
                    plt.close()

                    full_val = []
                    full_val.append(full_val_vel[0])
                    for i in range(1, len(full_val_vel)):
                        full_val.append(full_val_vel[i] + full_val[i - 1])

                    file = open(self.address + '(Солнце) График данных от времени.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val)
                    # value_graph.title('value_graph')
                    fig.savefig(self.address + '(Солнце) График данных от времени')
                    plt.close()
                else:
                    self.file_sun.close()

            if len(self.value_vel_axis_cloud) > 0:
                val_vel = self.value_vel_axis_cloud[0]
                time = self.value_vel_axis_cloud[1]
                sum_delta_time = 0
                length = len(val_vel)
                i = 0
                while i < length:
                    if val_vel[i] == 0:
                        del val_vel[i]
                        del time[i]
                        length -= 1
                    else:
                        i += 1
                if len(val_vel) > 1:
                    start_time = []
                    prev_start_time = time[0]
                    for j in range(1, len(val_vel)):
                        if (time[j] - time[j - 1]).total_seconds() > step:
                            start_time.append(prev_start_time)
                            prev_start_time = time[j]
                    start_time.append(prev_start_time)
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(start_time, firstDay, lastDay)
                    self.file_cloud.write('Средний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600) + '\n')

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Облака) Гистограмма плотности распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Облака) Гистограмма плотности распределения пролетов')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Облака) Гистограмма функции распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Облака) Гистограмма функции распределения пролетов')
                    file.close()
                    plt.close()

                if len(self.solving_cloud) > 2:
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(self.solving_cloud, firstDay, lastDay)
                    print('\nРешение задачи:\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file_cloud.write('\nРешение задачи:\nСредний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600))
                    self.file_cloud.close()

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Облака) Гистограмма плотности распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Облака) Гистограмма плотности распределения решений')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Облака) Гистограмма функции распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Облака) Гистограмма функции распределения решений')
                    file.close()
                    plt.close()

                    full_val_vel, full_time = self.toFullGraph(val_vel, time, startTime, endTime, step)

                    file = open(self.address + '(Облака) Данные о притоке информации.txt', 'w')
                    for i in range(0, len(val_vel)):
                        file.write(time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((time[i] - startTime).total_seconds()) + '\t' + str(val_vel[i]) + '\n')
                    file.close()

                    file = open(self.address + '(Облака) График притока информации.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    yf = abs(scipy.fftpack.fft(full_val_vel))

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val_vel)
                    #value_graph.title('value_graph')
                    fig.savefig(self.address + '(Облака) График притока информации')
                    plt.close()

                    full_val = []
                    full_val.append(full_val_vel[0])
                    for i in range(1, len(full_val_vel)):
                        full_val.append(full_val_vel[i] + full_val[i - 1])

                    file = open(self.address + '(Облака) График данных от времени.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val)
                    # value_graph.title('value_graph')
                    fig.savefig(self.address + '(Облака) График данных от времени')
                    plt.close()

                else:
                    self.file_cloud.close()

            if len(self.value_vel_axis_suncloud) > 0:
                val_vel = self.value_vel_axis_suncloud[0]
                time = self.value_vel_axis_suncloud[1]
                sum_delta_time = 0
                length = len(val_vel)
                i = 0
                while i < length:
                    if val_vel[i] == 0:
                        del val_vel[i]
                        del time[i]
                        length -= 1
                    else:
                        i += 1
                if len(val_vel) > 1:
                    start_time = []
                    prev_start_time = time[0]
                    for j in range(1, len(val_vel)):
                        if (time[j] - time[j - 1]).total_seconds() > step:
                            start_time.append(prev_start_time)
                            prev_start_time = time[j]
                    start_time.append(prev_start_time)
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(start_time, firstDay, lastDay)
                    print('\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file_suncloud.write('Средний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600) + '\n')

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Солнце и облака) Гистограмма плотности распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце и облака) Гистограмма плотности распределения пролетов')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Солнце и облака) Гистограмма функции распределения пролетов.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце и облака) Гистограмма функции распределения пролетов')
                    file.close()
                    plt.close()

                if len(self.solving_suncloud) > 2:
                    max, min, median, avarage, disp, stand_dev, difs = self.max_min_avarage_time(self.solving_suncloud, firstDay, lastDay)
                    print('\nРешение задачи:\nСредний период:\t\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t\t' + str(min / 24 / 3600))
                    self.file_suncloud.write('\nРешение задачи:\nСредний период:\t\t' + str(avarage / 24 / 3600) + '\nДисперсия:\t\t' + str(disp / 24 / 3600)
                          + '\nСред-квад. откл.:\t' + str(stand_dev / 24 / 3600) + '\nМедианный период:\t' + str(median / 24 / 3600)
                          + '\nМаксимальный период:\t' + str(max / 24 / 3600) + '\nМинимальный период:\t' + str(min / 24 / 3600))
                    self.file_suncloud.close()

                    histogramm = plt.gca()
                    st = 24 * 3600
                    hist, value = self.hist_distribution_density(difs, st)
                    y = []
                    file = open(self.address + '(Солнце и облака) Гистограмма плотности распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце и облака) Гистограмма плотности распределения решений')
                    file.close()
                    plt.close()

                    histogramm = plt.gca()
                    for i in range(1, len(hist)):
                        hist[i] += hist[i - 1]
                    file = open(self.address + '(Солнце и облака) Гистограмма функции распределения решений.txt', 'w')
                    file.write('1 шаг - ' + str(st) + ' секунд или ' + str(st / 86400) + ' дней\n')
                    y = []
                    for i in range(0, len(hist)):
                        y.append(i)
                        file.write(str(i) + '\t' + str(hist[i]) + '\n')
                    histogramm.bar(y, hist, align='edge')
                    plt.savefig(self.address + '(Солнце и облака) Гистограмма функции распределения решений')
                    file.close()
                    plt.close()

                    full_val_vel, full_time = self.toFullGraph(val_vel, time, startTime, endTime, step)

                    file = open(self.address + '(Солнце и облака) Данные о притоке информации.txt', 'w')
                    for i in range(0, len(val_vel)):
                        file.write(time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((time[i] - startTime).total_seconds()) + '\t' + str(val_vel[i]) + '\n')
                    file.close()

                    file = open(self.address + '(Солнце и облака) График притока информации.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    yf = abs(scipy.fftpack.fft(full_val_vel))

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val_vel)
                    #value_graph.title('value_graph')
                    fig.savefig(self.address + '(Солнце и облака) График притока информации')
                    plt.close()

                    full_val = []
                    full_val.append(full_val_vel[0])
                    for i in range(1, len(full_val_vel)):
                        full_val.append(full_val_vel[i] + full_val[i - 1])

                    file = open(self.address + '(Солнце и облака) График данных от времени.txt', 'w')
                    for i in range(0, len(full_val_vel)):
                        file.write(full_time[i].strftime("%Y-%m-%d %H:%M:%S") + '\t' + str((full_time[i] - startTime).total_seconds()) + '\t' + str(full_val_vel[i]) + '\n')
                    file.close()

                    fig = plt.figure()
                    value_graph = fig.add_subplot(111)
                    value_graph.plot(full_time, full_val)
                    # value_graph.title('value_graph')
                    fig.savefig(self.address + '(Солнце и облака) График данных от времени')
                    plt.close()

                else:
                    self.file_suncloud.close()

        def hist_distribution_density(self, dist, step):
            max_value = (max(dist) // step) * step + step
            hist_len = int((max_value) // step)
            hist = [0] * hist_len
            #value = pack.np.arange(step / 2, max_value + step / 2, step)
            value = []
            for i in range(0, hist_len):
                value.append(step / 2 + i * step)
            for dist_el in dist:
                index = int(dist_el // step)
                hist[index] += 1
            return hist, value

        def toFullGraph(self, val_vel, time, startTime, endTime, step):
            if startTime < time[0]:
                val_vel.insert(0, 0)
                time.insert(0, startTime)

            if endTime > time[-1]:
                val_vel.append(0)
                time.append(endTime)

            full_val_vel = []
            full_time = []

            previousTime = time[0]
            currentTime = previousTime + pack.timedelta(seconds=step)

            i = 0

            while currentTime <= time[-1]:
                stepSum = 0
                while (time[i] >= previousTime) and (time[i] < currentTime):
                    stepSum += val_vel[i]
                    i += 1
                full_val_vel.append(stepSum)
                full_time.append(previousTime)
                previousTime = currentTime
                currentTime += pack.timedelta(seconds=step)

            return full_val_vel, full_time

        def max_min_avarage_time(self, list, firstDay, lastDay):
            if len(list) > 2:
                firstSecond = (firstDay - 1) * 24 * 60 * 60
                lastSecond = lastDay * 24 * 60 * 60
                if (lastDay >= firstDay):
                    change_sec = (365 - lastDay + firstDay) * 24 * 60 * 60
                else:
                    change_sec = (firstDay - lastDay) * 24 * 60 * 60
                difs = []
                avarage = 0
                max = 0
                min = math.inf
                prev_time = list[0]
                #(prev_time - pack.datetime(prev_time.year, 1, 1, 0, 0, 0)).days * 24 * 60 * 60
                for time in list[1 :]:
                    zero_year = pack.datetime(prev_time.year, 1, 1, 0, 0, 0)
                    prev_sec = (prev_time - zero_year).total_seconds()
                    time_sec = (time - zero_year).total_seconds()
                    i = 0
                    if (lastDay >= firstDay):
                        while time_sec > lastSecond:
                            i += 1
                            time_sec -= 365 * 24 * 60 * 60
                    else:
                        while time_sec > firstSecond:
                            i += 1
                            time_sec -= 365 * 24 * 60 * 60
                    dif = (time - prev_time).total_seconds() - i * change_sec
                    avarage += dif
                    if dif > max:
                        max = dif
                    if dif < min:
                        min = dif
                    difs.append(dif)
                    prev_time = time
                leng = (len(list) - 1)
                avarage /= leng
                difs.sort()
                median = difs[round(leng / 2) - 1]

                disp = 0
                for dif in difs:
                    disp += (avarage - dif) ** 2
                disp /= (leng - 1)
                disp **= 0.5

                stand_dev = disp  ** 0.5

                return max, min, median, avarage, disp, stand_dev, difs
            else:
                return 0, 0, 0, 0, 0, 0, 0

        #def graphsToFile(self, address):
        #    file = open(address, 'w')
        #    for i in range(0, len())
        #        file.write()

        class SwathCoordinate:
            def __init__(self, leftGeoCoord, rightGeoCoord, utc_time):
                self.leftGeoCoord = leftGeoCoord
                self.rightGeoCoord = rightGeoCoord
                self.utc_time = utc_time

        class Area:
            def __init__(self, areaPolygon, start_time, end_time):
                self.areaPolygon = areaPolygon
                self.start_time = start_time
                self.end_time = end_time
                self.middle_time = start_time + (end_time - start_time) / 2

        class SatelliteCoordinates:
            def __init__(self, decCoord, velVect, utc_time, earth):
                self.decCoord = decCoord
                self.velVect = pack.MyGeometry.Vector(velVect.x + decCoord.decCoord.radVect.y * pack.EARTH_FREQUENCY(),
                                                      velVect.y - decCoord.decCoord.radVect.x * pack.EARTH_FREQUENCY(),
                                                      velVect.z)
                self.utc_time = utc_time
                self.groundCoord = pack.MyGeometry.nearestEllipsoidIntersection(pack.MyGeometry.Straight(
                    self.decCoord.decCoord, -self.decCoord.decCoord.radVect), earth.ellipsoid)
                alt = pack.MyGeometry.Vector(self.decCoord.decCoord.radVect.x - self.groundCoord.radVect.x,
                                             self.decCoord.decCoord.radVect.y - self.groundCoord.radVect.y,
                                             self.decCoord.decCoord.radVect.z - self.groundCoord.radVect.z).lenght()
                self.geoCoord = pack.decardToGeoCoordinates(decCoord, self.utc_time, alt)

            def __str__(self):
                return (str(self.geoCoord) + '\t' + str(self.velVect.lenght()) + '\t' + str(self.utc_time))