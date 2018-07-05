import Packeges as pack

if __name__ == '__main__':
    earth = pack.Earth(pack.ELLIPSOID_AXISES_WGS_84().a, pack.ELLIPSOID_AXISES_WGS_84().b,
                       pack.ELLIPSOID_AXISES_WGS_84().c)

    utc_time1 = pack.datetime(2019, 6, 5, 0, 0, 0)
    utc_time2 = pack.datetime(2020, 6, 5, 0, 0, 0)
    startDay = 121
    endDay = 274

    polygons = pack.ShapePolygonPack()
    #polygons.toReadShapeFile("D:/Shapefiles/Utrish")
    polygons.toReadShapeFile("D:/Карты/Валуйки/Важные объединенные участки леса валуйского лесничества (shape).shp")
    polygons.toSplitPoligons(0.005, 0.005, earth)
    for i in polygons.shapeList:
        #i.toPutCloudDistr([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], [0, 366])


        i.toPutCloudDistr([[0.03977273, 0.05397727, 0.07954545, 0.10795455, 0.11647727, 0.12215909, 0.13068182, 0.10795455, 0.10511364, 0.07954545, 0.05681818],
                           [0.01880878, 0.10658307, 0.10031348, 0.12225705, 0.13479624, 0.14106583, 0.12539185, 0.06583072, 0.10031348, 0.06583072, 0.01880878],
                           [0.03977273, 0.06818182, 0.13920455, 0.13636364, 0.14488636, 0.09943182, 0.14488636, 0.08806818, 0.06818182, 0.04261364, 0.02840909],
                           [0.01466276, 0.05571848, 0.10557185, 0.12609971, 0.15542522, 0.15835777, 0.18181818, 0.1026393,  0.07038123, 0.02932551, 0],
                           [0.00852273, 0.05965909, 0.13920455, 0.09943182, 0.15056818, 0.16761364, 0.17897727, 0.13068182, 0.05681818, 0.00852273, 0],
                           [0,          0.06534091, 0.15625,    0.13068182, 0.16477273, 0.15625,    0.11647727, 0.11079545, 0.09090909, 0.00852273, 0],
                           [0.0058651,  0.1026393,  0.13782991, 0.14369501, 0.13489736, 0.14076246, 0.14956012, 0.1026393,  0.07624633, 0.0058651,  0],
                           [0.00568182, 0.16477273, 0.17613636, 0.15340909, 0.17045455, 0.11079545, 0.10511364, 0.05681818, 0.04261364, 0.01420455, 0],
                           [0.01173021, 0.09677419, 0.17888563, 0.14662757, 0.13782991, 0.10557185, 0.1143695,  0.08797654, 0.05571848, 0.03225806, 0.03225806],
                           [0.00568182, 0.09090909, 0.17613636, 0.12215909, 0.15625,    0.09090909, 0.13352273, 0.09090909, 0.06534091, 0.05965909, 0.00852273],
                           [0.00879765, 0.11730205, 0.15249267, 0.12316716, 0.08211144, 0.09090909, 0.16129032, 0.1202346,  0.07038123, 0.06744868, 0.0058651],
                           [0.00577346, 0.07826246, 0.10428886, 0.13104839, 0.1308651,  0.1308651,  0.10483871, 0.11574413, 0.0789956, 0.09897361,  0.02034457]],
                            [0, 31, 59, 90, 120, 151, 182, 212, 243, 273, 304, 334, 365])
        #i.toPutCloudDistr([0.006535947712418301, 0.17647058823529413, 0.22875816993464052, 0.20261437908496732, 0.1437908496732026, 0.11764705882352941, 0.032679738562091505, 0.058823529411764705, 0.026143790849673203, 0.006535947712418301, 0.0])


    startTime = pack.datetime.now()
    group = pack.SatelliteGroup(earth, polygons, 'D://results.txt')
    group.toCreatSatellite('ISS (ZARYA)', 'D://TLE//tle.txt', 3.5, 'D://results//2//')
    print(pack.datetime.now() - startTime)

    group.satList[0].predictTrack(utc_time1, utc_time2, 0, 366, 1, None, 75, 'D://results//2019-2020 полный год (для тестирования старой модели)//', 90, 3)
    group.satList[0].graphs(utc_time1, utc_time2, 0, 366, 24 * 3600)


    startTime = pack.datetime.now()
    group = pack.SatelliteGroup(earth, polygons, 'D://results.txt')
    group.toCreatSatellite('ISS (ZARYA)', 'D://TLE//tle.txt', 3.5, 'D://results//2//')
    print(pack.datetime.now() - startTime)

    group.satList[0].predictTrack(utc_time1, utc_time2, startDay, endDay, 1, None, 75, 'D://results//2019-2020 неполный год (для тестирования старой модели)//', 90, 3)
    group.satList[0].graphs(utc_time1, utc_time2, startDay, endDay, 24 * 3600)


    #utc_time1 = pack.datetime(2009, 6, 5, 0, 0, 0)
    #utc_time2 = pack.datetime(2039, 6, 5, 0, 0, 0)

    #startTime = pack.datetime.now()
    #group = pack.SatelliteGroup(earth, polygons, 'D://results.txt')
    #group.toCreatSatellite('ISS (ZARYA)', 'D://TLE//tle.txt', 3.5, 'D://results//2//')
    #print(pack.datetime.now() - startTime)

    #group.satList[0].predictTrack(utc_time1, utc_time2, startDay, endDay, 1, None, 75, 'D://results//2009-2019 неполный год//', 90, 3)
    #group.satList[0].graphs(utc_time1, utc_time2, startDay, endDay, 24 * 3600)


    '''
    group = pack.SatelliteGroup(earth, polygons, 'D://results.txt')

    file = open('D://TLE//sat25544.txt', 'r')

    directory = 'D://TLE//newSats//'

    lines = file.readlines()

    line1 = lines[0]
    line2 = lines[1]
    tleAddress = directory + str(int(0)) + '.txt'
    newFile = open(tleAddress, 'w')
    newFile.write('ISS (ZARYA)' + '\n' + line1 + line2)
    newFile.close()

    tle = pack.tlefile.read('ISS (ZARYA)', tleAddress)
    group.toCreatSatellite('ISS (ZARYA)', tleAddress, 3.5, 'D://results//test//')

    timeStart = pack.datetime(2017, 1, 1, 0, 0, 0)

    
    i = 2
    while i <= len(lines) - 1:
        line1 = lines[i]
        line2 = lines[i + 1]
        tleAddress = directory + str(int(i / 2)) + '.txt'
        newFile = open(tleAddress, 'w')
        newFile.write('ISS (ZARYA)' + '\n' + line1 + line2)
        newFile.close()
        i += 2

        tle = pack.tlefile.read('ISS (ZARYA)', tleAddress)
        timeEnd64 = str(tle.epoch.real)
        yyyy = int(timeEnd64[0:4])
        MM = int(timeEnd64[5:7])
        dd = int(timeEnd64[8:10])
        hh = int(timeEnd64[11:13])
        mm = int(timeEnd64[14:16])
        ss = int(timeEnd64[17:19])
        timeEnd = pack.datetime(yyyy, MM, dd, hh, mm, ss)
        group.satList[0].predictTrack(timeStart, timeEnd, 121, 274, 1, None, 75, 'D://results//test//', 90, 3)
        group.satList[0].tle = pack.tlefile.read('ISS (ZARYA)', tleAddress)
        timeStart = timeEnd
    file.close()
    timeEnd = pack.datetime(2017, 12, 31, 23, 59, 59)
    group.satList[0].predictTrack(timeStart, timeEnd, 121, 274, 1, None, 75, 'D://results//test//', 90, 3)
    timeStart = pack.datetime(2017, 1, 1, 0, 0, 0)
    group.satList[0].graphs(timeStart, timeEnd, 121, 274, 24 * 3600)
    '''

