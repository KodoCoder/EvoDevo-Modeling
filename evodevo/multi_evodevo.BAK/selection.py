"""select ---

"""
import random
from operator import itemgetter

from initiate import add_noise


def next_generation(current_population, fitness_list, error_rate):
    """Returns a list of gene-codes the size of the current_population,
        based on the fitness scores provided

    """
    new_population = list()
    population_size = len(current_population)
    first_quarter = int(round(population_size * .05))
    second_quarter = int(round(population_size * .15))
    third_quarter = int(round(population_size * .3))
    fourth_quarter = int(round(population_size * .5))
    fitness_list = [c for c in enumerate(fitness_list)]
    selected_index = list()
    for i in xrange(first_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(4):
            selected_index.append(agent[0])
        fitness_list.remove(agent)
    for i in xrange(first_quarter, second_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(3):
            selected_index.append(agent[0])
        fitness_list.remove(agent)
    for i in xrange(second_quarter, third_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        for i in xrange(2):
            selected_index.append(agent[0])
        fitness_list.remove(agent)
    for i in xrange(third_quarter, fourth_quarter):
        agent = max(fitness_list, key=itemgetter(1))
        selected_index.append(agent[0])
        fitness_list.remove(agent)
    for index in selected_index:
        new_population.append(add_noise(current_population[index], error_rate))
    return new_population
