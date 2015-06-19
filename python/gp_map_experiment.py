################################################################
#  G->P Map
################################################################
#  Supporting Functions:
#
#  -> part_maker              :: Input (string); Output (void);
#                                Side Effects (fill parts_built).
#
#     -> gc_reader            :: Input (string); Output (void);
#                                Side Effects (fill parts_developing).
#
#         -> sequence_parser     :: Input (string); Output (void);
#                                   Side Effects (fill sequence_list).
#
#  -> agent_builder
#     ->
#
#  Supporting Variables:
#
#  -> parts_developing (list)
#  -> parts_built (list)
#  -> sequence_list (tuple)
#  -> isDeveloping (bool)
#  ->
#
#
# '/home/josh/Documents/projects/thesis/coding/trial/python/data/sens3/158-177/dev_data177.txt'
################################################################
# Headers
################################################################
import os
import random
import time
import itertools
import bisect
import timeout
import math
import tablib
import numpy as np
# import matplotlib.pyplot as plt
from my_table import table

###############################################################
# Global Variables
################################################################
# Development Vars
sequence_list = []
parts_developing = []
parts_diffusing = []
parts_built = []
passed_bodys = [[], [], [], [], [], [], [], []]
passed_joints = [[], [], [], [], [], []]
passed_neurons = [[], [], []]
passed_sensors = [[], []]
passed_wires = [[], [], []]
big_holder = ''
germ_genomes = []
soma_genomes = []

# diffusion
regulator_pool = [0.] * 40
diffusion_rate_push = .01
diffusion_rate_pull = .1

# Error Vars
# [0,1) ; the higher the more chance of error
mutation_error = .000
transcription_error = .000

# File Vars
blueprint_file = './blueprint.dat'
fit_file = './fits.dat'
app_file = '../c++/app'


def make_data_file(dat_dir, data_file='exp_data1.txt'):
    the_file = dat_dir + data_file
    count = 1
    while (os.path.isfile(the_file)):
        index = the_file.find('.txt')
        if (count <= 10):
            the_file = the_file[:index-1] + str(count) + the_file[index:]
        elif (count > 10 and count <= 100):
            the_file = the_file[:index-2] + str(count) + the_file[index:]
        elif (count > 100 and count <= 1000):
            the_file = the_file[:index-3] + str(count) + the_file[index:]
        count += 1
        # print data_file, count
    return the_file

# HillClimber Vars
gens = 200
pops = 60

# Data Vars
development_data = tablib.Dataset()
genecode_length = 0
genecode_used_length = 0
num_bodys_prepped = 0
actual_bodys_built = 0
num_joints_prepped = 0
actual_joints_built = 0
num_sensors_prepped = 0
actual_sensors_built = 0
num_neurons_prepped = 0
actual_neurons_built = 0
num_wires_prepped = 0
actual_wires_built = 0
read_codons = 0
regulators_built = 0
total_updates = 0
log_timeouts = []


# RESET FUNCTION
def reset_globals():
    global sequence_list, parts_developing, parts_diffusing, parts_built
    global passed_bodys, passed_joints, passed_neurons, passed_sensors
    global passed_sensors, passed_wires, big_holder, genecode_length
    global genecode_used_length, num_bodys_prepped, actual_bodys_built
    global num_joints_prepped, actual_joints_built, num_neurons_prepped
    global actual_neurons_built, num_sensors_prepped, actual_sensors_built
    global num_wires_prepped, actual_wires_built, read_codons
    global regulators_built, total_updates, regulator_pool
    sequence_list = []
    parts_developing = []
    parts_diffusing = []
    parts_built = []
    passed_bodys = [[], [], [], [], [], [], [], []]
    passed_joints = [[], [], [], [], [], []]
    passed_neurons = [[], [], []]
    passed_sensors = [[], []]
    passed_wires = [[], [], []]
    big_holder = ''
    genecode_length = 0
    genecode_used_length = 0
    num_bodys_prepped = 0
    actual_bodys_built = 0
    num_joints_prepped = 0
    actual_joints_built = 0
    num_sensors_prepped = 0
    actual_sensors_built = 0
    num_neurons_prepped = 0
    actual_neurons_built = 0
    num_wires_prepped = 0
    actual_wires_built = 0
    read_codons = 0
    regulators_built = 0
    total_updates = 0
    regulator_pool = [0.] * 40

###############################################################################
# Functions
###############################################################################


def sigmoid(x):
    val = 1 / (1 + math.exp(-x))
    if np.isnan(val):
        val = 0
    return val


def select(fs):
    p = random.uniform(0, sum(fs))
    print p
    for i, f in enumerate(fs):
        p -= f
        print i, f, p
        if p <= 0:
            break
    return i


def select_fast(cfl):
    return bisect.bisect_left(cfl, random.uniform(0, cfl[-1]))


