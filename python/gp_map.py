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
################################################################

# Headers
################################################################


import pdb 
import os
import random
import time
import math
import tablib
import numpy as np
#import matplotlib.pyplot as plt
from my_table import table


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

#s codons
# body
#total_bp_sphere = 0
#total_bp_cube = 0
total_br_size = [0, 0] 
total_br_s_num = [0, 0] # +1
total_br_j_num = [0, 0] # +1
total_br_n_num = [0, 0] # +1
total_br_s_loc = [0, 0, 0, 0, 0, 0]
total_br_j_loc = [0, 0, 0, 0, 0, 0] #22 + 3
# joint
#total_jp_hinge = 0
total_jr_inputs = [0, 0]
total_jr_active = [0, 0]
total_jr_free = [0, 0]
total_jr_upper = [0, 0]
total_jr_lower = [0, 0] #11 
# neurons
#total_np_neuron = 0
total_nr_inputs = [0, 0] # +1
total_nr_outputs = [0, 0] #5 + 2
# sensor
#total_sp_touch = 0
total_sr_outputs = [0, 0] #3 + 1
# wire
#total_wp_wire = 0
total_wr_weight = [0, 0] 
total_wr_direct = [0, 0] #5
# capacity
total_rc_30 = 0
total_rc_40 = 0
total_rc_50 = 0
total_rc_60 = 0
total_rc_70 = 0
total_rc_80 = 0
total_rc_90 = 0
total_rc_100 = 0
total_rc_110 = 0
total_rc_120 = 0 #10
# syntax/junk
#total_start = 0
#total_stop = 0 #2
total_junk = 0
total_regulators = 0

# diffusion (not based on time of development at all)
diffusion_rate = .0005

# Error Vars
# [0,1) ; the higher the more chance of error
mutation_error = .000
transcription_error = .000
mut_not_err = 1 - mutation_error
tran_not_err = 1 - transcription_error

# File Vars
blueprint_file = './blueprint.dat'
fit_file = './fits.dat'
#app_file = '/home/josh/Documents/projects/thesis/coding/trial/bullet_physics/app'
app_file = '../c++/app'
data_file = './data/sens/dev_data1.txt'

def make_data_file():
    global data_file
    the_file = data_file
    count = 1
    while (os.path.isfile(the_file)):
        index = the_file.find('.txt')
        if (count <= 10):
            #num = int(data_file[index-1])
            the_file = the_file[:index-1] + str(count) + the_file[index:]
        elif (count > 10 and count < 100):
            #num = int(data_file[index-2:index-1])
            the_file = the_file[:index-2] + str(count) + the_file[index:]
            
        count += 1
        #print data_file, count#, num
    return the_file   

def make_sub_file():
    global data_file
    the_file = data_file
    count = 1
    while (os.path.isfile(the_file)):
        index = the_file.find('/dev')
        if (count==1):
            the_file = the_file[:index] + '/' + str(count) + the_file[index:]
        elif (count > 1 and count <= 10):
            #num = int(data_file[index-1])
            the_file = the_file[:index-2] + '/' + str(count) + the_file[index:]
        elif (count > 10 and count < 100):
            #num = int(data_file[index-2:index-1])
            the_file = the_file[:index-3] + '/' + str(count) + the_file[index:]
            
        count += 1
        #print data_file, count#, num
    return the_file    

# HillClimber Vars
gens = 10
fits = np.zeros((1,gens+1))
fits = fits[0]
parentFitness = np.zeros((1,gens+2))
parentFitness = parentFitness[0]
#parentSequence = ''
childFitness = np.zeros((1,gens+2))
childFitness = childFitness[0]

#childSequence = ''

# Data Vars
genecode_length = 0
genecode_used_length = 0
num_bodys_prepped = 0
actual_bodys_built = 0
num_joints_prepped = 0
actual_joints_built = 0
num_sensors_prepped = 0
actual_sensors_built = 0
num_neurons_prepped = 0
actual_neurons_builts = 0
num_wires_prepped = 0
actual_wires_built = 0
read_codons = 0
regulators_built = 0
total_updates = 0

#RESET FUNCTION
def reset_globals():
    global sequence_list, parts_developing, parts_diffusing, parts_built, passed_bodys, passed_joints, passed_neurons, passed_sensors, passed_sensors, passed_wires, big_holder, genecode_length, genecode_used_length, num_bodys_prepped, actual_bodys_built, num_joints_prepped, actual_joints_built, num_neurons_prepped, actual_neurons_builts, num_sensors_prepped, actual_sensors_built, num_wires_prepped, actual_wires_built, read_codons, regulators_built, total_updates, data_file
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
    # Data Vars
    genecode_length = 0
    genecode_used_length = 0
    num_bodys_prepped = 0
    actual_bodys_built = 0
    num_joints_prepped = 0
    actual_joints_built = 0
    num_sensors_prepped = 0
    actual_sensors_built = 0
    num_neurons_prepped = 0
    actual_neurons_builts = 0
    num_wires_prepped = 0
    actual_wires_built = 0
    read_codons = 0
    regulators_built = 0
    total_updates = 0
    data_file = './data/sens/dev_data1.txt'

# Functions
################################################################

testx = "122303123333222"

#testy = generate(18000)

