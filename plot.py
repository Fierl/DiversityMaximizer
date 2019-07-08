import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import mannwhitneyu
import json
import os
import numpy as np
from curveProfile import *
from speedProfile import *
from OobSpeedSearch import *
from profileValues import  *
from A12 import *
import math
speedSsamplePath = 'c:/Users/SimonFierbeck/AsFault/results/RandomBest/speed/'
curvatureSamplePath = 'c:/Users/SimonFierbeck/AsFault/results/RandomBest/curvature/'
path = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/Novelty/Final'
finalNoveltyPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/Novelty/Best'
finalRandomPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/RandomBest/Best'
finalEvolutionaryPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/Evolutionary/Best'
overallFinalEvolutionaryPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/Evolutionary/Final'
overallFinalNoveltyPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/Novelty/Final'
overallFinalRandomPath = 'c:/Users/SimonFierbeck/AsFault/results/oobCounted/RandomBest/Final'
timeLabel = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]
segmentLabel = ['L_sS', 'L_sN', 'L_sW', 'L_lS', 'L_lN', 'L_lW', 'R_sS', 'R_sN', 'R_sW', 'R_lS', 'R_lN', 'R_lW']
speedLabel = ['0-9', '10-17', '18-26', '27-35', '36-44', '45-53', '54-61', '62-69', '70-77', '78-85', '86-93', '93-']
maxTestSuiteCount = 2
maxTestCaseCount = 10
firstTestSuiteCount = 1

#New High& Low Statistics=4159.000, p=0.000
#A12 New High& Low  0.7174592391304347

def getLowAndHighValues():
    methodCount = 0
    pathToDirectory = overallFinalNoveltyPath
    resList = []
    lowList = []
    highList = []
    lowValues = []
    lowMidValues = []
    highMidValues = []
    highValues = []
    novLow = []
    novHigh = []
    evoLow = []
    evoHigh = []
    testSuiteCount = 1
    while methodCount < 2:
        if methodCount == 1:
            pathToDirectory = overallFinalEvolutionaryPath
        elif methodCount == 2:
            pathToDirectory = overallFinalRandomPath
        while testSuiteCount < 16:
            count = 0
            while count < 12:
                path = os.path.join(pathToDirectory + str(testSuiteCount), str(count))
                oobList = []
                count2 = 0
                for file in os.listdir(path):
                    count2 = count2 + 1
                    if file.endswith("oobCount.txt"):
                        filePath = os.path.join(path, file)
                        f = open(filePath, "r")
                        f1 = f.readlines()
                        lineCount = 0
                        for x in f1:
                            myIntegers = x.split(" ", 1)
                            oobs = int(list(filter(str.isdigit, myIntegers[1]))[0])
                            try:
                                oobs = str(oobs)
                                oobs = oobs + str(list(filter(str.isdigit, myIntegers[1]))[1])
                                oobs = 5
                            except:
                                oobs = int(oobs)
                            oobList.append(oobs)
                            lineCount = lineCount + 1
                            if lineCount == 10:
                                break
                    print('oobList', oobList)
                    print('count222', count2)
                    if count2 < 10 and file.endswith(".json"):
                        with open(os.path.join(path, file), 'r') as f:
                            data = json.load(f)
                        testValues = getProfileValues(data)
                        if testValues[0] < 0.7 and testValues[1] < 0.7:
                            if (methodCount == 0):
                                novLow.append(oobList[2])
                            else:
                                evoLow.append((oobList[2]))
                            lowValues.append(oobList[count2])
                        elif testValues[0] < 0.65 and testValues[1] < 0.65:
                            if (methodCount == 0):
                                novLow.append(oobList[2])
                            else:
                                evoLow.append((oobList[2]))
                            lowValues.append(oobList[count2])
                            lowMidValues.append(oobList[count2])
                        elif testValues[0] < 0.7 and testValues[1] < 0.7:
                            highMidValues.append(oobList[count2])
                        else:
                            if (methodCount == 0):
                                novHigh.append(oobList[2])
                            else:
                                evoHigh.append((oobList[2]))
                            highValues.append(oobList[count2])
                        testValue = testValues[0] + testValues[1]
                        print('TestValues', testValues)
                        print('TestValues', testValue)
                        if testValue < 1.2:
                            print(testValue)
                            print('TestValues33', testValue)
                            print('TestValues333', testValue)
                            lowList.append(oobList[count2])
                        else:
                            highList.append(oobList[count2])
                resList.append(oobList)
                print(resList)
                count = count + 1
                print('count', count)
            testSuiteCount = testSuiteCount + 1
        testSuiteCount = 1
        count = 0
        methodCount = methodCount + 1
        print(methodCount)
    print('lowVlalue: ', len(lowValues))
    print('lowMidVlalue: ', len(lowMidValues))
    print('highMidVlalue: ', len(highMidValues))
    print('highVlalue: ', len(highValues))
    print('evoLow: ', len(evoLow))
    print('evoHigh: ', len(evoHigh))
    print('novLow: ', len(novLow))
    print('novHigh: ', len(novHigh))
    lowValue = 0
    newLowList = []
    newHighList = []
    highValue = 0
    for value in lowList:
        lowValue = lowValue + value
        if value is not 0:
            newLowList.append(value)
    for value in highList:
        highValue = highValue + value
        if value is not 0:
            newHighList.append(value)
    lowValue = lowValue / len(lowList)
    highValue = highValue / len(highList)
    print('lowList', lowList)
    print('highList', highList)
    print('newlowList', newLowList)
    print('newhighList', newHighList)
    print('HighValue:::',highValue)
    print('LowValue:::', lowValue)

    stat, p = mannwhitneyu(highValues, lowValues)
    print('New High& Low Statistics=%.3f, p=%.3f' % (stat, p))

    print('A12 New High& Low ', a12(highValues, lowValues))

    plotBoxplot(highValues, lowValues)
    plotHistogramsForLowAndHigh(novLow, novHigh, evoLow, evoHigh)
    plotBoxplot(newHighList, newLowList)
    return resList

