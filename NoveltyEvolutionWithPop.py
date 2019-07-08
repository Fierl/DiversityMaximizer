# This script creates a test suite, which contains roads, where the distance between each speed and curve profile
# of the individuals is maximized.

from deap import base
from deap import creator
from deap import tools
from profileValues import *
from func_timeout import *
import time

# settings for the evolutionary algorithm
initSize = 10
numberOfGenerations = 10
resultSize = initSize
# time for the evolution (in min)
computationTime = 360
intervall = 30
t_int = time.time() + 60 * intervall
# needed help variables for the evolution
offspring = []
offspringCount = 0
# statistical variable
newRoads = 0
outputCounts = 0
mutationProbability = 0.05
mutTried = 0
mutAccomplished = 0
cxTried = 0
cxAccomplished = 0

finalPath = 'c:/Users/SimonFierbeck/AsFault/results/Novelty/10'

# calculates the difference of the test suite
def getDistance(testSuite):
    distance = 0
    count = 0
    while (count < len(testSuite) - 1):
        distance = distance + abs(testSuite[count].fitness.values[0] - testSuite[count + 1].fitness.values[0]) \
                   + abs(testSuite[count].fitness.values[1] - testSuite[count + 1].fitness.values[1])
        count = count + 1
    return distance


# changes the test suite for each distance calculation
def getNewList(testSuite, ind, index):
    testSuite[index] = ind
    return testSuite


# evaluates the speed and curve profile of a test
def evalTest(individual):
    i = iter(individual)
    try:
        values = getProfileValues(individual[0])
    except TypeError:
        values = evalTest(individual[0])
    return values

# takes one road segment randomly out of a list of tests
def getRandomRoadsegment():
    roadList = getRandomRoadWithoutExecution()
    randomDict = roadList[0]
    randomNodes = randomDict['network']['nodes']
    nodesList = []
    for node in randomNodes:
        nodesList.append(node)
    randomNodesNumber = nodesList[random.randint(0, len(nodesList) - 1)]
    return randomNodes[randomNodesNumber]

# writes the new segment into the nodes section of a road
def putSegmentIntoRoad(road, segment):
    dic = road[0]
    nodes = dic['network']['nodes']
    seg_id = 1
    newIndex = False
    tup = (newIndex, segment)
    while newIndex == False:
        if str(seg_id) not in nodes:
            tup = (seg_id, segment)
            newIndex = True
        else:
            seg_id = seg_id + 1
    nodes[str(seg_id)] = segment
    nodes = dict(nodes)
    dic['network']['nodes'] = nodes
    road[0] = dic
    road = putSegmentIntoParentage(road, seg_id)
    return road


# writes a new segment into the nodes section of a road
def changeSegment(road, segment):
    dic = road[0]
    nodes = dic['network']['nodes']
    nodeList = []
    for node in nodes:
        nodeList.append(node)
    randomNumber = random.randint(0, len(nodeList) - 1)
    randomIndex = nodeList[randomNumber]
    nodes[randomIndex] = segment
    nodes = dict(nodes)
    dic['network']['nodes'] = nodes
    road[0] = dic
    return road


# writes a new segment into the parentage section of a road
def putSegmentIntoParentage(road, seg_id):
    dic = road[0]
    parentage = dic['network']['parentage']
    randomIndex = random.randint(1, len(dic) - 1)
    before = parentage[randomIndex][1]
    after = parentage[randomIndex][0]
    firstTup = [seg_id, before]
    lastTup = [after, seg_id]
    parentage.pop(randomIndex)
    parentage.insert(randomIndex, firstTup)
    parentage.insert(randomIndex, lastTup)
    dic['network']['parentage'] = parentage
    road[0] = dic
    return road


# gets a road segment as a target to mutate
def get_target(network):
    key = None
    options = [option for option in network.nodes.values(
    ) if option.roadtype not in GHOST_TYPES]
    options = [option for option in options if option.key != key]
    if options:
        return random.choice(options)
    return None