class Part(object):
    def __init__(self, gene_sequence):
        self.is_developing = True
        self.gene_sequence = gene_sequence #Also a data var via len(this)
        self.capacity = 0
        self.regulators_per_update = 0
        self.regulatory_elements = 0 #Also a data var 
        self.blueprint = []
       # BodyPart Codons
        self.codon_size = [0, 0] # +/- codons
        self.codon_s_num = [0, 0]
        self.codon_j_num = [0, 0]
        self.codon_n_num = [0, 0]
        self.codon_s_loc = [0, 0, 0, 0, 0, 0] # pos x,y,z then neg x,y,z
        self.codon_j_loc = [0, 0, 0, 0, 0, 0]
        # JointPart Codons
        self.codon_active_passive = [0, 0]
        self.codon_free_rigid = [0, 0]
        self.codon_upper_lower = [0, 0, 0, 0] #upper+/-, lower +/-
        self.codon_j_inputs = [0, 0]
        # NeuronPart Codons
        self.codon_n_inputs = [0, 0]
        self.codon_n_outputs = [0, 0]
        #self.codon_hidden = [0, 0]
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
        # Data vars
        self.codons_read = 0
        self.num_updates = 0
        self.num_diffuses = 0

    def calculate_capacity(self):
        if self.__class__!=Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                if cur_codon=='RC+30':
                    self.rc30 += 1
                    self.capacity += 30
                elif cur_codon=='RC+40':
                    self.rc40 += 1
                    self.capacity += 40
                elif cur_codon=='RC+50':
                    self.rc50 += 1
                    self.capacity += 50
                elif cur_codon=='RC+60':
                    self.rc60 += 1
                    self.capacity += 60
                elif cur_codon=='RC+70':
                    self.rc70 += 1
                    self.capacity += 70
                elif cur_codon=='RC+80':
                    self.rc80 += 1
                    self.capacity += 80
                elif cur_codon=='RC+90':
                    self.rc90 += 1
                    self.capacity += 90
                elif cur_codon=='RC+100':
                    self.rc100 += 1
                    self.capacity += 100
                elif cur_codon=='RC+110':
                    self.rc110 += 1
                    self.capacity += 110
                elif cur_codon=='RC+120':
                    self.rc120 += 1
                    self.capacity += 120
        else:
            raise TypeError('Only a Part subclass can use this!')

    def count_regulators(self):
        if self.__class__!=Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                if cur_codon[1]=='R':
                    self.regulators_per_update += 1
        else:
             raise TypeError('Only a Part subclass can use this!')

    def init_codons(self):
        if self.__class__!=Part:
            for i in range(0, len(self.gene_sequence), 3):
                cur_codon = table[self.gene_sequence[i:i+3]]
                #print cur_codon,
                self.codons_read += 1
                #BodyPart Codons
                if cur_codon=='BR_SIZE+':
                    self.codon_size[0] += 1
                elif cur_codon=='BR_SIZE-':
                    self.codon_size[1] += 1
                    
                elif cur_codon=='BR_S_M+':
                    self.codon_s_num[0] += 1
                elif cur_codon=='BR_S_M-':
                    self.codon_s_num[1] += 1
                    
                elif cur_codon=='BR_J_M+':
                    self.codon_j_num[0] += 1
                elif cur_codon=='BR_J_M-':
                    self.codon_j_num[1] += 1
                
                elif cur_codon=='BR_N_M+':
                    self.codon_n_num[0] += 1
                elif cur_codon=='BR_N_M-':
                    self.codon_n_num[1] += 1
                
                elif cur_codon=='BR_S_X+':
                    self.codon_s_loc[0] += 1
                elif cur_codon=='BR_S_X-':
                    self.codon_s_loc[3] += 1
                elif cur_codon=='BR_S_Y+':
                    self.codon_s_loc[1] += 1
                elif cur_codon=='BR_S_Y-':
                    self.codon_s_loc[4] += 1
                elif cur_codon=='BR_S_Z+':
                    self.codon_s_loc[2] += 1
                elif cur_codon=='BR_S_Z-':
                    self.codon_s_loc[5] += 1
                
                elif cur_codon=='BR_J_X+':
                    self.codon_j_loc[0] += 1
                elif cur_codon=='BR_J_X-':
                    self.codon_j_loc[3] += 1
                elif cur_codon=='BR_J_Y+':
                    self.codon_j_loc[1] += 1
                elif cur_codon=='BR_J_Y-':
                    self.codon_j_loc[4] += 1
                elif cur_codon=='BR_J_Z+':
                    self.codon_j_loc[2] += 1
                elif cur_codon=='BR_J_Z-':
                    self.codon_j_loc[5] += 1

                # JointPart Codons
                elif cur_codon=='JR_AP+':
                    self.codon_active_passive[0] += 1
                elif cur_codon=='JR_AP-':
                    self.codon_active_passive[1] += 1
                elif cur_codon=='JR_FR+':
                    self.codon_free_rigid[0] += 1
                elif cur_codon=='JR_FR-':
                    self.codon_free_rigid[1] += 1
                elif cur_codon=='JR_U+':
                    self.codon_upper_lower[0] += 1
                elif cur_codon=='JR_U-':
                    self.codon_upper_lower[1] += 1
                elif cur_codon=='JR_L+':
                    self.codon_upper_lower[2] += 1
                elif cur_codon=='JR_L-':
                    self.codon_upper_lower[3] += 1
                elif cur_codon=='JR_I+':
                    self.codon_j_inputs[0] += 1
                elif cur_codon=='JR_I-':
                    self.codon_j_inputs[1] += 1
                
                # NeuronPart Codons
                elif cur_codon=='NR_I+':
                    self.codon_n_inputs[0] += 1
                elif cur_codon=='NR_I-':
                    self.codon_n_inputs[1] += 1
                elif cur_codon=='NR_O+':
                    self.codon_n_outputs[0] += 1
                elif cur_codon=='NR_O-':
                    self.codon_n_outputs[1] += 1
                    #elif cur_codon=='NR_H+':
                    #   self.codon_hidden[0] += 1
                    #elif cur_codon=='NR_H-':
                    #   self.codon_hidden[1] += 1
                    # SensorPart Codons 
                elif cur_codon=='SR_O+':
                    self.codon_s_outputs[0] += 1
                elif cur_codon=='SR_O-':
                    self.codon_s_outputs[1] += 1

                # WirePart Codons
                elif cur_codon=='WR_W+':
                    self.codon_weight[0] += 1
                elif cur_codon=='WR_W-':
                    self.codon_weight[1] += 1
                elif cur_codon=='WR_D+':
                    self.codon_direct[0] += 1
                elif cur_codon=='WR_D-':
                    self.codon_direct[1] += 1

                # Everything else
                elif cur_codon[1]=='P' or cur_codon[0]=='R' or cur_codon[1]=='T':# or cur_codon=='S':
                    self.codon_junk += 1
                else: 
                    raise KeyError('Take a look at your Table!')
        else:
            raise TypeError('Only a Part subclass can use this!')

    def codon_totals(self):
        global total_br_size, total_br_s_num, total_br_j_num, total_br_n_num, total_br_s_loc, total_br_j_loc, total_jr_inputs, total_jr_active, total_jr_free, total_jr_upper, total_jr_lower, total_nr_inputs, total_nr_outputs, total_sr_outputs, total_wr_weight, total_wr_direct, total_rc_30, total_rc_40, total_rc_50, total_rc_60, total_rc_70, total_rc_80, total_rc_90, total_rc_100, total_rc_110, total_rc_120, total_junk, total_regulators
        # body
        #total_bp_sphere += 
        #total_bp_cube +=
        total_br_size[0] += self.codon_size[0] 
        total_br_size[1] += self.codon_size[1]
        total_br_s_num[0] += self.codon_s_num[0]
        total_br_s_num[1] += self.codon_s_num[1]
        total_br_j_num[0] += self.codon_j_num[0]
        total_br_j_num[1] += self.codon_j_num[1]
        total_br_n_num[0] += self.codon_n_num[0]
        total_br_n_num[1] += self.codon_n_num[1]
        total_br_s_loc[0] += self.codon_s_loc[0]
        total_br_s_loc[1] += self.codon_s_loc[1]
        total_br_s_loc[2] += self.codon_s_loc[2]
        total_br_s_loc[3] += self.codon_s_loc[3]
        total_br_s_loc[4] += self.codon_s_loc[4]
        total_br_s_loc[5] += self.codon_s_loc[5]
        total_br_j_loc[0] += self.codon_j_loc[0]
        total_br_j_loc[1] += self.codon_j_loc[1]
        total_br_j_loc[2] += self.codon_j_loc[2]
        total_br_j_loc[3] += self.codon_j_loc[3]
        total_br_j_loc[4] += self.codon_j_loc[4]
        total_br_j_loc[5] += self.codon_j_loc[5]
        # joint
        #total_jp_hinge += 
        total_jr_inputs[0] += self.codon_j_inputs[0]
        total_jr_inputs[1] += self.codon_j_inputs[1]
        total_jr_active[0] += self.codon_active_passive[0]
        total_jr_active[1] += self.codon_active_passive[1]
        total_jr_free[0] += self.codon_free_rigid[0]
        total_jr_free[1] += self.codon_free_rigid[1]
        total_jr_upper[0] += self.codon_upper_lower[0]
        total_jr_upper[1] += self.codon_upper_lower[1]
        total_jr_lower[0] += self.codon_upper_lower[2]
        total_jr_lower[1] += self.codon_upper_lower[3]
        # neurons
        #total_np_neuron +=
        total_nr_inputs[0] += self.codon_n_inputs[0]
        total_nr_inputs[1] += self.codon_n_inputs[1]
        total_nr_outputs[0] += self.codon_n_outputs[0]
        total_nr_outputs[1] += self.codon_n_outputs[1]
        # sensor
        #total_sp_touch +=
        total_sr_outputs[0] += self.codon_s_outputs[0]
        total_sr_outputs[1] += self.codon_s_outputs[1]
        # wire
        #total_wp_wire += 
        total_wr_weight[0] += self.codon_weight[0]
        total_wr_weight[1] += self.codon_weight[1]
        total_wr_direct[0] += self.codon_direct[0]
        total_wr_direct[1] += self.codon_direct[1]      
        # capacity
        total_rc_30 += self.rc30
        total_rc_40 += self.rc40
        total_rc_50 += self.rc50
        total_rc_60 += self.rc60
        total_rc_70 += self.rc70
        total_rc_80 += self.rc80
        total_rc_90 += self.rc90
        total_rc_100 += self.rc100
        total_rc_110 += self.rc110
        total_rc_120 += self.rc120
        # junk
        total_junk += self.codon_junk 
        # total
        total_regulators += self.regulators_per_update