def plotHistogramsForLowAndHigh(novLow, novHigh, evoLow, evoHigh):
    evoNumber = 0
    novNumber = 0

    for oob in evoLow:
        evoNumber = evoNumber + 1
    for oob in evoHigh:
        evoNumber = evoNumber + 1
    for oob in novLow:
        novNumber = novNumber + 1
    for oob in novHigh:
        novNumber = novNumber + 1

    print(evoNumber)
    print(novNumber)

    evoBoth = [round((len(evoLow) / evoNumber) * 100, 1), round((len(evoHigh) / evoNumber) * 100, 1)]
    novBoth = [round((len(novLow) / novNumber) * 100, 1), round((len(novHigh) / novNumber) * 100, 1)]

    ind = np.arange(len(novBoth))  # the x locations for the groups
    width = 0.25  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width / 2, evoBoth, width,
                    label="multi-objective search ")
    rects2 = ax.bar(ind + width / 2, novBoth, width,
                    label="novelty search ")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Percantage of distribution")
    #ax.set_title('Scores by group and gender')
    ax.set_xticks(ind)
    #ax.set_yticklabels([10,0,10,20,30])
    ax.set_xticklabels(['lower profile-values', 'higher profile-values'])
    ax.legend()

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(abs(height)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos] * 3, 3),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')

    def autolabelBeneath(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(abs(height)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos] * 3, -15),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')


    autolabel(rects1, "left")
    autolabel(rects2, "right")

    # red_patch = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # red_patch2 = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # plt.legend(handles=[red_patch, red_patch2])

    fig.tight_layout()

    plt.show()


# Plots a boxplot of the oobCount regarding the
def plotBoxplot(highList, lowList):

    oobListDict = {'Lower profile-values': lowList, 'Higher profile-values': highList}

    fig1, ax = plt.subplots()
    ax.boxplot(oobListDict.values())
    ax.set_xticklabels(oobListDict.keys())
    ax.set_ylabel("Number of Oob's")
    #ax1.boxplot(boxPlotData)

    #plt.xticks(np.arange(0, 60 + 1, 6.0))
    plt.yticks(np.arange(0, 10 + 1, 5.0))
    plt.show()


