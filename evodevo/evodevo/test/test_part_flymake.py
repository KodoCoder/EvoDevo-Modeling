"""
These are not unit-tests per se, as the input of some functions are the
output of other functions.  With this is mind, the tests are ordered to
reflect the order of dependency; that is, tests of dependent function come
after the tests of functions they depend on.
"""
import copy
import itertools
import pytest

from evodevo.my_table import table
import evodevo.part as edpart


@pytest.fixture()
def empty_part():
    """
    This part has no codons except for the start and stop codon.
    """
    return edpart.Part('122222')


@pytest.fixture()
def one_of_each_part():
    """
    This part has one of each codon. It's only copies of syntax codons are its
    own START at the beginning and STOP at the end.
    """
    gene_seq = '122'
    for i in sorted(iter(table)):
        if i == '122' or i == '222':
            pass
        else:
            gene_seq = ''.join((gene_seq, i))
    gene_seq = ''.join((gene_seq, '222'))
    return edpart.Part(gene_seq)


@pytest.fixture()
def eight_of_eight_parts():
    """
    A list of parts with eight of eight types of codons.
    """
    ret = list()
    gene_seq = '122'
    for c, i in enumerate(sorted(iter(table))):
        if (c+1) % 8 != 0:
            gene_seq = ''.join((gene_seq, i*8))
        else:
            gene_seq = ''.join((gene_seq, i*8, '222'))
            ret.append(edpart.Part(gene_seq))
            gene_seq = '122'
    return ret


@pytest.fixture()
def diffusion_part():
    """
    A part with 20 of each regulatory_element
    """
    gene_seq = '122'
    for i in sorted(set(table.iteritems())):
        if i[1][1] == 'R' and (i[1] not in
                               [table[gene_seq[j:j+3]] for j in
                                xrange(0, len(gene_seq), 3)]):
            gene_seq = ''.join((gene_seq, i[0]*10))
    gene_seq = ''.join((gene_seq, '222'))
    diff_part = edpart.Part(gene_seq)
    diff_part._update()
    diff_part._update()
    return diff_part


def test_init(empty_part, one_of_each_part, eight_of_eight_parts):
    """
    Also tests _init_re_codons(), _calculate_capacity(), _count_regulators()
    """
    # Empty part should have 0 for all attributes, except for other_codons
    # because it has both a START and a STOP codon.
    for i in empty_part.__dict__.iteritems():
        try:
            n = len(i[1])
            if i[0] != 'gene_sequence':
                assert i[1] == [0] * n
        except TypeError:
            if i[0] == 'other_codons':
                assert i[1] == 2
            else:
                assert i[1] == 0
    # One_of_each part should have 1 for most attributes.
    #
    # Codons that determine number of mounts or input/output slots have
    # redundant copies, so they have two positive versions and one negative.
    # Capacity is sum of multiples of ten [30-110].
    # other_codons is 2 for syntax, 9 for RCs, 6 for part-codons: 17 total
    # regulators_per_update is 64 - 17: 47 total
    for i in one_of_each_part.__dict__.iteritems():
        try:
            n = len(i[1])
            if i[0] == 'gene_sequence':
                pass
            elif i[0][:3] != 'reg':
                if i[0][-4:] == '_num' or i[0][-4:] == 'puts':
                    assert i[1] == [2, 1]
                else:
                    assert i[1] == [1] * n
            else:
                assert i[1] == [0] * n
        except TypeError:
            if i[0] == 'capacity':
                assert i[1] == 630
            elif i[0] == 'regulators_per_update':
                assert i[1] == 47
            elif i[0] == 'other_codons':
                assert i[1] == 17
            elif i[0][:2] == 'rc':
                assert i[1] == 1
            else:
                i[1] == 0
    # Eight_of_eight part should have 8 of 8 codons, and 0 for the rest. We're
    # only checking the first part in the set; the part with 8 of each codon
    # [000--013].
    #
    # One of these, codon_s_num, has a redundent positive codon:
    #     [16, 8] : generated from three unique triplets
    # One of these, codon_size, has both the positive and negative codon:
    #     [8, 8] : generated from two unique triplets
    # One of these, codon_j_num, has only the negative codon:
    #     [0, 8] : generated from one unique trilet
    # There are two additional part-codons, so that makes 16 other_codons in
    # addition to the 2 from syntax codons.
    # Regulators_per_update = 16 + 8 + 8 + 0 + 8 = 48
    for i in eight_of_eight_parts[0].__dict__.iteritems():
        try:
            n = len(i[1])
            if i[0] == 'gene_sequence':
                pass
            elif i[0] == 'codon_s_num':
                assert i[1] == [16, 8]
            elif i[0] == 'codon_size':
                assert i[1] == [8, 8]
            elif i[0] == 'codon_j_num':
                assert i[1] == [0, 8]
            else:
                assert i[1] == [0] * n
        except TypeError:
            if i[0] == 'other_codons':
                assert i[1] == 18
            elif i[0] == 'regulators_per_update':
                assert i[1] == 48
            else:
                assert i[1] == 0


def test_eq(empty_part, one_of_each_part, eight_of_eight_parts):
    """
    Check that parts are considered equal to copies of themselves,
    and not equal to different parts.
    """
    assert empty_part == copy.deepcopy(empty_part)
    assert empty_part != one_of_each_part
    assert one_of_each_part == copy.deepcopy(one_of_each_part)
    for part in eight_of_eight_parts:
        assert part == copy.deepcopy(part)
        assert part != empty_part
        assert part != one_of_each_part


