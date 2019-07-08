# This script computes the speed profile of a road, which is created through AsFault.

from asfault.plotter import *

# puts all car states of the testfile into bins
def getSpeedBinsValue(dict):
    count = 1
    stateList = []
    # the bins for the speed range between 0 and 100
    bin1 = []
    bin2 = []
    bin3 = []
    bin4 = []
    bin5 = []
    bin6 = []
    bin7 = []
    bin8 = []
    bin9 = []
    bin10 = []
    bin11 = []
    bin12 = []
    bin13 = []
    bin14 = []
    bin15 = []
    bin16 = []
    netW = dict['execution']
    states = netW['states']
    # Get the segment information out of the test file
    for state in states:
        vel_x = state['vel_x'] * state['vel_x']
        vel_y = state['vel_y'] * state['vel_y']
        vel_z = state['vel_z'] * state['vel_z']
        speed = math.sqrt(vel_x + vel_y + vel_z) * 3.6
        stateList.append(speed)
    print(len(stateList))
    # Put the speed into their bins
    for speed in stateList:
        if (int(speed) < 9):
            bin1.append(speed)
        elif (int(speed) < 17):
            bin2.append(speed)
        elif (int(speed) < 26):
            bin3.append(speed)
        elif (int(speed) < 35):
            bin4.append(speed)
        elif (int(speed) < 43):
            bin5.append(speed)
        elif (int(speed) < 52):
            bin6.append(speed)
        elif (int(speed) < 60):
            bin7.append(speed)
        elif (int(speed) < 68):
            bin8.append(speed)
        elif (int(speed) < 76):
            bin9.append(speed)
        elif (int(speed) < 85):
            bin10.append(speed)
        elif (int(speed) < 93):
            bin11.append(speed)
        elif (int(speed) < 100):
            bin12.append(speed)
        elif (int(speed) < 108):
            bin13.append(speed)
        elif (int(speed) < 116):
            bin14.append(speed)
        elif (int(speed) < 124):
            bin15.append(speed)
        else:
            bin16.append(speed)
    return [len(bin1), len(bin2), len(bin3), len(bin4), len(bin5), len(bin6), len(bin7), len(bin8), len(bin9),
            len(bin10), len(bin11), len(bin12), len(bin13), len(bin14), len(bin15), len(bin16)]


# calculates the mean speed of every segment and put them into bins
def getSpeedValues(nodes, carStateDic):
    bin1 = []
    bin2 = []
    bin3 = []
    bin4 = []
    bin5 = []
    bin6 = []
    bin7 = []
    bin8 = []
    bin9 = []
    bin10 = []
    bin11 = []
    bin12 = []
    for node in nodes:
        stateList = carStateDic[node]
        if stateList is not None:
            meanValues = []
            mean = 0
            for carState in stateList:
                state = dict(carState)
                vel_x = state['vel_x'] * state['vel_x']
                vel_y = state['vel_y'] * state['vel_y']
                vel_z = state['vel_z'] * state['vel_z']
                res = math.sqrt(vel_x + vel_y + vel_z) * 3.6
                meanValues.append(res)
            for value in meanValues:
                mean = mean + value
            mean = mean / len(stateList)
            if mean < 9:
                bin1.append(mean)
            elif mean < 17:
                bin2.append(mean)
            elif mean < 26:
                bin3.append(mean)
            elif mean < 35:
                bin4.append(mean)
            elif mean < 43:
                bin5.append(mean)
            elif mean < 52:
                bin6.append(mean)
            elif mean < 60:
                bin7.append(mean)
            elif mean < 68:
                bin8.append(mean)
            elif mean < 76:
                bin9.append(mean)
            elif mean < 85:
                bin10.append(mean)
            elif mean < 93:
                bin11.append(mean)
            else:
                bin12.append(mean)
    return [len(bin1), len(bin2), len(bin3), len(bin4), len(bin5), len(bin6), len(bin7), len(bin8), len(bin9),
            len(bin10), len(bin11), len(bin12)]


# calculates the mean speed of every segment and put them into bins + overwrites the oob speed values
def getSpeedValuesWithOobs(nodes, carStateDic, testDict):
    oobDict = testDict['execution']['seg_oob_count']
    oobSegment = False
    speed = None
    oobs = []
    for oob in oobDict:
        speed = oobDict[oob]
        oobs.append(oob)
    nodesDict = testDict['network']['nodes']
    bin1 = []
    bin2 = []
    bin3 = []
    bin4 = []
    bin5 = []
    bin6 = []
    bin7 = []
    bin8 = []
    bin9 = []
    bin10 = []
    bin11 = []
    bin12 = []
    for node in nodes:
        currentNode = nodesDict[str(node)]
        if currentNode['key'] in oobs :
            oobSegment = True
        stateList = carStateDic[node]
        if stateList is not None:
            meanValues = []
            mean = 0
            for carState in stateList:
                state = dict(carState)
                vel_x = state['vel_x'] * state['vel_x']
                vel_y = state['vel_y'] * state['vel_y']
                vel_z = state['vel_z'] * state['vel_z']
                res = math.sqrt(vel_x + vel_y + vel_z) * 3.6
                meanValues.append(res)
            for value in meanValues:
                mean = mean + value
            if oobSegment:
                mean = speed
                print(mean)
                oobSegment = False
            else:
                mean = mean / len(stateList)
            if mean == 0:
                print('one segment unbinabled')
            elif mean < 9:
                bin1.append(mean)
            elif mean < 17:
                bin2.append(mean)
            elif mean < 26:
                bin3.append(mean)
            elif mean < 35:
                bin4.append(mean)
            elif mean < 43:
                bin5.append(mean)
            elif mean < 52:
                bin6.append(mean)
            elif mean < 60:
                bin7.append(mean)
            elif mean < 68:
                bin8.append(mean)
            elif mean < 76:
                bin9.append(mean)
            elif mean < 85:
                bin10.append(mean)
            elif mean < 93:
                bin11.append(mean)
            else:
                bin12.append(mean)
    return [len(bin1), len(bin2), len(bin3), len(bin4), len(bin5), len(bin6), len(bin7), len(bin8), len(bin9),
            len(bin10), len(bin11), len(bin12)]