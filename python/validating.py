import numpy as np
import data_cruncher as dc
import math
import tablib
import gp_map_experiment as gpm
import gp_map_experiment_validation as gpvm
import my_table as mt
import itertools
import copy
import os
from scipy import stats


# ### GENOME GENERATION FUNCTIONS ###

def init_genomes():
    # Start by setting start and RC+100 reg_codons
    outty = []
    for i in range(64):
        outty.append('122230')
    # Set them to different types
    for i in range(len(outty)):
        if i < 12:
            outty[i] += '000'
        elif i < 24:
            outty[i] += '200'
        elif i < 36:
            outty[i] += '312'
        elif i < 48:
            outty[i] += '100'
        elif i < 60:
            outty[i] += '303'
        else:
            pass
    return outty


def fin_genomes(listy):
    assert len(listy) == 64
    for i in range(len(listy)):
        listy[i] += '222'
    return listy


def cat_keys(listy, n1, n2, dub=False):
    assert n1 <= 56
    holder = ''
    # n2 += 1
    if dub:
        for i in range(n1, n2):
            if i+4 < n2:
                holder += listy[i] + listy[i]
            else:
                holder += listy[i]
    else:
        for i in range(n1, n2):
            holder += listy[i]
    return holder


def generate_genomes():
    genomes_to_test = []
    setty = init_genomes()
    holder = ''
    tab = mt.table
    kys = tab.keys()
    kys.sort()
    assert len(setty) == 64
    # Test Case 1
    for i in range(len(setty)):
        setty[i] += kys[i]
    setty = fin_genomes(setty)
    for i in setty:
        holder += i
    genomes_to_test.append(holder)
    holder = ''
    # Test Case 2
    setty = init_genomes()
    for i in range(len(setty)):
        setty[i] = setty[i][:3] + kys[i] + setty[i][3:]
    setty = fin_genomes(setty)
    for i in setty:
        holder += i
    genomes_to_test.append(holder)
    holder = ''
    # Test Case 3
    setty = init_genomes()
    count = 0
    for i in range(len(setty)):
        if count >= 64:
            count = 0
        setty[i] += cat_keys(kys, count, count+8)
        count += 8
    setty = fin_genomes(setty)
    for i in setty:
        holder += i
    genomes_to_test.append(holder)
    holder = ''
    # Test Case 4
    setty = init_genomes()
    count = 0
    for i in range(len(setty)):
        if count >= 64:
            count = 0
        setty[i] += cat_keys(kys, count, count+8, True)
        count += 8
    setty = fin_genomes(setty)
    for i in setty:
        holder += i
    genomes_to_test.append(holder)
    holder = ''
    # Test Case 5
    setty = init_genomes()
    count = 0
    for i in range(len(setty)):
        if count >= 64:
            count = 0
        setty[i] += cat_keys(kys, count, count+8, True)
        count += 8
    setty = fin_genomes(setty)
    count = 0
    for i in setty:
        if count >= 64:
            count = 0
        holder += i
        holder += cat_keys(kys, count, count+8)
        count += 8
    genomes_to_test.append(holder)
    return genomes_to_test


# ### NO IDEA ###

def test_sequence(tests=100):
    genome = '000' * 6000
    assert len(genome) == 18000
    count = 0
    for i in range(0, 17900, 21):
        genome = genome[:i] + '122' + genome[i+3:]
        genome = genome[:i+9] + '222' + genome[i+12:]
        assert len(genome) == 18000
        gpm.sequence_parser(str(genome))
        count += 1
        assert len(gpm.sequence_list) == count
        gpm.sequence_list = []
    gpm.sequence_parser(str(genome))
    print count
    print len(gpm.sequence_list)


# ### GENERATION AND BUILD ERROR TESTS ###
# NOTE: Seperate from the process of other tests.

def test_generation(tests=10000):
    d = []
    for i in range(tests):
        l = [0, 0, 0, 0]
        t = gpm.generate(18000)
        for c in t:
            if c == '0':
                l[0] += 1
            elif c == '1':
                l[1] += 1
            elif c == '2':
                l[2] += 1
            elif c == '3':
                l[3] += 1
            else:
                raise TypeError('Bad char')
        li = [a - 4500 for a in l]
        print l, li
        # d = [e + (abs(c) >= threshold) for e, c in itertools.izip(d, li)]
        d.append(l)
    # out = stats.chi2_contingency(d)
    out = stats.chisquare(d, axis=None)
    # Not sure if I really know how to use this
    return out


