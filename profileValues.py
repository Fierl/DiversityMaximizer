# This script combines the speed and curve profiles scripts as well as creating the needed number of test cases.

from time import time
from asfault.experiments import *
from beamngpy import BeamNGpy, Scenario, Vehicle
from curveProfile import *
from speedProfile import *
from OobSpeedSearch import *
from KMeans import *

port = 32513
directory = os.getcwd()


# creates a new beamng instance and loads the scenario into it
def runScenario(scenario):
    bng = BeamNGpy('localhost', 64256, home='c:/Users/SimonFierbeck/seminar/research')
    # Create an ETK800 with the licence plate 'PYTHON'
    vehicle = Vehicle('ego_vehicle', model='etk800', licence='PYTHON')
    # Add it to our scenario at this position and rotation
    scenario.add_vehicle(vehicle, pos=(-717, 101, 118), rot=(0, 0, 45))
    # Place files defining our scenario for the simulator to read
    scenario.make(bng)

    # Launch BeamNG.research
    bng.open()
    # Load and start our scenario
    bng.load_scenario(scenario)
    bng.start_scenario()
    # Make the vehicle's AI span the map
    vehicle.ai_set_mode('span')


def getData(list):
    count = 0
    resultList = []
    while count < len(list):
        tup = (list[count], count + 1)
        resultList.append(tup)
        count = count + 1
    return resultList


# gets the road segments and a dictionary containing the nodes as keys
# and the car states as values
def getCarStates(road):
    test = RoadTest.from_dict(road)
    states = road['execution']['states']
    nodes = road['network']['nodes']
    resDic = {}
    nodeList = []
    # creates a list containing the seg_id
    for node in nodes:
        road = nodes[node]
        resDic[road['seg_id']] = None
        nodeList.append(road['seg_id'])
    # puts the car states into a dictionary and as key the segment it's taken from
    for state in states:
        carState = CarState.from_dict(test, state)
        carStateTup = carState.get_segment()
        if carStateTup is not None:
            if resDic[str(carStateTup.seg_id)] is None:
                resDic[str(carStateTup.seg_id)] = [state]
            else:
                resDic[str(carStateTup.seg_id)].append(state)
    return nodeList, resDic


# sets the config up and runs the generated tests inside beamng
def getRandomPopulation(budget):
    global port
    rng = random.Random()
    # getting the config data
    ev = EvolutionConfig('c:/Users/SimonFierbeck/.asfaultenv/cfg/evolution.json')
    con = ev.get_default()

    # setting up config for every modul
    DEFAULT_ENV = os.path.join(str(Path.home()), '.asfaultenv')
    c.load_configuration(DEFAULT_ENV)
    final_path = c.rg.get_final_path()

    # setting up bounds for road generation (out of the config file)
    size = con['bounds']
    bounds = box(-size, -size, size, size)
    
    count = 0
    resTestSuite = []
    while (count < int(budget)):
        testSuiteGen = TestSuiteGenerator()
        # generates a test case
        randomSeed = rng.randint(0, 2 ** 32 - 1)
        test = testSuiteGen.spawn_test(bounds, randomSeed)

        # generates execution states
        runner = TestRunner(test, "levels/asfault", 'localhost', port, False)
        execution = runner.run()

        # writes the states into the final directory
        export_test_exec(final_path, final_path, test)

        with open(final_path + '/test_0001.json') as f:
            data = json.load(f)
            
        oobList = getOobTuples(data)
        res = []
        res.append(data)
        print('Oob List: ', oobList)
        if not oobList:
            resTestSuite.append(data)
            port = port + 1
            count = count + 1
            return resTestSuite
        else:
            port = port + 1
            test = getOob(oobList, test, port)
            export_test_exec(final_path, final_path, test)
            with open(final_path + '/test_0001.json') as f:
                data = json.load(f)
            resTestSuite.append(data)
            port = port + 1
            count = count + 1
            return resTestSuite


# sets the config up and runs the generated tests inside beamng
def getRandomPopulationWithoutOOB(budget):
    global port
    rng = random.Random()
    # getting the config data
    ev = EvolutionConfig('c:/Users/SimonFierbeck/.asfaultenv/cfg/evolution.json')
    con = ev.get_default()

    # setting up config for every modul
    DEFAULT_ENV = os.path.join(str(Path.home()), '.asfaultenv')
    c.load_configuration(DEFAULT_ENV)
    final_path = c.rg.get_final_path()

    # setting up bounds for road generation (out of the config file)
    size = con['bounds']
    bounds = box(-size, -size, size, size)

    count = 0
    resTestSuite = []
    while (count < int(budget)):
        testSuiteGen = TestSuiteGenerator()
        # generates a test case
        randomSeed = rng.randint(0, 2 ** 32 - 1)
        test = testSuiteGen.spawn_test(bounds, randomSeed)

        # generates execution states
        runner = TestRunner(test, "levels/asfault", 'localhost', port, False)
        execution = runner.run()

        # writes the states into the final directory
        export_test_exec(final_path, final_path, test)

        with open(final_path + '/test_0001.json') as f:
            data = json.load(f)

        resTestSuite.append(data)
        port = port + 1
        count = count + 1
    return resTestSuite