def test_get_push_list(empty_part, diffusion_part):
    # Check that globals are initiated correctly
    assert edpart.DIFFUSION_RATE_PULL == .1
    assert edpart.DIFFUSION_RATE_PUSH == .05
    assert edpart.REGULATOR_POOL == [0.] * 40
    # Empty part checks
    # No effect on part oe REGULATOR_POOL
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    assert [0] * 40 == empty_part.get_push_list() == edpart.REGULATOR_POOL
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    # Diffusion part checks
    # No effect on part yet, but REGULATOR_POOL gets one RE for each codon.
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    assert [1] * 40 == diffusion_part.get_push_list()
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    assert [1] * 40 == edpart.REGULATOR_POOL


def test_get_pull_list(empty_part, diffusion_part):
    # Check globals are intitiated correctly
    assert edpart.DIFFUSION_RATE_PULL == .1
    assert edpart.DIFFUSION_RATE_PUSH == .05
    # Set REGULATOR_POOL
    edpart.REGULATOR_POOL = [11] * 40
    # Empty part checks
    # No effect on part yet, but REGULATOR_POOL loses one RE for each codon.
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    assert [1] * 40 == empty_part.get_pull_list()
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    assert [10] * 40 == edpart.REGULATOR_POOL
    # Diffusion part checks
    # No effect on part yet, but REGULATOR_POOL loses one more RE for each
    # codon. Then, because REGULATOR_POOL only has 9 for each, get_pull_list()
    # calls no longer produce filled lists or effect the REGULATOR_POOL.
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    assert [1] * 40 == diffusion_part.get_pull_list()
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    assert [9] * 40 == edpart.REGULATOR_POOL
    assert ([0] * 40 == empty_part.get_pull_list() ==
            diffusion_part.get_pull_list())
    assert [9] * 40 == edpart.REGULATOR_POOL


def test_use_phpl_list(empty_part, diffusion_part):
    # Check that globals are initated correctly
    assert edpart.DIFFUSION_RATE_PULL == .1
    assert edpart.DIFFUSION_RATE_PUSH == .05
    # Set REGULATOR_POOL
    edpart.REGULATOR_POOL = [0] * 40
    # Diffusion part checks, with empty REGULATOR_POOL
    # diffusion_part loses two REs for each codon type, and
    # REGULATOR_POOL gains them.
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    pllist = diffusion_part.get_pull_list()
    assert pllist == [0] * 40
    phlist = diffusion_part.get_push_list()
    assert phlist == [1] * 40
    phpllist = [i - j for i, j in
                itertools.izip(pllist, phlist)]
    assert phpllist == [-1] * 40
    diffusion_part.use_phpl_list(phpllist)
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [19] * len(attrib[1])
    assert edpart.REGULATOR_POOL == [1] * 40
    # Reset REGULATOR_POOL
    edpart.REGULATOR_POOL = [10] * 40
    # Empty part checks, with REGULATOR_POOL filled for one pull
    # empty_part gains one RE for each codon type, and
    # REGULATOR_POOL loses one
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    pllist = empty_part.get_pull_list()
    assert pllist == [1] * 40
    phlist = empty_part.get_push_list()
    assert phlist == [0] * 40
    phpllist = [i - j for i, j in
                itertools.izip(pllist, phlist)]
    assert phpllist == [1] * 40
    empty_part.use_phpl_list(phpllist)
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [1] * len(attrib[1])
    assert edpart.REGULATOR_POOL == [9] * 40


def test_diffusion(empty_part, diffusion_part):
    # Check that globals are initiated correctly
    assert edpart.DIFFUSION_RATE_PULL == .1
    assert edpart.DIFFUSION_RATE_PUSH == .05
    # Set REGULATOR_POOL
    edpart.REGULATOR_POOL = [0] * 40
    # Empty part checks
    # No diffusion effects for empty part and empty REGULATOR_POOL
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    empty_part._diffusion()
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    # Reset REGULATOR_POOL
    edpart.REGULATOR_POOL = [10] * 40
    # REGULATOR_POOL loses on RE of each type to empty part
    empty_part._diffusion()
    for attrib in empty_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [1] * len(attrib[1])
    assert [9] * 40 == edpart.REGULATOR_POOL
    # Reset REGULATOR_POOL
    edpart.REGULATOR_POOL = [0] * 40
    # Diffusion part checks
    # diffusion_part loses two REs of each type, and
    # REGULATOR_POOL gains them.
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    diffusion_part._diffusion()
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [19] * len(attrib[1])
    assert [1] * 40 == edpart.REGULATOR_POOL


def test_update(empty_part, one_of_each_part,
                eight_of_eight_parts, diffusion_part):
    # No effect of update() on empty_part, other than num_updates
    og_empty_part = copy.deepcopy(empty_part)
    empty_part._update()
    assert empty_part.num_updates == 1
    empty_part.num_updates = 0
    assert og_empty_part == empty_part
    # One_of_each part checks
    # Mount_num and input/output slot REs increase by two because those codons
    # have a redundant copy.
    # All other REs get one.
    for attrib in one_of_each_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [0] * len(attrib[1])
    one_of_each_part._update()
    for attrib in one_of_each_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            if(attrib[0][-4:] == '_num' or
               attrib[0][-4:] == 'puts'):
                assert attrib[1] == [2, 1]
            else:
                assert attrib[1] == [1] * len(attrib[1])
    # Diffusion part checks
    # Diffusion part has 10 of each RE codon, so all REs increase by 10.

    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [20] * len(attrib[1])
    diffusion_part._update()
    for attrib in diffusion_part.__dict__.iteritems():
        if attrib[0][:4] == 'reg_':
            assert attrib[1] == [30] * len(attrib[1])
