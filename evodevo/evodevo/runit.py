"""runit --- a module that integrates the other code into an
experimental run with data collection.
"""

import os
import pprint as pp
import sqlite3

from collections import namedtuple

import part
import initiate
import develop
import blueprint
import export
import simulate
import selection


# DataFromRun = namedtuple('DataFromRun', ['fitness', 'original_genome',
#                                          'built_genome'])


def make_sql_table(dat_dir='../data/', data_file='population_0.db'):
    the_file = dat_dir + data_file
    count = 0
    while (os.path.isfile(the_file)):
        index = the_file.find('.db')
        if (count <= 10):
            the_file = the_file[:index-1] + str(count) + the_file[index:]
        elif (count > 10 and count <= 100):
            the_file = the_file[:index-2] + str(count) + the_file[index:]
        elif (count > 100 and count <= 1000):
            the_file = the_file[:index-3] + str(count) + the_file[index:]
        count += 1
    conn = sqlite3.connect(the_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE pop (id INT PRIMARY KEY, generation INT,
    reproduction_error_rate REAL, buidling_error_rate REAL, fitness
    REAL, original_genome TEXT, built_genome TEXT)''')
    conn.commit()
    conn.close()
    return the_file


def sql_output(data, data_file):
    data_tup = tuple(data)
    conn = sqlite3.connect(data_file)
    c = conn.cursor()
    c.execute('INSERT INTO pop VALUES (?, ?, ?, ?, ?, ?, ?)', data_tup)
    conn.commit()
    conn.close()


def abort_run(genome, genome_to_build):
    failed_run = [0, genome, genome_to_build]
    return failed_run


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
                    generations=200, agents=60):
    data_file = make_sql_table()
    for generation in xrange(generations):
        genomes, fitnesses = list(), list()
        for agent in xrange(agents):
            genome = initiate.generate_genome(18000)
            data_list = list([agents*generation + agent, generation,
                              reproduction_error_rate, build_error_rate] +
                             run_one(genome, build_error_rate))
            genomes.append(genome)
            fitnesses.append(data_list[4])
            sql_output(data_list, data_file)
        genomes = selection.next_generation(genomes, fitnesses,
                                            reproduction_error_rate)