class Part(object):
    def __init__(self, gene_sequence):
        self.is_developing = True
        self.gene_sequence = gene_sequence   # Also a data var via len(this)
        self.capacity = 0
        self.regulators_per_update = 0
        self.regulatory_elements = 0   # Also a data var
        self.blueprint = []
        # BodyPart Codons
        self.codon_size = [0, 0]   # +/- codons
        self.codon_s_num = [0, 0]
        self.codon_j_num = [0, 0]
        self.codon_n_num = [0, 0]
        self.codon_s_loc = [0, 0, 0, 0, 0, 0]   # pos x,y,z then neg x,y,z
        self.codon_j_loc = [0, 0, 0, 0, 0, 0]
        # JointPart Codons
        self.codon_active_passive = [0, 0]
        self.codon_free_rigid = [0, 0]
        self.codon_upper_lower = [0, 0, 0, 0]   # upper+/-, lower +/-
        self.codon_j_inputs = [0, 0]
        # NeuronPart Codons
        self.codon_n_inputs = [0, 0]
        self.codon_n_outputs = [0, 0]
        # self.codon_hidden = [0, 0]
        # SensorPart Codon
        self.codon_s_outputs = [0, 0]
        # WirePart Codons
        self.codon_weight = [0, 0]
        self.codon_direct = [0, 0]
        # Capacity codons
        self.rc30 = 0
        self.rc40 = 0
        self.rc50 = 0
        self.rc60 = 0
        self.rc70 = 0
        self.rc80 = 0
        self.rc90 = 0
        self.rc100 = 0
        self.rc110 = 0
        self.rc120 = 0
        # Other codons
        self.codon_junk = 0
        # BodyPart REs
        self.reg_size = [0., 0.]  # add and subtract to compress into 1 var
        self.reg_s_num = [0., 0.]    # +/- values
        self.reg_j_num = [0., 0.]
        self.reg_n_num = [0, 0]
        self.reg_s_loc = [0., 0., 0., 0., 0., 0.]  # + x,y,z then -
        self.reg_j_loc = [0., 0., 0., 0., 0., 0.]
        # JointPart REs
        self.reg_active_passive = [0., 0.]
        self.reg_free_rigid = [0., 0.]
        self.reg_upper_lower = [0., 0., 0., 0.]   # upper+/-, then lower...
        self.reg_j_inputs = [0., 0.]  # NOTE: CHANGED
        # NeuronPart REs
        self.reg_n_inputs = [0., 0.]  # NOTE: CHANGED
        self.reg_n_outputs = [0., 0.]  # NOTE: CHANGED
        # SensorPart REs
        self.reg_s_outputs = [0., 0.]  # NOTE: CHANGED
        # WirePart REs
        self.reg_weight = [0., 0.]
        self.reg_direct = [0., 0.]
        # Data vars
        self.codons_read = 0
        self.num_updates = 0
        self.num_diffuses = 0

    def calculate_capacity(self):
        if self.__class__ != Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                if cur_codon == 'RC+30':
                    self.rc30 += 1
                    self.capacity += 30
                elif cur_codon == 'RC+40':
                    self.rc40 += 1
                    self.capacity += 40
                elif cur_codon == 'RC+50':
                    self.rc50 += 1
                    self.capacity += 50
                elif cur_codon == 'RC+60':
                    self.rc60 += 1
                    self.capacity += 60
                elif cur_codon == 'RC+70':
                    self.rc70 += 1
                    self.capacity += 70
                elif cur_codon == 'RC+80':
                    self.rc80 += 1
                    self.capacity += 80
                elif cur_codon == 'RC+90':
                    self.rc90 += 1
                    self.capacity += 90
                elif cur_codon == 'RC+100':
                    self.rc100 += 1
                    self.capacity += 100
                elif cur_codon == 'RC+110':
                    self.rc110 += 1
                    self.capacity += 110
                elif cur_codon == 'RC+120':
                    self.rc120 += 1
                    self.capacity += 120
        else:
            raise TypeError('Only a Part subclass can use this!')

    def count_regulators(self):
        if self.__class__ != Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                if cur_codon[1] == 'R':
                    self.regulators_per_update += 1
        else:
            raise TypeError('Only a Part subclass can use this!')

    def init_codons(self):
        if self.__class__ != Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                # print cur_codon,
                self.codons_read += 1
                # BodyPart Codons
                if cur_codon == 'BR_SIZE+':
                    self.codon_size[0] += 1
                elif cur_codon == 'BR_SIZE-':
                    self.codon_size[1] += 1
                elif cur_codon == 'BR_S_M+':
                    self.codon_s_num[0] += 1
                elif cur_codon == 'BR_S_M-':
                    self.codon_s_num[1] += 1
                elif cur_codon == 'BR_J_M+':
                    self.codon_j_num[0] += 1
                elif cur_codon == 'BR_J_M-':
                    self.codon_j_num[1] += 1
                elif cur_codon == 'BR_N_M+':
                    self.codon_n_num[0] += 1
                elif cur_codon == 'BR_N_M-':
                    self.codon_n_num[1] += 1
                elif cur_codon == 'BR_S_X+':
                    self.codon_s_loc[0] += 1
                elif cur_codon == 'BR_S_X-':
                    self.codon_s_loc[3] += 1
                elif cur_codon == 'BR_S_Y+':
                    self.codon_s_loc[1] += 1
                elif cur_codon == 'BR_S_Y-':
                    self.codon_s_loc[4] += 1
                elif cur_codon == 'BR_S_Z+':
                    self.codon_s_loc[2] += 1
                elif cur_codon == 'BR_S_Z-':
                    self.codon_s_loc[5] += 1
                elif cur_codon == 'BR_J_X+':
                    self.codon_j_loc[0] += 1
                elif cur_codon == 'BR_J_X-':
                    self.codon_j_loc[3] += 1
                elif cur_codon == 'BR_J_Y+':
                    self.codon_j_loc[1] += 1
                elif cur_codon == 'BR_J_Y-':
                    self.codon_j_loc[4] += 1
                elif cur_codon == 'BR_J_Z+':
                    self.codon_j_loc[2] += 1
                elif cur_codon == 'BR_J_Z-':
                    self.codon_j_loc[5] += 1
                # JointPart Codons
                elif cur_codon == 'JR_AP+':
                    self.codon_active_passive[0] += 1
                elif cur_codon == 'JR_AP-':
                    self.codon_active_passive[1] += 1
                elif cur_codon == 'JR_FR+':
                    self.codon_free_rigid[0] += 1
                elif cur_codon == 'JR_FR-':
                    self.codon_free_rigid[1] += 1
                elif cur_codon == 'JR_U+':
                    self.codon_upper_lower[0] += 1
                elif cur_codon == 'JR_U-':
                    self.codon_upper_lower[1] += 1
                elif cur_codon == 'JR_L+':
                    self.codon_upper_lower[2] += 1
                elif cur_codon == 'JR_L-':
                    self.codon_upper_lower[3] += 1
                elif cur_codon == 'JR_I+':
                    self.codon_j_inputs[0] += 1
                elif cur_codon == 'JR_I-':
                    self.codon_j_inputs[1] += 1
                # NeuronPart Codons
                elif cur_codon == 'NR_I+':
                    self.codon_n_inputs[0] += 1
                elif cur_codon == 'NR_I-':
                    self.codon_n_inputs[1] += 1
                elif cur_codon == 'NR_O+':
                    self.codon_n_outputs[0] += 1
                elif cur_codon == 'NR_O-':
                    self.codon_n_outputs[1] += 1
                # elif cur_codon=='NR_H+':
                #   self.codon_hidden[0] += 1
                # elif cur_codon=='NR_H-':
                #   self.codon_hidden[1] += 1
                # SensorPart Codons
                elif cur_codon == 'SR_O+':
                    self.codon_s_outputs[0] += 1
                elif cur_codon == 'SR_O-':
                    self.codon_s_outputs[1] += 1
                # WirePart Codons
                elif cur_codon == 'WR_W+':
                    self.codon_weight[0] += 1
                elif cur_codon == 'WR_W-':
                    self.codon_weight[1] += 1
                elif cur_codon == 'WR_D+':
                    self.codon_direct[0] += 1
                elif cur_codon == 'WR_D-':
                    self.codon_direct[1] += 1
                # Everything else
                elif (cur_codon[1] == 'P' or cur_codon[0] == 'R' or
                      cur_codon[1] == 'T'):
                    self.codon_junk += 1
                else:
                    raise KeyError('Take a look at your Table!')
        else:
            raise TypeError('Only a Part subclass can use this!')

    def get_push_list(self):
        global regulator_pool
        push_list = []
        # BodyPartREs
        push_list += self.reg_size
        push_list += self.reg_s_num
        push_list += self.reg_j_num
        push_list += self.reg_n_num
        push_list += self.reg_s_loc
        push_list += self.reg_j_loc
        # JointPart REs
        push_list += self.reg_active_passive
        push_list += self.reg_free_rigid
        push_list += self.reg_upper_lower
        push_list += self.reg_j_inputs
        # NeuronPart REs
        push_list += self.reg_n_inputs
        push_list += self.reg_n_outputs
        # SensorPart REs
        push_list += self.reg_s_outputs
        # WirePart REs
        push_list += self.reg_weight
        push_list += self.reg_direct
        # if push_list > 0:
        #    print "PHL:", push_list
        # n_push_list = [push_list[i]/sum(push_list)
        #                for i in range(len(push_list))]
        # o_push_list = [0] * 40
        o_push_list = [int(round(diffusion_rate_push * i)) for i in push_list]
        """
        re_to_push = int(diffusion_rate_push * sum(push_list))
        while sum(o_push_list) < re_to_push:
            m = max(push_list)
            ml = [i for i, j in enumerate(push_list) if j == m]
            mli = random.randrange(0, len(ml))
            o_push_list[ml[mli]] += 1
            push_list[ml[mli]] = 0
        """
        # push_list = [math.floor(i * diffusion_rate_push) for i in push_list]
        # if o_push_list > 0:
        #    print "PHL:", o_push_list
        regulator_pool = [i + j for i, j in
                          itertools.izip(regulator_pool, o_push_list)]
        # if sum(regulator_pool) > 0:
        #    print "RP af PH:", regulator_pool
        return o_push_list

    def get_pull_list(self):
        global regulator_pool
        pull_list = [i for i in regulator_pool]
        # if sum(pull_list) > 0:
        #    print "PLL flr:", pull_list
        # o_pull_list = [0] * 40
        o_pull_list = [int(round(diffusion_rate_pull * i)) for i in pull_list]
        """
        re_to_pull = int(diffusion_rate_pull * sum(pull_list))
        while sum(o_pull_list) < re_to_pull:
            m = max(pull_list)
            ml = [i for i, j in enumerate(pull_list) if j == m]
            mli = random.randrange(0, len(ml))
            o_pull_list[ml[mli]] += 1
            pull_list[ml[mli]] = 0
        """
        regulator_pool = [i - j for i, j in
                          itertools.izip(regulator_pool, o_pull_list)]
        for c, e in enumerate(regulator_pool):
            if e < 0:
                regulator_pool[c] = 0
                o_pull_list[c] += e
        # if sum(o_pull_list) > 0:
        #    print "PLL:", o_pull_list
        # if sum(regulator_pool) > 0:
        #    print "RP af PL:", regulator_pool
        return o_pull_list

    def use_phpl_list(self, phlst, pllst):
        self.reg_size[0] += pllst[0] - phlst[0]
        self.reg_size[1] += pllst[1] - phlst[1]
        self.reg_s_num[0] += pllst[2] - phlst[2]
        self.reg_s_num[1] += pllst[3] - phlst[3]
        self.reg_j_num[0] += pllst[4] - phlst[4]
        self.reg_j_num[1] += pllst[5] - phlst[5]
        self.reg_n_num[0] += pllst[6] - phlst[6]
        self.reg_n_num[1] += pllst[7] - phlst[7]
        self.reg_s_loc[0] += pllst[8] - phlst[8]
        self.reg_s_loc[1] += pllst[9] - phlst[9]
        self.reg_s_loc[2] += pllst[10] - phlst[10]
        self.reg_s_loc[3] += pllst[11] - phlst[11]
        self.reg_s_loc[4] += pllst[12] - phlst[12]
        self.reg_s_loc[5] += pllst[13] - phlst[13]
        self.reg_j_loc[0] += pllst[14] - phlst[14]
        self.reg_j_loc[1] += pllst[15] - phlst[15]
        self.reg_j_loc[2] += pllst[16] - phlst[16]
        self.reg_j_loc[3] += pllst[17] - phlst[17]
        self.reg_j_loc[4] += pllst[18] - phlst[18]
        self.reg_j_loc[5] += pllst[19] - phlst[19]
        # JointPart REs
        self.reg_active_passive[0] += pllst[20] - phlst[20]
        self.reg_active_passive[1] += pllst[21] - phlst[21]
        self.reg_free_rigid[0] += pllst[22] - phlst[22]
        self.reg_free_rigid[1] += pllst[23] - phlst[23]
        self.reg_upper_lower[0] += pllst[24] - phlst[24]
        self.reg_upper_lower[1] += pllst[25] - phlst[25]
        self.reg_upper_lower[2] += pllst[26] - phlst[26]
        self.reg_upper_lower[3] += pllst[27] - phlst[27]
        self.reg_j_inputs[0] += pllst[28] - phlst[28]
        self.reg_j_inputs[1] += pllst[29] - phlst[29]
        # NeuronPart REs
        self.reg_n_inputs[0] += pllst[30] - phlst[30]
        self.reg_n_inputs[1] += pllst[31] - phlst[31]
        self.reg_n_outputs[0] += pllst[32] - phlst[32]
        self.reg_n_outputs[1] += pllst[33] - phlst[33]
        # SensorPart REs
        self.reg_s_outputs[0] += pllst[34] - phlst[34]
        self.reg_s_outputs[1] += pllst[35] - phlst[35]
        # WirePart REs
        self.reg_weight[0] += pllst[36] - phlst[36]
        self.reg_weight[1] += pllst[37] - phlst[37]
        self.reg_direct[0] += pllst[38] - phlst[38]
        self.reg_direct[1] += pllst[39] - phlst[39]

    def _diffusion(self):
        pllst = self.get_pull_list()
        phlst = self.get_push_list()
        self.use_phpl_list(phlst, pllst)
        self.regulatory_elements += sum(phlst) - sum(pllst)

    def _update(self):
        self.num_updates += 1
        self.regulatory_elements += self.regulators_per_update
        # BodyPart REs
        self.reg_size[0] += self.codon_size[0]
        self.reg_size[1] += self.codon_size[1]
        self.reg_s_num[0] += self.codon_s_num[0]
        self.reg_s_num[1] += self.codon_s_num[1]
        self.reg_j_num[0] += self.codon_j_num[0]
        self.reg_j_num[1] += self.codon_j_num[1]
        self.reg_n_num[0] += self.codon_n_num[0]
        self.reg_n_num[1] += self.codon_n_num[1]
        self.reg_s_loc[0] += self.codon_s_loc[0]
        self.reg_s_loc[1] += self.codon_s_loc[1]
        self.reg_s_loc[2] += self.codon_s_loc[2]
        self.reg_s_loc[3] += self.codon_s_loc[3]
        self.reg_s_loc[4] += self.codon_s_loc[4]
        self.reg_s_loc[5] += self.codon_s_loc[5]
        self.reg_j_loc[0] += self.codon_j_loc[0]
        self.reg_j_loc[1] += self.codon_j_loc[1]
        self.reg_j_loc[2] += self.codon_j_loc[2]
        self.reg_j_loc[3] += self.codon_j_loc[3]
        self.reg_j_loc[4] += self.codon_j_loc[4]
        self.reg_j_loc[5] += self.codon_j_loc[5]
        # JointPart REs
        self.reg_active_passive[0] += self.codon_active_passive[0]
        self.reg_active_passive[1] += self.codon_active_passive[1]
        self.reg_free_rigid[0] += self.codon_free_rigid[0]
        self.reg_free_rigid[1] += self.codon_free_rigid[1]
        self.reg_upper_lower[0] += self.codon_upper_lower[0]
        self.reg_upper_lower[1] += self.codon_upper_lower[1]
        self.reg_upper_lower[2] += self.codon_upper_lower[2]
        self.reg_upper_lower[3] += self.codon_upper_lower[3]
        self.reg_j_inputs[0] += self.codon_j_inputs[0]
        self.reg_j_inputs[1] += self.codon_j_inputs[1]
        # NeuronPart REs
        self.reg_n_inputs[0] += self.codon_n_inputs[0]
        self.reg_n_inputs[1] += self.codon_n_inputs[1]
        self.reg_n_outputs[0] += self.codon_n_outputs[0]
        self.reg_n_outputs[1] += self.codon_n_outputs[1]
        # SensorPart REs
        self.reg_s_outputs[0] += self.codon_s_outputs[0]
        self.reg_s_outputs[1] += self.codon_s_outputs[1]
        # WirePart REs
        self.reg_weight[0] += self.codon_weight[0]
        self.reg_weight[1] += self.codon_weight[1]
        self.reg_direct[0] += self.codon_direct[0]
        self.reg_direct[1] += self.codon_direct[1]