class BodyPart(Part):
    def __init__(self, gene_sequence, kind):
        Part.__init__(self, gene_sequence)
        self.kind = kind
        
        self.reg_size = [0, 0] # just adding and subtracting to keep one number
        self.reg_s_num = [0., 0.] # +/- values
        self.reg_j_num = [0., 0.]
        self.reg_n_num = [0, 0]
        
        self.reg_s_loc = [0., 0., 0.] #x,y,z values 
        self.reg_j_loc = [0., 0., 0.]  

        self.s_mount_loc = []
        self.s_mount_num = 0
        self.j_mount_loc = []
        self.j_mount_num = 0

    def update(self):
        self.num_updates += 1

        self.reg_size[0] += self.codon_size[0] 
        self.reg_size[1] += self.codon_size[1]
        self.reg_s_num[0] += self.codon_s_num[0]
        self.reg_s_num[1] += self.codon_s_num[1]
        self.reg_j_num[0] += self.codon_j_num[0]
        self.reg_j_num[1] += self.codon_j_num[1]
        self.reg_n_num[0] += self.codon_n_num[0]
        self.reg_n_num[1] += self.codon_n_num[1]

        self.reg_s_loc[0] += (self.codon_s_loc[0] - self.codon_s_loc[3]) 
        self.reg_s_loc[1] += (self.codon_s_loc[1] - self.codon_s_loc[4])
        self.reg_s_loc[2] += (self.codon_s_loc[2] - self.codon_s_loc[5])
        self.reg_j_loc[0] += (self.codon_j_loc[0] - self.codon_j_loc[3])
        self.reg_j_loc[1] += (self.codon_j_loc[1] - self.codon_j_loc[4])
        self.reg_j_loc[2] += (self.codon_j_loc[2] - self.codon_j_loc[5])

        # Store last runs sensor and joint mount numbers
        old_s_num, old_j_num = self.s_mount_num, self.j_mount_num
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
        
        # If there's a change in amount of mounts, append a normalized location vector
        #diff1 = self.s_mount_num - old_s_num
        if ((self.s_mount_num - old_s_num) >= 1):
            norm = math.sqrt(self.reg_s_loc[0]**2 + self.reg_s_loc[1]**2 + self.reg_s_loc[2]**2)
            try:
                location = [self.reg_s_loc[0]/norm, self.reg_s_loc[1]/norm, self.reg_s_loc[2]/norm]
            except ZeroDivisionError:
                location = [0., 0., 0.]
            self.s_mount_loc.append(location)
            #diff1 -= 1

        #diff2 = self.j_mount_num - old_j_num
        if ((self.j_mount_num - old_j_num) >= 1):
            norm = math.sqrt(self.reg_j_loc[0]**2 + self.reg_j_loc[1]**2 + self.reg_j_loc[2]**2)
            try:
                location = [self.reg_j_loc[0]/norm, self.reg_j_loc[1]/norm, self.reg_j_loc[2]/norm]
            except ZeroDivisionError:
                location = [0., 0., 0.]
            self.j_mount_loc.append(location)
            #diff2 -= 1

        self.regulatory_elements += self.regulators_per_update

    def diffuse_codons(self):
        global total_br_size, total_br_s_num, total_br_j_num, total_br_n_num, total_br_s_loc, total_br_j_loc, total_junk, total_regulators
        nu = self.num_updates
        self.regulatory_elements -= math.floor(self.regulatory_elements*diffusion_rate*nu)
        #acc = 0
        if nu==0:
            pass
        else:
            while (self.regulatory_elements <= self.capacity):
                self.num_diffuses += 1
            
                self.reg_size[0] += total_br_size[0] * nu
                #acc += total_br_size[0]
                self.reg_size[1] += total_br_size[1] * nu
                #acc += total_br_size[1]
                self.reg_s_num[0] += total_br_s_num[0] * nu
                #acc += total_br_s_num[0]
                self.reg_s_num[1] += total_br_s_num[1] * nu
                #acc += total_br_s_num[1]
                self.reg_j_num[0] += total_br_j_num[0] * nu
                #acc += total_br_j_num[0]
                self.reg_j_num[1] += total_br_j_num[1] * nu
                #acc += total_br_j_num[1]
                self.reg_n_num[0] += total_br_n_num[0] * nu
                #acc += total_br_n_num[0]
                self.reg_n_num[1] += total_br_n_num[1] * nu
                #acc += total_br_n_num[1]
            
                self.reg_s_loc[0] += (total_br_s_loc[0] - total_br_s_loc[3]) * nu
                #acc +=  (total_br_s_loc[0] + total_br_s_loc[3])
                self.reg_s_loc[1] += (total_br_s_loc[1] - total_br_s_loc[4]) * nu
                #acc +=  (total_br_s_loc[1] + total_br_s_loc[4])
                self.reg_s_loc[2] += (total_br_s_loc[2] - total_br_s_loc[5]) * nu
                #acc +=  (total_br_s_loc[2] + total_br_s_loc[5])
                self.reg_j_loc[0] += (total_br_j_loc[0] - total_br_j_loc[3]) * nu
                #acc +=  (total_br_j_loc[0] + total_br_j_loc[3])
                self.reg_j_loc[1] += (total_br_j_loc[1] - total_br_j_loc[4]) * nu
                #acc +=  (total_br_j_loc[1] + total_br_j_loc[4])
                self.reg_j_loc[2] += (total_br_j_loc[2] - total_br_j_loc[5]) * nu
                #acc +=  (total_br_j_loc[2] + total_br_j_loc[5])

                # Store last runs sensor and joint mount numbers
                old_s_num, old_j_num = self.s_mount_num, self.j_mount_num
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
        
                # If there's a change in amount of mounts, append a normalized location vector
                if ((self.s_mount_num - old_s_num) >= 1):
                    norm = math.sqrt(self.reg_s_loc[0]**2 + self.reg_s_loc[1]**2 + self.reg_s_loc[2]**2)
                    try:
                        location = [self.reg_s_loc[0]/norm, self.reg_s_loc[1]/norm, self.reg_s_loc[2]/norm]
                    except ZeroDivisionError:
                        location = [0., 0., 0.]
                    self.s_mount_loc.append(location)
                if ((self.j_mount_num - old_j_num) >= 1):
                    norm = math.sqrt(self.reg_j_loc[0]**2 + self.reg_j_loc[1]**2 + self.reg_j_loc[2]**2)
                    try:
                        location = [self.reg_j_loc[0]/norm, self.reg_j_loc[1]/norm, self.reg_j_loc[2]/norm]
                    except ZeroDivisionError:
                        location = [0., 0., 0.]
                    self.j_mount_loc.append(location)

                #acc += total_junk
                #self.regulatory_elements += acc
                self.regulatory_elements += total_regulators * nu
                #acc = 0
            self.reg_size[0] = math.floor(self.reg_size[0])
            self.reg_size[1] = math.floor(self.reg_size[1])
            self.reg_j_num[0] = math.floor(self.reg_j_num[0])
            self.reg_j_num[1] = math.floor(self.reg_j_num[1])
            self.reg_n_num[0] = math.floor(self.reg_n_num[0])
            self.reg_n_num[1] = math.floor(self.reg_n_num[1])
            self.reg_s_num[0] = math.floor(self.reg_s_num[0])
            self.reg_s_num[0] = math.floor(self.reg_s_num[1])
            self.reg_j_loc[0] = math.floor(self.reg_j_loc[0])
            self.reg_j_loc[1] = math.floor(self.reg_j_loc[1])
            self.reg_j_loc[2] = math.floor(self.reg_j_loc[2])
            self.reg_s_loc[0] = math.floor(self.reg_s_loc[0])
            self.reg_s_loc[1] = math.floor(self.reg_s_loc[1])
            self.reg_s_loc[2] = math.floor(self.reg_s_loc[2])
            self.regulatory_elements = math.floor(self.regulatory_elements)
          
    
    def get_blueprint(self):
        """Returns final measurements for BodyPart.

        This includes: One size measure (radius); One mass measure (based on size);
        1 neuron-mount amount; 1 sensor-mount list (paired with location); 
        1 joint-mount list (paired with location);""" 
        size = 1 + .2 * (self.reg_size[0] - self.reg_size[1])
        if size < .5:
            size = .5
        # Mass will be calculated in BP
        #density = .23866348448
        #if self.kind=='sphere':
        #    mass = density * (4*math.pi/3) * size**3
        #elif self.kind=='cube':
        #    mass = density * (size*2)**3

        #Resize mounts based on number of locs registered
        joint_mounts = len(self.j_mount_loc)

        #Resize mounts based on size
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
        
        #Resize mounts based on number of locs registered
        sensor_mounts = len(self.s_mount_loc)

        # Abstract sesnor locations
        for m in self.s_mount_loc:
            #figure out max of three, then make a new list out of the info
            pass
        self.blueprint = [self.kind, size, joint_mounts, self.j_mount_loc, neuron_mounts, sensor_mounts, self.s_mount_loc]
        return self.blueprint

class JointPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        
        self.reg_active_passive = [0, 0]
        self.reg_free_rigid = [0, 0] 
        self.reg_upper_lower = [0. , 0. , 0., 0.] # upper+/-, then lower...
        self.reg_inputs = [0, 0]

    def update(self):
        self.num_updates += 1

        self.reg_active_passive[0] += self.codon_active_passive[0]
        self.reg_active_passive[1] += self.codon_active_passive[1]
        self.reg_free_rigid[0] += self.codon_free_rigid[0]
        self.reg_free_rigid[1] += self.codon_free_rigid[1]
        self.reg_upper_lower[0] += self.codon_upper_lower[0]
        self.reg_upper_lower[1] += self.codon_upper_lower[1]
        self.reg_upper_lower[2] += self.codon_upper_lower[2]
        self.reg_upper_lower[3] += self.codon_upper_lower[3]
        self.reg_inputs[0] += self.codon_j_inputs[0]
        self.reg_inputs[1] += self.codon_j_inputs[1]

        self.regulatory_elements += self.regulators_per_update

    def diffuse_codons(self):
        global total_jr_inputs, total_jr_active, total_jr_free, total_jr_upper, total_jr_lower, total_junk, total_regulators
        nu = self.num_updates
        self.regulatory_elements -= math.floor(self.regulatory_elements*diffusion_rate*nu)
        #acc = 0
        if nu==0:
            pass
        else:
            while (self.regulatory_elements <= self.capacity):
                self.num_diffuses += 1

                self.reg_active_passive[0] += total_jr_active[0] * nu
                #acc += total_jr_active[0]
                self.reg_active_passive[1] += total_jr_active[1] * nu
                #acc += total_jr_active[1]
                self.reg_free_rigid[0] += total_jr_free[0] * nu
                #acc += total_jr_free[0]
                self.reg_free_rigid[1] += total_jr_free[1] * nu
                #acc += total_jr_free[1]
                self.reg_upper_lower[0] += total_jr_upper[0] * nu
                #acc += total_jr_upper[0]
                self.reg_upper_lower[1] += total_jr_upper[1] * nu
                #acc += total_jr_upper[1]
                self.reg_upper_lower[2] += total_jr_lower[0] * nu
                #acc += total_jr_lower[0]
                self.reg_upper_lower[3] += total_jr_lower[1] * nu
                #acc += total_jr_lower[1]
                self.reg_inputs[0] += total_jr_inputs[0] * nu
                #acc += total_jr_inputs[0]
                self.reg_inputs[1] += total_jr_inputs[1] * nu
                #acc += total_jr_inputs[1]

                #acc += total_junk
                #self.regulatory_elements += acc
                self.regulatory_elements += total_regulators * nu
                #acc = 0
            self.reg_active_passive[0] = math.floor(self.reg_active_passive[0])
            self.reg_active_passive[1] = math.floor(self.reg_active_passive[1])
            self.reg_free_rigid[0] = math.floor(self.reg_free_rigid[0])
            self.reg_free_rigid[1] = math.floor(self.reg_free_rigid[1])
            self.reg_upper_lower[0] = math.floor(self.reg_upper_lower[0])
            self.reg_upper_lower[1] = math.floor(self.reg_upper_lower[1])
            self.reg_inputs[0] = math.floor(self.reg_inputs[0])
            self.reg_inputs[1] = math.floor(self.reg_inputs[1])
            self.regulatory_elements = math.floor(self.regulatory_elements)

    def get_blueprint(self):
        """Returns final measurements for JointPart
        
        Includes whether joint gets a motor; whether it is free or rigid;
        and one value for each limit in radians (upper/lower)"""
        motor = (self.reg_active_passive[0] - self.reg_active_passive[1]) > 0
        free = (self.reg_free_rigid[0] - self.reg_free_rigid[1]) > 0
        #Normalized angle ranges in radians
        maxi = 2 * math.pi
        mini = -2 * math.pi
        convi = math.pi/180
        try:
            upper_limit = ((30 * (self.reg_upper_lower[0]/self.reg_upper_lower[1]) * convi) - mini)/(maxi-mini)
        except ZeroDivisionError:
            upper_limit = ((30 * (self.reg_upper_lower[0]/1) * convi) - mini)/(maxi-mini)

        try:
            lower_limit = ((30 * (self.reg_upper_lower[2]/self.reg_upper_lower[3]) * convi) - mini)/(maxi-mini)
        except ZeroDivisionError:
            lower_limit = ((30 * (self.reg_upper_lower[2]/1) * convi) - mini)/(maxi-mini)

        inputs = self.reg_inputs[0] - self.reg_inputs[1]
        if inputs < 0:
            inputs = 0
        
        self.blueprint = [motor, free, upper_limit, lower_limit, inputs]
        return self.blueprint


class NeuronPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        
        self.reg_inputs = [0, 0]
        self.reg_outputs = [0, 0]

    def update(self):
        self.num_updates += 1

        self.reg_inputs[0] += self.codon_n_inputs[0]
        self.reg_inputs[1] += self.codon_n_inputs[1]
        self.reg_outputs[0] += self.codon_n_outputs[0]
        self.reg_outputs[1] += self.codon_n_outputs[1]

        self.regulatory_elements += self.regulators_per_update

    def diffuse_codons(self):
        global total_nr_inputs, total_nr_outputs, total_junk, total_regulators
        nu = self.num_updates
        self.regulatory_elements -= math.floor(self.regulatory_elements*diffusion_rate*nu)
        #acc = 0
        if nu==0:
            pass
        else:
            while (self.regulatory_elements <= self.capacity):
                self.num_diffuses += 1
                self.reg_inputs[0] += total_nr_inputs[0] * nu
                #acc += total_nr_inputs[0]
                self.reg_inputs[1] += total_nr_inputs[1] * nu
                #acc += total_nr_inputs[1]
                self.reg_outputs[0] += total_nr_outputs[0] * nu
                #acc += total_nr_outputs[0]
                self.reg_outputs[1] += total_nr_outputs[1] * nu
                #acc += total_nr_outputs[1]
             
                #acc += total_junk
                #self.regulatory_elements += acc
                self.regulatory_elements += total_regulators * nu
                #acc = 0
            self.reg_inputs[0] = math.floor(self.reg_inputs[0])
            self.reg_inputs[1] = math.floor(self.reg_inputs[1])
            self.reg_outputs[0] = math.floor(self.reg_outputs[0])
            self.reg_outputs[1] = math.floor(self.reg_outputs[1])
            self.regulatory_elements = math.floor(self.regulatory_elements)

    def get_blueprint(self):
        """Returns final measurements for NeuronPart

        Includes number of inputs, number of outputs, and whether its
        hidden (whether its outputs can go to motors, or neurons)"""
        try:
            input_slots = round(self.reg_inputs[0]/self.reg_inputs[1])
        except ZeroDivisionError:
            input_slots = round(self.reg_inputs[0]/1)

        try:
            output_slots = round(self.reg_outputs[0]/self.reg_inputs[1])
        except ZeroDivisionError:
            output_slots = round(self.reg_outputs[0]/1)

        #hidden = (self.reg_hidden[0]-self.reg_hidden[1]) > 0

        self.blueprint = [input_slots, output_slots]
        return self.blueprint

class SensorPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        
        self.reg_outputs = [0., 0.]

    def update(self):
        self.num_updates += 1

        self.reg_outputs[0] += self.codon_s_outputs[0]
        self.reg_outputs[1] += self.codon_s_outputs[1]

        self.regulatory_elements += self.regulators_per_update

    def diffuse_codons(self):
        global total_sr_outputs, total_junk, total_regulators
        nu = self.num_updates
        self.regulatory_elements -= math.floor(self.regulatory_elements*diffusion_rate*nu)
        #acc = 0
        if nu==0:
            pass
        else:
            while (self.regulatory_elements <= self.capacity):
                self.num_diffuses += 1
                self.reg_outputs[0] += total_sr_outputs[0] * nu
                #acc += total_sr_outputs[0]
                self.reg_outputs[1] += total_sr_outputs[1] * nu
                #acc += total_sr_outputs[1]
            
                #acc += total_junk
                #self.regulatory_elements += acc
                self.regulatory_elements += total_regulators * nu
                #acc = 0
            self.reg_outputs[0] = math.floor(self.reg_outputs[0])
            self.reg_outputs[1] = math.floor(self.reg_outputs[1])
            self.regulatory_elements = math.floor(self.regulatory_elements)
            
    def get_blueprint(self):
        """Returns final measurements for SensorPart

        This includes: Number of output slots"""
        try:
            output_slots = round(self.reg_outputs[0]/self.reg_outputs[1])
        except ZeroDivisionError:
            output_slots = round(self.reg_outputs[0]/1)
        self.blueprint = [output_slots]
        return self.blueprint

class WirePart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)

        self.reg_weight = 0.
        self.reg_direct = [0, 0]

    def update(self):
        self.num_updates += 1

        self.reg_weight += (self.codon_weight[0] - self.codon_weight[1])
        self.reg_direct[0] += self.codon_direct[0]
        self.reg_direct[1] += self.codon_direct[1]
        
        self.regulatory_elements += self.regulators_per_update

    def diffuse_codons(self):
        global total_wr_weight, total_wr_direct, total_junk, total_regulators
        nu = self.num_updates
        self.regulatory_elements -= math.floor(self.regulatory_elements*diffusion_rate*nu)
        #acc = 0
        if nu==0:
            pass
        else:
            while (self.regulatory_elements <= self.capacity):
                self.num_diffuses += 1

                self.reg_weight += (total_wr_weight[0] - total_wr_weight[1]) * nu
                self.reg_direct[0] += total_wr_direct[0] * nu
                self.reg_direct[1] += total_wr_direct[1] * nu

                self.regulatory_elements += total_regulators * nu
            self.reg_weight = math.floor(self.reg_weight)
            self.reg_direct[0] = math.floor(self.reg_direct[0])
            self.reg_direct[1] = math.floor(self.reg_direct[1])
            self.regulatory_elements = math.floor(self.regulatory_elements)

    def get_blueprint(self):
        """Returns final measurements for WirePart

        Includes weight of connection"""
        weight = math.tanh(self.reg_weight/10.)
        direct = ((self.reg_direct[0] - self.reg_direct[1]) >= 0)

        self.blueprint = [weight, direct]
        return self.blueprint

def codon_diffuse_totals():
        global total_br_size, total_br_s_num, total_br_j_num, total_br_n_num, total_br_s_loc, total_br_j_loc, total_jr_inputs, total_jr_active, total_jr_free, total_jr_upper, total_jr_lower, total_nr_inputs, total_nr_outputs, total_sr_outputs, total_wr_weight, total_wr_direct, total_rc_30, total_rc_40, total_rc_50, total_rc_60, total_rc_70, total_rc_80, total_rc_90, total_rc_100, total_rc_110, total_rc_120, total_junk, total_regulators
        # body
        #total_bp_sphere += 
        #total_bp_cube +=
        total_br_size[0] = diffusion_rate*total_br_size[0]
        total_br_size[1] = diffusion_rate*total_br_size[1]
        total_br_s_num[0] = diffusion_rate*total_br_s_num[0]
        total_br_s_num[1] = diffusion_rate*total_br_s_num[1]
        total_br_j_num[0] = diffusion_rate*total_br_j_num[0]
        total_br_j_num[1] = diffusion_rate*total_br_j_num[1]
        total_br_n_num[0] = diffusion_rate*total_br_n_num[0]
        total_br_n_num[1] = diffusion_rate*total_br_n_num[1]
        total_br_s_loc[0] = diffusion_rate*total_br_s_loc[0]
        total_br_s_loc[1] = diffusion_rate*total_br_s_loc[1]
        total_br_s_loc[2] = diffusion_rate*total_br_s_loc[2]
        total_br_s_loc[3] = diffusion_rate*total_br_s_loc[3]
        total_br_s_loc[4] = diffusion_rate*total_br_s_loc[4]
        total_br_s_loc[5] = diffusion_rate*total_br_s_loc[5]
        total_br_j_loc[0] = diffusion_rate*total_br_j_loc[0]
        total_br_j_loc[1] = diffusion_rate*total_br_j_loc[1]
        total_br_j_loc[2] = diffusion_rate*total_br_j_loc[2]
        total_br_j_loc[3] = diffusion_rate*total_br_j_loc[3]
        total_br_j_loc[4] = diffusion_rate*total_br_j_loc[4]
        total_br_j_loc[5] = diffusion_rate*total_br_j_loc[5]
        # joint
        #total_jp_hinge += 
        total_jr_inputs[0] = diffusion_rate*total_jr_inputs[0]
        total_jr_inputs[1] = diffusion_rate*total_jr_inputs[1]
        total_jr_active[0] = diffusion_rate*total_jr_active[0]
        total_jr_active[1] = diffusion_rate*total_jr_active[1]
        total_jr_free[0] = diffusion_rate*total_jr_free[0]
        total_jr_free[1] = diffusion_rate*total_jr_free[1]
        total_jr_upper[0] = diffusion_rate*total_jr_upper[0]
        total_jr_upper[1] = diffusion_rate*total_jr_upper[1]
        total_jr_lower[0] = diffusion_rate*total_jr_lower[0]
        total_jr_lower[1] = diffusion_rate*total_jr_lower[1]
        # neurons
        #total_np_neuron +=
        total_nr_inputs[0] = diffusion_rate*total_nr_inputs[0]
        total_nr_inputs[1] = diffusion_rate*total_nr_inputs[1]
        total_nr_outputs[0] = diffusion_rate*total_nr_outputs[0]
        total_nr_outputs[1] = diffusion_rate*total_nr_outputs[1]
        # sensor
        #total_sp_touch +=
        total_sr_outputs[0] = diffusion_rate*total_sr_outputs[0]
        total_sr_outputs[1] = diffusion_rate*total_sr_outputs[1]
        # wire
        #total_wp_wire += 
        total_wr_weight[0] = diffusion_rate*total_wr_weight[0]
        total_wr_weight[1] = diffusion_rate*total_wr_weight[1]
        total_wr_direct[0] = diffusion_rate*total_wr_direct[0]
        total_wr_direct[1] = diffusion_rate*total_wr_direct[1]
        # capacity
        total_rc_30 = diffusion_rate*total_rc_30
        total_rc_40 = diffusion_rate*total_rc_40
        total_rc_50 = diffusion_rate*total_rc_50
        total_rc_60 = diffusion_rate*total_rc_60
        total_rc_70 = diffusion_rate*total_rc_70
        total_rc_80 = diffusion_rate*total_rc_80
        total_rc_90 = diffusion_rate*total_rc_90
        total_rc_100 = diffusion_rate*total_rc_100
        total_rc_110 = diffusion_rate*total_rc_110
        total_rc_120 = diffusion_rate*total_rc_120
        # junk
        total_junk = diffusion_rate*total_junk
        # total
        total_regulators = diffusion_rate*total_regulators