def getRandomRoadWithoutExecution():
    global port
    rng = random.Random()
    # getting the config data
    ev = EvolutionConfig('c:/Users/SimonFierbeck/.asfaultenv/cfg/evolution.json')
    con = ev.get_default()

    # setting up config for every modul
    DEFAULT_ENV = os.path.join(str(Path.home()), '.asfaultenv')
    c.load_configuration(DEFAULT_ENV)
    final_path = c.rg.get_final_path()

    # setting up bounds for road generation (out of the config file)
    size = con['bounds']
    bounds = box(-size, -size, size, size)

    resTestSuite = []
    testSuiteGen = TestSuiteGenerator()
    # generates a test case
    randomSeed = rng.randint(0, 2 ** 32 - 1)
    test = testSuiteGen.spawn_test(bounds, randomSeed)
    testDict = RoadTest.to_dict(test)
    resTestSuite.append(testDict)
    return resTestSuite


# need for the deap framework, return one random generated track
def getRandomTrack():
    resList = getRandomPopulation(1)
    return resList[0]


# gets the profile values out of the files
def getProfileValues(test):
    carList, dic = getCarStates(test)
    if type(test) is dict:
        testDict = test
    else:
        testDict = RoadTest.to_dict(test)
    oobList = getOobTuples(testDict)
    if not oobList:
        sProfile = getSpeedValues(carList, dic)
    else:
        sProfile = getSpeedValuesWithOobs(carList, dic, testDict)
    cProfile = getCurveBinsValue(test)
    curveValue = getDistribution(cProfile)
    speedValue = getDistribution(sProfile)

    return curveValue, speedValue


# calculates the distribution of the bins
def getDistribution(disList):
    count = 0
    result = 0
    while count < len(disList):
        if disList[count] > 0:
            result = result + 1
        count = count + 1
    return result / len(disList)


# gets the node and the speed of the out of bounds situation
def getOobTuples(dic):
    resList = []
    seg_oob_count = dic['execution']['seg_oob_count']
    if seg_oob_count:
        tup = (dic['execution']['oob_speeds'], [dic['execution']['seg_oob_count']])
        resList.append(tup)
    return resList


# create a folder if needed and creates json files for each test case
def createResults(type, resList):
    mydir = os.path.join(
        os.getcwd(), 'results', type,
        datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(mydir):
        os.makedirs(mydir)
    count = 1
    for res in resList:
        if count < 10:
            filename = 'test_000' + str(count) + '.json'
        elif count < 100:
            filename = 'test_00' + str(count) + '.json'
        else:
            filename = 'test_0' + str(count) + '.json'
        with open(os.path.join(mydir, filename), 'w') as fp:
            json.dump(res[0], fp)
        count = count + 1

def resetPort():
    global port
    port = 32513

def getPort():
    global port
    newPort = port + 1
    port = port + 2
    return newPort


# create a folder if needed and creates json files for each test case
def createResultsWithDetails(type, outputCount, resList, details):
    mydir = os.path.join(
        os.getcwd(), 'results', type,
        datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(mydir):
        os.makedirs(mydir)
    count = 1
    oobCount = 0
    for ind in resList:
        try:
            oobList = getOobTuples(ind[0])
        except KeyError:
            oobList = getOobTuples(ind)
        for oobs in oobList:
            oobCount = oobCount + 1
    for res in resList:
        if count < 10:
            filename = 'test_000' + str(count) + '.json'
        elif count < 100:
            filename = 'test_00' + str(count) + '.json'
        else:
            filename = 'test_0' + str(count) + '.json'
        try:
            with open(os.path.join(mydir, filename), 'w') as fp:
                json.dump(res[0], fp)
        except KeyError:
            with open(os.path.join(mydir, filename), 'w') as fp:
                json.dump(res, fp)
        count = count + 1
    details.append('OobCount: ')
    details.append(oobCount)
    with open(os.path.join(mydir, 'details' + str(outputCount) + '.txt'), 'w') as fp:
        for item in details:
            fp.write("%s\n" % item)