class BodyPart(Part):
    def __init__(self, gene_sequence, kind):
        Part.__init__(self, gene_sequence)
        self.kind = kind
        self.j_mount_loc = []
        self.j_mount_num = 0
        self.j_loc_holder = [0., 0., 0.]
        self.s_mount_loc = []
        self.s_mount_num = 0
        self.s_loc_holder = [0., 0., 0.]

    def calculate_mount_info(self):
        # Store last runs sensor and joint mount numbers
        old_s_num, old_j_num = self.s_mount_num, self.j_mount_num
        # calculate current sensor and joint locs
        self.j_loc_holder = [self.reg_j_loc[0] - self.reg_j_loc[3],
                             self.reg_j_loc[1] - self.reg_j_loc[4],
                             self.reg_j_loc[2] - self.reg_j_loc[5]]
        self.s_loc_holder = [self.reg_s_loc[0] - self.reg_s_loc[3],
                             self.reg_s_loc[1] - self.reg_s_loc[4],
                             self.reg_s_loc[2] - self.reg_s_loc[5]]
        # Update current sensor and joint mount numbers
        # Sensor
        try:
            self.s_mount_num = round(self.reg_s_num[0]/self.reg_s_num[1])
        except ZeroDivisionError:
            self.s_mount_num = round(self.reg_s_num[0]/1)
        if self.s_mount_num < 1:
            self.s_mount_num = 0
        # Joint
        try:
            self.j_mount_num = round(self.reg_j_num[0]/self.reg_j_num[1])
        except ZeroDivisionError:
            self.j_mount_num = round(self.reg_j_num[0]/1)
        if self.j_mount_num < 1:
            self.j_mount_num = 0
        # If there's a change in amount of sesnor mounts,
        # append a normalized location vector
        if ((self.s_mount_num - old_s_num) >= 1):
            norm = math.sqrt(self.s_loc_holder[0]**2 +
                             self.s_loc_holder[1]**2 +
                             self.s_loc_holder[2]**2)
            try:
                location = [round(self.s_loc_holder[0]/norm, 3),
                            round(self.s_loc_holder[1]/norm, 3),
                            round(self.s_loc_holder[2]/norm, 3)]
            except ZeroDivisionError:
                location = [0., 0., 0.]
            self.s_mount_loc.append(location)
        # Same for joints
        if ((self.j_mount_num - old_j_num) >= 1):
            norm = math.sqrt(self.j_loc_holder[0]**2 +
                             self.j_loc_holder[1]**2 +
                             self.j_loc_holder[2]**2)
            try:
                location = [round(self.j_loc_holder[0]/norm, 3),
                            round(self.j_loc_holder[1]/norm, 3),
                            round(self.j_loc_holder[2]/norm, 3)]
            except ZeroDivisionError:
                location = [0., 0., 0.]
            self.j_mount_loc.append(location)

    def update(self):
        self._update()
        self.calculate_mount_info()

    def get_blueprint(self):
        """Returns final measurements for BodyPart.

        This includes: One size measure (radius); One mass measure
        (based on size); 1 neuron-mount amount; 1 sensor-mount list
        (paired with location); 1 joint-mount list (paired with location);"""
        size = round((1 + .2 * (self.reg_size[0] - self.reg_size[1])), 3)
        if size < .5:
            size = .5
        # Mass will be calculated in BP
        # density = .23866348448
        # if self.kind=='sphere':
        #    mass = density * (4*math.pi/3) * size**3
        # elif self.kind=='cube':
        #    mass = density * (size*2)**3
        # Resize mounts based on number of locs registered
        joint_mounts = len(self.j_mount_loc)
        # Resize mounts based on size
        if joint_mounts > 1:
            if size <= .5:
                joint_mounts = 1
                self.j_mount_loc = self.j_mount_loc[0:1]
            elif size <= 1:
                joint_mounts = min(5, joint_mounts)
                self.j_mount_loc = self.j_mount_loc[0:joint_mounts]
            elif size <= 2:
                joint_mounts = min(9, joint_mounts)
                self.j_mount_loc = self.j_mount_loc[0:joint_mounts]
        try:
            neuron_mounts = round(self.reg_n_num[0]/self.reg_n_num[1])
        except ZeroDivisionError:
            neuron_mounts = round(self.reg_n_num[0]/1)
        # Resize mounts based on number of locs registered
        sensor_mounts = len(self.s_mount_loc)
        # Create blueprint
        self.blueprint = [self.kind, size, joint_mounts, self.j_mount_loc,
                          neuron_mounts, sensor_mounts, self.s_mount_loc]
        return self.blueprint


class JointPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)

    def update(self):
        self._update()

    def get_blueprint(self):
        """Returns final measurements for JointPart

        Includes whether joint gets a motor; whether it is free or rigid;
        and one value for each limit in radians (upper/lower)"""
        motor = (self.reg_active_passive[0] - self.reg_active_passive[1]) > 0
        free = (self.reg_free_rigid[0] - self.reg_free_rigid[1]) > 0
        try:
            upper_ratio = ((float(self.reg_upper_lower[0]) -
                           self.reg_upper_lower[1]) /
                           (self.reg_upper_lower[0] +
                            self.reg_upper_lower[1]))
            upper_limit = upper_ratio * math.pi
        except ZeroDivisionError:
            upper_limit = .5 * math.pi
        try:
            lower_ratio = ((float(self.reg_upper_lower[2]) -
                           self.reg_upper_lower[3]) /
                           (self.reg_upper_lower[2] +
                            self.reg_upper_lower[3]))
            lower_limit = lower_ratio * math.pi
        except ZeroDivisionError:
            lower_limit = -.5 * math.pi
        if free:
            pass
        else:
            if (sum(self.reg_upper_lower[:2]) > sum(self.reg_upper_lower[2:])):
                lower_limit = upper_limit
            else:
                upper_limit = lower_limit
        # NEED TO CHANGE THIS \/
        inputs = self.reg_j_inputs[0] - self.reg_j_inputs[1]
        # NEED TO CHANGE THIS ^
        if inputs < 0:
            inputs = 0
        self.blueprint = [motor, free, round(upper_limit, 4),
                          round(lower_limit, 4), inputs]
        return self.blueprint


class NeuronPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)

    def update(self):
        self._update()

    def get_blueprint(self):
        """Returns final measurements for NeuronPart

        Includes number of inputs, number of outputs, and whether its
        hidden (whether its outputs can go to motors, or neurons)"""
        try:
            input_slots = int(round(self.reg_n_inputs[0]/self.reg_n_inputs[1]))
        except ZeroDivisionError:
            input_slots = int(round(self.reg_n_inputs[0]/1))
        try:
            output_slots = int(round(self.reg_n_outputs[0] /
                                     self.reg_n_inputs[1]))
        except ZeroDivisionError:
            output_slots = int(round(self.reg_n_outputs[0]/1))

        self.blueprint = [input_slots, output_slots]
        return self.blueprint


class SensorPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)

    def update(self):
        self._update()

    def get_blueprint(self):
        """Returns final measurements for SensorPart

        This includes: Number of output slots"""
        try:
            output_slots = int(round(self.reg_s_outputs[0] /
                                     self.reg_s_outputs[1]))
        except ZeroDivisionError:
            output_slots = int(round(self.reg_s_outputs[0]/1))
        self.blueprint = [output_slots]
        return self.blueprint


class WirePart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)

    def update(self):
        self._update()

    def get_blueprint(self):
        """Returns final measurements for WirePart

        Includes weight of connection"""
        try:
            weight_ratio = (float(self.reg_weight[0]) -
                            self.reg_weight[1]) / (self.reg_weight[0] +
                                                   self.reg_weight[1])
            weight = weight_ratio
        except ZeroDivisionError:
            weight = 0
        direct = ((self.reg_direct[0] - self.reg_direct[1]) >= 0)
        self.blueprint = [weight, direct]
        return self.blueprint


def reproduce_with_errors(gene_code):
    """Returns given gene code with some errors.

    Error rate set by variable 'mutation_error'"""
    global mutation_error
    new_gene_code = ''
    for char in gene_code:
        if (mutation_error < random.random() and mutation_error > 0):
            new_gene_code += str(char)
        else:
            error_bit = (int(char) + random.randrange(1, 4)) % 4
            new_gene_code += str(error_bit)
    return new_gene_code


def transcribe_with_errors(gene_code):
    """Returns given gene code with some errors.

    Error rate set by variable 'transcription_error'"""
    global transcription_error
    new_gene_code = ''
    for char in gene_code:
        if (transcription_error < random.random() and transcription_error > 0):
            new_gene_code += str(char)
        else:
            error_bit = (int(char) + random.randrange(1, 4)) % 4
            new_gene_code += str(error_bit)
    return new_gene_code


def sequence_parser(gene_code):
    """Fills variable sequence_list."""
    start, stop, started = 0, 0, False
    global sequence_list
    sequence_list = []   # make sure you start with empty list!
    output_sequence = ''
    for i in range(0, len(gene_code), 3):
        triplet = gene_code[i:i+3]
        output_sequence += triplet
        cur_codon = table[triplet]
        if (cur_codon == 'START' and not started):
            start = i   # testerss
            started = True
            # print 'start', i
        elif (cur_codon == 'STOP' and started):
            stop = i+3
            # print 'stop', i+3   # tester
            # print 'start', start
            sequence_list = sequence_list + [gene_code[start:stop]]
            started = False
    return output_sequence     # tester


def setup_part(part):
    """Takes part and creates proper subclass object"""
    global parts_developing

    if part.__class__ == Part:
        for i in range(0, len(part.gene_sequence), 3):
            cur_codon = table[part.gene_sequence[i:i+3]]
            if cur_codon == 'BP_SPHERE':
                parts_developing.append(BodyPart(part.gene_sequence, 'sphere'))
                break
            elif cur_codon == 'BP_CUBE':
                parts_developing.append(BodyPart(part.gene_sequence, 'cube'))
                break
            elif cur_codon == 'SP_TOUCH':
                parts_developing.append(SensorPart(part.gene_sequence))
                break
            elif cur_codon == 'JP_HINGE':
                parts_developing.append(JointPart(part.gene_sequence))
                break
            elif cur_codon == 'WP_WIRE':
                parts_developing.append(WirePart(part.gene_sequence))
                break
            elif cur_codon == 'NP_NEURON':
                parts_developing.append(NeuronPart(part.gene_sequence))
                break
    else:
        raise TypeError('Only the base Part class can use this!')


def setup_blueprints(list_of_parts):
    global passed_bodys, passed_joints, passed_neurons, passed_sensors
    global passed_wires, num_bodys_prepped, num_joints_prepped
    global num_sensors_prepped, num_neurons_prepped, num_wires_prepped
    b_counter, j_counter, n_counter, s_counter, w_counter = 0, 0, 0, 0, 0
    place_counter = 1
    b_max, j_max, n_max, s_max, w_max = 0, 0, 0, 0, 0
    # Set max variables
    for i in list_of_parts:
        if i.__class__ == BodyPart:
            b_max += 1
        elif i.__class__ == JointPart:
            j_max += 1
        elif i.__class__ == NeuronPart:
            n_max += 1
        elif i.__class__ == SensorPart:
            s_max += 1
        elif i.__class__ == WirePart:
            w_max += 1
        else:
            raise TypeError('Look at parts_built!')
    num_bodys_prepped = b_max
    num_joints_prepped = j_max
    num_neurons_prepped = n_max
    num_sensors_prepped = s_max
    num_wires_prepped = w_max
    while(b_counter < b_max):
        for i in list_of_parts:
            if i.__class__ == BodyPart:
                passed_bodys[0].append(b_counter)
                for k in i.get_blueprint():
                    passed_bodys[place_counter].append(k)
                    place_counter += 1
                b_counter += 1
                place_counter = 1
    while(j_counter < j_max):
        for i in list_of_parts:
            if i.__class__ == JointPart:
                passed_joints[0].append(j_counter)
                for k in i.get_blueprint():
                    passed_joints[place_counter].append(k)
                    place_counter += 1
                j_counter += 1
                place_counter = 1
    while(n_counter < n_max):
        for i in list_of_parts:
            if i.__class__ == NeuronPart:
                passed_neurons[0].append(n_counter)
                for k in i.get_blueprint():
                    passed_neurons[place_counter].append(k)
                    place_counter += 1
                n_counter += 1
                place_counter = 1
    while(s_counter < s_max):
        for i in list_of_parts:
            if i.__class__ == SensorPart:
                passed_sensors[0].append(s_counter)
                passed_sensors[1].append(i.get_blueprint()[0])
                s_counter += 1
    while(w_counter < w_max):
        for i in list_of_parts:
            if i.__class__ == WirePart:
                passed_wires[0].append(w_counter)
                passed_wires[1].append(i.get_blueprint()[0])
                passed_wires[2].append(i.get_blueprint()[1])
                w_counter += 1