# writes a new segment into the nodes section of a road
@func_set_timeout(5)
def changeRoadSegment(road, segment):
    dic = road[0]
    network = dic['network']
    newNetwork = NetworkLayout.from_dict(network)
    nodes = dic['network']['nodes']
    nodeList = []
    for node in nodes:
        nodeList.append(node)
    randomNumber = random.randint(0, len(nodeList) - 1)
    randomIndex = nodeList[randomNumber]
    target = get_target(newNetwork)
    newSegment = NetworkNode.from_dict(segment)
    newNetwork.replace_node(target, newSegment)
    dic['network'] = network
    road[0] = network
    return road


# picks out a road segment of the test suite and tries to mutate a road with this. There is also a check of the
# mutation probability
def mutator(population, road, mutProb):
    chance = random.random()
    resRoad = None
    newRoad = toolbox.clone(road)
    global mutTried
    if chance < mutProb:
        mutTried = mutTried + 1
        try:
            randomSegment = getRandomRoadsegment()
            newRoad = changeRoadSegment(newRoad, randomSegment)
            resRoad = runTest(newRoad)
        except:
            print('Timeout mut')
        if resRoad is not None:
            return resRoad
        else:
            resRoad = mutator(population, road, mutProb)
            return resRoad
    else:
        return resRoad


# runs the through evolution created roads
def runTest(road):
    dic = road[0]
    try:
        layout = getNetworkLayout(dic)
    except FunctionTimedOut:
        print('Timeout mutated')
    except TypeError:
        try:
            layout = getNetworkLayout(dic[0])
        except FunctionTimedOut:
            print('Timeout mutated#2')
    testSuiteGen = TestSuiteGenerator()
    try:
        newTest = testSuiteGen.test_from_network(layout)
        final_path = c.rg.get_final_path()
        port = 32513
        runner = TestRunner(newTest, "levels/asfault", 'localhost', port, False)
        try:
            execution = func_timeout(90, runner.run)
            export_test_exec(final_path, final_path, newTest)
            with open(final_path + '/test_0001.json') as f:
                ind1 = json.load(f)
            oobList = getOobTuples(ind1)
            print('Oob List: ', oobList)
            if oobList:
                port = port + 1
                newTest = getOob(oobList, newTest, port)
                export_test_exec(final_path, final_path, newTest)
                with open(final_path + '/test_0001.json') as f:
                    ind1 = json.load(f)
        except FunctionTimedOut:
            runner.kill_beamng()
            sleep(10)
            ind1 = None
    except Exception as e:
        ind1 = None
    return ind1


# splits a road dic into two for the crossover operation
def split_dict(a_dict):
    sortedDictList = sorted(a_dict.items(), key=lambda i: int(i[0]))
    firstList = []
    lastList = []
    count = 0
    while count < len(sortedDictList) / 2:
        firstList.append(sortedDictList[count])
        count = count + 1
    while count < len(sortedDictList):
        lastList.append(sortedDictList[count])
        count = count + 1
    return firstList, lastList


# splits a road list into two for the crossover operation
def split_list(a_list):
    count = 0
    firstHalf = []
    lastHalf = []
    if len(a_list) % 2 != 0:
        a_list.pop(int(len(a_list) / 2))
    while count < len(a_list) / 2:
        firstHalf.append(a_list[count])
        count = count + 1
    while count < len(a_list):
        if count == len(a_list) / 2:
            count = count + 1
            continue
        else:
            lastHalf.append(a_list[count])
            count = count + 1
    return firstHalf, lastHalf


# Function to compute the missing parentage tuple for the test.
def putNewParentInList(a_list):
    count = 0
    resList = []
    for dic in a_list:
        resList.append(dic)
    while count < len(resList) - 1:
        if (resList[count][1] != resList[count + 1][0]):
            tup = [resList[count][1], resList[count + 1][0]]
            resList.insert(count + 1, tup)
        count = count + 1
    return resList


