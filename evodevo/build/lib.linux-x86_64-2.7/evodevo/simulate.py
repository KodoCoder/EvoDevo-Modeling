
# ###Code###
import os
import time
from collections import namedtuple

SimulationData = namedtuple('SimulationData', ['fitness'])
OutputRow = namedtuple('OutputRow', ['fitness', 'original_genome_1',
                                     'original_genome_2', 'built_genome_1',
                                     'built_genome_2'])


def grab_data(data_file):
    """Returns a list of data that was generated by the simulation

    """
    with open(data_file, 'r') as fr:
        return SimulationData([line.strip('\n') for line in fr])


def run_simulation(agent, agent_to_build):
    """Returns fitness after running the simulation.

    """
    app_file = '../c++/app'
    data_file = '../io/simulation_data.dat'
    check_file = '../io/buffer.dat'
    while not os.path.isfile(check_file):
        time.sleep(0.1)
    os.system(app_file)
    while not os.path.isfile(data_file):
        time.sleep(0.1)
    simulation_data = grab_data(data_file)
    os.remove(check_file)
    os.remove(data_file)
    halfer = int(len(agent) * .5)
    agent_1, agent_2 = agent[:halfer], agent[halfer:]
    built_agent_1, built_agent_2 = agent_to_build[:halfer], agent_to_build[halfer:]
    output = OutputRow(fitness = simulation_data.fitness,
                       original_genome_1=agent_1,
                       original_genome_2=agent_2,
                       built_genome_1=built_agent_1,
                       built_genome_2=built_agent_2)
    return output