# ### GLOBAL VARS FOR OTHER TESTS


data_row = []


# ### SETUP TESTER FUNCTIONS ###

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def find_part(stry):
    part = None
    for i in range(0, len(stry), 3):
        curr_codon = stry[i:i+3]
        # Body-part codon
        if curr_codon == '000':
            part = '000'
            break
        elif curr_codon == '001':
            part = '001'
            break
        # Joint-part codon
        elif curr_codon == '200':
            part = '200'
            break
        # Neuron-part codon
        elif curr_codon == '312':
            part = '312'
            break
        # Sensor-part codon
        elif curr_codon == '100':
            part = '100'
            break
        # Wire-part codon
        elif curr_codon == '303':
            part = '303'
            break
    return part


def calc_cap_tester(curr_seq):
    rc_hold = 0
    cod_hold = []
    for i in range(0, len(curr_seq), 3):
        curr_codon = mt.table[curr_seq[i:i+3]]
        # Reg capacity
        if curr_codon == 'RC+30':
            rc_hold += 30
        elif curr_codon == 'RC+40':
            rc_hold += 40
        elif curr_codon == 'RC+50':
            rc_hold += 50
        elif curr_codon == 'RC+60':
            rc_hold += 60
        elif curr_codon == 'RC+70':
            rc_hold += 70
        elif curr_codon == 'RC+80':
            rc_hold += 80
        elif curr_codon == 'RC+90':
            rc_hold += 90
        elif curr_codon == 'RC+100':
            rc_hold += 100
        elif curr_codon == 'RC+110':
            rc_hold += 110
            # Codons
        elif curr_codon[1] == 'R':
            cod_hold.append(curr_codon)
    return [rc_hold, cod_hold]


def test_setup(genome, data_row):
    # Gives a row of data to describe the entire genome
    num_seq = 0     # whole num
    sequences = []  # list of int-strings (gene sequences)
    types = []      # list of int-strings (reg_codons)
    part = 0        # whole num
    reg_cap = []     # list of nums
    reg_codons = []     # list of char-strings (codon identifiers)
    """
    for i in range(0, len(genome), 3):
        started = False
        if (genome[i:i+3] == '122' and not started):
            start = i
            started = True
        elif (genome[i+i+3] == '222' and started):
            stop = i+3
            sequences.append(genome[start:stop])
            started = False
    """
    """
    for curr_seq in sequences:
    """
    # Turn genome string into list of codons
    parsed_genome = []
    for part in chunker(genome, 3):
        parsed_genome.append(part)
    # Search list of codons until there are no seqeunces
    while('122' in parsed_genome and '222' in parsed_genome):
        i1 = parsed_genome.index('122')
        i2 = parsed_genome.index('222')
        # if the sequence starts with a STOP
        if i1 >= i2:
            # Setup for next potential START:STOP section
            parsed_genome = parsed_genome[i2+1:]
        # If the sequence goes from start-to-stop
        else:
            # Number of sequences
            num_seq += 1
            # Sequences
            curr_seq = ''
            for i in range(i1, i2+1):
                curr_seq += parsed_genome[i]
            assert len(curr_seq) % 3 == 0
            assert curr_seq[0:3] == '122'
            assert curr_seq[-3:] == '222'
            sequences.append(curr_seq)
            # Types
            curr_type = find_part(curr_seq)
            types.append(curr_type)
            # Reg Capacity and Codons
            cod_hold = []
            if curr_type is not None:
                reg_cod_list = calc_cap_tester(curr_seq)
                reg_cap.append(reg_cod_list[0])
                cod_hold = reg_cod_list[1]
            # Reg capacity and Codons
            # Fill with a value, even if it's empty
            if cod_hold:
                reg_codons.append(cod_hold)
            # else:
            #    reg_codons.append([None])
            # Setup search for next START:STOP section
            parsed_genome = parsed_genome[i2+1:]
    # Part num
    part = len(types) - types.count(None)
    # assert (num_seq == len(sequences) == len(types) ==
    #         len(reg_cap) == len(reg_codons))
    dat_holder = [num_seq, sequences, types, part, reg_cap, reg_codons]
    for dat in dat_holder:
        data_row.append(dat)
    return data_row