def getOobSegmentFromJson(pathToDirectory, count):
    resList = []
    path = os.path.join(pathToDirectory, str(count))
    for file in os.listdir(path):
        if file.endswith("oobCount.txt"):
            filePath = os.path.join(path, file)
            f = open(filePath, "r")
            f1 = f.readlines()
            lineCount = 0
            for x in f1:
                if lineCount < 10:
                    myIntegers = x.split(" ")
                    lineCount = lineCount + 1
                else:
                    myIntegers = x.split(" ")
                    for y in myIntegers:
                        resList.append(y)
    return resList

def getOobsFromJson(pathToDirectory, count):
    resList = []
    path = os.path.join(pathToDirectory, str(count))
    for file in os.listdir(path):
        if file.endswith("oobCount.txt"):
            filePath = os.path.join(path, file)
            f = open(filePath, "r")
            f1 = f.readlines()
            lineCount = 0
            for x in f1:
                myIntegers = x.split(" ", 1)
                oobs = int(list(filter(str.isdigit, myIntegers[1]))[0])
                try:
                    oobs = str(oobs)
                    oobs = oobs + str(list(filter(str.isdigit, myIntegers[1]))[1])
                    oobs = 5
                except:
                    oobs = int(oobs)
                resList.append(oobs)
                lineCount = lineCount + 1
                if lineCount == 10:
                    break
    return resList

def getTestsFromJson(pathToDirectory):
    resBinList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    resList = []
    count = 1
    while count < 13:
        path = os.path.join(pathToDirectory, str(count))
        for file in os.listdir(path):
            if file.endswith(".json"):
                filePath = os.path.join(path, file)
                with open(filePath) as f:
                    data = json.load(f)
                curveBinValues = getCurveBinsValue(data)
                print(curveBinValues)
                binCount = 0
                while binCount < 12:
                    if binCount == 6:
                        resBinList[binCount] = resBinList[binCount] + 1
                    else:
                        resBinList[binCount] = resBinList[binCount] + curveBinValues[binCount]
                    binCount = binCount + 1
        count = count + 1
    print(resBinList)
    return resBinList

def plotHistogramsForBoth(evoBins, novBins, allEvo, allNov):
    print('BinsEvo1:', evoBins)
    print('NovBins1:', novBins)
    evoNumber = 0
    novNumber = 0

    for oob in evoBins:
        evoNumber = evoNumber + oob
    for oob in novBins:
        novNumber = novNumber + oob

    allEvoNumber = 0
    allNovNumber = 0

    for oob in allEvo:
        allEvoNumber = allEvoNumber + oob
    for oob in allNov:
        allNovNumber = allNovNumber + oob

    print(evoNumber)
    print(novNumber)
    print(allNovNumber)
    print(allEvoNumber)

    binCount = 0
    while binCount < 12:
        evoBins[binCount] = round(((evoBins[binCount] / evoNumber) * 100), 1)
        binCount = binCount + 1
    binCount = 0
    while binCount < 12:
        novBins[binCount] = round(((novBins[binCount] / novNumber) * 100), 1)
        binCount = binCount + 1
    binCount = 0
    while binCount < 12:
        allEvo[binCount] = round((-(allEvo[binCount] / allEvoNumber) * 100), 1)
        binCount = binCount + 1
    binCount = 0
    while binCount < 12:
        allNov[binCount] = round((-(allNov[binCount] / allNovNumber) * 100), 1)
        binCount = binCount + 1

    print('BinsEvo', evoBins)
    print('NovBins:', novBins)

    stat, p = mannwhitneyu(evoBins, novBins)
    print('Statistics=%.3f, p=%.3f' % (stat, p))

    print('A12 histogram ', a12(evoBins, novBins))

    utilityForEvoLabel = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,)
    utilityForNovLabel = (0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1,)
    utilityForAllEvoLabel = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,)
    utilityForAllNovLabel = (1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1,)

    ind = np.arange(len(novBins))  # the x locations for the groups
    width = 0.25  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width / 2, evoBins, width, yerr=utilityForEvoLabel,
                    label="multi-objective search with oob's in it")
    rects2 = ax.bar(ind + width / 2, novBins, width, yerr=utilityForNovLabel,
                    label="novelty search with oob's in it")
    rects3 = ax.bar(ind - width / 2, allEvo, width, color='gray', yerr=utilityForAllEvoLabel,
                    label='all road-segments of multi-objective')
    rects4 = ax.bar(ind + width / 2, allNov, width, color='black', yerr=utilityForAllNovLabel,
                    label='all road-segments of novelty')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("relative number of oob's")
    #ax.set_title('Scores by group and gender')
    ax.set_xticks(ind)
    #ax.set_yticklabels([10,0,10,20,30])
    ax.set_xticklabels(segmentLabel)
    ax.legend()

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(abs(height)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos] * 3, 3),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')

    def autolabelBeneath(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(abs(height)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos] * 3, -15),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')


    autolabel(rects1, "left")
    autolabel(rects2, "right")
    autolabelBeneath(rects3, "left")
    autolabelBeneath(rects4, "right")

    # red_patch = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # red_patch2 = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # plt.legend(handles=[red_patch, red_patch2])

    fig.tight_layout()

    plt.show()


