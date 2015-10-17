""" part --- a class module

"""
import itertools
import math
import numpy as np
from my_table import table

REGULATOR_POOL = [0.] * 40
DIFFUSION_RATE_PULL = .1
DIFFUSION_RATE_PUSH = .05


class Part(object):
    def __init__(self, gene_sequence):
        self.is_developing = True
        self.gene_sequence = gene_sequence
        self.capacity = 0
        self.regulators_per_update = 0
        self.regulatory_elements = 0
        # Turn numbered list of codons into a mapped list of codons
        codon_list_nums = []
        for i in range(0, len(gene_sequence), 3):
            codon_list_nums.append(gene_sequence[i:i+3])
        self.codon_list = [table[i] for i in codon_list_nums].sort()
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
        # BODYREG LIST
        self.index = 0
        self.reg_list = [None] * 15
        # BodyPart REs
        self.reg_size = [0., 0.]  # +/- values
        self.reg_s_num = [0., 0.] 
        self.reg_j_num = [0., 0.]
        self.reg_n_num = [0, 0]
        self.reg_s_loc = [0., 0., 0., 0., 0., 0.]  # pos x,y,z then neg
        self.reg_j_loc = [0., 0., 0., 0., 0., 0.]
        # JointPart REs
        self.reg_active_passive = [0., 0.]
        self.reg_free_rigid = [0., 0.]
        self.reg_upper_lower = [0., 0., 0., 0.]   # upper+/-, then lower...
        self.reg_j_inputs = [0., 0.] 
        # NeuronPart REs
        self.reg_n_inputs = [0., 0.]
        self.reg_n_outputs = [0., 0.]
        # SensorPart REs
        self.reg_s_outputs = [0., 0.]
        # WirePart REs
        self.reg_weight = [0., 0.]
        self.reg_direct = [0., 0.]
        # Data vars
        self.codons_read = 0
        self.num_updates = 0
        self.num_diffuses = 0

    def calculate_capacity(self):
        """Stores the number of REs a part can hold based on its codons."""
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
        else:
            raise TypeError('Only a Part subclass can use this!')

    def count_regulators(self):
        """Stores the total number of regulatory codons."""
        if self.__class__ != Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                if cur_codon[1] == 'R':
                    self.regulators_per_update += 1
        else:
            raise TypeError('Only a Part subclass can use this!')

    def init_codons(self):
        """Stores how many regulatory codons of each type the codon has."""
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
        global REGULATOR_POOL, DIFFUSION_RATE_PUSH
        push_list = []
        # BodyPart REs
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
        # Make push list, modify REGULATOR_POOL, and output list
        o_push_list = [int(math.floor(DIFFUSION_RATE_PUSH * i))
                       for i in push_list]
        REGULATOR_POOL = [i + j for i, j in
                          itertools.izip(REGULATOR_POOL, o_push_list)]
        return o_push_list

    def get_pull_list(self):
        global REGULATOR_POOL, DIFFUSION_RATE_PULL
        # Make pull list, modify REGULATOR_POOL, make sure that
        # REGULATOR_POOL doesn't drop below 0, and output list
        pull_list = [i for i in REGULATOR_POOL]
        o_pull_list = [int(math.floor(DIFFUSION_RATE_PULL * i))
                       for i in pull_list]
        REGULATOR_POOL = [i - j for i, j in
                          itertools.izip(REGULATOR_POOL, o_pull_list)]
        for c, e in enumerate(REGULATOR_POOL):
            if e < 0:
                REGULATOR_POOL[c] = 0
                o_pull_list[c] += e
        return o_pull_list

    def use_phpl_list(self, phpllst):
        """Updates the parts REs based on diffusion rate."""
        # BodyPart REs
        self.reg_size[0] = max(0, self.reg_size[0] + phpllst[0])
        self.reg_size[1] = max(0, self.reg_size[1] + phpllst[1])
        self.reg_s_num[0] = max(0, self.reg_s_num[0] + phpllst[2])
        self.reg_s_num[1] = max(0, self.reg_s_num[1] + phpllst[3])
        self.reg_j_num[0] = max(0, self.reg_j_num[0] + phpllst[4])
        self.reg_j_num[1] = max(0, self.reg_j_num[1] + phpllst[5])
        self.reg_n_num[0] = max(0, self.reg_n_num[0] + phpllst[6])
        self.reg_n_num[1] = max(0, self.reg_n_num[1] + phpllst[7])
        self.reg_s_loc[0] = max(0, self.reg_s_loc[0] + phpllst[8])
        self.reg_s_loc[1] = max(0, self.reg_s_loc[1] + phpllst[9])
        self.reg_s_loc[2] = max(0, self.reg_s_loc[2] + phpllst[10])
        self.reg_s_loc[3] = max(0, self.reg_s_loc[3] + phpllst[11])
        self.reg_s_loc[4] = max(0, self.reg_s_loc[4] + phpllst[12])
        self.reg_s_loc[5] = max(0, self.reg_s_loc[5] + phpllst[13])
        self.reg_j_loc[0] = max(0, self.reg_j_loc[0] + phpllst[14])
        self.reg_j_loc[1] = max(0, self.reg_j_loc[1] + phpllst[15])
        self.reg_j_loc[2] = max(0, self.reg_j_loc[2] + phpllst[16])
        self.reg_j_loc[3] = max(0, self.reg_j_loc[3] + phpllst[17])
        self.reg_j_loc[4] = max(0, self.reg_j_loc[4] + phpllst[18])
        self.reg_j_loc[5] = max(0, self.reg_j_loc[5] + phpllst[19])
        # JointPart REs
        self.reg_active_passive[0] = max(0, self.reg_active_passive[0] +
                                         phpllst[20])
        self.reg_active_passive[1] = max(0, self.reg_active_passive[1] +
                                         phpllst[21])
        self.reg_free_rigid[0] = max(0, self.reg_free_rigid[0] + phpllst[22])
        self.reg_free_rigid[1] = max(0, self.reg_free_rigid[1] + phpllst[23])
        self.reg_upper_lower[0] = max(0, self.reg_upper_lower[0] + phpllst[24])
        self.reg_upper_lower[1] = max(0, self.reg_upper_lower[1] + phpllst[25])
        self.reg_upper_lower[2] = max(0, self.reg_upper_lower[2] + phpllst[26])
        self.reg_upper_lower[3] = max(0, self.reg_upper_lower[3] + phpllst[27])
        self.reg_j_inputs[0] = max(0, self.reg_j_inputs[0] + phpllst[28])
        self.reg_j_inputs[1] = max(0, self.reg_j_inputs[1] + phpllst[29])
        # NeuronPart REs
        self.reg_n_inputs[0] = max(0, self.reg_n_inputs[0] + phpllst[30])
        self.reg_n_inputs[1] = max(0, self.reg_n_inputs[1] + phpllst[31])
        self.reg_n_outputs[0] = max(0, self.reg_n_outputs[0] + phpllst[32])
        self.reg_n_outputs[1] = max(0, self.reg_n_outputs[1] + phpllst[33])
        # SensorPart REs
        self.reg_s_outputs[0] = max(0, self.reg_s_outputs[0] + phpllst[34])
        self.reg_s_outputs[1] = max(0, self.reg_s_outputs[1] + phpllst[35])
        # WirePart REs
        self.reg_weight[0] = max(0, self.reg_weight[0] + phpllst[36])
        self.reg_weight[1] = max(0, self.reg_weight[1] + phpllst[37])
        self.reg_direct[0] = max(0, self.reg_direct[0] + phpllst[38])
        self.reg_direct[1] = max(0, self.reg_direct[1] + phpllst[39])

    def _diffusion(self):
        """Wrapper for diffusion sub_methods.
        
        Uses get_pull_list(), get_push_list(), and use_phpl_list(),
        with added check that class-instance regulatory_elements
        doesn't drop below 0. """ 
        pllst = self.get_pull_list()
        phlst = self.get_push_list()
        phpllst = [i - j for i, j in itertools.izip(phlst, pllst)]
        self.use_phpl_list(phpllst)
        self.regulatory_elements = max(0, self.regulatory_elements +
                                       sum(phpllst))

    def _update(self):
        """Adds one RE for each codon of each type the part has

        Also increases num_updates class-instance."""
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
