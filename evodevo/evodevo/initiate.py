"""initiate --- A module for

"""
import random

from my_table import table
from part import Part
from subpart import (BodyPart, JointPart, NeuronPart, SensorPart, WirePart)


BUILD_ERROR_RATE = .005


def generate_genomes(num_genomes, num_chars):
    """Returns a 'num_genomes' long list of strings of 0s-3s, each with
       length num_chars.

    """
    germ_genomes = list()
    for i in xrange(num_genomes):
        germ_genomes.append('')
        for j in xrange(num_chars):
            germ_genomes[i] = ''.join((germ_genomes[i],
                                       str(random.randrange(0, 4))))
    return germ_genomes


def add_noise(genome, error_rate=BUILD_ERROR_RATE):
    """Takes a genome, and returns it with some mutation.

    """
    new_gene_code = ''
    for char in genome:
        if (0 < error_rate < random.random()):
            new_gene_code = ''.join((new_gene_code, str(char)))
        else:
            error_bit = (int(char) + random.randrange(1, 4)) % 4
            new_gene_code = ''.join((new_gene_code, str(error_bit)))
    return new_gene_code


def sequence_parser(genome):
    """Takes a genome, splits in into gene_sequences, and returns list."""
    start_ind, stop_ind, started = 0, 0, False
    gene_sequences = list()
    for i in range(0, len(genome), 3):
        triplet = genome[i:i+3]
        cur_codon = table[triplet]
        if (cur_codon == 'START' and not started):
            start_ind = i
            started = True
        elif (cur_codon == 'STOP' and started):
            stop_ind = i+3
            gene_sequences.append(genome[start_ind:stop_ind])
            started = False
    return gene_sequences


def setup_part(part):
    """Takes part to create and return proper subclass object"""
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


def setup_agent(genome):
    """Returns a list containing: 0) a list of proto_parts that constitute
    a pre-developed agent; 1) the genome that generated those parts.
    """
    proto_parts = list()
    building_gene_code = add_noise(genome)
    sequence_list = sequence_parser(building_gene_code)
    for i in sequence_list:
        proto_part = setup_part(Part(i))
        if proto_part is not None:
            proto_parts.append(proto_part)
    for i in proto_parts:
        i.calculate_capacity()
        i.count_regulators()
        i.init_codons()
    return [proto_parts, building_gene_code]