def getMeanOob(listOfOobResults):
    resList = []
    print('List::::', listOfOobResults)
    print(listOfOobResults[0])
    testCaseCount = 0
    while testCaseCount < maxTestCaseCount:
        meanValue = 0
        testSuiteCount = 0
        while testSuiteCount < maxTestSuiteCount:
            meanValue = meanValue + listOfOobResults[testSuiteCount][testCaseCount]
            testSuiteCount = testSuiteCount + 1
        meanValue = meanValue / maxTestSuiteCount
        testCaseCount = testCaseCount + 1
        resList.append(meanValue)
    return resList


def getOobCount(listOfOobResults):
    resList = []
    print('ListDist::::', listOfOobResults)
    for oobResult in listOfOobResults:
        count = 0
        for value in oobResult:
            count = count + value
        resList.append(count)
    print('reslist:', resList)
    return resList


def getOverallMeanList():
    count = 0
    testSuiteList = []
    global path
    while count < 12:
        listOfOobs = getOobsFromJson(path, count)
        print(listOfOobs)
        testSuiteList.append(listOfOobs)
        count = count + 1
    meanList = getMeanOob(testSuiteList)
    return meanList

def getTestSuiteMeanValue(testSuite):
    meanValue = 0
    for oob in testSuite:
        meanValue = meanValue + oob
    meanValue = meanValue
    return meanValue

def plotGraphOobCountPerTime(oobCountList):
    meanList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for oobCount in oobCountList:
        count = 0
        plt.plot(timeLabel, oobCount, color='gray')
        while count < 12:
            meanList[count] = meanList[count] + oobCount[count]
            count = count + 1
    count = 0
    while count < 12:
        meanList[count] = meanList[count] / len(oobCountList)
        count = count + 1
    plt.plot(timeLabel, meanList, '-p', color='red',
             markersize=15, linewidth=4,
             markerfacecolor='white',
             markeredgecolor='gray',
             markeredgewidth=2)
    red_patch = mpatches.Patch(color='red', label='Mean value')
    plt.legend(handles=[red_patch])
    grey_patch = mpatches.Patch(color='grey', label='Executions')
    plt.legend(handles=[grey_patch, red_patch])
    plt.xticks(np.arange(0, max(timeLabel) + 1, 30.0))
    plt.yticks(np.arange(0, 50 + 1, 5.0))
    plt.show()