def format_output():
    global passed_bodys, passed_joints, passed_neurons
    global passed_sensors, passed_wires, big_holder
    big_holder = ''
    holder = ''
    i_num = 0
    j_num = 0
    k_num = 0
    # for quality-lists of bodies
    if any(passed_bodys):
        for i in passed_bodys:
            j_num = 0
            # for each quality
            for j in i:
                # if not loc list
                if i_num != 4 and i_num != 7:
                    # print out this quality in order of parts
                    holder += '{},'.format(i[j_num])
                    # if loc list
                else:
                    k_num = 0
                    # go through list
                    for k in j:
                        # if empty
                        if not i[j_num][k_num]:
                            holder += '{},'.format(i[j_num][k_num])
                        else:
                            # print through the elements
                            for m in k:
                                holder += '{},'.format(m)
                            holder += ';'
                    # and mark the end of a parts locs
                    holder += '|'
                    k_num += 1
                j_num += 1
            holder += '\n'
            i_num += 1
        big_holder += holder + '\n'
        holder = ''
    else:
        big_holder += 'EMPTY\n\n'
    if any(passed_joints):
        for i in passed_joints:
            j_num = 0
            for j in i:
                holder += '{},'.format(i[j_num])
                j_num += 1
            holder += '\n'
        big_holder += holder + '\n'
        holder = ''
    else:
        big_holder += 'EMPTY\n\n'
    if any(passed_neurons):
        for i in passed_neurons:
            j_num = 0
            for j in i:
                holder += '{},'.format(i[j_num])
                j_num += 1
            holder += '\n'
        big_holder += holder + '\n'
        holder = ''
    else:
        big_holder += 'EMPTY\n\n'
    if any(passed_sensors):
        for i in passed_sensors:
            j_num = 0
            for j in i:
                holder += '{},'.format(i[j_num])
                j_num += 1
            holder += '\n'
        big_holder += holder + '\n'
        holder = ''
    else:
        big_holder += 'EMPTY\n\n'
    if any(passed_wires):
        for i in passed_wires:
            j_num = 0
            for j in i:
                holder += '{},'.format(i[j_num])
                j_num += 1
            holder += '\n'
        big_holder += holder
    else:
        big_holder += 'EMPTY'


def output_to_file():
    global big_holder, blueprint_file
    f = open(blueprint_file, 'w')
    f.write(big_holder)
    f.close()


def Fitness_Collect_From_File():
    global fit_file
    with open(fit_file, 'r') as f:
        return f.readlines()


@timeout.timeout()
def Fitness3_Get(s_gene_code, agent):
    global app_file, blueprint_file, actual_bodys_built, actual_joints_built
    global actual_neurons_built, actual_sensors_built, actual_wires_built
    main(s_gene_code)
    while (not os.path.isfile(blueprint_file)):
        time.sleep(0.2)
    os.system(app_file)
    # Wait_For_Fitness_File(fitFileName)
    while (not os.path.isfile(fit_file)):
        time.sleep(0.2)
    collected_fits = Fitness_Collect_From_File()
    fits = float(collected_fits[0])
    actual_bodys_built = int(collected_fits[1])
    actual_joints_built = int(collected_fits[2])
    actual_sensors_built = int(collected_fits[3])
    actual_neurons_built = int(collected_fits[4])
    actual_wires_built = int(collected_fits[5])
    os.remove(fit_file)
    os.remove(blueprint_file)
    return fits


def calc_noise(prob):
    return -1 * ((prob * math.log(prob, 2)) + (1-prob) * math.log((1-prob), 2))


def set_output_data(gen, agent, fit, g_genecode, s_genecode, bad_run=False):
    global parts_built, genecode_length, genecode_used_length, read_codons
    global regulators_built, total_updates, num_bodys_prepped, data_row
    global development_data, mutation_error, transcription_error
    global actual_bodys_built, actual_joints_built
    global actual_sensors_built, actual_neurons_built, actual_wires_built
    global num_bodys_prepped, num_joints_prepped, num_sensors_prepped
    global num_neurons_prepped, num_wires_prepped, development_data
    if bad_run:
        # IT data
        if (mutation_error > 0):
            mutation_noise = calc_noise(mutation_error)
        else:
            mutation_noise = 0
        if (transcription_error > 0):
            transcription_noise = calc_noise(transcription_error)
        else:
            transcription_noise = 0
        # Genecode
        halfer = int(len(g_genecode) * .5)
        g_genecode_part1 = g_genecode[:halfer]
        g_genecode_part2 = g_genecode[halfer:]
        s_genecode_part1 = s_genecode[:halfer]
        s_genecode_part2 = s_genecode[halfer:]
        data_row = [gen, agent, 0, 0, 0, 0, 0, 0, 0, 0, mutation_noise,
                    transcription_noise, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    g_genecode_part1, g_genecode_part2, s_genecode_part1,
                    s_genecode_part2]
        development_data.append(data_row)
    else:
        # checking for a ridiculous fitness level
        if fit > 9000:
            fit = 0
        # dev data
        genecode_length = len(g_genecode)
        for p in parts_built:
            genecode_used_length += len(p.gene_sequence)
            read_codons += p.codons_read
            regulators_built += p.regulatory_elements
            total_updates += p.num_updates
        # IT data
        if (mutation_error > 0):
            mutation_noise = calc_noise(mutation_error)
        else:
            mutation_noise = 0
        if (transcription_error > 0):
            transcription_noise = calc_noise(transcription_error)
        else:
            transcription_noise = 0
        total_info = .5 * genecode_length   # -(.25 * log(.25, 2)) = .5 bits
        used_info = .5 * genecode_used_length
        # Genecode
        halfer = int(len(g_genecode) * .5)
        g_genecode_part1 = g_genecode[:halfer]
        g_genecode_part2 = g_genecode[halfer:]
        s_genecode_part1 = s_genecode[:halfer]
        s_genecode_part2 = s_genecode[halfer:]
        # output
        data_row = [gen, agent, fit, genecode_length, genecode_used_length,
                    read_codons, regulators_built, total_updates, total_info,
                    used_info, mutation_noise, transcription_noise,
                    num_bodys_prepped, actual_bodys_built, num_joints_prepped,
                    actual_joints_built, num_sensors_prepped,
                    actual_sensors_built, num_neurons_prepped,
                    actual_neurons_built, num_wires_prepped,
                    actual_wires_built, g_genecode_part1, g_genecode_part2,
                    s_genecode_part1, s_genecode_part2]
        development_data.append(data_row)


