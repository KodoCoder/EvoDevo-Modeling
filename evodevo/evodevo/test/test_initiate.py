"""
These are not unit-tests per se, as the input of some functions are the
output of other functions.  With this is mind, the tests are ordered to
reflect the order of dependency; that is, tests of dependent function come
after the tests of functions they depend on.
"""
from itertools import izip
import pytest

import evodevo.initiate as edinit
from evodevo.my_table import table
from evodevo.part import Part
from evodevo.subpart import (BodyPart, JointPart, NeuronPart, SensorPart,
                             WirePart)


GENE_CHARS = ('0', '1', '2', '3')


@pytest.fixture
def genome():
    return edinit.generate_genome(18000)


def test_generate_genome(genome):
    """
    Input Info:
        integer; 18000
    Test Criteria:
        generate_genome(num_chars) should return a list with length
        num_chars.  Each character should be a 0--3.
    """
    # genome = edinit.generate_genome(18000)
    assert len(genome) == 18000
    for char in genome:
        assert char in GENE_CHARS


def test_add_noise(genome):
    """
    Input Info:
        string of 0s--3s; output of generate_genome(num_chars)
    Test Criteria:
        add_noise(genome, error_rate) should always return a string the same
        length as the inputted string, and all characters in the outputted
        string should be 0--3.
    """
    # genome = edinit.generate_genome(18000)
    for i in xrange(0, 50, 1):
        new_genome = edinit.add_noise(genome, i/100.)
        assert len(new_genome) == len(genome)
        for char in new_genome:
            assert char in GENE_CHARS


def test_genome_parser(genome):
    """
    Input Info:
        string of 0s--3s; output of add_noise(genome, error_rate)
    Test Criteria:
        genome_parser(genome) returns a list of gene-sequences based on where
        START and STOP codons are.
    """
    # genome = edinit.generate_genome(18000)
    assert len(genome) == 18000
    # Transform genome into list of codons
    codons = [table[genome[i:i+3]] for i in
              xrange(0, len(genome), 3)]
    # Get output from genome_parser(genome) itself
    test_list = edinit.genome_parser(genome)

    # Store indexes of START-STOP codon couples in list
    index_list = list()
    start = False
    start_index = 0
    stop = False
    stop_index = 0
    for index, codon in enumerate(codons):
        if codon == 'START' and not start:
            start = True
            start_index = index
        if codon == 'STOP' and start:
            start = False
            stop = True
            stop_index = index
        if stop:
            stop = False
            index_list.append((start_index, stop_index))
    # Create list of sequences from list of indexes
    sequence_list = [''.join(genome[seq[0]*3:seq[1]*3+3])
                     for seq in index_list]

    assert len(index_list) == len(sequence_list) == len(test_list)
    assert all(seq == test for seq, test in
               izip(sequence_list, test_list))
    for sequence in sequence_list:
        for char in sequence:
            assert char in GENE_CHARS


def test_setup_part():
    """
    Input Info:
        string of 0s--3s; output from item list from genome_parser(genome)
    Test Criteria:
        setup_part(basic_part) should return a part that corresponds to the
        first part-codon found in basic_part's gene_sequence.  If no
        part-codons exits, then None should be returned.
    """
    # Setup Test Cases
    body_sequence1 = ''.join(('112', '000',
                              edinit.generate_genome(102), '222'))
    body_sequence2 = ''.join(('112', '001',
                              edinit.generate_genome(2001), '222'))
    joint_sequence = ''.join(('112', '200',
                              edinit.generate_genome(51), '222'))
    sensor_sequence = ''.join(('112', '100',
                               edinit.generate_genome(12), '222'))
    neuron_sequence = ''.join(('112', '312',
                               edinit.generate_genome(3000), '222'))
    wire_sequence = ''.join(('112', '303',
                             edinit.generate_genome(6000), '222'))
    none_sequence = '112210002302323220123311130131133333231102102111033'
    body_part1 = BodyPart(body_sequence1)
    body_part2 = BodyPart(body_sequence2)
    joint_part = JointPart(joint_sequence)
    sensor_part = SensorPart(sensor_sequence)
    neuron_part = NeuronPart(neuron_sequence)
    wire_part = WirePart(wire_sequence)

    assert edinit.setup_part(body_sequence1) == body_part1
    assert edinit.setup_part(body_sequence2) == body_part2
    assert edinit.setup_part(joint_sequence) == joint_part
    assert edinit.setup_part(sensor_sequence) == sensor_part
    assert edinit.setup_part(neuron_sequence) == neuron_part
    assert edinit.setup_part(wire_sequence) == wire_part
    assert edinit.setup_part(none_sequence) is None