# Plots a boxplot of the oobCount regarding the
def plotBoxplotOob():
    count = 1
    oobNoveltyList = []
    oobRandomList = []
    oobEvolutionaryList = []
    while count < 16:
        oobNoveltyList.append(getOobsFromJson(finalNoveltyPath, count))
        oobRandomList.append(getOobsFromJson(finalRandomPath, count))
        oobEvolutionaryList.append(getOobsFromJson(finalEvolutionaryPath, count))
        count = count + 1

    print('OobListN', oobNoveltyList)
    print('OobListR', oobRandomList)
    print('OobListE', oobEvolutionaryList)
    print('hereN', getOobCount(oobNoveltyList))
    print('hereR', getOobCount(oobRandomList))
    print('hereE', getOobCount(oobEvolutionaryList))

    boxPlotNoveltyData = getOobCount(oobNoveltyList)
    boxPlotRandomData = getOobCount(oobRandomList)
    boxPlotEvolutionaryData = getOobCount(oobEvolutionaryList)
    stat, p = mannwhitneyu(boxPlotEvolutionaryData, boxPlotNoveltyData)
    print('Evo& Nov Statistics=%.3f, p=%.3f' % (stat, p))
    stat, p = mannwhitneyu(boxPlotRandomData, boxPlotNoveltyData)
    print('Random& Nov Statistics=%.3f, p=%.3f' % (stat, p))
    stat, p = mannwhitneyu(boxPlotEvolutionaryData, boxPlotRandomData)
    print('Evo& Random Statistics=%.3f, p=%.3f' % (stat, p))
    oobListDict = {'Novelty': boxPlotNoveltyData, 'Random': boxPlotRandomData, 'Multi-objective': boxPlotEvolutionaryData}

    print('A12 Evo& Nov ', a12(boxPlotEvolutionaryData, boxPlotNoveltyData))
    print('A12 Random& Nov ', a12(boxPlotRandomData, boxPlotNoveltyData))
    print('A12 Evo& Random ', a12(boxPlotEvolutionaryData, boxPlotRandomData))

    fig1, ax = plt.subplots()
    ax.boxplot(oobListDict.values())
    ax.set_xticklabels(oobListDict.keys())
    ax.set_ylabel("Number of oob's per test-suite")
    #ax.set_xticklabels('Number')
    #ax1.boxplot(boxPlotData)

    #plt.xticks(np.arange(0, 60 + 1, 6.0))
    plt.yticks(np.arange(0, 50 + 1, 5.0))
    plt.show()

def plotGraphOverallTestSuiteMeanValues():
    meanListList = []
    numberOfTestSuites = 16
    global firstTestSuiteCount
    while firstTestSuiteCount < numberOfTestSuites:
        meanList = []
        count = 0
        while count < 12:
            listOfOobs = getOobsFromJson(path + str(firstTestSuiteCount), count)
            print(listOfOobs)
            meanValue = getTestSuiteMeanValue(listOfOobs)
            meanValue = meanValue
            meanList.append(meanValue)
            count = count + 1
        meanListList.append(meanList)
        firstTestSuiteCount = firstTestSuiteCount + 1
    print(meanListList)
    plotGraphOobCountPerTime(meanListList)


# bins for the road segments l_ = left, r_ = right, l = large,
# s = short, S = sharp, N = normal, W = wide
# put the l_turn segments from a list into their six bins
def putL_TurnsIntoBins(l_turns):
    l_sSCurve = []
    l_sNCurve = []
    l_sWCurve = []
    l_lSCurve = []
    l_lNCurve = []
    l_lWCurve = []
    for turn in l_turns:
        pivot = turn[0]
        angle = abs(turn[0])
        if pivot < 25:
            if angle < 4:
                l_sSCurve.append(turn)
            elif angle > 44 and angle < 90:
                l_sNCurve.append(turn)
            else:
                l_sWCurve.append(turn)
        else:
            if angle < 45:
                l_lSCurve.append(turn)
            elif angle > 44 and angle < 90:
                l_lNCurve.append(turn)
            else:
                l_lWCurve.append(turn)
    return l_sSCurve, l_sNCurve, l_sWCurve, l_lSCurve, l_lNCurve, l_lWCurve