def select_next_gen(g, p=pops):
    global germ_genomes, development_data
    fit_list = development_data['Fitness'][g*p:(g+1)*p]
    gc_1 = development_data['Gene Code p1'][g*p:(g+1)*p]
    gc_2 = development_data['Gene Code p2'][g*p:(g+1)*p]
    selected = []
    total_fit = 0
    ran = int(round(p * .5))
    for i in range(ran):
        try:
            x = float(fit_list[i])
            if np.isnan(x):
                fit_list[i] = 0
        except ValueError:
            fit_list[i] = 0
    for i in range(ran):
        indy = fit_list.index(max(fit_list))
        # print fit_list[indy]
        new_gc = (gc_1[indy] + gc_2[indy])
        selected.append(tuple([float(fit_list[indy]), new_gc]))
        total_fit += max(fit_list)
        del(fit_list[indy])
        del(gc_1[indy])
        del(gc_2[indy])
    for i in range(ran):
        # contribution = int(round((selected[i][0]/total_fit) * numx))
        # print contribution
        # print i, selected[i][0]
        if(i >= 0 and i < 3):
            germ_genomes[i] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 1] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 2] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 3] = reproduce_with_errors(selected[i][1])
        elif(i >= 3 and i < 9):
            germ_genomes[i] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 1] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 2] = reproduce_with_errors(selected[i][1])
        elif(i >= 9 and i < 18):
            germ_genomes[i] = reproduce_with_errors(selected[i][1])
            germ_genomes[i + 1] = reproduce_with_errors(selected[i][1])
        elif(i >= 18):
            germ_genomes[i] = reproduce_with_errors(selected[i][1])


def select_next_gen2(g, p=pops):
    global germ_genomes, development_data
    fit_list = development_data['Fitness'][g*p:(g+1)*p]
    gc_1 = development_data['Gene Code p1'][g*p:(g+1)*p]
    gc_2 = development_data['Gene Code p2'][g*p:(g+1)*p]
    n_fit_list = [int(round(p * (float(i)/sum(fit_list))))
                  for i in fit_list]
    while sum(n_fit_list) < pops:
        m = max(fit_list)
        ml = [i for i, j in enumerate(fit_list) if j == m]
        mli = random.randrange(0, len(ml))
        n_fit_list[ml[mli]] += 1
        fit_list[ml[mli]] = 0
    count = 0
    for c, e in enumerate(fit_list):
        for j in range(e):
            germ_genomes[count] = reproduce_with_errors(gc_1[c] + gc_2[c])
            count += 1


def grab_genomes(dat_file, p=pops):
    m_data = tablib.Dataset()
    m_data.csv = open(dat_file, 'r').read()
    l1 = m_data['Gene Code p1'][0:p]
    l2 = m_data['Gene Code p2'][0:p]
    for i in range(p):
        l1[i] += l2[i]
    return l1


def grab_one_genome(dat_file, g, a, p=pops):
    m_data = tablib.Dataset()
    m_data.csv = open(dat_file, 'r').read()
    l1 = m_data['Gene Code p1'][g*p + a]
    l1 += m_data['Gene Code p2'][g*p + a]
    return l1


def generate(n):
    string = ''
    for i in range(n):
        char = str(random.randrange(0, 4))
        string += char
    return string


def test(s):
    global parts_developing, sequence_list
    parts_developing, sequence_list = [], []
    sequence_parser(s)
    for i in sequence_list:
        p = Part(i)
        setup_part(p)
    for i in parts_developing:
        i.calculate_capacity()
        i.count_regulators()
        i.init_codons()
    for i in parts_developing:
        print i.capacity
        print i.regulators_per_update


def main(gene_code):
    global germ_genomes
    reset_globals()
    sequence_parser(gene_code)
    for i in sequence_list:
        p = Part(i)
        setup_part(p)
    for i in parts_developing:
        i.calculate_capacity()
        i.count_regulators()
        i.init_codons()
    while(parts_developing):
        for i in parts_developing:
            if i.capacity <= (i.regulatory_elements + i.regulators_per_update):
                # print i, i.regulatory_elements, i.capacity, regulator_pool
                # print "REs:", i.regulatory_elements
                parts_developing.remove(i)
                parts_built.append(i)
            else:
                # print i, i.regulatory_elements, i.capacity, regulator_pool
                i.update()
                i._diffusion()
    setup_blueprints(parts_built)
    format_output()
    # print big_holder
    output_to_file()


def run_one(f='./data/exp/dat/pop9/exp_data2.txt', g=11, a=1):
    d = tablib.Dataset()
    d.csv = open(f, 'r').read()
    gc = d['Gene Code p1'][g*60 + a] + d['Gene Code p2'][g*60 + a]
    return Fitness3_Get(gc, 0)


def gen_runner(pop, gn):
    reset_globals()
    for i in range(pop):
        try:
            agentFit = Fitness3_Get(soma_genomes[i], i)
            set_output_data(gn, i, agentFit, germ_genomes[i], soma_genomes[i])
        except timeout.TimeoutError:
            agentFit = 0
            log_timeouts.append(tuple([gn, i]))
            set_output_data(gn, i, agentFit,
                            germ_genomes[i], soma_genomes[i], True)
        # print i, agentFit