def reproduce_with_errors(gene_code):
    """Returns given gene code with some errors.

    Error rate set by variable 'mutation_error'"""
    global mutation_error
    new_gene_code = ''
    for char in gene_code:
        if (mutation_error < random.random()):
            new_gene_code = new_gene_code + str(char)
        else:
            error_bit = (int(char) + random.randrange(1,4)) % 4
            new_gene_code = new_gene_code + str(error_bit)
    return new_gene_code

def sequence_parser(gene_code):
    """Fills variable sequence_list."""
    start, stop, started = 0, 0, False
    global sequence_list, transcription_error
    sequence_list = [] #make sure you start with empty list!
    output_sequence = ''
    for i in range(0, len(gene_code), 3):
        triplet = gene_code[i:i+3]
        if (transcription_error > 0):
            triplet2 = triplet
            triplet = ''
            for j in range(3):
                if (transcription_error < random.random()):
                    triplet += triplet2[j] 
                else:
                    triplet += str((int(triplet2[j]) + random.randrange(1,4)) % 4)
        output_sequence += triplet
        cur_codon = table[triplet]
        if (cur_codon=='START' and not started): 
            start = i   #testerss
            started = True
            #print 'start', i
        elif (cur_codon=='STOP' and started):
            stop = i+3
            #print 'stop', i+3    #tester
            #print 'start', start
            sequence_list = sequence_list + [gene_code[start:stop]]
            started = False
    return output_sequence     #tester

def setup_part(part):
    """Takes part and creates proper subclass object"""
    global parts_developing

    if part.__class__ == Part:
        for i in range(0, len(part.gene_sequence), 3):
            cur_codon = table[part.gene_sequence[i:i+3]]
            if cur_codon=='BP_SPHERE':
                parts_developing.append(BodyPart(part.gene_sequence, 'sphere'))
                break
            elif cur_codon=='BP_CUBE':
                parts_developing.append(BodyPart(part.gene_sequence, 'cube'))
                break
            elif cur_codon=='SP_TOUCH':
                parts_developing.append(SensorPart(part.gene_sequence))
                break
            elif cur_codon=='JP_HINGE':
                parts_developing.append(JointPart(part.gene_sequence))
                break
            elif cur_codon=='WP_WIRE':
                parts_developing.append(WirePart(part.gene_sequence))
                break
            elif cur_codon=='NP_NEURON':
                parts_developing.append(NeuronPart(part.gene_sequence))
                break
    else:
        raise TypeError('Only the base Part class can use this!')

def setup_blueprints(list_of_parts):
    global passed_bodys, passed_joints, passed_neurons, passed_sensors, passed_wires, num_bodys_prepped, num_joints_prepped, num_sensors_prepped, num_neurons_prepped, num_wires_prepped
    b_counter, j_counter, n_counter, s_counter, w_counter = 0,0,0,0,0
    place_counter = 1
    b_max, j_max, n_max, s_max, w_max = 0,0,0,0,0
    #Set max variables
    for i in list_of_parts:
        if i.__class__==BodyPart:
            b_max += 1
        elif i.__class__==JointPart:
            j_max += 1
        elif i.__class__==NeuronPart:
            n_max += 1
        elif i.__class__==SensorPart:
            s_max += 1
        elif i.__class__==WirePart:
            w_max += 1
        else:
            raise TypeError('Look at parts_built!')
    num_bodys_prepped = b_max
    num_joints_prepped = j_max
    num_neurons_prepped = n_max
    num_sensors_prepped = s_max
    num_wires_prepped = w_max
    while(b_counter<b_max):
        for i in list_of_parts:
            if i.__class__==BodyPart:
                passed_bodys[0].append(b_counter)
                for k in i.get_blueprint():
                    passed_bodys[place_counter].append(k)
                    place_counter +=1
                b_counter += 1
                place_counter = 1
    while(j_counter<j_max):
        for i in list_of_parts:
            if i.__class__==JointPart:
                passed_joints[0].append(j_counter)
                for k in i.get_blueprint():
                    passed_joints[place_counter].append(k)
                    place_counter += 1
                j_counter += 1
                place_counter = 1
    while(n_counter<n_max):
        for i in list_of_parts:
            if i.__class__==NeuronPart:
                passed_neurons[0].append(n_counter)
                for k in i.get_blueprint():
                    passed_neurons[place_counter].append(k)
                    place_counter += 1
                n_counter += 1
                place_counter = 1
    while(s_counter<s_max):
        for i in list_of_parts:
            if i.__class__==SensorPart:
                passed_sensors[0].append(s_counter)
                passed_sensors[1].append(i.get_blueprint()[0])
                s_counter += 1
    while(w_counter<w_max):
        for i in list_of_parts:
            if i.__class__==WirePart:
                passed_wires[0].append(w_counter)
                passed_wires[1].append(i.get_blueprint()[0])
                passed_wires[2].append(i.get_blueprint()[1])
                w_counter += 1

def format_output():
    global passed_bodys, passed_joints, passed_neurons, passed_sensors, passed_wires, big_holder
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
                if i_num!=4 and i_num!=7:
                    # print out this quality in order of parts
                    holder += '{},'.format(i[j_num])
                    # if loc list
                else:
                    k_num = 0
                    # go through list
                    for k in j:
                        # if empty
                        if not i[j_num][k_num]:
                            # print  
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

    #print big_holder

def output_to_file():
    global big_holder, blueprint_file
    f = open(blueprint_file, "w")
    f.write(big_holder)
    f.close()

def Fitness_Collect_From_File(n):
    global fit_file
    f = open(fit_file, "r")
    for i in range(n):
        f.readline()
    return f.readline()
    f.close()

