
# ### Code ###
import random
from operator import itemgetter

from prepare import add_noise

REPRODUCTION_ERROR_RATE = .005


def select_next_generation(current_population, fitness_list,
                           error_rate=REPRODUCTION_ERROR_RATE):
    """Returns a list of gene-codes the size of the current_population,
        based on the fitness scores provided

    """
    new_population = list()
    population_size = len(current_population)
    first_quarter = int(round(population_size * .2))
    second_quarter = int(round(population_size * .5))
    third_quarter = int(round(population_size * .8))
    fourth_quarter = population_size
    fitness_list = [c for c in enumerate(fitness_list)]
    selected = list()
    for i in xrange(first_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(4):
            selected.append(agent)
        fitness_list.remove(agent)
    for i in xrange(first_quarter, second_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(3):
            selected.append(agent)
        fitness_list.remove(agent)
    for i in xrange(second_quarter, third_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(2):
            selected.append(agent)
        fitness_list.remove(agent)
    for i in xrange(third_quarter, fourth_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        selected.append(agent)
        fitness_list.remove(agent)
    for agent in selected:
        new_population.append(add_noise(current_population[agent[0]],
                                        error_rate))
    return new_population