def sensitivity_run():
    global mutation_error, transcription_error, log_timeouts
    global pops, gens, germ_genomes, soma_genomes, development_data
    reset_globals()
    germ_genomes = []
    sl = grab_genomes('/root/sim/python/data/sens/sens_data1.txt')
    for i in range(pops):
        germ_genomes.append(sl[i])
        # germ_genomes.append(generate(18000))
    start_genes = germ_genomes
    for r in range(2,3):
        if r == 0:
            for i in range(5, 51, 5):
                mutation_error = float(i)/10000
                for j in range(5, 51, 5):
                    transcription_error = float(j)/10000
                    development_data = tablib.Dataset()
                    development_data.headers = ['Generation', 'Agent', 'Fitness',
                                                'GeneCode Length',
                                                'GeneCode Length Used', 'Codons Read',
                                                'Regulatory Elements Built',
                                                'Total Updates', 'Total Info',
                                                'Used Info', 'Mutation Noise',
                                                'Transcription Noise', 'Bodys Prepped',
                                                'Bodys Built', 'Joints Prepped',
                                                'Joints Built', 'Sensors Prepped',
                                                'Sensors Built', 'Neurons Prepped',
                                                'Neurons Built', 'Wires Prepped',
                                                'Wires Built', 'Germline Genes p1',
                                                'Germline Genes p2', 'Somaline Genes p1',
                                                'Somaline Genes p2']
                    d = make_data_file('/root/sim/python/data/sens3/')
                    germ_genomes = start_genes
                    print "Testing ME: " + str(mutation_error),
                    print "; TE: " + str(transcription_error)
                    for k in range(gens):
                        for l in range(pops):
                            soma_genomes[l] = transcribe_with_errors(germ_genomes[l])
                        gen_runner(pops, k)
                        # print "Done with generation " + str(i)
                        select_next_gen(k)
                    with open(d, 'w') as f:
                        f.write(development_data.csv)
                    with open('/root/sim/python/data/sens3/log_file.txt', 'a+') as t:
                        t.write('M_Err: {0}; T_Err: {1};--{2}\n'.format(
                            round(mutation_error, 3),
                            round(transcription_error, 3),
                            log_timeouts))
                    log_timeouts = []
        if r == 1:
            for i in range(5, 51, 5):
                mutation_error = float(i)/1000
                for j in range(5, 51, 5):
                    if i == 5 and j <= 35:
                        continue
                    transcription_error = float(j)/1000
                    development_data = tablib.Dataset()
                    development_data.headers = ['Generation', 'Agent', 'Fitness',
                                                'GeneCode Length',
                                                'GeneCode Length Used', 'Codons Read',
                                                'Regulatory Elements Built',
                                                'Total Updates', 'Total Info',
                                                'Used Info', 'Mutation Noise',
                                                'Transcription Noise', 'Bodys Prepped',
                                                'Bodys Built', 'Joints Prepped',
                                                'Joints Built', 'Sensors Prepped',
                                                'Sensors Built', 'Neurons Prepped',
                                                'Neurons Built', 'Wires Prepped',
                                                'Wires Built', 'Germline Genes p1',
                                                'Germline Genes p2', 'Somaline Genes p1',
                                                'Somaline Genes p2']
                    d = make_data_file('/root/sim/python/data/sens2/')
                    print "Testing ME: " + str(mutation_error),
                    print "; TE: " + str(transcription_error)
                    germ_genomes = start_genes
                    for k in range(gens):
                        for l in range(pops):
                            soma_genomes[l] = transcribe_with_errors(germ_genomes[l])
                        gen_runner(pops, k)
                        # print "Done with generation " + str(i)
                        select_next_gen(k)
                    with open(d, 'w') as f:
                        f.write(development_data.csv)
                    with open('/root/sim/python/data/sens2/log_file.txt', 'a+') as t:
                        t.write('M_Err: {0}; T_Err: {1};--{2}\n'.format(
                            round(mutation_error, 3),
                            round(transcription_error, 3),
                            log_timeouts))
                    log_timeouts = []
        if r == 2:
            for i in range(5, 51, 5):
                mutation_error = float(i)/100
                for j in range(5, 51, 5):
                    if i == 5 and j == 5:
                        continue
                    transcription_error = float(j)/100
                    development_data = tablib.Dataset()
                    development_data.headers = ['Generation', 'Agent', 'Fitness',
                                                'GeneCode Length',
                                                'GeneCode Length Used', 'Codons Read',
                                                'Regulatory Elements Built',
                                                'Total Updates', 'Total Info',
                                                'Used Info', 'Mutation Noise',
                                                'Transcription Noise', 'Bodys Prepped',
                                                'Bodys Built', 'Joints Prepped',
                                                'Joints Built', 'Sensors Prepped',
                                                'Sensors Built', 'Neurons Prepped',
                                                'Neurons Built', 'Wires Prepped',
                                                'Wires Built', 'Germline Genes p1',
                                                'Germline Genes p2', 'Somaline Genes p1',
                                                'Somaline Genes p2']
                    d = make_data_file('/root/sim/python/data/sens/')
                    print "Testing ME: " + str(mutation_error),
                    print "; TE: " + str(transcription_error)
                    germ_genomes = start_genes
                    for k in range(gens):
                        for l in range(pops):
                            soma_genomes[l] = transcribe_with_errors(germ_genomes[l])
                        gen_runner(pops, k)
                        # print "Done with generation " + str(i)
                        select_next_gen(k)
                    with open(d, 'w') as f:
                        f.write(development_data.csv)
                    with open('/root/sim/python/data/sens/log_file.txt', 'a+') as t:
                        t.write('M_Err: {0}; T_Err: {1};--{2}\n'.format(
                            round(mutation_error, 3),
                            round(transcription_error, 3),
                            log_timeouts))
                    log_timeouts = []


# Make sure that when you get the start neurons they are the
#    pre-transcribed ones!
# Change slect_next_gen before you run this!
def experimental_run(f):
    global mutation_error, transcription_error, log_timeouts
    global pops, gens, germ_genomes, soma_genomes, development_data
    reset_globals()
    germ_genomes = []
    # sl = grab_genomes('./data/sens/dev_data1.txt')
    for i in range(pops):
        # germ_genomes.append(sl[i])
        germ_genomes.append(generate(18000))
    start_genes = germ_genomes
    sgd = tablib.Dataset()
    sgd.headers = ['Gene Code p1', 'Gene Code p2']
    sgf = './data/pop' + str(f) + '_genes.txt'
    halfer = int(len(start_genes[0]) * .5)
    with open(sgf, 'w+') as wsgf:
        for gc in start_genes:
            sgd.append([gc[:halfer], gc[halfer:]])
        wsgf.write(sgd.csv)
    for i in range(3):
        if i == 0:
            mutation_error = .0005
        if i == 1:
            mutation_error = .003
        if i == 2:
            mutation_error = .0035
        for j in range(3):
            if j == 0:
                transcription_error = .0005
            if j == 1:
                transcription_error = .001
            if j == 2:
                transcription_error = .0025
            development_data = tablib.Dataset()
            development_data.headers = ['Generation', 'Agent', 'Fitness',
                                        'GeneCode Length',
                                        'GeneCode Length Used', 'Codons Read',
                                        'Regulatory Elements Built',
                                        'Total Updates', 'Total Info',
                                        'Used Info', 'Mutation Noise',
                                        'Transcription Noise', 'Bodys Prepped',
                                        'Bodys Built', 'Joints Prepped',
                                        'Joints Built', 'Sensors Prepped',
                                        'Sensors Built', 'Neurons Prepped',
                                        'Neurons Built', 'Wires Prepped',
                                        'Wires Built', 'Gene Code p1',
                                        'Gene Code p2']
            mdf = '/root/sim/python/data/exp/pop' + str(f) + '/'
            df = make_data_file(mdf)
            print "Running Population: " + str(f),
            print "; ME: " + str(mutation_error),
            print "; TE: " + str(transcription_error)
            germ_genomes = start_genes
            soma_genomes = [None] * len(germ_genomes)
            for i in range(gens):
                for j in range(pops):
                    soma_genomes[j] = transcribe_with_errors(germ_genomes[j])
                gen_runner(pops, i)
                print "Done with generation " + str(i)
                select_next_gen(i)
            with open(df, 'w') as wdf:
                wdf.write(development_data.csv)
            lf = '/root/sim/python/data/exp/log_file' + str(f) + '.txt'
            with open(lf, 'w+') as wlf:
                wlf.write('M_Err: {0}; T_Err: {1};--{2}\n'.format(
                    round(mutation_error, 4),
                    round(transcription_error, 4),
                    log_timeouts))
            log_timeouts = []


def exp_wrapper(t=10):
    for i in range(t):
        experimental_run(i)


###############################################################################
# Run the Code
###############################################################################

"""
if __name__ == "__main__":
    exp_wrapper()
"""
