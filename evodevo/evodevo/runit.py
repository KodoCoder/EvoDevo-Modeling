"""runit --- a module that integrates the other code into an
experimental run with data collection.
"""

import os
import random
import pprint as pp
# import sqlite3

# from collections import namedtuple
import timeout

import part
import initiate
import develop
import blueprint
import export
import simulate
import selection


# DataFromRun = namedtuple('DataFromRun', ['fitness', 'original_genome',
#                                          'built_genome'])

def make_data_file(dat_dir='../data/pop_1/', data_file='run_0.csv'):
    the_file = dat_dir + data_file
    count = 1
    while (os.path.isfile(the_file)):
        index = the_file.find('.csv')
        if (count <= 10):
            the_file = the_file[:index-1] + str(count) + the_file[index:]
        elif (count > 10 and count <= 100):
            the_file = the_file[:index-2] + str(count) + the_file[index:]
        elif (count > 100 and count <= 1000):
            the_file = the_file[:index-3] + str(count) + the_file[index:]
        count += 1
        # print data_file, count
    return the_file


def abort_run(genome, genome_to_build):
    failed_run = [0, genome, genome_to_build]
    return failed_run


@timeout.timeout(5)
def run_one(genome, build_er):
    proto_parts, genome_to_build = initiate.setup_agent(genome, build_er)
    parts_developed = develop.update_cycles(proto_parts)
    frame_selection = develop.select_frame_parts(parts_developed)
    if any([i == [] for i in frame_selection]):
        return abort_run(genome, genome_to_build)
    ann_selection = develop.select_ann_parts(parts_developed, frame_selection)
    if any([i == [] for i in ann_selection]):
        return abort_run(genome, genome_to_build)
    blueprints = blueprint.all_parts_to_send(parts_developed, frame_selection,
                                             ann_selection)
    export.export_all(*blueprints)
    return [simulate.run_simulation(), genome, genome_to_build]


def run_generations(reproduction_error_rate, build_error_rate,
                    run_genomes, generations=100):
    # data_file = make_sql_table()
    data_file = make_data_file()
    with open(data_file, 'w') as df:
        df.write('agent,generation,reproduction_error_rate,build_error_rate,'
                 'fitness,original_genome_1,original_genome_2,'
                 'built_genome_1,built_genome_2\n')
    for generation in xrange(generations):
        selection_genomes, fitnesses = list(), list()
        for agent in xrange(len(run_genomes)):
            genome = run_genomes[agent]
            setup_data = [agent, generation, reproduction_error_rate,
                          build_error_rate]
            try:
                run_data = run_one(genome, build_error_rate)
                data_row = setup_data + [run_data[0], run_data[1][:9000],
                                         run_data[1][9000:],
                                         run_data[2][:9000],
                                         run_data[2][9000:]]
            except timeout.TimeoutError:
                run_data = [0, genome, 'Timeout']
                data_row = setup_data + [run_data[0], run_data[1][:9000],
                                         run_data[1][9000:],
                                         run_data[2], run_data[2]]
                print 'Timeout!'
            selection_genomes.append(genome)
            fitnesses.append(data_row[4])
            with open(data_file, 'a') as df:
                df.write('{},{},{},{},{},{},{},{},{}\n'.format(*data_row))
            # sql_output(data_list, data_file)
            del(setup_data)
            del(run_data)
            del(data_row)
        run_genomes = selection.next_generation(selection_genomes,
                                                fitnesses,
                                                reproduction_error_rate)
        print 'Done with Gen: ' + str(generation)


if __name__ == '__main__':
    population = list()
    for a in xrange(60):
        population.append(initiate.generate_genome(18000))
    for i in xrange(0, 30, 5):
        rep_er = i / 100.
        for j in xrange(0, 30, 5):
            build_er = j / 100.
            random.seed(42)
            run_generations(rep_er, build_er, population)
            print 'Done with BE: ' + str(build_er)
        print 'Done with RE: ' + str(rep_er)