# ### UPDATE TESTER FUNCTIONS ###

def count_regulators(part):
    total = 0
    for i in part:
        if i[0] is not None:
            total += i[2]
    return total


def test_update(data_row):
    # type, part, capacity, and codon index
    # buffered by 1 because of how data_row is initialized
    typ_i = 2 + 1
    par_i = 3 + 1
    cap_i = 4 + 1
    cod_i = 5 + 1
    # ### Without diffusion ###
    # ## Number of updates
    capacity_list = []
    ag_codon_list = []
    update_nd = []
    # For all sequences
    for i in range(len(data_row[cap_i])):
        # Only using sequences with types
        if data_row[typ_i][i] is not None:
            capacity_list.append(data_row[cap_i][i])
            ag_codon_list.append(data_row[cod_i][i])
            try:
                # Divide capacity by amount of regulatory codons
                update_nd.append(data_row[cap_i][i] /
                                 (len(data_row[cod_i][i]) -
                                  data_row[cod_i][i].count(None)))
            except ZeroDivisionError:
                update_nd.append(0)
    assert data_row[par_i] == len(update_nd)
    # ## Number of final regulatory elements for each part
    ag_codon_list_count = []
    ag_codon_list_clone = copy.deepcopy(ag_codon_list)
    codon_list = list(set([i for i in mt.table.itervalues()]))
    codon_list_to_fill = [[i, 0] for i in codon_list]
    reg_elems_nd = []
    # Go through each codon-set (of a sequence) in the genome
    for cset_list in ag_codon_list_clone:
        bg_holder = copy.deepcopy(codon_list_to_fill)
        # for each codon-set
        while cset_list:
            # Add a list with the next codon and how many of them there are
            curr_codon = cset_list[0]
            assert (type(curr_codon) is str) or (curr_codon is None)
            if curr_codon is not None:
                index = codon_list.index(curr_codon)
                bg_holder[index][1] += cset_list.count(curr_codon)
            # Then remove all other codons of that type from the codon-set
            while curr_codon in cset_list:
                cset_list.remove(curr_codon)
        ag_codon_list_count.append(bg_holder)
    assert len(ag_codon_list_count) == len(ag_codon_list)
    assert len(ag_codon_list_count) == len(update_nd)
    assert len(ag_codon_list_count[0]) == len(codon_list)
    for i in range(len(ag_codon_list_count[0])):
        assert ag_codon_list_count[0][i][0] == codon_list[i]
    for i in range(len(ag_codon_list_count)):
        part_holder = [[j[0], j[1]*update_nd[i]] for
                       j in ag_codon_list_count[i]]
        reg_elems_nd.append(part_holder)
    # ### With Diffusion ###
    # make holders
    codon_elems_counter = []
    for i in range(len(ag_codon_list_count)):
        # codon | num_of_this_codon_type_in_part | num_of_elems_this_part_has
        part_holder = [[j[0], j[1], 0] for j in ag_codon_list_count[i]]
        codon_elems_counter.append(part_holder)
    codon_elems_final = []
    reg_up_per = []
    for i in ag_codon_list_count:
        reg_up_holder = 0
        for j in i:
            if j[0] is not None and j[0][1] == 'R':
                reg_up_holder += j[1]
        reg_up_per.append(reg_up_holder)
    #    elements in part   |  total part capacity
    part_elems_counter = [[0, i] for i in capacity_list]
    pool_total = copy.deepcopy(codon_list_to_fill)
    reg_push_count = copy.deepcopy(pool_total)
    reg_pull_count = copy.deepcopy(pool_total)
    update_count = [0] * len(codon_elems_counter)
    update_wd = []
    assert len(codon_elems_counter[0]) == len(pool_total)
    for i in range(len(codon_elems_counter[0])):
        assert codon_elems_counter[0][i][0] == pool_total[i][0]
    # ## Abstract updating process with regulatory interaction
    while(codon_elems_counter):
        count = 0
        part = 0
        # For each part in the genome
        for i in codon_elems_counter:
            assert i == codon_elems_counter[part]
            reg_total = count_regulators(i)
            reg_max = capacity_list[part]
            # print reg_max, reg_total, reg_up_per[part]
            # Check to see if you should start discarding parts
            if reg_up_per[part] == 0:
                count += 1
                if count == len(codon_elems_counter):
                    # print 'Discarded:', part, i
                    codon_elems_counter.pop(part)
                    part_elems_counter.pop(part)
                    reg_up_per.pop(part)
                    update_count.pop(part)
                    count -= 1
                part += 1
            # If part has reached capacity
            # print part_elems_counter[part], reg_up_per[part]
            elif (reg_max <= (reg_total + reg_up_per[part])):
                # Get it out of the loop
                # print 'Popped:', part, len(codon_elems_counter), i
                codon_elems_final.append(codon_elems_counter.pop(part))
                update_wd.append(update_count.pop(part))
                part_elems_counter.pop(part)
                reg_up_per.pop(part)
                part += 1
            # If part is not at capacity
            else:
                # Update it codon-by-codons
                for j in i:
                    if j[0] is not None:
                        if j[1] > 0:
                            j[2] += j[1]
                # Regulatory Element Interaction Setup
                pushed = copy.deepcopy(codon_list_to_fill)
                pulled = copy.deepcopy(codon_list_to_fill)
                # pl_filler = [k[1] for k in pool_total]
                ph_filler = [k[2] for k in i]
                # Pulled
                pulled = [[j[0], int(math.floor(j[1]))]
                          for j in pool_total]
                pool_total = [[j[0], j[1] - k[1]] for j, k in
                              itertools.izip(pool_total, pulled)]
                for c, e in enumerate(pool_total):
                    if e[1] < 0:
                        pool_total[c][1] = 0
                        pulled[c][1] += e[1]
                # Pushed
                for k in range(len(pushed)):
                    assert pushed[k][0] == i[k][0]
                    try:
                        pushed[k][1] += int(math.floor(ph_filler[k] *
                                            gpm.diffusion_rate_push))
                    except TypeError:
                        print "Error!", pushed[k][0], ph_filler[k]
                pool_total = [[j[0], j[1] + k[1]] for j, k in
                              itertools.izip(pool_total, pushed)]
                # Application
                for k in range(len(pool_total)):
                    assert pool_total[k][0] == i[k][0]
                    try:
                        i[k][2] = max(0, i[k][2] +
                                      pulled[k][1] - pushed[k][1])
                    except TypeError:
                        print "Error!", pool_total[k][0]
                update_count[part] += 1
                part += 1
    assert len(reg_push_count) == len(reg_pull_count)
    # Regulatory Elements with interaction
    reg_elems_wd = []
    # Fill with info from copied list of finished parts
    for i in codon_elems_final:
        c_holder = copy.deepcopy(codon_list_to_fill)
        for j in i:
            ind = codon_list.index(j[0])
            c_holder[ind][1] += j[2]
        # re_wd_holder = [[j[0], j[2]] for j in codon_elems_final]
        reg_elems_wd.append(c_holder)
    dat_holder = [update_nd, reg_elems_nd, update_wd, reg_elems_wd]
    for dat in dat_holder:
        data_row.append(dat)
    return data_row