def Fitness3_Get(gene_code, generation):
    global app_file, blueprint_file, fits, actual_bodys_built, actual_joints_built, actual_neurons_builts, actual_sensors_built, actual_wires_built
    main(gene_code)
    while (os.path.isfile(blueprint_file) == False):
        time.sleep(0.2)
    os.system(app_file)
    #Wait_For_Fitness_File(fitFileName)
    while (os.path.isfile(fit_file) == False):
        time.sleep(0.2)
    fits[generation] = float(Fitness_Collect_From_File(0))
    actual_bodys_built = int(Fitness_Collect_From_File(1))
    actual_joints_built = int(Fitness_Collect_From_File(2))
    actual_sensors_built = int(Fitness_Collect_From_File(3))
    actual_neurons_builts = int(Fitness_Collect_From_File(4))
    actual_wires_built = int(Fitness_Collect_From_File(5))
    os.remove(fit_file)
    return fits[generation]

def set_output_data(gen, fit, genecode):
    global parts_built, genecode_length, genecode_used_length, read_codons, regulators_built, total_updates, num_bodys_prepped, data_row, development_data, mutation_error, transcription_error, mut_not_err, tran_not_err, actual_bodys_built, actual_joints_built, actual_sensors_built, actual_neurons_builts, actual_wires_built, num_bodys_prepped, num_joints_prepped, num_sensors_prepped, num_neurons_prepped, num_wires_prepped
    # dev data
    genecode_length = len(genecode)
    for p in parts_built:
        genecode_used_length += len(p.gene_sequence)
        read_codons += p.codons_read
        regulators_built += p.regulatory_elements
        total_updates += p.num_updates
    # IF data
    if (mutation_error>0):
        mutation_noise = -1 * ((mutation_error * math.log(mutation_error,2)) + (mut_not_err * math.log(mut_not_err,2)))
    else:
        mutation_noise = 0
    if (transcription_error>0):
        transcription_noise = -1 * ((transcription_error * math.log(transcription_error,2)) + (tran_not_err * math.log(tran_not_err,2)))
    else:
        transcription_noise = 0
    total_info = .5 * genecode_length # -(.25 * log(.25, 2)) = .5 bits 
    used_info = .5 * genecode_used_length
    # Genecode
    halfer = int(len(genecode) *.5)
    genecode_part1 = genecode[:halfer]
    genecode_part2 = genecode[halfer:]
    # output 
    data_row = [gen, fit, genecode_length, genecode_used_length, read_codons, regulators_built, total_updates, total_info, used_info, mutation_noise, transcription_noise, num_bodys_prepped, actual_bodys_built, num_joints_prepped, actual_joints_built, num_sensors_prepped, actual_sensors_built, num_neurons_prepped, actual_neurons_builts, num_wires_prepped, actual_wires_built, genecode_part1, genecode_part2]
    development_data.append(data_row)

def generate(n):
    string = ''
    for i in range(n):
        char = str(random.randrange(0,4))
        string = string + char
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
    #global testx
    #s = generate(18000)
    #s = testx
    reset_globals()
    sequence_parser(gene_code)
    for i in sequence_list:
        p = Part(i)
        setup_part(p)
    for i in parts_developing:
        i.calculate_capacity()
        i.count_regulators()
        i.init_codons()
    #print total_regulators
    while(parts_developing):
        for i in parts_developing:
            if i.capacity <= (i.regulatory_elements + i.regulators_per_update):
                i.codon_totals()
                parts_diffusing.append(i)
                parts_developing.remove(i)
            else:
                i.update()
    #print total_regulators
    codon_diffuse_totals()
    #print total_regulators
    for i in parts_diffusing:
        #print i, i.regulatory_elements, i.capacity, i.num_updates, i.regulators_per_update
        i.diffuse_codons()
        parts_built.append(i)
        #print i, i.regulatory_elements, i.capacity, i.num_diffuses
        #print total_regulators, total_regulators*i.num_updates, total_regulators*i.num_updates*i.num_diffuses
            
    setup_blueprints(parts_built)
    format_output()
    output_to_file()

def HillClimber():
    global gens, parentFitness, childFitness, data_file, testy
    reset_globals()
    global development_data
    development_data = tablib.Dataset()
    development_data.headers = ['Generation', 'Fitness', 'GeneCode Length', 'GeneCode Length Used', 'Codons Read', 'Regulatory Elements Built', 'Total Updates', 'Total Info', 'Used Info', 'Mutation Noise', 'Transcription Noise', 'Bodys Prepped', 'Bodys Built', 'Joints Prepped', 'Joints Built', 'Sensors Prepped', 'Sensors Built', 'Neurons Prepped', 'Neurons Built', 'Wires Prepped', 'Wires Built', 'Gene Code p1', 'GeneCode p2'] 
    parentSequence = generate(18000)
    #parentSequence = testy
    parentFitness[0] = Fitness3_Get(parentSequence, 0)
    parentFitness[1] = parentFitness[0]
    print 0, parentFitness[0], 'NA'
    set_output_data(0, parentFitness[0], parentSequence)    
    for currentGeneration in range (1, gens+1):
        childSequence = reproduce_with_errors(parentSequence)
        childFitness[currentGeneration] = Fitness3_Get(childSequence, currentGeneration)
        #print "Testing It"
        set_output_data(currentGeneration, childFitness[currentGeneration], childSequence)
        print currentGeneration, parentFitness[currentGeneration], childFitness[currentGeneration], parentSequence==childSequence
        #print parentSequence==childSequence
        if (childFitness[currentGeneration] > parentFitness[currentGeneration]):
            parentFitness[currentGeneration + 1] = childFitness[currentGeneration]
            parentSequence = childSequence
        else:
            parentFitness[currentGeneration + 1] = parentFitness[currentGeneration]
    d = make_data_file()
    f = open(d, 'w')
    f.write(development_data.csv)

def sensitivity_run():
    global mutation_error, transcription_error, data_file
    reset_globals()
    while (mutation_error < .06):
        #f = make_sub_file()
        #f = make_data_file()
        mutation_error += .005
        transcription_error += .005
        for i in range (0, 10):
            #f = make_data_file()
            HillClimber()
            print "Done with " + str(i) + " agent"
        print "Done with a generation"

######################## TESTING CODE ##########################################



"""
    for i in passed_bodys:
        print i
        
    for i in passed_joints:
        print i

    for i in passed_neurons:
        print i

    for i in passed_sensors:
        print i

    for i in passed_wires:
        print i
"""
