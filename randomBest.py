# This script creates a test suite, which contains roads, which have maximized oob'S

from profileValues import *

# settings for the evolutionary algorithm
initSize = 10
# time for the evolution (in min)
computationTime = 360
intervall = 30
t_int = time() + 60 * intervall
newRoadListCount = 0
maxOOBCount = 0
outputCount = 0

def main():
    t_end = time() + 60 * computationTime
    global maxOOBCount
    resultList = []
    global newRoadListCount
    global outputCount
    global t_int
    t_int = time() + 60 * intervall
    while time() < t_end:
        newRoadListCount = newRoadListCount + 1
        roadList = getRandomPopulationWithoutOOB(initSize)
        oobCount = 0
        for road in roadList:
            oobList = getOobTuples(road)
            for oob in oobList:
                oobCount = oobCount + 1
        if oobCount > maxOOBCount:
            maxOOBCount = oobCount
            resultList = roadList
        if t_int < time():
            detail = ['Number of generated road population', newRoadListCount, 'OOB Count:', maxOOBCount]
            createResultsWithDetails('RandomBest', outputCount, resultList, detail)
            outputCount = outputCount + 1
            t_int = t_int + 60 * intervall
    newRoadListCount = 0
    maxOOBCount = 0
    outputCount = 0
    return resultList


if __name__ == "__main__":
    count = 0
    while count < 10:
        resList = main()
        details = ['Number of generated road population', newRoadListCount, 'OOB Count:', maxOOBCount]
        if t_int < time():
            createResultsWithDetails('RandomBest', count, resList, details)
        count = count + 1
        resetPort()

