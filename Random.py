# This script creates a random test suite

from deap import base
from deap import creator
from deap import tools
from profileValues import *

# size of the test suite
size = 10


# evaluates the speed and curve profile of a test
def evalTest(individual):
    i = iter(individual)
    try:
        values = getProfileValues(individual[0])
    except TypeError:
        values = evalTest(individual[0])
    return values


# setup of the deap tools for the evolutionary algorithm
creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

# Creates the first individuals
toolbox.register("getInd", getRandomTrack)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.getInd, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Evolution Operations
toolbox.register("evaluate", evalTest)


def main(seed=None):
    random.seed(seed)

    logbook = tools.Logbook()
    try:
        pop = toolbox.population(n=size)
    except:
        pop = toolbox.population(n=size)

    # calculate the speed and curve profiles for the initial population
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
        print(ind.fitness.values)
    details = []
    createResultsWithDetails('Random', pop, details)

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