# Help Function used to invoke a timer
@func_set_timeout(5)
def getNetworkLayout(dic):
    try:
        resLayout = NetworkLayout.from_dict(dic['network'])
    except:
        resLayout = NetworkLayout.from_dict(dic)
    return resLayout


# creates a list filled with two segment lists
def fillCrossList(firstList, lastList):
    resList = []
    for ele in firstList:
        resList.append(ele)
    for ele in lastList:
        resList.append(ele)
    return resList


def crossParents(mom, dad):
    testSuiteGen = TestSuiteGenerator()

    momDict = mom[0]
    dadDict = dad[0]

    momNodes = momDict['network']['nodes']
    dadNodes = dadDict['network']['nodes']

    momParent = momDict['network']['parentage']
    dadParent = dadDict['network']['parentage']

    # splits the road segments
    firstHelpMomNodes, lastHelpMomNodes = split_dict(momNodes)
    firstHelpDadNodes, lastHelpDadNodes = split_dict(dadNodes)

    newMomNodes = fillCrossList(firstHelpMomNodes, lastHelpDadNodes)
    newDadNodes = fillCrossList(firstHelpDadNodes, lastHelpMomNodes)

    # splits the road parentage
    firstHelpMomParent, lastHelpMomParent = split_list(momParent)
    firstHelpDadParent, lastHelpDadParent = split_list(dadParent)

    newMomParent = fillCrossList(firstHelpMomParent, lastHelpDadParent)
    newDadParent = fillCrossList(firstHelpDadParent, lastHelpMomParent)

    newMomParent = putNewParentInList(newMomParent)
    newDadParent = putNewParentInList(newDadParent)

    newMomNodes = dict(newMomNodes)
    newDadNodes = dict(newDadNodes)

    momDict['network']['nodes'] = newMomNodes
    dadDict['network']['nodes'] = newDadNodes

    momDict['network']['parentage'] = newMomParent
    dadDict['network']['parentage'] = newDadParent

    # run and evaluate the new created tests
    try:
        momLayout = getNetworkLayout(momDict)
    except FunctionTimedOut:
        print('Timeout mom')
    except TypeError:
        try:
            momLayout = getNetworkLayout(momDict[0])
        except FunctionTimedOut:
            print('Timeout mom#2')
    except KeyError:
        try:
            momLayout = getNetworkLayout(momDict[0])
        except FunctionTimedOut:
            print('Timeout mom#2')
    try:
        dadLayout = getNetworkLayout(dadDict)
    except FunctionTimedOut:
        print('Timeout dad')
    except TypeError:
        try:
            dadLayout = getNetworkLayout(dadDict[0])
        except FunctionTimedOut:
            print('Timeout dad#2')
    except KeyError:
        try:
            dadLayout = getNetworkLayout(dadDict[0])
        except FunctionTimedOut:
            print('Timeout dad#2')
    global cxTried
    cxTried = cxTried + 2
    try:
        newTest = testSuiteGen.test_from_network(momLayout)
        final_path = c.rg.get_final_path()
        port = getPort()
        runner = TestRunner(newTest, "levels/asfault", 'localhost', port, False)
        try:
            execution = func_timeout(90, runner.run)
            export_test_exec(final_path, final_path, newTest)
            with open(final_path + '/test_0001.json') as f:
                ind1 = json.load(f)
            oobList = getOobTuples(ind1)
            print('Oob List: ', oobList)
            if oobList:
                port = port + 1
                newTest = getOob(oobList, newTest, port)
                export_test_exec(final_path, final_path, newTest)
                with open(final_path + '/test_0001.json') as f:
                    ind1 = json.load(f)
        except FunctionTimedOut:
            runner.kill_beamng()
            sleep(10)
            ind1 = None
    except Exception as e:
        ind1 = None
    try:
        newTest = testSuiteGen.test_from_network(dadLayout)
        final_path = c.rg.get_final_path()
        port = getPort()
        runner = TestRunner(newTest, "levels/asfault", 'localhost', port, False)
        try:
            execution = func_timeout(90, runner.run)
            export_test_exec(final_path, final_path, newTest)
            with open(final_path + '/test_0001.json') as f:
                ind2 = json.load(f)
            oobList = getOobTuples(ind2)
            print('Oob List: ', oobList)
            if oobList:
                port = port + 1
                newTest = getOob(oobList, newTest, port)
                export_test_exec(final_path, final_path, newTest)
                with open(final_path + '/test_0001.json') as f:
                    ind2 = json.load(f)
        except FunctionTimedOut:
            runner.kill_beamng()
            sleep(10)
            ind2 = None
    except Exception as e:
        ind2 = None
    return ind1, ind2