# 6 bins for the road segments l_ = left, r_ = right, l = large,
# s = short, S = sharp, N = normal, W = wide
# put the r_turn segments from a list into their six bins
def putR_TurnsIntoBins(r_turns):
    r_sSCurve = []
    r_sNCurve = []
    r_sWCurve = []
    r_lSCurve = []
    r_lNCurve = []
    r_lWCurve = []
    for turn in r_turns:
        pivot = turn[1]
        angle = abs(turn[0])
        if pivot < 25:
            if angle < 45:
                r_sSCurve.append(turn)
            elif angle > 44 and angle < 90:
                r_sNCurve.append(turn)
            else:
                r_sWCurve.append(turn)
        else:
            if angle < 45:
                r_lSCurve.append(turn)
            elif angle > 44 and angle < 90:
                r_lNCurve.append(turn)
            else:
                r_lWCurve.append(turn)
    return r_sSCurve, r_sNCurve, r_sWCurve, r_lSCurve, r_lNCurve, r_lWCurve

def seperateSegments(segmentList):
    l_turns = []
    r_turns = []
    straights = []
    count = 0
    try:
        for segment in segmentList:
            infos = segment.split('_')
            # seperate the segments and put them into the needed list
            if infos[0].startswith('straight'):
                length = float(infos[1])
                tup = (segment, length)
                straights.append(tup)
            else:
                if infos[0].startswith('l'):
                    angle = int(infos[2])
                    pivotInfo = infos[3].split((' '))
                    pivot = float(pivotInfo[0])
                    tup = (angle, pivot)
                    l_turns.append(tup)
                else:
                    angle = int(infos[2])
                    pivotInfo = infos[3].split((' '))
                    pivot = float(pivotInfo[0])
                    tup = (angle, pivot)
                    r_turns.append(tup)
    except:
        count = count + 1
    return straights, l_turns, r_turns

def seperateSegmentsSample(dic):
    l_turns = []
    r_turns = []
    straights = []
    count = 1
    netW = dic['network']
    nodes = netW['nodes']
    # Get the keys of all the segments
    while count < 1000:
        # try because of the inconsitence of the key values
        try:
            node = nodes[str(count)]
            name = node['key']
            seg_id = int(node['seg_id'])
            infos = name.split('_')
            # seperate the segments and put them into the needed list
            if name.startswith('straight'):
                length = float(infos[1])
                tup = (seg_id, length)
                straights.append(tup)
            elif name.startswith('root'):
                count = count
            else:
                if name.startswith('l'):
                    angle = int(infos[2])
                    pivot = float(infos[3])
                    tup = (seg_id, angle, pivot)
                    l_turns.append(tup)
                else:
                    angle = int(infos[2])
                    pivot = float(infos[3])
                    tup = (seg_id, angle, pivot)
                    r_turns.append(tup)
            count = count + 1
        except KeyError:
            count = count + 1
    return straights, l_turns, r_turns

def putSegmentsIntoBin(path):
    bestCount = 1
    resBinList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    while bestCount < 15:
        resList = getOobSegmentFromJson(path, bestCount)
        straights, l_turns, r_turns = seperateSegments(resList)
        l_turns = putL_TurnsIntoBins(l_turns)
        r_turns = putR_TurnsIntoBins(r_turns)
        binValues = orderCurveIntoBins(r_turns, l_turns)
        binCount = 0
        print(binValues)
        while binCount < 12:
            resBinList[binCount] = resBinList[binCount] + binValues[binCount]
            binCount = binCount + 1
        bestCount = bestCount + 1
    return resBinList

def putMeanSegmentsIntoBin(path):
    bestCount = 1
    result = []
    resBinList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    while bestCount < 15:
        resList = getOobSegmentFromJson(path, bestCount)
        straights, l_turns, r_turns = seperateSegments(resList)
        l_turns = putL_TurnsIntoBins(l_turns)
        r_turns = putR_TurnsIntoBins(r_turns)
        binValues = orderCurveIntoBins(r_turns, l_turns)
        binCount = 0
        print(binValues)
        while binCount < 12:
            resBinList[binCount] = resBinList[binCount] + binValues[binCount]
            binCount = binCount + 1
        bestCount = bestCount + 1
        result.append(resBinList)
        resBinList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return result

