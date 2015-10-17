
# ### Code ###
import os
import pprint as pp
from collections import namedtuple

import generate
import part
import prepare
import update
import blueprint_select
import blueprint_make
import blueprint_send
import simulate
import selection


DataFromRun = namedtuple('DataFromRun', ['fitness', 'original_genome_1',
                                         'original_genome_2', 'built_genome_1',
                                         'build_genome_2'])


def abort_run(agent, agent_to_build):
    halfer = int(len(agent) * .5)
    failed_run = DataFromRun(0, agent[:halfer], agent[halfer:],
                                 agent_to_build[:halfer], 
                                 agent_to_build[halfer:])
    return failed_run


def run_one(agent):
    dev_parts, agent_to_build = prepare.setup_agent(agent)
    built_parts = update.update_cycles(dev_parts)
    frame_selection = blueprint_select.get_frame_parts(built_parts)
    if any([i == [] for i in frame_selection]):
        # pp.pprint("Agent Aborted: Bad Frame")
        # pp.pprint(frame_selection)
        return abort_run(agent, agent_to_build)
    neuron_parts, sensor_parts, wire_parts = blueprint_select.get_ann_parts(built_parts,
                                                                            frame_selection)
    if any([i == [] for i in [neuron_parts, sensor_parts, wire_parts]]):
        halfer = int(len(agent) * .5)
        failed_run = DataFromRun(0, agent[:halfer], agent[halfer:],
                                 agent_to_build[:halfer], 
                                 agent_to_build[halfer:])
        # pp.pprint("Agent Aborted: Bad ANN")
        # pp.pprint([neuron_parts, sensor_parts, wire_parts])
        return abort_run(agent, agent_to_build)
    sent_bodys, sent_joints, rotated_bodys = blueprint_make.setup_frame_to_send(built_parts,
                                                                                frame_selection)
    sent_sensors = blueprint_make.setup_sensors_to_send(sensor_parts, 
                                                        rotated_bodys)
    sent_ann = blueprint_make.setup_ann_to_send(built_parts, wire_parts, 
                                                len(frame_selection[1]),
                                                len(neuron_parts), 
                                                len(sensor_parts))
    # pp.pprint([sent_bodys, sent_joints, sent_sensors, sent_ann])  
    blueprint_send.export_all(sent_bodys, sent_joints, sent_sensors, *sent_ann)
    return simulate.run_simulation(agent, agent_to_build)


def run_multiple(population, generations):
    genomes = generate.generate(population, 18000)
    for generation in xrange(generations):
        data_from_run = list()
        for agent in genomes:
            data_from_run.append(DataFromRun(*run_one(agent)))
        # print "Gen Done!"
        genomes = selection.select_next_generation(genomes, 
                                                   [i.fitness for i 
                                                    in data_from_run])