# ### PARTS LIST TESTER FUNCTIONS ###

def test_parts_list():
    pass


# ### BUILT AGENT TESTER FUNCTIONS ###


# ### BEHAVIOR TESTER FUNCTIONS ###

# This will be handled during data analysis, becuase
# the test is to see if the performance is consistant.
# I just need to ensure I record the fitness scores
# of all the agents, and label them properly


# ### SELECTION TESETER FUNCTIONS ###

# This will also be handled during data analysis,
# because it's just about recorded hamming distance
# and child-parent relationships


# ### DATA TABLE FUNCTIONS ###

def output_tester_sheet_p():
    sheet = tablib.Dataset()
    sheet.headers = ['Agent', 'Num_Sequences', 'Sequences', 'Types', 'Part',
                     'Reg_Capacity', 'Codons', 'Updates_NI', 'Reg_Elem_NI',
                     'Updates_WI', 'Reg_Elem_WI', 'Germ_Genome']
    agents = generate_genomes()
    for i in range(len(agents)):
        data_row = []
        print '1'
        data_row.append(i)
        data_row = test_setup(agents[i], data_row)
        print '2'
        data_row = test_update(data_row)
        print '3'
        data_row.append(agents[i])
        print len(data_row), len(sheet.headers)
        sheet.append(data_row)
        print '4'
    if os.path.isfile('./output_tester_sheet_p.csv'):
        os.remove('./output_tester_sheet_p.csv')
    with open('./output_tester_sheet_p.csv', 'w+') as f:
        f.write(sheet.csv)