def plotHistogram(binValues):
    yint = range(0, math.ceil(max(binValues)) + 1)
    fig, ax = plt.subplots()
    plt.yticks(yint)
    ax.hist(binValues, bins=24)
    ax.set_xticklabels(segmentLabel)
    plt.show()

def plotHistogramsForSample(evoBins, novBins):
    print('BinsEvo1:', evoBins)
    print('NovBins1:', novBins)

    stat, p = mannwhitneyu(evoBins, novBins)
    print('Statistics=%.3f, p=%.3f' % (stat, p))

    print('A12 histogram ', a12(evoBins, novBins))
    
    binaryEvo = []
    binaryNov = []
    
    for x in novBins:
        if x > 0:
            binaryEvo.append(-1)
        else:
            binaryEvo.append(0)

    print(binaryEvo)

    utilityForEvoLabel = (0, 0, 0.1, 0, 0, 0.1, 0, 0, 0, 0.1, 0, 0,)
    utilityForBinaryLabel = (0, 0, 0.1, 0, 0, 0, 0.1, 0.1, 0.1, 0.1, 0, 0,)

    ind = np.arange(len(novBins))  # the x locations for the groups
    width = 0.25  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width / 2, novBins, width, label=' Total distribution')
    rects2 = ax.bar(ind + width / 2, binaryEvo, width, color='black', label=' Binary distribution')


    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of segments')
    ax.set_yticks([-1, 0, 1, 2])
    #ax.set_title('Scores by group and gender')
    ax.set_xticks(ind)
    ax.set_xticklabels(speedLabel)
    ax.set_yticklabels([1, 0, 1, 2])
    ax.legend()

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos] * 3, 3),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')

    #autolabel(rects1, "left")
    #autolabel(rects2, "right")

    # red_patch = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # red_patch2 = mpatches.Patch(label='l_ = left, r_ = right, l = large,')
    # plt.legend(handles=[red_patch, red_patch2])

    fig.tight_layout()

    plt.show()

def plotSample():
    f = open('c:/Users/SimonFierbeck/AsFault/results/RandomBest/speed/1/test_0001.json')
    data1 = json.load(f)
    f.close()
    f = open('c:/Users/SimonFierbeck/AsFault/results/RandomBest/curvature/1/test_0001.json')
    data2 = json.load(f)
    f.close()
    speedBins = getCurveBinsValue(data1)
    curvatureBins = getCurveBinsValue(data2)
    plotHistogramsForSample(speedBins, curvatureBins)
    #test1 = RoadTest.from_dict(data1)
    #test2 = RoadTest.from_dict(data2)
    carList, dic = getCarStates(data1)
    sProfile1 = getSpeedValues(carList, dic)
    print(sProfile1)
    carList, dic = getCarStates(data2)
    sProfile2 = getSpeedValues(carList, dic)
    print(sProfile2)
    plotHistogramsForSample(sProfile1, sProfile2)

def main():
    getLowAndHighValues()
    plotBoxplotOob()
    plotGraphOverallTestSuiteMeanValues()
    binEvolutionaryValues = putSegmentsIntoBin(finalEvolutionaryPath)
    binNoveltyValues = putSegmentsIntoBin(finalNoveltyPath)
    evoList = getTestsFromJson(finalEvolutionaryPath)
    novList = getTestsFromJson(finalNoveltyPath)
    #print('Bin', binValues)
    plotHistogram(binValues)
    plotHistogramsForBoth(binEvolutionaryValues, binNoveltyValues, evoList, novList)
    #plotSample()
    #print(binValues)




if __name__ == "__main__":
    # with open("pareto_front/zdt1_front.json") as optimal_front_data:
    #     optimal_front = json.load(optimal_front_data)
    # Use 500 of the 1000 points in the json file
    # optimal_front = sorted(optimal_front[i] for i in range(0, len(optimal_front), 2))

    main()