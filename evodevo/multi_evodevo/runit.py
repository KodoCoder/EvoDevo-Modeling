"""runit --- a module that integrates the other code into an
experimental run with data collection.
"""

import os
import pprint as pp
from numpy.random import RandomState
import multiprocess as mp
from mpi4py import MPI
from functools import partial
import sqlite3
from pprint import pprint
import pickle

# import pickle
import pdb
# import pandas as pd
# from pathos.multiprocessing import ProcessingPool as Pool
# import sqlite3
# import timeout

import part
import initiate
import develop
import blueprint
import export
import simulate
import selection

# DataFromRun = namedtuple('DataFromRun', ['fitness', 'original_genome',
#                                          'built_genome'])


def make_io_file(pop, repro_cond, build_cond, io_dir='../io/'):
    mod_repro_cond = int(repro_cond * 10000)
    mod_build_cond = int(build_cond * 10000)
    cond_str = 'pop{}r{:04}b{:04}'.format(pop,
                                          mod_repro_cond,
                                          mod_build_cond)
    io_file = ''.join((io_dir, cond_str))
    if not os.path.isdir(io_file):
        os.makedirs(io_file)
    return io_file


POP_DB = '../data/population_genes.db'


# Making a set of populations
def make_population_db(db=POP_DB, num=10):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for i in range(num):
        tab = ''.join(('pop', str(i)))
        s = 'CREATE TABLE {} (id INT PRIMARY KEY, genome TEXT)'.format(tab)
        c.execute(s)
    conn.commit()
    conn.close()