def get_nested_1(line):
    holder = []
    line = line.replace(' ', '').replace('[', '')
    for i in line.split(','):
        holder.append(i.replace(']', ''))
    return holder


def get_nested_2(line):
    line = line.replace(' ', '').replace('[', '')
    holder_2 = []
    for i in line.split('],'):
        holder = []
        for j in i.split(','):
            holder.append(j.replace(']', ''))
        holder_2.append(holder)
    return holder_2


def get_nested_3(line):
    line = line.replace(' ', '').replace('[', '')
    holder_3 = []
    for i in line.split(']],'):
        holder_2 = []
        for j in i.split('],'):
            holder = []
            for k in j.split(','):
                holder.append(k.replace(']', ''))
            holder_2.append(holder)
        holder_3.append(holder_2)
    return holder_3


def compare_sheets():
    tester = tablib.Dataset()
    tested = tablib.Dataset()
    compare_sheet = tablib.Dataset()
    compare_sheet.headers = ['Agent', 'Num_Sequences', 'Sequences', 'Types',
                             'Part', 'Reg_Capacity', 'Codons', 'Updates_NI',
                             'Reg_Elem_NI', 'Updates_WI', 'Reg_Elem_WI',
                             'Germ_Genome']
    tester.csv = open('./output_tester_sheet_p.csv', 'r').read()
    tested.csv = open('./output_to_test_p.csv', 'r').read()
    for i in range(len(tester)):
        row = []
        for j in range(len(tester[i])):
            holder = []
            if tester[i][j] == tested[i][j]:
                holder = True
            else:
                t1 = str(tester[i][j])
                t2 = str(tested[i][j])
                if (t1.find(']],') != -1) or (t2.find(']],') != -1):
                    l1 = get_nested_3(t1)
                    l2 = get_nested_3(t2)
                    for k in range(len(l1)):
                        for m in range(len(l1[k])):
                            for n in range(len(l1[k][m])):
                                try:
                                    if (l1[k][m][n] != l2[k][m][n]):
                                        holder.append(((k, m, n),
                                                       l1[k][m][n],
                                                       l2[k][m][n]))
                                except IndexError:
                                    pass
                elif (t1.find('],') != -1) or (t2.find('],') != -1):
                    l1 = get_nested_2(t1)
                    l2 = get_nested_2(t2)
                    for m in range(len(l1)):
                            for n in range(len(l1[m])):
                                try:
                                    if (l1[m][n] != l2[m][n]):
                                        holder.append(((m, n),
                                                       l1[m][n],
                                                       l2[m][n]))
                                except IndexError:
                                    pass
                elif (t1.find(']') != -1) or (t2.find(']') != -1):
                    l1 = get_nested_1(t1)
                    l2 = get_nested_1(t2)
                    for n in range(len(l1)):
                                try:
                                    if (l1[n] != l2[n]):
                                        holder.append(((n), l1[n], l2[n]))
                                except IndexError:
                                    pass
                else:
                    l1 = int(t1)
                    l2 = int(t2)
            row.append(holder)
        compare_sheet.append(row)
    if os.path.isfile('./compare_sheet.csv'):
        os.remove('./compare_sheet.csv')
    with open('./compare_sheet.csv', 'w+') as f:
        f.write(compare_sheet.csv)
