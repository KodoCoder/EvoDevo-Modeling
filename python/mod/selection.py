
# ### Code ###
import random
from operator import itemgetter

from prepare import add_noise


def select_next_generation(population_list, fitness_list, mutation_rate=0):
    """Returns a list of gene-codes the size of the population_list,
        based on the fitness scores provided

    """
    assert len(population_list) == len(fitness_list)
    new_population = [''] * len(population_list)
    selection_spots = int(round(len(population_list * .5)))
    selected = []
    fitness_list = [c for c in enumerate(fitness_list)]
    for i in xrange(selection_spots):
        agent = max(fitness_list, key=itemgetter(1))
        selected.append(agent)
        fitness_list.remove(agent)
    first_quarter = int(round(selection_spots * .05))
    second_quarter = int(round(selection_spots * .15))
    third_quarter = int(round(selection_spots * .3))
    for i in xrange(selection_spots):
        if(i < first_quarter):
            new_population[i] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 1] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 2] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 3] = add_noise(selected[i][1], mutation_rate)
        elif(i >= first_quarter and i < second_quarter):
            new_population[i] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 1] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 2] = add_noise(selected[i][1], mutation_rate)
        elif(i >= second_quarter and i < third_quarter):
            new_population[i] = add_noise(selected[i][1], mutation_rate)
            new_population[i + 1] = add_noise(selected[i][1], mutation_rate)
        elif(i >= third_quarter):
            new_population[i] = add_noise(selected[i][1], mutation_rate)
    return new_population