def fill_population_table(tab, db=POP_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    pop = list()
    prng = RandomState(24)
    for i in xrange(60):
        genome = initiate.generate_genome(18000, prng)
        pop.append((i, genome))
    s = 'INSERT into pop{} VALUES (?, ?)'.format(tab)
    c.executemany(s, pop)
    conn.commit()
    conn.close()


def make_filled_db(db=POP_DB, num=10):
    make_population_db(db, num)
    for i in xrange(num):
        fill_population_table(i, db)


# Create and manage simulation data
def make_sql_db(population, reproduction_cond,
                building_cond, generations):
    mod_repro_cond = int(reproduction_cond * 10000)
    mod_build_cond = int(building_cond * 10000)
    the_file = '../data/pop{}r{:04}b{:04}.db'.format(population,
                                                     mod_repro_cond,
                                                     mod_build_cond)
    while (os.path.isfile(the_file)):
        # print the_file
        index = the_file.find('.db')
        if the_file[index-1] == ')':
            if the_file[index-3:index-1] == '10':
                raise ValueError
            count = int(the_file[index-2]) + 1
            insert = ''.join((' (', str(count), ')'))
            the_file = ''.join((the_file[:index-4], insert, '.db'))
        else:
            the_file = ''.join((the_file[:index], ' (1).db'))
    # print the_file
    conn = sqlite3.connect(the_file)
    c = conn.cursor()
    for i in xrange(generations):
        s = '''CREATE TABLE gen{} (sim_num INT PRIMARY KEY,
        parent INT, fitness REAL, reproduction_error_rate REAL,
        buidling_error_rate REAL, germline_genes TEXT,
        somaline_genes TEXT)'''.format(i)
        c.execute(s)
    conn.commit()
    conn.close()
    return the_file


def write_to_sql_table(db, generation, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    s = '''INSERT INTO gen{} VALUES (?, ?, ?, ?, ?, ?, ?)'''.format(generation)
    c.execute(s, data)
    conn.commit()
    conn.close()


def grab_sim_selection_data(db, gen):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    s = 'SELECT sim_num, fitness, germline_genes FROM gen{}'.format(gen)
    c.execute(s)
    data = sorted(c.fetchall(),
                  key=lambda dat: dat[1])
    conn.close()
    fitness = [data[i][1] for i in range(len(data))]
    genomes = [(data[i][0], data[i][2]) for i in range(len(data))]
    while fitness[-1] == u'-nan':
        print fitness
        fitness.pop()
        fitness.insert(0, 0)
        print fitness
        genomes.insert(0, genomes.pop())
    return [fitness, genomes]


def grab_pop_genome(tab, agent, db=POP_DB):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    t = (agent,)
    s = 'SELECT genome FROM pop{} WHERE id=?'.format(tab)
    c.execute(s, t)
    genome = c.fetchone()
    conn.close()
    return genome[0]


# For examining various aspects of the data
def grab_a_genome(db, gen, agent, u=False):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    s = 'SELECT fitness, germline_genes, somaline_genes FROM gen{}'.format(gen)
    c.execute(s)
    data = sorted(c.fetchall(),
                  key=lambda row: row[0])
    conn.close()
    if u:
        fitness = [data[i][0] for i in range(len(data))]
        germ_g = [data[i][1] for i in range(len(data))]
        soma_g = [data[i][2] for i in range(len(data))]
        while fitness[-1] == u'-nan':
            fitness.pop()
            fitness.insert(0, 0)
            germ_g.insert(0, germ_g.pop())
            soma_g.insert(0, soma_g.pop())
        return [germ_g, soma_g]
    return data[agent][1:]


def grab_all_genomes(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sl = list()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for i in range(len(c.fetchall())):
        sl.append('SELECT germline_genes, somaline_genes from gen{}'.format(i))
    genomes = list()
    for i in sl:
        c.execute(i)
        gen_genomes = c.fetchall()
        # gen_genomes = [gen_genomes[i][0] for i in len(gen_genomes)]
        genomes.append(gen_genomes)
    conn.close()
    return genomes


def compare_data(db1, db2, gen):
    conn = sqlite3.connect(db1)
    c = conn.cursor()
    s = 'SELECT sim_num, fitness, germline_genes, somaline_genes FROM gen{}'.format(gen)
    c.execute(s)
    data1 = sorted(c.fetchall(),
                   key=lambda pair: pair[0])
    conn.close()
    conn = sqlite3.connect(db2)
    c = conn.cursor()
    s = 'SELECT sim_num, fitness, germline_genes, somaline_genes FROM gen{}'.format(gen)
    c.execute(s)
    data2 = sorted(c.fetchall(),
                   key=lambda pair: pair[0])
    conn.close()
    # return [fitnesses, genomes]
    diff = list()
    for i in range(len(data1)):
        diff.append([data1[i][j] == data2[i][j] for j in range(1, 4)])
    for num, check in enumerate(diff):
        if all(check):
            print data1[num][0], check
        else:
            print data1[num][0], check, data1[num][1], data2[num][1]


# Run and view one agent
def test_one_agent(pop, gen, build_er, repro_er, version, agent):
    db = '../data/pop{}r{:04}b{:04}.db'.format(pop,
                                               int(repro_er * 10000),
                                               int(build_er * 10000))
    if version != 0:
        index = db.find('.db')
        insert = ''.join((' (', str(version), ')'))
        db = ''.join((db[:index], insert, db[index:]))
    print db
    io_file = ''.join((make_io_file(pop, repro_er, build_er), '/'))
    genome, genome_to_build = grab_a_genome(db, gen, agent)
    filler_prng = RandomState(2)
    da_state = filler_prng.get_state()
    proto_parts, genome_to_build = initiate.setup_agent(genome_to_build,
                                                        0,
                                                        filler_prng)
    parts_developed = develop.update_cycles(proto_parts)
    frame_selection = develop.select_frame_parts(parts_developed)
    abort_data = (agent,
                  0,  # PARENT_HOLDER
                  0,  # fit = 0 when aborted
                  repro_er,
                  build_er,
                  genome,
                  genome_to_build)
    if any([i == [] for i in frame_selection]):
        return abort_data
    ann_selection = develop.select_ann_parts(parts_developed, frame_selection)
    if any([i == [] for i in ann_selection]):
        return abort_data
    blueprints = blueprint.all_parts_to_send(parts_developed, frame_selection,
                                             ann_selection)
    pprint(blueprints)
    export.export_all(blueprints[0], blueprints[1], blueprints[2],
                      blueprints[3], blueprints[4], blueprints[5],
                      blueprints[6], agent, io_file)
    fitness = simulate.run_simulation(io_file, agent, True)
    data = (agent,
            0,  # PARENT_HOLDER
            fitness,
            repro_er,
            build_er,
            genome,
            genome_to_build)
    return da_state


def run_test(rer, ber, pop_num, gens):
    # run_generations(rer. ber, pop_num, gens)
    # run_generations(rer. ber, pop_num, gens)
    cond = 'pop{}r{:04}b{:04}'.format(pop_num,
                                      int(rer * 10000),
                                      int(ber * 10000))
    og = '../io/' + cond + '/'
    cp = '../io/copies/'
    check_data(og, cp)
    og = './check_1/'
    cp = './check_2/'
    check_data(og, cp)
    db1 = ''.join(('../data/', cond, '.db'))
    db2 = ''.join(('../data/', cond, ' (1).db'))
    compare_data(db1, db2, 0)


def grab_data(data_file):
    with open(data_file, 'r') as fr:
        lines = [line.strip('\n') for line in fr]
    return lines


def write_data(data_file, data, part=False):
    with open(data_file, 'w+') as fw:
        for line in data:
            if not part:
                fw.write(str(line))
                fw.write('\n')
            else:
                fw.write(str(line.characteristics))
                fw.write('\n')


def check_data(og, cp):
    dbs_with_errors = list()
    for dirname, dirs, files in os.walk(og):
        for filename in files:
            og_file = os.path.join(dirname, filename)
            # print og_file,
            og_data = grab_data(og_file)
            found = False
            for dirname2, dirs2, files2 in os.walk(cp):
                for filename2 in files2:
                    if filename == filename2:
                        found = True
                        cp_file = os.path.join(dirname2, filename2)
                        # print cp_file
                        cp_data = grab_data(cp_file)
                        # pprint(cp_data)
                        if cp_data != og_data:
                            print "ERROR with ", og_file
                            # pprint([og_data, cp_data])
                            dbs_with_errors.append(og_file[-14:-4])
            if not found:
                print "Could not find other ", og_file
    dbs_with_errors = sorted(set(dbs_with_errors))
    print len(dbs_with_errors), dbs_with_errors


# Single simulation. Will be multiprocessed
def run_one(sim_num, seeds, all_genomes, gen, build_er, repro_er, io_file, db):
    agent_prng = RandomState(seeds[sim_num])
    genome_info = all_genomes[sim_num]
    parent = genome_info[0]
    genome = genome_info[1]
    proto_parts, genome_to_build = initiate.setup_agent(genome,
                                                        build_er,
                                                        agent_prng)
    parts_developed = develop.update_cycles(proto_parts)
    frame_selection = develop.select_frame_parts(parts_developed)
    # write_data('./check_2/pd_info_'+str(sim_num)+'.dat', parts_developed, True)
    # write_data('./check_2/fs_info_'+str(sim_num)+'.dat', frame_selection)
    abort_data = (sim_num,
                  parent,
                  0,  # fit = 0 when aborted
                  repro_er,
                  build_er,
                  genome,
                  genome_to_build)
    if any([i == [] for i in frame_selection]):
        return write_to_sql_table(db, gen, abort_data)
    ann_selection = develop.select_ann_parts(parts_developed,
                                             frame_selection)
    if any([i == [] for i in ann_selection]):
        return write_to_sql_table(db, gen, abort_data)
    # write_data('./check_2/as_info_'+str(sim_num)+'.dat', ann_selection)
    blueprints = blueprint.all_parts_to_send(parts_developed,
                                             frame_selection,
                                             ann_selection)
    # write_data('./check_2/bp_info_'+str(sim_num)+'.dat', blueprints)
    export.export_all(blueprints[0], blueprints[1], blueprints[2],
                      blueprints[3], blueprints[4], blueprints[5],
                      blueprints[6], sim_num, io_file)
    # export.export_all(blueprints[0], blueprints[1], blueprints[2],
    #                   blueprints[3], blueprints[4], blueprints[5],
    #                   blueprints[6], sim_num, '../io/copies/')
    fitness = simulate.run_simulation(io_file, sim_num)
    # if fitness > 1000 or fitness != fitness or len(blueprints[0]) > 8:
    #     print sim_num, fitness
    #     for bp in blueprints:
    #         print len(bp),
    #     print
    data = (sim_num,
            parent,
            fitness,
            repro_er,
            build_er,
            genome,
            genome_to_build)
    return write_to_sql_table(db, gen, data)


def run_generations(reproduction_error_rate, build_error_rate,
                    pop_num, generations=100, agents=60):
    main_prng = RandomState(42)

    db_name = make_sql_db(pop_num,
                          reproduction_error_rate,
                          build_error_rate,
                          generations)
    io_file = ''.join((make_io_file(pop_num,
                                    reproduction_error_rate,
                                    build_error_rate),
                       '/'))
    initial_genomes = list()
    for i in xrange(agents):
        initial_genomes.append((i,
                                grab_pop_genome(pop_num,
                                                i)))
    for generation in xrange(generations):
        # print 'Gen:', generation, 'Genomes:', len(initial_genomes)
        # print 'Length of genomes:'
        # for i in initial_genomes:
        #     if len(i[1]) < 10:
        #         # pdb.set_trace()
        #         print
        #         print i[1]
        #     else:
        #         print len(i[1]),
        # print; print
        agent_prng_seeds = main_prng.randint(0, 1000000, agents+1)
        setup_data = [generation, reproduction_error_rate, build_error_rate]
        wrap_run_one = partial(run_one,
                               seeds=agent_prng_seeds,
                               all_genomes=initial_genomes,
                               gen=generation,
                               build_er=build_error_rate,
                               repro_er=reproduction_error_rate,
                               db=db_name,
                               io_file=io_file)
        sim_pool = mp.Pool(mp.cpu_count())
        sim_pool.map(wrap_run_one, xrange(agents))
        sim_pool.close()
        sim_pool.join()
        fit_data, selection_genomes = grab_sim_selection_data(db_name,
                                                              generation)
        # print fit_data
        # print ('Fits:', len(fit_data), 'Selection Genomes:',
        #        len(selection_genomes))
        # print 'Length of selection genomes:'
        # for i in selection_genomes:
        #     if len(i[1]) < 10:
        #         # pdb.set_trace()
        #         print
        #         print len(i[1]), i[1]
        #     else:
        #         print len(i[1]),
        # print; print
        initial_genomes = selection.next_generation(selection_genomes,
                                                    fit_data,
                                                    reproduction_error_rate,
                                                    agent_prng_seeds[-1])
        # print 'Length of Selected Genomes:'
        # for i in initial_genomes:
        #     if len(i[1]) < 10:
        #         # pdb.set_trace()
        #         print
        #         print len(i[1]), i[1]
        #     else:
        #         print len(i[1]),
        # print; print
        del(selection_genomes)
        del(fit_data)
        # print "Done with generation", generation


# if __name__ == '__main__':
#     run_generations(.0025, .0025, 0)


# Script to run 1 population through all conditions, serially
if __name__ == '__main__':
    pop_num = int(raw_input("What population should be run? "))
    gen_num = int(raw_input("How many generations should be run? "))
    for rep_er_cond in xrange(5, 51, 5):
        rep_er = rep_er_cond / 10000.
        for build_er_cond in xrange(5, 51, 5):
            build_er = build_er_cond / 10000.
            print "Start condition ", [rep_er, build_er]
            run_generations(rep_er, build_er, pop_num, gen_num)


"""
# Script to run 1 population under 100 conditions at the same time
CONDITIONS = list()
for i in range(5, 51, 5):
    r = i / 10000.
    for j in range(5, 51, 5):
        b = i / 10000.
        CONDITIONS.append([r, b])

population = [0] * 60

if __name__ = '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        for i in xrange(60):
            population[i] = initiate.generate_genome(18000)
    comm.Bcast(population, root=0)
    this_pop_run = 0
    rep_er, build_er = CONDITIONS[rank]
    random.seed(42)
    run_generations(rep_er, build_er, population, this_pop_run)
"""

"""
# Script to run X populations under each condition at the same time
if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    population = list()
    for a in xrange(60):
        population.append(initiate.generate_genome(18000))
    for rep_er_cond in xrange(5, 51, 5):
        rep_er = rep_er_cond / 10000.
        for build_er_cond in xrange(5, 51, 5):
            build_er = build_er_cond / 10000.
            random.seed(42)
            run_generations(rep_er, build_er, population, rank)
"""


"""
sys.settrace(tracer)


def tracer(frame, event, arg):
    dump_stack(frame)
    return tracer


def dump_stack(frame):
    while frame is not None:
        dump_frame(frame)
        frame = frame.f_back


def dump_frame(frame):
    m_locals = frame.f_locals
    m_globals = frame.f_globals
    print m_locals, m_globals
"""
