
# ### Code ###
import itertools
import math
import numpy as np
from collections import namedtuple
from my_table import table

regulator_pool = [0.] * 40
diffusion_rate_pull = .1
diffusion_rate_push = .05


# Generic Part
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
        global regulator_pool, diffusion_rate_push
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
        # Make push list, modify regulator_pool, and output list 
        o_push_list = [int(math.floor(diffusion_rate_push * i))
                       for i in push_list]
        regulator_pool = [i + j for i, j in
                          itertools.izip(regulator_pool, o_push_list)]
        return o_push_list

    def get_pull_list(self):
        global regulator_pool, diffusion_rate_pull
        # Make pull list, modify regulator_pool, make sure that 
        # regulator_pool doesn't drop below 0, and output list
        pull_list = [i for i in regulator_pool]
        o_pull_list = [int(math.floor(diffusion_rate_pull * i))
                       for i in pull_list]
        regulator_pool = [i - j for i, j in
                          itertools.izip(regulator_pool, o_pull_list)]
        for c, e in enumerate(regulator_pool):
            if e < 0:
                regulator_pool[c] = 0
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


# Specific types of parts
class BodyPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        self.j_mount_loc = []
        self.j_mount_num = 0
        self.j_loc_holder = [0., 0., 0.]
        self.s_mount_loc = []
        self.s_mount_num = 0
        self.s_loc_holder = [0., 0., 0.]
        self.Body_Characteristics = namedtuple('Body_Characteristics',
                                               ['size', 'joint_mount_num',
                                                'joint_mount_loc', 'neuron_mount_num',
                                                'sensor_mount_num', 'sensor_mount_loc'])
        self.characteristics = self.Body_Characteristics(0, 0, 0, 0, 0, 0)

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
        # If there's a change in amount of sensor mounts,
        # append a normalized location vector
        if ((self.s_mount_num - old_s_num) >= 1):
            location = np.array([self.s_loc_holder[0],
                                 self.s_loc_holder[1],
                                 self.s_loc_holder[2]], dtype='f')
            # if any(location):
            #     location = location / np.linalg.norm(location)
            #     self.s_mount_loc.append(location)
            if any(location):
                location = location / np.linalg.norm(location)
                if any((location == i).all() or (location == j).all() 
                       for i, j in itertools.izip(self.s_mount_loc,
                                                  self.j_mount_loc)):
                    pass
                else:
                    self.s_mount_loc.append(location)
        # Same for joints
        if ((self.j_mount_num - old_j_num) >= 1):
            location = np.array([self.j_loc_holder[0],
                                 self.j_loc_holder[1],
                                 self.j_loc_holder[2]], dtype='f')
            # if any(location):
            #     location = location / np.linalg.norm(location)
            #     self.j_mount_loc.append(location)
            if any(location):
                location = location / np.linalg.norm(location)
                if any((location == i).all() or (location == j).all()
                       for i, j in itertools.izip(self.s_mount_loc,
                                                  self.j_mount_loc)):
                    pass
                else:
                    self.j_mount_loc.append(location)

    def update(self):
        self._update()
        self.calculate_mount_info()

    def rotate_body(self, orientation):
        """Uniformly rotates all jount and sensor mount locations. 

        The rotation will be by the difference in angle between the
        additive inverse of the orientation vector (which is the
        active jount mount vector of the base part) and the direction
        of the first joint mount of this body."""
        inv_orientation = -1 * orientation
        jm_direction = self.j_mount_loc[0]
        # spherical coordinates are defined by three numbers:
        # r --- radius, will always be one in this code
        # theta --- azimuth angle [0-2pi]  =  atan(y/x)
        # phi --- zenith angle [0-pi]      =  acos(-z/r)
        io_theta = math.atan2(inv_orientation[1], inv_orientation[0])
        io_phi = math.acos(inv_orientation[2])
        jm_theta = math.atan2(jm_direction[1], jm_direction[0])
        jm_phi = math.acos(jm_direction[2])
        diff_theta = (io_theta - jm_theta) % (2 * math.pi)
        diff_phi = (io_phi - jm_phi) % math.pi
        # Calculate rotation matrix
        cos_t, sin_t = math.cos(diff_theta), math.sin(diff_theta)
        cos_p, sin_p = math.cos(diff_phi), math.sin(diff_phi)
        z_matrix = np.array([[cos_t, -1 * sin_t, 0], [sin_t, cos_t, 0],
                             [0, 0, 1]], dtype='f')
        y_matrix = np.array([[cos_p, 0, sin_p], [0, 1, 0], [-1 * sin_p, 0,
                                                            cos_p]], dtype='f')
        rotation_matrix = np.around(z_matrix.dot(y_matrix), 10)
        # Apply rotation matrix
        for i in range(len(self.s_mount_loc)):
            self.s_mount_loc[i] = rotation_matrix.dot(self.s_mount_loc[i])
        for i in range(len(self.j_mount_loc)):
            self.j_mount_loc[i] = rotation_matrix.dot(self.j_mount_loc[i])

    def set_characteristics(self):
        """Returns values for BodyPart characteristics.

        This includes: size measure--(radius); joint mount number;
        joint mount locations; neuron mount number; sensor mount number;
        and sensor mount locations."""
        size = round((1 + .2 * (self.reg_size[0] - self.reg_size[1])), 3)
        if size < .5:
            size = .5
        # Resize joint mounts based on number of locations registered
        joint_mounts = len(self.j_mount_loc)
        # Resize joint mounts based on size
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
        # calculate neuron mounts
        try:
            neuron_mounts = round(self.reg_n_num[0]/self.reg_n_num[1])
        except ZeroDivisionError:
            neuron_mounts = round(self.reg_n_num[0]/1)
        # Resize sensor mounts based on number of locations registered
        sensor_mounts = len(self.s_mount_loc)
        # Create characteristics
        self.characteristics = self.Body_Characteristics(size,
                                                         joint_mounts,
                                                         self.j_mount_loc,
                                                         neuron_mounts,
                                                         sensor_mounts,
                                                         self.s_mount_loc)

    def get_characteristics(self):
        if any(self.characteristics):
            return self.characteristics
        else:
            raise ValueError


class JointPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        self.Joint_Characteristics = namedtuple('Joint_Characteristics',
                                                ['motor', 'free', 'upper_limit',
                                                 'lower_limit', 'input_num'])
        self.characteristics = self.Joint_Characteristics(0, 0, 0, 0, 0)

    def update(self):
        self._update()

    def set_characteristics(self):
        """Returns final values for JointPart characteristics.

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
            upper_limit = math.pi
        try:
            lower_ratio = ((float(self.reg_upper_lower[2]) -
                           self.reg_upper_lower[3]) /
                           (self.reg_upper_lower[2] +
                            self.reg_upper_lower[3]))
            lower_limit = lower_ratio * math.pi
        except ZeroDivisionError:
            lower_limit = -1 * math.pi
        if free:
            pass
        else:
            if (sum(self.reg_upper_lower[:2]) > sum(self.reg_upper_lower[2:])):
                lower_limit = upper_limit
            else:
                upper_limit = lower_limit
        try:
            inputs = int(round(self.reg_j_inputs[0] / self.reg_j_inputs[1]))
        except ZeroDivisionError:
            inputs = int(round(self.reg_j_inputs[0]))
        if inputs < 0:
            inputs = 0
        self.characteristics = self.Joint_Characteristics(motor, free,
                                                          round(upper_limit,
                                                                5),
                                                          round(lower_limit,
                                                                5), inputs)

        def get_characteristics(self):
            if any(self.characteristics):
                return self.characteristics
            else:
                raise ValueError


class NeuronPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        self.Neuron_Characteristics = namedtuple('Neuron_Characteristics',
                                            ['input_num', 'output_num'])
        self.characteristics = self.Neuron_Characteristics(0, 0)

    def update(self):
        self._update()

    def set_characteristics(self):
        """Returns final values for NeuronPart characteristics.

        Includes number of inputs and number of outputs"""
        try:
            input_slots = int(round(self.reg_n_inputs[0] /
                                    self.reg_n_inputs[1]))
        except ZeroDivisionError:
            input_slots = int(round(self.reg_n_inputs[0]))
        try:
            output_slots = int(round(self.reg_n_outputs[0] /
                                     self.reg_n_outputs[1]))
        except ZeroDivisionError:
            output_slots = int(round(self.reg_n_outputs[0]))

        self.characteristics = self.Neuron_Characteristics(input_slots, output_slots)

    def get_characteristics(self):
        if any(self.characteristics):
            return self.characteristics
        else:
            raise ValueError


class SensorPart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        self.Sensor_Characteristics = namedtuple('Sensor_Characteristics',
                                                 ['output_num'])
        self.characteristics = self.Sensor_Characteristics(0)

    def update(self):
        self._update()

    def set_characteristics(self):
        """Returns final values for SensorPart characteristics.

        This includes: Number of output slots"""
        try:
            output_slots = int(round(self.reg_s_outputs[0] /
                                     self.reg_s_outputs[1]))
        except ZeroDivisionError:
            output_slots = int(round(self.reg_s_outputs[0]/1))
        self.characteristics = self.Sensor_Characteristics(output_slots)

    def get_characteristics(self):
        if any(self.characteristics):
            return self.characteristics
        else:
            raise ValueError


class WirePart(Part):
    def __init__(self, gene_sequence):
        Part.__init__(self, gene_sequence)
        self.Wire_Characteristics = namedtuple('Wire_Characteristics',
                                               ['weight', 'to_joint'])
        self.characteristics = self.Wire_Characteristics(0, 0)

    def update(self):
        self._update()

    def set_characteristics(self):
        """Returns final values for WirePart characteristics.

        Includes weight (0,1); and connection preference."""
        connection_weight = math.atan(((self.reg_weight[0] - 
                                        self.reg_weight[1]) /
                                       3.) / (math.pi / 2))
        direct = ((self.reg_direct[0] - self.reg_direct[1]) >= 0)
        self.characteristics = self.Wire_Characteristics(connection_weight,
                                                         direct)

    def get_characteristics(self):
        if any(self.characteristics):
            return self.characteristics
        else:
            raise ValueError