# function to transfer a road into a individual for the evolution
def transformIntoIndividual():
    global offspringCount
    global offspring
    child = offspring[offspringCount]
    offspringCount = offspringCount + 1
    try:
        return child[0]
    except Exception:
        return child


def getTestsFromJson(pathToDirectory):
    resList = []
    for file in os.listdir(pathToDirectory):
        if file.endswith(".json"):
            print(os.path.join(pathToDirectory, file))
            with open(os.path.join(pathToDirectory, file), 'r') as f:
                data = json.load(f)
                #print(data)
                #test = RoadTest.from_dict(data)
                resList.append(data)
    return resList

# setup of the deap tools for the evolutionary algorithm
creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

# Creates the first individuals
toolbox.register("getInd", getRandomTrack)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.getInd, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Transform the generated roads into individuals
toolbox.register('getChild', transformIntoIndividual)
toolbox.register('child', tools.initRepeat, creator.Individual, toolbox.getChild, n=1)
toolbox.register("offspring", tools.initRepeat, list, toolbox.child)

# Evolution Operations
toolbox.register("evaluate", evalTest)
toolbox.register("select", tools.selNSGA2)
toolbox.register("mutate", mutator)
toolbox.register("mate", crossParents)



def main(seed=None):
    archieveList = getTestsFromJson(finalPath)

    random.seed(seed)
    global outputCounts
    logbook = tools.Logbook()

    global offspring

    offspring = toolbox.clone(archieveList)

    pop = toolbox.offspring(n=(len(offspring)))

    # calculate the speed and curve profiles for the initial population
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
        print(ind.fitness.values)

    # set the timer
    t_end = time.time() + 60 * computationTime

    # ordering the population and calculating the distance of the initial population
    pop = toolbox.select(pop, len(pop))
    maxDistance = getDistance(pop)
    print(maxDistance)

    count = 0

    # Clone the selected individuals
    off = [toolbox.clone(ind) for ind in pop]

    t_start = time.time()

    global t_int
    global intervall

    # loop for generating new individuals
    while time.time() < t_end:
        count = count + 1

        global offspringCount
        offspringCount = 0
        # generating a new test
        try:
            newInd = toolbox.individual()
        except:
            newInd = toolbox.individual()

        global newRoads
        newRoads = newRoads + 1

        listCount = 0

        helpOff = [toolbox.clone(ind) for ind in off]

        # compare every possibilities of the offspring distance to population distance
        while listCount < len(off):
            helpList = [toolbox.clone(ind) for ind in off]
            newOff = getNewList(helpList, newInd, listCount)

            invalid_ind = [ind for ind in newOff if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                print('New Value: ', ind.fitness.values)

            newOff = toolbox.select(newOff, len(newOff))
            newDistance = getDistance(newOff)
            if newDistance > maxDistance:
                maxDistance = newDistance
                helpOff = [toolbox.clone(ind) for ind in newOff]
            listCount = listCount + 1

        off = [toolbox.clone(ind) for ind in helpOff]

        operatedOff = [toolbox.clone(ind) for ind in off]

        # Creating a list for the functional mated roads
        childrenList = []

        random.shuffle(operatedOff)
        for child1, child2 in zip(operatedOff[::2], operatedOff[1::2]):
            mutatedChild1 = toolbox.mutate(pop, child1, mutationProbability)
            mutatedChild2 = toolbox.mutate(pop, child2, mutationProbability)
            global mutAccomplished
            global cxAccomplished
            if mutatedChild1 is not None:
                childrenList.append(mutatedChild1)
                mutAccomplished = mutAccomplished + 1
                print('mutated')
            if mutatedChild2 is not None:
                childrenList.append(mutatedChild2)
                mutAccomplished = mutAccomplished + 1
                print('mutated')
            child1, child2 = toolbox.mate(child1, child2)
            if child1 is not None:
                childrenList.append(child1)
                cxAccomplished = cxAccomplished + 1
                print('crossover child1')
            if child2 is not None:
                childrenList.append(child2)
                cxAccomplished = cxAccomplished + 1
                print('crossover child2')

        # transfer newly created roads into individual

        offspring = toolbox.clone(childrenList)
        print(len(childrenList))
        children = toolbox.offspring(n=(len(offspring)))

        # Evaluate the individuals
        invalid_ind = [ind for ind in children if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            print(ind.fitness.values)

        for child in children:
            helpOff = [toolbox.clone(ind) for ind in off]

            # compare every possibilities of the offspring distance to population distance
            while listCount < len(off):
                helpList = [toolbox.clone(ind) for ind in off]
                newOff = getNewList(helpList, child, listCount)

                invalid_ind = [ind for ind in newOff if not ind.fitness.valid]
                fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit
                    print('New Value: ', ind.fitness.values)

                newOff = toolbox.select(newOff, len(newOff))
                newDistance = getDistance(newOff)
                if newDistance > maxDistance:
                    maxDistance = newDistance
                    helpOff = [toolbox.clone(ind) for ind in newOff]
                listCount = listCount + 1

            off = [toolbox.clone(ind) for ind in helpOff]

        for ind in off:
            print('Generation ', count, ': ', ind.fitness.values)
        print(getDistance(off))

        details = ['New Roads generated:', newRoads, 'Distance', getDistance(off), "Time:", time.time() - t_start]
        if t_int < time.time():
            createResultsWithDetails('Novelty', outputCounts, pop, details)
            t_int = t_int + 60 * intervall
            outputCounts = outputCounts + 1

    pop = [toolbox.clone(ind) for ind in off]
    for ind in pop:
        print(ind.fitness.values)
    details = ['New Roads generated:', newRoads, 'Distance', getDistance(off), "Time:", time.time() - t_start]
    createResultsWithDetails('Novelty', outputCounts, pop, details)
    print('Outcome: ', getDistance(pop))
    return pop, logbook


if __name__ == "__main__":
    # with open("pareto_front/zdt1_front.json") as optimal_front_data:
    #     optimal_front = json.load(optimal_front_data)
    # Use 500 of the 1000 points in the json file
    # optimal_front = sorted(optimal_front[i] for i in range(0, len(optimal_front), 2))

    pop, stats = main()
    # pop.sort(key=lambda x: x.fitness.values)

    # print(stats)
    # print("Convergence: ", convergence(pop, optimal_front))
    # print("Diversity: ", diversity(pop, optimal_front[0], optimal_front[-1]))

    # import matplotlib.pyplot as plt
    # import numpy

    # front = numpy.array([ind.fitness.values for ind in pop])
    # optimal_front = numpy.array(optimal_front)
    # plt.scatter(optimal_front[:,0], optimal_front[:,1], c="r")
    # plt.scatter(front[:,0], front[:,1], c="b")
    # plt.axis("tight")
    # plt.show()

