
# ### Code ###
import random

from my_table import table
from part import Part, BodyPart, JointPart, NeuronPart, SensorPart, WirePart

BUILD_ERROR_RATE = .005

def add_noise(gene_code, error_rate=BUILD_ERROR_RATE):
    """Takes a genome, and returns it with some mutation.
      
    """
    new_gene_code = ''
    for char in gene_code:
        if (0 < error_rate < random.random()):
            new_gene_code = ''.join((new_gene_code, str(char)))
        else:
            error_bit = (int(char) + random.randrange(1, 4)) % 4
            new_gene_code = ''.join((new_gene_code, str(error_bit)))
    return new_gene_code


def sequence_parser(gene_code):
    """Takes a genome, splits in into gene_sequences, and returns list."""
    start_ind, stop_ind, started = 0, 0, False
    gene_sequences = []
    for i in range(0, len(gene_code), 3):
        triplet = gene_code[i:i+3]
        cur_codon = table[triplet]
        if (cur_codon == 'START' and not started):
            start_ind = i
            started = True
        elif (cur_codon == 'STOP' and started):
            stop_ind = i+3
            gene_sequences.append(gene_code[start_ind:stop_ind])
            started = False
    return gene_sequences


def setup_part(part):
    """Takes part and creates proper subclass object"""
    new_part = None
    for i in range(0, len(part.gene_sequence), 3):
        cur_codon = table[part.gene_sequence[i:i+3]]
        if cur_codon == 'BP_SPHERE':
            new_part = BodyPart(part.gene_sequence)
            break
        elif cur_codon == 'SP_TOUCH':
            new_part = SensorPart(part.gene_sequence)
            break
        elif cur_codon == 'JP_HINGE':
            new_part = JointPart(part.gene_sequence)
            break
        elif cur_codon == 'WP_WIRE':
            new_part = WirePart(part.gene_sequence)
            break
        elif cur_codon == 'NP_NEURON':
            new_part = NeuronPart(part.gene_sequence)
            break
        elif i+3 == len(part.gene_sequence):
            break
    return new_part


def setup_agent(gene_code):
    parts_developing = []
    building_gene_code = add_noise(gene_code)
    sequence_list = sequence_parser(building_gene_code)
    for i in sequence_list:
        proto_part = setup_part(Part(i))
        if proto_part is not None:
            parts_developing.append(proto_part)
    for i in parts_developing:
        i.calculate_capacity()
        i.count_regulators()
        i.init_codons()
    return [parts_developing, building_gene_code]
