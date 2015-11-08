import random

from my_table import table
from part import Part
from subpart import (BodyPart, JointPart, NeuronPart, SensorPart, WirePart)


BUILD_ERROR_RATE = .005


def generate_genome(num_chars):
    """
    Returns string of 0s--3s that represents a genome.

    Args:
        num_chars: An integer that determines/equals the length of the returned
                   string.

    Returns:
        germ_genome: A string of 0s--3s.
    """
    germ_genome = ''
    for i in xrange(num_chars):
        germ_genome = ''.join((germ_genome,
                               str(random.randrange(0, 4))))
    return germ_genome


def add_noise(genome, error_rate=BUILD_ERROR_RATE):
    """
    Returns a copy of inputted genomes with some mutation.

    Args:
        genome: A string of 0s--3s, normally taken from the output of
                generate_genome.
        error_rate: A percent (a float) that determines what percentage (on
                    average) of characters of the string get randomly changed.

    Returns:
        new_genome: A mutated copy of the inputted genome. Will always have
                    the same number of characters of inputted genome.
    """
    new_genome = ''
    for char in genome:
        if (0 < error_rate < random.random()):
            new_genome = ''.join((new_genome, str(char)))
        else:
            error_bit = (int(char) + random.randrange(1, 4)) % 4
            new_genome = ''.join((new_genome, str(error_bit)))
    return new_genome


def genome_parser(genome):
    """
    Returns list of gene-sequences that are delimited by START and STOP codons.

    Not used outside this module.

    Args:
        genome: A string of 0s--3s, normally taken from the output of
                add_noise.

    Returns:
        gene_sequences: A list of strings taken from the inputted genome. If
                        the list is empty, then there were no START codon
                        followed by a STOP codon in the inputted genome.
    """
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


def setup_part(part_sequence):
    """
    Returns a specific part subclass object from a gene_sequence.

    The part-type returned is determined by the first part-codon encountered.
    If no part-codon is encountered, then None is returned.
    Not used outside this module.

    Args:
        part_sequence: A string of 0s--3s, normally taken from the list
                      output of genome_parser.

    Returns:
        new_part: An initialized part object.  See part module documentation
                  for more info.
    """
    new_part = None
    for i in range(0, len(part_sequence), 3):
        cur_codon = table[part_sequence[i:i+3]]
        if cur_codon == 'BP_SPHERE':
            new_part = BodyPart(part_sequence)
            break
        elif cur_codon == 'SP_TOUCH':
            new_part = SensorPart(part_sequence)
            break
        elif cur_codon == 'JP_HINGE':
            new_part = JointPart(part_sequence)
            break
        elif cur_codon == 'WP_WIRE':
            new_part = WirePart(part_sequence)
            break
        elif cur_codon == 'NP_NEURON':
            new_part = NeuronPart(part_sequence)
            break
        elif i+3 == len(part_sequence):
            break
    return new_part


def setup_agent(genome):
    """
    Returns a list of proto_parts and the genome that generated those parts.

    Proto-parts are pre-developed, but initialized part objects. Taken as a
    whole, the list proto_parts is the pre-developed agent.

    Args:
        genome: A string of 0s--3s, normally the output of generate_genome.

    Returns:
        proto_parts: a list of part objects.
    """
    proto_parts = list()
    building_gene_code = add_noise(genome)
    sequence_list = genome_parser(building_gene_code)
    for sequence in sequence_list:
        proto_part = setup_part(sequence)
        if proto_part is not None:
            proto_parts.append(proto_part)
    return [proto_parts, building_gene_code]
