"""runit --- a module that integrates the other code into an
experimental run with data collection.
"""

import os
import pprint as pp

from collections import namedtuple

import part
import initiate
import develop
import blueprint
import export
import simulate
import selection


DataFromRun = namedtuple('DataFromRun', ['fitness', 'original_genome_1',
                                         'original_genome_2', 'built_genome_1',
                                         'build_genome_2'])


def abort_run(genome, genome_to_build):
    halfer = int(len(genome) * .5)
    failed_run = DataFromRun(0, genome[:halfer], genome[halfer:],
                             genome_to_build[:halfer],
                             genome_to_build[halfer:])
    return failed_run


def run_one(genome):
    proto_parts, genome_to_build = initiate.setup_agent(genome)
    parts_developed = develop.update_cycles(proto_parts)
    frame_selection = develop.select_frame_parts(parts_developed)
    if any([i == [] for i in frame_selection]):
        return abort_run(genome, genome_to_build)
    ann_selection = develop.select_ann_parts(parts_developed, frame_selection)
    if any([i == [] for i in ann_selection]):
        halfer = int(len(genome) * .5)
        return abort_run(genome, genome_to_build)
    blueprints = blueprint.all_parts_to_send(parts_developed, frame_selection,
                                             ann_selection)
    export.export_all(*blueprints)
    return simulate.run_simulation(genome, genome_to_build)


def run_multiple(population, generations):
    genomes = initiate.generate_genomes(population, 18000)
    for generation in xrange(generations):
        data_from_run = list()
        for genome in genomes:
            data_from_run.append(DataFromRun(*run_one(genome)))
        # print "Gen Done!"
        genomes = selection.next_generation(genomes, [i.fitness for i
                                                      in data_from_run])
